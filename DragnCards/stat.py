# pylint: disable=C0209,W0703
# -*- coding: utf8 -*-
""" Collect DragnCards and RingsDB statistics.
"""
import calendar
import copy
import datetime
import json
import logging
import os
import re
import sys
import time

import psycopg2
import requests


LOG_PATH = 'stat.log'
LOG_LEVEL = logging.INFO

DRAGNCARDS_USER = 'postgres'
DRAGNCARDS_PASSWORD = 'postgres'
DRAGNCARDS_HOST = '127.0.0.1'
DRAGNCARDS_PORT = 5432
DRAGNCARDS_DATABASE = 'dragncards_prod'

RINGSDB_COOKIES_PATH = 'ringsdb_cookies.json'
RINGSDB_DATA_MOCK_PATH = 'ringsdb_data.mock'
RINGSDB_URL = 'https://ringsdb.com/admin/stat'

QUERY_LIMIT = 500
USE_RINGSDB_DATA_MOCK = False

CARD_TYPES_PLAYER = {'Ally', 'Attachment', 'Contract', 'Event', 'Hero',
                     'Player Objective', 'Player Side Quest', 'Treasure'}

IGNORE_ID = {
    '3e471bd0-5ee5-4846-815d-fd6a5cd5f921',  # Daybreak/Nightfall
    'beb13658-234c-44c2-9987-4dea3351184f'  # Stinker
}
PACK_ALIAS = {
    'Revised Core Set': 'Revised Core Set (Campaign Only)',
    'Revized Core Set': 'Revised Core Set (Campaign Only)',
    'Khazad-dum': 'Khazad-dûm',
    'The Hobbit - Over Hill and Under Hill': 'Over Hill and Under Hill',
    'The Battle of Lake-Town': 'The Battle of Lake-town',
    'Heirs of Numenor': 'Heirs of Númenor',
    'The Hobbit - On the Doorstep': 'On the Doorstep',
    'The Stewards Fear': "The Steward's Fear",
    'The Druadan Forest': 'The Drúadan Forest',
    'Encounter at Amon Din': 'Encounter at Amon Dîn',
    'Voice of Isengard': 'The Voice of Isengard',
    'Dark of Mirkwood': 'The Dark of Mirkwood',
    'The Nin-in-Eilph': 'The Nîn-in-Eilph',
    'Celebrimbors Secret': "Celebrimbor's Secret",
    'The Battle of Carn Dum': 'The Battle of Carn Dûm',
    'The Mumakil': 'The Mûmakil',
    'The Siege of Annuminas':  'The Siege of Annúminas',
    'The Wizards Quest': "The Wizard's Quest",
    'Escape from Khazad-dum': 'Escape from Khazad-dûm',
    'Shadows of Mirkwood': 'The Hunt for Gollum',
    'Dwarrowdelf': 'The Redhorn Gate',
    'Against the Shadow': "The Steward's Fear",
    'The Ring-maker': 'The Dunland Trap',
    'Ringmaker': 'The Dunland Trap',
    'Angmar Awakened': 'The Wastes of Eriador',
    'Dream-chaser': 'Flight of the Stormcaller',
    'Dreamchaser': 'Flight of the Stormcaller',
    'Dream-chaser Campaign Expansion': 'The City of Corsairs'
}


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(filename=LOG_PATH, level=LOG_LEVEL,
                        format='%(asctime)s %(levelname)s: %(message)s')


def get_last_month():
    """ Get last month in 'YYYY-MM' format.
    """
    last_month = (datetime.date.today().replace(day=1) -
                  datetime.timedelta(days=1))
    return last_month.strftime('%Y-%m')


def get_next_month(month):
    """ Get next month in 'YYYY-MM' format.
    """
    next_month = (datetime.date.fromisoformat('{}-01'.format(month)).replace(
        day=calendar.monthrange(
            *[int(i) for i in month.split('-')])[1]) +
                  datetime.timedelta(days=1))
    return next_month.strftime('%Y-%m')


def get_ringsdb_data(month):
    """ Get the data from RingsDB.
    """
    if USE_RINGSDB_DATA_MOCK:
        try:
            with open(RINGSDB_DATA_MOCK_PATH, 'r', encoding='utf-8') as fobj:
                return json.load(fobj)
        except Exception as exc:
            message = 'Reading RingsDB data mock failed: {}'.format(str(exc))
            logging.error(message)
            print(message)
            raise

    try:
        with open(RINGSDB_COOKIES_PATH, 'r', encoding='utf-8') as fobj:
            cookies = json.load(fobj)
    except Exception as exc:
        message = 'Reading RingsDB cookies failed: {}'.format(str(exc))
        logging.error(message)
        print(message)
        raise

    session = requests.Session()
    session.cookies.update(cookies)

    res = session.get('{}?month={}'.format(RINGSDB_URL, month))
    res = res.content.decode('utf-8')
    try:
        res = json.loads(res)
    except Exception as exc:
        message = 'Reading RingsDB data failed: {}'.format(str(exc))
        logging.error(message)
        print(message)
        raise

    cookies = session.cookies.get_dict()
    with open(RINGSDB_COOKIES_PATH, 'w', encoding='utf-8') as fobj:
        json.dump(cookies, fobj)

    return res


def process_dragncards_data(dragncards_data, ringsdb_data, packs, stat):  # pylint: disable=R0912,R0914,R0915
    """ Process raw records from DragnCards database.
    """
    for row in dragncards_data:
        ignore_replay = False
        cards = row[0]
        user = row[1]
        played_date = row[2].strftime('%Y-%m-%d')
        unreleased_packs = {p for p in packs if packs[p] > played_date}

        owners = {'player1': {},
                  'player2': {},
                  'player3': {},
                  'player4': {},
                  'shared': {}}
        for card in cards.values():
            if card['cardDbId'] in IGNORE_ID:
                continue

            player_card = card['sides']['A']['type'] in CARD_TYPES_PLAYER

            pack_name = card['cardPackName']
            if pack_name.startswith('Custom Set ') or not pack_name:
                pack_name = 'Custom Set'

            pack_name = pack_name.replace(' - Nightmare', '')
            pack_name = PACK_ALIAS.get(pack_name, pack_name)
            if pack_name not in packs or pack_name in unreleased_packs:
                if not (pack_name.startswith('ALeP ') or
                        pack_name in {'The Withered Heath Nightmare',
                                      'Escape from Umbar Nightmare'}):
                    message = 'Unknown pack detected: {}'.format(pack_name)
                    logging.error(message)
                    print(message)

                ignore_replay = True
                break

            owners[card['owner']][card['cardDbId']] = (pack_name,
                                                       player_card)

        if ignore_replay:
            continue

        card_ids = list(owners['shared'].keys())
        for card_id in card_ids:
            if owners['shared'][card_id][1]:
                if not (card_id in owners['player1'] or
                        card_id in owners['player2'] or
                        card_id in owners['player3'] or
                        card_id in owners['player4']):
                    owners['player1'][card_id] = owners['shared'][card_id]

                del owners['shared'][card_id]

        for owner in ('player1', 'player2', 'player3', 'player4'):
            card_ids = list(owners[owner].keys())
            for card_id in card_ids:
                if not owners[owner][card_id][1]:
                    owners['shared'][card_id] = owners[owner][card_id]
                    del owners[owner][card_id]

        if not owners['shared']:
            continue

        if not (owners['player1'] or owners['player2'] or owners['player3']
                or owners['player4']):
            continue

        for owner in owners.keys():  # pylint: disable=C0201,C0206
            if 'Custom Set' in {c[0] for c in owners[owner].values()}:
                owners[owner] = {}

        for owner, cards in owners.items():
            if cards:
                last_release_date = max(packs[c[0]] for c in cards.values())
                last_cycle = None
                for cycle in ringsdb_data['pack_rules']:
                    if (ringsdb_data['pack_rules'][cycle][0]
                            <= last_release_date
                            < ringsdb_data['pack_rules'][cycle][1]):
                        last_cycle = cycle
                        break

                if last_cycle:
                    if owner == 'shared':
                        stat['quests'].append((last_cycle, user))
                    else:
                        stat['decks'].append((last_cycle, user))
                else:
                    message = 'No cycle for the pack: {}'.format(pack_name)
                    logging.error(message)
                    print(message)


def get_dragncards_data(ringsdb_data, month):  # pylint: disable=R0914
    """ Get the data from DragnCards database.
    """
    next_month = get_next_month(month)
    packs = {p['name']: p['date_release'] for p in ringsdb_data['packs']}
    packs['Custom Set'] = '2000-01-01'
    stat = {'quests': [], 'decks': []}

    conn = psycopg2.connect(user=DRAGNCARDS_USER,
                            password=DRAGNCARDS_PASSWORD,
                            host=DRAGNCARDS_HOST,
                            port=DRAGNCARDS_PORT,
                            database=DRAGNCARDS_DATABASE)
    try:
        cursor = conn.cursor('replays')
        cursor.itersize = QUERY_LIMIT
        query = """
        SELECT game_json::json->'cardById' AS cards,
          "user",
          inserted_at
        FROM replays
        WHERE inserted_at BETWEEN '{}-01' AND '{}-01'
          AND rounds > 0
          AND (rounds > 1 OR outcome IN ('victory', 'defeat', 'incomplete'))
        """.format(month, next_month)
        cursor.execute(query)

        while True:
            dragncards_data = cursor.fetchmany(QUERY_LIMIT)
            logging.info('Obtained %s records from DragnCards database',
                         len(dragncards_data))
            process_dragncards_data(dragncards_data, ringsdb_data, packs,
                                    stat)
            if len(dragncards_data) < QUERY_LIMIT:
                break
    finally:
        conn.close()

    logging.info('Processed all records from DragnCards database')

    decks = {}
    users = {}
    for record in stat['decks']:
        decks[record[0]] = decks.get(record[0], 0) + 1
        users.setdefault(record[1], []).append(record[0])

    decks_users = {}
    for cycles in users.values():
        last_cycle = sorted(
            cycles,
            key=lambda c: ringsdb_data['pack_rules'][c][0], reverse=True)[0]
        decks_users[last_cycle] = decks_users.get(last_cycle, 0) + 1

    quests = {}
    users = {}
    for record in stat['quests']:
        quests[record[0]] = quests.get(record[0], 0) + 1
        users.setdefault(record[1], []).append(record[0])

    quests_users = {}
    for cycles in users.values():
        last_cycle = sorted(
            cycles,
            key=lambda c: ringsdb_data['pack_rules'][c][0], reverse=True)[0]
        quests_users[last_cycle] = quests_users.get(last_cycle, 0) + 1

    res = {'decks_created': copy.deepcopy(ringsdb_data['decks_created']),
           'decks_played': copy.deepcopy(ringsdb_data['decks_played']),
           'quests_played': copy.deepcopy(ringsdb_data['quests_played'])
          }
    for record in res['decks_played']:
        record['number_decks_dragncards'] = decks.get(record['cycle'], 0)
        record['number_users_dragncards'] = decks_users.get(record['cycle'], 0)

    for record in res['quests_played']:
        record['number_quests_dragncards'] = quests.get(record['cycle'], 0)
        record['number_users_dragncards'] = quests_users.get(record['cycle'], 0)

    return res


def main():
    """ Main function.
    """
    timestamp = time.time()
    if len(sys.argv) > 1:
        month = sys.argv[1]
        if not re.match(r'^[0-9]{4}-[0-9]{2}$', month):
            message = 'Incorrect month value: {}'.format(month)
            logging.error(message)
            print(message)
            raise ValueError(message)
    else:
        month = get_last_month()

    logging.info('Obtainining data for %s', month)
    ringsdb_data = get_ringsdb_data(month)
    logging.info('RingsDB data:')
    logging.info(ringsdb_data)
    res = get_dragncards_data(ringsdb_data, month)
    output = '{}'.format(month)
    for i in range(len(res['decks_created'])):
        output += ','
        output += ','.join(str(i) for i in [
            res['decks_created'][i]['number_decks'],
            res['decks_created'][i]['number_users'],
            res['decks_played'][i]['number_decks'],
            res['decks_played'][i]['number_users'],
            res['decks_played'][i]['number_decks_dragncards'],
            res['decks_played'][i]['number_users_dragncards'],
            res['quests_played'][i]['number_quests'],
            res['quests_played'][i]['number_users'],
            res['quests_played'][i]['number_quests_dragncards'],
            res['quests_played'][i]['number_users_dragncards']
        ])

    logging.info(output)
    print(output)
    logging.info('Done (%ss)', round(time.time() - timestamp, 3))


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
