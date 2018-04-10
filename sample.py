from wowpy import WowAPI
from pprint import pprint

wow_api = WowAPI(api_key='Your_key_goes_here', region='us', locale='en_US')

basic_guild_info = wow_api.guild_info(realm='Gallywix', guild_name='Tua Mae')
pprint(basic_guild_info, indent=4)

# Get a little bit more info from same guild
more_guild_info = wow_api.guild_info(realm='Gallywix', guild_name='Tua Mae', details=['members', 'news'])
pprint(more_guild_info, indent=4)

# Get basic info from char
basic_char_info = wow_api.char_info(realm='Gallywix', charname='zimbhabwe')
pprint(basic_char_info, indent=4)

# Get some details from same char
char_info = wow_api.char_info(realm='Gallywix', charname='zimbhabwe', details=['achievements', 'titles', 'guild'])
pprint(char_info, indent=4)

# Get item info
item_info = wow_api.game_item_info(73541)
pprint(item_info, indent=4)

# Get several items info (get all concurrently)
items_info = wow_api.multi('game_item_info', (
    (73541, ),
    (73542, ),
    (73543, ),
    (73544, ),
    (73545, )
))

pprint(items_info)
