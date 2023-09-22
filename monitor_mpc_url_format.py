# pylint: disable=W0703,C0209
""" Monitor MakePlayingCards URL format.
"""
from email.header import Header
import json
import logging
import os
import re
import time
import uuid
#import warnings

import requests


ALERT_SUBJECT_TEMPLATE = 'MPC URL Format Monitor ALERT: {}'
ERROR_SUBJECT_TEMPLATE = 'MPC URL Format Monitor ERROR: {}'
LOG_LEVEL = logging.INFO
CONFIGURATION_PATH = 'mpc_monitor.json'
LOG_PATH = 'monitor_mpc_url_format.log'
MAILS_PATH = 'mails'

EMAIL_LIMIT = 50000
LOG_LIMIT = 5000
URL_TEMPLATE = (
    'https://www.makeplayingcards.com/products/playingcard/design/'
    'dn_playingcards_front_dynamic.aspx?id={}')


#warnings.filterwarnings('ignore', category=DeprecationWarning)


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
        subject = Header(subject, 'utf-8').encode()

    path = os.path.join(MAILS_PATH,
                        '{}_{}'.format(int(time.time()), uuid.uuid4()))
    with open(path, 'w', encoding='utf-8') as fobj:
        json.dump({'subject': subject, 'body': body, 'html': False}, fobj)


def run():
    """ Run the check.
    """
    with open(CONFIGURATION_PATH, 'r', encoding='utf-8') as fobj:
        conf = json.load(fobj)

    if not conf['decks']:
        return

    deck_name = list(conf['decks'].keys())[0]
    deck_id = conf['decks'][deck_name]['deck_id']
    url = URL_TEMPLATE.format(deck_id)
    req = requests.get(url, timeout=30)
    res = req.content.decode('utf-8').strip()
    if deck_name not in res:
        message = 'MakePlayingCards URL for "{}" doesn\'t work'.format(
            deck_name)
        logging.info(message)
        logging.info(res[:LOG_LIMIT])
        create_mail(ALERT_SUBJECT_TEMPLATE.format(message), res[:EMAIL_LIMIT])
    else:
        logging.info('Success')


def main():
    """ Main function.
    """
    logging.info('Started')
    try:
        run()
    except Exception as exc:
        message = 'Script failed: {}: {}'.format(type(exc).__name__, str(exc))
        logging.exception(message)
        try:
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)
        except Exception as exc_new:
            logging.exception(str(exc_new))
    finally:
        logging.info('Finished')


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
