# pylint: disable=C0209
# -*- coding: utf8 -*-
""" Get all plays for the quest.
"""
import json
import logging
import os
import re
import sys

import psycopg2
from psycopg2 import extras

DRAGNCARDS_USER = 'postgres'
DRAGNCARDS_PASSWORD = 'postgres'
DRAGNCARDS_HOST = '127.0.0.1'
DRAGNCARDS_PORT = 5432
DRAGNCARDS_DATABASE = 'dragncards_prod'

LOG_PATH = 'all_plays.log'
QUEST_PATH = '/var/www/dragncards.com/Lord-of-the-Rings/o8g/Decks/Quests/QPT-AleP-Playtest/'

LIMIT = 500
MIN_INSERTED_AT = '2021-09-01 00:00:00'


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')


def get_playtesting_quests():
    """ Get the names of all playtesting quests.
    """
    quests = set()
    for _, _, filenames in os.walk(QUEST_PATH):
        for filename in filenames:
            if not filename.endswith('.o8d'):
                continue

            quest = re.sub(r'(-playtest)?\.o8d$', '', filename.lower())
            parts = quest.split('-')
            if len(parts) < 2:
                continue

            quest = ' '.join(parts[1:])
            quest = re.sub(r'^alep +', '', quest)
            quest = re.sub(r'^alep +', '', quest)
            quests.add(quest)

        break

    return quests


def get_replays(quest, inserted_at):
    """ Get all replays for the quest from the database.
    """
    query = """
SELECT inserted_at,
  uuid,
  num_players,
  rounds,
  CASE WHEN outcome != '' THEN outcome ELSE 'incomplete' END AS outcome,
  game_json::json->>'playerData' AS player_data,
  player1_heroes,
  player2_heroes,
  player3_heroes,
  player4_heroes
FROM replays
WHERE encounter ILIKE %s
  AND inserted_at >= %s
  AND rounds > 0
  AND (rounds > 1 OR outcome IN ('victory', 'defeat', 'incomplete'))
ORDER BY inserted_at DESC
LIMIT %s
    """

    conn = psycopg2.connect(user=DRAGNCARDS_USER,
                            password=DRAGNCARDS_PASSWORD,
                            host=DRAGNCARDS_HOST,
                            port=DRAGNCARDS_PORT,
                            database=DRAGNCARDS_DATABASE)
    try:
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute(query, ('%{}'.format(quest), inserted_at, LIMIT))
        res = cursor.fetchall()
        res = [dict(row) for row in res]
        res.reverse()
        return res

    finally:
        conn.close()


def main():  # pylint: disable=R0912,R0915
    """ Main function.
    """
    if len(sys.argv) <= 1 or not sys.argv[1]:
        res = 'no quest specified'
        logging.error(res)
        print(res)
        return

    quest_raw = sys.argv[1]
    quest = quest_raw.lower().replace('-', ' ')
    quest = re.sub(r'^alep +', '', quest)
    quests = get_playtesting_quests()
    if quest not in quests:
        res = '{} is not a playtesting quest'.format(quest_raw)
        logging.error(res)
        print(res)
        return

    if (len(sys.argv) > 2 and sys.argv[2] and
            sys.argv[2] > MIN_INSERTED_AT):
        inserted_at = sys.argv[2]
    else:
        inserted_at = MIN_INSERTED_AT

    replays = get_replays(quest, inserted_at)
    if not replays:
        if inserted_at > MIN_INSERTED_AT:
            inserted_at_str = ' since {}'.format(inserted_at)
        else:
            inserted_at_str = ''

        res = 'no plays found for quest {}{}'.format(quest_raw,
                                                     inserted_at_str)
        logging.info(res)
        print(res)
        return

    filtered = []
    for replay in replays:
        replay['player_data'] = json.loads(replay['player_data'])
        if (not replay['player_data']['player1']['threat'] or
                not replay['player1_heroes']):
            continue

        if replay['num_players'] == 4 and (not replay['player2_heroes'] or
                                           not replay['player3_heroes'] or
                                           not replay['player4_heroes']):
            continue

        if replay['num_players'] == 3 and (not replay['player2_heroes'] or
                                           not replay['player3_heroes']):
            continue

        if replay['num_players'] == 2 and not replay['player2_heroes']:
            continue

        filtered.append(replay)

    if not filtered:
        if inserted_at > MIN_INSERTED_AT:
            inserted_at_str = ' since {}'.format(inserted_at)
        else:
            inserted_at_str = ''

        res = 'no plays found for quest {}{}'.format(quest_raw,
                                                     inserted_at_str)
        logging.info(res)
        print(res)
        return

    max_num_players = max(r['num_players'] for r in filtered)
    if max_num_players == 4:
        max_threat_length = 11
    elif max_num_players == 3:
        max_threat_length = 8
    else:
        max_threat_length = 6

    threat_header = 'threat'
    while len(threat_header) < max_threat_length:
        threat_header = '{} '.format(threat_header)

    headers = ['date       ', 'replay_id                           ',
               'P ', 'R ', 'outcome', threat_header, 'heroes']
    headers = ' '.join(headers)

    res = []
    for replay in filtered:
        replay['player1_threat'] = str(
            replay['player_data']['player1']['threat'])
        replay['player2_threat'] = str(
            replay['player_data']['player2']['threat'])
        replay['player3_threat'] = str(
            replay['player_data']['player3']['threat'])
        replay['player4_threat'] = str(
            replay['player_data']['player4']['threat'])

        replay['player1_heroes'] = ', '.join(replay['player1_heroes'])
        replay['player2_heroes'] = ', '.join(replay['player2_heroes'])
        replay['player3_heroes'] = ', '.join(replay['player3_heroes'])
        replay['player4_heroes'] = ', '.join(replay['player4_heroes'])

        replay['inserted_at'] = replay['inserted_at'].strftime('%Y-%m-%d ')
        if replay['outcome'] == 'incomplete':
            replay['outcome'] = '-      '
        elif replay['outcome'] == 'defeat':
            replay['outcome'] = 'defeat '

        replay['rounds'] = str(replay['rounds'])
        while len(replay['rounds']) < 2:
            replay['rounds'] = '{} '.format(replay['rounds'])

        if replay['num_players'] == 1:
            replay['threat'] = replay['player1_threat']
            replay['heroes'] = replay['player1_heroes']
        elif replay['num_players'] == 2:
            replay['threat'] = '|'.join([replay['player1_threat'],
                                         replay['player2_threat']])
            replay['heroes'] = '|'.join([replay['player1_heroes'],
                                         replay['player2_heroes']])
        elif replay['num_players'] == 3:
            replay['threat'] = '|'.join([replay['player1_threat'],
                                         replay['player2_threat'],
                                         replay['player3_threat']])
            replay['heroes'] = '|'.join([replay['player1_heroes'],
                                         replay['player2_heroes'],
                                         replay['player3_heroes']])
        else:
            replay['threat'] = '|'.join([replay['player1_threat'],
                                         replay['player2_threat'],
                                         replay['player3_threat'],
                                         replay['player4_threat']])
            replay['heroes'] = '|'.join([replay['player1_heroes'],
                                         replay['player2_heroes'],
                                         replay['player3_heroes'],
                                         replay['player4_heroes']])

        replay['num_players'] = '{} '.format(replay['num_players'])

        while len(replay['threat']) < max_threat_length:
            replay['threat'] = '{} '.format(replay['threat'])

        replay['heroes'] = replay['heroes'].replace(
            ' , ', ',').replace(', ', ',')

        values = [replay['inserted_at'],
                  replay['uuid'],
                  replay['num_players'],
                  replay['rounds'],
                  replay['outcome'],
                  replay['threat'],
                  replay['heroes']]
        res.append(' '.join(values))

    total = '\n{} plays in total.'.format(len(filtered))
    res = '\n'.join([headers] + res + [total])
    logging.info(res)
    print(res)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
