# pylint: disable=W0703,C0209,C0301
""" Cron for LotR workflow (Part 1).

NOTE: It's not run as a cron anymore, see `run_before_se_service.py`.
"""
import copy
from datetime import datetime
from email.header import Header
import json
import logging
import os
import re
import subprocess
import sys
import time
import uuid

import requests
import yaml

import common
from lotr import (DATA_PATH, LOG_LIMIT, SANITY_CHECK_PATH, SanityCheckError,
                  read_conf)
from run_before_se import main


DISCORD_CONF_PATH = 'discord.yaml'
INTERNET_SENSOR_PATH = 'internet_state'
LOG_PATH = 'run_before_se.log'
MAIL_COUNTER_PATH = os.path.join(DATA_PATH, 'run_before_se.cnt')
MAILS_PATH = 'mails'

ERROR_SUBJECT_TEMPLATE = 'LotR Cron ERROR: {}'
SANITY_CHECK_SUBJECT_TEMPLATE = 'LotR Cron CHECK: {}'
WARNING_SUBJECT_TEMPLATE = 'LotR Cron WARNING: {}'
MAIL_QUOTA = 50

LOG_LEVEL = logging.INFO


class DiscordResponseError(Exception):
    """ Discord Response error.
    """


class RCloneError(Exception):
    """ RClone error.
    """


class LoggerWriter:
    """ Custom writer to redirect stdout/stderr to existing logging.
    """
    def __init__(self, level):
        self.level = level

    def write(self, message):
        """ Write data.
        """
        if message and message != '\n':
            self.level(message)

    def flush(self):
        """ Flush data.
        """


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(filename=LOG_PATH, level=LOG_LEVEL,
                        format='%(asctime)s %(levelname)s: %(message)s')
    sys.stdout = LoggerWriter(logging.info)
    sys.stderr = LoggerWriter(logging.warning)


def internet_state():
    """ Check external internet sensor.
    """
    if not os.path.exists(INTERNET_SENSOR_PATH):
        return True

    try:
        with open(INTERNET_SENSOR_PATH, 'r', encoding='utf-8') as obj:
            value = obj.read()
            return value.strip() != 'off'
    except Exception as exc:
        message = str(exc)
        logging.warning(message)
        create_mail(WARNING_SUBJECT_TEMPLATE.format(message))
        return True


def get_sanity_check_message():
    """ Get the latest sanity check message.
    """
    try:
        with open(SANITY_CHECK_PATH, 'r', encoding='utf-8') as obj:
            return obj.read()
    except Exception:
        return ''


def set_sanity_check_message(message):
    """ Set a new sanity check message.
    """
    try:
        with open(SANITY_CHECK_PATH, 'w', encoding='utf-8') as obj:
            obj.write(message)
    except Exception as exc:
        message = str(exc)
        logging.warning(message)
        create_mail(WARNING_SUBJECT_TEMPLATE.format(message))


def send_discord(message):
    """ Send a message to a Discord channel.
    """
    try:  # pylint: disable=R1702
        with open(DISCORD_CONF_PATH, 'r', encoding='utf-8') as f_conf:
            conf = yaml.safe_load(f_conf)

        if conf.get('webhook_url'):
            for i, chunk in enumerate(common.split_result(message)):
                if i > 0:
                    time.sleep(1)

                data = {'content': chunk}
                res = requests.post(conf['webhook_url'], json=data)
                res = res.content.decode('utf-8')
                if res != '':
                    raise DiscordResponseError(
                        'Non-empty response: {}'.format(res))

            return True
    except Exception as exc:
        message = 'Discord message failed: {}: {}'.format(
            type(exc).__name__, str(exc))
        logging.exception(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)

    return False


def is_non_ascii(value):
    """ Check whether the string is ASCII only or not.
    """
    return not all(ord(c) < 128 for c in value)


def create_mail(subject, body='', skip_check=False):
    """ Create mail file.
    """
    if not skip_check and not check_mail_counter():
        return

    increment_mail_counter()
    subject = re.sub(r'\s+', ' ', subject)
    if len(subject) > 200:
        subject = subject[:200] + '...'

    if is_non_ascii(subject):
        subject = Header(subject, 'utf-8').encode()

    path = os.path.join(MAILS_PATH,
                        '{}_{}'.format(int(time.time()), uuid.uuid4()))
    with open(path, 'w', encoding='utf-8') as fobj:
        json.dump({'subject': subject, 'body': body, 'html': False}, fobj)


def check_mail_counter():
    """ Check whether a new email may be sent or not.
    """
    today = datetime.today().strftime('%Y-%m-%d')
    try:
        with open(MAIL_COUNTER_PATH, 'r', encoding='utf-8') as fobj:
            data = json.load(fobj)
    except Exception:
        data = {'day': today,
                'value': 0,
                'allowed': True}
        with open(MAIL_COUNTER_PATH, 'w', encoding='utf-8') as fobj:
            json.dump(data, fobj)

        return True

    if today != data['day']:
        data = {'day': today,
                'value': 0,
                'allowed': True}
        with open(MAIL_COUNTER_PATH, 'w', encoding='utf-8') as fobj:
            json.dump(data, fobj)

        return True

    if not data['allowed']:
        if data['value'] >= MAIL_QUOTA:
            return False

        data['allowed'] = True
        with open(MAIL_COUNTER_PATH, 'w', encoding='utf-8') as fobj:
            json.dump(data, fobj)

        return True

    if data['value'] >= MAIL_QUOTA:
        data['allowed'] = False
        with open(MAIL_COUNTER_PATH, 'w', encoding='utf-8') as fobj:
            json.dump(data, fobj)

        message = 'Mail quota exceeded: {}/{}'.format(data['value'] + 1,
                                                      MAIL_QUOTA)
        logging.warning(message)
        create_mail(WARNING_SUBJECT_TEMPLATE.format(message), skip_check=True)
        return False

    return True


def increment_mail_counter():
    """ Increment mail counter.
    """
    try:
        with open(MAIL_COUNTER_PATH, 'r', encoding='utf-8') as fobj:
            data = json.load(fobj)

        data['value'] += 1
        with open(MAIL_COUNTER_PATH, 'w', encoding='utf-8') as fobj:
            json.dump(data, fobj)
    except Exception:
        pass


def rclone(conf):
    """ Sync folders to Google Drive.
    """
    res = subprocess.run(
        './rclone_octgn.sh "{}" "{}"'.format(
            conf['octgn_set_xml_destination_path'],
            conf['octgn_o8d_destination_path']),
        capture_output=True, shell=True, check=True)
    stdout = res.stdout.decode('utf-8').strip()
    stderr = res.stderr.decode('utf-8').strip()
    logging.info('Rclone finished, stdout: %s, stderr: %s', stdout, stderr)
    if stdout != 'Done':
        raise RCloneError('RClone failed, stdout: {}, stderr: {}'.format(
            stdout, stderr))


def rclone_scratch(conf):
    """ Sync scratch folders to Google Drive.
    """
    res = subprocess.run(
        './rclone_octgn_scratch.sh "{}" "{}"'.format(
            conf['octgn_set_xml_scratch_destination_path'],
            conf['octgn_o8d_scratch_destination_path']),
        capture_output=True, shell=True, check=True)
    stdout = res.stdout.decode('utf-8').strip()
    stderr = res.stderr.decode('utf-8').strip()
    logging.info('Rclone Scratch finished, stdout: %s, stderr: %s',
                 stdout, stderr)
    if stdout != 'Done':
        raise RCloneError('RClone Scratch failed, stdout: {}, stderr: {}'
                          .format(stdout, stderr))


def run(conf=None):  # pylint: disable=R0912,R0915
    """ Main function.
    """
    cron_id = uuid.uuid4()
    logging.info('Started: %s', cron_id)

    if conf:
        conf = copy.deepcopy(conf)
    else:
        conf = read_conf()

    sheet_changes = True
    scratch_changes = True
    timestamp = time.time()
    try:  # pylint: disable=R1702
        if not internet_state():
            logging.warning('Internet is not available right now, exiting')
            sheet_changes = False
            scratch_changes = False
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

            rclone(conf)

        if scratch_changes:
            rclone_scratch(conf)

    except SanityCheckError as exc:
        message = str(exc)
        logging.error(message)
        logging.info('Done (%ss)', round(time.time() - timestamp, 3))
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
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)
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
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # init_logging()
    # run(my_conf)

    import cProfile
    from run_before_se import init_logging as init_logging_stdout
    init_logging_stdout()
    cProfile.run('run()', sort='time')
