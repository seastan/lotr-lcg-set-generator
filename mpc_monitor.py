# pylint: disable=W0703,C0209,C0301,C0302
""" Monitor MakePlayingCards shared URLs.
"""
from datetime import datetime
from email.header import Header
import json
import logging
import os
import random
import re
import sys
import time
import uuid

import requests
import yaml

import common


SAVED_PROJECTS_URL = \
    'https://www.makeplayingcards.com/design/dn_temporary_designes.aspx'
PREVIEW_URL = (
    'https://www.makeplayingcards.com/design/dn_parse_products.aspx?'
    'product={}&pieces={}&attach={}&give=&orderno=&sellID=&effectNo='
    '&componentList={}&rm={}')

DECK_REGEX = (
    r'<a href="javascript:oTempSave.show\(\'([^\']+)\'[^"]+">'
    r'<img src="[^?]+\?([^"]+)" alt="[^"]*"><\/a><\/div>'
    r'<div class="bmrbox"><div class="bmname">{}<\/div>')
DECK_ID_REGEX = (
    r'<a href="javascript:oTempSave.show\(\'{}\'[^"]+">'
    r'<img src="[^?]+\?([^"]+)" alt="[^"]*"><\/a><\/div>'
    r'<div class="bmrbox"><div class="bmname">([^<]+)<\/div>')
VIEWSTATE_REGEX = r'id="__VIEWSTATE" value="([^"]+)"'
VIEWSTATEGENERATOR_REGEX = r'id="__VIEWSTATEGENERATOR" value="([^"]+)"'
SESSIONID_REGEX = (
    r'<form method="post" action="\.\/dn_playingcards_front_dynamic\.aspx\?'
    r'[^"]*?ssid=([^&"]+)')
NEXT_REGEX = (
    r'<a href="javascript:__doPostBack\(&#39;([^&]+)&#39;,'
    r'&#39;([^&]+)&#39;\)" style="[^"]+">Next<\/a>')
PREVIEW_REGEX = r'(?<=javascript:oTempSave\.show\()[^\)]+'
IMAGE_REGEX = r'(?<=<img src=")[^"]+'

DEFAULT_VIEWSTATE = \
    '/wEPDwUKMTk3MTM0MTI5NGRkq5zAH+KPIx3IAH6syg3EXVOr5hc='
DEFAULT_VIEWSTATEGENERATOR = '7D57AF60'
DEFAULT_HIDDGRECAPTCHAV3TOKEN = \
    '03AFcWeA7vbjH-M3idb7CW2LqXo4MoFTWSVlpdn7vRbGTObMtZvnmpKhl0Shxc-O9PDF-PWvE7Ywx04nO8OGMxid9qPoNW6enVustmzlLfihWuZNzedovk4yBS1A_1dzDravFutU8EmeOQSw30c1m-SgosDqQQFKykljigYWtcYuYOYf2i4JKSAG96I0Tw7ayCQmN72C0PEazLqZw4E41tet1bavuSbEtAU_QqoxOnLH8RCXk1siWVfYtJ1oEq_l_PZbC-GTLNTvdY6obgiyHQqlQm2Kt_ZSnCF3YIQq81stYMwAvsPMo8AJE14rXsJjhtQby8NVmTQzNdo7P3QaSj3QSOuUZwXbw4c0Y-LfD-gj_csro_Ba1uL1kx8Ge4KTUo3qp8AO9HRIo_YJFH9JCjwRx2F5Xy8ykU0aQWsF1LYkM-O1ylm2chsBtaJTS4B97Cb7ahN58g-V68wvel5cancpxnReLvKdt-XqpzAfeS1fYXxHFfkqSqg-GroRwIj8yGgrulkb3j51Dy8MuF-KUbvWPzERdGVPU9G57IqJZ60MBtwInM54c9XQZ-juFV4AcUvN23C7F8-H0FZ2vZBouzRTjWeTLOSWFfwth8kZ7IBQOGX8hFx-UkAU0DW2eMObvU8osI6ThyKjSa0IC0wgoDlGSNR72gJXP_C0gbEw6Bk7Edc2ttmdZ_8m8'

ALERT_SUBJECT_TEMPLATE = 'LotR MPC Monitor ALERT: {}'
ERROR_SUBJECT_TEMPLATE = 'LotR MPC Monitor ERROR: {}'
WARNING_SUBJECT_TEMPLATE = 'LotR MPC Monitor WARNING: {}'
MAIL_QUOTA = 50

CONF_PATH = 'mpc_monitor.json'
COOKIES_PATH = 'mpc_monitor_cookies.json'
DISCORD_CONF_PATH = 'discord.yaml'
INTERNET_SENSOR_PATH = 'internet_state'
LOG_PATH = 'mpc_monitor.log'
MAIL_COUNTER_PATH = os.path.join('Data', 'mpc_monitor.cnt')
MAILS_PATH = 'mails'

LOG_LEVEL = logging.INFO
MAX_NOT_FOUND_ERRORS = 5
NEXT_LIMIT = 10
URL_TIMEOUT = 30
URL_RETRIES = 5
URL_SLEEP = 60

DEBUG = False
DEBUG_PATH = os.path.join('Data', 'mpc_monitor_debug.html')

REFRESH_URL_TIMEOUT = 300
MIN_IMAGES = 18


class ConfigurationError(Exception):
    """ Configuration error.
    """


class ResponseError(Exception):
    """ Response error.
    """


class DiscordResponseError(Exception):
    """ Discord Response error.
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


def init_logging_manual():
    """ Init logging (manual run).
    """
    logging.basicConfig(filename=LOG_PATH, level=LOG_LEVEL,
                        format='%(asctime)s %(levelname)s: %(message)s')


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


def is_non_ascii(value):
    """ Check whether a string is ASCII only or not.
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


def send_get(session, url, timeout=None):
    """ Send GET request.
    """
    timeout = timeout or URL_TIMEOUT
    for i in range(URL_RETRIES):
        try:
            req = session.get(url, timeout=timeout)
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

    if DEBUG:
        with open(DEBUG_PATH, 'w', encoding='utf-8') as fobj:
            fobj.write(res)

    return res


def get_wordpress_content(data):
    """ Get content of WordPress page.
    """
    url = data['wordpress_url']
    headers = {'Authorization': 'Bearer {}'.format(data['wordpress_token'])}
    for i in range(URL_RETRIES):
        try:
            req = requests.get(
                url,
                headers=headers,
                timeout=URL_TIMEOUT)
            res = json.loads(req.content)['content']['rendered']
            break
        except Exception as exc:
            if i < URL_RETRIES - 1:
                time.sleep(URL_SLEEP)
            else:
                message = ('Error obtaining WordPress content: {}: {}'
                           .format(type(exc).__name__, str(exc)))
                logging.exception(message)
                create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)
                return ''

    return res


def update_wordpress_content(data, content):
    """ Update content of WordPress page.
    """
    url = data['wordpress_url']
    headers = {'Authorization': 'Bearer {}'.format(data['wordpress_token']),
               'Content-Type': 'application/json'}
    for i in range(URL_RETRIES):
        try:
            requests.put(
                url,
                headers=headers,
                data=json.dumps({'content': content}),
                timeout=URL_TIMEOUT)
            break
        except Exception as exc:
            if i < URL_RETRIES - 1:
                time.sleep(URL_SLEEP)
            else:
                message = ('Error updating WordPress content: {}: {}'
                           .format(type(exc).__name__, str(exc)))
                logging.exception(message)
                create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)


def replace_url(data, old_id, new_id):
    """ Replace deck ID on Wordpress site.
    """
    old_content = get_wordpress_content(data)
    if old_id not in old_content:
        return False

    new_content = old_content.replace(old_id, new_id)
    update_wordpress_content(data, new_content)
    new_content = get_wordpress_content(data)
    return new_id in new_content


def init_session(cookies):
    """ Init session object.
    """
    session = requests.Session()
    session.cookies.update(cookies)

    session.headers['Accept'] = \
        'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    session.headers['Accept-Encoding'] = 'gzip, deflate, br, zstd'
    session.headers['Accept-Language'] = 'en-US'
    session.headers['Connection'] = 'keep-alive'
    session.headers['DNT'] = '1'
    session.headers['Host'] = 'www.makeplayingcards.com'
    session.headers['Origin'] = 'https://www.makeplayingcards.com'
    session.headers['Priority'] = 'u=0, i'
    session.headers['Referer'] = SAVED_PROJECTS_URL
    session.headers['Sec-Fetch-Dest'] = 'document'
    session.headers['Sec-Fetch-Mode'] = 'navigate'
    session.headers['Sec-Fetch-Site'] = 'same-origin'
    session.headers['Sec-Fetch-User'] = '?1'
    session.headers['Upgrade-Insecure-Requests'] = '1'
    session.headers['User-Agent'] = \
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0'
    return session


def get_viewstate(session, content=''):
    """ Get VIEWSTATE values.
    """
    if not content:
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


def init_form_data(eventtarget, viewstate, viewstategenerator, hidd_type='',  # pylint: disable=R0913
                   hidd_value='', hidd_project_name='', hidd_product_type='',
                   eventargument=''):
    """ Init POST data.
    """
    data = {'__EVENTTARGET': eventtarget,
            '__EVENTARGUMENT': eventargument,
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            'hidd_type': hidd_type,
            'hidd_value': hidd_value,
            'hidd_project_name': hidd_project_name,
            'hidd_product_type': hidd_product_type,
            'hidd_sortby': 'Date',
            'hidd_close_shop_message_info': '',
            'hiddGrecaptChaV3Token': DEFAULT_HIDDGRECAPTCHAV3TOKEN}
    return data


def get_decks(session):
    """ Get a list of decks.
    """
    viewstate = DEFAULT_VIEWSTATE
    viewstategenerator = DEFAULT_VIEWSTATEGENERATOR
    form_data = init_form_data('btn_pageload_handle', viewstate,
                               viewstategenerator)
    content = send_post(session, SAVED_PROJECTS_URL, form_data)
    if 'Our system is currently undergoing system upgrade' in content:
        return ''

    if 'My saved projects' not in content:
        if DEBUG:
            with open(DEBUG_PATH, 'w', encoding='utf-8') as fobj:
                fobj.write(content)

        raise ResponseError('No saved projects found, content length: {}'
                            .format(len(content)))

    full_content = content
    cnt = 0
    res = re.search(NEXT_REGEX, content)
    while res and cnt < NEXT_LIMIT:
        cnt += 1
        logging.info('Following Page %s', res.groups()[1])
        viewstate, viewstategenerator = get_viewstate(session, content)
        form_data = init_form_data(res.groups()[0], viewstate,
                                   viewstategenerator,
                                   eventargument=res.groups()[1])
        content = send_post(session, SAVED_PROJECTS_URL, form_data)
        if not content:
            break

        res = re.search(NEXT_REGEX, content)
        full_content += content

    return full_content


def delete_deck(session, content, deck_id, deck):
    """ Delete the deck.
    """
    viewstate, viewstategenerator = get_viewstate(session, content)
    form_data = init_form_data('btn_submit', viewstate, viewstategenerator,
                               hidd_type='delete', hidd_value=deck_id,
                               hidd_project_name=deck)
    content = send_post(session, SAVED_PROJECTS_URL, form_data)
    if 'My saved projects' not in content:
        raise ResponseError('No saved projects found, content length: {}'
                            .format(len(content)))

    content = get_decks(session)
    return content


def clone_deck(session, content, deck_id, new_deck_name):
    """ Clone the deck.
    """
    viewstate, viewstategenerator = get_viewstate(session, content)
    form_data = init_form_data('btn_submit', viewstate, viewstategenerator,
                               hidd_type='saveas', hidd_value=deck_id,
                               hidd_project_name=new_deck_name)
    content = send_post(session, SAVED_PROJECTS_URL, form_data)
    if 'My saved projects' not in content:
        raise ResponseError('No saved projects found, content length: {}'
                            .format(len(content)))

    content = get_decks(session)
    return content


def rename_deck(session, deck_id, deck_name, actual_deck_name):
    """ Rename a deck.

    ATTENTION: Renaming a deck causes a new content ID.
    """
    res = send_get(
        session,
        'https://www.makeplayingcards.com/products/playingcard/design/'
        'dn_playingcards_front_dynamic.aspx?id={}&edit=Y'
        .format(deck_id))
    match = re.search(SESSIONID_REGEX, res)
    if not match:
        raise ResponseError('No session ID found, content length: {}'
                            .format(len(res)))

    session_id = match.groups()[0]
    res = send_post(
        session,
        'https://www.makeplayingcards.com/design/dn_project_save.aspx?ssid={}'
        .format(session_id), {'name': deck_name})
    if '[CDATA[SUCCESS]]' not in res:
        raise ResponseError('Deck {} was not renamed, response: {}'.format(
            actual_deck_name, res))

    content = get_decks(session)
    regex = DECK_REGEX.format(re.escape(deck_name))
    match = re.search(regex, content)
    if not match:
        raise ResponseError('Deck {} was not renamed, content length: {}'
                            .format(actual_deck_name, len(content)))

    return content


def fix_deck(session, data, content, deck_id, backup_id, deck_name,  # pylint: disable=R0912,R0913,R0914,R0915
             actual_deck_name, content_id, actual_content_id):
    """ Fix a corrupted deck.
    """
    discord_users = data['discord_users']
    if actual_deck_name != deck_name:
        message = ('Deck {} has been changed and renamed to {}! Attempting to '
                   'fix it automatically...'.format(deck_name,
                                                    actual_deck_name))
        discord_message = f"""Deck **{deck_name}** has been changed and renamed to **{actual_deck_name}**!
Attempting to fix it automatically...
{discord_users}"""
    else:
        message = ('Deck {} has been changed! Attempting to fix it '
                   'automatically...'.format(deck_name))
        discord_message = f"""Deck **{deck_name}** has been changed!
Attempting to fix it automatically...
{discord_users}"""
    logging.info(message)
    create_mail(ALERT_SUBJECT_TEMPLATE.format(message))
    send_discord(discord_message)

    try:  # pylint: disable=R1705
        if actual_deck_name != deck_name:
            new_deck_name = 'Corrupted {} ({}, {})'.format(deck_name,
                                                           actual_deck_name,
                                                           actual_content_id)
        else:
            new_deck_name = 'Corrupted {} ({})'.format(deck_name,
                                                       actual_content_id)

        regex = DECK_REGEX.format(re.escape(new_deck_name))
        match = re.search(regex, content)
        if match:
            logging.info('A copy of the deck already exists: %s',
                         new_deck_name)
        else:
            logging.info('Creating a copy of the deck: %s...', new_deck_name)
            content = clone_deck(session, content, deck_id, new_deck_name)
            match = re.search(regex, content)
            if match:
                discord_message = 'Created a copy of the deck: {}'.format(
                    new_deck_name)
                send_discord(discord_message)
            else:
                discord_message = ('Failed to create a copy of the deck: {}'
                                   .format(new_deck_name))
                send_discord(discord_message)

                message = 'Deck {} not found, content length: {}'.format(
                    new_deck_name, len(content))
                logging.error(message)
                create_mail(ERROR_SUBJECT_TEMPLATE.format(message))

        logging.info('Deleting the deck...')
        content = delete_deck(session, content, deck_id, actual_deck_name)
        regex = DECK_ID_REGEX.format(deck_id)
        match = re.search(regex, content)
        if match:
            discord_message = ('Failed to delete the deck: {}'
                               .format(actual_deck_name))
            send_discord(discord_message)

            message = 'Deck {} was not deleted'.format(actual_deck_name)
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))

            logging.info('Renaming the deck...')
            content = rename_deck(session, deck_id,
                                  'Delete {}'.format(new_deck_name),
                                  actual_deck_name)
        else:
            discord_message = 'Deleted the deck...'
            send_discord(discord_message)

        regex = DECK_ID_REGEX.format(backup_id)
        match = re.search(regex, content)
        if not match:
            raise ResponseError('Deck {} Backup not found, content length: {}'
                                .format(deck_name, len(content)))

        regex = DECK_REGEX.format(re.escape(deck_name))
        match = re.search(regex, content)
        if match:
            raise ResponseError('Deck {} already exists'.format(deck_name))

        logging.info('Creating a new deck from backup...')
        content = clone_deck(session, content, backup_id, deck_name)
        regex = DECK_REGEX.format(re.escape(deck_name))
        match = re.search(regex, content)
        if not match:
            raise ResponseError('Deck {} not found, content length: {}'
                                .format(deck_name, len(content)))

        new_deck_id = match.groups()[0]
        new_content_id = match.groups()[1]
        if new_content_id != content_id:
            raise ResponseError('Deck {} from backup has incorrect content'
                                .format(deck_name))

        discord_message = 'Created a new deck from backup...'
        send_discord(discord_message)
    except Exception as exc:
        message = ('Attempt to fix deck {}, content ID {} automatically '
                   'failed: {}: {}'.format(deck_name, actual_content_id,
                                           type(exc).__name__, str(exc)))
        logging.exception(message)
        body = f"""Do the following:
(depending on the error, some steps may be already done)
1. Open https://www.makeplayingcards.com/design/dn_temporary_designes.aspx and login (if needed)
2. Click Delete near {actual_deck_name} deck
3. Find {deck_name} Backup deck in the list, click Save As, type "{deck_name}" and click Save
4. Find {deck_name} deck in the list again, right click on the checkbox and copy its ID (after "chk_")
5. Construct a URL https://www.makeplayingcards.com/products/playingcard/design/dn_playingcards_front_dynamic.aspx?id=<ID>
6. Open https://wordpress.com, login (if needed), click Pages and open "MakePlayingCards Direct Links"
7. Update the link to that URL
"""
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message), body)
        discord_message = f"""Attempt to fix deck **{deck_name}** automatically failed!
Do the following:
(depending on the error, some steps may be already done)
1. Open https://www.makeplayingcards.com/design/dn_temporary_designes.aspx and login (if needed)
2. Click *Delete* near **{actual_deck_name}** deck
3. Find **{deck_name} Backup** deck in the list, click *Save As*, type "{deck_name}" and click *Save*
4. Find **{deck_name}** deck in the list again, right click on the checkbox and copy its ID (after "chk_")
5. Construct a URL https://www.makeplayingcards.com/products/playingcard/design/dn_playingcards_front_dynamic.aspx?id=<ID>
6. Open https://wordpress.com, login (if needed), click Pages and open "MakePlayingCards Direct Links"
7. Update the link to that URL
{discord_users}"""
        send_discord(discord_message)
        return '', ''
    else:
        res = replace_url(data, deck_id, new_deck_id)
        if res:
            message = ('Attempt to fix deck {} automatically succeeded! '
                       'WordPress web-site is already updated.'.format(deck_name))
            logging.info(message)
            body = ''
            create_mail(ALERT_SUBJECT_TEMPLATE.format(message), body)
            discord_message = f"""Attempt to fix deck **{deck_name}** automatically succeeded!
WordPress web-site is already updated."""
            send_discord(discord_message)
        else:
            message = ('Attempt to fix deck {} automatically succeeded, but '
                       'updating WordPress web-site failed. New deck ID: {}'
                       .format(deck_name, new_deck_id))
            logging.info(message)
            body = f"""Do the following:
1. Open https://wordpress.com, login (if needed), click Pages and open "MakePlayingCards Direct Links"
2. Update the link to:
https://www.makeplayingcards.com/products/playingcard/design/dn_playingcards_front_dynamic.aspx?id={new_deck_id}
"""
            create_mail(ALERT_SUBJECT_TEMPLATE.format(message), body)
            discord_message = f"""Attempt to fix deck **{deck_name}** automatically succeeded!
At the same time, updating WordPress web-site failed.
Do the following:
1. Open https://wordpress.com, login (if needed), click Pages and open "MakePlayingCards Direct Links"
2. Update the link to:
https://www.makeplayingcards.com/products/playingcard/design/dn_playingcards_front_dynamic.aspx?id={new_deck_id}
{discord_users}"""
            send_discord(discord_message)

        return content, new_deck_id


def add_deck(deck_name):  # pylint: disable=R0915
    """ Add a new deck to monitoring.
    """
    logging.info('Adding deck %s to monitoring', deck_name)
    try:
        with open(CONF_PATH, 'r', encoding='utf-8') as fobj:
            data = json.load(fobj)
    except Exception:
        message = 'No configuration found'
        logging.error(message)
        print(message)
        return

    try:
        with open(COOKIES_PATH, 'r', encoding='utf-8') as fobj:
            cookies = json.load(fobj)
    except Exception:
        message = 'No cookies found'
        logging.error(message)
        print(message)
        return

    if 'decks' in data and deck_name in data['decks']:
        message = 'Deck {} already added to monitoring'.format(deck_name)
        logging.info(message)
        print(message)
        return

    session = init_session(cookies)
    content = get_decks(session)
    if not content:
        message = 'The site is undergoing system upgrade'
        logging.info(message)
        print(message)
        return

    regex = DECK_REGEX.format(re.escape(deck_name))
    match = re.search(regex, content)
    if not match:
        logging.error('Deck %s not found, content length: %s',
                      deck_name, len(content))
        print('Deck {} not found'.format(deck_name))
        return

    deck_id = match.groups()[0]
    content_id = match.groups()[1]

    backup_name = '{} Backup'.format(deck_name)
    regex = DECK_REGEX.format(re.escape(backup_name))
    match = re.search(regex, content)
    if match:
        logging.info('Deck %s already exists', backup_name)
    else:
        logging.info('Creating a backup of the deck...')
        content = clone_deck(session, content, deck_id, backup_name)
        match = re.search(regex, content)
        if match:
            logging.info('Created deck %s', backup_name)
        else:
            logging.error('Deck %s not found, content length: %s',
                          backup_name, len(content))
            print('Deck {} not found'.format(backup_name))
            return

    backup_id = match.groups()[0]
    if 'decks' not in data:
        data['decks'] = {}

    data['decks'][deck_name] = {
        'content_id': content_id,
        'backup_id': backup_id,
        'deck_id': deck_id,
        'failed_content_ids': []
    }
    with open(CONF_PATH, 'w', encoding='utf-8') as fobj:
        json.dump(data, fobj, indent=4)

    cookies = session.cookies.get_dict()
    with open(COOKIES_PATH, 'w', encoding='utf-8') as fobj:
        json.dump(cookies, fobj, indent=4)

    deck_url = (
        'https://www.makeplayingcards.com/products/playingcard/design/dn_playingcards_front_dynamic.aspx?id={}'
        .format(deck_id))
    message = 'Deck {} successfully added to monitoring, URL: {}'.format(
        deck_name, deck_url)
    logging.info(message)
    print(message)
    print('See {} for details'.format(LOG_PATH))


def backup():  # pylint: disable=R0912,R0914,R0915
    """ Save all backups as new decks.
    """
    logging.info('Saving all backups as new decks')
    try:
        with open(CONF_PATH, 'r', encoding='utf-8') as fobj:
            data = json.load(fobj)
    except Exception as exc:
        raise ConfigurationError('No configuration found') from exc

    try:
        with open(COOKIES_PATH, 'r', encoding='utf-8') as fobj:
            cookies = json.load(fobj)
    except Exception as exc:
        raise ConfigurationError('No cookies found') from exc

    session = init_session(cookies)
    content = get_decks(session)
    if not content:
        logging.info('The site is undergoing system upgrade')
        return

    decks = data.get('decks', {})
    for deck_name in decks:
        logging.info('Processing %s', deck_name)
        content_id = data['decks'][deck_name]['content_id']
        backup_id = data['decks'][deck_name]['backup_id']
        backup_name = '{} Backup'.format(deck_name)
        regex = DECK_ID_REGEX.format(backup_id)
        match = re.search(regex, content)
        if not match:
            message = ('Deck {} not found, content length: {}'
                       .format(backup_name, len(content)))
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
            break

        temp_backup_name = '{} Backup Temp'.format(deck_name)
        logging.info('Creating a copy of the deck backup...')
        content = clone_deck(session, content, backup_id, temp_backup_name)
        regex = DECK_REGEX.format(re.escape(temp_backup_name))
        match = re.search(regex, content)
        if not match:
            message = 'Deck {} not found, content length: {}'.format(
                temp_backup_name, len(content))
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
            break

        new_backup_id = match.groups()[0]
        new_content_id = match.groups()[1]
        if new_content_id != content_id:
            message = 'Deck {} has incorrect content'.format(temp_backup_name)
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
            break

        logging.info('Deleting original deck backup...')
        content = delete_deck(session, content, backup_id, backup_name)
        regex = DECK_ID_REGEX.format(backup_id)
        match = re.search(regex, content)
        if match:
            message = 'Deck {} was not deleted'.format(backup_name)
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
            break

        logging.info('Renaming new deck backup...')
        content = clone_deck(session, content, new_backup_id, backup_name)
        regex = DECK_REGEX.format(re.escape(backup_name))
        match = re.search(regex, content)
        if not match:
            message = ('INCONSISTENT STATE: Deck {} not found, content '
                       'length: {}'.format(backup_name, len(content)))
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
            break

        backup_id = match.groups()[0]
        content_id = match.groups()[1]
        if content_id != new_content_id:
            message = ('INCONSISTENT STATE: Deck {} has incorrect content'
                       .format(backup_name))
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
            break

        data['decks'][deck_name]['backup_id'] = backup_id

        logging.info('Deleting redundant deck backup...')
        content = delete_deck(session, content, new_backup_id,
                              temp_backup_name)
        regex = DECK_ID_REGEX.format(new_backup_id)
        match = re.search(regex, content)
        if match:
            message = 'Deck {} was not deleted'.format(temp_backup_name)
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
            break

        logging.info('Successfully saved backup as a new deck')

    with open(CONF_PATH, 'w', encoding='utf-8') as fobj:
        json.dump(data, fobj, indent=4)

    cookies = session.cookies.get_dict()
    with open(COOKIES_PATH, 'w', encoding='utf-8') as fobj:
        json.dump(cookies, fobj, indent=4)


def test():  # pylint: disable=R0911,R0914,R0915
    """ Test all MakePlayingCards commands.
    """
    logging.info('Testing all MakePlayingCards commands')
    try:
        with open(CONF_PATH, 'r', encoding='utf-8') as fobj:
            data = json.load(fobj)
    except Exception as exc:
        raise ConfigurationError('No configuration found') from exc

    try:
        with open(COOKIES_PATH, 'r', encoding='utf-8') as fobj:
            cookies = json.load(fobj)
    except Exception as exc:
        raise ConfigurationError('No cookies found') from exc

    session = init_session(cookies)
    content = get_decks(session)
    if not content:
        logging.info('The site is undergoing system upgrade')
        return

    decks = data.get('decks', {})
    if not decks:
        logging.info('No decks in the configuration file')
        return

    deck_name = list(decks.keys())[0]
    deck_id = data['decks'][deck_name]['deck_id']
    content_id = data['decks'][deck_name]['content_id']
    regex = DECK_ID_REGEX.format(deck_id)
    match = re.search(regex, content)
    if not match:
        message = ('Deck {} not found, content length: {}'
                   .format(deck_name, len(content)))
        logging.error(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
        return

    temp_name = '{} Temp Test'.format(deck_name)
    logging.info('Creating a copy of the deck...')
    content = clone_deck(session, content, deck_id, temp_name)
    regex = DECK_REGEX.format(re.escape(temp_name))
    match = re.search(regex, content)
    if not match:
        message = 'Deck {} not found, content length: {}'.format(
            temp_name, len(content))
        logging.error(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
        return

    temp_id = match.groups()[0]
    temp_content_id = match.groups()[1]
    if temp_content_id != content_id:
        message = 'Deck {} has incorrect content'.format(temp_name)
        logging.error(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
        return

    logging.info('Renaming the deck...')
    temp_name_new = '{} New'.format(temp_name)
    try:
        content = rename_deck(session, temp_id, temp_name_new, temp_name)
    except ResponseError as exc:
        message = str(exc)
        logging.error(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
        return

    logging.info('Deleting the deck...')
    content = delete_deck(session, content, temp_id, temp_name_new)
    regex = DECK_ID_REGEX.format(temp_id)
    match = re.search(regex, content)
    if match:
        message = 'Deck {} was not deleted'.format(temp_name_new)
        logging.error(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
        return

    logging.info('All tests passed')

    cookies = session.cookies.get_dict()
    with open(COOKIES_PATH, 'w', encoding='utf-8') as fobj:
        json.dump(cookies, fobj, indent=4)


def refresh():  # pylint: disable=R0914
    """ Refresh all decks.
    """
    logging.info('Refreshing all decks')
    try:
        with open(CONF_PATH, 'r', encoding='utf-8') as fobj:
            data = json.load(fobj)
    except Exception as exc:
        raise ConfigurationError('No configuration found') from exc

    try:
        with open(COOKIES_PATH, 'r', encoding='utf-8') as fobj:
            cookies = json.load(fobj)
    except Exception as exc:
        raise ConfigurationError('No cookies found') from exc

    session = init_session(cookies)
    content = get_decks(session)
    if not content:
        logging.info('The site is undergoing system upgrade')
        return

    preview_data = re.findall(PREVIEW_REGEX, content)
    for i in range(len(preview_data)):  # pylint: disable=C0200
        preview_data[i] = preview_data[i][1:-1].split("','")

    preview_data = {p[0]:p for p in preview_data}

    decks = []
    for deck_name in data.get('decks', {}):
        decks.append({'name': deck_name,
                      'id': data['decks'][deck_name]['deck_id']})
        decks.append({'name': '{} Backup'.format(deck_name),
                      'id': data['decks'][deck_name]['backup_id']})

    for deck in decks:
        if deck['id'] not in preview_data:
            logging.error('Deck %s not found, content length: %s',
                          deck['name'], len(content))
            continue

        item = preview_data[deck['id']]
        deck['url'] = PREVIEW_URL.format(
            item[0], item[1], item[2], item[4],
            random.randint(100000, 1000000))

    decks.sort(key=lambda d: d['name'])
    broken_decks = []
    for deck in decks:
        logging.info('Refreshing %s, URL: %s', deck['name'], deck['url'])
        deck_content = send_get(session, deck['url'],
                                timeout=REFRESH_URL_TIMEOUT)
        logging.info('Content length: %s', len(deck_content))
        if not deck_content:
            broken_decks.append(deck['name'])
            logging.error('No response for deck %s', deck['name'])
            continue

        images = re.findall(IMAGE_REGEX, deck_content)
        images = [i for i in images if i.endswith('.jpg')]
        logging.info('Images found: %s', len(images))
        if len(images) < MIN_IMAGES:
            logging.error('Not enough images for deck %s', deck['name'])

    cookies = session.cookies.get_dict()
    with open(COOKIES_PATH, 'w', encoding='utf-8') as fobj:
        json.dump(cookies, fobj, indent=4)

    if broken_decks:
        message = 'Detected {} broken decks'.format(len(broken_decks))
        logging.error(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message),
                    '\n'.join(broken_decks))


def monitor():  # pylint: disable=R0912,R0914,R0915
    """ Run the monitoring checks.
    """
    try:
        with open(CONF_PATH, 'r', encoding='utf-8') as fobj:
            data = json.load(fobj)
    except Exception as exc:
        raise ConfigurationError('No configuration found') from exc

    try:
        with open(COOKIES_PATH, 'r', encoding='utf-8') as fobj:
            cookies = json.load(fobj)
    except Exception as exc:
        raise ConfigurationError('No cookies found') from exc

    session = init_session(cookies)
    content = get_decks(session)
    if not content:
        logging.info('The site is undergoing system upgrade')
        return

    not_found_errors = 0
    decks = data.get('decks', {})
    for deck_name in decks:
        content_id = data['decks'][deck_name]['content_id']
        deck_id = data['decks'][deck_name]['deck_id']
        backup_id = data['decks'][deck_name]['backup_id']
        logging.info('Processing %s', deck_name)
        regex = DECK_ID_REGEX.format(deck_id)
        match = re.search(regex, content)
        if not match:
            not_found_errors += 1
            if not_found_errors >= MAX_NOT_FOUND_ERRORS:
                message = 'Too many not found errors, exiting'
                logging.error(message)
                create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
                break

            message = 'Deck {} not found, content length: {}'.format(
                deck_name, len(content))
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
            continue

        actual_content_id = match.groups()[0]
        actual_deck_name = match.groups()[1]

        regex = DECK_ID_REGEX.format(backup_id)
        match = re.search(regex, content)
        if match:
            backup_content_id = match.groups()[0]
            if content_id != backup_content_id:
                if actual_content_id == backup_content_id:
                    logging.warning('Content ID has been changed for Deck %s '
                        'and its backup from %s to %s on MakePlayingCards '
                        'side', deck_name, content_id, backup_content_id)
                    content_id = backup_content_id
                    data['decks'][deck_name]['content_id'] = content_id
                else:
                    message = ('Content ID has been changed for Deck {} '
                               'Backup from {} to {}'.format(
                               deck_name, content_id, backup_content_id))
                    logging.error(message)
                    create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
                    continue
        else:
            not_found_errors += 1
            if not_found_errors >= MAX_NOT_FOUND_ERRORS:
                message = 'Too many not found errors, exiting'
                logging.error(message)
                create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
                break

            message = ('Deck {} Backup not found, content length: {} '
                       '(continuing the checks)'.format(deck_name,
                                                        len(content)))
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))

        if actual_content_id != content_id or actual_deck_name != deck_name:
            if (actual_content_id in
                    data['decks'][deck_name]['failed_content_ids']):
                logging.warning('Skipping known failed content ID %s for '
                    'Deck %s', actual_content_id, deck_name)
            else:
                new_content, new_deck_id = fix_deck(
                    session, data, content, deck_id, backup_id, deck_name,
                    actual_deck_name, content_id, actual_content_id)
                if new_content:
                    content = new_content
                    data['decks'][deck_name]['deck_id'] = new_deck_id
                else:
                    data['decks'][deck_name]['failed_content_ids'].append(
                        actual_content_id)

    with open(CONF_PATH, 'w', encoding='utf-8') as fobj:
        json.dump(data, fobj, indent=4)

    cookies = session.cookies.get_dict()
    with open(COOKIES_PATH, 'w', encoding='utf-8') as fobj:
        json.dump(cookies, fobj, indent=4)


def main():  # pylint: disable=R0912
    """ Main function.
    """
    logging.info('Started')
    try:
        if not internet_state():
            logging.warning('Internet is not available right now, exiting')
            return

        if len(sys.argv) > 1:
            if sys.argv[1] == 'refresh':
                refresh()
            elif sys.argv[1] == 'backup':
                backup()
            elif sys.argv[1] == 'test':
                test()
            elif sys.argv[1] == 'add':
                if len(sys.argv) > 2:
                    add_deck(sys.argv[2])
                else:
                    message = 'No deck name specified'
                    logging.error(message)
                    print(message)
            else:
                message = 'Unknown command: {}'.format(sys.argv[1])
                logging.error(message)
                print(message)
        else:
            monitor()
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
    if len(sys.argv) > 1 and sys.argv[1] not in {'refresh', 'backup', 'test'}:
        init_logging_manual()
    else:
        init_logging()

    main()
