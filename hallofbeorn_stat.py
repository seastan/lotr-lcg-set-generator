""" Collect various data from Hall of Beorn.
"""
import codecs
from collections import Counter
import csv
import json
import os
import re
import time
import uuid

import requests
import unidecode


HALLOFBEORN_URL = 'http://hallofbeorn.com/Export/Cards?setType=ALL_SETS'
OUTPUT_PATH = os.path.join('Output', 'Scripts')

URL_TIMEOUT = 15
URL_RETRIES = 3
URL_SLEEP = 10


def get_content(url):
    """ Get URL content.
    """
    for i in range(URL_RETRIES):
        try:
            req = requests.get(url, timeout=URL_TIMEOUT)
            res = req.content
            break
        except Exception:  # pylint: disable=W0703
            if i < URL_RETRIES - 1:
                time.sleep(URL_SLEEP)
            else:
                raise

    return res


def get_data():
    """ Get Hall of Beorn data.
    """
    data = get_content(HALLOFBEORN_URL)
    data = json.loads(data)
    return data


def filter_data(data):
    """ Filter Hall of Beorn data.
    """
    data = [c for c in data
            if c['type_name'] in ('Hero', 'Ally', 'Attachment', 'Event',
                                  'Player Side Quest', 'Contract')
            and c['pack_name'] not in (
                'Two-Player Limited Edition Starter', 'Revised Core Set',
                'Dwarves of Durin', 'Elves of Lórien', 'Defenders of Gondor',
                'Riders of Rohan',
                'The Massing at Osgiliath', 'The Battle of Lake-town',
                'The Stone of Erech', 'Fog on the Barrow-downs',
                'The Old Forest', 'Murder at the Prancing Pony',
                'The Ruins of Belegost', 'The Siege of Annúminas',
                'Attack on Dol Guldur', 'The Wizard\'s Quest',
                'The Woodland Realm', 'The Mines of Moria',
                'Escape from Khazad-dûm', 'First Age',
                'Trial Upon the Marches', 'Among the Outlaws',
                'The Betrayal of Mîm', 'The Fall of Nargothrond')
            and 'Preorder Promotion' not in c['pack_name']
            and c.get('subtype_code') != 'boon'
            and c['sphere_name'] not in ('Baggins', 'Fellowship')
            and (c['pack_name'] not in ('The Scouring of the Shire',)
                 or c['type_name'] != 'Hero')]
    return data


def collect_traits(data):
    """ Collect traits statistics from Hall of Beorn.
    """
    data = filter_data(data)
    text = [(c['text'].replace('~', '')
             .replace('[leadership]', '***')
             .replace('[lore]', '***')
             .replace('[spirit]', '***')
             .replace('[tactics]', '***')
             .replace(c['name'], '***')
             .replace(unidecode.unidecode(c['name']), '***')
             .replace('Ranger of the North', '***')
             .replace('Ring-bearer', '***')
             .replace('The One Ring', '***'),
             c['name']) for c in data]
    traits = [
        item for sublist in [
            [(t.strip(),
              c['type_name'],
              c['sphere_name']
              ) for t in c['traits'].split('.') if t.strip()]
            for c in data if c['traits']
            and c['type_name'] in ('Hero', 'Ally', 'Attachment', 'Event')]
        for item in sublist]
    traits = list(zip(Counter(traits).keys(), Counter(traits).values()))

    res = {}
    for row in traits:
        trait = res.setdefault(
            row[0][0],
            {'Total': 0, 'Hero': 0, 'Ally': 0, 'Attachment': 0, 'Event': 0,
             'Leadership': 0, 'Lore': 0, 'Spirit': 0, 'Tactics': 0,
             'Neutral': 0})
        trait[row[0][1]] += row[1]
        trait[row[0][2]] += row[1]
        trait['Total'] += row[1]

    for trait in res:
        res[trait]['Mentions'] = sorted([
            t[1] for t in text if re.search(r'\b{}\b'.format(trait), t[0])])

    res = sorted(list(res.items()), key=lambda i: (-i[1]['Total'], i[0]))

    file_path = os.path.join(OUTPUT_PATH, 'traits.csv')
    with open(file_path, 'w', newline='', encoding='utf-8') as obj:
        obj.write(codecs.BOM_UTF8.decode('utf-8'))
        fieldnames = ['Trait', 'Total', 'Hero', 'Ally', 'Attachment', 'Event',
                      'Leadership', 'Lore', 'Spirit', 'Tactics', 'Neutral',
                      'Mentions', 'Mentioned on Cards']
        writer = csv.DictWriter(obj, fieldnames=fieldnames)
        writer.writeheader()
        for row in res:
            csv_row = {
                'Trait': row[0],
                'Total': row[1]['Total'],
                'Hero': row[1]['Hero'] or '',
                'Ally': row[1]['Ally'] or '',
                'Attachment': row[1]['Attachment'] or '',
                'Event': row[1]['Event'] or '',
                'Leadership': row[1]['Leadership'] or '',
                'Lore': row[1]['Lore'] or '',
                'Spirit': row[1]['Spirit'] or '',
                'Tactics': row[1]['Tactics'] or '',
                'Neutral': row[1]['Neutral'] or '',
                'Mentions': len(row[1]['Mentions']) or '',
                'Mentioned on Cards': ', '.join(row[1]['Mentions'])
                }
            writer.writerow(csv_row)


def transform_keyword(value):
    """ Transform a keyword value if needed.
    """
    value = re.sub(r' [0-9X]$', ' N', value)
    return value


def collect_keywords(data):
    """ Collect keywords statistics from Hall of Beorn.
    """
    data = filter_data(data)
    keywords = [
        item for sublist in [
            [(transform_keyword(t.strip()),
              c['type_name'],
              c['sphere_name']
              ) for t in c['keywords'].split('.') if t.strip()]
            for c in data if c.get('keywords')
            and c['type_name'] in ('Hero', 'Ally', 'Attachment', 'Event')]
        for item in sublist]
    keywords = list(zip(Counter(keywords).keys(), Counter(keywords).values()))

    res = {}
    for row in keywords:
        keyword = res.setdefault(
            row[0][0],
            {'Total': 0, 'Hero': 0, 'Ally': 0, 'Attachment': 0, 'Event': 0,
             'Leadership': 0, 'Lore': 0, 'Spirit': 0, 'Tactics': 0,
             'Neutral': 0})
        keyword[row[0][1]] += row[1]
        keyword[row[0][2]] += row[1]
        keyword['Total'] += row[1]

    res = sorted(list(res.items()), key=lambda i: (-i[1]['Total'], i[0]))

    file_path = os.path.join(OUTPUT_PATH, 'keywords.csv')
    with open(file_path, 'w', newline='', encoding='utf-8') as obj:
        obj.write(codecs.BOM_UTF8.decode('utf-8'))
        fieldnames = ['Keyword', 'Total', 'Hero', 'Ally', 'Attachment', 'Event',
                      'Leadership', 'Lore', 'Spirit', 'Tactics', 'Neutral']
        writer = csv.DictWriter(obj, fieldnames=fieldnames)
        writer.writeheader()
        for row in res:
            csv_row = {
                'Keyword': row[0],
                'Total': row[1]['Total'],
                'Hero': row[1]['Hero'] or '',
                'Ally': row[1]['Ally'] or '',
                'Attachment': row[1]['Attachment'] or '',
                'Event': row[1]['Event'] or '',
                'Leadership': row[1]['Leadership'] or '',
                'Lore': row[1]['Lore'] or '',
                'Spirit': row[1]['Spirit'] or '',
                'Tactics': row[1]['Tactics'] or '',
                'Neutral': row[1]['Neutral'] or ''
                }
            writer.writerow(csv_row)


def collect_stat():
    """ Collect traits and keywords statistics from Hall of Beorn.
    """
    data = get_data()
    collect_traits(data)
    collect_keywords(data)
    print('Done')


def get_ringsdb_csv(pack_name, pack_code):
    """ Get Hall of Beorn data and prepare a csv file for RingsDB.
    """
    data = get_data()
    data = [c for c in data if c['pack_name'] == pack_name]
    file_path = os.path.join(OUTPUT_PATH, '{}.csv'.format(pack_name))
    with open(file_path, 'w', newline='', encoding='utf-8') as obj:
        obj.write(codecs.BOM_UTF8.decode('utf-8'))
        fieldnames = ['pack', 'type', 'sphere', 'position', 'code', 'name',
                      'traits', 'text', 'flavor', 'isUnique', 'cost', 'threat',
                      'willpower', 'attack', 'defense', 'health', 'victory',
                      'quest', 'quantity', 'deckLimit', 'illustrator',
                      'octgnid', 'hasErrata']
        writer = csv.DictWriter(obj, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            if row['type_name'] in ('Contract', 'Player Objective'):
                type_name = 'Other'
            elif (row['type_name'] == 'Treasure' or
                  row.get('subtype_code') in ('Boon', 'Burden')):
                type_name = 'Campaign'
            else:
                type_name = row['type_name']

            if (row['type_name'] in ('Contract', 'Player Objective',
                                     'Treasure') or
                    row.get('subtype_code') in ('Boon', 'Burden')):
                sphere_name = 'Neutral'
            else:
                sphere_name = row.get('sphere_name') or 'Neutral'

            csv_row = {
                'pack': row['pack_name'],
                'type': type_name,
                'sphere': sphere_name,
                'position': row['position'],
                'code': '{}{}'.format(pack_code,
                                      str(int(row['position'])).zfill(3)),
                'name': row['name'].replace('’', "'"),
                'traits': row.get('traits', ''),
                'text': row.get('text', ''),
                'flavor': row.get('flavor', ''),
                'isUnique': row.get('is_unique') and '1' or '',
                'cost': row.get('cost', ''),
                'threat': row.get('threat', ''),
                'willpower': row.get('willpower', ''),
                'attack': row.get('attack', ''),
                'defense': row.get('defense', ''),
                'health': row.get('health', ''),
                'victory': row.get('victory', ''),
                'quest': row.get('quest_points', ''),
                'quantity': row.get('quantity', ''),
                'deckLimit': row.get('deck_limit', ''),
                'illustrator': row.get('illustrator', ''),
                'octgnid': row.get('', uuid.uuid4()),
                'hasErrata': row.get('has_errata') and '1' or ''
                }
            writer.writerow(csv_row)

    print('Done')


if __name__ == '__main__':
    collect_stat()
    # get_ringsdb_csv('Dwarves of Durin', '31')
