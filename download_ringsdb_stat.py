# pylint: disable=C0209
# -*- coding: utf8 -*-
""" Download RingsDB statistics.
"""
from email.header import Header
import json
import logging
import os
import re
import time
import uuid

import requests


ERROR_SUBJECT_TEMPLATE = 'Download RingsDB Stat Cron ERROR: {}'
LOG_PATH = 'download_ringsdb_stat.log'
LOG_LEVEL = logging.INFO
MAILS_PATH = 'mails'
OUTPUT_PATH = os.path.join('Data', 'ringsdb_stat.json')

RINGSDB_COOKIES_PATH = 'ringsdb_prod_cookies.json'
RINGSDB_URL = 'https://ringsdb.com/admin/stat_packs'


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(filename=LOG_PATH, level=LOG_LEVEL,
                        format='%(asctime)s %(levelname)s: %(message)s')


def is_non_ascii(value):
    """ Check whether the string is ASCII only or not.
    """
    return not all(ord(c) < 128 for c in value)


def create_mail(subject, body=''):
    """ Create mail file.
    """
    subject = re.sub(r'\s+', ' ', subject)
    if len(subject) > 200:
        subject = subject[:200] + '...'

    if is_non_ascii(subject):
        subject = Header(subject, 'utf8').encode()

    path = os.path.join(MAILS_PATH,
                        '{}_{}'.format(int(time.time()), uuid.uuid4()))
    with open(path, 'w', encoding='utf-8') as fobj:
        json.dump({'subject': subject, 'body': body, 'html': False}, fobj)


def get_ringsdb_data():
    """ Get the data from RingsDB.
    """
    try:
        with open(RINGSDB_COOKIES_PATH, 'r', encoding='utf-8') as fobj:
            cookies = json.load(fobj)
    except Exception as exc:
        message = 'Reading RingsDB cookies failed: {}'.format(str(exc))
        logging.error(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
        raise

    session = requests.Session()
    session.cookies.update(cookies)

    try:
        res = session.get(RINGSDB_URL)
        res = res.content.decode('utf-8')
        logging.info('RingsDB answer: %s', res[:100])
        res = json.loads(res)
    except Exception as exc:
        message = 'Reading RingsDB data failed: {}'.format(str(exc))
        logging.error(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
        raise

    cookies = session.cookies.get_dict()
    with open(RINGSDB_COOKIES_PATH, 'w', encoding='utf-8') as fobj:
        json.dump(cookies, fobj)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as fobj:
        json.dump(res, fobj)


def main():
    """ Main function.
    """
    timestamp = time.time()
    get_ringsdb_data()
    logging.info('Done (%ss)', round(time.time() - timestamp, 3))


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
