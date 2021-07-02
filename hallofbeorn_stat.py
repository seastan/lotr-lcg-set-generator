""" Collect various statistics from Hall of Beorn.
"""
import codecs
from collections import Counter
import csv
import json
import os
import re
import unidecode
from lotr import get_content


HALLOFBEORN_URL = 'http://hallofbeorn.com/Export/Cards?setType=ALL_SETS'
OUTPUT_PATH = os.path.join('Output', 'Scripts')


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
                'Two-Player Limited Edition Starter',
                'Fog on the Barrow-downs', 'The Old Forest',
                'Murder at the Prancing Pony', 'The Ruins of Belegost',
                'The Siege of Annúminas', 'Attack on Dol Guldur',
                'The Wizard\'s Quest', 'The Woodland Realm',
                'The Mines of Moria', 'Escape from Khazad-dûm',
                'First Age', 'Trial Upon the Marches', 'Among the Outlaws',
                'The Betrayal of Mîm', 'The Fall of Nargothrond')
            and 'Preorder Promotion' not in c['pack_name']
            and c.get('subtype_code') != 'boon'
            and c['sphere_name'] not in ('Baggins', 'Fellowship')]
    return data


def collect_traits(data):
    """ Collect traits statistics from Hall of Beorn.
    """
    data = filter_data(data)
    text = [(c['text'].replace('~', '')
             .replace('[leadership]', 'Leadership')
             .replace('[lore]', 'Lore')
             .replace('[spirit]', 'Spirit')
             .replace('[tactics]', 'Tactics')
             .replace(c['name'], '***')
             .replace(unidecode.unidecode(c['name']), '***')
             .replace('Ranger of the North', '***')
             .replace('Ring-bearer', '***')
             .replace('The One Ring', '***'),
             c['name']) for c in data]
    traits = [
        item for sublist in [
            [(t.strip(),
              'Character' if c['type_name'] in ('Hero', 'Ally')
              else c['type_name'],
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
            {'Total': 0, 'Character': 0, 'Attachment': 0, 'Event': 0,
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
        fieldnames = ['Trait', 'Total', 'Character', 'Attachment', 'Event',
                      'Leadership', 'Lore', 'Spirit', 'Tactics', 'Neutral',
                      'Mentions', 'Mentioned on Cards']
        writer = csv.DictWriter(obj, fieldnames=fieldnames)
        writer.writeheader()
        for row in res:
            csv_row = {
                'Trait': row[0],
                'Total': row[1]['Total'],
                'Character': row[1]['Character'] or '',
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


def main():
    """ Main function.
    """
    data = get_data()
    collect_traits(data)
    print('Done')


if __name__ == '__main__':
    main()
