# pylint: disable=W0703,C0301
""" Monitor MakePlayingCards shared URLs.
"""
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
SESSIONID_REGEX = \
    r'<form method="post" action="\.\/dn_preview_layout\.aspx\?ssid=([^"]+)"'
NEXT_REGEX = (
    r'<a href="javascript:__doPostBack\(&#39;([^&]+)&#39;,'
    r'&#39;([^&]+)&#39;\)" style="[^"]+">Next<\/a>')

DEFAULT_VIEWSTATE = \
    '/wEPDwUJNjAwNDE3MDgyDxYCHhNWYWxpZGF0ZVJlcXVlc3RNb2RlAgFkZKxwlxJ+dQzVGn0L8+0kT3Qk5oie'
DEFAULT_VIEWSTATEGENERATOR = '7D57AF60'
DEFAULT_HIDDGRECAPTCHAV3TOKEN = \
    '03AGdBq25A2GL4dhQ7lzrQbq4yeJycZQ2Hgi-5zhDei6hpGs3eap2F_eyLtIPSdtMPn5ardl-fTRFaxI8mj12HNBp-ezuEiTdRXRCHnuRt5039oDE1znUCzJhxz1l_R-kqpgGQoaXGPPjXvgOxeTYCaHXUcuq1PgCJrz4LPId18uvY0bZwPM9hdVA6avdiS_K_Ia7eLfWaPrBbuJvrS9L7hwW0uCP3cgaxRQdRF9tpLzo1ZEWEPmDUeYUaz_iHKoW44oZkthNjnb1SbJir0gz3_jmpslf4b-UUQZvO_-JNjkvYPmU9aOPmakhrk0WrdMzl74C5PlDEZSKdHmLUqSGlZ2OhgGu_2N9tbIVDlA5vkxL4koRPD2EQsnFoiDW5WZAmlzjdCzRjeDY79Aphs-PM508cKnl9CrDvvu9zDn36_jqqrRAf_YzJ-Rl1_VfMMoKpa-DAi_mUWleLWURV-Ik3b3YZbuCHe8gxQA'

DISCORD_USERS = '<@!637024738782216212> <@!134863257050677248> <@!464924763312226304>'
ALERT_SUBJECT_TEMPLATE = 'LotR MPC Monitor ALERT: {}'
ERROR_SUBJECT_TEMPLATE = 'LotR MPC Monitor ERROR: {}'
WARNING_SUBJECT_TEMPLATE = 'LotR MPC Monitor WARNING: {}'
MAIL_QUOTA = 50

CONF_PATH = 'mpc_monitor.json'
DISCORD_CONF_PATH = 'discord.yaml'
INTERNET_SENSOR_PATH = 'internet_state'
LOG_PATH = 'mpc_monitor.log'
MAIL_COUNTER_PATH = 'mpc_monitor.cnt'
MAILS_PATH = 'mails'

URL_TIMEOUT = 60
URL_RETRIES = 1
URL_SLEEP = 1
NEXT_LIMIT = 10


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
    if not os.path.exists(INTERNET_SENSOR_PATH):
        return True

    try:
        with open(INTERNET_SENSOR_PATH, 'r') as obj:
            value = obj.read()
            return value.strip() != 'off'
    except Exception as exc:
        message = str(exc)
        logging.warning(message)
        create_mail(WARNING_SUBJECT_TEMPLATE.format(message))
        return True


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
        subject = Header(subject, 'utf8').encode()

    path = os.path.join(MAILS_PATH,
                        '{}_{}'.format(int(time.time()), uuid.uuid4()))
    with open(path, 'w') as fobj:
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
        create_mail(WARNING_SUBJECT_TEMPLATE.format(message), skip_check=True)
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
            chunks = []
            while len(message) > 1900:
                chunks.append(message[:1900])
                message = message[1900:]

            chunks.append(message)
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


def init_session(cookies):
    """ Init session object.
    """
    session = requests.Session()
    session.cookies.update(cookies)
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

    return content


def clone_deck(session, content, deck_id, new_deck_name):
    """ Delete the deck.
    """
    viewstate, viewstategenerator = get_viewstate(session, content)
    form_data = init_form_data('btn_submit', viewstate, viewstategenerator,
                               hidd_type='saveas', hidd_value=deck_id,
                               hidd_project_name=new_deck_name)
    content = send_post(session, SAVED_PROJECTS_URL, form_data)
    if 'My saved projects' not in content:
        raise ResponseError('No saved projects found, content length: {}'
                            .format(len(content)))

    return content


def rename_deck(session, deck_id, deck_name, actual_deck_name):
    """ Rename a deck.
    """
    res = send_get(
        session,
        'https://www.makeplayingcards.com/design/dn_temporary_parse.aspx?id={}&edit=Y'
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
    if not '[CDATA[SUCCESS]]' in res:
        raise ResponseError('Deck {} was not renamed, response: {}'.format(
            actual_deck_name, res))

    content = get_decks(session)
    regex = DECK_REGEX.format(re.escape(deck_name))
    match = re.search(regex, content)
    if not match:
        raise ResponseError('Deck {} was not renamed, content length: {}'
                            .format(actual_deck_name, len(content)))

    return content


def fix_deck_rename(session, deck_id, deck_name, actual_deck_name):
    """ Fix a renamed deck.
    """
    message = ('Deck {} has been renamed to {}! Attempting to '
               'rename it automatically...'.format(deck_name,
                                                   actual_deck_name))
    discord_message = f"""Deck **{deck_name}** has been renamed to **{actual_deck_name}**!
Attempting to rename it automatically..."""
    logging.info(message)
    create_mail(ALERT_SUBJECT_TEMPLATE.format(message))
    send_discord(discord_message)

    try:
        content = rename_deck(session, deck_id, deck_name, actual_deck_name)
    except Exception as exc:
        message = ('Attempt to rename deck {} automatically failed: {}: {}'
                   .format(actual_deck_name, type(exc).__name__, str(exc)))
        logging.exception(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)
        discord_message = f"""Attempt to rename deck **{actual_deck_name}** automatically failed!
{DISCORD_USERS}"""
        send_discord(discord_message)
        return ''
    else:
        message = ('Attempt to rename deck {} automatically succeeded!'
                   .format(actual_deck_name))
        logging.info(message)
        create_mail(ALERT_SUBJECT_TEMPLATE.format(message))
        discord_message = f"""Attempt to rename deck **{actual_deck_name}** automatically succeeded!
{DISCORD_USERS}"""
        send_discord(discord_message)
        return content


def fix_deck(session, content, deck_id, backup_id, deck_name, actual_deck_name,  # pylint: disable=R0912,R0913,R0914,R0915
             content_id, actual_content_id):
    """ Fix a corrupted deck.
    """
    if actual_deck_name != deck_name:
        message = ('Deck {} has been changed and renamed to {}! Attempting to '
                   'fix it automatically...'.format(deck_name,
                                                    actual_deck_name))
        discord_message = f"""Deck **{deck_name}** has been changed and renamed to **{actual_deck_name}**!
Attempting to fix it automatically...
{DISCORD_USERS}"""
    else:
        message = ('Deck {} has been changed! Attempting to fix it '
                   'automatically...'.format(deck_name))
        discord_message = f"""Deck **{deck_name}** has been changed!
Attempting to fix it automatically...
{DISCORD_USERS}"""
    logging.info(message)
    create_mail(ALERT_SUBJECT_TEMPLATE.format(message))
    send_discord(discord_message)

    try:
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
            rename_deck(session, deck_id, 'Delete {}'.format(new_deck_name),
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
1. Open https://www.makeplayingcards.com/design/dn_temporary_designes.aspx and login into ALeP account (if needed)
2. Click Delete near {actual_deck_name} deck
3. Find {deck_name} Backup deck in the list, click Save As, type "{deck_name}" and click Save
4. Find {deck_name} deck in the list again, right click on the checkbox and copy its ID (after "chk_")
5. Construct a URL https://www.makeplayingcards.com/design/dn_temporary_parse.aspx?id=<ID>
6. Open https://www.blogger.com/u/6/blog/page/edit/2051510818249539805/6592070748291624930 and login into ALeP account (if needed)
7. Switch to Compose view (if needed) and update the link to that URL
"""
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message), body)
        discord_message = f"""Attempt to fix deck **{deck_name}** automatically failed!
Do the following:
(depending on the error, some steps may be already done)
1. Open https://www.makeplayingcards.com/design/dn_temporary_designes.aspx and login into ALeP account (if needed)
2. Click *Delete* near **{actual_deck_name}** deck
3. Find **{deck_name} Backup** deck in the list, click *Save As*, type "{deck_name}" and click *Save*
4. Find **{deck_name}** deck in the list again, right click on the checkbox and copy its ID (after "chk_")
5. Construct a URL https://www.makeplayingcards.com/design/dn_temporary_parse.aspx?id=<ID>
6. Open https://www.blogger.com/u/6/blog/page/edit/2051510818249539805/6592070748291624930 and login into ALeP account (if needed)
7. Switch to Compose view (if needed) and update the link to that URL
{DISCORD_USERS}"""
        send_discord(discord_message)
        return '', ''
    else:
        message = ('Attempt to fix deck {} automatically succeeded! '
                   'New deck ID: {}'.format(deck_name, new_deck_id))
        logging.info(message)
        body = f"""Do the following:
1. Open https://www.blogger.com/u/6/blog/page/edit/2051510818249539805/6592070748291624930 and login into ALeP account (if needed)
2. Switch to Compose view (if needed) and update the link to:
https://www.makeplayingcards.com/design/dn_temporary_parse.aspx?id={new_deck_id}
"""
        create_mail(ALERT_SUBJECT_TEMPLATE.format(message), body)
        discord_message = f"""Attempt to fix deck **{deck_name}** automatically succeeded!
Do the following:
1. Open https://www.blogger.com/u/6/blog/page/edit/2051510818249539805/6592070748291624930 and login into ALeP account (if needed)
2. Switch to Compose view (if needed) and update the link to:
https://www.makeplayingcards.com/design/dn_temporary_parse.aspx?id={new_deck_id}
{DISCORD_USERS}"""
        send_discord(discord_message)
        return content, new_deck_id


def run():
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

    session = init_session(data['cookies'])
    content = get_decks(session)
    if not content:
        logging.info('The site is undergoing system upgrade')
        return

    for deck_name in data.get('decks', {}):
        content_id = data['decks'][deck_name]['content_id']
        deck_id = data['decks'][deck_name]['deck_id']
        backup_id = data['decks'][deck_name]['backup_id']
        logging.info('Processing %s', deck_name)
        regex = DECK_ID_REGEX.format(deck_id)
        match = re.search(regex, content)
        if not match:
            message = 'Deck {} not found, content length: {}'.format(
                deck_name, len(content))
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
            continue

        actual_content_id = match.groups()[0]
        actual_deck_name = match.groups()[1]
        if actual_content_id != content_id:
            if (actual_content_id in
                    data['decks'][deck_name]['failed_content_ids']):
                logging.warning('Skipping known failed content ID: %s',
                                actual_content_id)
            else:
                new_content, new_deck_id = fix_deck(
                    session, content, deck_id, backup_id, deck_name,
                    actual_deck_name, content_id, actual_content_id)
                if new_content:
                    content = new_content
                    data['decks'][deck_name]['deck_id'] = new_deck_id
                else:
                    data['decks'][deck_name]['failed_content_ids'].append(
                        actual_content_id)
        elif actual_deck_name != deck_name:
            new_content = fix_deck_rename(session, deck_id, deck_name,
                                          actual_deck_name)
            if new_content:
                content = new_content

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
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)
        except Exception as exc_new:
            logging.exception(str(exc_new))
    finally:
        logging.info('Finished')


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
