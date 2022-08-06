# pylint: disable=C0209
# -*- coding: utf8 -*-
""" Get aggregated plays statistics for the quest.
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

LOG_PATH = 'plays_stat.log'
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
SELECT num_players,
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
    """

    conn = psycopg2.connect(user=DRAGNCARDS_USER,
                            password=DRAGNCARDS_PASSWORD,
                            host=DRAGNCARDS_HOST,
                            port=DRAGNCARDS_PORT,
                            database=DRAGNCARDS_DATABASE)
    try:
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute(query, ('%{}'.format(quest), start_date, end_date))
        res = cursor.fetchall()
        res = [dict(row) for row in res]
        return res
    finally:
        conn.close()


def prepare_row(replays, players, outcome):
    """ Prepare statistics row.
    """
    if players == '[any]':
        players_filter = {'1', '2', '3', '4'}
    else:
        players_filter = {players}

    if outcome == '[any]':
        outcome_filter = {'win', 'loss', '-'}
    else:
        outcome_filter = {outcome}

    selected = [r for r in replays if r['num_players'] in players_filter and
                r['outcome'] in outcome_filter]
    if not selected:
        return None

    threats = []
    for replay in selected:
        threats.extend([replay['player1_threat'], replay['player2_threat'],
                        replay['player3_threat'], replay['player4_threat']])

    threats = [t for t in threats if t != 0]
    values = [players,
              outcome,
              len(selected),
              min(r['rounds'] for r in selected),
              max(r['rounds'] for r in selected),
              round(sum(r['rounds'] for r in selected) / len(selected), 1),
              min(threats),
              max(threats),
              round(sum(threats) / len(threats), 1)
              ]
    res = '\t'.join([str(v) for v in values])
    return res


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

        replay['num_players'] = str(replay['num_players'])
        if replay['outcome'] == 'victory':
            replay['outcome'] = 'win'
        elif replay['outcome'] == 'defeat':
            replay['outcome'] = 'loss'
        else:
            replay['outcome'] = '-'

        replay['player1_threat'] = replay['player_data']['player1']['threat']
        replay['player2_threat'] = replay['player_data']['player2']['threat']
        replay['player3_threat'] = replay['player_data']['player3']['threat']
        replay['player4_threat'] = replay['player_data']['player4']['threat']

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

    headers = ['players', 'result', 'plays', 'rnd_min', 'rnd_max',
               'rnd_avg', 'thr_min', 'thr_max', 'thr_avg']
    headers = '\t'.join(headers)

    res = []
    for players in ('[any]', '1', '2', '3', '4'):
        for outcome in ('[any]', 'win', 'loss', '-'):
            row = prepare_row(filtered, players, outcome)
            if row:
                res.append(row)

    res = '\n'.join([headers] + res)
    logging.info(res)
    print(res)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
