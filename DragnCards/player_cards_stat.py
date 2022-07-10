# pylint: disable=C0209
# -*- coding: utf8 -*-
""" Get aggregated statistics about player cards being playtested.
"""
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

LOG_PATH = 'player_cards_stat.log'

DEFAULT_START_DATE = '2021-10-01'


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')


def get_stat(card_ids, start_date):
    """ Get cards statistics from the database.
    """
    query = """
    SELECT card_id,
        decks,
        decks - multiplayer AS solo,
        multiplayer,
        victory,
        defeat,
        decks - victory - defeat AS incomplete,
        ROUND(avg_included::numeric, 2) AS avg_included,
        ROUND((avg_deck * 100 / avg_included)::numeric, 2) AS pct_deck,
        ROUND((avg_hand * 100 / avg_included)::numeric, 2) AS pct_hand,
        ROUND((avg_play * 100 / avg_included)::numeric, 2) AS pct_play,
        ROUND(((avg_included - avg_deck - avg_hand - avg_play) * 100 /
               avg_included)::numeric, 2) AS pct_out
    FROM (
        SELECT card_id,
            SUM(decks) AS decks,
            SUM(multiplayer) AS multiplayer,
            SUM(victory) AS victory,
            SUM(defeat) AS defeat,
            SUM(avg_included * decks) / SUM(decks) AS avg_included,
            SUM(avg_deck * decks) / SUM(decks) AS avg_deck,
            SUM(avg_hand * decks) / SUM(decks) AS avg_hand,
            SUM(avg_play * decks) / SUM(decks) AS avg_play
        FROM player_cards_stat
        WHERE stat_date >= %s
            AND card_id IN %s
        GROUP BY card_id
    ) t
    """

    conn = psycopg2.connect(user=DRAGNCARDS_USER,
                            password=DRAGNCARDS_PASSWORD,
                            host=DRAGNCARDS_HOST,
                            port=DRAGNCARDS_PORT,
                            database=DRAGNCARDS_DATABASE)
    try:
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute(query, (start_date, tuple(card_ids)))
        res = cursor.fetchall()
        res = [dict(row) for row in res]
        return res
    finally:
        conn.close()


def prepare_row_value(value):
    """ Prepare a row value.
    """
    if isinstance(value, str):
        return value

    if isinstance(value, int):
        return str(value)

    value = re.sub(r'\.?0+$', '', str(value))
    return value


def prepare_row(row):
    """ Prepare statistics row.
    """
    row = {k:prepare_row_value(v) for k, v in row.items()}
    values = [row['card_id'],
              row['decks'],
              row['solo'],
              row['multiplayer'],
              row['victory'],
              row['defeat'],
              row['incomplete'],
              row['avg_included'],
              '{}%'.format(row['pct_deck']),
              '{}%'.format(row['pct_hand']),
              '{}%'.format(row['pct_play']),
              '{}%'.format(row['pct_out'])
              ]
    res = '\t'.join(values)
    return res


def main():
    """ Main function.
    """
    if len(sys.argv) <= 1 or not sys.argv[1]:
        res = 'no player cards specified'
        logging.error(res)
        print(res)
        return

    card_ids = sys.argv[1].split(',')
    if (len(sys.argv) > 2 and sys.argv[2] and
            sys.argv[2] > DEFAULT_START_DATE):
        start_date = sys.argv[2]
    else:
        start_date = DEFAULT_START_DATE

    data = get_stat(card_ids, start_date)
    if not data:
        if start_date > DEFAULT_START_DATE:
            start_date_str = ' since {}'.format(start_date)
        else:
            start_date_str = ''

        res = 'no player cards statistics found{}'.format(start_date_str)
        logging.info(res)
        print(res)
        return

    headers = ['card\t\t\t\t', 'plays', 'solo', 'mplayer', 'victory',
               'defeat', '-', 'copies', 'deck', 'hand', 'play', 'other']
    headers = '\t'.join(headers)

    found_card_ids = [r['card_id'] for r in data]
    for card_id in card_ids:
        if card_id not in found_card_ids:
            row = {'card_id': card_id,
                   'decks': 0,
                   'solo': 0,
                   'multiplayer': 0,
                   'victory': 0,
                   'defeat': 0,
                   'incomplete': 0,
                   'avg_included': 0,
                   'pct_deck': 0,
                   'pct_hand': 0,
                   'pct_play': 0,
                   'pct_out': 0
                   }
            data.append(row)

    res = []
    for row in data:
        res.append(prepare_row(row))

    res = '\n'.join([headers] + res)
    logging.info(res)
    print(res)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
