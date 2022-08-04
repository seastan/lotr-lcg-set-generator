# pylint: disable=W0703,C0209
# -*- coding: utf8 -*-
""" Check recent RingsDB ALeP decks.
"""
from datetime import datetime, timedelta
from email.header import Header
import json
import logging
import os
import re
import time
import uuid

import requests
import yaml


DATA_PATH = 'check_ringsdb_alep_decks.json'
DISCORD_CONF_PATH = 'discord.yaml'
ERROR_SUBJECT_TEMPLATE = 'RingsDB ALeP Decks Cron ERROR: {}'
INTERNET_SENSOR_PATH = 'internet_state'
LOG_PATH = 'check_ringsdb_alep_decks.log'
LOG_LEVEL = logging.INFO
MAILS_PATH = 'mails'

RINGSDB_URL = 'http://ringsdb.com/api/public/decklists/by_date/{}'

EMOJIS = {
    'Leadership': '<:leadership:822573464601886740>',
    'Lore': '<:lore:822573464678301736>',
    'Spirit': '<:spirit:822573464417206273>',
    'Tactics': '<:tactics:822573464593629264>',
    'Baggins': '<:baggins:822573762415296602>',
    'Fellowship': '<:fellowship:822573464586027058>'
}


class DiscordResponseError(Exception):
    """ Discord Response error.
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


def send_discord(message):
    """ Send a message to a Discord channel.
    """
    try:
        with open(DISCORD_CONF_PATH, 'r', encoding='utf-8') as f_conf:
            conf = yaml.safe_load(f_conf)

        if conf.get('ringsdb_alep_decks_webhook_url'):
            chunks = []
            while len(message) > 1900:
                chunks.append(message[:1900])
                message = message[1900:]

            chunks.append(message)
            for i, chunk in enumerate(chunks):
                if i > 0:
                    time.sleep(1)

                data = {'content': chunk}
                res = requests.post(conf['ringsdb_alep_decks_webhook_url'],
                                    json=data)
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


def process_ringsdb_data():  # pylint: disable=R0914
    """ Process the data from RingsDB.
    """
    today = datetime.today().strftime('%Y-%m-%d')
    try:
        url = RINGSDB_URL.format(today)
        res = requests.get(url)
        res = res.content.decode('utf-8')
        data = json.loads(res)
    except Exception as exc:
        message = 'Reading RingsDB data for today failed: {}'.format(str(exc))
        logging.error(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
        return

    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    try:
        url = RINGSDB_URL.format(yesterday)
        res = requests.get(url)
        res = res.content.decode('utf-8')
        data_yesterday = json.loads(res)
    except Exception as exc:
        message = 'Reading RingsDB data for yesterday failed: {}'.format(
            str(exc))
        logging.error(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
        return

    data.extend(data_yesterday)

    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as fobj:
            previous_data = json.load(fobj)
    except Exception as exc:
        previous_data = {'previous_decks': []}

    data.sort(key=lambda d: d['id'])
    new_decks = [d['id'] for d in data]
    previous_decks = set(previous_data['previous_decks'])
    alep_count = 0
    for deck in data:
        if deck['id'] in previous_decks:
            continue

        if deck['last_pack'].startswith('ALeP - '):
            alep_count += 1
            heroes = []
            for hero in deck['heroes_details']:
                hero_text = '{} {} *({})*'.format(
                    EMOJIS.get(hero['sphere'], ''),
                    hero['name'],
                    hero['pack'])
                heroes.append(hero_text)

            url = 'https://ringsdb.com/decklist/view/{}'.format(deck['id'])
            message = """New AleP deck has been published to RingsDB:

**{}** *({} threat, cards up to {})*
{}
{}
` `""".format(deck['name'].replace('*', '').strip(),
             deck['starting_threat'],
             deck['last_pack'],
             ', '.join(heroes),
             url)
            logging.info(message)
            send_discord(message)

    if alep_count > 1:
        logging.info('Found %s new ALeP deck(s)', alep_count)
    else:
        logging.info('No new ALeP decks found')

    new_data = {'previous_decks': new_decks}
    with open(DATA_PATH, 'w', encoding='utf-8') as fobj:
        json.dump(new_data, fobj)


def main():
    """ Main function.
    """
    timestamp = time.time()
    try:
        if not internet_state():
            logging.warning('Internet is not available right now, exiting')
            return

        process_ringsdb_data()
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
