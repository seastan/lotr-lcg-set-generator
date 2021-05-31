# pylint: disable=W0703,C0301
""" Monitor remote pipeline.

NOTE: This script heavily relies on my existing smart home environment.

You need to setup rclone:

curl -L https://raw.github.com/pageauc/rclone4pi/master/rclone-install.sh | bash
rclone config

Setup a cron as:
6 6 * * *  python3 /home/homeassistant/lotr-lcg-set-generator/monitor_remote_pipeline.py >> /home/homeassistant/.homeassistant/cron.log 2>&1
"""
from email.header import Header
import json
import logging
import os
import re
import subprocess
import time
import uuid

import yaml
import lotr


ALERT_SUBJECT_TEMPLATE = 'LotR Remote Pipeline Monitor ALERT: {}'
ERROR_SUBJECT_TEMPLATE = 'LotR Remote Pipeline Monitor ERROR: {}'

LOG_PATH = 'monitor_remote_pipeline.log'
MAILS_PATH = '/home/homeassistant/.homeassistant/mails'
WORKING_DIRECTORY = '/home/homeassistant/lotr-lcg-set-generator/'


class RCloneError(Exception):
    """ RClone error.
    """


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
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

    with open('{}/{}_{}'.format(MAILS_PATH, int(time.time()), uuid.uuid4()),
              'w') as fobj:
        json.dump({'subject': subject, 'body': body, 'html': False}, fobj)


def rclone_logs():
    """ Sync logs folder from Google Drive.
    """
    res = subprocess.run('./rclone_logs.sh', capture_output=True, shell=True,
                         check=True)
    stdout = res.stdout.decode('utf-8').strip()
    stderr = res.stderr.decode('utf-8').strip()
    logging.info('Rclone finished, stdout: %s, stderr: %s', stdout, stderr)
    if stdout != 'Done':
        raise RCloneError('RClone failed, stdout: {}, stderr: {}'.format(
            stdout, stderr))


def run():
    """ Run the check.
    """
    with open(lotr.CONFIGURATION_PATH, 'r') as f_conf:
        conf = yaml.safe_load(f_conf)

    log_path = conf.get('remote_logs_path', '')
    rclone_logs()


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
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
        except Exception as exc_new:
            logging.exception(str(exc_new))
    finally:
        logging.info('Finished')


if __name__ == '__main__':
    os.chdir(WORKING_DIRECTORY)
    init_logging()
    main()
