# pylint: disable=W0703,C0209,C0301
""" Monitor remote pipeline.
"""
from email.header import Header
import hashlib
import json
import logging
import os
import re
import subprocess
import time
import uuid
import warnings

import requests
import yaml


ALERT_SUBJECT_TEMPLATE = 'LotR Remote Pipeline Monitor ALERT: {}'
ERROR_SUBJECT_TEMPLATE = 'LotR Remote Pipeline Monitor ERROR: {}'

CHUNK_LIMIT = 1980
IO_SLEEP_TIME = 1
LOG_LEVEL = logging.INFO
MESSAGE_SLEEP_TIME = 30

CONFIGURATION_PATH = 'configuration.yaml'
DATA_PATH = 'monitor_remote_pipeline.json'
DISCORD_CARD_DATA_PATH = os.path.join('Discord', 'card_data.json')
DISCORD_CONF_PATH = 'discord.yaml'
LOG_PATH = 'monitor_remote_pipeline.log'
MAILS_PATH = 'mails'


warnings.filterwarnings('ignore', category=DeprecationWarning)


class DiscordResponseError(Exception):
    """ Discord Response error.
    """


class RCloneError(Exception):
    """ RClone error.
    """


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


def rclone_logs(conf):
    """ Sync logs folder from Google Drive.
    """
    res = subprocess.run(
        './rclone_logs.sh "{}"'.format(conf.get('remote_logs_path')),
        capture_output=True, shell=True, check=True)
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


def send_discord(message):
    """ Send a message to a Discord channel.
    """
    try:  # pylint: disable=R1702
        with open(DISCORD_CONF_PATH, 'r', encoding='utf-8') as f_conf:
            conf = yaml.safe_load(f_conf)

        if conf.get('webhook_url'):
            chunks = []
            chunk = ''
            for line in message.split('\n'):
                if len(chunk + line) + 1 <= CHUNK_LIMIT:
                    chunk += line + '\n'
                else:
                    while len(chunk) > CHUNK_LIMIT:
                        pos = chunk[:CHUNK_LIMIT].rfind(' ')
                        if pos == -1:
                            pos = CHUNK_LIMIT - 1

                        chunks.append(chunk[:pos + 1])
                        chunk = chunk[pos + 1:]

                    chunks.append(chunk)
                    chunk = line + '\n'

            chunks.append(chunk)

            for i, chunk in enumerate(chunks):
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


def run():  # pylint: disable=R0912,R0914,R0915
    """ Run the check.
    """
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as fobj:
            previous_data = json.load(fobj)
    except Exception:
        previous_data = {'checksum': ''}

    with open(CONFIGURATION_PATH, 'r', encoding='utf-8') as f_conf:
        conf = yaml.safe_load(f_conf)

    rclone_logs(conf)
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

    new_checksum = hashlib.md5(res.encode('utf-8')).hexdigest()
    old_checksum = previous_data['checksum']
    if old_checksum == new_checksum:
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

    overflow_ids = re.findall(r'(?<=Too long text for card )[0-9a-f-]+',
                              errors)
    if overflow_ids:
        card_data = read_json_data(DISCORD_CARD_DATA_PATH)
        card_ids = {r['Card GUID'] for r in card_data['data']}
        overflow_ids = [card_id for card_id in overflow_ids
                        if card_id in card_ids]

    if overflow_ids:
        send_discord('!image refresh')
        time.sleep(MESSAGE_SLEEP_TIME)
        for overflow_id in overflow_ids:
            send_discord('Too long text on the rendered image for the card:')
            send_discord('!alepcard {}'.format(overflow_id))
            send_discord('!image {}'.format(overflow_id))
            time.sleep(MESSAGE_SLEEP_TIME)

    new_data = {'checksum': new_checksum}
    with open(DATA_PATH, 'w', encoding='utf-8') as fobj:
        json.dump(new_data, fobj)


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
