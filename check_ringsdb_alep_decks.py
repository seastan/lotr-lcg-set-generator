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

import common


DATA_PATH = os.path.join('Data', 'check_ringsdb_alep_decks.json')
DISCORD_CARD_DATA_PATH = os.path.join('Discord', 'Data', 'card_data.json')
DISCORD_CONF_PATH = 'discord.yaml'
ERROR_SUBJECT_TEMPLATE = 'RingsDB ALeP Decks Cron ERROR: {}'
INTERNET_SENSOR_PATH = 'internet_state'
LOG_PATH = 'check_ringsdb_alep_decks.log'
MAILS_PATH = 'mails'
RINGSDB_URL = 'http://ringsdb.com/api/public/decklists/by_date/{}'

IO_SLEEP_TIME = 1
LOG_LEVEL = logging.INFO

SPHERE_EMOJIS = {
    'Leadership': '<:leadership:822573464601886740>',
    'Lore': '<:lore:822573464678301736>',
    'Spirit': '<:spirit:822573464417206273>',
    'Tactics': '<:tactics:822573464593629264>',
    'Baggins': '<:baggins:822573762415296602>',
    'Fellowship': '<:fellowship:822573464586027058>'
}

TAG_EMOJIS = {
    '<span class="icon-leadership"></span>':
        '<:leadership:822573464601886740>',
    '<span class="icon-lore"></span>': '<:lore:822573464678301736>',
    '<span class="icon-spirit"></span>': '<:spirit:822573464417206273>',
    '<span class="icon-tactics"></span>': '<:tactics:822573464593629264>',
    '<span class="icon-baggins"></span>': '<:baggins:822573762415296602>',
    '<span class="icon-fellowship"></span>':
        '<:fellowship:822573464586027058>',
    '<span class="icon-unique"></span>': '<:unique:822573762474016818>',
    '<span class="icon-threat"></span>': '<:threat:822572608994148362>',
    '<span class="icon-attack"></span>': '<:attack:822573464367792221>',
    '<span class="icon-defense"></span>': '<:defense:822573464615518209>',
    '<span class="icon-willpower"></span>': '<:willpower:822573464367792170>',
    '<span class="icon-health"></span>': '<:hitpoints:822572931254714389>',
    '<span class="icon-neutral"></span>': '*Neutral* '
}

URL_TIMEOUT = 30
URL_RETRIES = 3
URL_SLEEP = 30


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
    try:  # pylint: disable=R1702
        with open(DISCORD_CONF_PATH, 'r', encoding='utf-8') as f_conf:
            conf = yaml.safe_load(f_conf)

        if conf.get('ringsdb_alep_decks_webhook_url'):
            for i, chunk in enumerate(common.split_result(message)):
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


def get_ringsdb_content(url):
    """ Get RingsDB URL content.
    """
    for i in range(URL_RETRIES):
        try:
            res = requests.get(url)
            res = res.content.decode('utf-8')
            logging.info('RingsDB answer: %s', res[:100])
            data = json.loads(res)
            break
        except Exception:
            if i < URL_RETRIES - 1:
                time.sleep(URL_SLEEP * (i + 1))
            else:
                raise

    return data


def process_ringsdb_data():  # pylint: disable=R0912,R0914,R0915
    """ Process the data from RingsDB.
    """
    today = datetime.today().strftime('%Y-%m-%d')
    try:
        url = RINGSDB_URL.format(today)
        data = get_ringsdb_content(url)
    except Exception as exc:
        message = 'Reading RingsDB data for today failed: {}'.format(str(exc))
        logging.error(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
        return

    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    try:
        url = RINGSDB_URL.format(yesterday)
        data_yesterday = get_ringsdb_content(url)
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
    except Exception:
        previous_data = {'previous_decks': []}

    card_data = read_json_data(DISCORD_CARD_DATA_PATH)
    codes = {r['_RingsDB Code']:'{} ({})'.format(r.get('Name', ''),
                                                 r.get('_Set Name', ''))
             for r in card_data['data'] if r.get('_RingsDB Code')}

    data.sort(key=lambda d: d['id'])
    new_decks = [d['id'] for d in data]
    previous_decks = set(previous_data['previous_decks'])
    deck_count = 0
    for deck in data:
        if deck['id'] in previous_decks:
            continue

        if deck['last_pack'].startswith('ALeP - '):
            deck_count += 1
            heroes = []
            for hero in deck['heroes_details']:
                hero_text = '{} {} *({})*'.format(
                    SPHERE_EMOJIS.get(hero['sphere'],
                                      '*{}*'.format(hero['sphere'])),
                    hero['name'],
                    hero['pack'])
                heroes.append(hero_text)

            alep_codes = []
            for code in deck['slots']:
                code = str(code)
                if code in codes:
                    alep_codes.append(code)

            if len(alep_codes) > 1:
                alep_cards_count = '{} ALeP cards'.format(len(alep_codes))
                alep_cards = 'ALeP cards:\n{}'.format('\n'.join(
                    ['- {}'.format(codes[c]) for c in sorted(alep_codes)]))
            elif len(alep_codes) == 1:
                alep_cards_count = '1 ALeP card'
                alep_cards = 'ALeP card:\n- {}'.format(codes[alep_codes[0]])
            else:
                continue

            if deck['description_md']:
                description = deck['description_md']
                for tag, emoji in TAG_EMOJIS.items():
                    description = description.replace(tag, emoji)
                    description = description.replace('<b>', '**').replace(
                        '</b>', '**')
                    description = description.replace('<i>', '*').replace(
                        '</i>', '*')
                    description = description.replace('<u>', '__').replace(
                        '</u>', '__')
            else:
                description = 'no description'

            url = 'https://ringsdb.com/decklist/view/{}'.format(deck['id'])
            message = """New AleP deck has been published to RingsDB:

**{}** by {} *({} threat, {} up to {})*
{}
{}
{}
{}
` `""".format(deck['name'].replace('*', '').strip(),
              deck['username'],
              deck['starting_threat'],
              alep_cards_count,
              deck['last_pack'],
              ', '.join(heroes),
              alep_cards,
              description,
              url)
            logging.info(message)
            send_discord(message)

    if deck_count > 1:
        logging.info('Found %s new ALeP deck(s)', deck_count)
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
