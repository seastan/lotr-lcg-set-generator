""" Monitor MakePlayingCards shared URLs.
"""
# pylint: disable=W0703,C0301
from datetime import datetime
from email.header import Header
import json
import logging
import os
import re
import time
import uuid

import requests
import yaml


COOKIES = {
    "ASP.NET_SessionId": "m54mkkfuyyfl0df2wkfxhbp0",
    "PrinterStudioCookie": "B13C6275B2336A094A58EE9CBF88F314ACDC4C729AA9F7C348727E005F44F3DEF92611CE25CF4082DD139E760A8531CEE24015DA7B3705BB1C994DD172C4888DDAE11891F5F980E933E2216DC5BAAC6B0B972B6A49E0D10E0BAC07D017F2E2685B45D901D850198E03BF4E900FBC6954926BD0D26F53F34F1C8A6A343090229BF64E6A973BDDFF70714030510F7E25D9B374DBE7C21443AFEC73FDE63EAE5EB1062C946072703C8DBE53FA75AD83F66D6A75868B3B884B3DAD4909E7FF1C2ED8C3C91392C682D8182437F8837710E26E5F577982",
    "PrinterStudioUserName": "alongextendedparty@gmail.com"
}

ID_REGEX = r'src="\.\.\/\/PreviewFiles\/Normal\/temp\/thumb\/([0-9A-F]+)_'

ALERT_SUBJECT_TEMPLATE = 'LotR MPC Monitor ALERT: {}'
ERROR_SUBJECT_TEMPLATE = 'LotR MPC Monitor ERROR: {}'
WARNING_SUBJECT_TEMPLATE = 'LotR MPC Monitor WARNING: {}'
MAIL_QUOTA = 50

DISCORD_CONF_PATH = 'discord.yaml'
INTERNET_SENSOR_PATH = '/home/homeassistant/.homeassistant/internet_state'
LINKS_PATH = 'mpc_monitor.json'
LOG_PATH = 'mpc_monitor.log'
MAIL_COUNTER_PATH = 'mpc_monitor.cnt'
MAILS_PATH = '/home/homeassistant/.homeassistant/mails'
WORKING_DIRECTORY = '/home/homeassistant/lotr-lcg-set-generator/'

URL_TIMEOUT = 30
URL_RETRIES = 3
URL_SLEEP = 1


class ResponseError(Exception):
    """ Response error.
    """


class DiscordResponseError(Exception):
    """ Discord Response error.
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


def send_discord(message):
    """ Send a message to a Discord channel.
    """
    try:
        with open(DISCORD_CONF_PATH, 'r') as f_conf:
            conf = yaml.safe_load(f_conf)

        if conf.get('webhook_url'):
            data = {'content': message}
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
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message))

    return False


def get_url(session, url):
    """ Get URL content.
    """
    for i in range(URL_RETRIES):
        try:
            req = session.get(url, timeout=URL_TIMEOUT)
            res = req.content.decode('unicode-escape', errors='ignore')
            break
        except Exception:
            if i < URL_RETRIES - 1:
                time.sleep(URL_SLEEP)
            else:
                raise

    return res


def run():
    """ Run the check.
    """
    try:
        with open(LINKS_PATH, 'r') as fobj:
            data = json.load(fobj)
    except Exception:
        message = 'No links found'
        logging.warning(message)
        create_mail(WARNING_SUBJECT_TEMPLATE.format(message), '')
        return

    session = requests.Session()
    session.cookies.update(COOKIES)

    for deck in data:
        logging.info('Processing %s', deck)
        content = get_url(session, data[deck]['url'])
        match = re.search(ID_REGEX, content)
        if not match:
            raise ResponseError('No ID found')

        deck_id = match.groups()[0]
        if deck_id != data[deck]['id']:
            message = 'Deck {} has been changed!'.format(deck)
            logging.info(message)
            send_discord(message)
            create_mail(ALERT_SUBJECT_TEMPLATE.format(message))
            data[deck]['id'] = deck_id
            with open(LINKS_PATH, 'w') as fobj:
                json.dump(data, fobj, indent=4)

def main():
    """ Main function.
    """
    logging.info('Started')
    try:
        if not internet_state():
            logging.warning('Internet is not available right now, exiting')
            return

        run()
    except ResponseError as exc:
        message = 'Response Error: {}'.format(str(exc))
        logging.error(message)
        try:
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
        except Exception as exc_new:
            logging.exception(str(exc_new))
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
