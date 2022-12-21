# pylint: disable=W0703,C0209
""" Monitor Wordpress web-site.
"""
from email.header import Header
import json
import logging
import os
import re
import time
import uuid
import warnings

import requests


ALERT_SUBJECT_TEMPLATE = 'LotR Wordpress Monitor ALERT: {}'
ERROR_SUBJECT_TEMPLATE = 'LotR Wordpress Monitor ERROR: {}'
LOG_LEVEL = logging.INFO
CONFIGURATION_PATH = 'mpc_monitor.json'
LOG_PATH = 'monitor_wordpress_site.log'
MAILS_PATH = 'mails'


warnings.filterwarnings('ignore', category=DeprecationWarning)


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


def run():
    """ Run the check.
    """
    with open(CONFIGURATION_PATH, 'r', encoding='utf-8') as fobj:
        conf = json.load(fobj)

    headers = {'Authorization': 'Bearer {}'.format(conf['wordpress_token'])}
    req = requests.get(conf['wordpress_url'], headers=headers, timeout=30)
    content = json.loads(req.content)
    if content.get('error') or not content.get('content'):
        logging.info('Wordpress web-site is unavailable, response:')
        logging.info(content)
        error = content.get('error', 'unknown error')
        if content.get('message'):
            error = '{}: {}'.format(error, content['message'])

        create_mail(ALERT_SUBJECT_TEMPLATE.format(error), content)
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
