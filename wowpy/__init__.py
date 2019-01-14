from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from urllib.parse import quote
from datetime import datetime, timedelta
from base64 import b64encode
from os import path
import pickle


class WowAPIError(Exception):
    def __init__(self, mensagem=''):
        self.message = mensagem


class WowAPI(object):
    def __init__(self, client_secret: str, region: str='us', locale: str='en_US') -> None:
        self._region_list = ['us', 'eu', 'kr', 'tw']
        self._locale_list = ['en_US', 'es_MX', 'pt_BR', 'de_DE', 'es_ES', 'fr_FR', 'it_IT', 'pt_PT', 'ru_RU', 'ko_KR', 'zh_TW', 'zh_CN']

        if region.lower() not in self._region_list or \
           locale not in self._locale_list:
            raise WowAPIError()

        self._url = 'https://{}.api.blizzard.com/wow'.format(region)
        self._url_token = 'https://{}.battle.net/oauth/token'.format(region)
        self._client_secret = client_secret
        self._client_id = '506d11fa07534228b81cec328fb112b3'
        self._locale = locale
        self._multi_size = 50
        self._auth_header = {}
        self._date_token = None

    def get_access_token(self):
        tmp_file_token = '/tmp/wow_token.tmp'
        if not self._date_token:  # Não tem data, é a primeira vez
            self._date_token = datetime(2000, 1, 1)
            if path.isfile(tmp_file_token):  # Já tem um token, vamos ler ele
                dados = pickle.loads(open(tmp_file_token, 'rb').read())
                self._date_token = dados['valido_ate']

        if self._date_token < datetime.now():  # Precisa pegar novo token
            auth = b64encode('{}:{}'.format(self._client_id, self._client_secret).encode('ascii')).decode('ascii')

            req = requests.get(self._url_token,
                               headers={'Authorization': 'Basic {}'.format(auth)},
                               params={'grant_type': 'client_credentials'})

            dados = req.json()
            dados['valido_ate'] = datetime.now() + timedelta(seconds=dados.get('expires_in') - 2)

            with open(tmp_file_token, 'wb') as saida:
                saida.write(pickle.dumps(dados))

            self._date_token = dados['valido_ate']
            self._auth_header['Authorization'] = 'Bearer {}'.format(dados['access_token'])

    def _iget(self, url: str, data: dict=None, locale: str=None) -> dict:
        """Internal use only"""
        dados = {'locale': locale or self._locale}

        self.get_access_token()

        if isinstance(data, dict):
            dados.update(data)

        i_url = self._url + quote(url)

        req = requests.get(i_url, params=dados, headers=self._auth_header)

        # Mesmo se houver erro, retorna aqui
        return req.json()

    # Character services ----------------------
    def char_info(self, realm: str, charname: str, details: list=None, locale: str=None) -> dict:
        """Get info from specific char.
  *** Input parameters:
    * realm: Realm of the char...
    * charname:
    * details (optional): List of required details. Valid values are: achievements, appearance, feed, guild, hunterPets, audit,
              items, mounts, pets, petSlots, professions, progression, pvp, quests, reputation, statistics, stats, talents, titles
  *** Returns a dict with required info

  example: ret = WowApi.char_info('testRealm', 'testChar', ['quests', 'feed', 'guild'])
"""
        valid_details = ('achievements', 'appearance', 'feed', 'guild', 'hunterPets', 'items', 'mounts', 'pets', 'petSlots',
                         'professions', 'progression', 'pvp', 'quests', 'reputation', 'statistics', 'stats', 'talents', 'titles',
                         'audit')
        if details:
            data = {'fields': ','.join([detail for detail in details if detail in valid_details])}
        else:
            data = None

        return self._iget('/character/{}/{}'.format(realm, charname), data, locale)

    def multi(self, fnc: str, param_list: tuple) -> list:
        """Get info from specific char.
  *** Input parameters:
    * realm: Realm of the char...
    * charname:
    * details (optional): List of required details. Valid values are: achievements, appearance, feed, guild, hunterPets, audit,
              items, mounts, pets, petSlots, professions, progression, pvp, quests, reputation, statistics, stats, talents, titles
  *** Returns a dict with required info

  example: ret = WowApi.char_info('testRealm', 'testChar', ['quests', 'feed', 'guild'])
"""
        fnc_point = getattr(self, fnc, None)
        if not fnc_point:
            raise WowAPIError('Invalid function')

        result = []
        with ThreadPoolExecutor(max_workers=None) as executor:
            futures = {}
            for parameters in param_list:
                if isinstance(parameters, dict):
                    futures[executor.submit(fnc_point, **parameters)] = parameters
                else:
                    futures[executor.submit(fnc_point, *parameters)] = parameters

            for future in as_completed(futures):
                result.append((futures[future], future.result()))

        return result

    # Game services
    def game_achievement_info(self, achievement_id, locale: str=None):
        assert isinstance(achievement_id, int)

        return self._iget('/achievement/{}'.format(achievement_id), locale)

    def game_auction_data(self, realm, lastModified=0, locale: str=None):
        resp = self._iget('/auction/data/{realm}'.format(realm=realm), locale=locale)
        retorno = []
        for file in resp['files']:
            if file['lastModified'] > lastModified:
                retorno.append({'lastModified': file['lastModified'], 'data': requests.get(file['url']).json()})

        return retorno

    def game_boss_list(self, locale: str=None):
        return self._iget('/boss/', locale=locale)

    def game_boss_info(self, boss_id, locale: str=None):
        assert isinstance(boss_id, int)

        return self._iget('/boss/{}'.format(boss_id), locale=locale)

    def game_challenge_realm_leaderboard(self, realm, locale: str=None):
        return self._iget('/challenge/{}'.format(realm), locale=locale)

    def game_challenge_region_leaderboard(self, locale: str=None):
        return self._iget('/challenge/region', locale=locale)

    def game_item_info(self, item_id, locale: str=None):
        assert isinstance(item_id, int)

        return self._iget('/item/{}'.format(item_id), locale=locale)

    def game_item_set(self, itemset_id, locale: str=None):
        assert isinstance(itemset_id, int)

        return self._iget('/item/set/{}'.format(itemset_id), locale=locale)

    def game_mount_list(self, locale: str=None):
        return self._iget('/mount/', locale=locale)

    def game_pvp_leaderboards(self, bracket='rbg', locale: str=None):
        if bracket not in ('2v2', '3v3', '5v5', 'rbg'):
            raise WowAPIError('Invalid pvp bracket')

        return self._iget('/leaderboard/{}'.format(bracket), locale=locale)

    def game_quest_info(self, quest_id, locale: str=None):
        assert isinstance(quest_id, int)

        return self._iget('/quest/{}'.format(quest_id), locale=locale)

    def game_realm_status(self, realms=None, locale: str=None):
        data = {'realms': ','.join(realms)} if realms else None
        return self._iget('/realm/status', data, locale=locale)

    def game_recipe_info(self, recipe_id, locale: str=None):
        assert isinstance(recipe_id, int)

        return self._iget('/recipe/{}'.format(recipe_id), locale=locale)

    def game_spell_info(self, spell_id, locale: str=None):
        assert isinstance(spell_id, int)

        return self._iget('/spell/{}'.format(spell_id), locale=locale)

    def game_zone_list(self, locale: str=None):
        return self._iget('/zone/', locale=locale)

    def game_zone_info(self, zone_id, locale: str=None):
        assert isinstance(zone_id, int)

        return self._iget('/zone/{}'.format(zone_id), locale=locale)

    def game_battlegroups_list(self, locale: str=None):
        return self._iget('/data/battlegroups/', locale=locale)

    def game_races_list(self, locale: str=None):
        return self._iget('/data/character/races', locale=locale)

    def game_classes_list(self, locale: str=None):
        return self._iget('/data/character/classes', locale=locale)

    def game_achievements_list(self, locale: str=None):
        return self._iget('/data/character/achievements', locale=locale)

    def game_itemclass_list(self, locale: str=None):
        return self._iget('/data/item/classes', locale=locale)

    def game_talents_list(self, locale: str=None):
        return self._iget('/data/talents', locale=locale)

    # pet services
    def pet_list(self, locale: str=None):
        return self._iget('/pet/', locale=locale)

    def pet_ability(self, ability_id, locale: str=None):
        assert isinstance(ability_id, int)

        return self._iget('/pet/ability/{}'.format(ability_id), locale=locale)

    def pet_species(self, species_id, locale: str=None):
        assert isinstance(species_id, int)

        return self._iget('/pet/species/{}'.format(species_id), locale=locale)

    def pet_stats(self, species_id, level=1, breed_id=3, quality_id=1, locale: str=None):
        assert isinstance(species_id, int) | isinstance(level, int) | isinstance(breed_id, int) | isinstance(quality_id, int)

        data = {
            'level': level,
            'breedId': breed_id,
            'qualityId': quality_id
        }

        return self._iget('/pet/stats/{}'.format(species_id), data, locale=locale)

    def pet_types_list(self, locale: str=None):
        return self._iget('/data/pet/types', locale=locale)

    # Guild services
    def guild_info(self, realm, guild_name, details=None, locale: str=None):
        valid_details = ('members', 'achievements', 'news', 'challenge')
        if details:
            data = {'fields': ','.join([detail for detail in details if detail in valid_details])}
        else:
            data = None

        return self._iget('/guild/{}/{}'.format(realm, guild_name), data, locale=locale)

    def guild_rewards_list(self, locale: str=None):
        return self._iget('/data/guild/rewards', locale=locale)

    def guild_perks_list(self, locale: str=None):
        return self._iget('/data/guild/perks', locale=locale)

    def guild_achievements_list(self, locale: str=None):
        return self._iget('/data/guild/achievements', locale=locale)
