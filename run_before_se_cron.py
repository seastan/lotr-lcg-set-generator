# pylint: disable=W0703,C0301
""" Cron for LotR ALeP workflow (Part 1, before Strange Eons).

NOTE: This script heavily relies on my existing smart home environment.

Setup rclone:

curl -L https://raw.github.com/pageauc/rclone4pi/master/rclone-install.sh | bash
rclone confi

Setup a cron as:
*/5 * * * * flock -xn /home/homeassistant/lotr-lcg-set-generator/cron.lock -c 'python3 /home/homeassistant/lotr-lcg-set-generator/run_before_se_cron.py > /dev/null' 2>&1
"""
from datetime import datetime
from email.header import Header
import json
import logging
import os
import re
import subprocess
import time
import uuid

from lotr import SanityCheckError
from run_before_se import main as imported_main


INTERNET_SENSOR_PATH = '/home/homeassistant/.homeassistant/internet_state'
LOG_PATH = 'cron.log'
MAIL_COUNTER_PATH = 'cron.cnt'
MAILS_PATH = '/home/homeassistant/.homeassistant/mails'
SANITY_CHECK_PATH = 'sanity_check.txt'
WORKING_DIRECTORY = '/home/homeassistant/lotr-lcg-set-generator/'

ERROR_SUBJECT_TEMPLATE = 'LotR ALeP Cron ERROR: {}'
SANITY_CHECK_SUBJECT_TEMPLATE = 'LotR ALeP Cron: {}'
WARNING_SUBJECT_TEMPLATE = 'LotR ALeP Cron WARNING: {}'
MAIL_QUOTA = 50


class RCloneError(Exception):
    """ RClone error.
    """


def set_directory():
    """ Set working directory.
    """
    os.chdir(WORKING_DIRECTORY)


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')


def internet_state():
    """ Check external internet sensor.
    """
    try:
        with open(INTERNET_SENSOR_PATH, 'r') as obj:
            value = obj.read().strip()
            return value != 'off'
    except Exception as exc:
        message = str(exc)
        logging.warning(message)
        create_mail(WARNING_SUBJECT_TEMPLATE.format(message))
        return True


def get_sanity_check_message():
    """ Get the latest sanity check message.
    """
    try:
        with open(SANITY_CHECK_PATH, 'r') as obj:
            return obj.read().strip()
    except Exception:
        return ''


def set_sanity_check_message(message):
    """ Set a new sanity check message.
    """
    try:
        with open(SANITY_CHECK_PATH, 'w') as obj:
            obj.write(message)
    except Exception as exc:
        message = str(exc)
        logging.warning(message)
        create_mail(WARNING_SUBJECT_TEMPLATE.format(message))


def is_non_ascii(value):
    """ Check whether the string is ASCII only or not.
    """
    return not all(ord(c) < 128 for c in value)


def create_mail(subject, body=''):
    """ Create mail file.
    """
    increment_mail_counter()
    subject = re.sub(r'\s+', ' ', subject)
    if len(subject) > 200:
        subject = subject[:200] + '...'

    if is_non_ascii(subject):
        subject = Header(subject, 'utf8').encode()

    with open('{}/{}_{}'.format(MAILS_PATH, int(time.time()), uuid.uuid4()),
              'w') as fobj:
        json.dump({'subject': subject, 'body': body, 'html': False}, fobj)


def check_mail_counter():
    """ Check whether a new email may be sent or not.
    """
    today = datetime.today().strftime('%Y-%m-%d')
    try:
        with open(MAIL_COUNTER_PATH, 'r') as fobj:
            data = json.load(fobj)
    except Exception:
        data = {'day': today,
                'value': 0,
                'allowed': True}
        with open(MAIL_COUNTER_PATH, 'w') as fobj:
            json.dump(data, fobj)

        return True

    if today != data['day']:
        data = {'day': today,
                'value': 0,
                'allowed': True}
        with open(MAIL_COUNTER_PATH, 'w') as fobj:
            json.dump(data, fobj)

        return True

    if not data['allowed']:
        if data['value'] >= MAIL_QUOTA:
            return False

        data['allowed'] = True
        with open(MAIL_COUNTER_PATH, 'w') as fobj:
            json.dump(data, fobj)

        return True

    if data['value'] >= MAIL_QUOTA:
        data['allowed'] = False
        with open(MAIL_COUNTER_PATH, 'w') as fobj:
            json.dump(data, fobj)

        message = 'Mail quota exceeded: {}/{}'.format(data['value'] + 1,
                                                      MAIL_QUOTA)
        logging.warning(message)
        create_mail(WARNING_SUBJECT_TEMPLATE.format(message))
        return False

    return True


def increment_mail_counter():
    """ Increment mail counter.
    """
    try:
        with open(MAIL_COUNTER_PATH, 'r') as fobj:
            data = json.load(fobj)

        data['value'] += 1
        with open(MAIL_COUNTER_PATH, 'w') as fobj:
            json.dump(data, fobj)
    except Exception:
        pass


def rclone():
    """ Sync Google Drive.
    """
    res = subprocess.run('./rclone.sh', capture_output=True, shell=True,
                         check=True)
    stdout = res.stdout.decode('utf-8').strip()
    stderr = res.stderr.decode('utf-8').strip()
    logging.info('Rclone finished, stdout: %s, stderr: %s', stdout, stderr)
    if stdout != 'Done':
        raise RCloneError('RClone failed, stdout: {}, stderr: {}'.format(
            stdout, stderr))


def main():
    """ Main function.
    """
    try:
        if not internet_state():
            logging.info('Internet is not available right now, exiting')
            return

        if not check_mail_counter():
            return

        last_message = get_sanity_check_message()
        imported_main()
        if last_message:
            set_sanity_check_message('')
            create_mail(SANITY_CHECK_SUBJECT_TEMPLATE.format(
                'Sanity check passed'))

        rclone()
    except SanityCheckError as exc:
        message = str(exc)
        logging.error(message)
        if message != last_message:
            try:
                set_sanity_check_message(message)
                create_mail(SANITY_CHECK_SUBJECT_TEMPLATE.format(message))
            except Exception as exc_new:
                logging.error(str(exc_new))
    except Exception as exc:
        message = str(exc)
        logging.exception(message)
        try:
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
        except Exception as exc_new:
            logging.error(str(exc_new))


if __name__ == '__main__':
    set_directory()
    init_logging()
    main()
