# pylint: disable=C0209
# -*- coding: utf8 -*-
""" Download replay JSON.
"""
import json
import sys

import psycopg2

DRAGNCARDS_USER = 'postgres'
DRAGNCARDS_PASSWORD = 'postgres'
DRAGNCARDS_HOST = '127.0.0.1'
DRAGNCARDS_PORT = 5432
DRAGNCARDS_DATABASE = 'dragncards_prod'


def main():
    """ Main function.
    """
    if len(sys.argv) <= 1:
        print('No replay ID or UUID specified')
        return

    param = sys.argv[1]

    conn = psycopg2.connect(user=DRAGNCARDS_USER,
                            password=DRAGNCARDS_PASSWORD,
                            host=DRAGNCARDS_HOST,
                            port=DRAGNCARDS_PORT,
                            database=DRAGNCARDS_DATABASE)
    try:
        cursor = conn.cursor()
        if '-' in param:
            query = """
            SELECT game_json
            FROM replays
            WHERE uuid = %s
            """
            cursor.execute(query, (param,))
        else:
            query = """
            SELECT game_json
            FROM replays
            WHERE id = %s
            """
            cursor.execute(query, (int(param),))

        res = cursor.fetchone()
        if res:
            res = json.dumps(res, ensure_ascii=True, indent=4)
            filename = '{}.json'.format(param)
            with open(filename, 'w', encoding='utf-8') as obj:
                obj.write(res)

            print('Downloaded replay JSON for {}'.format(param))
        else:
            print('No replay found for {}'.format(param))
    finally:
        conn.close()


if __name__ == '__main__':
    main()
