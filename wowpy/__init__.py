from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from urllib.parse import quote


class WowAPIError(Exception):
    def __init__(self, mensagem=''):
        self.message = mensagem


class WowAPI(object):
    def __init__(self, api_key: str, region: str='us', locale: str='en_US') -> None:
        self._region_list = ['us', 'eu', 'kr', 'tw']
        self._locale_list = ['en_US', 'es_MX', 'pt_BR', 'de_DE', 'es_ES', 'fr_FR', 'it_IT', 'pt_PT', 'ru_RU', 'ko_KR', 'zh_TW', 'zh_CN']

        if region.lower() not in self._region_list or \
           locale not in self._locale_list:
            raise WowAPIError()

        self._url = 'https://{}.api.battle.net/wow'.format(region)
        self._api_key = api_key
        self._locale = locale
        self._multi_size = 50

    def _iget(self, url: str, data: dict=None) -> dict:
        """Internal use only"""
        dados = {
            'locale': self._locale,
            'apiKey': self._api_key
        }
        if isinstance(data, dict):
            dados.update(data)

        i_url = self._url + quote(url)

        req = requests.get(i_url, params=dados)

        # Mesmo se houver erro, retorna aqui
        return req.json()

    # Character services ----------------------
    def char_info(self, realm: str, charname: str, details: list=None) -> dict:
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

        return self._iget('/character/{}/{}'.format(realm, charname), data)

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
    def game_achievement_info(self, achievement_id):
        assert isinstance(achievement_id, int)

        return self._iget('/achievement/{}'.format(achievement_id))

    def game_auction_data(self, realm, lastModified=0):
        resp = self._iget('/auction/data/{realm}'.format(realm=realm))
        retorno = []
        for file in resp['files']:
            if file['lastModified'] > lastModified:
                retorno.append({'lastModified': file['lastModified'], 'data': requests.get(file['url']).json()})

        return retorno

    def game_boss_list(self):
        return self._iget('/boss/')

    def game_boss_info(self, boss_id):
        assert isinstance(boss_id, int)

        return self._iget('/boss/{}'.format(boss_id))

    def game_challenge_realm_leaderboard(self, realm):
        return self._iget('/challenge/{}'.format(realm))

    def game_challenge_region_leaderboard(self):
        return self._iget('/challenge/region')

    def game_item_info(self, item_id):
        assert isinstance(item_id, int)

        return self._iget('/item/{}'.format(item_id))

    def game_item_set(self, itemset_id):
        assert isinstance(itemset_id, int)

        return self._iget('/item/set/{}'.format(itemset_id))

    def game_mount_list(self):
        return self._iget('/mount/')

    def game_pvp_leaderboards(self, bracket='rbg'):
        if bracket not in ('2v2', '3v3', '5v5', 'rbg'):
            raise WowAPIError('Invalid pvp bracket')

        return self._iget('/leaderboard/{}'.format(bracket))

    def game_quest_info(self, quest_id):
        assert isinstance(quest_id, int)

        return self._iget('/quest/{}'.format(quest_id))

    def game_realm_status(self, realms=None):
        data = {'realms': ','.join(realms)} if realms else None
        return self._iget('/realm/status', data)

    def game_recipe_info(self, recipe_id):
        assert isinstance(recipe_id, int)

        return self._iget('/recipe/{}'.format(recipe_id))

    def game_spell_info(self, spell_id):
        assert isinstance(spell_id, int)

        return self._iget('/spell/{}'.format(spell_id))

    def game_zone_list(self):
        return self._iget('/zone/')

    def game_zone_info(self, zone_id):
        assert isinstance(zone_id, int)

        return self._iget('/zone/{}'.format(zone_id))

    def game_battlegroups_list(self):
        return self._iget('/data/battlegroups/')

    def game_races_list(self):
        return self._iget('/data/character/races')

    def game_classes_list(self):
        return self._iget('/data/character/classes')

    def game_achievements_list(self):
        return self._iget('/data/character/achievements')

    def game_itemclass_list(self):
        return self._iget('/data/item/classes')

    def game_talents_list(self):
        return self._iget('/data/talents')

    # pet services
    def pet_list(self):
        return self._iget('/pet/')

    def pet_ability(self, ability_id):
        assert isinstance(ability_id, int)

        return self._iget('/pet/ability/{}'.format(ability_id))

    def pet_species(self, species_id):
        assert isinstance(species_id, int)

        return self._iget('/pet/species/{}'.format(species_id))

    def pet_stats(self, species_id, level=1, breed_id=3, quality_id=1):
        assert isinstance(species_id, int) | isinstance(level, int) | isinstance(breed_id, int) | isinstance(quality_id, int)

        data = {
            'level': level,
            'breedId': breed_id,
            'qualityId': quality_id
        }

        return self._iget('/pet/stats/{}'.format(species_id), data)

    def pet_types_list(self):
        return self._iget('/data/pet/types')

    # Guild services
    def guild_info(self, realm, guild_name, details=None):
        valid_details = ('members', 'achievements', 'news', 'challenge')
        if details:
            data = {'fields': ','.join([detail for detail in details if detail in valid_details])}
        else:
            data = None

        return self._iget('/guild/{}/{}'.format(realm, guild_name), data)

    def guild_rewards_list(self):
        return self._iget('/data/guild/rewards')

    def guild_perks_list(self):
        return self._iget('/data/guild/perks')

    def guild_achievements_list(self):
        return self._iget('/data/guild/achievements')
