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
MAILS_PATH = 'mails'


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

    path = os.path.join(MAILS_PATH,
                        '{}_{}'.format(int(time.time()), uuid.uuid4()))
    with open(path, 'w') as fobj:
        json.dump({'subject': subject, 'body': body, 'html': False}, fobj)


def rclone_logs():
    """ Sync logs folder from Google Drive.
    """
    res = subprocess.run('./rclone_logs.sh', capture_output=True, shell=True,
                         check=True)
    stdout = res.stdout.decode('unicode-escape', errors='ignore').strip()
    stderr = res.stderr.decode('unicode-escape', errors='ignore').strip()
    logging.info('Rclone finished, stdout: %s, stderr: %s', stdout, stderr)
    if stdout != 'Done':
        raise RCloneError('RClone failed, stdout: {}, stderr: {}'.format(
            stdout, stderr))


def parse_logs(folder):
    """ Parse logs files for today.
    """
    res = subprocess.run('./remote_cron_log.sh {}'.format(folder),
                         capture_output=True, shell=True, check=True)
    stdout = res.stdout.decode('unicode-escape', errors='ignore').strip()
    stderr = res.stderr.decode('unicode-escape', errors='ignore').strip()
    if stderr:
        logging.error('Parsing logs finished with errors: stdout: %s, '
                      'stderr: %s', stdout, stderr)

    return stdout


def run():
    """ Run the check.
    """
    with open(lotr.CONFIGURATION_PATH, 'r') as f_conf:
        conf = yaml.safe_load(f_conf)

    rclone_logs()
    res = parse_logs(conf.get('remote_logs_path', ''))
    parts = res.split('\n', 1)
    if len(parts) > 1:
        errors = parts[1]
    else:
        errors = ''

    parts = parts[0].split(' ', 1)
    if len(parts) == 1 or not parts[0].isdigit():
        message = 'Incorrect parsing logs result: {}'.format(res)
        logging.error(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)
        return

    code, description = parts
    code = int(code)
    if 0 < code < 10:
        message = 'Missing remote logs: {}'.format(description)
        logging.error(message)
        if errors:
            logging.info('Log errors: %s', errors)

        create_mail(ERROR_SUBJECT_TEMPLATE.format(message), errors)
    elif 10 < code < 20:
        message = 'Failure: {}'.format(description)
        logging.info(message)
        if errors:
            logging.info('Log errors: %s', errors)

        create_mail(ALERT_SUBJECT_TEMPLATE.format(message), errors)
    elif 20 < code < 30:
        logging.info('Success: %s', description)
        if errors:
            logging.info('Log errors: %s', errors)
            message = 'Success with log errors: {}'.format(errors)
            create_mail(ALERT_SUBJECT_TEMPLATE.format(message), errors)
    else:
        message = 'Incorrect parsing logs result: {}'.format(res)
        logging.error(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)


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
