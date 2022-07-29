# pylint: disable=C0209
# -*- coding: utf8 -*-
""" Collect various data from Hall of Beorn and RingsDB.
"""
import codecs
from collections import Counter
import csv
import html
import json
import os
import re
import uuid

import unidecode

from lotr import (create_folder, escape_filename, get_content, handle_int,
                  is_int)


HALLOFBEORN_CARDS_URL = 'http://hallofbeorn.com/Export/ALeP'
HALLOFBEORN_SCENARIO_URL = 'http://hallofbeorn.com/Cards/ScenarioDetails/{}'
HALLOFBEORN_SCENARIOS_URL = 'http://hallofbeorn.com/LotR/Scenarios/'
RINGSDB_URL = 'https://ringsdb.com/api/public/cards/'
HALLOFBEORN_PATH = os.path.join('Output', 'HallOfBeorn')
OUTPUT_PATH = os.path.join('Output', 'Scripts')
OUTPUT_SCENARIOS_PATH = os.path.join('Output', 'Scripts', 'Scenarios')

EXCLUDE_SETS = {
    'Revised Core Set', 'Angmar Awakened Hero Expansion',
    'The Bonds of Fellowship', 'Two-Player Limited Edition Starter',
    'Dwarves of Durin', 'Elves of Lórien', 'Defenders of Gondor',
    'Riders of Rohan', 'The Massing at Osgiliath', 'The Battle of Lake-town',
    'The Stone of Erech', 'Fog on the Barrow-downs', 'The Old Forest',
    'Murder at the Prancing Pony', 'The Ruins of Belegost',
    'The Siege of Annúminas', 'Attack on Dol Guldur', 'The Wizard\'s Quest',
    'The Woodland Realm', 'The Mines of Moria', 'Escape from Khazad-dûm',
    'First Age', 'Trial Upon the Marches', 'Among the Outlaws',
    'The Betrayal of Mîm', 'The Fall of Nargothrond'}
PROMO_HEROES_SETS = {'The Scouring of the Shire', 'The Nine are Abroad'}
FUTURE_SETS = {'Blood in the Isen'}

SCENARIOS_REGEX = r' href="\/LotR\/Scenarios/([^"]+)">'

USE_HALLOFBEORN_CARDS_CACHE = False


def get_hall_data():
    """ Get Hall of Beorn data.
    """
    cache_path = os.path.join(OUTPUT_PATH, 'hall.json')
    data = None
    if USE_HALLOFBEORN_CARDS_CACHE:
        try:
            with open(cache_path, 'r', encoding='utf-8') as fobj:
                data = json.load(fobj)

            print('Reading Hall of Beorn data from cache')
        except Exception:  # pylint: disable=W0703
            pass

    if not data:
        data = get_content(HALLOFBEORN_CARDS_URL)
        data = json.loads(data)
        print('Downloading Hall of Beorn data from the site')
        with open(cache_path, 'w', encoding='utf-8') as fobj:
            json.dump(data, fobj)

    current_sets = {c['pack_name'] for c in data}
    for future_set in FUTURE_SETS:
        if future_set.replace('ALeP - ', '') in current_sets:
            print('{} is already included in Hall of Beorn data'
                  .format(future_set))
            continue

        path = os.path.join(HALLOFBEORN_PATH,
                            '{}.English'.format(future_set),
                            '{}.English.json'.format(future_set))
        try:
            with open(path, 'r', encoding='utf-8') as fobj:
                additional_data = json.load(fobj)

            print('Reading additional data from {}'.format(path))
        except Exception:  # pylint: disable=W0703
            path = os.path.join(HALLOFBEORN_PATH,
                                'ALeP - {}.English'.format(future_set),
                                'ALeP - {}.English.json'.format(future_set))
            try:
                with open(path, 'r', encoding='utf-8') as fobj:
                    additional_data = json.load(fobj)

                print('Reading additional data from {}'.format(path))
            except Exception:  # pylint: disable=W0703
                print("Can't find additional data for {}".format(future_set))
                additional_data = []

        for card in additional_data:
            if card.get('traits'):
                card['traits'] = '{}.'.format('. '.join(card['traits']))

            if card.get('keywords'):
                card['keywords'] = '{}.'.format('. '.join(card['keywords']))

        data.extend(additional_data)

    return data


def filter_hall_data(data):
    """ Filter Hall of Beorn data.
    """
    data = [c for c in data
            if c['type_name'] in {'Ally', 'Attachment', 'Contract', 'Event',
                                  'Hero', 'Player Objective',
                                  'Player Side Quest'}
            and c['pack_name'] not in EXCLUDE_SETS
            and 'Preorder Promotion' not in c['pack_name']
            and c.get('subtype_code') != 'boon'
            and c['sphere_name'] not in {'Baggins', 'Fellowship'}
            and (c['pack_name'] not in PROMO_HEROES_SETS
                 or c['type_name'] != 'Hero')]
    return data


def collect_spheres(data):
    """ Collect spheres statistics from Hall of Beorn.
    """
    spheres = {'Leadership', 'Lore', 'Spirit', 'Tactics', 'Neutral',
               'No Sphere'}
    sphere_types = {'Ally', 'Attachment', 'Event', 'Hero', 'Player Side Quest'}
    unique_types = {'Ally', 'Attachment'}
    columns = ['Total', 'Hero', 'Ally', 'Ally (unique)',
               'Attachment', 'Attachment (unique)', 'Event',
               'Player Side Quest', 'Contract', 'Player Objective']

    res = {}
    for sphere in spheres:
        res[sphere] = {c:0 for c in columns}

    for card in data:
        if card['type_name'] in sphere_types:
            if card['type_name'] in unique_types:
                res[card['sphere_name']]['Total'] += 1
                res[card['sphere_name']][card['type_name']] += 1
                if card.get('is_unique'):
                    res[card['sphere_name']]['{} (unique)'.format(
                        card['type_name'])] += 1
            else:
                res[card['sphere_name']]['Total'] += 1
                res[card['sphere_name']][card['type_name']] += 1
        else:
            res['No Sphere'][card['type_name']] += 1
            res['No Sphere']['Total'] += 1

    res = sorted(list(res.items()), key=lambda i: (-i[1]['Total'], i[0]))

    file_path = os.path.join(OUTPUT_PATH, 'spheres.csv')
    with open(file_path, 'w', newline='', encoding='utf-8') as obj:
        obj.write(codecs.BOM_UTF8.decode('utf-8'))
        fieldnames = ['Sphere'] + columns
        writer = csv.DictWriter(obj, fieldnames=fieldnames)
        writer.writeheader()
        for row in res:
            csv_row = {
                'Sphere': row[0],
            }
            for column in columns:
                csv_row[column] = row[1][column] or ''

            writer.writerow(csv_row)


def collect_numbers(data):  # pylint: disable=R0912,R0914,R0915
    """ Collect numbers statistics from Hall of Beorn.
    """
    non_sphere_types = ['Player Objective']
    sphere_types = ['Hero', 'Ally', 'Attachment', 'Event', 'Player Side Quest']
    unique_types = ['Ally', 'Attachment']
    spheres = ['Leadership', 'Lore', 'Spirit', 'Tactics', 'Neutral']

    rows = []
    for card_type in sphere_types:
        if card_type in unique_types:
            rows.append(card_type)
            rows.append('{} (unique)'.format(card_type))
        else:
            rows.append(card_type)

    rows.extend(non_sphere_types)
    rows.extend(spheres)
    for card_type in sphere_types:
        if card_type in unique_types:
            for sphere in spheres:
                rows.append('{} {}'.format(sphere, card_type))
                rows.append('{} {} (unique)'.format(sphere, card_type))
        else:
            for sphere in spheres:
                rows.append('{} {}'.format(sphere, card_type))

    columns = set(['Avg Thr', 'Avg Cost', 'Avg WP', 'Avg Att', 'Avg Def',
                   'Avg HP'])
    min_values = {}
    max_values = {}
    res = {}
    for card in data:
        affected_rows = set()
        if card['type_name'] in non_sphere_types:
            affected_rows.add(card['type_name'])
        elif card['type_name'] in sphere_types:
            affected_rows.add(card['sphere_name'])
            if card['type_name'] in unique_types:
                affected_rows.add(card['type_name'])
                affected_rows.add('{} {}'.format(card['sphere_name'],
                                                       card['type_name']))
                if card.get('is_unique'):
                    affected_rows.add('{} (unique)'.format(card['type_name']))
                    affected_rows.add('{} {} (unique)'.format(
                        card['sphere_name'], card['type_name']))
            else:
                affected_rows.add(card['type_name'])
                affected_rows.add('{} {}'.format(card['sphere_name'],
                                                 card['type_name']))

        for row in affected_rows:
            row_dict = res.setdefault(row, {})
            row_dict['Total'] = row_dict.get('Total', 0) + 1
            if 'threat' in card:
                key = 'Thr {}'.format(card['threat'])
                columns.add(key)
                row_dict[key] = row_dict.get(key, 0) + 1
                if is_int(card['threat']):
                    min_values['Thr'] = min(min_values.get('Thr', 100),
                                            int(card['threat']))
                    max_values['Thr'] = max(max_values.get('Thr', 0),
                                            int(card['threat']))
                    row_dict['Thr Count'] = row_dict.get('Thr Count', 0) + 1
                    row_dict['Thr Sum'] = (row_dict.get('Thr Sum', 0) +
                                           int(card['threat']))

            if 'cost' in card:
                key = 'Cost {}'.format(card['cost'])
                columns.add(key)
                row_dict[key] = row_dict.get(key, 0) + 1
                if is_int(card['cost']):
                    min_values['Cost'] = min(min_values.get('Cost', 100),
                                             int(card['cost']))
                    max_values['Cost'] = max(max_values.get('Cost', 0),
                                             int(card['cost']))
                    row_dict['Cost Count'] = row_dict.get('Cost Count', 0) + 1
                    row_dict['Cost Sum'] = (row_dict.get('Cost Sum', 0) +
                                            int(card['cost']))

            if 'willpower' in card:
                if card['willpower'] == 254:
                    card['willpower'] = 'X'

                key = 'WP {}'.format(card['willpower'])
                columns.add(key)
                row_dict[key] = row_dict.get(key, 0) + 1
                if is_int(card['willpower']):
                    min_values['WP'] = min(min_values.get('WP', 100),
                                           int(card['willpower']))
                    max_values['WP'] = max(max_values.get('WP', 0),
                                           int(card['willpower']))
                    row_dict['WP Count'] = row_dict.get('WP Count', 0) + 1
                    row_dict['WP Sum'] = (row_dict.get('WP Sum', 0) +
                                          int(card['willpower']))

            if 'attack' in card:
                key = 'Att {}'.format(card['attack'])
                columns.add(key)
                row_dict[key] = row_dict.get(key, 0) + 1
                if is_int(card['attack']):
                    min_values['Att'] = min(min_values.get('Att', 100),
                                            int(card['attack']))
                    max_values['Att'] = max(max_values.get('Att', 0),
                                            int(card['attack']))
                    row_dict['Att Count'] = row_dict.get('Att Count', 0) + 1
                    row_dict['Att Sum'] = (row_dict.get('Att Sum', 0) +
                                           int(card['attack']))

            if 'defense' in card:
                key = 'Def {}'.format(card['defense'])
                columns.add(key)
                row_dict[key] = row_dict.get(key, 0) + 1
                if is_int(card['defense']):
                    min_values['Def'] = min(min_values.get('Def', 100),
                                            int(card['defense']))
                    max_values['Def'] = max(max_values.get('Def', 0),
                                            int(card['defense']))
                    row_dict['Def Count'] = row_dict.get('Def Count', 0) + 1
                    row_dict['Def Sum'] = (row_dict.get('Def Sum', 0) +
                                           int(card['defense']))

            if 'health' in card:
                key = 'HP {}'.format(card['health'])
                columns.add(key)
                row_dict[key] = row_dict.get(key, 0) + 1
                if is_int(card['health']):
                    min_values['HP'] = min(min_values.get('HP', 100),
                                           int(card['health']))
                    max_values['HP'] = max(max_values.get('HP', 0),
                                           int(card['health']))
                    row_dict['HP Count'] = row_dict.get('HP Count', 0) + 1
                    row_dict['HP Sum'] = (row_dict.get('HP Sum', 0) +
                                          int(card['health']))

    for i in range(min_values['Thr'] + 1, max_values['Thr']):
        columns.add('Thr {}'.format(i))

    for i in range(min_values['Cost'] + 1, max_values['Cost']):
        columns.add('Cost {}'.format(i))

    for i in range(min_values['WP'] + 1, max_values['WP']):
        columns.add('WP {}'.format(i))

    for i in range(min_values['Att'] + 1, max_values['Att']):
        columns.add('Att {}'.format(i))

    for i in range(min_values['Def'] + 1, max_values['Def']):
        columns.add('Def {}'.format(i))

    for i in range(min_values['HP'] + 1, max_values['HP']):
        columns.add('HP {}'.format(i))

    columns = sorted(list(columns),
                     key=lambda c: (c != 'Avg Thr',
                                    c.split(' ')[0] != 'Thr',
                                    c != 'Avg Cost',
                                    c.split(' ')[0] != 'Cost',
                                    c != 'Avg WP',
                                    c.split(' ')[0] != 'WP',
                                    c != 'Avg Att',
                                    c.split(' ')[0] != 'Att',
                                    c != 'Avg Def',
                                    c.split(' ')[0] != 'Def',
                                    c != 'Avg HP',
                                    not is_int(c.split(' ')[1]),
                                    c.split(' ')[1] != 'X',
                                    handle_int(c.split(' ')[1])))
    file_path = os.path.join(OUTPUT_PATH, 'numbers.csv')
    with open(file_path, 'w', newline='', encoding='utf-8') as obj:
        obj.write(codecs.BOM_UTF8.decode('utf-8'))
        fieldnames = ['Type/Sphere', 'Total'] + columns
        writer = csv.DictWriter(obj, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            csv_row = {
                'Type/Sphere': row,
                'Total': res.get(row, {}).get('Total', 0)
            }
            for column in columns:
                if column.startswith('Avg '):
                    key = column.split(' ')[1]
                    key_sum = res.get(row, {}).get('{} Sum'.format(key), 0)
                    key_count = res.get(row, {}).get('{} Count'.format(key), 0)
                    if key_count > 0:
                        csv_row[column] = round(key_sum / key_count, 2)
                else:
                    csv_row[column] = res.get(row, {}).get(column, '')

            writer.writerow(csv_row)


def collect_traits(data):
    """ Collect traits statistics from Hall of Beorn.
    """
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

    for trait, trait_data in res.items():
        trait_data['Mentions'] = sorted([
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


def _transform_keyword(value):
    """ Transform a keyword value if needed.
    """
    value = re.sub(r' [0-9X]$', ' N', value)
    return value


def collect_keywords(data):
    """ Collect keywords statistics from Hall of Beorn.
    """
    keywords = [
        item for sublist in [
            [(_transform_keyword(t.strip()),
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
    data = get_hall_data()
    data = filter_hall_data(data)
    collect_spheres(data)
    collect_numbers(data)
    collect_traits(data)
    collect_keywords(data)
    print('Done')


def collect_scenarios():
    """ Collect scenarios statistics from Hall of Beorn.
    """
    create_folder(OUTPUT_SCENARIOS_PATH)
    html_data = get_content(HALLOFBEORN_SCENARIOS_URL).decode('utf-8')
    scenarios = re.findall(SCENARIOS_REGEX, html_data)
    cnt = 0
    for scenario in scenarios:
        scenario = html.unescape(scenario)
        url = HALLOFBEORN_SCENARIO_URL.format(scenario)
        data = get_content(url)
        try:
            json.loads(data)
        except Exception:  # pylint: disable=W0703
            print('Error collecting scenario data for {}'.format(scenario))
        else:
            cnt += 1
            path = os.path.join(OUTPUT_SCENARIOS_PATH,
                                '{}.json'.format(scenario))
            with open(path, 'wb') as obj:
                obj.write(data)

    print('Collected {} scenarios'.format(cnt))
    print('Done')


def create_ringsdb_csv(pack_name, pack_code):
    """ Get Hall of Beorn data and create a csv file for RingsDB.
    """
    data = get_hall_data()
    data = [c for c in data if c['pack_name'] == pack_name]
    file_path = os.path.join(OUTPUT_PATH, '{}.csv'.format(
        escape_filename(pack_name)))
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
            for key, value in row.items():
                if isinstance(value, str):
                    row[key] = value.replace('\r\n', '\n')

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
                'octgnid': row.get('octgnid', '') or uuid.uuid4(),
                'hasErrata': row.get('has_errata') and '1' or ''
                }
            writer.writerow(csv_row)

    print('Done')


def get_ringsdb_data():
    """ Get RingsDB data.
    """
    data = get_content(RINGSDB_URL)
    data = json.loads(data)
    return data


def create_dragncards_json(pack_name, pack_id):  # pylint: disable=R0912,R0914
    """ Get RingsDB data and create a json file for DragnCards.
    """
    source_data = get_ringsdb_data()
    cards = {}
    for row in source_data:
        if row['pack_code'] in ('Starter', 'DoD', 'EoL', 'DoG', 'RoR', 'MotKA',
                                'ALePMotKA'):
            continue

        if 'cost' in row:
            cost = str(row['cost'])
        elif 'threat' in row:
            cost = str(row['threat'])
        else:
            cost = ''

        key = (row['name'], row['type_name'], row['sphere_name'], cost)
        if key in cards:
            cards[key] = '{}, {}'.format(cards[key], row['octgnid'])
            print('Duplicate IDs for key {}: {}'.format(key, cards[key]))
        else:
            cards[key] = row['octgnid']

    data = [r for r in source_data if r['pack_name'] == pack_name]
    json_data = {}
    sh_data = ''
    for row in data:
        card_type = row['type_name']
        if card_type == 'Other':
            card_type = 'Contract'
        elif card_type == 'Campaign':
            card_type = 'Treasure'

        if 'cost' in row:
            cost = str(row['cost'])
        elif 'threat' in row:
            cost = str(row['threat'])
        else:
            cost = ''

        side_a = {
            'name': unidecode.unidecode(row['name'].replace("'", '’')),
            'printname': row['name'].replace("'", '’'),
            'unique': str(int(row['is_unique'])),
            'type': card_type,
            'sphere': row['sphere_name'],
            'traits': row['traits'],
            'keywords': '',
            'cost': cost,
            'engagementcost': '',
            'threat': '',
            'willpower': str(row.get('willpower', '')),
            'attack': str(row.get('attack', '')),
            'defense': str(row.get('defense', '')),
            'hitpoints': str(row.get('health', '')),
            'questpoints': str(row.get('quest', '')),
            'victorypoints': str(row.get('victory', '')),
            'text': re.sub(r'(?:<b>|<\/b>|<i>|<\/i>)', '', row['text']),
            'shadow': ''
        }

        side_b = {
            'name': 'player',
            'printname': 'player',
            'unique': '',
            'type': '',
            'sphere': '',
            'traits': '',
            'keywords': '',
            'cost': '',
            'engagementcost': '',
            'threat': '',
            'willpower': '',
            'attack': '',
            'defense': '',
            'hitpoints': '',
            'questpoints': '',
            'victorypoints': '',
            'text': '',
            'shadow': ''
        }

        card_data = {
            'sides': {
                'A': side_a,
                'B': side_b
            },
            'cardsetid': pack_id,
            'cardpackname': pack_name,
            'cardid': row['octgnid'],
            'cardnumber': str(row['position']),
            'cardquantity': str(row['quantity']),
            'cardencounterset': ''
        }
        json_data[row['octgnid']] = card_data

        key = (row['name'], row['type_name'], row['sphere_name'], cost)
        if key in cards:
            line = 'cp {}.jpg {}.jpg\n'.format(cards[key], row['octgnid'])
        else:
            line = '  No matching card found for {}\n'.format(key)

        sh_data += line

    file_path = os.path.join(OUTPUT_PATH, '{}.json'.format(
        escape_filename(pack_name)))
    with open(file_path, 'w', encoding='utf-8') as obj:
        res = json.dumps(json_data, ensure_ascii=True, indent=4)
        obj.write(res)

    file_path = os.path.join(OUTPUT_PATH, '{}.sh'.format(
        escape_filename(pack_name)))
    with open(file_path, 'w', encoding='utf-8') as obj:
        obj.write(sh_data)
    print('Done')


if __name__ == '__main__':
    collect_stat()
    collect_scenarios()
    # create_ringsdb_csv('Dwarves of Durin', '31')
    # create_dragncards_json('Dwarves of Durin', '5971cfbb-b5e4-40aa-be0f-3cc575141f18')
    # create_dragncards_json('Elves of Lórien', '1dffad96-4516-4da5-9b5c-31596784040f')
    # create_dragncards_json('Defenders of Gondor', 'a4ad9700-a391-4f7c-a239-f32bc1878eaa')
    # create_dragncards_json('Riders of Rohan', '5a5e23e5-455c-47eb-8275-bfc4b939f7f6')
