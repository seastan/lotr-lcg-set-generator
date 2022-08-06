# pylint: disable=C0209
# -*- coding: utf8 -*-
""" Get all plays for the quest.
"""
from datetime import datetime
import json
import logging
import os
import sys

import psycopg2
from psycopg2 import extras

DRAGNCARDS_USER = 'postgres'
DRAGNCARDS_PASSWORD = 'postgres'
DRAGNCARDS_HOST = '127.0.0.1'
DRAGNCARDS_PORT = 5432
DRAGNCARDS_DATABASE = 'dragncards_prod'

LOG_PATH = 'all_plays.log'
LIMIT = 500
DEFAULT_START_DATE = '2021-09-01'


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')


def get_replays(quest, start_date, end_date):
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
  AND inserted_at < %s
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
        cursor.execute(query, ('%{}'.format(quest), start_date, end_date,
                               LIMIT))
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

    quest = sys.argv[1]

    if (len(sys.argv) > 2 and sys.argv[2] and
            sys.argv[2] > DEFAULT_START_DATE):
        start_date = sys.argv[2]
    else:
        start_date = DEFAULT_START_DATE

    if len(sys.argv) > 3 and sys.argv[3]:
        end_date = sys.argv[3]
    else:
        end_date = datetime.utcnow().date().strftime('%Y-%m-%d')

    logging.info('Processing %s between %s and %s', quest, start_date,
                 end_date)
    replays = get_replays(quest, start_date, end_date)
    if not replays:
        if start_date > DEFAULT_START_DATE:
            start_date_str = ' since {}'.format(start_date)
        else:
            start_date_str = ''

        res = 'no plays found for quest {}{}'.format(quest,
                                                     start_date_str)
        logging.info(res)
        print(res)
        return

    filtered = []
    for replay in replays:
        replay['player_data'] = json.loads(replay['player_data'])
        if (not replay['player_data']['player1']['threat'] or
                not replay['player1_heroes']):
            continue

        if replay['num_players'] == 4 and not replay['player4_heroes']:
            replay['num_players'] = 3

        if replay['num_players'] == 3 and not replay['player3_heroes']:
            replay['num_players'] = 2

        if replay['num_players'] == 2 and not replay['player2_heroes']:
            replay['num_players'] = 1

        filtered.append(replay)

    if not filtered:
        if start_date > DEFAULT_START_DATE:
            start_date_str = ' since {}'.format(start_date)
        else:
            start_date_str = ''

        res = 'no plays found for quest {}{}'.format(quest,
                                                     start_date_str)
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
    if len(threat_header) < max_threat_length:
        threat_header = (threat_header +
                         ' ' * (max_threat_length - len(threat_header)))

    headers = ['date       ', 'replay_id                           ',
               'P ', 'R ', 'res ', threat_header, 'heroes']
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
        if replay['outcome'] == 'victory':
            replay['outcome'] = 'win '
        elif replay['outcome'] == 'defeat':
            replay['outcome'] = 'loss'
        else:
            replay['outcome'] = '-   '

        replay['rounds'] = str(replay['rounds'])
        if len(replay['rounds']) < 2:
            replay['rounds'] = (replay['rounds'] +
                                ' ' * (2 - len(replay['rounds'])))

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

        if len(replay['threat']) < max_threat_length:
            replay['threat'] = (replay['threat'] + ' ' *
                                (max_threat_length - len(replay['threat'])))

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
