# pylint: disable=C0103,C0209,C0302,W0703
# -*- coding: utf8 -*-
""" Discord bot.
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

import aiohttp
import discord
import yaml

import lotr


CHANGES_PATH = os.path.join('Discord', 'Changes')
CONF_PATH = 'discord.yaml'
IMAGES_PATH = os.path.join('Discord', 'Images')
LOG_PATH = 'discord_bot.log'
MAIL_COUNTER_PATH = 'discord_bot.cnt'
MAILS_PATH = 'mails'
PLAYTEST_PATH = os.path.join('Discord', 'playtest.json')

CRON_ERRORS_CMD = './cron_errors.sh'
CRON_LOG_CMD = './cron_log.sh'
RCLONE_ART_CMD = "rclone copy '{}' 'ALePCardImages:/'"
RCLONE_ART_FOLDER_CMD = "rclone lsjson 'ALePCardImages:/{}/'"
RCLONE_COPY_IMAGE_CMD = "rclone copy 'ALePRenderedImages:/{}/{}' '{}/'"
RCLONE_COPY_CLOUD_IMAGE_CMD = \
    "rclone copy 'ALePRenderedImages:/{}/{}' 'ALePRenderedImages:/{}/'"
RCLONE_LOGS_CMD = "rclone copy 'ALePLogs:/' '{}/'"
RCLONE_IMAGE_FOLDER_CMD = "rclone lsjson 'ALePRenderedImages:/{}/'"
RCLONE_MOVE_CLOUD_ART_CMD = \
    "rclone move 'ALePCardImages:/{}/{}' 'ALePCardImages:/{}/'"
RCLONE_RENDERED_FOLDER_CMD = "rclone lsjson 'ALePRenderedImages:/{}/'"
RCLONE_RENDERER_CMD = './rclone_renderer.sh'
REMOTE_CRON_TIMESTAMP_CMD = './remote_cron_timestamp.sh "{}"'
RESTART_BOT_CMD = './restart_discord_bot.sh'
RESTART_CRON_CMD = './restart_run_before_se_service.sh'

DIRECT_URL_REGEX = r'itemJson: \[[^,]+,"[^"]+","([^"]+)"'
PREVIEW_URL = 'https://drive.google.com/file/d/{}/preview'

CMD_SLEEP_TIME = 2
COMMUNICATION_SLEEP_TIME = 5
IO_SLEEP_TIME = 1
RCLONE_ART_SLEEP_TIME = 300
REMOTE_CRON_TIMESTAMP_SLEEP_TIME = 1800
WATCH_SLEEP_TIME = 5

ERROR_SUBJECT_TEMPLATE = 'LotR Discord Bot ERROR: {}'
WARNING_SUBJECT_TEMPLATE = 'LotR Discord Bot WARNING: {}'
MAIL_QUOTA = 50

CHANNEL_LIMIT = 500
CHUNK_LIMIT = 1900
MAX_PINS = 50
ARCHIVE_CATEGORY = 'Archive'
CARD_DECK_SECTION = '_Deck Section'
CRON_CHANNEL = 'cron'
NOTIFICATIONS_CHANNEL = 'notifications'
PLAYTEST_CHANNEL = 'playtesting-checklist'
SCRATCH_FOLDER = '_Scratch'
UPDATES_CHANNEL = 'spreadsheet-updates'
GENERAL_CATEGORIES = {
    'Text Channels', 'Division of Labor', 'Player Card Design', 'Printing',
    'Rules', 'Voice Channels', 'Archive'
}

RENDERED_IMAGES_TTL = 600

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

**!cron dragncards build** - trigger a DragnCards build
**!cron errors** - display all errors from the latest cron run
**!cron log** - display a full execution log of the latest cron run
**!cron restart bot** - restart the Discord bot
**!cron restart cron** - restart the cron process
**!cron trigger** - trigger reprocessing of all sheets in the next cron run
**!cron help** - display this help message
""",
    'playtest': """
List of **!playtest** commands:

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
**!playtest view** - display existing playtesting target
**!playtest remove <target or list of targets separated by space>** - remove a given target or a list of targets (for example: `!playtest remove 11 12`)
**!playtest update <target or list of targets separated by space> <player>** - mark a given target or a list of targets as completed by a given player (for example: `!playtest update 7 Shellin`)
**!playtest random <number>** - generate a random number from 1 to a given number (for example: `!playtest random 10`)
**!playtest help** - display this help message
""",
    'stat': """
List of **!stat** commands:

**!stat assistants** - display the list of assistants (all Discord users except for those who have a role)
**!stat channels** - display the number of Discord channels and free channel slots
**!stat dragncards build** - display information about the latest DragnCards build
**!stat quest <quest name or set name or set code>** - display the quest statistics (for example: `!stat quest The Battle for the Beacon` or `!stat quest Children of Eorl` or `!stat quest TAP`)
**!stat help** - display this help message
""",
    'art': """
List of **!art** commands:

**!art artists <set name or set code>** - display a copy-pasteable list of artist names (for example: `!art artists Children of Eorl` or `!art artists CoE`)
**!art save <artist>** (as a reply to a message with an image attachment) - save the image as a card's artwork for the front side (for example: `!art save Ted Nasmith`)
**!art saveb <artist>** (as a reply to a message with an image attachment) - save the image as a card's artwork for the back side (for example: `!art saveb John Howe`)
**!art savescr** (or **!art savescr <artist>**) (as a reply to a message with an image attachment) - save the image to the scratch folder
**!art verify <set name or set code>** - verify artwork for a set (for example: `!art verify Children of Eorl` or `!art verify CoE`)
**!art help** - display this help message
""",
    'image': """
List of **!image** commands:

**!image set <set name or set code>** - post the last rendered images for all cards from a set (for example: `!image set The Aldburg Plot` or `!image set TAP`)
**!image card <card name>** (or **!image <card name>**) - post the last rendered images for the first card matching a given card name (for example: `!image card Gavin`)
**!image card this** (or **!image this**) - if in a card channel, post the last rendered images for the card
**!image refresh** - clear the image cache (if you just uploaded new images to the Google Drive)
**!image help** - display this help message
"""
}

CARD_DATA = {}
CONF = {}
EXTERNAL_DATA = {}
EXTERNAL_FILES = set()
RENDERED_IMAGES = {}
TIMESTAMPS = {}


def _incremental_id():
    """ A closure to get a unique incremental ID.
    """
    data = [0]

    def _inside():
        data[0] += 1
        return data[0]

    return _inside


incremental_id = _incremental_id()
watch_changes_lock = asyncio.Lock()
rclone_art_lock = asyncio.Lock()
remote_cron_timestamp_lock = asyncio.Lock()
playtest_lock = asyncio.Lock()
art_lock = asyncio.Lock()


class CommunicationError(Exception):
    """ Communication error.
    """


class DiscordError(Exception):
    """ Discord error.
    """


class FormatError(Exception):
    """ Change format error.
    """


class RCloneFolderError(Exception):
    """ Artwork folder error.
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


def get_discord_configuration():
    """ Get Discord configuration.
    """
    try:
        with open(CONF_PATH, 'r', encoding='utf-8') as f_conf:
            conf = yaml.safe_load(f_conf)

        return conf
    except Exception as exc:
        message = 'Error obtaining Discord configuration: {}: {}'.format(
            type(exc).__name__, str(exc))
        logging.exception(message)
        create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)
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
    except Exception as exc:
        message = 'Error running shell command "{}": {}: {}'.format(
            cmd, type(exc).__name__, str(exc))
        logging.exception(message)
        return ('', message)

    stdout = stdout.decode('utf-8').strip()
    stderr = stderr.decode('utf-8').strip()
    return (stdout, stderr)


async def run_and_forget_shell(cmd):
    """ Run a shell command.
    """
    await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)


def split_result(value):
    """ Split result into chunks.
    """
    res = []
    chunk = ''
    for line in value.split('\n'):
        if len(chunk + line) + 1 <= CHUNK_LIMIT:
            chunk += line + '\n'
        else:
            res.append(chunk)
            chunk = line + '\n'

    res.append(chunk)

    for i in range(len(res) - 1):
        cnt = res[i].count('```')
        if cnt % 2 == 0:
            continue

        if res[i].split('```')[-1].startswith('diff'):
            res[i + 1] = '```diff\n' + res[i + 1]
        else:
            res[i + 1] = '```\n' + res[i + 1]

        res[i] += '```\n'

    res = [chunk.replace('```diff\n```', '').replace('```\n```', '')
           for chunk in res]
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
        with open(path, 'r', encoding='utf-8') as obj:
            data = json.load(obj)
    except Exception:
        await asyncio.sleep(IO_SLEEP_TIME)
        with open(path, 'r', encoding='utf-8') as obj:
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


async def load_timestamps_data():
    """ Load timestamps data generated by the cron job.
    """
    if TIMESTAMPS.get('loaded'):
        return

    if os.path.exists(lotr.DISCORD_TIMESTAMPS_PATH):
        data = await read_json_data(lotr.DISCORD_TIMESTAMPS_PATH)
    else:
        data = {}

    TIMESTAMPS['data'] = data
    TIMESTAMPS['loaded'] = True


def read_external_data():
    """ Read external card data.
    """
    new_files = set()
    for _, _, filenames in os.walk(lotr.URL_CACHE_PATH):
        for filename in filenames:
            if filename.endswith('.xml.cache'):
                new_files.add(filename)

        break

    new_files = new_files.difference(EXTERNAL_FILES)
    for new_file in new_files:
        EXTERNAL_FILES.add(new_file)
        data = lotr.load_external_xml(re.sub(r'\.xml\.cache$', '', new_file))
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


def find_card_matches(data, command, this=False):
    """ Find all card matches and return the match number.
    """
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

    matches.sort(key=lambda m: (
        m[1],
        m[0][lotr.CARD_TYPE] in ('Rules', 'Presentation'),
        m[0][lotr.CARD_SET_RINGSDB_CODE],
        lotr.is_positive_or_zero_int(m[0][lotr.CARD_NUMBER])
        and int(m[0][lotr.CARD_NUMBER]) or 0,
        m[0][lotr.CARD_NUMBER]))

    return matches, num


def update_emojis(text):
    """ Update emojis in the text.
    """
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
    return text

def update_text(text):  # pylint: disable=R0915
    """ Update card text.
    """
    text = re.sub(r'\b(Quest Resolution)( \([^\)]+\))?:', '[b]\\1[/b]\\2:',
                  text)
    text = re.sub(r'\b(Valour )?(Resource |Planning |Quest |Travel |Encounter '
                  r'|Combat |Refresh )?(Action):', '[b]\\1\\2\\3[/b]:', text)
    text = re.sub(r'\b(When Revealed|Forced|Valour Response|Response|Travel'
                  r'|Shadow|Resolution):', '[b]\\1[/b]:', text)
    text = re.sub(r'\b(Setup)( \([^\)]+\))?:', '[b]\\1[/b]\\2:', text)
    text = re.sub(r'\b(Condition)\b', '[bi]\\1[/bi]', text)

    def _fix_bi_in_b(match):
        return '[b]{}[/b]'.format(
            match.groups()[0].replace('[bi]', '[i]').replace('[/bi]', '[/i]'))

    def _fix_bi_in_i(match):
        return '[i]{}[/i]'.format(
            match.groups()[0].replace('[bi]', '[b]').replace('[/bi]', '[/b]'))

    text = text.replace('[bi][bi]', '[bi]').replace('[/bi][/bi]', '[/bi]')
    text = text.replace('[b][b]', '[b]').replace('[/b][/b]', '[/b]')
    text = text.replace('[i][i]', '[i]').replace('[/i][/i]', '[/i]')

    text = re.sub(r'\[b\](.+?)\[\/b\]', _fix_bi_in_b, text, flags=re.DOTALL)
    text = re.sub(r'\[i\](.+?)\[\/i\]', _fix_bi_in_i, text, flags=re.DOTALL)

    text = text.replace('[bi]', '***').replace('[/bi]', '***')
    text = text.replace('[b]', '**').replace('[/b]', '**')
    text = text.replace('[i]', '*').replace('[/i]', '*')
    text = text.replace('[u]', '__').replace('[/u]', '__')
    text = text.replace('[strike]', '~~').replace('[/strike]', '~~')

    text = update_emojis(text)

    text = text.replace('[split]', '')
    text = text.replace('[', '`[').replace(']', ']`')
    text = text.replace('``', '')
    text = text.replace('`[lsb]`', '[').replace('`[rsb]`', ']')

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
    elif sphere in ('Neutral', 'Boon', 'Burden', 'Nightmare', 'Upgraded',
                    'Cave', 'Region'):
        card_sphere = '*{}* '.format(sphere)
    else:
        card_sphere = ''

    if 'Promo' in lotr.extract_flags(card.get(prefix + lotr.CARD_FLAGS)):
        card_promo = ' (**Promo**)'
    else:
        card_promo = ''

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
    for skill, value in skill_map.items():
        if card.get(value, '') != '':
            card_skills += '   {} {}'.format(EMOJIS['[{}]'.format(skill)],
                                             card[value])

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
    if (card_artist and 'NoArtist' in
            lotr.extract_flags(card.get(prefix + lotr.CARD_FLAGS))):
        card_artist = '{} *(not displayed on the card)*'.format(card_artist)

    res = f"""{card_unique}{card_name}
{card_sphere}{card_type}{card_promo}{card_cost}{card_engagement}{card_stage}{card_skills}

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

    custom_back = card.get(lotr.CARD_BACK, '')
    if custom_back:
        card_custom_back = '**{} Card Back**\n'.format(custom_back)
    elif (card_type in lotr.CARD_TYPES_PLAYER and
          'Encounter' in
          card.get(lotr.CARD_KEYWORDS, '').replace('. ', '.').split('.')):
        card_custom_back = '**Encounter Card Back**\n'
    else:
        card_custom_back = ''

    if card.get(lotr.CARD_ENCOUNTER_SET_BACK):
        encounter_set_back = ' / {}'.format(card[lotr.CARD_ENCOUNTER_SET_BACK])
    else:
        encounter_set_back = ''

    card_encounter_set = (
        '' if encounter_set == ''
        else '*Encounter Set*: {}{}{}\n'.format(encounter_set,
                                                encounter_set_back,
                                                additional_sets))

    card_set = re.sub(r'^ALeP - ', '', card[lotr.CARD_SET_NAME])
    card_id = '*id:* {}'.format(card[lotr.CARD_ID])

    if (card.get(lotr.CARD_PRINTED_NUMBER) or
            card.get(lotr.BACK_PREFIX + lotr.CARD_PRINTED_NUMBER)):
        if res_b:
            front_number = (card.get(lotr.CARD_PRINTED_NUMBER) or
                            card[lotr.CARD_NUMBER])
            back_number = (card.get(lotr.BACK_PREFIX +
                                    lotr.CARD_PRINTED_NUMBER) or
                           card[lotr.CARD_NUMBER])
            card_number = '**#{}/{}** *({})*'.format(front_number,
                                                     back_number,
                                                     card[lotr.CARD_NUMBER])
        else:
            front_number = (card.get(lotr.CARD_PRINTED_NUMBER) or
                            card[lotr.CARD_NUMBER])
            card_number = '**#{}** *({})*'.format(front_number,
                                                  card[lotr.CARD_NUMBER])
    else:
        card_number = '**#{}**'.format(card[lotr.CARD_NUMBER])

    icon = card.get(lotr.CARD_ICON, '')
    card_icon = '' if icon == '' else ' ({})'.format(icon)

    version = card.get(lotr.CARD_VERSION, '')
    card_version = '' if version == '' else ' **{}**'.format(version)

    custom_copyright = card.get(lotr.CARD_COPYRIGHT, '')
    card_custom_copyright = ('' if custom_copyright == ''
                             else '**{}**\n'.format(custom_copyright))

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
        ringsdb_url = '<{}/card/{}>\n'.format(
            CONF.get('ringsdb_url', ''), card[lotr.CARD_RINGSDB_CODE])
    else:
        ringsdb_url = ''

    row_url = '<{}&range=A{}>'.format(spreadsheet_url, card[lotr.ROW_COLUMN])
    if channel_url:
        channel_url = '<{}>'.format(channel_url)

    res = f"""{res_a}{res_b}

{card_set}{card_icon}, {card_number}{card_version} {card_quantity}
{card_encounter_set}{card_adventure}{card_custom_back}{card_custom_copyright}{card_id}

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

    if 'Promo' in lotr.extract_flags(card.get(lotr.CARD_FLAGS)):
        card_type = '{} (**Promo**)'.format(card_type)

    if (card_type_back and
            'Promo' in lotr.extract_flags(
                card.get(lotr.BACK_PREFIX + lotr.CARD_FLAGS))):
        card_type_back = '{} (**Promo**)'.format(card_type_back)

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


async def restart_bot():
    """ Restart the Discord bot.
    """
    await run_and_forget_shell(RESTART_BOT_CMD)


async def restart_cron():
    """ Restart the cron process.
    """
    await run_and_forget_shell(RESTART_CRON_CMD)


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

        if (card.get(lotr.CARD_TEXT) and
                (' Restricted.' in card[lotr.CARD_TEXT] or
                 '\nRestricted.' in card[lotr.CARD_TEXT])):
            keywords.add('Restricted')

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


def format_diffs(old_value, new_value):  # pylint: disable=R0912,R0914
    """ Format differences.
    """
    old_lines = [re.sub(r'^([-+])', ' \\1', line)
                 for line in old_value.strip().split('\n')]
    new_lines = [re.sub(r'^([-+])', ' \\1', line)
                 for line in new_value.strip().split('\n')]
    matches = 0
    left = []
    right = []
    for left_line in old_lines:
        if left_line in new_lines:
            while new_lines:
                right_line = new_lines.pop(0)
                if left_line == right_line:
                    left.append(left_line)
                    right.append(right_line)
                    matches += 1
                    break

                right.append('+ {}'.format(right_line))
        else:
            left.append('- {}'.format(left_line))

    for right_line in new_lines:
        right.append('+ {}'.format(right_line))

    left_value = '\n'.join(left).strip() or ' '
    right_value = '\n'.join(right).strip() or ' '

    old_lines = [re.sub(r'^([-+])', ' \\1', line)
                 for line in old_value.strip().split('\n')]
    new_lines = [re.sub(r'^([-+])', ' \\1', line)
                 for line in new_value.strip().split('\n')]
    matches_alt = 0
    left_alt = []
    right_alt = []
    for right_line in new_lines:
        if right_line in old_lines:
            while old_lines:
                left_line = old_lines.pop(0)
                if right_line == left_line:
                    right_alt.append(right_line)
                    left_alt.append(left_line)
                    matches_alt += 1
                    break

                left_alt.append('- {}'.format(left_line))
        else:
            right_alt.append('+ {}'.format(right_line))

    for left_line in old_lines:
        left_alt.append('- {}'.format(left_line))

    left_value_alt = '\n'.join(left_alt).strip() or ' '
    right_value_alt = '\n'.join(right_alt).strip() or ' '

    if matches_alt > matches:
        return left_value_alt, right_value_alt

    return left_value, right_value


def clear_rendered_images():
    """ Clear old rendered images from the local disk.
    """
    for _, subfolders, _ in os.walk(IMAGES_PATH):
        for subfolder in subfolders:
            lotr.delete_folder(os.path.join(IMAGES_PATH, subfolder))

        break


async def get_rendered_images(set_name):  # pylint: disable=R0914
    """ Get rendered images for the set.
    """
    if set_name not in RENDERED_IMAGES:
        RENDERED_IMAGES[set_name] = {'data': {},
                                     'download_time': None,
                                     'ts': 0}

    if (RENDERED_IMAGES[set_name]['data'] and
            time.time() - RENDERED_IMAGES_TTL <=
            RENDERED_IMAGES[set_name]['ts']):
        return (RENDERED_IMAGES[set_name]['data'],
                RENDERED_IMAGES[set_name]['download_time'])

    local_path = os.path.join(IMAGES_PATH, lotr.escape_filename(set_name))
    lotr.clear_folder(local_path)
    lotr.create_folder(local_path)

    folder = '{}.English'.format(lotr.escape_filename(set_name))
    stdout, stderr = await run_shell(RCLONE_RENDERED_FOLDER_CMD.format(folder))
    try:
        items = sorted(json.loads(stdout),
                       key=lambda i: i['Name']
                       if (i['Name'].endswith('-2.png')
                           or i['Name'] == 'download_time.txt')
                       else re.sub(r'\.png$', '-1.png', i['Name']))
    except Exception:
        message = ('RClone failed (rendered images), stdout: {}, stderr: {}'
                   .format(stdout, stderr))
        logging.error(message)
        if 'directory not found' not in stderr:
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)

        return {}, None

    card_data = await read_card_data()
    empty_rules_backs = {
        row[lotr.CARD_ID] for row in card_data['data']
        if row[lotr.CARD_SET_NAME] == set_name and
        row[lotr.CARD_TYPE] == 'Rules' and
        not row.get(lotr.BACK_PREFIX + lotr.CARD_TEXT) and
        not row.get(lotr.BACK_PREFIX + lotr.CARD_VICTORY)}

    data = {}
    download_time = None
    for item in items:
        filename = item['Name']
        if filename == 'download_time.txt':
            file_path = os.path.join(local_path, filename)
            stdout, stderr = await run_shell(
                RCLONE_COPY_IMAGE_CMD.format(folder, filename, local_path))
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as obj:
                    download_time = obj.read()
            else:
                if stdout or stderr:
                    message = ('RClone failed (rendered images), '
                               'stdout: {}, stderr: {}'
                               .format(stdout, stderr))
                    logging.error(message)
                    create_mail(ERROR_SUBJECT_TEMPLATE.format(message),
                                message)

            continue

        if not filename.endswith('.png') or not '----' in filename:
            continue

        card_id = filename.split('----')[1][:36]
        if filename.endswith('-2.png') and card_id in empty_rules_backs:
            continue

        data.setdefault(card_id, []).append(
            {'filename': filename,
             'modified': item['ModTime'].replace('T', ' ').split('.')[0]})

    RENDERED_IMAGES[set_name]['data'] = data
    RENDERED_IMAGES[set_name]['download_time'] = download_time
    RENDERED_IMAGES[set_name]['ts'] = time.time()
    return data, download_time


async def get_attachment_content(message):
    """ Get attachment content from the message.
    """
    if message.reference.resolved.attachments:
        attachment = message.reference.resolved.attachments[0]
        content = await attachment.read()
    else:
        url = message.reference.resolved.embeds[0].url
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                content = await res.read()

    return content


class MyClient(discord.Client):  # pylint: disable=R0902
    """ My bot class.
    """

    watch_changes_schedule_id = None
    rclone_art_schedule_id = None
    remote_cron_timestamp_schedule_id = None
    archive_category = None
    cron_channel = None
    notifications_channel = None
    playtest_channel = None
    updates_channel = None
    rclone_art = False
    categories = {}
    channels = {}
    general_channels = {}


    async def get_all_channels_safe(self):
        """ Safe method to get all Discord channels.
        """
        channels = [c for c in self.get_all_channels()]  # pylint: disable=R1721
        if not channels:
            await asyncio.sleep(COMMUNICATION_SLEEP_TIME)
            channels = [c for c in self.get_all_channels()]  # pylint: disable=R1721
            if not channels:
                message = 'No channels obtained from Discord'
                logging.error(message)
                create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)
                raise CommunicationError(message)

        return channels


    async def on_ready(self):
        """ Invoked when the client is ready.
        """
        logging.info('Logged in as %s (%s)', self.user.name, self.user.id)
        all_channels = await self.get_all_channels_safe()
        try:
            self.archive_category = self.get_channel(
                [c for c in all_channels
                 if str(c.type) == 'category' and
                 c.name == ARCHIVE_CATEGORY][0].id)
        except Exception as exc:
            logging.exception(str(exc))
            create_mail(WARNING_SUBJECT_TEMPLATE.format(
                'error obtaining archive category: {}'.format(str(exc))))

        try:
            self.cron_channel = self.get_channel(
                [c for c in all_channels
                 if str(c.type) == 'text' and
                 c.name == CRON_CHANNEL][0].id)
        except Exception as exc:
            logging.exception(str(exc))
            create_mail(WARNING_SUBJECT_TEMPLATE.format(
                'error obtaining Cron channel: {}'.format(str(exc))))

        try:
            self.notifications_channel = self.get_channel(
                [c for c in all_channels
                 if str(c.type) == 'text' and
                 c.name == NOTIFICATIONS_CHANNEL][0].id)
        except Exception as exc:
            logging.exception(str(exc))
            create_mail(WARNING_SUBJECT_TEMPLATE.format(
                'error obtaining Notifications channel: {}'.format(str(exc))))

        try:
            self.playtest_channel = self.get_channel(
                [c for c in all_channels
                 if str(c.type) == 'text' and
                 c.name == PLAYTEST_CHANNEL][0].id)
        except Exception as exc:
            logging.exception(str(exc))
            create_mail(WARNING_SUBJECT_TEMPLATE.format(
                'error obtaining Playtest channel: {}'.format(str(exc))))

        try:
            self.updates_channel = self.get_channel(
                [c for c in all_channels
                 if str(c.type) == 'text' and
                 c.name == UPDATES_CHANNEL][0].id)
        except Exception as exc:
            logging.exception(str(exc))
            create_mail(WARNING_SUBJECT_TEMPLATE.format(
                'error obtaining Spreadsheet Updates channel: {}'
                .format(str(exc))))

        clear_rendered_images()
        self.categories, self.channels, self.general_channels = (
            await self._load_channels())
        await self._test_channels()

        self.loop.create_task(self._watch_changes_schedule())
        self.loop.create_task(self._rclone_art_schedule())
        self.loop.create_task(self._remote_cron_timestamp_schedule())
        read_external_data()
        await read_card_data()
        await load_timestamps_data()


    async def _load_channels(self):  # pylint: disable=R0912
        categories = {}
        channels = {}
        general_channels = {}
        all_channels = await self.get_all_channels_safe()
        for channel in all_channels:
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
        logging.info('Starting watch changes schedule...')
        my_id = incremental_id()
        while True:
            async with watch_changes_lock:
                if (not self.watch_changes_schedule_id or
                        self.watch_changes_schedule_id < my_id):
                    self.watch_changes_schedule_id = my_id
                    logging.info('Acquiring watch changes schedule id: %s',
                                 my_id)
                elif self.watch_changes_schedule_id > my_id:
                    logging.info(
                        'Detected a new watch changes schedule id: %s, '
                        'exiting with the old id: %s',
                        self.watch_changes_schedule_id, my_id)
                    break

                await self._watch_changes()

            await asyncio.sleep(WATCH_SLEEP_TIME)


    async def _rclone_art_schedule(self):
        logging.info('Starting rclone art schedule...')
        my_id = incremental_id()
        while True:
            async with rclone_art_lock:
                if (not self.rclone_art_schedule_id or
                        self.rclone_art_schedule_id < my_id):
                    self.rclone_art_schedule_id = my_id
                    logging.info('Acquiring rclone art schedule id: %s', my_id)
                elif self.rclone_art_schedule_id > my_id:
                    logging.info(
                        'Detected a new rclone art schedule id: %s, '
                        'exiting with the old id: %s',
                        self.rclone_art_schedule_id, my_id)
                    break

                await self._rclone_art()

            await asyncio.sleep(RCLONE_ART_SLEEP_TIME)


    async def _remote_cron_timestamp_schedule(self):
        logging.info('Starting remote cron timestamp schedule...')
        my_id = incremental_id()
        while True:
            async with remote_cron_timestamp_lock:
                if (not self.remote_cron_timestamp_schedule_id or
                        self.remote_cron_timestamp_schedule_id < my_id):
                    self.remote_cron_timestamp_schedule_id = my_id
                    logging.info(
                        'Acquiring remote cron timestamp schedule id: %s',
                        my_id)
                elif self.remote_cron_timestamp_schedule_id > my_id:
                    logging.info(
                        'Detected a new remote cron timestamp schedule id: '
                        '%s, exiting with the old id: %s',
                        self.remote_cron_timestamp_schedule_id, my_id)
                    break

                await self._remote_cron_timestamp()

            await asyncio.sleep(REMOTE_CRON_TIMESTAMP_SLEEP_TIME)


    async def _watch_changes(self):
        try:
            for _, _, filenames in os.walk(CHANGES_PATH):
                filenames.sort()
                filenames = [f for f in filenames if f.endswith('.json')
                             and not f.startswith('__')]
                broken_filenames = [f for f in filenames if f.endswith('.json')
                                    and f.startswith('__')]
                if broken_filenames or not filenames:
                    break

                logging.info('Processing files: %s', filenames)
                await load_timestamps_data()
                for filename in filenames:
                    path = os.path.join(CHANGES_PATH, filename)
                    try:
                        data = await read_json_data(path)
                        logging.info('Processing changes: %s', data)
                        for card_id in data['card_ids']:
                            TIMESTAMPS['data'][card_id] = data['utc_time']

                        new_slots = len(
                            [c for c in data.get('categories', [])
                             if len(c) == 2 and c[0] == 'add']
                            ) + len(
                                [c for c in data.get('channels', [])
                                 if len(c) == 3 and c[0] == 'add']
                            )
                        all_channels = await self.get_all_channels_safe()
                        if CHANNEL_LIMIT - len(all_channels) < new_slots:
                            raise DiscordError(
                                'No free slots to create {} new channels'
                                .format(new_slots))

                        await self._process_category_changes(data)
                        await self._process_channel_changes(data)
                        await self._process_card_changes(data)
                    except Exception as exc:
                        logging.exception(str(exc))
                        message = 'error processing {}: {}'.format(
                            filename, str(exc))
                        create_mail(ERROR_SUBJECT_TEMPLATE.format(message),
                                    message)
                        if self.cron_channel:
                            await self._send_channel(self.cron_channel,
                                                     message)

                        shutil.move(path, os.path.join(
                            CHANGES_PATH, '__{}'.format(filename)))
                    else:
                        os.remove(path)

                break
        except Exception as exc:
            message = ('Unexpected error during watching for changes: {}: {}'
                       .format(type(exc).__name__, str(exc)))
            logging.exception(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)


    async def _rclone_art(self):
        if not self.rclone_art:
            return

        self.rclone_art = False
        stdout, stderr = await run_shell(
            RCLONE_ART_CMD.format(CONF.get('artwork_destination_path')))
        if stdout or stderr:
            message = ('RClone failed (artwork), stdout: {}, stderr: {}'
                       .format(stdout, stderr))
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)
            self.rclone_art = True
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


    async def _remote_cron_timestamp(self):
        stdout, stderr = await run_shell(
            RCLONE_LOGS_CMD.format(CONF.get('remote_logs_path')))
        if stdout or stderr:
            message = ('RClone failed (remote cron), stdout: {}, stderr: {}'
                       .format(stdout, stderr))
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)
            return

        stdout, _ = await run_shell(
            REMOTE_CRON_TIMESTAMP_CMD.format(CONF.get('remote_logs_path')))
        if stdout == '1' and self.notifications_channel:
            clear_rendered_images()
            await run_shell(RCLONE_RENDERER_CMD)
            await self._send_channel(
                self.notifications_channel,
                'New pixel-perfect card images are available in Discord and '
                'DragnCards')


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
                    all_channels = await self.get_all_channels_safe()
                    if CHANNEL_LIMIT - len(all_channels) <= 0:
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

                    if change[1][0] in self.general_channels:
                        channel = self.get_channel(
                            self.general_channels[change[1][0]]['id'])
                        del self.general_channels[change[1][0]]
                        self.general_channels[channel.category.name] = {
                            'name': channel.category.name,
                            'id': channel.id,
                            'category_id': channel.category_id}

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
                if len(change) != 3:
                    raise FormatError('Incorrect change format: {}'
                                      .format(change))

                if change[0] == 'add':
                    if len(change[1]) != 2:
                        raise FormatError('Incorrect change format: {}'.format(
                            change))

                    if change[1][1] not in self.categories:
                        raise DiscordError('Category "{}" not found'.format(
                            change[1][1]))

                    all_channels = await self.get_all_channels_safe()
                    if CHANNEL_LIMIT - len(all_channels) <= 0:
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
                    res = await self._move_artwork_files(
                        change[2]['card_id'], change[2]['old_set_id'],
                        change[2]['new_set_id'])
                    if res:
                        await channel.send(res)
                        await asyncio.sleep(CMD_SLEEP_TIME)

                    await self._copy_image_files(
                        change[2]['card_id'], change[2]['old_set_id'],
                        change[2]['new_set_id'])
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
                    res = await self._move_artwork_files(
                        change[2]['card_id'], change[2]['old_set_id'],
                        SCRATCH_FOLDER)
                    if res:
                        await channel.send(res)
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
                        all_channels = await self.get_all_channels_safe()
                        if CHANNEL_LIMIT - len(all_channels) <= 0:
                            message = (
                                'No free slots to create a new channel '
                                '"general" in category "{}"'
                                .format(card[lotr.CARD_DISCORD_CATEGORY]))
                            logging.error(message)
                            create_mail(ERROR_SUBJECT_TEMPLATE.format(message),
                                        message)
                            continue

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
                    diff[1] = str(diff[1]) if diff[1] is not None else ''
                    diff[2] = str(diff[2]) if diff[2] is not None else ''
                    diff[1], diff[2] = format_diffs(diff[1], diff[2])
                    diff[1] = '```diff\n{}\n```'.format(diff[1])
                    diff[2] = '```diff\n{}\n```'.format(diff[2])

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
                        logging.warning('Channel "%s" not found', channel_name)
                        continue

                    res = """
The card has been updated:

{}
""".format('\n'.join(diffs))
                    channel = self.get_channel(
                        self.channels[channel_name]['id'])
                    await self._send_channel(channel, res)
                else:
                    if card[lotr.CARD_DISCORD_CATEGORY] not in self.categories:
                        logging.warning('Category "%s" not found',
                                        card[lotr.CARD_DISCORD_CATEGORY])
                        continue

                    if (card[lotr.CARD_DISCORD_CATEGORY]
                            not in self.general_channels):
                        all_channels = await self.get_all_channels_safe()
                        if CHANNEL_LIMIT - len(all_channels) <= 0:
                            logging.warning(
                                'No free slots to create a new channel '
                                '"general" in category "%s"',
                                card[lotr.CARD_DISCORD_CATEGORY])
                            continue

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
        all_channels = await self.get_all_channels_safe()
        slots = CHANNEL_LIMIT - len(all_channels)
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
        first_message = None
        for i, chunk in enumerate(split_result(content)):
            if i > 0:
                await asyncio.sleep(1)

            message = await channel.send(chunk)
            if i == 0:
                first_message = message

        return first_message


    async def _process_cron_command(self, message):  #pylint: disable=R0912
        """ Process a cron command.
        """
        if message.content.lower() == '!cron':
            command = 'help'
        else:
            command = re.sub(r'^!cron ', '', message.content,
                             flags=re.IGNORECASE).split('\n')[0].strip()

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
        elif command.lower() == 'dragncards build':
            try:
                lotr.trigger_dragncards_build(CONF)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            await message.channel.send('done')
        elif command.lower() == 'errors':
            res, _ = await run_shell(CRON_ERRORS_CMD)
            if not res:
                res = 'no cron logs found'

            await self._send_channel(message.channel, res)
        elif command.lower() == 'trigger':
            delete_sheet_checksums()
            await message.channel.send('done')
        elif command.lower() == 'restart bot':
            await message.channel.send('restarting...')
            try:
                await restart_bot()
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return
        elif command.lower() == 'restart cron':
            try:
                await restart_cron()
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            await message.channel.send('done')
        else:
            res = HELP['cron']
            await self._send_channel(message.channel, res)


    async def _new_target(self, content):  # pylint: disable=R0914
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

        old_target_message = await self._view_target()

        async with playtest_lock:
            with open(PLAYTEST_PATH, 'w', encoding='utf-8') as obj:
                json.dump(data, obj)

        playtest_message = """----------
New playtesting targets:
{}""".format(format_playtest_message(data))

        if self.playtest_channel:
            if old_target_message:
                old_target_message = """----------
Archiving the previous targets:
{}""".format(old_target_message)
                pin_message = await self._send_channel(self.playtest_channel,
                                                       old_target_message)
                old_pins = await self.playtest_channel.pins()
                if len(old_pins) >= MAX_PINS:
                    first_pin = old_pins[-1]
                    await first_pin.unpin()

                await pin_message.pin()

            await self._send_channel(self.playtest_channel, playtest_message)

        return ''


    async def _view_target(self):
        """ Display existing playtesting target.
        """
        async with playtest_lock:
            try:
                with open(PLAYTEST_PATH, 'r', encoding='utf-8') as obj:
                    data = json.load(obj)
            except Exception:
                data = {'targets': [],
                        'description': ''}

        return format_playtest_message(data)


    async def _complete_target(self, content, num, user, url):
        """ Complete playtesting target.
        """
        if not re.match(r'^[0-9]+$', num):
            return 'target number "{}" doesn\'t look correct'.format(num)

        if len(content.split('\n', 1)) == 1:
            return 'please add a playtesting report'

        async with playtest_lock:
            try:
                with open(PLAYTEST_PATH, 'r+', encoding='utf-8') as obj:
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
            except Exception:
                return 'no previous targets found'

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
            try:
                with open(PLAYTEST_PATH, 'r+', encoding='utf-8') as obj:
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
            except Exception:
                return 'no previous targets found'

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


    async def _add_target(self, content):  # pylint: disable=R0911
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
            try:
                with open(PLAYTEST_PATH, 'r+', encoding='utf-8') as obj:
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
            except Exception:
                return 'no previous targets found'

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
            try:
                with open(PLAYTEST_PATH, 'r+', encoding='utf-8') as obj:
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
            except Exception:
                return 'no previous targets found'

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
                             flags=re.IGNORECASE).split('\n')[0].strip()

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
                if not res:
                    res = 'no previous targets found'
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


    async def get_quests_stat(self, quest):  # pylint: disable=R0914
        """ Get statistics for all found quests.
        """
        data = await read_card_data()
        if quest.lower() in data['set_codes']:
            quest = data['set_codes'][quest.lower()].replace('ALeP - ', '')

        quest_folder = lotr.escape_filename(quest).lower()
        quest_file = lotr.escape_octgn_filename(quest_folder)
        set_folders = {lotr.escape_filename(s) for s in data['sets']}
        quests = {}
        for _, subfolders, _ in os.walk(lotr.OUTPUT_OCTGN_DECKS_PATH):  # pylint: disable=R1702
            for subfolder in subfolders:
                if subfolder not in set_folders:
                    continue

                path = os.path.join(lotr.OUTPUT_OCTGN_DECKS_PATH, subfolder)
                for _, _, filenames in os.walk(path):
                    for filename in filenames:
                        if ((filename.endswith('.o8d') and
                             not filename.startswith('Player-') and
                             ('-{}-'.format(quest_file) in filename.lower() or
                              '-{}.'.format(quest_file) in filename.lower()))
                                or (quest_folder ==
                                    subfolder.replace('ALeP - ', '').lower())):
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

{stat['encounter_deck']}
"""

        if not res:
            res = 'no quests found'

        res = res.strip()
        res = re.sub(r'\n(?=\n)', '\n` `', res)
        return res


    async def _get_card(self, command, this=False):  # pylint: disable=R0912,R0914
        """ Get the card information.
        """
        data = await read_card_data()
        matches, num = find_card_matches(data, command, this)
        if not matches:
            return 'no cards found'

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
                             flags=re.IGNORECASE).split('\n')[0].strip()

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


    def get_users(self):
        """ Get the list of Discord users.
        """
        ignore_users = {u.strip() for u in CONF.get('ignore_users').split(',')}
        users = [m.display_name for m in self.guilds[0].members
                 if m.display_name not in ignore_users]
        users = [re.sub(r'[^\u0000-\uffff]+', '', u).strip() for u in users]
        users = [re.sub(r'[,./<>?;\':"\[\]\|{}]$', '', u).strip()
                 for u in users]
        users = [u.replace('[', '[[').replace(']', ']]').replace('[[', '[lsb]')
                 .replace(']]', '[rsb]') for u in users]
        users = sorted(list(set(users)), key=str.casefold)
        return ', '.join(users)


    async def _process_stat_command(self, message):
        """ Process a stat command.
        """
        if message.content.lower() == '!stat':
            command = 'help'
        else:
            command = re.sub(r'^!stat ', '', message.content,
                             flags=re.IGNORECASE).split('\n')[0].strip()

        logging.info('Received stat command: %s', command)

        if command.lower().startswith('quest '):
            try:
                quest = re.sub(r'^quest ', '', command,
                               flags=re.IGNORECASE)
                res = await self.get_quests_stat(quest)
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
                all_channels = await self.get_all_channels_safe()
                num = len(all_channels)
                res = 'There are {} channels and {} free slots'.format(
                    num, CHANNEL_LIMIT - num)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'assistants':
            try:
                res = self.get_users()
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'dragncards build':
            await message.channel.send('Please wait...')
            try:
                res = lotr.get_dragncards_build(CONF)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        else:
            res = HELP['stat']
            await self._send_channel(message.channel, res)


    async def _save_artwork(self, message, side, artist):  # pylint: disable=R0911,R0912,R0914
        """ Save an artwork image for the card.
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

        artwork_destination_path = CONF.get('artwork_destination_path')
        if not artwork_destination_path:
            raise RCloneFolderError('no artwork folder specified on the '
                                    'server')

        if not message.reference or not message.reference.resolved:
            return 'please reply to a message with an image attachment'

        if not (message.reference.resolved.attachments or
                message.reference.resolved.embeds):
            return 'please reply to a message with an image attachment'

        if message.reference.resolved.attachments:
            attachment = message.reference.resolved.attachments[0]
            if (attachment.content_type == 'image/png' or
                    attachment.filename.lower().endswith('png')):
                filetype = 'png'
            else:
                filetype = 'jpg'
        else:
            url = message.reference.resolved.embeds[0].url
            filename = re.sub(r'\/$', '', url.split('#')[0].split('?')[0]
                             ).split('/')[-1].lower()
            if filename.endswith('png'):
                filetype = 'png'
            else:
                filetype = 'jpg'

        content = await get_attachment_content(message)
        folder = os.path.join(artwork_destination_path, card[lotr.CARD_SET])
        filename = '{}_{}_{}_Artist_{}.{}'.format(
            card[lotr.CARD_ID],
            side,
            lotr.escape_filename(card[lotr.CARD_NAME]),
            artist,
            filetype)
        filename = filename.replace(' ', '_')
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


    async def _save_scratch_artwork(self, message, artist=None):
        """ Save an artwork image to the scratch folder.
        """
        artwork_destination_path = CONF.get('artwork_destination_path')
        if not artwork_destination_path:
            raise RCloneFolderError('no artwork folder specified on the '
                                    'server')

        if not message.reference or not message.reference.resolved:
            return 'please reply to a message with an image attachment'

        if not (message.reference.resolved.attachments or
                message.reference.resolved.embeds):
            return 'please reply to a message with an image attachment'

        if message.reference.resolved.attachments:
            attachment = message.reference.resolved.attachments[0]
            filename = attachment.filename
        else:
            url = message.reference.resolved.embeds[0].url
            filename = re.sub(r'\/$', '', url.split('#')[0].split('?')[0]
                             ).split('/')[-1]

        filename = lotr.escape_filename(filename)
        if artist:
            filename = '{}_{}'.format(artist, filename)

        filename = filename.replace(' ', '_')

        content = await get_attachment_content(message)
        folder = os.path.join(artwork_destination_path, SCRATCH_FOLDER)
        path = os.path.join(folder, filename)

        async with art_lock:
            if not os.path.exists(folder):
                os.mkdir(folder)

            with open(path, 'wb') as f_obj:
                f_obj.write(content)

            self.rclone_art = True

        return ''


    async def _get_artwork_files(self, set_id):
        """ Get the ordered list of artwork files for the set.
        """
        async with rclone_art_lock:
            await self._rclone_art()

        stdout, stderr = await run_shell(RCLONE_ART_FOLDER_CMD.format(set_id))
        try:
            filenames = [(f['Name'], f['ModTime']) for f in json.loads(stdout)]
            filenames.sort(key=lambda f: (f[1], f[0]), reverse=True)
            filenames = [f[0] for f in filenames]
        except Exception as exc:
            if 'directory not found' in stderr:
                return []

            message = ('RClone failed (artwork), stdout: {}, stderr: {}'
                       .format(stdout, stderr))
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)
            raise RCloneFolderError(message) from exc

        return filenames


    async def _get_image_files(self, set_folder):
        """ Get the list of rendered images for the set.
        """
        stdout, stderr = await run_shell(
            RCLONE_IMAGE_FOLDER_CMD.format(set_folder))
        try:
            filenames = [f['Name'] for f in json.loads(stdout)]
        except Exception as exc:
            if 'directory not found' in stderr:
                return []

            message = ('RClone failed (rendered images), stdout: {}, '
                       'stderr: {}'.format(stdout, stderr))
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)
            raise RCloneFolderError(message) from exc

        return filenames


    async def _move_artwork_files(self, card_id, old_set_id, new_set_id):
        """ Move artwork files for the card.
        """
        return_message = ''
        filenames = await self._get_artwork_files(old_set_id)
        for filename in filenames:
            if filename.split('_')[0] != card_id:
                continue

            stdout, stderr = await run_shell(
                RCLONE_MOVE_CLOUD_ART_CMD.format(
                    old_set_id, filename, new_set_id))
            if stdout or stderr:
                message = ('RClone failed (artwork), stdout: {}, stderr: {}'
                           .format(stdout, stderr))
                logging.error(message)
                create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)
                return_message = 'Failing to move artwork files for the card'
                break

            return_message = \
                'Artwork files for the card were successfully moved'

        return return_message


    async def _copy_image_files(self, card_id, old_set_id, new_set_id):
        """ Copy rendered images for the card.
        """
        data = await read_card_data()
        if (old_set_id not in data['set_ids'] or
                new_set_id not in data['set_ids']):
            return

        old_set_folder = '{}.English'.format(
            lotr.escape_filename(data['set_ids'][old_set_id]))
        new_set_folder = '{}.English'.format(
            lotr.escape_filename(data['set_ids'][new_set_id]))

        filenames = await self._get_image_files(old_set_folder)
        for filename in filenames:
            if '-{}'.format(card_id) not in filename:
                continue

            stdout, stderr = await run_shell(
                RCLONE_COPY_CLOUD_IMAGE_CMD.format(
                    old_set_folder, filename, new_set_folder))
            if stdout or stderr:
                message = ('RClone failed (rendered images), stdout: {}, '
                           'stderr: {}'.format(stdout, stderr))
                logging.error(message)
                create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)
                break


    async def _verify_artwork(self, value):  # pylint: disable=R0912,R0914,R0915
        """ Verify artwork for a set.
        """
        data = await read_card_data()

        set_name = re.sub(r'^alep---', '', lotr.normalized_name(value))
        matches = [card for card in data['data'] if re.sub(
            r'^alep---', '',
            lotr.normalized_name(card[lotr.CARD_SET_NAME])) ==
                   set_name and card[lotr.CARD_TYPE] not in ('Presentation',
                                                             'Rules')]
        if not matches:
            set_code = value.lower()
            matches = [card for card in data['data']
                       if card[lotr.CARD_SET_HOB_CODE].lower() == set_code
                       and card[lotr.CARD_TYPE] not in ('Presentation',
                                                        'Rules')]
            if not matches:
                return 'no cards found for the set'

        matches.sort(key=lambda card: (card[lotr.ROW_COLUMN]))
        filenames = await self._get_artwork_files(matches[0][lotr.CARD_SET])

        file_data = {}
        duplicate_artwork = []
        for filename in filenames:
            if (not filename.endswith('.png') and
                    not filename.endswith('.jpg')):
                continue

            parts = '.'.join(filename.split('.')[:-1]).split(
                '_Artist_', maxsplit=1)
            if len(parts) != 2:
                continue

            file_artist = parts[1].replace('_', ' ')
            parts = parts[0].split('_')
            if len(parts) < 3:
                continue

            file_id = parts[0]
            file_side = parts[1]
            if (file_id, file_side) in file_data:
                duplicate_artwork.append(filename)
            else:
                file_data[((file_id, file_side))] = file_artist

        missing_artwork = []
        different_artist = []
        no_spreadsheet_artist = []
        for card in matches:
            sides = ['A']
            if (card.get(lotr.BACK_PREFIX + lotr.CARD_NAME) and
                    (card.get(lotr.BACK_PREFIX + lotr.CARD_ARTIST) or
                     card.get(lotr.CARD_TYPE) not in
                     lotr.CARD_TYPES_DOUBLESIDE_OPTIONAL)):
                sides.append('B')

            for side in sides:
                artist = (card.get(lotr.CARD_ARTIST, '')
                          if side == 'A'
                          else card.get(lotr.BACK_PREFIX + lotr.CARD_ARTIST,
                                        ''))
                if (card[lotr.CARD_ID], side) not in file_data:
                    missing_artwork.append('{} ({}), side {}'.format(
                        card[lotr.CARD_ID], card[lotr.CARD_NAME], side))
                elif (lotr.escape_filename(
                        file_data[(card[lotr.CARD_ID], side)]) !=
                      lotr.escape_filename(artist)):
                    if artist:
                        different_artist.append(
                            '{} ({}), side {}: {} in spreadsheet and {} '
                            'on disk'.format(
                                card[lotr.CARD_ID], card[lotr.CARD_NAME], side,
                                artist, file_data[(card[lotr.CARD_ID], side)]))
                    else:
                        no_spreadsheet_artist.append(
                            '{} ({}), side {}: {} on disk'.format(
                                card[lotr.CARD_ID], card[lotr.CARD_NAME], side,
                                file_data[(card[lotr.CARD_ID], side)]))

        res = ''
        if missing_artwork:
            res += '\n**Missing artwork found**:```\n{}```'.format(
                '\n'.join(missing_artwork))

        if duplicate_artwork:
            res += '\n**Duplicate artwork found**:```\n{}```'.format(
                '\n'.join(duplicate_artwork))

        if different_artist:
            res += ('\n**Different spreadsheet artists found**:```\n{}```'
                    .format('\n'.join(different_artist)))

        if no_spreadsheet_artist:
            res += ('\n**Missing spreadsheet artists found**:```\n{}```'
                    .format('\n'.join(no_spreadsheet_artist)))

        res = res.strip()
        if not res:
            res = 'no issues found'

        return res


    async def _artwork_artists(self, value):  # pylint: disable=R0912,R0914
        """ Display a copy-pasteable list of artist names.
        """
        data = await read_card_data()

        set_name = re.sub(r'^alep---', '', lotr.normalized_name(value))
        matches = [card for card in data['data'] if re.sub(
            r'^alep---', '',
            lotr.normalized_name(card[lotr.CARD_SET_NAME])) ==
                   set_name and card[lotr.CARD_TYPE] not in ('Presentation',
                                                             'Rules')]
        if not matches:
            set_code = value.lower()
            matches = [card for card in data['data']
                       if card[lotr.CARD_SET_HOB_CODE].lower() == set_code
                       and card[lotr.CARD_TYPE] not in ('Presentation',
                                                        'Rules')]
            if not matches:
                return 'no cards found for the set'

        matches.sort(key=lambda card: (card[lotr.ROW_COLUMN]))
        filenames = await self._get_artwork_files(matches[0][lotr.CARD_SET])

        file_data = {}
        for filename in filenames:
            if (not filename.endswith('.png') and
                    not filename.endswith('.jpg')):
                continue

            parts = '.'.join(filename.split('.')[:-1]).split(
                '_Artist_', maxsplit=1)
            if len(parts) != 2:
                continue

            file_artist = parts[1].replace('_', ' ')
            parts = parts[0].split('_')
            if len(parts) < 3:
                continue

            file_id = parts[0]
            file_side = parts[1]
            if (file_id, file_side) not in file_data:
                file_data[((file_id, file_side))] = file_artist

        clusters = []
        last_cluster = []
        for card in matches:
            if not last_cluster:
                last_cluster.append(card)
                continue

            if last_cluster[-1][lotr.ROW_COLUMN] != card[lotr.ROW_COLUMN] - 1:
                clusters.append(last_cluster)
                last_cluster = []

            last_cluster.append(card)

        if last_cluster:
            clusters.append(last_cluster)

        res = ''
        sides = ['A', 'B']
        for cluster in clusters:
            artists = {'A': [], 'B': []}

            for card in cluster:
                for side in sides:
                    artists[side].append(file_data.get(
                        (card[lotr.CARD_ID], side), ''))

            for side in sides:
                if any(artists[side]):
                    row = cluster[0][lotr.ROW_COLUMN]
                    while artists[side][0] == '':
                        row += 1
                        artists[side].pop(0)

                    res += ('\nPaste into column "Artist" (Side {}), row '
                            '#**{}**:```\n{}\n```'.format(
                                side, row, '\n'.join(artists[side])))

        return res


    async def _process_art_command(self, message):  # pylint: disable=R0911,R0912,R0915
        """ Process an art command.
        """
        if message.content.lower() == '!art':
            command = 'help'
        else:
            command = re.sub(r'^!art ', '', message.content,
                             flags=re.IGNORECASE).split('\n')[0].strip()

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
        elif command.lower() == 'savescr':
            try:
                error = await self._save_scratch_artwork(message)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await message.channel.send(error)
                return

            await message.channel.send('done')
        elif command.lower().startswith('savescr '):
            try:
                artist = re.sub(r'^savescr ', '', command, flags=re.IGNORECASE)
                error = await self._save_scratch_artwork(message, artist)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await message.channel.send(error)
                return

            await message.channel.send('done')
        elif command.lower().startswith('verify '):
            await message.channel.send('Please wait...')
            try:
                set_name = re.sub(r'^verify ', '', command,
                                  flags=re.IGNORECASE)
                res = await self._verify_artwork(set_name)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'verify':
            await message.channel.send('please specify the set')
        elif command.lower().startswith('artists '):
            await message.channel.send('Please wait...')
            try:
                set_name = re.sub(r'^artists ', '', command,
                                  flags=re.IGNORECASE)
                res = await self._artwork_artists(set_name)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'artists':
            await message.channel.send('please specify the set')
        else:
            res = HELP['art']
            await self._send_channel(message.channel, res)


    async def _post_rendered_set(self, value):  # pylint: disable=R0912,R0914
        """ Post the last rendered images for all cards from a set.
        """
        data = await read_card_data()

        set_name = re.sub(r'^alep---', '', lotr.normalized_name(value))
        matches = [card for card in data['data'] if re.sub(
            r'^alep---', '',
            lotr.normalized_name(card[lotr.CARD_SET_NAME])) == set_name]
        if not matches:
            set_code = value.lower()
            matches = [card for card in data['data']
                       if card[lotr.CARD_SET_HOB_CODE].lower() == set_code]

            if not matches:
                return 'no cards found for the set'

        set_name = matches[0][lotr.CARD_SET_NAME]
        images, download_time = await get_rendered_images(set_name)
        if not images:
            return 'no rendered images found for the set'

        await load_timestamps_data()
        local_path = os.path.join(IMAGES_PATH, lotr.escape_filename(set_name))
        for card in matches:
            if card[lotr.CARD_ID] not in images:
                continue

            if card.get(lotr.CARD_DISCORD_CHANNEL):
                channel_name = card[lotr.CARD_DISCORD_CHANNEL]
                if channel_name not in self.channels:
                    raise DiscordError('Channel "{}" not found'.format(
                        channel_name))

                channel = self.get_channel(self.channels[channel_name]['id'])
            else:
                if (card[lotr.CARD_DISCORD_CATEGORY] not in self.categories or
                        card[lotr.CARD_DISCORD_CATEGORY]
                        not in self.general_channels):
                    continue

                channel = self.get_channel(self.general_channels[
                    card[lotr.CARD_DISCORD_CATEGORY]]['id'])

            modified_times = []
            for image in images[card[lotr.CARD_ID]]:
                image_path = os.path.join(local_path, image['filename'])
                modified_times.append(image['modified'])
                if not os.path.exists(image_path):
                    stdout, stderr = await run_shell(
                        RCLONE_COPY_IMAGE_CMD.format(
                            '{}.English'.format(lotr.escape_filename(set_name)),
                            image['filename'], local_path))
                    if not os.path.exists(image_path):
                        if stdout or stderr:
                            message = ('RClone failed (rendered images), '
                                       'stdout: {}, stderr: {}'
                                       .format(stdout, stderr))
                            logging.error(message)
                            create_mail(ERROR_SUBJECT_TEMPLATE.format(message),
                                        message)

                        await channel.send(
                            "Can't download the image from Google Drive")
                        continue

                await channel.send(file=discord.File(image_path))

            modified_time = download_time or max(modified_times)
            if (card[lotr.CARD_ID] in TIMESTAMPS['data'] and
                    TIMESTAMPS['data'][card[lotr.CARD_ID]] > modified_time):
                await channel.send(
                    'Last modified: {} UTC (**Card text was probably '
                    'changed since that time**)'.format(modified_time))
            else:
                await channel.send(
                    'Last modified: {} UTC'.format(modified_time))

        return 'done'


    async def _post_rendered_card(self, channel, value, this):  # pylint: disable=R0914
        """ Post the last rendered images for the card.
        """
        data = await read_card_data()
        matches, num = find_card_matches(data, value, this)
        matches = matches[:25]
        if not matches or num > len(matches):
            return 'no cards found'

        card = matches[num - 1][0]
        set_name = card[lotr.CARD_SET_NAME]
        images, download_time = await get_rendered_images(set_name)
        if not images or card[lotr.CARD_ID] not in images:
            return 'no rendered images found for the card'

        await load_timestamps_data()
        local_path = os.path.join(IMAGES_PATH, lotr.escape_filename(set_name))
        modified_times = []
        for image in images[card[lotr.CARD_ID]]:
            image_path = os.path.join(local_path, image['filename'])
            modified_times.append(image['modified'])
            if not os.path.exists(image_path):
                stdout, stderr = await run_shell(RCLONE_COPY_IMAGE_CMD.format(
                    '{}.English'.format(lotr.escape_filename(set_name)),
                    image['filename'], local_path))

                if not os.path.exists(image_path):
                    if stdout or stderr:
                        message = ('RClone failed (rendered images), '
                                   'stdout: {}, stderr: {}'
                                   .format(stdout, stderr))
                        logging.error(message)
                        create_mail(ERROR_SUBJECT_TEMPLATE.format(message),
                                    message)

                    return "Can't download the image from Google Drive"

            await channel.send(file=discord.File(image_path))

        modified_time = download_time or max(modified_times)
        if (card[lotr.CARD_ID] in TIMESTAMPS['data'] and
                TIMESTAMPS['data'][card[lotr.CARD_ID]] > modified_time):
            await channel.send(
                'Last modified: {} UTC (**Card text was probably '
                'changed since that time**)'.format(modified_time))
        else:
            await channel.send(
                'Last modified: {} UTC'.format(modified_time))

        return None


    async def _process_image_command(self, message):  # pylint: disable=R0912
        """ Process an image command.
        """
        if message.content.lower() == '!image':
            command = 'help'
        else:
            command = re.sub(r'^!image ', '', message.content,
                             flags=re.IGNORECASE).split('\n')[0].strip()

        logging.info('Received image command: %s', command)

        if command.lower().startswith('set '):
            await message.channel.send('Please wait...')
            try:
                set_name = re.sub(r'^set ', '', command,
                                  flags=re.IGNORECASE)
                res = await self._post_rendered_set(set_name)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'set':
            await message.channel.send('please specify the set')
        elif command.lower() == 'refresh':
            RENDERED_IMAGES.clear()
            await message.channel.send('done')
        elif command.lower() == 'card':
            await message.channel.send('please specify the card')
        elif command.lower() == 'help':
            res = HELP['image']
            await self._send_channel(message.channel, res)
        else:
            await message.channel.send('Please wait...')
            try:
                card_name = re.sub(r'^card ', '', command,
                                   flags=re.IGNORECASE)
                if card_name.lower() == 'this':
                    card_name = message.channel.name
                    this = True
                else:
                    this = False

                res = await self._post_rendered_card(message.channel,
                                                     card_name, this)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            if res:
                await self._send_channel(message.channel, res)


    async def _process_help_command(self, message):
        """ Process a help command.
        """
        logging.info('Received help command')

        help_keys = sorted([key for key in HELP if key != 'playtest'])
        help_keys.append('playtest')
        res = ''.join(HELP[key] for key in help_keys)
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
            elif (message.content.lower().startswith('!image ') or
                  message.content.lower() == '!image'):
                await self._process_image_command(message)
            elif (message.content.lower().startswith('!stat ') or
                  message.content.lower() == '!stat'):
                await self._process_stat_command(message)
            elif message.content.lower().startswith('!help'):
                await self._process_help_command(message)
        except Exception as exc:
            message = ('Unexpected error during  processing a message: {}: {}'
                       .format(type(exc).__name__, str(exc)))
            logging.exception(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    CONF.update(get_discord_configuration())
    intents = discord.Intents.default()
    intents.members = True  # pylint: disable=E0237
    client = MyClient(intents=intents)
    client.run(CONF.get('token'))
