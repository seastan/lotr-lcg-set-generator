# pylint: disable=C0209,W0703
# -*- coding: utf8 -*-
""" Collect statistics about player cards being playtested.
"""
import datetime
import json
import logging
import os
import re
import time

import psycopg2


JSON_PATH = '/var/www/dragncards.com/dragncards/frontend/src/cardDB/ALeP/'
LOG_PATH = 'player_cards_stat.log'
LOG_LEVEL = logging.INFO

DRAGNCARDS_USER = 'postgres'
DRAGNCARDS_PASSWORD = 'postgres'
DRAGNCARDS_HOST = '127.0.0.1'
DRAGNCARDS_PORT = 5432
DRAGNCARDS_DATABASE = 'dragncards_prod'

DEFAULT_START_DATE = '2021-10-01'
CARD_TYPES_PLAYER = {'Ally', 'Attachment', 'Contract', 'Event', 'Hero',
                     'Player Objective', 'Player Side Quest', 'Treasure'}

def init_logging():
    """ Init logging.
    """
    logging.basicConfig(filename=LOG_PATH, level=LOG_LEVEL,
                        format='%(asctime)s %(levelname)s: %(message)s')


def get_playtest_cards():
    """ Get the names of all player cards being playtested.
    """
    playtest_cards = set()
    for _, _, filenames in os.walk(JSON_PATH):
        for filename in filenames:
            if not filename.endswith('.json'):
                continue

            with open(os.path.join(JSON_PATH, filename), 'r',
                      encoding='utf-8') as fobj:
                try:
                    cards = json.load(fobj)
                except Exception as exc:
                    logging.error('Error parsing %s: %s', filename, str(exc))
                    continue

            if not cards:
                continue

            first_card = list(cards.values())[0]
            if first_card.get('playtest') != 1:
                continue

            for card in cards.values():
                if card['sides']['A']['type'] in CARD_TYPES_PLAYER:
                    playtest_cards.add(card['cardid'])

        break

    return playtest_cards


def create_table(cursor):
    """ Create the table if it doesn't exist yet.
    """
    query = """
    CREATE TABLE IF NOT EXISTS player_cards_stat (
        id SERIAL PRIMARY KEY,
        card_id VARCHAR(255) NOT NULL,
        decks INTEGER NOT NULL,
        multiplayer INTEGER NOT NULL,
        victory INTEGER NOT NULL,
        defeat INTEGER NOT NULL,
        avg_included DOUBLE PRECISION NOT NULL,
        avg_deck DOUBLE PRECISION NOT NULL,
        avg_hand DOUBLE PRECISION NOT NULL,
        avg_play DOUBLE PRECISION NOT NULL,
        stat_date DATE NOT NULL,
        CONSTRAINT idx_player_cards_stat_unique UNIQUE (card_id, stat_date)
    )
    """
    cursor.execute(query)

    query = """
    CREATE INDEX IF NOT EXISTS idx_player_cards_stat_stat_date
    ON player_cards_stat(stat_date)
    """
    cursor.execute(query)


def get_start_date(cursor):
    """ Get the start date to collect statistics for.
    """
    query = """
    SELECT MAX(stat_date)
    FROM player_cards_stat
    """
    cursor.execute(query)
    res = cursor.fetchone()
    if res and res[0]:
        res = res[0] + datetime.timedelta(days=1)
    else:
        res = datetime.datetime.strptime(DEFAULT_START_DATE, '%Y-%m-%d')

    res = res.date()
    return res


def get_end_date():
    """ Get the end date to collect statistics for.
    """
    res = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    res = res.date()
    return res


def get_dragncards_data(cursor, stat_date):
    """ Get DragnCards data for a particular date.
    """
    start_time = '{} 00:00:00'.format(stat_date.strftime('%Y-%m-%d'))
    end_time = '{} 23:59:59'.format(stat_date.strftime('%Y-%m-%d'))
    query = """
    SELECT game_json::json->'cardById' AS cards,
        game_json::json->'groupById' AS groups,
        game_json::json->'stackById' AS stacks,
        num_players > 1 AS multiplayer,
        CASE WHEN outcome != '' THEN outcome ELSE 'incomplete' END AS outcome
    FROM replays
    WHERE inserted_at >= %s
        AND inserted_at <= %s
        AND rounds > 0
        AND (rounds > 1 OR outcome IN ('victory', 'defeat', 'incomplete'))
    """
    cursor.execute(query, (start_time, end_time))
    res = cursor.fetchall()
    res = [{'cards': r[0], 'groups': r[1], 'stacks': r[2], 'multiplayer': r[3],
            'outcome': r[4]} for r in res]
    return res


def insert_stat(cursor, values):
    """ Get DragnCards data for a particular date.
    """
    values = ['({})'.format(','.join(["'{}'".format(v['card_id'].replace("'", '')),
                                      str(v['decks']),
                                      str(v['multiplayer']),
                                      str(v['victory']),
                                      str(v['defeat']),
                                      str(v['avg_included']),
                                      str(v['avg_deck']),
                                      str(v['avg_hand']),
                                      str(v['avg_play']),
                                      "'{}'".format(str(v['stat_date']))]))
              for v in values]
    query = """
    INSERT INTO player_cards_stat
        (card_id, decks, multiplayer, victory, defeat, avg_included, avg_deck,
         avg_hand, avg_play, stat_date)
    VALUES {}
    """.format(','.join(values))
    cursor.execute(query)


def process_stat_date(cursor, stat_date, playtest_cards):  # pylint: disable=R0912,R0914,R0915
    """ Collect statistics for a particular date.
    """
    logging.info('Processing %s', stat_date)
    data = get_dragncards_data(cursor, stat_date)
    if not data:
        logging.info('No DragnCards plays for %s', stat_date)
        return

    logging.info('Found %s DragnCards plays for %s', len(data), stat_date)
    res = {}
    for row in data:
        stacks = {'deck': set(),
                  'hand': set(),
                  'play': set(),
                  'discard': set()}
        areas = {'deck': set(),
                 'hand': set(),
                 'play': set(),
                 'discard': set()}

        for group in row['groups'].values():
            if re.match(r'^player[1-4]Sideboard$', group['id']):
                continue

            if re.match(r'^player[1-4]Event$', group['id']):
                stacks['discard'] = stacks['discard'].union(
                    set(group['stackIds']))
            elif group['id'].startswith('shared') and group['type'] == 'deck':
                stacks['discard'] = stacks['discard'].union(
                    set(group['stackIds']))
            else:
                stacks[group['type']] = stacks[group['type']].union(
                    set(group['stackIds']))

        for stack in row['stacks'].values():
            for area, stack_ids in stacks.items():
                if stack['id'] in stack_ids:
                    areas[area] = areas[area].union(set(stack['cardIds']))
                    break

        owners = {'player1': {},
                  'player2': {},
                  'player3': {},
                  'player4': {},
                  'shared': {}}
        for card in row['cards'].values():
            if card['cardDbId'] not in playtest_cards:
                continue

            card_deck = False
            card_hand = False
            card_play = False
            if card['id'] in areas['deck']:
                card_deck = True
            elif card['id'] in areas['hand']:
                card_hand = True
            elif card['id'] in areas['play']:
                card_play = True
            elif card['id'] in areas['discard']:
                pass
            else:
                continue

            owners[card['owner']].setdefault(card['cardDbId'], []).append(
                {'deck': card_deck, 'hand': card_hand, 'play': card_play})

        for card_id, card_stat in owners['shared'].items():
            if card_id in owners['player2']:
                owners['player2'][card_id].extend(card_stat)
            elif card_id in owners['player3']:
                owners['player3'][card_id].extend(card_stat)
            elif card_id in owners['player4']:
                owners['player4'][card_id].extend(card_stat)
            else:
                owners['player1'].setdefault(card_id, []).extend(card_stat)

            if len(owners['player1'].get(card_id, [])) > 3:
                owners['player1'][card_id] = owners['player1'][card_id][:3]

            if len(owners['player2'].get(card_id, [])) > 3:
                owners['player2'][card_id] = owners['player2'][card_id][:3]

            if len(owners['player3'].get(card_id, [])) > 3:
                owners['player3'][card_id] = owners['player3'][card_id][:3]

            if len(owners['player4'].get(card_id, [])) > 3:
                owners['player4'][card_id] = owners['player4'][card_id][:3]

        for cards in owners.values():
            if not cards:
                continue

            for card_id, card_stat in cards.items():
                res.setdefault(card_id, []).append({
                    'multiplayer': row['multiplayer'],
                    'outcome': row['outcome'],
                    'included': len(card_stat),
                    'deck': len([c for c in card_stat if c['deck']]),
                    'hand': len([c for c in card_stat if c['hand']]),
                    'play': len([c for c in card_stat if c['play']])
                })

    if not res:
        logging.info('No playtest statistics for %s', stat_date)
        return

    logging.info('Found playtest statistics for %s card(s) for %s',
                 len(res), stat_date)
    values = []
    for card_id, card_stat in res.items():
        decks = len(card_stat)
        if not decks:
            continue

        values.append({
            'card_id': card_id,
            'decks': len(card_stat),
            'multiplayer': len([c for c in card_stat if c['multiplayer']]),
            'victory': len([c for c in card_stat
                            if c['outcome'] == 'victory']),
            'defeat': len([c for c in card_stat
                           if c['outcome'] == 'defeat']),
            'avg_included': round(sum(c['included'] for c in card_stat) /
                                  decks, 2),
            'avg_deck': round(sum(c['deck'] for c in card_stat) /
                              decks, 2),
            'avg_hand': round(sum(c['hand'] for c in card_stat) /
                              decks, 2),
            'avg_play': round(sum(c['play'] for c in card_stat) /
                              decks, 2),
            'stat_date': stat_date
        })

    logging.info(values)
    insert_stat(cursor, values)


def main():
    """ Main function.
    """
    logging.info('Starting the script')
    timestamp = time.time()
    try:
        playtest_cards = get_playtest_cards()
        logging.info('Collected %s playtest card(s)', len(playtest_cards))
        if not playtest_cards:
            logging.info('No playtest cards, exiting')
            return

        conn = psycopg2.connect(user=DRAGNCARDS_USER,
                                password=DRAGNCARDS_PASSWORD,
                                host=DRAGNCARDS_HOST,
                                port=DRAGNCARDS_PORT,
                                database=DRAGNCARDS_DATABASE)
        try:
            conn.autocommit = True
            cursor = conn.cursor()
            create_table(cursor)
            start_date = get_start_date(cursor)
            end_date = get_end_date()
            while start_date <= end_date:
                process_stat_date(cursor, start_date, playtest_cards)
                start_date += datetime.timedelta(days=1)
        finally:
            conn.close()

        logging.info('Done (%ss)', round(time.time() - timestamp, 3))
    except Exception as exc:
        logging.exception('Script failed: %s: %s', type(exc).__name__, str(exc))


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
