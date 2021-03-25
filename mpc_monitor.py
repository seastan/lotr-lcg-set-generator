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


SAVED_PROJECTS_URL = \
    'https://www.makeplayingcards.com/design/dn_temporary_designes.aspx'
VIEWSTATE_REGEX = r'id="__VIEWSTATE" value="([^"]+)"'
VIEWSTATEGENERATOR_REGEX = r'id="__VIEWSTATEGENERATOR" value="([^"]+)"'
CONTENT_ID_REGEX = \
    r'<img src="[^?]+\?([^"]+)" alt="[^"]*"><\/a><\/div><div class="bmrbox"><div class="bmname">{}<\/div>'

DEFAULT_VIEWSTATE = \
    '/wEPDwUJNjAwNDE3MDgyDxYCHhNWYWxpZGF0ZVJlcXVlc3RNb2RlAgFkZKxwlxJ+dQzVGn0L8+0kT3Qk5oie'
DEFAULT_VIEWSTATEGENERATOR = '7D57AF60'
DEFAULT_HIDDGRECAPTCHAV3TOKEN = \
    '03AGdBq25A2GL4dhQ7lzrQbq4yeJycZQ2Hgi-5zhDei6hpGs3eap2F_eyLtIPSdtMPn5ardl-fTRFaxI8mj12HNBp-ezuEiTdRXRCHnuRt5039oDE1znUCzJhxz1l_R-kqpgGQoaXGPPjXvgOxeTYCaHXUcuq1PgCJrz4LPId18uvY0bZwPM9hdVA6avdiS_K_Ia7eLfWaPrBbuJvrS9L7hwW0uCP3cgaxRQdRF9tpLzo1ZEWEPmDUeYUaz_iHKoW44oZkthNjnb1SbJir0gz3_jmpslf4b-UUQZvO_-JNjkvYPmU9aOPmakhrk0WrdMzl74C5PlDEZSKdHmLUqSGlZ2OhgGu_2N9tbIVDlA5vkxL4koRPD2EQsnFoiDW5WZAmlzjdCzRjeDY79Aphs-PM508cKnl9CrDvvu9zDn36_jqqrRAf_YzJ-Rl1_VfMMoKpa-DAi_mUWleLWURV-Ik3b3YZbuCHe8gxQA'

ALERT_SUBJECT_TEMPLATE = 'LotR MPC Monitor ALERT: {}'
ERROR_SUBJECT_TEMPLATE = 'LotR MPC Monitor ERROR: {}'
WARNING_SUBJECT_TEMPLATE = 'LotR MPC Monitor WARNING: {}'
MAIL_QUOTA = 50

CONF_PATH = 'mpc_monitor.json'
DISCORD_CONF_PATH = 'discord.yaml'
INTERNET_SENSOR_PATH = '/home/homeassistant/.homeassistant/internet_state'
LOG_PATH = 'mpc_monitor.log'
MAIL_COUNTER_PATH = 'mpc_monitor.cnt'
MAILS_PATH = '/home/homeassistant/.homeassistant/mails'
WORKING_DIRECTORY = '/home/homeassistant/lotr-lcg-set-generator/'

URL_TIMEOUT = 30
URL_RETRIES = 1
URL_SLEEP = 1


class ConfigurationError(Exception):
    """ Configuration error.
    """


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


def send_get(session, url):
    """ Send GET request.
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


def send_post(session, url, form_data):
    """ Send POST request.
    """
    for i in range(URL_RETRIES):
        try:
            req = session.post(url, data=form_data, timeout=URL_TIMEOUT)
            res = req.content.decode('unicode-escape', errors='ignore')
            break
        except Exception:
            if i < URL_RETRIES - 1:
                time.sleep(URL_SLEEP)
            else:
                raise

    return res


def get_viewstate(session):
    """ Get VIEWSTATE values.
    """
    content = send_get(session, SAVED_PROJECTS_URL)
    viewstate = re.search(VIEWSTATE_REGEX, content)
    if not viewstate:
        raise ResponseError('No VIEWSTATE found, content length: {}'
                            .format(len(content)))

    viewstategenerator = re.search(VIEWSTATEGENERATOR_REGEX, content)
    if not viewstategenerator:
        raise ResponseError('No VIEWSTATEGENERATOR found, content length: {}'
                            .format(len(content)))

    viewstate = viewstate.groups()[0]
    viewstategenerator = viewstategenerator.groups()[0]
    return viewstate, viewstategenerator


def run():  # pylint: disable=R0915
    """ Run the check.
    """
    try:
        with open(CONF_PATH, 'r') as fobj:
            data = json.load(fobj)
    except Exception:
        message = 'No configuration found'
        logging.error(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
        return

    if not data.get('cookies'):
        raise ConfigurationError('No cookies found')

    session = requests.Session()
    session.cookies.update(data['cookies'])
    session.headers['Accept'] = \
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    session.headers['Accept-Encoding'] = 'gzip, deflate, br'
    session.headers['Accept-Language'] = 'en-US'
    session.headers['Cache-Control'] = 'no-cache'
    session.headers['Connection'] = 'keep-alive'
    session.headers['DNT'] = '1'
    session.headers['Host'] = 'www.makeplayingcards.com'
    session.headers['Origin'] = 'https://www.makeplayingcards.com'
    session.headers['Pragma'] = 'no-cache'
    session.headers['Referer'] = SAVED_PROJECTS_URL
    session.headers['Upgrade-Insecure-Requests'] = '1'
    session.headers['User-Agent'] = \
        'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'

    # viewstate, viewstategenerator = get_viewstate(session)
    viewstate = DEFAULT_VIEWSTATE
    viewstategenerator = DEFAULT_VIEWSTATEGENERATOR

    hiddgrecaptchav3token = DEFAULT_HIDDGRECAPTCHAV3TOKEN
    form_data = {'__EVENTTARGET': 'btn_pageload_handle',
                 '__EVENTARGUMENT': '',
                 '__VIEWSTATE': viewstate,
                 '__VIEWSTATEGENERATOR': viewstategenerator,
                 'hidd_type': '',
                 'hidd_value': '',
                 'hidd_project_name': '',
                 'hidd_product_type': '',
                 'hidd_sortby': 'Date',
                 'hidd_close_shop_message_info': '',
                 'hiddGrecaptChaV3Token': hiddgrecaptchav3token}
    content = send_post(session, SAVED_PROJECTS_URL, form_data)
    if 'My saved projects' not in content:
        raise ResponseError('No saved projects found, content length: {}'
                            .format(len(content)))

    for deck in data.get('decks', {}):
        logging.info('Processing %s', deck)
        regex = CONTENT_ID_REGEX.format(deck)
        match = re.search(regex, content)
        if not match:
            message = ('No content ID found for deck {}, content length: {}'
                       .format(deck, len(content)))
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
            continue

        content_id = match.groups()[0]
        if content_id != data['decks'][deck]['last_id']:
            if content_id != data['decks'][deck]['content_id']:
                message = 'Deck {} has been corrupted!'.format(deck)
                logging.info(message)
                create_mail(ALERT_SUBJECT_TEMPLATE.format(message))
                discord_message = f"""Deck **{deck}** has been corrupted!
Do the following:
1. Open https://www.makeplayingcards.com/design/dn_temporary_designes.aspx and login into ALeP account (if needed)
2. Find **{deck}** deck in the list, click *Save As*, type **Corrupted** and click *Save* (to inspect it later)
3. Ater page refresh, click *Delete* near **{deck}** deck
4. Find **{deck} Backup** deck in the list, click *Save As*, type **{deck}** and click *Save*
5. Find **{deck}** deck in the list again, right click on the checkbox and copy its ID (after "chk_")
6. Construct a URL https://www.makeplayingcards.com/design/dn_temporary_parse.aspx?id=<ID>
7. Open https://www.blogger.com/u/6/blog/page/edit/2051510818249539805/4960180109813771074 and login into ALeP account (if needed)
8. Switch to *Compose view* and update the link for "MakePlayingCards Direct Order Link"
<@!637024738782216212> <@!134863257050677248> <@!464924763312226304>"""
                if not send_discord(discord_message):
                    continue

            data['decks'][deck]['last_id'] = content_id

    data['cookies'] = session.cookies.get_dict()
    with open(CONF_PATH, 'w') as fobj:
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
