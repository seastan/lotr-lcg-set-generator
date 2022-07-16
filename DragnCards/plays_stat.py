# pylint: disable=C0209
# -*- coding: utf8 -*-
""" Get aggregated plays statistics for the quest.
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

LOG_PATH = 'plays_stat.log'
QUEST_PATH = '/var/www/dragncards.com/Lord-of-the-Rings/o8g/Decks/Quests/QPT-AleP-Playtest/'

MIN_INSERTED_AT = '2022-01-01 00:00:00'


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
  AND rounds > 0
  AND (rounds > 1 OR outcome IN ('victory', 'defeat', 'incomplete'))
ORDER BY inserted_at
    """

    conn = psycopg2.connect(user=DRAGNCARDS_USER,
                            password=DRAGNCARDS_PASSWORD,
                            host=DRAGNCARDS_HOST,
                            port=DRAGNCARDS_PORT,
                            database=DRAGNCARDS_DATABASE)
    try:
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute(query, ('%{}'.format(quest), inserted_at))
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
        outcome_filter = {'victory', 'defeat', '-'}
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

        replay['num_players'] = str(replay['num_players'])
        if replay['outcome'] == 'incomplete':
            replay['outcome'] = '-'

        replay['player1_threat'] = replay['player_data']['player1']['threat']
        replay['player2_threat'] = replay['player_data']['player2']['threat']
        replay['player3_threat'] = replay['player_data']['player3']['threat']
        replay['player4_threat'] = replay['player_data']['player4']['threat']

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
