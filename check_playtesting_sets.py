# pylint: disable=W0703,C0209
# -*- coding: utf8 -*-
""" Check redundant playtesting sets.
"""
from email.header import Header
import json
import logging
import os
import re
import time
import uuid

import yaml

from lotr import list_dragncards_files, run_cmd, UUID_REGEX


DATA_PATH = os.path.join('Data', 'check_playtesting_sets.json')
DISCORD_CARD_DATA_PATH = os.path.join('Discord', 'Data', 'card_data.json')
DISCORD_CONF_PATH = 'discord.yaml'
DUPLICATE_ALERT_SUBJECT_TEMPLATE = \
    'Playtesting Sets Cron Duplicate ALERT: {}'
REDUNDANT_ALERT_SUBJECT_TEMPLATE = \
    'Playtesting Sets Cron Redundant ALERT: {}'
ERROR_SUBJECT_TEMPLATE = 'Playtesting Sets Cron ERROR: {}'
INTERNET_SENSOR_PATH = 'internet_state'
LOG_PATH = 'check_playtesting_sets.log'
MAILS_PATH = 'mails'

RCLONE_OCTGN_FILES_CMD = "rclone lsjson 'ALePOCTGN:/{}/'"
IO_SLEEP_TIME = 1
LOG_LEVEL = logging.INFO


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
        return True


def read_json_data(path):
    """ Read data from a JSON file.
    """
    try:
        with open(path, 'r', encoding='utf-8') as obj:
            data = json.load(obj)
    except Exception:
        time.sleep(IO_SLEEP_TIME)
        with open(path, 'r', encoding='utf-8') as obj:
            data = json.load(obj)

    return data


def get_playtesting_set_ids():
    """ Get playtesting set IDs.
    """
    card_data = read_json_data(DISCORD_CARD_DATA_PATH)
    set_ids = set(card_data['playtesting_set_ids'])
    return set_ids


def get_dragncards_set_ids():
    """ Get DragnCards set IDs.
    """
    with open(DISCORD_CONF_PATH, 'r', encoding='utf-8') as f_conf:
        conf = yaml.safe_load(f_conf)

    res = list_dragncards_files(conf)
    filenames = re.split(r'\s+', res)
    set_ids = [re.sub(r'\.json$', '', f) for f in filenames]
    set_ids = [s for s in set_ids if re.match(UUID_REGEX, s)]
    set_ids = set(set_ids)
    return set_ids


def get_drive_set_ids():
    """ Get Google Drive set IDs.
    """
    set_ids = set()
    duplicate_ids = set()
    for path in ('Set Folders', 'Scratch Set Folders'):
        res = run_cmd(RCLONE_OCTGN_FILES_CMD.format(path))
        stdout = res.stdout.decode('utf-8').strip()
        filenames = [f['Name'] for f in json.loads(stdout)]
        new_set_ids = [f for f in filenames if re.match(UUID_REGEX, f)]
        new_duplicate_ids = set_ids.intersection(new_set_ids)
        set_ids = set_ids.union(new_set_ids)
        duplicate_ids = duplicate_ids.union(new_duplicate_ids)

    return set_ids, duplicate_ids


def main():  # pylint: disable=R0912
    """ Main function.
    """
    timestamp = time.time()
    try:
        if not internet_state():
            logging.warning('Internet is not available right now, exiting')
            return

        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as fobj:
                previous_data = json.load(fobj)
        except Exception:
            previous_data = {'dragncards_set_ids': [], 'drive_set_ids': [],
                             'drive_duplicate_ids': []}

        playtesting_set_ids = get_playtesting_set_ids()
        dragncards_set_ids = get_dragncards_set_ids().difference(
            playtesting_set_ids)
        drive_set_ids, drive_duplicate_ids = get_drive_set_ids()
        drive_set_ids = drive_set_ids.difference(playtesting_set_ids)
        if (dragncards_set_ids == set(previous_data['dragncards_set_ids']) and
                drive_set_ids == set(previous_data['drive_set_ids']) and
                drive_duplicate_ids ==
                set(previous_data['drive_duplicate_ids'])):
            logging.info("Sets didn't change since the previous run")
            return

        all_set_ids = dragncards_set_ids.union(drive_set_ids)
        if all_set_ids:
            res = []
            if dragncards_set_ids:
                res.append('\nRedundant set(s) found on the DragnCards host:')
                for set_id in sorted(dragncards_set_ids):
                    res.append(set_id)

            if drive_set_ids:
                res.append('\nRedundant set(s) found on the Google Drive:')
                for set_id in sorted(drive_set_ids):
                    res.append(set_id)

            res = '\n'.join(res).strip()
            logging.info(res)
            create_mail(REDUNDANT_ALERT_SUBJECT_TEMPLATE.format(
                ', '.join(sorted(all_set_ids))), res)
        else:
            logging.info('No redundant sets found')

        if drive_duplicate_ids:
            res = '\n'.join(sorted(drive_duplicate_ids))
            res = ('Duplicate set(s) found in the Google Drive folders:\n{}'
                   .format(res))
            logging.info(res)
            create_mail(DUPLICATE_ALERT_SUBJECT_TEMPLATE.format(
                ', '.join(sorted(drive_duplicate_ids))), res)

        new_data = {'dragncards_set_ids': list(dragncards_set_ids),
                    'drive_set_ids': list(drive_set_ids),
                    'drive_duplicate_ids': list(drive_duplicate_ids)}
        with open(DATA_PATH, 'w', encoding='utf-8') as fobj:
            json.dump(new_data, fobj)
    except Exception as exc:
        message = 'Script failed: {}: {}'.format(type(exc).__name__, str(exc))
        logging.exception(message)
        try:
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)
        except Exception as exc_new:
            logging.exception(str(exc_new))
    finally:
        logging.info('Done (%ss)', round(time.time() - timestamp, 3))


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
