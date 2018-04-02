import requests


class WowAPIError(Exception):
    def __init__(self, mensagem=''):
        self.message = mensagem


class WowAPI(object):
    def __init__(self, api_key: str, region: str='us', locale: str='en_US') -> None:
        if region.lower() not in ('us', 'eu', 'kr', 'tw'):
            raise WowAPIError()

        self.url = 'https://{}.api.battle.net/wow'.format(region)
        self.api_key = api_key
        self.locale = locale

    def get(self, url: str, data=None) -> dict:
        dados = {
            'locale': self.locale,
            'apiKey': self.api_key
        }
        if isinstance(data, dict):
            dados.update(data)

        req = requests.get(self.url + url, params=dados)
        if req.status_code != 200:
            raise WowAPIError()

        return req.json()

    # Character services ----------------------
    def char_info(self, realm: str, charname: str, details: list=None) -> dict:
        valid_details = ('achievements', 'appearance', 'feed', 'guild', 'hunterPets', 'items', 'mounts', 'pets', 'petSlots',
                         'professions', 'progression', 'pvp', 'quests', 'reputation', 'statistics', 'stats', 'talents', 'titles',
                         'audit')
        data = ','.join([detail for detail in details if detail in valid_details]) if details else None

        return self.get('/character/{}/{}'.format(realm, charname), data or None)

    # Game services
    def game_achievement_info(self, achievement_id):
        assert isinstance(achievement_id, int)

        return self.get('/achievement/{}'.format(achievement_id))

    def game_auction_data(self, realm):
        resp = self.get('/auction/data/{realm}'.format(realm=realm))
        retorno = []
        for file in resp['files']:
            retorno.append((file['lastModified'], requests.get(file['url'])))

        return retorno

    def game_boss_list(self):
        return self.get('/boss/')

    def game_boss_info(self, boss_id):
        assert isinstance(boss_id, int)

        return self.get('/boss/{}'.format(boss_id))

    def game_challenge_realm_leaderboard(self, realm):
        return self.get('/challenge/{}'.format(realm))

    def game_challenge_region_leaderboard(self):
        return self.get('/challenge/region')

    def game_item_info(self, item_id):
        assert isinstance(item_id, int)

        return self.get('/item/{}'.format(item_id))

    def game_item_set(self, itemset_id):
        assert isinstance(itemset_id, int)

        return self.get('/item/set/{}'.format(itemset_id))

    def game_mount_list(self):
        return self.get('/mount/')

    def game_pvp_leaderboards(self, bracket='rbg'):
        if bracket not in ('2v2', '3v3', '5v5', 'rbg'):
            raise WowAPIError('Invalid pvp bracket')

        return self.get('/leaderboard/{}'.format(bracket))

    def game_quest_info(self, quest_id):
        assert isinstance(quest_id, int)

        return self.get('/quest/{}'.format(quest_id))

    def game_realm_status(self, realms=None):
        data = {'realms': ','.join(realms)} if realms else None
        return self.get('/realm/status', data)

    def game_recipe_info(self, recipe_id):
        assert isinstance(recipe_id, int)

        return self.get('/recipe/{}'.format(recipe_id))

    def game_spell_info(self, spell_id):
        assert isinstance(spell_id, int)

        return self.get('/spell/{}'.format(spell_id))

    def game_zone_list(self):
        return self.get('/zone/')

    def game_zone_info(self, zone_id):
        assert isinstance(zone_id, int)

        return self.get('/zone/{}'.format(zone_id))

    def game_battlegroups_list(self):
        return self.get('/data/battlegroups/')

    def game_races_list(self):
        return self.get('/data/character/races')

    def game_classes_list(self):
        return self.get('/data/character/classes')

    def game_achievements_list(self):
        return self.get('/data/character/achievements')

    def game_itemclass_list(self):
        return self.get('/data/item/classes')

    def game_talents_list(self):
        return self.get('/data/talents')

    # pet services
    def pet_list(self):
        return self.get('/pet/')

    def pet_ability(self, ability_id):
        assert isinstance(ability_id, int)

        return self.get('/pet/ability/{}'.format(ability_id))

    def pet_species(self, species_id):
        assert isinstance(species_id, int)

        return self.get('/pet/species/{}'.format(species_id))

    def pet_stats(self, species_id, level=1, breed_id=3, quality_id=1):
        assert isinstance(species_id, int) | isinstance(level, int) | isinstance(breed_id, int) | isinstance(quality_id, int)

        data = {
            'level': level,
            'breedId': breed_id,
            'qualityId': quality_id
        }

        return self.get('/pet/stats/{}'.format(species_id), data)

    def pet_types_list(self):
        return self.get('/data/pet/types')

    # Guild services
    def guild_info(self, realm, guild_name, details=None):
        valid_details = ('members', 'achievements', 'news', 'challenge')
        data = ','.join([detail for detail in details if detail in valid_details]) if details else None

        return self.get('/guild/{}/{}'.format(realm, guild_name), data or None)

    def guild_rewards_list(self):
        return self.get('/data/guild/rewards')

    def guild_perks_list(self):
        return self.get('/data/guild/perks')

    def guild_achievements_list(self):
        return self.get('/data/guild/achievements')
