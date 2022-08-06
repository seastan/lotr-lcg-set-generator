# pylint: disable=C0209
# -*- coding: utf8 -*-
""" Get aggregated statistics for all released ALeP quests.
"""
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

LOG_PATH = 'quests_stat.log'
DEFAULT_START_DATE = '2021-09-01'


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')


def get_replays(quests):
    """ Get all replays for the quests from the database.
    """
    conditions = ["(encounter ILIKE '%{}' AND inserted_at >= '{}')".format(
        q[0], q[1]) for q in quests]
    condition = ' OR '.join(conditions)

    query = """
SELECT encounter AS quest,
  num_players,
  rounds,
  CASE WHEN outcome != '' THEN outcome ELSE 'incomplete' END AS outcome,
  game_json::json->>'playerData' AS player_data,
  player1_heroes,
  player2_heroes,
  player3_heroes,
  player4_heroes
FROM replays
WHERE ({})
  AND rounds > 0
  AND (rounds > 1 OR outcome IN ('victory', 'defeat', 'incomplete'))
    """.format(condition)

    conn = psycopg2.connect(user=DRAGNCARDS_USER,
                            password=DRAGNCARDS_PASSWORD,
                            host=DRAGNCARDS_HOST,
                            port=DRAGNCARDS_PORT,
                            database=DRAGNCARDS_DATABASE)
    try:
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute(query)
        res = cursor.fetchall()
        res = [dict(row) for row in res]
        return res
    finally:
        conn.close()


def prepare_row(replays, quest):
    """ Prepare statistics row.
    """
    selected = [r for r in replays
                if r['quest'].lower().endswith(quest.lower())]
    if selected:
        wins = [r for r in selected if r['outcome'] == 'victory']
        defeats = [r for r in selected if r['outcome'] == 'defeat']
        incomplete = [r for r in selected if r['outcome'] == 'incomplete']

        threats_win = []
        for replay in wins:
            threats_win.extend([replay['player1_threat'],
                                replay['player2_threat'],
                                replay['player3_threat'],
                                replay['player4_threat']])

        threats_win = [t for t in threats_win if t != 0]

        threats_defeat = []
        for replay in defeats:
            threats_defeat.extend([replay['player1_threat'],
                                   replay['player2_threat'],
                                   replay['player3_threat'],
                                   replay['player4_threat']])

        threats_defeat = [t for t in threats_defeat if t != 0]

        if len(quest) < 29:
            quest = quest + ' ' * (29 - len(quest))

        values = [quest,
                  len(selected),
                  len([r for r in selected if r['num_players'] == 1]),
                  len([r for r in selected if r['num_players'] > 1]),
                  len(wins),
                  len(defeats),
                  len(incomplete),
                  round(sum(r['rounds'] for r in wins) / len(wins), 1)
                  if wins else 0,
                  round(sum(r['rounds'] for r in defeats) / len(defeats), 1)
                  if defeats else 0,
                  round(sum(threats_win) / len(threats_win), 1)
                  if threats_win else 0,
                  round(sum(threats_defeat) / len(threats_defeat), 1)
                  if threats_defeat else 0
                  ]
    else:
        if len(quest) < 29:
            quest = quest + ' ' * (29 - len(quest))

        values = [quest, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    res = '\t'.join([str(v) for v in values])
    return (res, len(selected))


def main():
    """ Main function.
    """
    if len(sys.argv) <= 1 or not sys.argv[1]:
        res = 'no quests specified'
        logging.error(res)
        print(res)
        return

    quests = sys.argv[1].replace("'", "’").split(';')
    quests = [q.split('|') if '|' in q else (q, DEFAULT_START_DATE)
              for q in quests]

    quests_str = '; '.join('{} since {}'.format(q[0], q[1]) for q in quests)
    logging.info('Processing quests: %s', quests_str)
    replays = get_replays(quests)
    if not replays:
        res = 'no quests statistics found'
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

        replay['player1_threat'] = replay['player_data']['player1']['threat']
        replay['player2_threat'] = replay['player_data']['player2']['threat']
        replay['player3_threat'] = replay['player_data']['player3']['threat']
        replay['player4_threat'] = replay['player_data']['player4']['threat']

        filtered.append(replay)

    if not filtered:
        res = 'no quests statistics found'
        logging.info(res)
        print(res)
        return

    headers = ['quest\t\t\t\t', 'plays', 'solo', 'mp', 'win', 'loss', '-',
               'rnd W', 'rnd L', 'thr W', 'thr L']
    headers = '\t'.join(headers)

    res = []
    for quest in [q[0] for q in quests]:
        res.append(prepare_row(filtered, quest))

    res.sort(key=lambda r: r[1], reverse=True)
    res = '\n'.join([headers] + [r[0] for r in res])
    logging.info(res)
    print(res)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
