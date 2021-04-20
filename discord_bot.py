# pylint: disable=C0103,C0302,W0703
# -*- coding: utf8 -*-
""" Discord bot.

You need to install a new dependency:
pip install discord.py==1.7.0

Create discord.yaml (see discord.default.yaml).
"""
import asyncio
from datetime import datetime
from email.header import Header
import json
import logging
import os
import random
import re
import shutil
import time
import uuid
import xml.etree.ElementTree as ET

import discord
import yaml

import lotr


CHANGES_PATH = os.path.join('Discord', 'Changes')
CONF_PATH = 'discord.yaml'
LOG_PATH = 'discord_bot.log'
MAIL_COUNTER_PATH = 'discord_bot.cnt'
MAILS_PATH = '/home/homeassistant/.homeassistant/mails'
PLAYTEST_PATH = os.path.join('Discord', 'playtest.json')
WORKING_DIRECTORY = '/home/homeassistant/lotr-lcg-set-generator/'

CRON_LOG_CMD = './cron_log.sh'
RCLONE_ART_CMD = './rclone_art.sh'

CMD_SLEEP_TIME = 2
IO_SLEEP_TIME = 1
MESSAGE_SLEEP_TIME = 1
RCLONE_ART_SLEEP_TIME = 300
WATCH_SLEEP_TIME = 5

ERROR_SUBJECT_TEMPLATE = 'LotR Discord Bot ERROR: {}'
WARNING_SUBJECT_TEMPLATE = 'LotR Discord Bot WARNING: {}'
MAIL_QUOTA = 50

CHANNEL_LIMIT = 500
ARCHIVE_CATEGORY = 'Archive'
CRON_CHANNEL = 'cron'
PLAYTEST_CHANNEL = 'playtesting-checklist'
UPDATES_CHANNEL = 'spreadsheet-updates'
GENERAL_CATEGORIES = {
    'Text Channels', 'Division of Labor', 'Player Card Design', 'Printing',
    'Rules', 'Voice Channels', 'Archive'
}

EMOJIS = {
    '[leadership]': '<:leadership:822573464601886740>',
    '[lore]': '<:lore:822573464678301736>',
    '[spirit]': '<:spirit:822573464417206273>',
    '[tactics]': '<:tactics:822573464593629264>',
    '[baggins]': '<:baggins:822573762415296602>',
    '[fellowship]': '<:fellowship:822573464586027058>',
    '[unique]': '<:unique:822573762474016818>',
    '[threat]': '<:threat:822572608994148362>',
    '[attack]': '<:attack:822573464367792221>',
    '[defense]': '<:defense:822573464615518209>',
    '[willpower]': '<:willpower:822573464367792170>',
    '[sunny]': '<:sunny:826923723655217212>',
    '[cloudy]': '<:cloudy:826923723734253589>',
    '[rainy]': '<:rainy:826923723667669043>',
    '[stormy]': '<:stormy:826923723646173236>',
    '[sailing]': '<:sailing:826923723780784168>',
    '[eos]': '<:eyeofsauron:826923723662557215>',
    '[eyeofsauron]': '<:eyeofsauron:826923723662557215>',
    '[pp]': '<:pp:823008093898145792>',
    '[hitpoints]': '<:hitpoints:822572931254714389>',
    '[progress]': '<:progress:823007871494520872>'
}

HELP = {
    'alepcard': """
List of **!alepcard** commands:

**!alepcard <card name>** - display the first card matching a given card name (for example: `!alepcard Thengel`)
**!alepcard <card name> n:<number>** - display the card #number matching a given card name (for example: `!alepcard Back Card n:2`)
**!alepcard <card name> s:<set code>** - display the first card matching a given card name from a given set (for example: `!alepcard Back Card s:CoE`)
**!alepcard <card name> s:<set code> n:<number>** - display the card #number matching a given card name from a given set (for example: `!alepcard Roused s:TSotS n:2`)
**!alepcard this** - if in a card channel, display this card
**!alepcard help** - display this help message
""",
    'cron': """
List of **!cron** commands:

**!cron errors** - display all errors from the latest cron run
**!cron log** - display a full execution log of the latest cron run
**!cron trigger** - trigger reprocessing of all sheets in the next cron run
**!cron help** - display this help message
""",
    'playtest': """
List of **!playtest** commands:

**!playtest view** - display existing playtesting target

**!playtest new
<optional description>
<list of targets>**
Create a new list of targets, for example:
```
!playtest new
Deadline: tomorrow.
1. Escape From Dol Guldur (solo)
2. Frogs deck
```
**!playtest add
<optional new description>
<list of new targets>**
Add new target(s) to the current list, for example:
```
!playtest add
3. Frogs deck (again)
```
**!playtest complete <target>
<mandatory playtesting report>**
Mark a given target as completed by you, for example:
```
!playtest complete 5
Some report
```
**!playtest remove <target or list of targets separated by space>** - remove a given target or a list of targets (for example: `!playtest remove 11 12`)

**!playtest update <target or list of targets separated by space> <player>** - mark a given target or a list of targets as completed by a given player (for example: `!playtest update 7 Shellin`)

**!playtest random <number>** - generate a random number from 1 to a given number (for example: `!playtest random 10`)

**!playtest help** - display this help message
""",
    'stat': """
List of **!stat** commands:

**!stat channels** - number of Discord channels and free channel slots
**!stat quest <quest>** - display the quest statistics (for example: `!stat quest The Battle for the Beacon`)
**!stat help** - display this help message
""",
    'art': """
List of **!art** commands:

**!art save <artist>** (as a reply to a message with an image attachment) - save the image as a card's artwork for the front side (for example: `!art save Ted Nasmith`)
**!art saveb <artist>** (as a reply to a message with an image attachment) - save the image as a card's artwork for the back side (for example: `!art saveb John Howe`)
**!art help** - display this help message
"""
}

CARD_DECK_SECTION = '_Deck Section'

CARD_DATA = {}
CONF = {}
EXTERNAL_DATA = {}
EXTERNAL_FILES = set()

playtest_lock = asyncio.Lock()
art_lock = asyncio.Lock()


class DiscordError(Exception):
    """ Discord error.
    """


class FormatError(Exception):
    """ Change format error.
    """


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')


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


def get_discord_configuration():
    """ Get Discord configuration.
    """
    try:
        with open(CONF_PATH, 'r') as f_conf:
            conf = yaml.safe_load(f_conf)

        return conf
    except Exception as exc:
        logging.exception(str(exc))
        create_mail(ERROR_SUBJECT_TEMPLATE.format(
            'error obtaining Discord configuration: {}'.format(str(exc))))
        return {}


async def run_shell(cmd):
    """ Run a shell command.
    """
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
    except Exception:
        return ''

    stdout = stdout.decode('utf-8').strip()
    stderr = stderr.decode('utf-8').strip()
    return (stdout, stderr)


async def get_errors():
    """ Get errors of the last cron execution.
    """
    try:
        proc = await asyncio.create_subprocess_shell(
            './cron_errors.sh',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
    except Exception:
        return ''

    res = stdout.decode('utf-8').strip()
    return res


def split_result(value):
    """ Split result into chunks.
    """
    res = []
    chunk = ''
    for line in value.split('\n'):
        if len(chunk + line) + 1 <= 1900:
            chunk += line + '\n'
        else:
            res.append(chunk)
            chunk = line + '\n'

    res.append(chunk)
    return res


def format_playtest_message(data):
    """ Format playtest message to post to Discord.
    """
    res = ''
    if data['description']:
        res += '{}\n'.format(data['description'])

    for line in data['targets']:
        completed = '~~' if line['completed'] else ''
        user = ' (**{}**)'.format(line['user']) if line['user'] else ''
        res += '{}{}. {}{}{}\n'.format(completed,  # pylint: disable=W1308
                                       line['num'],
                                       line['title'],
                                       completed,
                                       user)

    res = res.strip()
    return res


async def read_json_data(path):
    """ Read data from a JSON file.
    """
    try:
        with open(path, 'r') as obj:
            data = json.load(obj)
    except Exception:
        await asyncio.sleep(IO_SLEEP_TIME)
        with open(path, 'r') as obj:
            data = json.load(obj)

    return data


async def read_card_data():
    """ Read card data generated by the cron job.
    """
    size = os.path.getsize(lotr.DISCORD_CARD_DATA_PATH)
    mtime = os.path.getmtime(lotr.DISCORD_CARD_DATA_PATH)
    if size == CARD_DATA.get('size') and mtime == CARD_DATA.get('mtime'):
        return CARD_DATA['cache']

    data = await read_json_data(lotr.DISCORD_CARD_DATA_PATH)
    data['dict'] = {r[lotr.CARD_ID]:r for r in data['data']}

    CARD_DATA['cache'] = data
    CARD_DATA['size'] = size
    CARD_DATA['mtime'] = mtime
    return data


def read_external_data():
    """ Read external card data.
    """
    new_files = set()
    for _, _, filenames in os.walk(lotr.URL_CACHE_PATH):
        for filename in filenames:
            if filename.endswith('.cache'):
                new_files.add(filename)

        break

    new_files = new_files.difference(EXTERNAL_FILES)
    for new_file in new_files:
        EXTERNAL_FILES.add(new_file)
        data = lotr.load_external_xml(re.sub(r'\.cache$', '', new_file))
        EXTERNAL_DATA.update({r[lotr.CARD_ID]:r for r in data})

    return EXTERNAL_DATA


def card_match(card_name, card_back_name, search_name):
    """ Compare a search name with a card name.
    """
    if search_name in (card_name, card_back_name):
        return 1

    if (card_name.startswith(search_name + '-') or
            card_back_name.startswith(search_name + '-')):
        return 2

    if ('-' + search_name + '-' in card_name or
            '-' + search_name + '-' in card_back_name):
        return 3

    if (card_name.endswith('-' + search_name) or
            card_back_name.endswith('-' + search_name)):
        return 3

    return 0


def update_text(text):  # pylint: disable=R0915
    """ Update card text.
    """
    text = re.sub(r'\b(Quest Resolution)( \([^\)]+\))?:', '[b]\\1[/b]\\2:',
                  text)
    text = re.sub(r'\b(Valour )?(Resource |Planning |Quest |Travel |Encounter '
                  r'|Combat |Refresh )?(Action):', '[b]\\1\\2\\3[/b]:', text)
    text = re.sub(r'\b(When Revealed|Setup|Forced|Valour Response|Response'
                  r'|Travel|Shadow|Resolution):', '[b]\\1[/b]:', text)
    text = re.sub(r'\b(Condition)\b', '[bi]\\1[/bi]', text)

    def _fix_bi_in_b(match):
        return '[b]{}[/b]'.format(
            match.groups()[0].replace('[bi]', '[i]').replace('[/bi]', '[/i]'))

    def _fix_bi_in_i(match):
        return '[i]{}[/i]'.format(
            match.groups()[0].replace('[bi]', '[b]').replace('[/bi]', '[/b]'))

    text = re.sub(r'\[b\](.+?)\[\/b\]', _fix_bi_in_b, text, flags=re.DOTALL)
    text = re.sub(r'\[i\](.+?)\[\/i\]', _fix_bi_in_i, text, flags=re.DOTALL)

    text = re.sub(r'\[bi\]', '***', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/bi\]', '***', text, flags=re.IGNORECASE)
    text = re.sub(r'\[b\]', '**', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/b\]', '**', text, flags=re.IGNORECASE)
    text = re.sub(r'\[i\]', '*', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/i\]', '*', text, flags=re.IGNORECASE)
    text = re.sub(r'\[u\]', '`__', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/u\]', '__', text, flags=re.IGNORECASE)
    text = re.sub(r'\[strike\]', '~~', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/strike\]', '~~', text, flags=re.IGNORECASE)

    text = text.replace('[willpower]', EMOJIS['[willpower]'])
    text = text.replace('[threat]', EMOJIS['[threat]'])
    text = text.replace('[attack]', EMOJIS['[attack]'])
    text = text.replace('[defense]', EMOJIS['[defense]'])
    text = text.replace('[leadership]', EMOJIS['[leadership]'])
    text = text.replace('[spirit]', EMOJIS['[spirit]'])
    text = text.replace('[tactics]', EMOJIS['[tactics]'])
    text = text.replace('[lore]', EMOJIS['[lore]'])
    text = text.replace('[baggins]', EMOJIS['[baggins]'])
    text = text.replace('[fellowship]', EMOJIS['[fellowship]'])
    text = text.replace('[unique]', EMOJIS['[unique]'])
    text = text.replace('[sunny]', EMOJIS['[sunny]'])
    text = text.replace('[cloudy]', EMOJIS['[cloudy]'])
    text = text.replace('[rainy]', EMOJIS['[rainy]'])
    text = text.replace('[stormy]', EMOJIS['[stormy]'])
    text = text.replace('[sailing]', EMOJIS['[sailing]'])
    text = text.replace('[eos]', EMOJIS['[eos]'])
    text = text.replace('[pp]', EMOJIS['[pp]'])

    text = text.replace('[', '`[')
    text = text.replace(']', ']`')
    text = text.replace('``', '')

    text = re.sub(r'`\[lsb\]`', '[', text, flags=re.IGNORECASE)
    text = re.sub(r'`\[rsb\]`', ']', text, flags=re.IGNORECASE)

    text = text.strip()
    text = re.sub(r' +(?=\n)', '', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'(?<![\n`])\n(?!\n)', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text


def format_side(card, prefix):  # pylint: disable=R0912,R0914,R0915
    """ Format a card side.
    """
    card_name = '**{}**'.format(card[prefix + lotr.CARD_NAME])
    card_type = card[prefix + lotr.CARD_TYPE]

    card_unique = ('{} '.format(EMOJIS['[unique]'])
                   if card.get(prefix + lotr.CARD_UNIQUE)
                   else '')

    sphere = card.get(prefix + lotr.CARD_SPHERE, '')
    if sphere in ('Leadership', 'Lore', 'Spirit', 'Tactics', 'Baggins',
                  'Fellowship'):
        card_sphere = '*{}* {} '.format(sphere,
                                        EMOJIS['[{}]'.format(sphere.lower())])
    elif sphere in ('Neutral', 'Boon', 'Burden', 'Nightmare', 'Upgraded'):
        card_sphere = '*{}* '.format(sphere)
    else:
        card_sphere = ''

    cost = card.get(prefix + lotr.CARD_COST, '')
    if cost == '' or card_type == 'Quest':
        card_cost = ''
    elif card_type == 'Hero':
        card_cost = ', *Threat Cost*: **{}**'.format(cost)
    else:
        card_cost = ', *Cost*: **{}**'.format(cost)

    engagement = card.get(prefix + lotr.CARD_ENGAGEMENT, '')
    if engagement == '' or card_type == 'Quest':
        card_engagement = ''
    else:
        card_engagement = ', *Engagement Cost*: **{}**'.format(engagement)

    if card_type == 'Quest':
        card_stage = ', **{}{}**'.format(
            card.get(prefix + lotr.CARD_COST, ''),
            card.get(prefix + lotr.CARD_ENGAGEMENT, ''))
    else:
        card_stage = ''

    card_skills = ''
    skill_map = {
        'threat': prefix + lotr.CARD_THREAT,
        'willpower': prefix + lotr.CARD_WILLPOWER,
        'attack': prefix + lotr.CARD_ATTACK,
        'defense': prefix + lotr.CARD_DEFENSE,
        'hitpoints': prefix + lotr.CARD_HEALTH,
        'progress': prefix + lotr.CARD_QUEST
    }
    for skill in skill_map:
        if card.get(skill_map[skill], '') != '':
            card_skills += '   {} {}'.format(EMOJIS['[{}]'.format(skill)],
                                             card[skill_map[skill]])

    card_skills = card_skills.strip()
    if card_skills:
        card_skills = '\n' + card_skills

    traits = card.get(prefix + lotr.CARD_TRAITS, '')
    card_traits = '' if traits == '' else '***{}***\n'.format(traits)

    keywords = update_text(card.get(prefix + lotr.CARD_KEYWORDS, ''))
    if keywords == '':
        card_keywords = ''
    elif keywords.endswith('`[inline]`'):
        card_keywords = '{} '.format(re.sub(r'`\[inline\]`$', '', keywords))
    else:
        card_keywords = '{}\n'.format(keywords)

    card_text = update_text(card.get(prefix + lotr.CARD_TEXT, ''))

    shadow = update_text(card.get(prefix + lotr.CARD_SHADOW, ''))
    card_shadow = (
        '' if shadow == ''
        else '\n**\\~\\~\\~\\~\\~\\~\\~\\~\\~\\~**\n{}'.format(shadow))

    victory = card.get(prefix + lotr.CARD_VICTORY, '')
    if victory == '':
        card_victory = ''
    elif card_type in ('Presentation', 'Rules'):
        card_victory = '\n**Page {}**'.format(victory)
    elif lotr.is_positive_or_zero_int(victory):
        card_victory = '\n**VICTORY {}**'.format(victory)
    else:
        card_victory = '\n**{}**'.format(victory)

    special_icon = card.get(prefix + lotr.CARD_SPECIAL_ICON, '')
    if special_icon == '':
        card_special_icon = ''
    else:
        card_special_icon = '\n{}'.format(
            EMOJIS['[{}]'.format(special_icon.lower().replace(' ', ''))])

    flavour = update_text(card.get(prefix + lotr.CARD_FLAVOUR, ''))
    card_flavour = '' if flavour == '' else '\n\n*{}*'.format(flavour)

    artist = card.get(prefix + lotr.CARD_ARTIST, '')
    card_artist = '' if artist == '' else '\n\n*Artist*: {}'.format(artist)

    res = f"""{card_unique}{card_name}
{card_sphere}{card_type}{card_cost}{card_engagement}{card_stage}{card_skills}

{card_traits}{card_keywords}{card_text}{card_shadow}{card_victory}{card_special_icon}{card_flavour}{card_artist}"""  # pylint: disable=C0301
    return res


def format_card(card, spreadsheet_url, channel_url):  # pylint: disable=R0912,R0914,R0915
    """ Format the card.
    """
    card_type = card[lotr.CARD_TYPE]
    res_a = format_side(card, '')
    if (card.get(lotr.BACK_PREFIX + lotr.CARD_NAME) and
            card_type != 'Presentation' and
            (card_type not in ('Rules', 'Campaign', 'Contract', 'Nightmare') or
             card.get(lotr.BACK_PREFIX + lotr.CARD_TEXT))):
        res_b = '\n\n`SIDE B`\n\n{}'.format(format_side(card, lotr.BACK_PREFIX))
    else:
        res_b = ''

    adventure = card.get(lotr.CARD_ADVENTURE, '')
    if adventure == '':
        card_adventure = ''
    elif card_type == 'Campaign':
        card_adventure = '*Campaign*: {}\n'.format(adventure)
    else:
        card_adventure = '*Adventure*: {}\n'.format(adventure)

    encounter_set = card.get(lotr.CARD_ENCOUNTER_SET, '')
    additional_sets = card.get(lotr.CARD_ADDITIONAL_ENCOUNTER_SETS, '')
    if additional_sets != '':
        additional_sets = ' (+{})'.format(additional_sets).replace(';', ',')

    card_encounter_set = (
        '' if encounter_set == ''
        else '*Encounter Set*: {}{}\n'.format(encounter_set, additional_sets))

    card_set = re.sub(r'^ALeP - ', '', card[lotr.CARD_SET_NAME])
    card_id = '*id:* {}'.format(card[lotr.CARD_ID])

    card_number = '**#{}**'.format(card[lotr.CARD_NUMBER])
    if (card.get(lotr.CARD_PRINTED_NUMBER) or
            card.get(lotr.BACK_PREFIX + lotr.CARD_PRINTED_NUMBER)):
        if res_b:
            front_number = (card.get(lotr.CARD_PRINTED_NUMBER) or
                            card[lotr.CARD_NUMBER])
            back_number = (card.get(lotr.BACK_PREFIX +
                                    lotr.CARD_PRINTED_NUMBER) or
                           card[lotr.CARD_NUMBER])
            card_number = '{} *({}/{})*'.format(card_number, front_number,
                                                back_number)
        else:
            front_number = (card.get(lotr.CARD_PRINTED_NUMBER) or
                            card[lotr.CARD_NUMBER])
            card_number = '{} *({})*'.format(card_number, front_number)

    icon = card.get(lotr.CARD_ICON, '')
    card_icon = '' if icon == '' else ' ({})'.format(icon)

    version = card.get(lotr.CARD_VERSION, '')
    card_version = '' if version == '' else ' **{}**'.format(version)

    quantity = card[lotr.CARD_QUANTITY]
    removed_easy_mode = card.get(lotr.CARD_EASY_MODE, 0)
    if removed_easy_mode > 0:
        easy_mode = '/x{}'.format(quantity - removed_easy_mode)
    else:
        easy_mode = ''

    card_quantity = '(x{}{})'.format(quantity, easy_mode)

    deck_rules = card.get(lotr.CARD_DECK_RULES, '')
    card_deck_rules = ('' if deck_rules == ''
                       else '*Deck Rules*:\n```{}```\n'.format(deck_rules))

    if card.get(lotr.CARD_RINGSDB_CODE):
        ringsdb_url = '<https://test.ringsdb.com/card/{}>\n'.format(
            card[lotr.CARD_RINGSDB_CODE])
    else:
        ringsdb_url = ''

    row_url = '<{}&range=A{}>'.format(spreadsheet_url, card[lotr.ROW_COLUMN])
    if channel_url:
        channel_url = '<{}>'.format(channel_url)

    res = f"""{res_a}{res_b}

{card_set}{card_icon}, {card_number}{card_version} {card_quantity}
{card_encounter_set}{card_adventure}{card_id}

{card_deck_rules}{ringsdb_url}{row_url}
{channel_url}"""
    res = re.sub(r'\n{3,}', '\n\n', res)
    res = res.replace('\n\n', '\n` `\n')
    res = res.strip()
    return res


def format_match(card, num):
    """ Format a match.
    """
    card_unique = ('{} '.format(EMOJIS['[unique]'])
                   if card.get(lotr.CARD_UNIQUE)
                   else '')
    card_name = card[lotr.CARD_NAME]
    card_type = card[lotr.CARD_TYPE]

    sphere = card.get(lotr.CARD_SPHERE, '')
    if sphere in ('Leadership', 'Lore', 'Spirit', 'Tactics', 'Baggins',
                  'Fellowship'):
        card_type = '{} {} {}'.format(sphere,
                                      EMOJIS['[{}]'.format(sphere.lower())],
                                      card_type)
    elif sphere in ('Neutral', 'Boon', 'Burden', 'Nightmare', 'Upgraded'):
        card_type = '{} {}'.format(sphere, card_type)

    card_name_back = card.get(lotr.BACK_PREFIX + lotr.CARD_NAME)
    if card_name_back and card_name_back != card_name:
        card_unique_back = ('{} '.format(EMOJIS['[unique]'])
                            if card.get(lotr.BACK_PREFIX + lotr.CARD_UNIQUE)
                            else '')
        card_name = '{} / {}{}'.format(card_name, card_unique_back,
                                       card_name_back)

    card_type_back = card.get(lotr.BACK_PREFIX + lotr.CARD_TYPE, '')
    sphere = card.get(lotr.BACK_PREFIX + lotr.CARD_SPHERE, '')
    if sphere in ('Leadership', 'Lore', 'Spirit', 'Tactics', 'Baggins',
                  'Fellowship'):
        card_type_back = '{} {} {}'.format(
            sphere, EMOJIS['[{}]'.format(sphere.lower())], card_type_back)
    elif sphere in ('Neutral', 'Boon', 'Burden', 'Nightmare', 'Upgraded'):
        card_type_back = '{} {}'.format(sphere, card_type_back)

    if card_type_back and card_type_back != card_type:
        card_type = '{} / {}'.format(card_type, card_type_back)

    card_set = re.sub(r'^ALeP - ', '', card[lotr.CARD_SET_NAME])
    card_number = '*#{}*'.format(card[lotr.CARD_NUMBER])
    res = f'**{num}.** {card_unique}{card_name}  (*{card_type}*, {card_set}, {card_number})'
    return res


def format_matches(matches, num):
    """ Format other matches.
    """
    res = []
    for i, (card, _) in enumerate(matches):
        prefix = '**>>>**  ' if i == num - 1 else ''
        res.append(prefix + format_match(card, i + 1))

    return '\n'.join(res)


def delete_sheet_checksums():
    """ Delete existing spredsheet checksums.
    """
    os.remove(lotr.SHEETS_JSON_PATH)


async def read_deck_xml(path):
    """ Read deck XML file.
    """
    data = {}
    data.update(read_external_data())
    data.update((await read_card_data())['dict'])

    cards = []
    tree = ET.parse(path)
    root = tree.getroot()
    for section in root:
        section_name = section.attrib.get('name')
        if not section_name:
            continue

        for card in section:
            card_id = card.attrib['id']
            if card_id not in data:
                continue

            row = data[card_id].copy()
            if row[lotr.CARD_TYPE] not in lotr.CARD_TYPES_ENCOUNTER_SET:
                continue

            row[lotr.CARD_QUANTITY] = int(card.attrib['qty'])
            row[CARD_DECK_SECTION] = section_name
            cards.append(row)

    return cards


def get_quest_stat(cards):  # pylint: disable=R0912,R0915
    """ Get quest statistics.
    """
    res = {}
    encounter_sets = set()
    keywords = set()
    card_types = {}

    for card in cards:
        if card.get(lotr.CARD_KEYWORDS):
            keywords = keywords.union(
                lotr.extract_keywords(card[lotr.CARD_KEYWORDS]))

        if card.get(lotr.CARD_ENCOUNTER_SET):
            encounter_sets.add(card[lotr.CARD_ENCOUNTER_SET])

        if card.get(lotr.CARD_ADDITIONAL_ENCOUNTER_SETS):
            encounter_sets = encounter_sets.union(
                [s.strip() for s in
                 str(card[lotr.CARD_ADDITIONAL_ENCOUNTER_SETS]).split(';')])

        card_type = card[lotr.CARD_TYPE]
        if card.get(lotr.CARD_SPHERE) in ('Boon', 'Burden'):
            card_type = '{} ({})'.format(card_type, card[lotr.CARD_SPHERE])

        card_types[card_type] = (
            card_types.get(card_type, 0) + card[lotr.CARD_QUANTITY])

    if encounter_sets:
        res['encounter_sets'] = '*Encounter Sets*: {}\n'.format(
            ', '.join(sorted(encounter_sets)))
    else:
        res['encounter_sets'] = ''

    if keywords:
        res['keywords'] = '*Keywords*: {}\n'.format(
            ', '.join(sorted(keywords)))
    else:
        res['keywords'] = ''

    card_types = sorted(list(card_types.items()), key=lambda t: t[0])
    card_types = sorted(card_types, key=lambda t: t[1], reverse=True)
    res['total'] = '*Cards*: {}\n'.format(sum(t[1] for t in card_types))
    res['card_types'] = '\n'.join('*{}*: {}'.format(
        t[0], t[1]) for t in card_types)

    card_types = {}
    threat = 0
    max_threat = 0
    shadow = 0
    surge = 0

    res['encounter_deck'] = ''
    deck = [card for card in cards if card[CARD_DECK_SECTION] == 'Encounter']
    for card in deck:
        card_type = card[lotr.CARD_TYPE]
        if card.get(lotr.CARD_SPHERE) in ('Boon', 'Burden'):
            card_type = '{} ({})'.format(card_type, card[lotr.CARD_SPHERE])

        card_types[card_type] = (
            card_types.get(card_type, 0) + card[lotr.CARD_QUANTITY])

        if lotr.is_positive_int(card.get(lotr.CARD_THREAT)):
            threat += int(card[lotr.CARD_THREAT]) * card[lotr.CARD_QUANTITY]
            max_threat = max(max_threat, int(card[lotr.CARD_THREAT]))

        if card.get(lotr.CARD_SHADOW):
            shadow += card[lotr.CARD_QUANTITY]

        if card.get(lotr.CARD_KEYWORDS):
            if 'Surge' in lotr.extract_keywords(card[lotr.CARD_KEYWORDS]):
                surge += card[lotr.CARD_QUANTITY]

    if not card_types:
        return res

    card_types = sorted(list(card_types.items()), key=lambda t: t[0])
    card_types = sorted(card_types, key=lambda t: t[1], reverse=True)
    total = sum(t[1] for t in card_types)
    card_types = [(t[0], '{} ({}%)'.format(t[1], round(t[1] * 100 / total)))
                  for t in card_types]
    res['encounter_deck'] = '**Encounter Deck**\n*Cards*: {}\n\n{}\n\n'.format(
        total, '\n'.join('*{}*: {}'.format(t[0], t[1]) for t in card_types))

    if shadow:
        res['encounter_deck'] += '*Shadow*: {} ({}%)\n'.format(
            shadow, round(shadow * 100 / total))

    if surge:
        res['encounter_deck'] += '*Surge*: {} ({}%)\n'.format(
            surge, round(surge * 100 / total))

    res['encounter_deck'] += '*Threat*: {} (Avg), {} (Max)\n\n'.format(
        round(threat / total, 1), max_threat)

    return res


class MyClient(discord.Client):  # pylint: disable=R0902
    """ My bot class.
    """

    archive_category = None
    cron_channel = None
    playtest_channel = None
    updates_channel = None
    rclone_art = False
    categories = {}
    channels = {}
    general_channels = {}


    async def on_ready(self):
        """ Invoked when the client is ready.
        """
        logging.info('Logged in as %s (%s)', self.user.name, self.user.id)
        try:
            self.archive_category = self.get_channel(
                [c for c in self.get_all_channels()
                 if str(c.type) == 'category' and
                 c.name == ARCHIVE_CATEGORY][0].id)
        except Exception as exc:
            logging.exception(str(exc))
            create_mail(WARNING_SUBJECT_TEMPLATE.format(
                'error obtaining archive category: {}'.format(str(exc))))

        try:
            self.cron_channel = self.get_channel(
                [c for c in self.get_all_channels()
                 if str(c.type) == 'text' and
                 c.name == CRON_CHANNEL][0].id)
        except Exception as exc:
            logging.exception(str(exc))
            create_mail(WARNING_SUBJECT_TEMPLATE.format(
                'error obtaining Cron channel: {}'.format(str(exc))))

        try:
            self.playtest_channel = self.get_channel(
                [c for c in self.get_all_channels()
                 if str(c.type) == 'text' and
                 c.name == PLAYTEST_CHANNEL][0].id)
        except Exception as exc:
            logging.exception(str(exc))
            create_mail(WARNING_SUBJECT_TEMPLATE.format(
                'error obtaining Playtest channel: {}'.format(str(exc))))

        try:
            self.updates_channel = self.get_channel(
                [c for c in self.get_all_channels()
                 if str(c.type) == 'text' and
                 c.name == UPDATES_CHANNEL][0].id)
        except Exception as exc:
            logging.exception(str(exc))
            create_mail(WARNING_SUBJECT_TEMPLATE.format(
                'error obtaining Spreadsheet Updates channel: {}'
                .format(str(exc))))

        self.categories, self.channels, self.general_channels = (
            await self._load_channels())
        await self._test_channels()
        self.loop.create_task(self._watch_changes_schedule())
        self.loop.create_task(self._rclone_art_schedule())
        read_external_data()
        await read_card_data()


    async def _load_channels(self):  # pylint: disable=R0912
        categories = {}
        channels = {}
        general_channels = {}
        for channel in self.get_all_channels():
            if str(channel.type) == 'category':
                if channel.name in GENERAL_CATEGORIES:
                    continue

                if channel.name in categories:
                    logging.warning(
                        'Duplicate category name detected: %s', channel.name)
                else:
                    categories[channel.name] = {
                        'name': channel.name,
                        'id': channel.id,
                        'position': channel.position}
            elif str(channel.type) == 'text' and channel.name == 'general':
                if (not channel.category_id
                        or channel.category.name in GENERAL_CATEGORIES):
                    continue

                if channel.category.name in general_channels:
                    logging.warning(
                        'Duplicate general channel for category "%s" detected',
                        channel.category.name)
                else:
                    general_channels[channel.category.name] = {
                        'name': channel.category.name,
                        'id': channel.id,
                        'category_id': channel.category_id}
            elif str(channel.type) == 'text':
                if (not channel.category_id
                        or channel.category.name in GENERAL_CATEGORIES):
                    continue

                if channel.name in channels:
                    logging.warning(
                        'Duplicate channel name detected: %s (categories "%s" '
                        'and "%s")',
                        channel.name,
                        channels[channel.name]['category_name'],
                        channel.category.name)
                else:
                    channels[channel.name] = {
                        'name': channel.name,
                        'id': channel.id,
                        'category_id': channel.category_id,
                        'category_name': channel.category.name}

        return categories, channels, general_channels


    async def _watch_changes_schedule(self):
        while True:
            await self._watch_changes()
            await asyncio.sleep(WATCH_SLEEP_TIME)


    async def _rclone_art_schedule(self):
        while True:
            await self._rclone_art()
            await asyncio.sleep(RCLONE_ART_SLEEP_TIME)


    async def _watch_changes(self):
        try:
            for _, _, filenames in os.walk(CHANGES_PATH):
                filenames.sort()
                for filename in filenames:
                    if (not filename.endswith('.json') or
                            filename.startswith('__')):
                        continue

                    path = os.path.join(CHANGES_PATH, filename)
                    try:
                        data = await read_json_data(path)
                        logging.info('Processing changes: %s', data)
                        await self._process_category_changes(data)
                        await self._process_channel_changes(data)
                        await self._process_card_changes(data)
                    except Exception as exc:
                        logging.exception(str(exc))
                        message = 'error processing {}: {}'.format(
                            filename, str(exc))
                        create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
                        if self.cron_channel:
                            await self._send_channel(self.cron_channel,
                                                     message)

                        shutil.move(path, os.path.join(
                            CHANGES_PATH, '__{}'.format(filename)))
                    else:
                        os.remove(path)

                break
        except Exception as exc:
            logging.exception(str(exc))
            create_mail(ERROR_SUBJECT_TEMPLATE.format(
                'unexpected error during watching for changes: {}'
                .format(str(exc))))


    async def _rclone_art(self):
        if not self.rclone_art:
            return

        self.rclone_art = False
        stdout, stderr = await run_shell(RCLONE_ART_CMD)
        if stdout != 'Done':
            message = 'RClone failed, stdout: {}, stderr: {}'.format(stdout,
                                                                     stderr)
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
            return

        artwork_destination_path = CONF.get('artwork_destination_path')
        if not artwork_destination_path:
            return

        async with art_lock:
            if self.rclone_art:
                return

            for _, subfolders, _ in os.walk(artwork_destination_path):
                for subfolder in subfolders:
                    shutil.rmtree(
                        os.path.join(artwork_destination_path, subfolder),
                        ignore_errors=True)

                break


    async def _process_category_changes(self, data):  #pylint: disable=R0912
        changes = data.get('categories', [])
        if not changes:
            return

        new_categories = {}
        old_category_names = []
        try:
            for change in changes:
                if len(change) != 2:
                    raise FormatError('Incorrect change format: {}'
                                      .format(change))

                if change[0] == 'add':
                    if CHANNEL_LIMIT - len(list(self.get_all_channels())) <= 0:
                        raise DiscordError(
                            'No free slots to create a new category "{}"'
                            .format(change[1]))

                    position = max([c['position'] for c
                                    in self.categories.values()] or [0])
                    category = await self.guilds[0].create_category(
                        change[1], position=position)
                    new_categories[change[1]] = {
                        'name': category.name,
                        'id': category.id,
                        'position': category.position}
                    logging.info('Created new category "%s"', change[1])

                    await self._check_free_slots()
                    await asyncio.sleep(CMD_SLEEP_TIME)
                elif change[0] == 'rename':
                    if len(change[1]) != 2:
                        raise FormatError('Incorrect change format: {}'.format(
                            change))

                    if change[1][0] not in self.categories:
                        raise DiscordError('Category "{}" not found'.format(
                            change[1][0]))

                    category = self.get_channel(
                        self.categories[change[1][0]]['id'])
                    await category.edit(name=change[1][1])
                    new_categories[change[1][1]] = {
                        'name': category.name,
                        'id': category.id,
                        'position': category.position}
                    old_category_names.append(change[1][0])
                    logging.info('Renamed category "%s" to "%s"', change[1][0],
                                 change[1][1])
                    await asyncio.sleep(CMD_SLEEP_TIME)
                else:
                    raise FormatError('Unknown category change type: {}'
                                      .format(change[0]))
        finally:
            for name in old_category_names:
                del self.categories[name]

            self.categories.update(new_categories)


    async def _process_channel_changes(self, data):  #pylint: disable=R0912,R0915
        changes = data.get('channels', [])
        if not changes:
            return

        new_channels = {}
        old_channel_names = []
        try:
            for change in changes:
                if len(change) != 2:
                    raise FormatError('Incorrect change format: {}'
                                      .format(change))

                if change[0] == 'add':
                    if len(change[1]) != 2:
                        raise FormatError('Incorrect change format: {}'.format(
                            change))

                    if change[1][1] not in self.categories:
                        raise DiscordError('Category "{}" not found'.format(
                            change[1][1]))

                    if CHANNEL_LIMIT - len(list(self.get_all_channels())) <= 0:
                        raise DiscordError(
                            'No free slots to create a new channel "{}"'
                            .format(change[1][0]))

                    category = self.get_channel(
                        self.categories[change[1][1]]['id'])
                    channel = await self.guilds[0].create_text_channel(
                        change[1][0], category=category)
                    new_channels[change[1][0]] = {
                        'name': channel.name,
                        'id': channel.id,
                        'category_id': channel.category_id,
                        'category_name': channel.category.name}
                    logging.info('Created new channel "%s" in category "%s"',
                                 change[1][0], change[1][1])
                    await self._check_free_slots()
                    await asyncio.sleep(CMD_SLEEP_TIME)
                elif change[0] == 'move':
                    if len(change[1]) != 2:
                        raise FormatError('Incorrect change format: {}'.format(
                            change))

                    if change[1][0] not in self.channels:
                        raise DiscordError('Channel "{}" not found'.format(
                            change[1][0]))

                    if change[1][1] not in self.categories:
                        raise DiscordError('Category "{}" not found'.format(
                            change[1][1]))

                    channel = self.get_channel(
                        self.channels[change[1][0]]['id'])
                    old_category_name = channel.category.name
                    category = self.get_channel(
                        self.categories[change[1][1]]['id'])
                    await channel.move(category=category, end=True)
                    new_channels[change[1][0]] = {
                        'name': channel.name,
                        'id': channel.id,
                        'category_id': channel.category_id,
                        'category_name': channel.category.name}
                    logging.info('Moved channel "%s" from category "%s" to '
                                 '"%s"', change[1][0], old_category_name,
                                 change[1][1])
                    await channel.send('Moved from category "{}" to "{}"'
                                       .format(old_category_name,
                                               change[1][1]))
                    await asyncio.sleep(CMD_SLEEP_TIME)
                elif change[0] == 'remove':
                    if change[1] not in self.channels:
                        raise DiscordError('Channel "{}" not found'.format(
                            change[1]))

                    if not self.archive_category:
                        raise DiscordError('Category "{}" not found'.format(
                            ARCHIVE_CATEGORY))

                    channel = self.get_channel(self.channels[change[1]]['id'])
                    old_category_name = channel.category.name
                    await channel.move(category=self.archive_category,
                                       end=True)
                    old_channel_names.append(change[1])
                    logging.info('The card has been removed from the '
                                 'spreadsheet. Moved channel "%s" from '
                                 'category "%s" to "%s"', change[1],
                                 old_category_name, ARCHIVE_CATEGORY)
                    await channel.send('The card has been removed from the '
                                       'spreadsheet. Moved from category "{}" '
                                       'to "{}"'.format(old_category_name,
                                                        ARCHIVE_CATEGORY))
                    await asyncio.sleep(CMD_SLEEP_TIME)
                elif change[0] == 'rename':
                    if len(change[1]) != 2:
                        raise FormatError('Incorrect change format: {}'.format(
                            change))

                    if change[1][0] not in self.channels:
                        raise DiscordError('Channel {} not found'.format(
                            change[1][0]))

                    channel = self.get_channel(
                        self.channels[change[1][0]]['id'])
                    await channel.edit(name=change[1][1])
                    new_channels[change[1][1]] = {
                        'name': channel.name,
                        'id': channel.id,
                        'category_id': channel.category_id,
                        'category_name': channel.category.name}
                    old_channel_names.append(change[1][0])
                    logging.info('Renamed channel "%s" to "%s"', change[1][0],
                                 change[1][1])
                    await channel.send('Renamed from "{}" to "{}"'.format(
                        change[1][0], change[1][1]))
                    await asyncio.sleep(CMD_SLEEP_TIME)
                else:
                    raise FormatError('Unknown channel change type: {}'.format(
                        change[0]))
        finally:
            for name in old_channel_names:
                del self.channels[name]

            self.channels.update(new_channels)


    async def _process_card_changes(self, data):  #pylint: disable=R0912,R0914,R0915
        changes = data.get('cards', [])
        if not changes:
            return

        data = await read_card_data()
        for change in changes:
            if len(change) != 3:
                raise FormatError('Incorrect change format: {}'.format(change))

            if change[0] == 'add':
                card = change[2]
                if (card.get(lotr.CARD_DISCORD_CHANNEL) and
                        card[lotr.CARD_DISCORD_CHANNEL] not in self.channels):
                    raise DiscordError('Channel "{}" not found'.format(
                        card[lotr.CARD_DISCORD_CHANNEL]))

                if self.updates_channel:
                    if card.get(lotr.CARD_DISCORD_CHANNEL):
                        channel = self.channels[
                            card[lotr.CARD_DISCORD_CHANNEL]]
                        channel_url = ('https://discord.com/channels/{}/{}'
                                       .format(self.guilds[0].id,
                                               channel['id']))
                    else:
                        channel_url = ''

                    res = 'Card "{}" (set "{}") has been added. {}'.format(
                        card[lotr.CARD_NAME], card[lotr.CARD_SET_NAME],
                        channel_url)
                    await self._send_channel(self.updates_channel, res)

                if card.get(lotr.CARD_DISCORD_CHANNEL):
                    channel = self.get_channel(
                        self.channels[card[lotr.CARD_DISCORD_CHANNEL]]['id'])
                    res = await self._get_card(card[lotr.CARD_DISCORD_CHANNEL],
                                               True)
                    await self._send_channel(channel, res)
                else:
                    if card[lotr.CARD_DISCORD_CATEGORY] not in self.categories:
                        raise DiscordError('Category "{}" not found'.format(
                            card[lotr.CARD_DISCORD_CATEGORY]))

                    if (card[lotr.CARD_DISCORD_CATEGORY]
                            not in self.general_channels):
                        await self._add_general_channel(
                            card[lotr.CARD_DISCORD_CATEGORY])

                    channel = self.get_channel(self.general_channels[
                        card[lotr.CARD_DISCORD_CATEGORY]]['id'])
                    res = ('Card "{}" has been added.'.format(
                        card[lotr.CARD_NAME]))
                    await self._send_channel(channel, res)
                    res = await self._get_card(change[1], False)
                    await self._send_channel(channel, res)
            elif change[0] == 'remove':
                card = change[2]
                if self.updates_channel:
                    res = ('Card "{}" (set "{}") has been removed from the '
                           'spreadsheet.'.format(card[lotr.CARD_NAME],
                                                 card[lotr.CARD_SET_NAME]))
                    await self._send_channel(self.updates_channel, res)

                if (not card.get(lotr.CARD_DISCORD_CHANNEL) and
                        card[lotr.CARD_DISCORD_CATEGORY] in self.categories and
                        card[lotr.CARD_DISCORD_CATEGORY]
                        in self.general_channels):
                    channel = self.get_channel(self.general_channels[
                        card[lotr.CARD_DISCORD_CATEGORY]]['id'])
                    res = ('Card "{}" has been removed from the spreadsheet.'
                           .format(card[lotr.CARD_NAME]))
                    await self._send_channel(channel, res)
            elif change[0] == 'change':
                for diff in change[2]:
                    if len(diff) != 3:
                        raise FormatError('Incorrect change format: {}'.format(
                            change))

                if change[1] in data['dict']:
                    card = data['dict'][change[1]]
                else:
                    raise DiscordError('Card with ID "{}" not found'
                                       .format(change[1]))

                for diff in change[2]:
                    diff[0] = diff[0].replace(lotr.BACK_PREFIX + lotr.CARD_NAME,
                                              lotr.CARD_SIDE_B).replace(
                                                  lotr.BACK_PREFIX, '[Back] ')
                    if not str(diff[1] or '').strip():
                        diff[1] = '```\n ```'
                        new_lines = str(diff[2] or '').strip().split('\n')
                        diff[2] = '```diff\n{}```'.format(
                            '\n'.join('+ {}'.format(r)
                                      for r in new_lines).strip())
                        continue

                    if not str(diff[2] or '').strip():
                        old_lines = str(diff[1] or '').strip().split('\n')
                        diff[1] = '```diff\n{}```'.format(
                            '\n'.join('- {}'.format(r)
                                      for r in old_lines).strip())
                        diff[2] = '```\n ```'
                        continue

                    old_lines = str(diff[1] or '').strip().split('\n')
                    new_lines = str(diff[2] or '').strip().split('\n')
                    max_length = max(len(old_lines), len(new_lines))
                    for i in range(max_length):
                        if i >= len(old_lines):
                            new_lines[i] = '+ {}'.format(
                                new_lines[i])
                        elif i >= len(new_lines):
                            old_lines[i] = '- {}'.format(
                                old_lines[i])
                        elif old_lines[i] != new_lines[i]:
                            old_lines[i] = '- {}'.format(
                                old_lines[i])
                            new_lines[i] = '+ {}'.format(
                                new_lines[i])

                    diff[1] = '```diff\n{}```'.format(
                        '\n'.join(old_lines).strip())
                    diff[2] = '```diff\n{}```'.format(
                        '\n'.join(new_lines).strip())

                diffs = [
                    '**{}**\n\xa0\xa0\xa0\xa0\xa0OLD\n{}\xa0\xa0\xa0\xa0\xa0NEW\n{}'
                    .format(d[0], d[1] or '', d[2] or '')
                    for d in change[2]]

                if self.updates_channel:
                    if card.get(lotr.CARD_DISCORD_CHANNEL) in self.channels:
                        channel = self.channels[
                            card[lotr.CARD_DISCORD_CHANNEL]]
                        channel_url = ('https://discord.com/channels/{}/{}'
                                       .format(self.guilds[0].id,
                                               channel['id']))
                    else:
                        channel_url = ''

                    res = """
Card "{}" (set "{}") has been updated:

{}
{}
""".format(card[lotr.CARD_NAME], card[lotr.CARD_SET_NAME], '\n'.join(diffs),
           channel_url)
                    await self._send_channel(self.updates_channel, res)

                if card.get(lotr.CARD_DISCORD_CHANNEL):
                    channel_name = card[lotr.CARD_DISCORD_CHANNEL]
                    if channel_name not in self.channels:
                        raise DiscordError('Channel "{}" not found'.format(
                            channel_name))

                    res = """
The card has been updated:

{}
""".format('\n'.join(diffs))
                    channel = self.get_channel(
                        self.channels[channel_name]['id'])
                    await self._send_channel(channel, res)
                else:
                    if card[lotr.CARD_DISCORD_CATEGORY] not in self.categories:
                        raise DiscordError('Category "{}" not found'.format(
                            card[lotr.CARD_DISCORD_CATEGORY]))

                    if (card[lotr.CARD_DISCORD_CATEGORY]
                            not in self.general_channels):
                        await self._add_general_channel(
                            card[lotr.CARD_DISCORD_CATEGORY])

                    channel = self.get_channel(self.general_channels[
                        card[lotr.CARD_DISCORD_CATEGORY]]['id'])
                    res = """
Card "{}" has been updated:

{}
""".format(card[lotr.CARD_NAME], '\n'.join(diffs))
                    await self._send_channel(channel, res)
            else:
                raise FormatError('Unknown card change type: {}'.format(
                    change[0]))


    async def _add_general_channel(self, category_name):
        if CHANNEL_LIMIT - len(list(self.get_all_channels())) <= 0:
            raise DiscordError(
                'No free slots to create a new channel "general" in category '
                '"{}"'.format(category_name))

        category = self.get_channel(self.categories[category_name]['id'])
        channel = await self.guilds[0].create_text_channel(
            'general', category=category, position=0)
        await channel.move(category=category, beginning=True)
        self.general_channels[category_name] = {
            'name': channel.category.name,
            'id': channel.id,
            'category_id': channel.category_id}
        logging.info('Created new channel "general" in category "%s"',
                     category_name)
        await self._check_free_slots()
        await asyncio.sleep(CMD_SLEEP_TIME)


    async def _check_free_slots(self):
        slots = CHANNEL_LIMIT - len(list(self.get_all_channels()))
        if slots < 5:
            logging.warning('Only %s channel slots remain', slots)
            message = 'only {} channel slots remain'.format(slots)
            create_mail(WARNING_SUBJECT_TEMPLATE.format(message))
            if self.cron_channel:
                await self._send_channel(self.cron_channel,
                                         message)


    async def _test_channels(self):
        channels = self.channels.copy()
        data = await read_card_data()
        orphan_cards = []
        for card in data['data']:
            if not card.get(lotr.CARD_DISCORD_CHANNEL):
                continue

            name = card[lotr.CARD_DISCORD_CHANNEL]
            if name in channels:
                if (card[lotr.CARD_DISCORD_CATEGORY] !=
                        channels[name]['category_name']):
                    logging.warning(
                        'Card %s (%s) has a wrong channel category: %s '
                        'instead of %s', card[lotr.CARD_NAME],
                        card[lotr.CARD_DISCORD_CHANNEL],
                        channels[name]['category_name'],
                        card[lotr.CARD_DISCORD_CATEGORY])

                del channels[name]
            else:
                orphan_cards.append(card)

        if orphan_cards:
            logging.warning('Orphan cards detected:')
            for card in orphan_cards:
                logging.warning('%s (%s): %s, %s', card[lotr.CARD_NAME],
                                card[lotr.CARD_DISCORD_CHANNEL],
                                card[lotr.CARD_TYPE],
                                card[lotr.CARD_SET_NAME])

        if channels:
            logging.info('Non-card channels detected:')
            for channel in channels:
                logging.info('%s (%s)', channel,
                             channels[channel]['category_name'])


    async def _send_channel(self, channel, content):
        for i, chunk in enumerate(split_result(content)):
            if i > 0:
                await asyncio.sleep(MESSAGE_SLEEP_TIME)

            await channel.send(chunk)


    async def _process_cron_command(self, message):  #pylint: disable=R0912
        """ Process a cron command.
        """
        if message.content.lower() == '!cron':
            command = 'help'
        else:
            command = re.sub(r'^!cron ', '', message.content,
                             flags=re.IGNORECASE).split('\n')[0]

        logging.info('Received cron command: %s', command)
        if command.lower().startswith('hello'):
            await message.channel.send('hello')
        elif command.lower().startswith('test'):
            await message.channel.send('passed')
        elif (command.lower().startswith('thank you') or
              command.lower().startswith('thanks')):
            await message.channel.send('you are welcome')
        elif command.lower() == 'log':
            res, _ = await run_shell(CRON_LOG_CMD)
            if not res:
                res = 'no cron logs found'

            await self._send_channel(message.channel, res)
        elif command.lower() == 'errors':
            res = await get_errors()
            if not res:
                res = 'no cron logs found'

            await self._send_channel(message.channel, res)
        elif command.lower() == 'trigger':
            delete_sheet_checksums()
            await message.channel.send('done')
        else:
            res = HELP['cron']
            await self._send_channel(message.channel, res)


    async def _new_target(self, content):
        """ Set new playtesting targets.
        """
        error_message = """incorrect command format: {}
try something like:
```
!playtest new
Deadline: tomorrow.
1. Escape From Dol Guldur (solo)
2. Frogs deck
```
"""
        lines = [line.strip() for line in content.split('\n')[1:]]
        nums = set()
        description = []
        targets = []
        for line in lines:
            if not re.match(r'^[0-9]+\.? ', line):
                if nums:
                    return error_message.format('no number for a target')

                description.append(line)
                continue

            if '~~' in line:
                return error_message.format('a target is already crossed out')

            num, title = line.split(' ', 1)
            num = re.sub(r'\.$', '', num)
            if num in nums:
                return error_message.format(
                    'a duplicate target number "{}"'.format(num))

            nums.add(num)
            targets.append({'num': num,
                            'title': title,
                            'completed': False,
                            'user': None})

        if not targets:
            return error_message.format('no targets specified')

        data = {'targets': targets,
                'description': '\n'.join(description)}

        async with playtest_lock:
            with open(PLAYTEST_PATH, 'w') as obj:
                json.dump(data, obj)

        playtest_message = """----------
New playtesting targets:
{}""".format(format_playtest_message(data))
        if self.playtest_channel:
            await self._send_channel(self.playtest_channel, playtest_message)

        return ''


    async def _view_target(self):
        """ Display existing playtesting target.
        """
        async with playtest_lock:
            with open(PLAYTEST_PATH, 'r') as obj:
                data = json.load(obj)

        return format_playtest_message(data)


    async def _complete_target(self, content, num, user, url):
        """ Complete playtesting target.
        """
        if not re.match(r'^[0-9]+$', num):
            return 'target number "{}" doesn\'t look correct'.format(num)

        if len(content.split('\n', 1)) == 1:
            return 'please add a playtesting report'

        async with playtest_lock:
            with open(PLAYTEST_PATH, 'r+') as obj:
                data = json.load(obj)

                nums = [target['num'] for target in data['targets']]
                if num not in nums:
                    return 'target "{}" not found'.format(num)

                nums = [target['num'] for target in data['targets']
                        if not target['completed']]
                if num not in nums:
                    return 'target "{}" already completed'.format(num)

                for target in data['targets']:
                    if target['num'] == num:
                        target['completed'] = True
                        target['user'] = user
                        break

                obj.seek(0)
                obj.truncate()
                json.dump(data, obj)

        all_targets = ('All targets completed now!'
                       if all(target['completed']
                              for target in data['targets'])
                       else '')
        playtest_message = """----------
Target "{}" completed. Link: {}
{}
{}""".format(num, url, format_playtest_message(data), all_targets)
        if self.playtest_channel:
            await self._send_channel(self.playtest_channel, playtest_message)

        return ''


    async def _update_target(self, params):  # pylint: disable=R0912
        """ Update playtesting target.
        """
        nums = set()
        while params:
            param = params[0]
            if not param:
                params.pop(0)
            elif re.match(r'^[0-9]+$', param):
                if param in nums:
                    return 'a duplicate target number "{}"'.format(param)

                params.pop(0)
                nums.add(param)
            else:
                break

        if not nums:
            return 'no target number(s) specified'

        user = ' '.join(params)
        async with playtest_lock:
            with open(PLAYTEST_PATH, 'r+') as obj:
                data = json.load(obj)

                existing_nums = set(target['num']
                                    for target in data['targets'])
                for num in nums:
                    if num not in existing_nums:
                        return 'target "{}" not found'.format(num)

                for target in data['targets']:
                    if target['num'] in nums:
                        if user:
                            target['completed'] = True
                            target['user'] = user
                        else:
                            target['completed'] = False
                            target['user'] = None

                obj.seek(0)
                obj.truncate()
                json.dump(data, obj)

        all_targets = ('All targets completed now!'
                       if all(target['completed']
                              for target in data['targets'])
                       else '')
        playtest_message = """----------
Targets updated.
{}
{}""".format(format_playtest_message(data), all_targets)
        if self.playtest_channel:
            await self._send_channel(self.playtest_channel, playtest_message)

        return ''


    async def _add_target(self, content):
        """ Add additional playtesting targets.
        """
        lines = [line.strip() for line in content.split('\n')[1:]]
        nums = set()
        description = []
        targets = []
        for line in lines:
            if not re.match(r'^[0-9]+\.? ', line):
                if nums:
                    return 'no number for a target'

                description.append(line)
                continue

            if '~~' in line:
                return 'a target is already crossed out'

            num, title = line.split(' ', 1)
            num = re.sub(r'\.$', '', num)
            if num in nums:
                return 'a duplicate target number "{}"'.format(num)

            nums.add(num)
            targets.append({'num': num,
                            'title': title,
                            'completed': False,
                            'user': None})

        if not description and not targets:
            return 'no new desription or targets specified'

        async with playtest_lock:
            with open(PLAYTEST_PATH, 'r+') as obj:
                data = json.load(obj)

                existing_nums = set(target['num']
                                    for target in data['targets'])
                for num in nums:
                    if num in existing_nums:
                        return 'a duplicate target number "{}"'.format(num)

                if description:
                    data['description'] = '\n'.join(description)

                data['targets'].extend(targets)
                obj.seek(0)
                obj.truncate()
                json.dump(data, obj)

        playtest_message = """----------
Targets added.
{}""".format(format_playtest_message(data))
        if self.playtest_channel:
            await self._send_channel(self.playtest_channel, playtest_message)

        return ''


    async def _remove_target(self, params):
        """ Remove existing playtesting targets.
        """
        nums = set()
        while params:
            param = params[0]
            if not param:
                params.pop(0)
            elif re.match(r'^[0-9]+$', param):
                if param in nums:
                    return 'a duplicate target number "{}"'.format(param)

                params.pop(0)
                nums.add(param)
            else:
                return 'target number "{}" doesn\'t look correct'.format(param)

        if not nums:
            return 'no target number(s) specified'

        async with playtest_lock:
            with open(PLAYTEST_PATH, 'r+') as obj:
                data = json.load(obj)

                existing_nums = set(target['num']
                                    for target in data['targets'])
                for num in nums:
                    if num not in existing_nums:
                        return 'target "{}" not found'.format(num)

                data['targets'] = [target for target in data['targets']
                                   if target['num'] not in nums]
                obj.seek(0)
                obj.truncate()
                json.dump(data, obj)

        playtest_message = """----------
Targets removed.
{}""".format(format_playtest_message(data))
        if self.playtest_channel:
            await self._send_channel(self.playtest_channel, playtest_message)

        return ''


    async def _process_playtest_command(self, message):  # pylint: disable=R0911,R0912,R0915
        """ Process a playtest command.
        """
        if message.content.lower() == '!playtest':
            command = 'help'
        else:
            command = re.sub(r'^!playtest ', '', message.content,
                             flags=re.IGNORECASE).split('\n')[0]

        logging.info('Received playtest command: %s', command)
        if command.lower() == 'new':
            try:
                error = await self._new_target(message.content)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await message.channel.send(error)
                return

            await message.channel.send('done')
        elif command.lower() == 'view':
            try:
                res = await self._view_target()
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            await message.channel.send(res)
        elif command.lower().startswith('complete '):
            try:
                num = re.sub(r'^complete ', '', command, flags=re.IGNORECASE)
                user = message.author.display_name
                error = await self._complete_target(message.content, num, user,
                                                    message.jump_url)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await message.channel.send(error)
                return

            await message.channel.send('done')
        elif command.lower().startswith('update '):
            try:
                params = re.sub(r'^update ', '', command, flags=re.IGNORECASE
                               ).split(' ')
                error = await self._update_target(params)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await message.channel.send(error)
                return

            await message.channel.send('done')
        elif command.lower() == 'add':
            try:
                error = await self._add_target(message.content)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await message.channel.send(error)
                return

            await message.channel.send('done')
        elif command.lower().startswith('remove '):
            try:
                params = re.sub(r'^remove ', '', command, flags=re.IGNORECASE
                               ).split(' ')
                error = await self._remove_target(params)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await message.channel.send(error)
                return

            await message.channel.send('done')
        elif command.lower().startswith('random '):
            num = re.sub(r'^random ', '', command, flags=re.IGNORECASE)
            if lotr.is_positive_int(num):
                res = random.randint(1, int(num))
                await message.channel.send(str(res))
            else:
                await message.channel.send(
                    '"{}" is not a positive integer'.format(num))
        else:
            res = HELP['playtest']
            await self._send_channel(message.channel, res)


    async def _get_quests_stat(self, quest):  # pylint: disable=R0914
        """ Get statistics for all found quests.
        """
        data = await read_card_data()
        quest = lotr.escape_octgn_filename(lotr.escape_filename(quest)).lower()
        set_folders = {lotr.escape_filename(s) for s in data['sets']}
        quests = {}
        for _, subfolders, _ in os.walk(lotr.OUTPUT_OCTGN_DECKS_PATH):  # pylint: disable=R1702
            for subfolder in subfolders:
                if subfolder not in set_folders:
                    continue

                path = os.path.join(lotr.OUTPUT_OCTGN_DECKS_PATH, subfolder)
                for _, _, filenames in os.walk(path):
                    for filename in filenames:
                        if (filename.endswith('.o8d') and
                                not filename.startswith('Player-') and
                                ('-{}-'.format(quest) in filename.lower() or
                                 '-{}.'.format(quest) in filename.lower())):
                            quest_name = re.sub(r'\.o8d$', '', filename)
                            cards = await read_deck_xml(
                                os.path.join(path, filename))
                            if cards:
                                quests[quest_name] = get_quest_stat(cards)

                    break

            break

        res = ''
        for quest_name, stat in sorted(quests.items()):
            res += f"""**{quest_name}**
{stat['total']}{stat['encounter_sets']}{stat['keywords']}
{stat['card_types']}

{stat['encounter_deck']}"""

        if not res:
            res = 'no quests found'

        return res


    async def _get_card(self, command, this=False):  # pylint: disable=R0912,R0914
        """ Get the card information.
        """
        data = await read_card_data()

        if this:
            matches = [(card, 1) for card in data['data']
                       if card.get(lotr.CARD_DISCORD_CHANNEL, '') == command]
            num = 1
        elif re.match(r'^[0-9]+$', command):
            matches = [(card, 1) for card in data['data']
                       if card[lotr.ROW_COLUMN] == int(command)]
            num = 1
        elif re.match(
                r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
                command):
            if command in data['dict']:
                matches = [(data['dict'][command], 1)]
            else:
                matches = []

            num = 1
        else:
            if re.search(r' n:[0-9]+$', command):
                parts = command.split(' ')
                command = ' '.join(parts[:-1])
                num = int(parts[-1].replace('n:', ''))
            else:
                num = 1

            if re.search(r' s:[a-zA-Z][a-zA-Z0-9]+$', command):
                parts = command.split(' ')
                name = ' '.join(parts[:-1])
                set_code = parts[-1].replace('s:', '').lower()
            else:
                name = command
                set_code = None

            name = lotr.normalized_name(name)
            matches = [m for m in [
                (card, card_match(
                    card[lotr.CARD_NORMALIZED_NAME],
                    card.get(lotr.BACK_PREFIX + lotr.CARD_NORMALIZED_NAME, ''),
                    name))
                for card in data['data']] if m[1] > 0]

            if set_code:
                matches = [m for m in matches
                           if m[0][lotr.CARD_SET_HOB_CODE].lower() == set_code]

        if not matches:
            return 'no cards found'

        matches.sort(key=lambda m: (
            m[1],
            m[0][lotr.CARD_TYPE] in ('Rules', 'Presentation'),
            m[0][lotr.CARD_SET_RINGSDB_CODE],
            lotr.is_positive_or_zero_int(m[0][lotr.CARD_NUMBER])
            and int(m[0][lotr.CARD_NUMBER]) or 0,
            m[0][lotr.CARD_NUMBER]))

        ending = '\n...' if len(matches) > 25 else ''
        matches = matches[:25]
        if num > len(matches):
            list_matches = format_matches(matches, num)
            cards_text = 'cards' if len(matches) > 1 else 'card'
            return 'we found only {} {}:\n{}'.format(len(matches),
                                                     cards_text,
                                                     list_matches)

        card = matches[num - 1][0]
        if card.get(lotr.CARD_DISCORD_CHANNEL) in self.channels:
            channel = self.channels[card[lotr.CARD_DISCORD_CHANNEL]]
            channel_url = ('https://discord.com/channels/{}/{}'
                           .format(self.guilds[0].id, channel['id']))
        else:
            channel_url = ''

        res = format_card(card, data['url'], channel_url)
        if len(matches) > 1:
            list_matches = format_matches(matches, num)
            res += '\n` `\n**all matches:**\n{}{}'.format(list_matches, ending)

        return res


    async def _process_card_command(self, message):
        """ Process a card command.
        """
        if message.content.lower() == '!alepcard':
            command = 'help'
        else:
            command = re.sub(r'^!alepcard ', '', message.content,
                             flags=re.IGNORECASE).split('\n')[0]

        logging.info('Received card command: %s', command)

        if command.lower().startswith('help'):
            res = HELP['alepcard']
            await self._send_channel(message.channel, res)
            return

        if command.lower() == 'this':
            command = message.channel.name
            this = True
        else:
            this = False

        try:
            res = await self._get_card(command, this)
        except Exception as exc:
            logging.exception(str(exc))
            await message.channel.send(
                'unexpected error: {}'.format(str(exc)))
            return

        await self._send_channel(message.channel, res)


    async def _process_stat_command(self, message):
        """ Process a stat command.
        """
        if message.content.lower() == '!stat':
            command = 'help'
        else:
            command = re.sub(r'^!stat ', '', message.content,
                             flags=re.IGNORECASE).split('\n')[0]

        logging.info('Received stat command: %s', command)

        if command.lower().startswith('quest '):
            try:
                quest = re.sub(r'^quest ', '', command,
                               flags=re.IGNORECASE)
                res = await self._get_quests_stat(quest)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'quest':
            await message.channel.send('please specify the quest name')
        elif command.lower() == 'channels':
            try:
                num = len(list(self.get_all_channels()))
                res = 'There are {} channels and {} free slots'.format(
                    num, CHANNEL_LIMIT - num)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        else:
            res = HELP['stat']
            await self._send_channel(message.channel, res)


    async def _save_artwork(self, message, side, artist):  # pylint: disable=R0911,R0914
        """ Save an artwork image.
        """
        data = await read_card_data()

        channel_name = message.channel.name
        matches = [card for card in data['data']
                   if card.get(lotr.CARD_DISCORD_CHANNEL, '') == channel_name]
        if not matches:
            return 'no card found for this channel'

        card = matches[0]
        if card.get(lotr.CARD_SET_LOCKED):
            return 'set {} is locked for modifications'.format(
                card[lotr.CARD_SET_NAME])

        if side == 'B' and not card.get(lotr.BACK_PREFIX + lotr.CARD_NAME):
            return 'no side B found for the card'

        if (not message.reference or not message.reference.resolved
                or not message.reference.resolved.attachments):
            return 'please reply to a message with an image attachment'

        attachment = message.reference.resolved.attachments[0]
        if (attachment.content_type not in ('image/png', 'image/jpeg') and
                not attachment.filename.lower().split('.')[-1] in
                ('png', 'jpg', 'jpeg')):
            return 'attachment must be either JPG ot PNG image'

        if (attachment.content_type == 'image/png' or
                attachment.filename.lower().split('.')[-1] == 'png'):
            filetype = 'png'
        else:
            filetype = 'jpg'

        artwork_destination_path = CONF.get('artwork_destination_path')
        if not artwork_destination_path:
            return 'no destination folder specified on the server'

        content = await attachment.read()

        folder = os.path.join(artwork_destination_path, card[lotr.CARD_SET])
        filename = '{}_{}_{}_{}.{}'.format(card[lotr.CARD_ID], side,
                                           card[lotr.CARD_NAME], artist,
                                           filetype)
        filename = lotr.escape_filename(filename).replace(' ', '_')
        path = os.path.join(folder, filename)

        async with art_lock:
            if not os.path.exists(folder):
                os.mkdir(folder)

            for _, _, filenames in os.walk(folder):
                for filename in filenames:
                    if filename.startswith(
                            '{}_{}'.format(card[lotr.CARD_ID], side)):
                        os.remove(os.path.join(folder, filename))

                break

            with open(path, 'wb') as f_obj:
                f_obj.write(content)

            self.rclone_art = True

        return ''


    async def _process_art_command(self, message):
        """ Process an art command.
        """
        if message.content.lower() == '!art':
            command = 'help'
        else:
            command = re.sub(r'^!art ', '', message.content,
                             flags=re.IGNORECASE).split('\n')[0]

        logging.info('Received art command: %s', command)

        if (command.lower().startswith('save ') or
                command.lower().startswith('saveb ')):
            try:
                side = 'B' if command.lower().startswith('saveb ') else 'A'
                artist = re.sub(r'^saveb? ', '', command, flags=re.IGNORECASE)
                error = await self._save_artwork(message, side, artist)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await message.channel.send(error)
                return

            await message.channel.send('done')
        elif command.lower() == 'save':
            await message.channel.send('please specify the artist')
        else:
            res = HELP['art']
            await self._send_channel(message.channel, res)


    async def _process_help_command(self, message):
        """ Process a help command.
        """
        logging.info('Received help command')

        res = ''.join(HELP[key] for key in sorted(HELP.keys()))
        await self._send_channel(message.channel, res)


    async def on_message(self, message):
        """ Invoked when a new message posted.
        """
        try:
            if not message.content or message.content[0] != '!':
                return

            if (message.content.lower().startswith('!alepcard ') or
                    message.content.lower() == '!alepcard'):
                await self._process_card_command(message)
            elif (message.content.lower().startswith('!playtest ') or
                  message.content.lower() == '!playtest'):
                await self._process_playtest_command(message)
            elif (message.content.lower().startswith('!cron ') or
                  message.content.lower() == '!cron'):
                await self._process_cron_command(message)
            elif (message.content.lower().startswith('!art ') or
                  message.content.lower() == '!art'):
                await self._process_art_command(message)
            elif (message.content.lower().startswith('!stat ') or
                  message.content.lower() == '!stat'):
                await self._process_stat_command(message)
            elif message.content.lower().startswith('!help'):
                await self._process_help_command(message)
        except Exception as exc:
            logging.exception(str(exc))
            create_mail(ERROR_SUBJECT_TEMPLATE.format(
                'unexpected error during processing a message: {}'
                .format(str(exc))))


if __name__ == '__main__':
    os.chdir(WORKING_DIRECTORY)
    init_logging()
    CONF.update(get_discord_configuration())
    MyClient().run(CONF.get('token'))
