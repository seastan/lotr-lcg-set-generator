# pylint: disable=W0703,C0301
""" Cron for LotR ALeP workflow (Part 1, before Strange Eons).

NOTE: This script heavily relies on my existing smart home environment.

Create discord.yaml (see discord.default.yaml).

Setup rclone:

curl -L https://raw.github.com/pageauc/rclone4pi/master/rclone-install.sh | bash
rclone config

Setup a cron as:
*/2 * * * * flock -xn /home/homeassistant/lotr-lcg-set-generator/cron.lock -c 'python3 /home/homeassistant/lotr-lcg-set-generator/run_before_se_cron.py > /dev/null' 2>&1
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

import requests
import yaml

from lotr import LOG_LIMIT, SanityCheckError
from run_before_se import main


DISCORD_CONF_PATH = 'discord.yaml'
INTERNET_SENSOR_PATH = '/home/homeassistant/.homeassistant/internet_state'
LOG_PATH = 'cron.log'
MAIL_COUNTER_PATH = 'cron.cnt'
MAILS_PATH = '/home/homeassistant/.homeassistant/mails'
SANITY_CHECK_PATH = 'sanity_check.txt'
WORKING_DIRECTORY = '/home/homeassistant/lotr-lcg-set-generator/'

ERROR_SUBJECT_TEMPLATE = 'LotR ALeP Cron ERROR: {}'
SANITY_CHECK_SUBJECT_TEMPLATE = 'LotR ALeP Cron CHECK: {}'
WARNING_SUBJECT_TEMPLATE = 'LotR ALeP Cron WARNING: {}'
MAIL_QUOTA = 50
MESSAGE_SLEEP_TIME = 1


class DiscordResponseError(Exception):
    """ Discord Response error.
    """


class RCloneError(Exception):
    """ RClone error.
    """


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


def send_discord(message):
    """ Send a message to a Discord channel.
    """
    try:
        with open(DISCORD_CONF_PATH, 'r') as f_conf:
            conf = yaml.safe_load(f_conf)

        if conf.get('webhook_url'):
            chunks = []
            while len(message) > 1900:
                chunks.append(message[:1900])
                message = message[1900:]

            chunks.append(message)
            for i, chunk in enumerate(chunks):
                if i > 0:
                    time.sleep(MESSAGE_SLEEP_TIME)

                data = {'content': chunk}
                res = requests.post(conf['webhook_url'], json=data)
                res = res.content.decode('utf-8')
                if res != '':
                    raise DiscordResponseError(
                        'Non-empty response: {}'.format(res))

            return True
    except Exception as exc:
        message = 'Discord message failed: {}: {}'.format(
            type(exc).__name__, str(exc))[:LOG_LIMIT]
        logging.exception(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message))

    return False


def is_non_ascii(value):
    """ Check whether the string is ASCII only or not.
    """
    return not all(ord(c) < 128 for c in value)


def create_mail(subject, body=''):
    """ Create mail file.
    """
    if not check_mail_counter():
        return

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
    """ Sync folders to Google Drive.
    """
    res = subprocess.run('./rclone.sh', capture_output=True, shell=True,
                         check=True)
    stdout = res.stdout.decode('utf-8').strip()
    stderr = res.stderr.decode('utf-8').strip()
    logging.info('Rclone finished, stdout: %s, stderr: %s', stdout, stderr)
    if stdout != 'Done':
        raise RCloneError('RClone failed, stdout: {}, stderr: {}'.format(
            stdout, stderr))


def rclone_scratch():
    """ Sync scratch folders to Google Drive.
    """
    res = subprocess.run('./rclone_scratch.sh', capture_output=True,
                         shell=True, check=True)
    stdout = res.stdout.decode('utf-8').strip()
    stderr = res.stderr.decode('utf-8').strip()
    logging.info('Rclone Scratch finished, stdout: %s, stderr: %s',
                 stdout, stderr)
    if stdout != 'Done':
        raise RCloneError('RClone Scratch failed, stdout: {}, stderr: {}'
                          .format(stdout, stderr))


def run(conf=None):  # pylint: disable=R0912
    """ Main function.
    """
    cron_id = uuid.uuid4()
    logging.info('Started: %s', cron_id)
    sheet_changes = True
    scratch_changes = True
    try:  # pylint: disable=R1702
        if not internet_state():
            logging.warning('Internet is not available right now, exiting')
            return

        sheet_changes, scratch_changes = main(conf)

        if sheet_changes:
            if get_sanity_check_message():
                message = 'Sanity check passed'
                try:
                    if send_discord(message):
                        set_sanity_check_message('')
                        create_mail(SANITY_CHECK_SUBJECT_TEMPLATE.format(message))
                except Exception as exc_new:
                    logging.exception(str(exc_new)[:LOG_LIMIT])

            rclone()

        if scratch_changes:
            rclone_scratch()

    except SanityCheckError as exc:
        message = str(exc)[:LOG_LIMIT]
        logging.error(message)
        if message != get_sanity_check_message():
            try:
                if send_discord(message):
                    set_sanity_check_message(message)
                    create_mail(SANITY_CHECK_SUBJECT_TEMPLATE.format(message))
            except Exception as exc_new:
                logging.exception(str(exc_new)[:LOG_LIMIT])
    except Exception as exc:
        message = 'Script failed: {}: {}'.format(
            type(exc).__name__, str(exc))[:LOG_LIMIT]
        logging.exception(message)
        try:
            send_discord(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
        except Exception as exc_new:
            logging.exception(str(exc_new)[:LOG_LIMIT])
    finally:
        if not sheet_changes and not scratch_changes:
            logging.info('Finished (No Changes): %s', cron_id)
        else:
            logging.info('Finished: %s', cron_id)
        logging.info('')
        logging.info('')


if __name__ == '__main__':
    os.chdir(WORKING_DIRECTORY)
    init_logging()
    run()
