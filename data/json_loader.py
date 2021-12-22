import os

import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#DATA_BASE = os.path.join(BASE_DIR, 'db.sqlite3')

with open(os.path.join(BASE_DIR, 'ingredients.json'), 'r', encoding='utf-8') as json_list:
    jdata = json.load(json_list)

dpos = 3
newdata = [None] * len(jdata)
for pos, data in enumerate(jdata):
    newdata[pos] = {
        'model': 'api.ingredient',
        'pk': str(pos+dpos),
        'fields': {
            'name': data['name'].replace('"', '~'),
            'measurement_unit': data['measurement_unit'].replace('"', '\\"')
        }
    }

#newdump = json.dumps(newdata)
newdump = str(newdata).replace('\'', '"').replace('~', '\\"')

with open(os.path.join(BASE_DIR, 'new_ingredients.json'), 'w', encoding='utf-8') as json_file:
    print(newdump, file=json_file)
