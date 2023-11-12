# pylint: disable=C0103,C0209,C0302,W0703
# -*- coding: utf8 -*-
""" Discord bot.
"""
import asyncio
import codecs
import csv
from datetime import datetime
from email.header import Header
import json
import logging
import os
import random
import re
import shutil
import sys
import time
import uuid
import xml.etree.ElementTree as ET

import aiohttp
import discord
import yaml

import common
import lotr


CHANGES_PATH = os.path.join(lotr.DISCORD_PATH, 'Changes')
CONF_PATH = 'discord.yaml'
IMAGES_PATH = os.path.join(lotr.DISCORD_PATH, 'Images')
LOG_PATH = 'discord_bot.log'
MAIL_COUNTER_PATH = os.path.join(lotr.DATA_PATH, 'discord_bot.cnt')
MAILS_PATH = 'mails'
PLAYTEST_PATH = os.path.join(lotr.DISCORD_PATH, 'Data', 'playtest.json')
RINGSDB_STAT_PATH = os.path.join(lotr.DATA_PATH, 'ringsdb_stat.json')
TEMP_PATH = os.path.join(lotr.DISCORD_PATH, 'Temp')
USERS_LIST_PATH = os.path.join(lotr.DISCORD_PATH, 'Data', 'users.csv')

CRON_ERRORS_CMD = './cron_errors.sh'
CRON_LOG_CMD = './cron_log.sh'
MAGICK_GENERATE_CMD = (
    'convert -resize {}x{} -gravity center -background black -extent {}x{} '
    '-crop {}x{}+0+0 -format jpg {} {}')
MONITOR_REMOTE_PIPELINE_CMD = 'python3 monitor_remote_pipeline.py'
RCLONE_ART_CMD = "rclone copy '{}' 'ALePCardImages:/'"
RCLONE_ART_FOLDER_CMD = "rclone lsjson 'ALePCardImages:/{}/'"
RCLONE_COPY_KEEP_ART_CMD = \
    "rclone copy 'ALePCardImages:/{}/{}/' '{}/{}/{}/'"
RCLONE_COPY_IMAGE_CMD = "rclone copy 'ALePRenderedImages:/{}/{}' '{}/'"
RCLONE_COPY_CLOUD_FOLDER_CMD = \
    "rclone copy 'ALePRenderedImages:/{}/' 'ALePRenderedImages:/{}/'"
RCLONE_COPY_CLOUD_IMAGE_CMD = \
    "rclone copy 'ALePRenderedImages:/{}/{}' 'ALePRenderedImages:/{}/'"
RCLONE_GENERATED_CMD = "rclone copy '{}' 'ALePCardImages:/generated/'"
RCLONE_LOGS_CMD = "rclone copy 'ALePLogs:/' '{}/'"
RCLONE_MOVE_CLOUD_ART_CMD = \
    "rclone move 'ALePCardImages:/{}/{}' 'ALePCardImages:/{}/'"
RCLONE_RENDERED_FOLDER_CMD = "rclone lsjson 'ALePRenderedImages:/{}/'"
RCLONE_RENDERER_CMD = './rclone_renderer.sh'
REMOTE_CRON_TIMESTAMP_CMD = './remote_cron_timestamp.sh "{}"'
RESTART_BOT_CMD = './restart_discord_bot.sh'
RESTART_CRON_CMD = './restart_run_before_se_service.sh'

CHANNEL_ID_REGEX = r'^<#[0-9]+>$'
DIRECT_URL_REGEX = r'itemJson: \[[^,]+,"[^"]+","([^"]+)"'

CMD_SLEEP_TIME = 2
COMMUNICATION_SLEEP_TIME = 5
IO_SLEEP_TIME = 1
RCLONE_ART_SLEEP_TIME = 300
REMOTE_CRON_TIMESTAMP_SLEEP_TIME = 1800
SANITY_CHECK_WAIT_TIME = 3600
WATCH_CHANGES_SLEEP_TIME = 5
WATCH_SANITY_CHECK_SLEEP_TIME = 300

ERROR_SUBJECT_TEMPLATE = 'LotR Discord Bot ERROR: {}'
WARNING_SUBJECT_TEMPLATE = 'LotR Discord Bot WARNING: {}'

CRON_CHANNEL = 'cron'
NOTIFICATIONS_CHANNEL = 'notifications'
PLAYTEST_CHANNEL = 'checklist'
UPDATES_CHANNEL = 'spreadsheet-updates'

KEEP_FOLDER = '_Keep'
SCRATCH_FOLDER = '_Scratch'

ARCHIVE_CATEGORY = 'Archive'
CARD_DECK_SECTION = '_Deck Section'
CHANNEL_LIMIT = 500
GENERAL_CATEGORIES = {
    'Text Channels', 'Division of Labor', 'Player Card Design', 'Printing',
    'Rules', 'Voice Channels', 'Archive'
}
LOG_LEVEL = logging.INFO
MAIL_QUOTA = 50
MAX_PINS = 50
PREVIEW_URL = 'https://drive.google.com/file/d/{}/preview'
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

PORTRAIT = {
    'Ally': '87,0,326,330',
    'Attachment': '40,50,333,280',
    'Campaign': '0,0,413,245',
    'Contract': '0,0,413,315',
    'Encounter Side Quest': '0,0,563,413',
    'Enemy': '87,0,326,330',
    'Enemy NoStat': '0,0,413,563',
    'Event': '60,0,353,330',
    'Hero': '87,0,326,330',
    'Location': '0,60,413,268',
    'Nightmare': '0,77,413,245',
    'Objective': '0,69,413,300',
    'Objective Ally': '78,81,335,268',
    'Objective Hero': '78,81,335,268',
    'Objective Location': '0,69,413,300',
    'Player Objective': '0,69,413,300',
    'Player Side Quest': '0,0,563,413',
    'Quest': '0,0,563,413',
    'Ship Enemy': '87,0,326,330',
    'Ship Objective': '78,81,335,268',
    'Treachery': '60,0,353,330',
    'Treasure': '0,61,413,265'
}

HELP = {
    'alepcard': """
List of **!alepcard** commands:
` `
**!alepcard <card name>** - display the first card matching a given card name (for example: `!alepcard Thengel`)
**!alepcard <card name> n:<number>** - display the card #number matching a given card name (for example: `!alepcard Back Card n:2`)
**!alepcard <card name> s:<set code>** - display the first card matching a given card name from a given set (for example: `!alepcard Back Card s:CoE`)
**!alepcard <card name> s:<set code> n:<number>** - display the card #number matching a given card name from a given set (for example: `!alepcard Roused s:TSotS n:2`)
**!alepcard this** - if in a card channel, display this card
**!alepcard help** - display this help message
""",
    'cron': """
List of **!cron** commands:
` `
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
` `
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
` `
**!stat assistants** - display the list of assistants (all Discord users except for those who have a role)
**!stat channels** - display the number of Discord channels and free channel slots
**!stat dragncards build** - display information about the latest DragnCards build
**!stat quest <quest name or set name or set code>** - display the quest statistics
` `
**!stat player cards <set name or set code>** - display DragnCards player cards statistics for the set
**!stat player cards <set name or set code> <date in YYYY-MM-DD format>** - display DragnCards player cards statistics for the set starting from the specified date
**!stat player cards help** - display additional help about DragnCards player cards statistics
` `
**!stat all plays <quest name>** - display all DragnCards plays for the quest
**!stat all plays <quest name> <date in YYYY-MM-DD format>** - display all DragnCards plays for the quest starting from the specified date
**!stat all plays help** - display additional help about all DragnCards plays for the quest
` `
**!stat plays <quest name>** - display aggregated DragnCards plays statistics for the quest
**!stat plays <quest name> <date in YYYY-MM-DD format>** - display aggregated DragnCards plays statistics for the quest starting from the specified date
**!stat plays help** - display additional help about aggregated DragnCards plays statistics for the quest
` `
**!stat quests** - display aggregated DragnCards statistics for all released ALeP quests
**!stat quests <date in YYYY-MM-DD format>** - display aggregated DragnCards statistics for all released ALeP quests starting from the specified date
**!stat quests help** - display additional help about aggregated DragnCards statistics for all released ALeP quests
` `
**!stat help** - display this help message
""",
    'art': """
List of **!art** commands:
` `
**!art artists <set name or set code>** - display a copy-pasteable list of artist names (for example: `!art artists Children of Eorl` or `!art artists CoE`)
**!art keep <artist>** (as a reply to a message with an image attachment, empty artist means "Midjourney") - keep image for the channel's card (for example: `!art keep Alan Lee`)
**!art keep <card id> <artist>** (as a reply to a message with an image attachment, empty artist means "Midjourney") - keep image for the card with the given id (for example: `!art keep fd9da66d-06cd-430e-b6d2-9da2aa5bc52c Alan Lee`)
**!art keep <channel> <artist>** (as a reply to a message with an image attachment, empty artist means "Midjourney") - keep image for the card from the given channel (for example: `!art keep #hunting-dogs Alan Lee`)
**!art keep** - display all kept images for the channel's card
**!art keep <card id>** - display all kept images for the card with the given id (for example: `!art keep fd9da66d-06cd-430e-b6d2-9da2aa5bc52c`)
**!art keep <channel>** - display all kept images for the card from the given channel (for example: `!art keep #hunting-dogs`)
**!art save <artist>** (as a reply to a message with an image attachment, empty artist means "Midjourney") - save image as the channel's card front artwork (for example: `!art save Alan Lee`)
**!art save <card id> <artist>** (as a reply to a message with an image attachment, empty artist means "Midjourney") - save image as the front artwork of the card with the given id (for example: `!art save fd9da66d-06cd-430e-b6d2-9da2aa5bc52c Alan Lee`)
**!art save <channel> <artist>** (as a reply to a message with an image attachment, empty artist means "Midjourney") - save image as the front artwork of the card from the given channel (for example: `!art save #hunting-dogs Alan Lee`)
**!art saveb <artist>** (as a reply to a message with an image attachment, empty artist means "Midjourney") - save image as the channel's card back artwork (for example: `!art saveb John Howe`)
**!art saveb <card id> <artist>** (as a reply to a message with an image attachment, empty artist means "Midjourney") - save image as the back artwork of the card with the given id (for example: `!art saveb fd9da66d-06cd-430e-b6d2-9da2aa5bc52c John Howe`)
**!art saveb <channel> <artist>** (as a reply to a message with an image attachment, empty artist means "Midjourney") - save image as the back artwork of the card from the given channel (for example: `!art saveb #hunting-dogs Alan Lee`)
**!art savescr <artist>** (as a reply to a message with an image attachment, empty artist means "Midjourney") - save image to the scratch folder, <artist> is optional (for example: `!art savescr Ted Nasmith` or `!art savescr`)
**!art verify <set name or set code>** - verify artwork for a set (for example: `!art verify Children of Eorl` or `!art verify CoE`)
**!asm** - alias for **!art save Midjourney** (see above)
**!asbm** - alias for **!art saveb Midjourney** (see above)
**!art help** - display this help message
""",
    'image': """
List of **!image** commands:
` `
**!image set <set name or set code>** - post the last rendered images for all cards from a set (for example: `!image set The Aldburg Plot` or `!image set TAP`)
**!image card <card name>** - post the last rendered images for the first card matching a given card name (for example: `!image card Gavin`)
**!image card this** - if in a card channel, post the last rendered images for the card
**!image <card name>** - alias for **!image card <card name>** (see above)
**!image this** - alias for **!image card this** (see above)
**!image refresh** - clear the image cache (if you just uploaded new images to the Google Drive)
**!image help** - display this help message
""",
    'edit': """
List of **!edit** commands:
` `
**!edit check traits <a dot-separated list of traits>** - display the correct order of traits (for example: `!edit check traits Goblin. Orc.`)
**!edit flavour <set name or set code>** - display possible flavour text issues (for example: `!edit flavour Children of Eorl` or `!edit flavour CoE`)
**!edit names <set name or set code>** - display potentially unknown or misspelled names (for example: `!edit names Children of Eorl` or `!edit names CoE`)
**!edit numbers <set name or set code>** - display potentially incorrect card numbers (for example: `!edit numbers Children of Eorl` or `!edit numbers CoE`)
**!edit quests <set name or set code>** - display possible quest issues such as incorrect additional encounter sets or adventure values (for example: `!edit quests Children of Eorl` or `!edit quests CoE`)
**!edit space <set name or set code>** - display possible spacing issues like single linebreaks (for example: `!edit space Children of Eorl` or `!edit space CoE`)
**!edit text <set name or set code>** - display text that may be a subject of editing rules for a set (for example: `!edit text Children of Eorl` or `!edit text CoE`)
**!edit traits <set name or set code>** - display possible trait issues for a set (for example: `!edit traits Children of Eorl` or `!edit traits CoE`)
**!edit all <set name or set code>** - display results of all commands above (for example: `!edit all Children of Eorl` or `!edit all CoE`)
""",
    'secret': """
List of **!secret** commands:
` `
**!secret image refresh** - clear the image cache (if you just uploaded new images to the Google Drive)
**!secret users** - prepare a list of all Discord users and save it in `{}`
""".format(USERS_LIST_PATH)
}
HELP_STAT_PLAYER_CARDS = """
**!stat player cards <set name or set code>** - display DragnCards player cards statistics for the set
**!stat player cards <set name or set code> <date in YYYY-MM-DD format>** - display DragnCards player cards statistics for the set starting from the specified date
**!stat player cards help** - display this help message
` `
**Columns:**
`card      ` card name
`plays     ` total number of plays
`solo      ` number of solo plays
`mp        ` number of multiplayer plays
`win       ` number of victories
`loss      ` number of defeats
`-         ` number of incomplete plays
`num       ` average number of copies of the card included in the deck
`deck      ` % of cards in the player deck at the end of the play
`hand      ` % of cards in the player hand at the end of the play
`play      ` % of cards in play at the end of the play
`other     ` % of cards in all other areas at the end of the play (discard pile, victory display, etc.)
"""
HELP_STAT_ALL_PLAYS = """
**!stat all plays <quest name>** - display all DragnCards plays for the quest
**!stat all plays <quest name> <date in YYYY-MM-DD format>** - display all DragnCards plays for the quest starting from the specified date
**!stat all plays help** - display this help message
` `
**Columns:**
`date      ` date of the play
`replay_id ` replay ID.  You may replay any play by using a URL like `https://www.dragncards.com/newroom/replay/8da313ce-2f3a-4671-bd97-5ab379d39133`
`user      ` user name
`P         ` number of players
`R         ` number of rounds
`res       ` outcome of the play.  "win" means victory, "loss" means defeat, and "-" means an incomplete play.
`threat    ` threat of each player at the end of the play
`heroes    ` starting heroes of each player
"""
HELP_STAT_PLAYS = """
**!stat plays <quest name>** - display aggregated DragnCards plays statistics for the quest
**!stat plays <quest name> <date in YYYY-MM-DD format>** - display aggregated DragnCards plays statistics for the quest starting from the specified date
**!stat plays help** - display this help message
` `
**Columns:**
`players   ` number of players. "[any]" means aggregated statistics for any number of players.
`result    ` outcome of the play.  "win" means victory, "loss" means defeat, "-" means an incomplete play, and "[any]" means aggregated statistics for all outcomes.
`plays     ` total number of plays
`rnd_min   ` minimum number of rounds
`rnd_max   ` maximum number of rounds
`rnd_avg   ` average number of rounds
`thr_min   ` minimum player's threat at the end of the play
`thr_max   ` maximum player's threat at the end of the play
`thr_avg   ` average player's threat at the end of the play

`plays     ` total number of plays arranged by a user
`user      ` user name
"""
HELP_STAT_QUESTS = """
**!stat quests** - display aggregated DragnCards statistics for all released ALeP quests
**!stat quests <date in YYYY-MM-DD format>** - display aggregated DragnCards statistics for all released ALeP quests starting from the specified date
**!stat quests help** - display this help message
` `
**Columns:**
`quest     ` quest name
`plays     ` total number of plays
`solo      ` number of solo plays
`mp        ` number of multiplayer plays
`win       ` number of victories
`loss      ` number of defeats
`-         ` number of incomplete plays
`rnd W     ` average number of rounds (victories)
`rnd L     ` average number of rounds (defeats)
`thr W     ` average player's threat at the end of the play (victories)
`thr L     ` average player's threat at the end of the play (defeats)
"""

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
watch_sanity_check_lock = asyncio.Lock()
playtest_lock = asyncio.Lock()
art_lock = asyncio.Lock()
generate_lock = asyncio.Lock()


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


def get_next_card_number(old_value):
    """ Get the next card number.
    """
    old_value = str(old_value)
    if lotr.is_positive_int(old_value):
        new_value = str(int(old_value) + 1)
    elif old_value.startswith('0.') and len(old_value) == 3:
        old_value = old_value[-1]
        if old_value in '12345678':
            new_value = '0.{}'.format(str(int(old_value) + 1))
        elif old_value == '9':
            new_value = '0.A'
        elif old_value in 'ABCDEFGHIJKLMNOPQRSTUVWXY':
            new_value = '0.{}'.format(chr(ord(old_value) + 1))
        else:
            new_value = None
    else:
        new_value = None

    return new_value


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

        if re.search(r' s:[A-Za-z][A-Za-z0-9]+$', command):
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
            matches = [
                m for m in matches
                if m[0].get(lotr.CARD_SET_HOB_CODE, '').lower() == set_code]

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

    text = text.replace('[space]', ' ')
    text = text.replace('[vspace]', ' ')
    text = text.replace('[tab]', '   ')
    text = text.replace('[br]', '')
    text = text.replace('[nobr]', ' ')
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

    traits = re.sub(r'\[[^\]]+\]', '',
                    card.get(prefix + lotr.CARD_TRAITS, ''))
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

    icons = card.get(prefix + lotr.CARD_ICONS, '')
    if icons == '':
        card_icons = ''
    else:
        card_icons = '\n{}'.format(update_emojis(icons))

    info = card.get(prefix + lotr.CARD_INFO, '')
    if info == '':
        card_info = ''
    else:
        card_info = '\n**{}**'.format(info)

    flavour = update_text(card.get(prefix + lotr.CARD_FLAVOUR, ''))
    card_flavour = '' if flavour == '' else '\n\n*{}*'.format(flavour)

    artist = card.get(prefix + lotr.CARD_ARTIST, '')
    card_artist = '' if artist == '' else '\n\n*Artist*: {}'.format(artist)
    if (card_artist and 'NoArtist' in
            lotr.extract_flags(card.get(prefix + lotr.CARD_FLAGS))):
        card_artist = '{} *(not displayed on the card)*'.format(card_artist)

    res = f"""{card_unique}{card_name}
{card_sphere}{card_type}{card_promo}{card_cost}{card_engagement}{card_stage}{card_skills}

{card_traits}{card_keywords}{card_text}{card_shadow}{card_victory}{card_icons}{card_info}{card_flavour}{card_artist}"""  # pylint: disable=C0301
    return res


def format_card(card, spreadsheet_url, channel_url):  # pylint: disable=R0912,R0914,R0915
    """ Format the card.
    """
    card_type = card[lotr.CARD_TYPE]
    res_a = format_side(card, '')
    if (card.get(lotr.BACK_PREFIX + lotr.CARD_NAME) and  # pylint: disable=R0916
            card_type != 'Presentation' and
            (card_type not in ('Rules', 'Campaign', 'Contract', 'Nightmare') or
             (card_type == 'Contract' and
              card.get(lotr.BACK_PREFIX + lotr.CARD_TYPE) != 'Contract') or
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
          lotr.extract_keywords(card.get(lotr.CARD_KEYWORDS))):
        card_custom_back = '**Encounter Card Back**\n'
    else:
        card_custom_back = ''

    card_encounter_set = (
        '' if encounter_set == ''
        else '*Encounter Set*: {}{}\n'.format(encounter_set,
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

    collection_icon = card.get(lotr.CARD_COLLECTION_ICON, '')
    card_collection_icon = ('' if collection_icon == ''
                            else ' ({})'.format(collection_icon))

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
            CONF.get('ringsdb_url') or '', card[lotr.CARD_RINGSDB_CODE])
    else:
        ringsdb_url = ''

    row_url = '<{}&range=A{}>'.format(spreadsheet_url, card[lotr.ROW_COLUMN])
    if channel_url:
        channel_url = '<{}>'.format(channel_url)

    res = f"""{res_a}{res_b}

{card_set}{card_collection_icon}, {card_number} {card_quantity}
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
    """ Delete existing spreadsheet checksums.
    """
    if os.path.exists(lotr.SHEETS_JSON_PATH):
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

    download_time_file = os.path.split(lotr.DOWNLOAD_TIME_PATH)[-1]
    folder = '{}.English'.format(lotr.escape_filename(set_name))
    stdout, stderr = await run_shell(RCLONE_RENDERED_FOLDER_CMD.format(folder))
    try:
        items = sorted(json.loads(stdout),
                       key=lambda i: i['Name']
                       if (i['Name'].endswith('-2.png')
                           or i['Name'] == download_time_file)
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
        if filename == download_time_file:
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


async def get_dragncards_player_cards_stat(set_name, start_date):
    """ Get DragnCards player cards statistics for the set.
    """
    data = await read_card_data()
    set_name = re.sub(r'^alep---', '', lotr.normalized_name(set_name))
    matches = [card for card in data['data'] if re.sub(
        r'^alep---', '',
        lotr.normalized_name(card[lotr.CARD_SET_NAME])) == set_name and
        card[lotr.CARD_TYPE] in lotr.CARD_TYPES_PLAYER and
        'Promo' not in lotr.extract_flags(card.get(lotr.CARD_FLAGS))]

    if not matches:
        new_set_name = 'the-{}'.format(set_name)
        matches = [card for card in data['data'] if re.sub(
            r'^alep---', '',
            lotr.normalized_name(card[lotr.CARD_SET_NAME])) == new_set_name and
            card[lotr.CARD_TYPE] in lotr.CARD_TYPES_PLAYER and
            'Promo' not in lotr.extract_flags(card.get(lotr.CARD_FLAGS))]

    if not matches:
        set_code = set_name.lower()
        matches = [
            card for card in data['data']
            if card.get(lotr.CARD_SET_HOB_CODE, '').lower() == set_code and
            card[lotr.CARD_TYPE] in lotr.CARD_TYPES_PLAYER and
            'Promo' not in lotr.extract_flags(card.get(lotr.CARD_FLAGS))]
        if not matches:
            return 'no cards found for the set'

    set_name = matches[0][lotr.CARD_SET_NAME]
    try:
        with open(RINGSDB_STAT_PATH, 'r', encoding='utf-8') as obj:
            ringsdb_data = json.load(obj)
            end_date = [p['date_release'] for p in ringsdb_data['packs']
                        if p['name'] == set_name][0]
    except Exception:
        end_date = ''

    cards = {c[lotr.CARD_ID]:c[lotr.CARD_NAME] for c in matches}
    card_ids = ';'.join(list(cards.keys()))
    res = lotr.get_dragncards_player_cards_stat(
        CONF, card_ids, start_date, end_date)
    lines = res.split('\n')
    for i in range(1, len(lines)):
        parts = lines[i].split('\t', 1)
        if parts[0] in cards:
            parts[0] = cards[parts[0]]
            if len(parts[0]) < 29:
                parts[0] = parts[0] + ' ' * (29 - len(parts[0]))

            lines[i] = '\t'.join(parts)

    lines[1:] = sorted(lines[1:])
    res = '\n'.join(lines)
    res = '```\n{}```'.format(res.expandtabs(6))
    return res


async def get_dragncards_all_plays(quest, start_date):  # pylint: disable=R0914
    """ Get information about all DragnCards plays for the quest.
    """
    data = await read_card_data()
    matches = [card for card in data['data']
               if card.get(lotr.CARD_ENCOUNTER_SET, '').lower() ==
               quest.lower()]

    if not matches:
        new_quest = 'the {}'.format(quest.lower())
        matches = [card for card in data['data']
                   if card.get(lotr.CARD_ENCOUNTER_SET, '').lower() ==
                   new_quest]

    if not matches:
        return 'quest {} not found'.format(quest)

    set_name = matches[0][lotr.CARD_SET_NAME]
    try:
        with open(RINGSDB_STAT_PATH, 'r', encoding='utf-8') as obj:
            ringsdb_data = json.load(obj)
            end_date = [p['date_release'] for p in ringsdb_data['packs']
                        if p['name'] == set_name][0]
    except Exception:
        end_date = ''

    res = lotr.get_dragncards_all_plays(CONF, quest, start_date, end_date)
    res = res.expandtabs()

    ignore_playtesters = {
        u.strip()[:12].strip()
        for u in (CONF.get('ignore_playtesters') or '').split(',')}
    ignore_playtesters = [' {} '.format(p) for p in ignore_playtesters if p]

    if res and ignore_playtesters:
        filtered = []
        res = res.split('\n')
        header = res.pop(0)
        pos = header.find(' user ')
        filtered.append(header)

        for row in res:
            for playtester in ignore_playtesters:
                if pos > -1 and row.find(playtester) == pos:
                    row = '{} [private]'.format(row.split(' ')[0])
                    break

            filtered.append(row)

        filtered = '\n'.join(filtered)
    else:
        filtered = res

    res = '```\n{}```'.format(filtered)
    return res


async def get_dragncards_plays_stat(quest, start_date):
    """ Get aggregated DragnCards plays statistics for the quest.
    """
    data = await read_card_data()
    matches = [card for card in data['data']
               if card.get(lotr.CARD_ENCOUNTER_SET, '').lower() ==
               quest.lower()]

    if not matches:
        new_quest = 'the {}'.format(quest.lower())
        matches = [card for card in data['data']
                   if card.get(lotr.CARD_ENCOUNTER_SET, '').lower() ==
                   new_quest]

    if not matches:
        return 'quest {} not found'.format(quest)

    set_name = matches[0][lotr.CARD_SET_NAME]
    try:
        with open(RINGSDB_STAT_PATH, 'r', encoding='utf-8') as obj:
            ringsdb_data = json.load(obj)
            end_date = [p['date_release'] for p in ringsdb_data['packs']
                        if p['name'] == set_name][0]
    except Exception:
        end_date = ''

    res = lotr.get_dragncards_plays_stat(CONF, quest, start_date, end_date)
    res = res.expandtabs()

    ignore_playtesters = {
        u.strip() for u in (CONF.get('ignore_playtesters') or '').split(',')}
    ignore_playtesters = ['  {}'.format(p) for p in ignore_playtesters if p]

    if res and ignore_playtesters:
        filtered = []
        res = res.split('\n')
        for row in res:
            for playtester in ignore_playtesters:
                if re.match(r'^[1-9]', row) and row.endswith(playtester):
                    row = row.replace(playtester, '  [private]')
                    break

            filtered.append(row)

        filtered = '\n'.join(filtered)
    else:
        filtered = res

    res = '```\n{}```'.format(filtered)
    return res


async def get_dragncards_quests_stat(start_date):
    """ Get aggregated DragnCards statistics for all released ALeP quests.
    """
    with open(RINGSDB_STAT_PATH, 'r', encoding='utf-8') as obj:
        ringsdb_data = json.load(obj)

    packs = {}
    for pack in ringsdb_data['packs']:
        if pack['name'].startswith('ALeP - '):
            packs[pack['name']] = pack['date_release']

    quests = []
    for pack in ringsdb_data['quests']:
        if pack['name'] in packs:
            pack_start_date = max(packs[pack['name']], start_date)
            for quest in pack['quests']:
                quests.append('{}|{}'.format(re.sub(r'^ALeP - ', '', quest),
                                             pack_start_date))

    if not quests:
        return 'no quests found'

    res = lotr.get_dragncards_quests_stat(CONF, ';'.join(quests))
    res = '```\n{}```'.format(res.expandtabs(6))
    return res


def detect_traits(text):
    """ Detect trait names in the text.
    """
    traits = re.findall(r'(?<=\[bi\])[^\[]+(?=\[\/bi\])', text)
    return traits


def detect_names(text, card_type):  # pylint: disable=R0912
    """ Detect names in the text.
    """
    text = re.sub(r'\n{2,}', ' [] ', text)
    text = text.replace('\n', ' ')
    text = re.sub(r'\[red\][^\[]+\[\/red\]', ' [] ', text)
    text = re.sub(r'\[lotrheader[^\[]+\[\/lotrheader\]', ' [] ', text)
    text = re.sub(r'\[bi\][^\[]+\[\/bi\]', ' text ', text)
    text = re.sub(r'\[[^\]]+\]', ' separator ', text)
    text = re.sub(r'\.”|[.:()]', ' [] ', text)
    text = re.sub(r'(?![“”!?…,’\- \[\]]|\w).', ' unknown ', text)
    text = re.sub(r' stage [0-9][A-F]\b', ' text ', text)
    text = re.sub(r'(?:^|[ “])[0-9]+(?:[”, ]|$)', ' text ', text)
    text = text.replace(' son of ', ' sonof_ ')

    if card_type == 'Rules':
        text = re.sub(r'Adventure Pack in the “[^”]+”', ' text ', text)

    parts = [p.strip() for p in text.split('[]') if p.strip()]

    names = []
    for part in parts:
        part = re.sub(r'(?:separator +)+', '', part)
        words = re.split(r' +', part)
        words.append('word')
        last_name = []
        first_pos = None
        for pos, word in enumerate(words):
            cleaned_word = re.sub(r'[“”!?…,]', '', word)
            if lotr.is_capitalized(cleaned_word) and cleaned_word != 'X':
                if not last_name:
                    first_pos = pos

                last_name.append(word)
            elif cleaned_word.lower() in lotr.LOWERCASE_WORDS:
                if last_name:
                    last_name.append(word)
            else:
                while last_name:
                    cleaned_word = re.sub(r'[“”!?…,]', '', last_name[-1])
                    if lotr.is_capitalized(cleaned_word):
                        break

                    last_name = last_name[:-1]

                if last_name:
                    name = ' '.join(last_name)
                    name = re.sub(r'’$', '', re.sub(r'’s$', '',
                                                    re.sub(r',$', '', name)))
                    name = name.replace(' sonof_ ', ' son of ')
                    if name[0] == '“' and '”' not in name:
                        name = name[1:]

                    if name[-1] == '”' and '“' not in name:
                        name = name[:-1]

                    if not re.match(
                            r'Condition|Forced|Quest Resolution|Resolution|'
                            r'Response|Restricted|Setup|Shadow|Travel|'
                            r'Valour Response|When Revealed|(?:(?:Valour )?'
                            r'(?:Combat |Encounter |Planning |Quest |Refresh |'
                            r'Resource |Travel )?Action)', name):
                        names.append((first_pos, name))

                    first_pos = None
                    last_name = []

    return names


def verify_known_name(pos, name, card_type, all_card_names,  # pylint: disable=R0911,R0912,R0913
                      all_set_and_quest_names, all_encounter_set_names):
    """ Check whether the name is known or not.
    """
    all_names = set(all_card_names)
    if card_type == 'Rules':
        all_names.update(all_set_and_quest_names)
        all_names.update(
            ['“{}”'.format(n) for n in all_set_and_quest_names])
        all_names.update(all_encounter_set_names)
        all_names.update(lotr.ALLOWED_RULES_NAMES)
    elif card_type == 'Campaign':
        all_names.update(all_encounter_set_names)
        all_names.update(lotr.ALLOWED_CAMPAIGN_NAMES)
    elif card_type == 'Quest':
        all_names.update(all_encounter_set_names)

    if name in all_names:
        return True

    parts = re.split(r', and |, or |, | and | or ', name)
    if all(p.strip() in all_names for p in parts):
        return True

    parts = name.split(' to ')
    if all(p.strip() in all_names for p in parts):
        return True

    parts = re.split(r' to |, and |, or |, | and | or ', name)
    if all(p.strip() in all_names for p in parts):
        return True

    parts = name.split(' than on ')
    if all(p.strip() in all_names for p in parts):
        return True

    parts = re.split(r', | than on ', name)
    if all(p.strip() in all_names for p in parts):
        return True

    if pos == 0:
        parts = name.split(' ')
        first_word = re.sub(r'^[“…]', '', re.sub(r'[”!?…,]$', '', parts[0]))
        if first_word in lotr.ALLOWED_FIRST_WORDS:
            parts = parts[1:]
            if not parts:
                return True

            if parts[0] in ('and', 'or', 'to'):
                parts = parts[1:]

            name = ' '.join(parts)
            if name in all_names:
                return True

    parts = re.split(r', and |, or |, | and | or ', name)
    if all(p.strip() in all_names for p in parts):
        return True

    parts = name.split(' to ')
    if all(p.strip() in all_names for p in parts):
        return True

    parts = re.split(r' to |, and |, or |, | and | or ', name)
    if all(p.strip() in all_names for p in parts):
        return True

    parts = name.split(' than on ')
    if all(p.strip() in all_names for p in parts):
        return True

    parts = re.split(r', | than on ', name)
    if all(p.strip() in all_names for p in parts):
        return True

    return False


def get_flavour_errors(text, field, card, res):
    """ Detect possible flavour text issues.
    """
    errors, _, _, _ = lotr.parse_flavour(text, 'English')
    for error in errors:
        data = {'name': card[lotr.CARD_NAME],
                'field': field,
                'text': '*{}*'.format(text),
                'row': card[lotr.ROW_COLUMN]}
        res.setdefault(error, []).append(data)


def get_unknown_names(text, field, card, res, all_card_names,  # pylint: disable=R0913
                      all_set_and_quest_names, all_encounter_set_names):
    """ Detect unknown names in the text.
    """
    text = re.sub(r'(^|\n)(?:\[[^\]]+\])*\[i\](?!\[b\]Rumor\[\/b\]|Example:)'
                  r'.+?\[\/i\](?:\[[^\]]+\])*(?:\n|$)', '\\1',
                  text, flags=re.DOTALL)

    if 'developed by A Long-extended Party' in text:
        return

    unknown_names = set()
    names = detect_names(text, card[lotr.CARD_TYPE])
    for pos, name in names:
        if not verify_known_name(pos, name, card[lotr.CARD_TYPE],
                                 all_card_names, all_set_and_quest_names,
                                 all_encounter_set_names):
            unknown_names.add(name)

    if unknown_names:
        data = {'name': card[lotr.CARD_NAME],
                'field': field,
                'text': '\n'.join(sorted(unknown_names)),
                'row': card[lotr.ROW_COLUMN]}
        res.setdefault('Potentially unknown or misspelled names', []).append(
            data)


def get_rules_precedents(text, field, card, res, keywords_regex,  # pylint: disable=R0912,R0913,R0914,R0915
                         all_card_names, all_traits):
    """ Detect text rules precedents.
    """
    text = re.sub(r'(^|\n)(?:\[[^\]]+\])*\[i\](?!\[b\]Rumor\[\/b\]|Example:)'
                  r'.+?\[\/i\](?:\[[^\]]+\])*(?:\n|$)', '\\1\\*\\*\\*',
                  text, flags=re.DOTALL)
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
    if not paragraphs:
        return

    for paragraph in paragraphs:
        paragraph = paragraph.replace('\n', ' ')

        traits = detect_traits(paragraph)
        traits = sorted([t for t in traits if t not in all_traits and
                         t not in lotr.COMMON_TRAITS])
        if traits:
            traits_regex = (r'(?<=\[bi\])(' +
                            '|'.join([re.escape(t) for t in traits]) +
                            r')(?=\[\/bi\])')
            data = {'name': card[lotr.CARD_NAME],
                    'field': field,
                    'text': re.sub(traits_regex, '__**\\1**__', paragraph),
                    'row': card[lotr.ROW_COLUMN]}
            res.setdefault('Unknown traits', []).append(data)

        sentences = [s.strip() for s in paragraph.split('.') if s.strip()]
        for sentence in sentences:
            sentence_original = sentence
            sentence = sentence.replace('additional', '')
            sentence = re.sub(
                r'\bplace(?!.+?\badd.+?token)(?!.+?\bput.+?token).+?token'
                r'(?!.+?\bpool)', '', sentence, flags=re.IGNORECASE)
            sentence = re.sub(
                r'\bplace(?!.+?\badd.+?progress)(?!.+?\bput.+?progress).+?'
                r'progress', '', sentence, flags=re.IGNORECASE)
            sentence = re.sub(
                r'\badd(?!.+?\bplace.+?resource)(?!.+?\bput.+?resource).+?'
                r'resource.+?\bpool', '', sentence, flags=re.IGNORECASE)
            if (re.search('token', sentence, flags=re.IGNORECASE) and (
                    re.search(r'\badd', sentence, flags=re.IGNORECASE) or
                    re.search(r'\bput', sentence, flags=re.IGNORECASE) or
                    re.search(r'\bpool', sentence, flags=re.IGNORECASE))):
                data = {'name': card[lotr.CARD_NAME],
                        'field': field,
                        'text': re.sub(
                            r'((?:token|\badd|\bput|\bpool)[a-z]*)',
                            '__**\\1**__', sentence_original,
                            flags=re.IGNORECASE),
                        'row': card[lotr.ROW_COLUMN]}
                res.setdefault('Place vs Put vs Add', []).append(data)

            if (re.search('progress', sentence, flags=re.IGNORECASE) and (
                    re.search(r'\badd', sentence, flags=re.IGNORECASE) or
                    re.search(r'\bput', sentence, flags=re.IGNORECASE))):
                data = {'name': card[lotr.CARD_NAME],
                        'field': field,
                        'text': re.sub(
                            r'((?:progress|\badd|\bput)[a-z]*)',
                            '__**\\1**__', sentence_original,
                            flags=re.IGNORECASE),
                        'row': card[lotr.ROW_COLUMN]}
                res.setdefault('Place vs Put vs Add', []).append(data)

            if (re.search('resource(?! token)', sentence,
                          flags=re.IGNORECASE) and (
                    re.search(r'\badd', sentence, flags=re.IGNORECASE) or
                    re.search(r'\bput', sentence, flags=re.IGNORECASE) or
                    re.search(r'\bplace', sentence, flags=re.IGNORECASE))):
                data = {'name': card[lotr.CARD_NAME],
                        'field': field,
                        'text': re.sub(
                            r'((?:resource|\badd|\bput|\bplace)[a-z]*)',
                            '__**\\1**__', sentence_original,
                            flags=re.IGNORECASE),
                        'row': card[lotr.ROW_COLUMN]}
                res.setdefault('Place vs Put vs Add', []).append(data)

        value = paragraph.replace('Encounter Cards', '')
        match = re.search(keywords_regex, value)
        if match:
            similar_names = lotr.get_similar_names(match[0], all_card_names)
            for similar_name in similar_names:
                similar_name_regex = (
                    r'(?<!\[bi\])\b' + re.escape(similar_name) + r'\b')
                value = re.sub(similar_name_regex, '', value)

            if re.search(keywords_regex, value):
                data = {'name': card[lotr.CARD_NAME],
                        'field': field,
                        'text': re.sub(keywords_regex, ' __**\\1**__',
                                       paragraph),
                        'row': card[lotr.ROW_COLUMN]}
                res.setdefault('Possibly capitalized keywords',
                               []).append(data)

        if re.search(r'\bsearch[^.]+?\bdeck(?!.+?\bshuffle)', paragraph,
                     flags=re.IGNORECASE):
            data = {'name': card[lotr.CARD_NAME],
                    'field': field,
                    'text': re.sub(r'\b(search[^ ]*)(?=[^.]+?\bdeck)',
                                   '__**\\1**__', paragraph,
                                   flags=re.IGNORECASE),
                    'row': card[lotr.ROW_COLUMN]}
            res.setdefault('Shuffle after search', []).append(data)

        if re.search(r'\b(?:they|them|their)\b', paragraph,
                     flags=re.IGNORECASE):
            data = {'name': card[lotr.CARD_NAME],
                    'field': field,
                    'text': re.sub(r'\b(they|them|their)\b', '__**\\1**__',
                                   paragraph, flags=re.IGNORECASE),
                    'row': card[lotr.ROW_COLUMN]}
            res.setdefault('Ambiguous third-person pronouns', []).append(data)

        if re.search(r'\beither\b[^.]+\bor\b', paragraph, flags=re.IGNORECASE):
            data = {'name': card[lotr.CARD_NAME],
                    'field': field,
                    'text': re.sub(r'\b(either)\b', '__**\\1**__',
                                   re.sub(r'\b(or)\b', '__**\\1**__',
                                          paragraph, flags=re.IGNORECASE),
                                   flags=re.IGNORECASE),
                    'row': card[lotr.ROW_COLUMN]}
            res.setdefault('Commas in either ... or statements',
                           []).append(data)

        if re.search(r' 1\[pp\] [a-zàáâãäąæçćĉèéêëęìíîïłñńòóôõöœśßùúûüźż\[]',
                     paragraph, flags=re.IGNORECASE):
            data = {'name': card[lotr.CARD_NAME],
                    'field': field,
                    'text': re.sub(
                        r'(?<= 1\[pp\] )([a-zàáâãäąæçćĉèéêëęìíîïłñńòóôõöœśß'
                        r'ùúûüźż\'\-\[\]\/]+)', '__**\\1**__',
                        paragraph, flags=re.IGNORECASE),
                    'row': card[lotr.ROW_COLUMN]}
            res.setdefault('Plural after [pp]', []).append(data)

        if re.search(r'\b(?:he|him|his|she|her)\b', paragraph,
                     flags=re.IGNORECASE):
            data = {'name': card[lotr.CARD_NAME],
                    'field': field,
                    'text': re.sub(r'\b(he|him|his|she|her)\b',
                                   '__**\\1**__', paragraph,
                                   flags=re.IGNORECASE),
                    'row': card[lotr.ROW_COLUMN]}
            res.setdefault('Self-referential pronouns', []).append(data)
        elif (re.search(r'\b(?:it|its)\b', paragraph, flags=re.IGNORECASE) and
              card[lotr.CARD_TYPE] in (
                'Ally', 'Hero', 'Enemy', 'Objective Ally', 'Objective Hero',
                'Ship Enemy', 'Ship Objective') and
              card.get(lotr.CARD_UNIQUE)):
            data = {'name': card[lotr.CARD_NAME],
                    'field': field,
                    'text': re.sub(r'\b(it|its)\b', '__**\\1**__', paragraph,
                                   flags=re.IGNORECASE),
                    'row': card[lotr.ROW_COLUMN]}
            res.setdefault('Self-referential pronouns', []).append(data)

        if re.search(r'\bany\b(?! active location| [2-9])', paragraph,
                     flags=re.IGNORECASE):
            data = {'name': card[lotr.CARD_NAME],
                    'field': field,
                    'text': re.sub(
                        r'\b(any\b(?: 1)?)(?! active location| [2-9])',
                        '__**\\1**__', paragraph, flags=re.IGNORECASE),
                    'row': card[lotr.ROW_COLUMN]}
            res.setdefault('Use of singular "any"', []).append(data)

        if re.search(r'\b(?:one|two|three|four|five|six)\b', paragraph,
                     flags=re.IGNORECASE):
            data = {'name': card[lotr.CARD_NAME],
                    'field': field,
                    'text': re.sub(r'\b(one|two|three|four|five|six)\b',
                                   '__**\\1**__', paragraph,
                                   flags=re.IGNORECASE),
                    'row': card[lotr.ROW_COLUMN]}
            res.setdefault('Use of numerals', []).append(data)

        if re.search(r'\b(?:a|an)\b', paragraph, flags=re.IGNORECASE):
            data = {'name': card[lotr.CARD_NAME],
                    'field': field,
                    'text': re.sub(r'\b(a|an)\b', '__**\\1**__', paragraph,
                                   flags=re.IGNORECASE),
                    'row': card[lotr.ROW_COLUMN]}
            res.setdefault('Use of numerals (a/an)', []).append(data)

        if re.search(r'\b(?:less|fewer)\b', paragraph,
                     flags=re.IGNORECASE):
            data = {'name': card[lotr.CARD_NAME],
                    'field': field,
                    'text': re.sub(r'\b(less|fewer)\b', '__**\\1**__',
                                   paragraph, flags=re.IGNORECASE),
                    'row': card[lotr.ROW_COLUMN]}
            res.setdefault('Less vs fewer', []).append(data)

        if re.search(r'\b(?:more|greater)\b', paragraph,
                     flags=re.IGNORECASE):
            data = {'name': card[lotr.CARD_NAME],
                    'field': field,
                    'text': re.sub(r'\b(more|greater)\b', '__**\\1**__',
                                   paragraph, flags=re.IGNORECASE),
                    'row': card[lotr.ROW_COLUMN]}
            res.setdefault('More vs greater', []).append(data)

        if re.search(r'\bif able\b', paragraph,
                     flags=re.IGNORECASE):
            data = {'name': card[lotr.CARD_NAME],
                    'field': field,
                    'text': re.sub(r'\b(if able)\b', '__**\\1**__', paragraph,
                                   flags=re.IGNORECASE),
                    'row': card[lotr.ROW_COLUMN]}
            res.setdefault('If able', []).append(data)

        if re.search(r'\bcannot leave the staging area'
                     r'(?! \(?(?:except|unless) )',
                     paragraph, flags=re.IGNORECASE):
            data = {'name': card[lotr.CARD_NAME],
                    'field': field,
                    'text': re.sub(r'\b(cannot leave the staging area)\b',
                                   '__**\\1**__', paragraph,
                                   flags=re.IGNORECASE),
                    'row': card[lotr.ROW_COLUMN]}
            res.setdefault('Cannot leave the staging area (except ...)',
                           []).append(data)

        if (field in (lotr.CARD_SHADOW, lotr.BACK_PREFIX + lotr.CARD_SHADOW)
                and re.search(r'\badditional attacks?(?! against you)',
                              paragraph)):
            data = {'name': card[lotr.CARD_NAME],
                    'field': field,
                    'text': re.sub(r'\b(additional attacks?)\b', '__**\\1**__',
                                   paragraph),
                    'row': card[lotr.ROW_COLUMN]}
            res.setdefault('Additional attack against you', []).append(data)

        if re.search(r'\bForced: When\b', paragraph):
            data = {'name': card[lotr.CARD_NAME],
                    'field': field,
                    'text': re.sub(r'\b(Forced: When)\b', '__**\\1**__',
                                   paragraph),
                    'row': card[lotr.ROW_COLUMN]}
            res.setdefault('Forced: When vs Forced: After', []).append(data)

        if (card[lotr.CARD_TYPE] in lotr.CARD_TYPES_ENCOUNTER_SET and
                re.search(
                    r'\bcost\b',
                    re.sub(r'\b(?:no|engagement|printed(?: resource)?) cost\b',
                           '', paragraph, flags=re.IGNORECASE),
                    flags=re.IGNORECASE)):
            data = {'name': card[lotr.CARD_NAME],
                    'field': field,
                    'text': re.sub(r'\b(cost)\b', '__**\\1**__',
                                   paragraph, flags=re.IGNORECASE),
                    'row': card[lotr.ROW_COLUMN]}
            res.setdefault('Printed cost', []).append(data)

        if re.search(r': [A-Z]', paragraph):
            paragraph = re.sub(r'\bQuest Resolution(?: \([^\)]+\))?:',
                               '\\*\\*\\*', paragraph)
            paragraph = re.sub(r'\b(?:Valour )?(?:Resource |Planning |Quest '
                               r'|Travel |Encounter |Combat |Refresh )?'
                               r'(?:Action):', '\\*\\*\\*', paragraph)
            paragraph = re.sub(r'\b(?:When Revealed|Forced|Valour Response'
                               r'|Response|Travel|Shadow|Resolution):',
                               '\\*\\*\\*', paragraph)
            paragraph = re.sub(r'\bSetup(?: \([^\)]+\))?:', '\\*\\*\\*',
                               paragraph)
            paragraph = re.sub(r'^\[i\]\[b\]Rumor\[\/b\]:', '\\*\\*\\*',
                               paragraph)
            if re.search(r': [A-Z]',
                         paragraph.replace(card[lotr.CARD_NAME], '\\*\\*\\*')):
                data = {'name': card[lotr.CARD_NAME],
                        'field': field,
                        'text': re.sub(r'(?<=: )([A-Z][A-Za-z\'\-]+)',
                                       '__**\\1**__', paragraph),
                        'row': card[lotr.ROW_COLUMN]}
                res.setdefault('Capitalization after a colon', []).append(data)


class MyClient(discord.Client):  # pylint: disable=R0902
    """ My bot class.
    """

    watch_changes_schedule_id = None
    rclone_art_schedule_id = None
    remote_cron_timestamp_schedule_id = None
    watch_sanity_check_schedule_id = None
    archive_category = None
    cron_channel = None
    notifications_channel = None
    playtest_channel = None
    updates_channel = None
    rclone_art = False
    last_sanity_check_mtime = None
    categories = {}
    channels = {}
    general_channels = {}


    def get_channel_name_by_id(self, channel_id):
        """ Get channel name by its ID.
        """
        for channel in self.channels.values():
            if channel['id'] == channel_id:
                return channel['name']

        return None


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
            create_mail(ERROR_SUBJECT_TEMPLATE.format(
                'Error obtaining Archive category: {}'.format(str(exc))))

        try:
            self.cron_channel = self.get_channel(
                [c for c in all_channels
                 if str(c.type) == 'text' and
                 c.name == CRON_CHANNEL][0].id)
        except Exception as exc:
            logging.exception(str(exc))
            create_mail(ERROR_SUBJECT_TEMPLATE.format(
                'Error obtaining Cron channel: {}'.format(str(exc))))

        try:
            self.notifications_channel = self.get_channel(
                [c for c in all_channels
                 if str(c.type) == 'text' and
                 c.name == NOTIFICATIONS_CHANNEL][0].id)
        except Exception as exc:
            logging.exception(str(exc))
            create_mail(ERROR_SUBJECT_TEMPLATE.format(
                'Error obtaining Notifications channel: {}'.format(str(exc))))

        try:
            self.playtest_channel = self.get_channel(
                [c for c in all_channels
                 if str(c.type) == 'text' and
                 c.name == PLAYTEST_CHANNEL][0].id)
        except Exception as exc:
            logging.exception(str(exc))
            create_mail(ERROR_SUBJECT_TEMPLATE.format(
                'Error obtaining Playtest channel: {}'.format(str(exc))))

        try:
            self.updates_channel = self.get_channel(
                [c for c in all_channels
                 if str(c.type) == 'text' and
                 c.name == UPDATES_CHANNEL][0].id)
        except Exception as exc:
            logging.exception(str(exc))
            create_mail(ERROR_SUBJECT_TEMPLATE.format(
                'Error obtaining Spreadsheet Updates channel: {}'
                .format(str(exc))))

        clear_rendered_images()
        self.categories, self.channels, self.general_channels = (
            await self._load_channels())
        await self._test_channels()

        self.loop.create_task(self._watch_changes_schedule())
        self.loop.create_task(self._rclone_art_schedule())
        self.loop.create_task(self._remote_cron_timestamp_schedule())
        self.loop.create_task(self._watch_sanity_check_schedule())
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
                    message = 'Duplicate category name detected: {}'.format(
                        channel.name)
                    logging.warning(message)
                    create_mail(WARNING_SUBJECT_TEMPLATE.format(message))
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
                    message = ('Duplicate general channel for category "{}" '
                               'detected'.format(channel.category.name))
                    logging.warning(message)
                    create_mail(WARNING_SUBJECT_TEMPLATE.format(message))
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
                    message = (
                        'Duplicate channel name detected: {} (categories '
                        '"{}" and "{}")'.format(
                            channel.name,
                            channels[channel.name]['category_name'],
                            channel.category.name))
                    logging.warning(message)
                    create_mail(WARNING_SUBJECT_TEMPLATE.format(message))
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

            await asyncio.sleep(WATCH_CHANGES_SLEEP_TIME)


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


    async def _watch_sanity_check_schedule(self):
        logging.info('Starting watch sanity check schedule...')
        my_id = incremental_id()
        while True:
            async with watch_sanity_check_lock:
                if (not self.watch_sanity_check_schedule_id or
                        self.watch_sanity_check_schedule_id < my_id):
                    self.watch_sanity_check_schedule_id = my_id
                    logging.info('Acquiring watch sanity check schedule id: '
                                 '%s', my_id)
                elif self.watch_sanity_check_schedule_id > my_id:
                    logging.info(
                        'Detected a new watch sanity check schedule id: %s, '
                        'exiting with the old id: %s',
                        self.watch_sanity_check_schedule_id, my_id)
                    break

                await self._watch_sanity_check()

            await asyncio.sleep(WATCH_SANITY_CHECK_SLEEP_TIME)


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
                        await self._process_set_name_changes(data)
                        await self._process_set_changes(data)
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

        artwork_destination_path = CONF.get('artwork_destination_path')
        if not artwork_destination_path:
            return

        self.rclone_art = False
        stdout, stderr = await run_shell(
            RCLONE_ART_CMD.format(artwork_destination_path))
        if stdout or stderr:
            message = ('RClone failed (artwork), stdout: {}, stderr: {}'
                       .format(stdout, stderr))
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)
            self.rclone_art = True
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
            await run_shell(MONITOR_REMOTE_PIPELINE_CMD)


    async def _watch_sanity_check(self):
        if not os.path.exists(lotr.SANITY_CHECK_PATH):
            return

        size = os.path.getsize(lotr.SANITY_CHECK_PATH)
        if size == 0:
            return

        mtime = os.path.getmtime(lotr.SANITY_CHECK_PATH)
        if mtime == self.last_sanity_check_mtime:
            return

        if time.time() > mtime + SANITY_CHECK_WAIT_TIME:
            self.last_sanity_check_mtime = mtime

            sanity_check_users = CONF.get('sanity_check_users') or ''
            await self._send_channel(
                self.cron_channel,
                '{} Please take a look at the sanity check issues above'
                .format(sanity_check_users).strip())


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

        for change in changes:
            if len(change) != 3:
                raise FormatError('Incorrect change format: {}'.format(change))

            if change[0] not in ('add', 'move', 'remove', 'rename'):
                raise FormatError('Unknown channel change type: {}'.format(
                    change[0]))

        for change in changes:
            if change[0] == 'move':
                if len(change[1]) != 2:
                    raise FormatError('Incorrect change format: {}'.format(
                        change))

                if change[1][0] not in self.channels:
                    raise DiscordError('Channel "{}" not found'.format(
                        change[1][0]))

                if change[1][1] not in self.categories:
                    raise DiscordError('Category "{}" not found'.format(
                        change[1][1]))

                channel = self.get_channel(self.channels[change[1][0]]['id'])
                old_category_name = channel.category.name
                category = self.get_channel(
                    self.categories[change[1][1]]['id'])
                await channel.move(category=category, end=True)
                logging.info('Moved channel "%s" from category "%s" to "%s"',
                             change[1][0], old_category_name, change[1][1])
                await self._send_channel(
                    channel,
                    'Moved from category "{}" to "{}"'
                    .format(old_category_name, change[1][1]))
                await asyncio.sleep(CMD_SLEEP_TIME)
                self.channels[change[1][0]] = {
                    'name': channel.name,
                    'id': channel.id,
                    'category_id': channel.category_id,
                    'category_name': channel.category.name}

        for change in changes:
            if change[0] == 'remove':
                if change[1] not in self.channels:
                    raise DiscordError('Channel "{}" not found'.format(
                        change[1]))

                if not self.archive_category:
                    raise DiscordError('Category "{}" not found'.format(
                        ARCHIVE_CATEGORY))

                channel = self.get_channel(self.channels[change[1]]['id'])
                old_category_name = channel.category.name
                await channel.move(category=self.archive_category, end=True)
                logging.info('The card has been removed from the spreadsheet. '
                             'Moved channel "%s" from category "%s" to "%s"',
                             change[1], old_category_name, ARCHIVE_CATEGORY)
                await self._send_channel(
                    channel,
                    'The card has been removed from the spreadsheet. Moved '
                    'from category "{}" to "{}"'.format(old_category_name,
                                                        ARCHIVE_CATEGORY))
                await asyncio.sleep(CMD_SLEEP_TIME)
                await self._move_artwork_files(
                    [change[2]['card_id']], change[2]['old_set_id'],
                    SCRATCH_FOLDER)
                del self.channels[change[1]]

        old_channel_names = []
        new_channels = {}
        try:
            for change in changes:
                if change[0] == 'rename':
                    if len(change[1]) != 2:
                        raise FormatError('Incorrect change format: {}'.format(
                            change))

                    if change[1][0] not in self.channels:
                        logging.warning('Channel "%s" not found', change[1][0])
                        continue

                    channel = self.get_channel(
                        self.channels[change[1][0]]['id'])
                    await channel.edit(name=change[1][1])
                    old_channel_names.append(change[1][0])
                    new_channels[change[1][1]] = {
                        'name': channel.name,
                        'id': channel.id,
                        'category_id': channel.category_id,
                        'category_name': channel.category.name}
                    logging.info('Renamed channel "%s" to "%s"', change[1][0],
                                 change[1][1])
                    await self._send_channel(
                        channel,
                        'Renamed from "{}" to "{}"'.format(change[1][0],
                                                           change[1][1]))
                    await asyncio.sleep(CMD_SLEEP_TIME)
        finally:
            for name in old_channel_names:
                del self.channels[name]

            self.channels.update(new_channels)

        for change in changes:
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
                logging.info('Created new channel "%s" in category "%s"',
                             change[1][0], change[1][1])
                await self._check_free_slots()
                await asyncio.sleep(CMD_SLEEP_TIME)
                self.channels[change[1][0]] = {
                    'name': channel.name,
                    'id': channel.id,
                    'category_id': channel.category_id,
                    'category_name': channel.category.name}


    async def _process_card_changes(self, data):  #pylint: disable=R0912,R0914,R0915
        changes = data.get('cards', [])
        if not changes:
            return

        data = await read_card_data()
        for change in changes:  # pylint: disable=R1702
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
                            if self.cron_channel:
                                await self._send_channel(self.cron_channel,
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
                    if diff[0] == lotr.BACK_PREFIX + lotr.CARD_NAME:
                        diff[0] = lotr.CARD_SIDE_B

                    if card[lotr.CARD_TYPE] == 'Quest':
                        if diff[0] in (lotr.CARD_COST,
                                       lotr.BACK_PREFIX + lotr.CARD_COST):
                            diff[0] = '{} (Quest Stage)'.format(diff[0])
                        elif diff[0] in (
                                lotr.CARD_ENGAGEMENT,
                                lotr.BACK_PREFIX + lotr.CARD_ENGAGEMENT):
                            diff[0] = '{} (Stage Letter)'.format(diff[0])
                    elif card[lotr.CARD_TYPE] in ('Presentation', 'Rules'):
                        if diff[0] in (lotr.CARD_VICTORY,
                                       lotr.BACK_PREFIX + lotr.CARD_VICTORY):
                            diff[0] = '{} (Page)'.format(diff[0])

                    diff[0] = diff[0].replace(lotr.BACK_PREFIX, '[Back] ')
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
                            message = (
                                'No free slots to create a new channel '
                                '"general" in category "{}"'.format(
                                    card[lotr.CARD_DISCORD_CATEGORY]))
                            logging.error(message)
                            create_mail(ERROR_SUBJECT_TEMPLATE.format(message))
                            if self.cron_channel:
                                await self._send_channel(self.cron_channel,
                                                         message)

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


    async def _process_set_name_changes(self, data):
        set_name_changes = data.get('set_names', {})
        if not set_name_changes:
            return

        for old_set_name, new_set_name in set_name_changes:
            old_folder_name = '{}.English'.format(
                lotr.escape_filename(old_set_name))
            new_folder_name = '{}.English'.format(
                lotr.escape_filename(new_set_name))
            stdout, stderr = await run_shell(
                RCLONE_COPY_CLOUD_FOLDER_CMD.format(old_folder_name,
                                                    new_folder_name))
            if (stdout or stderr) and 'directory not found' not in stderr:
                message = ('RClone failed (set names), stdout: {}, '
                           'stderr: {}'.format(stdout, stderr))
                logging.error(message)
                create_mail(ERROR_SUBJECT_TEMPLATE.format(message),
                            message)


    async def _process_set_changes(self, data):
        set_changes = data.get('sets', {})
        if not set_changes:
            return

        for key, card_ids in set_changes.items():
            parts = key.split('|')
            if len(parts) != 2:
                raise FormatError('Incorrect set change key: {}'.format(key))

            old_set_id, new_set_id = parts
            await self._move_artwork_files(card_ids, old_set_id, new_set_id)
            await self._copy_image_files(card_ids, old_set_id, new_set_id)


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
            message = 'Only {} channel slots remain'.format(slots)
            logging.warning(message)
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
                    message = (
                        'Card {} ({}) has a wrong channel category: {} '
                        'instead of {}'.format(
                            card[lotr.CARD_NAME],
                            card[lotr.CARD_DISCORD_CHANNEL],
                            channels[name]['category_name'],
                            card[lotr.CARD_DISCORD_CATEGORY]))
                    logging.warning(message)
                    create_mail(WARNING_SUBJECT_TEMPLATE.format(message))

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
        for i, chunk in enumerate(common.split_result(content)):
            if i > 0:
                await asyncio.sleep(1)

            message = await channel.send(chunk)
            if i == 0:
                first_message = message

        return first_message


    async def _process_cron_command(self, message):  #pylint: disable=R0912,R0915
        """ Process a cron command.
        """
        if message.content.lower() == '!cron':
            command = 'help'
        else:
            command = re.sub(r'^!cron ', '', message.content,
                             flags=re.IGNORECASE).split('\n')[0].strip()

        logging.info('Received cron command: %s', command)
        if command.lower().startswith('hello'):
            await self._send_channel(message.channel, 'hello')
        elif command.lower().startswith('test'):
            await self._send_channel(message.channel, 'passed')
        elif (command.lower().startswith('thank you') or
              command.lower().startswith('thanks')):
            await self._send_channel(message.channel, 'you are welcome')
        elif command.lower() == 'log':
            res, _ = await run_shell(CRON_LOG_CMD)
            if not res:
                res = 'no cron logs found'

            res = res.replace('_', '\\_').replace('*', '\\*')
            await self._send_channel(message.channel, res)
        elif command.lower() == 'dragncards build':
            try:
                lotr.trigger_dragncards_build(CONF)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, 'done')
        elif command.lower() == 'errors':
            res, _ = await run_shell(CRON_ERRORS_CMD)
            if not res:
                res = 'no cron logs found'

            res = res.replace('_', '\\_').replace('*', '\\*')
            await self._send_channel(message.channel, res)
        elif command.lower() == 'trigger':
            delete_sheet_checksums()
            await self._send_channel(message.channel, 'done')
        elif command.lower() == 'restart bot':
            await self._send_channel(message.channel, 'restarting...')
            try:
                await restart_bot()
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return
        elif command.lower() == 'restart cron':
            try:
                await restart_cron()
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, 'done')
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
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await self._send_channel(message.channel, error)
                return

            await self._send_channel(message.channel, 'done')
        elif command.lower() == 'view':
            try:
                res = await self._view_target()
                if not res:
                    res = 'no previous targets found'
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower().startswith('complete '):
            try:
                num = re.sub(r'^complete ', '', command, flags=re.IGNORECASE)
                user = message.author.display_name
                error = await self._complete_target(message.content, num, user,
                                                    message.jump_url)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await self._send_channel(message.channel, error)
                return

            await self._send_channel(message.channel, 'done')
        elif command.lower().startswith('update '):
            try:
                params = re.sub(r'^update ', '', command, flags=re.IGNORECASE
                               ).split(' ')
                error = await self._update_target(params)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await self._send_channel(message.channel, error)
                return

            await self._send_channel(message.channel, 'done')
        elif command.lower() == 'add':
            try:
                error = await self._add_target(message.content)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await self._send_channel(message.channel, error)
                return

            await self._send_channel(message.channel, 'done')
        elif command.lower().startswith('remove '):
            try:
                params = re.sub(r'^remove ', '', command, flags=re.IGNORECASE
                               ).split(' ')
                error = await self._remove_target(params)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await self._send_channel(message.channel, error)
                return

            await self._send_channel(message.channel, 'done')
        elif command.lower().startswith('random '):
            num = re.sub(r'^random ', '', command, flags=re.IGNORECASE)
            if lotr.is_positive_int(num):
                res = random.randint(1, int(num))
                await self._send_channel(message.channel, str(res))
            else:
                await self._send_channel(
                    message.channel,
                    '"{}" is not a positive integer'.format(num))
        else:
            res = HELP['playtest']
            await self._send_channel(message.channel, res)


    async def get_quests_stat(self, quest):  # pylint: disable=R0914
        """ Get statistics for all found quests.
        """
        data = await read_card_data()
        if quest.lower() in data['sets_by_code']:
            quest = data['sets_by_code'][quest.lower()].replace('ALeP - ', '')

        quest_folder = lotr.escape_filename(quest).lower()
        quest_file = lotr.escape_octgn_filename(quest_folder)
        set_folders = {lotr.escape_filename(s) for s in data['set_names']}
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


    async def _get_general_cards(self, category):
        """ Get IDs of all cards associated with a general channel.
        """
        data = await read_card_data()
        cards = [card[lotr.CARD_ID] for card in data['data']
                 if card.get(lotr.CARD_DISCORD_CATEGORY) == category
                 and not card.get(lotr.CARD_DISCORD_CHANNEL)]
        return cards


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

        if command.lower() == 'this' and message.channel.name == 'general':
            commands = await self._get_general_cards(
                message.channel.category.name)
            if not commands:
                await self._send_channel(message.channel, 'no cards found')
                return

            for command in commands:
                try:
                    res = await self._get_card(command, False)
                except Exception as exc:
                    logging.exception(str(exc))
                    await self._send_channel(
                        message.channel,
                        'unexpected error: {}'.format(str(exc)))
                    return

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
            await self._send_channel(
                message.channel,
                'unexpected error: {}'.format(str(exc)))
            return

        await self._send_channel(message.channel, res)


    def get_assistants(self):
        """ Get the list of Discord assistants.
        """
        ignore_assistants = {
            u.strip()
            for u in (CONF.get('ignore_assistants') or '').split(',')}
        add_assistants = [
            u.strip()
            for u in (CONF.get('add_assistants') or '').split(',')]
        assistants = [m.display_name for m in self.guilds[0].members
                     if m.display_name not in ignore_assistants]
        assistants.extend(add_assistants)
        assistants = [re.sub(r'[^\u0000-\uffff]+', '', u).strip()
                      for u in assistants]
        assistants = [re.sub(r'[,./<>?;\':"\[\]\|{}]$', '', u).strip()
                      for u in assistants]
        assistants = [u.replace('[', '[[').replace(']', ']]')
                      .replace('[[', '[lsb]').replace(']]', '[rsb]')
                      for u in assistants]
        assistants = [
            u.replace('(he/him)', '').replace('(she/her)', '').strip()
            for u in assistants]
        assistants = sorted(list(set(assistants)), key=str.casefold)
        assistants = ', '.join(assistants)
        return assistants


    async def _process_stat_command(self, message):  # pylint: disable=R0911.R0912,R0915
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
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'quest':
            await self._send_channel(message.channel,
                                     'please specify the quest name')
        elif command.lower() == 'channels':
            try:
                all_channels = await self.get_all_channels_safe()
                num = len(all_channels)
                res = 'There are {} channels and {} free slots'.format(
                    num, CHANNEL_LIMIT - num)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'assistants':
            try:
                res = self.get_assistants()
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            res = res.replace('_', '\\_').replace('*', '\\*')
            await self._send_channel(message.channel, res)
        elif command.lower() == 'dragncards build':
            await self._send_channel(message.channel, 'Please wait...')
            try:
                res = lotr.get_dragncards_build(CONF)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'player cards help':
            await self._send_channel(message.channel, HELP_STAT_PLAYER_CARDS)
        elif command.lower().startswith('player cards '):
            await self._send_channel(message.channel, 'Please wait...')
            try:
                set_name = re.sub(r'^player cards ', '', command,
                                  flags=re.IGNORECASE)
                start_date = ''
                parts = set_name.split(' ')
                if (len(parts) > 1 and
                        re.match(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$', parts[-1])):
                    try:
                        datetime.strptime(parts[-1], '%Y-%m-%d')
                    except ValueError:
                        pass
                    else:
                        start_date = parts[-1]
                        set_name = ' '.join(parts[:-1])

                res = await get_dragncards_player_cards_stat(set_name,
                                                             start_date)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'all plays help':
            await self._send_channel(message.channel, HELP_STAT_ALL_PLAYS)
        elif command.lower().startswith('all plays '):
            await self._send_channel(message.channel, 'Please wait...')
            try:
                quest = re.sub(r'^all plays ', '', command,
                               flags=re.IGNORECASE)
                start_date = ''
                parts = quest.split(' ')
                if (len(parts) > 1 and
                        re.match(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$', parts[-1])):
                    try:
                        datetime.strptime(parts[-1], '%Y-%m-%d')
                    except ValueError:
                        pass
                    else:
                        start_date = parts[-1]
                        quest = ' '.join(parts[:-1])

                res = await get_dragncards_all_plays(quest, start_date)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'plays help':
            await self._send_channel(message.channel, HELP_STAT_PLAYS)
        elif command.lower().startswith('plays '):
            await self._send_channel(message.channel, 'Please wait...')
            try:
                quest = re.sub(r'^plays ', '', command,
                               flags=re.IGNORECASE)
                start_date = ''
                parts = quest.split(' ')
                if (len(parts) > 1 and
                        re.match(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$', parts[-1])):
                    try:
                        datetime.strptime(parts[-1], '%Y-%m-%d')
                    except ValueError:
                        pass
                    else:
                        start_date = parts[-1]
                        quest = ' '.join(parts[:-1])

                res = await get_dragncards_plays_stat(quest, start_date)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'quests help':
            await self._send_channel(message.channel, HELP_STAT_QUESTS)
        elif (command.lower() == 'quests' or
              command.lower().startswith('quests ')):
            await self._send_channel(message.channel, 'Please wait...')
            try:
                start_date = re.sub(r'^quests ?', '', command,
                                    flags=re.IGNORECASE)
                if start_date:
                    if not re.match(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$',
                                    start_date):
                        res = 'incorrect date format'
                    else:
                        try:
                            datetime.strptime(start_date, '%Y-%m-%d')
                        except ValueError:
                            res = 'incorrect date format'
                        else:
                            res = await get_dragncards_quests_stat(start_date)
                else:
                    res = await get_dragncards_quests_stat('')
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        else:
            res = HELP['stat']
            await self._send_channel(message.channel, res)


    async def _process_secret_command(self, message):
        """ Process a secret command.
        """
        command = re.sub(r'^!secret ', '', message.content,
                         flags=re.IGNORECASE).split('\n')[0].strip()

        logging.info('Received secret command: %s', command)

        if command.lower() == 'image refresh':
            await message.delete()
            RENDERED_IMAGES.clear()
            clear_rendered_images()
        elif command.lower() == 'users':
            await message.delete()
            try:
                await self._prepare_users_list()
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error happened, see the log')
                return

            await self._send_channel(message.channel, 'done')


    async def _prepare_users_list(self):  # pylint: disable=R0914
        """ Prepare a list of all Discord users and save it in the CSV file.

        """
        ignore_users = {
            u.strip() for u in (CONF.get('ignore_users') or '').split(',')}
        role_names = sorted([r.name.replace(' Assistant', '')
                             for r in self.guilds[0].roles
                             if r.name.endswith(' Assistant')])

        messages = {}
        for channel in self.guilds[0].text_channels:
            async for message in channel.history(limit=None):
                created = message.created_at.strftime('%Y-%m-%d')
                if created > messages.get(message.author.id, ('', ''))[0]:
                    messages[message.author.id] = (created, channel.name)

        members = self.guilds[0].members
        rows = []
        for member in members:
            if (member.bot or member.system or
                    member.display_name in ignore_users):
                continue

            if member.display_name == member.name:
                name = member.display_name
            else:
                name = '{} [{}]'.format(member.display_name, member.name)

            row = {
                'name': name,
                'joined': member.joined_at.strftime('%Y-%m-%d'),
                'last message date': messages.get(member.id, ('', ''))[0],
                'last message channel': messages.get(member.id, ('', ''))[1]
                }

            for role in member.roles:
                role_name = role.name.replace(' Assistant', '')
                if role_name in role_names:
                    row[role_name] = 1

            rows.append(row)

        rows.sort(key=lambda r: r['name'].lower())
        with open(USERS_LIST_PATH, 'w', newline='', encoding='utf-8') as obj:
            obj.write(codecs.BOM_UTF8.decode('utf-8'))
            fieldnames = ['name', 'joined', 'last message date',
                          'last message channel']
            fieldnames.extend(role_names)
            writer = csv.DictWriter(obj, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)


    async def _display_artwork(self, message, card_id, channel_id):  # pylint: disable=R0911,R0912,R0914,R0915
        """ Display all artwork images kept for the card.
        """
        data = await read_card_data()
        if card_id:
            if card_id not in data['artwork_ids']:
                return 'card id not found or is locked'
        elif channel_id:
            channel_name = self.get_channel_name_by_id(channel_id)
            if not channel_name:
                return 'card channel not found'

            matches = [
                card for card in data['data']
                if card.get(lotr.CARD_DISCORD_CHANNEL, '') == channel_name]
            if not matches:
                return 'no card found for the channel'

            card = matches[0]
            if card.get(lotr.CARD_SET_LOCKED):
                return 'set {} is locked for modifications'.format(
                    card[lotr.CARD_SET_NAME])

            card_id = card[lotr.CARD_ID]
        else:
            channel_name = message.channel.name
            matches = [
                card for card in data['data']
                if card.get(lotr.CARD_DISCORD_CHANNEL, '') == channel_name]
            if not matches:
                return 'no card found for this channel'

            card = matches[0]
            if card.get(lotr.CARD_SET_LOCKED):
                return 'set {} is locked for modifications'.format(
                    card[lotr.CARD_SET_NAME])

            card_id = card[lotr.CARD_ID]

        artwork_destination_path = CONF.get('artwork_destination_path')
        if not artwork_destination_path:
            raise RCloneFolderError('no artwork folder specified on the '
                                    'server')

        artwork_path = CONF.get('artwork_path')
        if not artwork_path:
            raise RCloneFolderError('no artwork folder specified on the '
                                    'server')

        found_images = set()
        local_folder = os.path.join(artwork_destination_path, KEEP_FOLDER,
                                    card_id)
        async with art_lock:
            if os.path.exists(local_folder):
                for _, _, filenames in os.walk(local_folder):
                    for filename in filenames:
                        if (not filename.endswith('.png') and
                                not filename.endswith('.jpg')):
                            continue

                        found_images.add(filename)
                        path = os.path.join(local_folder, filename)
                        await message.channel.send(file=discord.File(path))
                        artist = ' '.join(
                            '.'.join(filename.split('.')[:-1]).split('_')[1:])
                        await self._send_channel(message.channel,
                                                 'Artist: {}'.format(artist))

                    break

        root_folder = os.path.join(artwork_path, KEEP_FOLDER)
        folder = os.path.join(root_folder, card_id)
        async with art_lock:
            if not os.path.exists(root_folder):
                os.mkdir(root_folder)

            if not os.path.exists(folder):
                os.mkdir(folder)

        _, _ = await run_shell(
            RCLONE_COPY_KEEP_ART_CMD.format(KEEP_FOLDER, card_id, artwork_path,
                                            KEEP_FOLDER, card_id))
        for _, _, filenames in os.walk(folder):
            for filename in filenames:
                if filename in found_images:
                    continue

                if (not filename.endswith('.png') and not
                        filename.endswith('.jpg')):
                    continue

                found_images.add(filename)
                path = os.path.join(folder, filename)
                await message.channel.send(file=discord.File(path))
                artist = ' '.join(
                    '.'.join(filename.split('.')[:-1]).split('_')[1:])
                await self._send_channel(message.channel,
                                         'Artist: {}'.format(artist))

            break

        async with art_lock:
            shutil.rmtree(folder, ignore_errors=True)

        if not found_images:
            return 'no artwork images found'

        return ''


    async def _keep_artwork(self, message, artist, card_id, channel_id):  # pylint: disable=R0911,R0912,R0914,R0915
        """ Keep an artwork image for the card.
        """
        data = await read_card_data()
        if card_id:
            if card_id not in data['artwork_ids']:
                return 'card id not found or is locked'
        elif channel_id:
            channel_name = self.get_channel_name_by_id(channel_id)
            if not channel_name:
                return 'card channel not found'

            matches = [
                card for card in data['data']
                if card.get(lotr.CARD_DISCORD_CHANNEL, '') == channel_name]
            if not matches:
                return 'no card found for the channel'

            card = matches[0]
            if card.get(lotr.CARD_SET_LOCKED):
                return 'set {} is locked for modifications'.format(
                    card[lotr.CARD_SET_NAME])

            card_id = card[lotr.CARD_ID]
        else:
            channel_name = message.channel.name
            matches = [
                card for card in data['data']
                if card.get(lotr.CARD_DISCORD_CHANNEL, '') == channel_name]
            if not matches:
                return 'no card found for this channel'

            card = matches[0]
            if card.get(lotr.CARD_SET_LOCKED):
                return 'set {} is locked for modifications'.format(
                    card[lotr.CARD_SET_NAME])

            card_id = card[lotr.CARD_ID]

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
        root_folder = os.path.join(artwork_destination_path, KEEP_FOLDER)
        folder = os.path.join(root_folder, card_id)
        filename = '{}_{}.{}'.format(uuid.uuid4(), artist, filetype)
        filename = filename.replace(' ', '_')
        path = os.path.join(folder, filename)

        async with art_lock:
            if not os.path.exists(root_folder):
                os.mkdir(root_folder)

            if not os.path.exists(folder):
                os.mkdir(folder)

            with open(path, 'wb') as f_obj:
                f_obj.write(content)

            self.rclone_art = True

        return ''

    async def _save_artwork(self, message, side, artist, card_id,  # pylint: disable=R0911,R0912,R0913,R0914,R0915
                            channel_id):
        """ Save an artwork image for the card.
        """
        data = await read_card_data()
        if card_id:
            if card_id not in data['artwork_ids']:
                return 'card id not found or is locked'

            card = data['artwork_ids'][card_id]
            card[lotr.CARD_ID] = card_id
        elif channel_id:
            channel_name = self.get_channel_name_by_id(channel_id)
            if not channel_name:
                return 'card channel not found'

            matches = [
                card for card in data['data']
                if card.get(lotr.CARD_DISCORD_CHANNEL, '') == channel_name]
            if not matches:
                return 'no card found for the channel'

            card = matches[0]
            if card.get(lotr.CARD_SET_LOCKED):
                return 'set {} is locked for modifications'.format(
                    card[lotr.CARD_SET_NAME])
        else:
            channel_name = message.channel.name
            matches = [
                card for card in data['data']
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

        async with generate_lock:
            await self._generate_artwork(card, filetype, side, content)

            if (side == 'A' and card.get(lotr.BACK_PREFIX + lotr.CARD_NAME) and
                    (card[lotr.CARD_TYPE] == 'Quest' or
                     card[lotr.CARD_TYPE] == card.get(
                         lotr.BACK_PREFIX + lotr.CARD_TYPE) == 'Contract')):
                await self._generate_artwork(card, filetype, 'B', content)

        return ''


    async def _generate_artwork(self, card, filetype, side, content):  # pylint: disable=R0914
        """ Generate light-weight artwork for the card.
        """
        if side == 'A':
            card_type = card[lotr.CARD_TYPE]
        else:
            card_type = card.get(lotr.BACK_PREFIX + lotr.CARD_TYPE, '')

        portrait = PORTRAIT.get(card_type)
        if not portrait:
            return

        filename = '{}{}.temp.{}'.format(card[lotr.CARD_ID],
                                         side == 'B' and '.B' or '',
                                         filetype)
        path = os.path.join(TEMP_PATH, filename)
        output_filename = re.sub(r'\.temp\.(?:jpg|png)$', '.jpg', filename)
        output_path = os.path.join(TEMP_PATH, output_filename)
        destination_path = os.path.join(lotr.RENDERER_GENERATED_IMAGES_PATH,
                                        output_filename)
        with open(path, 'wb') as f_obj:
            f_obj.write(content)

        portrait = portrait.split(',')
        width = float(round(int(portrait[2]) * 2 / 1.75))
        height = float(round(int(portrait[3]) * 2 / 1.75))
        max_dim = max(width, height)
        command = MAGICK_GENERATE_CMD.format(
            max_dim, max_dim, max_dim, max_dim, width, height, path,
            output_path)
        stdout, stderr = await run_shell(command)

        if os.path.exists(output_path):
            logging.info('Generated light-weight artwork file: %s', filename)
            stdout, stderr = await run_shell(
                RCLONE_GENERATED_CMD.format(output_path))
            if stdout or stderr:
                message = (
                    'RClone failed (generated artwork), stdout: {}, stderr: {}'
                    .format(stdout, stderr))
                logging.error(message)
                create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)

            shutil.move(output_path, destination_path)
            try:
                with open(lotr.EXPIRE_DRAGNCARDS_JSON_PATH, 'r',
                          encoding='utf-8') as fobj:
                    expired_hashes = json.load(fobj)
            except Exception:
                expired_hashes = []

            expired_hashes.append(card[lotr.CARD_ID])

            with open(lotr.EXPIRE_DRAGNCARDS_JSON_PATH, 'w',
                      encoding='utf-8') as fobj:
                json.dump(expired_hashes, fobj)

            delete_sheet_checksums()
        else:
            message = ('Command "{}" failed, stdout: {}, stderr: {}'
                       .format(command, stdout, stderr))
            logging.error(message)
            create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)

        if os.path.exists(path):
            os.remove(path)


    async def _save_scratch_artwork(self, message, artist):
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
            RCLONE_RENDERED_FOLDER_CMD.format(set_folder))
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


    async def _move_artwork_files(self, card_ids, old_set_id, new_set_id):
        """ Move artwork files for the cards.
        """
        if old_set_id == new_set_id:
            return

        async with rclone_art_lock:
            await self._rclone_art()

        filenames = await self._get_artwork_files(old_set_id)
        for filename in filenames:
            if filename.split('_')[0] not in card_ids:
                continue

            stdout, stderr = await run_shell(
                RCLONE_MOVE_CLOUD_ART_CMD.format(
                    old_set_id, filename, new_set_id))
            if stdout or stderr:
                message = ('RClone failed (artwork), stdout: {}, stderr: {}'
                           .format(stdout, stderr))
                logging.error(message)
                create_mail(ERROR_SUBJECT_TEMPLATE.format(message), message)
                break


    async def _copy_image_files(self, card_ids, old_set_id, new_set_id):
        """ Copy rendered images for the card.
        """
        data = await read_card_data()
        if (old_set_id not in data['sets_by_id'] or
                new_set_id not in data['sets_by_id']):
            return

        old_set_folder = '{}.English'.format(
            lotr.escape_filename(data['sets_by_id'][old_set_id]))
        new_set_folder = '{}.English'.format(
            lotr.escape_filename(data['sets_by_id'][new_set_id]))

        filenames = await self._get_image_files(old_set_folder)
        for filename in filenames:
            if re.sub(r'(?:\-2)?\.png$', '', filename)[-36:] not in card_ids:
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
            lotr.normalized_name(card[lotr.CARD_SET_NAME])) == set_name and
            card[lotr.CARD_TYPE] not in ('Presentation', 'Rules')]

        if not matches:
            new_set_name = 'the-{}'.format(set_name)
            matches = [card for card in data['data'] if re.sub(
                r'^alep---', '',
                lotr.normalized_name(card[lotr.CARD_SET_NAME])) == new_set_name
                and card[lotr.CARD_TYPE] not in ('Presentation', 'Rules')]

        if not matches:
            set_code = value.lower()
            matches = [
                card for card in data['data']
                if card.get(lotr.CARD_SET_HOB_CODE, '').lower() == set_code and
                card[lotr.CARD_TYPE] not in ('Presentation', 'Rules')]
            if not matches:
                return 'no cards found for the set'

        matches.sort(key=lambda card: card[lotr.ROW_COLUMN])
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
                     not lotr.is_doubleside(
                         card.get(lotr.CARD_TYPE),
                         card.get(lotr.BACK_PREFIX + lotr.CARD_TYPE)))):
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
            lotr.normalized_name(card[lotr.CARD_SET_NAME])) == set_name and
            card[lotr.CARD_TYPE] not in ('Presentation', 'Rules')]
        if not matches:
            new_set_name = 'the-{}'.format(set_name)
            matches = [card for card in data['data'] if re.sub(
                r'^alep---', '',
                lotr.normalized_name(card[lotr.CARD_SET_NAME])) == new_set_name
                and card[lotr.CARD_TYPE] not in ('Presentation', 'Rules')]

        if not matches:
            set_code = value.lower()
            matches = [
                card for card in data['data']
                if card.get(lotr.CARD_SET_HOB_CODE, '').lower() == set_code and
                card[lotr.CARD_TYPE] not in ('Presentation', 'Rules')]
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
        elif message.content.lower() == '!asm':
            command = 'save Midjourney'
        elif message.content.lower() == '!asbm':
            command = 'saveb Midjourney'
        else:
            command = re.sub(r'^!art ', '', message.content,
                             flags=re.IGNORECASE).split('\n')[0].strip()

        logging.info('Received art command: %s', command)

        if (command.lower().startswith('keep ') or
                (command.lower() == 'keep' and message.reference and
                 message.reference.resolved)):
            try:
                if command.lower() == 'keep':
                    await self._send_channel(message.channel,
                                             'assuming Midjourney artist')
                    artist = 'Midjourney'
                else:
                    artist = re.sub(r'^keep ', '', command, flags=re.IGNORECASE)

                if re.match(lotr.UUID_REGEX, artist):
                    if message.reference and message.reference.resolved:
                        await self._send_channel(message.channel,
                                                 'assuming Midjourney artist')
                        card_id = artist
                        artist = 'Midjourney'
                        error = await self._keep_artwork(message, artist,
                                                         card_id, None)
                    else:
                        card_id = artist
                        error = await self._display_artwork(message, card_id,
                                                            None)
                elif re.match(CHANNEL_ID_REGEX, artist):
                    if message.reference and message.reference.resolved:
                        await self._send_channel(message.channel,
                                                 'assuming Midjourney artist')
                        channel_id = int(artist[2:-1])
                        artist = 'Midjourney'
                        error = await self._keep_artwork(message, artist, None,
                                                         channel_id)
                    else:
                        channel_id = int(artist[2:-1])
                        error = await self._display_artwork(message, None,
                                                            channel_id)
                else:
                    parts = artist.split(' ')
                    if len(parts) > 1 and re.match(lotr.UUID_REGEX, parts[0]):
                        card_id = parts[0]
                        channel_id = None
                        artist = ' '.join(parts[1:])
                    elif (len(parts) > 1 and re.match(CHANNEL_ID_REGEX,
                                                      parts[0])):
                        card_id = None
                        channel_id = int(parts[0][2:-1])
                        artist = ' '.join(parts[1:])
                    else:
                        card_id = None
                        channel_id = None

                    error = await self._keep_artwork(message, artist, card_id,
                                                     channel_id)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await self._send_channel(message.channel, error)
                return

            await self._send_channel(message.channel, 'done')
        elif command.lower() == 'keep':
            try:
                error = await self._display_artwork(message, None, None)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await self._send_channel(message.channel, error)
                return

            await self._send_channel(message.channel, 'done')
        elif (command.lower() == 'save' or command.lower() == 'saveb' or
              command.lower().startswith('save ') or
              command.lower().startswith('saveb ')):
            try:
                side = 'B' if (command.lower() == 'saveb' or
                               command.lower().startswith('saveb ')) else 'A'
                if command.lower() == 'save' or command.lower() == 'saveb':
                    await self._send_channel(message.channel,
                                             'assuming Midjourney artist')
                    artist = 'Midjourney'
                else:
                    artist = re.sub(r'^saveb? ', '', command,
                                    flags=re.IGNORECASE)
                    if (re.match(lotr.UUID_REGEX, artist) or
                            re.match(CHANNEL_ID_REGEX, artist)):
                        await self._send_channel(message.channel,
                                                 'assuming Midjourney artist')
                        artist = '{} Midjourney'.format(artist)

                parts = artist.split(' ')
                if len(parts) > 1 and re.match(lotr.UUID_REGEX, parts[0]):
                    card_id = parts[0]
                    channel_id = None
                    artist = ' '.join(parts[1:])
                elif len(parts) > 1 and re.match(CHANNEL_ID_REGEX, parts[0]):
                    card_id = None
                    channel_id = int(parts[0][2:-1])
                    artist = ' '.join(parts[1:])
                else:
                    card_id = None
                    channel_id = None

                error = await self._save_artwork(message, side, artist,
                                                 card_id, channel_id)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await self._send_channel(message.channel, error)
                return

            await self._send_channel(message.channel, 'done')
        elif (command.lower() == 'savescr' or
              command.lower().startswith('savescr ')):
            try:
                if command.lower() == 'savescr':
                    await self._send_channel(message.channel,
                                             'assuming Midjourney artist')
                    artist = 'Midjourney'
                else:
                    artist = re.sub(r'^savescr ', '', command,
                                    flags=re.IGNORECASE)

                error = await self._save_scratch_artwork(message, artist)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await self._send_channel(message.channel, error)
                return

            await self._send_channel(message.channel, 'done')
        elif command.lower().startswith('verify '):
            await self._send_channel(message.channel, 'Please wait...')
            try:
                set_name = re.sub(r'^verify ', '', command,
                                  flags=re.IGNORECASE)
                res = await self._verify_artwork(set_name)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'verify':
            await self._send_channel(message.channel, 'please specify the set')
        elif command.lower().startswith('artists '):
            await self._send_channel(message.channel, 'Please wait...')
            try:
                set_name = re.sub(r'^artists ', '', command,
                                  flags=re.IGNORECASE)
                res = await self._artwork_artists(set_name)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'artists':
            await self._send_channel(message.channel, 'please specify the set')
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
            new_set_name = 'the-{}'.format(set_name)
            matches = [card for card in data['data'] if re.sub(
                r'^alep---', '',
                lotr.normalized_name(card[lotr.CARD_SET_NAME])) ==
                new_set_name]

        if not matches:
            set_code = value.lower()
            matches = [
                card for card in data['data']
                if card.get(lotr.CARD_SET_HOB_CODE, '').lower() == set_code]

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

                        await self._send_channel(
                            channel,
                            "Can't download the image from Google Drive")
                        continue

                await channel.send(file=discord.File(image_path))

            modified_time = download_time or max(modified_times)
            if (card[lotr.CARD_ID] in TIMESTAMPS['data'] and
                    TIMESTAMPS['data'][card[lotr.CARD_ID]] > modified_time):
                await self._send_channel(
                    channel,
                    'Last modified: {} UTC (**Card text was probably '
                    'changed since that time**)'.format(modified_time))
            else:
                await self._send_channel(
                    channel,
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
            await self._send_channel(
                channel,
                'Last modified: {} UTC (**Card text was probably '
                'changed since that time**)'.format(modified_time))
        else:
            await self._send_channel(
                channel,
                'Last modified: {} UTC'.format(modified_time))

        return None


    async def _process_image_command(self, message):  # pylint: disable=R0912,R0915
        """ Process an image command.
        """
        if message.content.lower() == '!image':
            command = 'help'
        else:
            command = re.sub(r'^!image ', '', message.content,
                             flags=re.IGNORECASE).split('\n')[0].strip()

        logging.info('Received image command: %s', command)

        if command.lower().startswith('set '):
            await self._send_channel(message.channel, 'Please wait...')
            try:
                set_name = re.sub(r'^set ', '', command,
                                  flags=re.IGNORECASE)
                res = await self._post_rendered_set(set_name)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'set':
            await self._send_channel(message.channel, 'please specify the set')
        elif command.lower() == 'refresh':
            RENDERED_IMAGES.clear()
            clear_rendered_images()
            await self._send_channel(message.channel, 'done')
        elif command.lower() == 'card':
            await self._send_channel(message.channel,
                                     'please specify the card')
        elif command.lower() == 'help':
            res = HELP['image']
            await self._send_channel(message.channel, res)
        elif (re.sub(r'^card ', '', command,
                     flags=re.IGNORECASE).lower() == 'this' and
              message.channel.name == 'general'):
            await self._send_channel(message.channel, 'Please wait...')
            commands = await self._get_general_cards(
                message.channel.category.name)
            if not commands:
                await self._send_channel(message.channel, 'no cards found')
                return

            for command in commands:
                try:
                    res = await self._post_rendered_card(message.channel,
                                                         command, False)
                except Exception as exc:
                    logging.exception(str(exc))
                    await self._send_channel(
                        message.channel,
                        'unexpected error: {}'.format(str(exc)))
                    return

                if res:
                    await self._send_channel(message.channel, res)
        else:
            await self._send_channel(message.channel, 'Please wait...')
            command = re.sub(r'^card ', '', command, flags=re.IGNORECASE)
            if command.lower() == 'this':
                command = message.channel.name
                this = True
            else:
                this = False

            try:
                res = await self._post_rendered_card(message.channel,
                                                     command, this)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            if res:
                await self._send_channel(message.channel, res)


    async def _display_flavour(self, value):
        """ Display possible flavour text issues for a set.
        """
        data = await read_card_data()

        set_name = re.sub(r'^alep---', '', lotr.normalized_name(value))
        matches = [card for card in data['data'] if re.sub(
            r'^alep---', '',
            lotr.normalized_name(card[lotr.CARD_SET_NAME])) == set_name]

        if not matches:
            new_set_name = 'the-{}'.format(set_name)
            matches = [card for card in data['data'] if re.sub(
                r'^alep---', '',
                lotr.normalized_name(card[lotr.CARD_SET_NAME])) ==
                new_set_name]

        if not matches:
            set_code = value.lower()
            matches = [
                card for card in data['data']
                if card.get(lotr.CARD_SET_HOB_CODE, '').lower() == set_code]
            if not matches:
                return 'no cards found for the set'

        matches.sort(key=lambda card: card[lotr.ROW_COLUMN])
        res = {}
        for card in matches:
            if card.get(lotr.CARD_FLAVOUR) is not None:
                get_flavour_errors(
                    card[lotr.CARD_FLAVOUR], lotr.CARD_FLAVOUR, card, res)

            if card.get(lotr.BACK_PREFIX + lotr.CARD_FLAVOUR) is not None:
                get_flavour_errors(
                    card[lotr.BACK_PREFIX + lotr.CARD_FLAVOUR],
                         lotr.BACK_PREFIX + lotr.CARD_FLAVOUR, card, res)

        output = []
        for rule, card_list in res.items():
            rule_output = (
                '\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\n**{}**:\n'
                '\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_'.format(rule))
            for card_data in card_list:
                row_url = '<{}&range=A{}>'.format(data['url'],
                                                  card_data['row'])
                rule_output += '\n` `\n*{}* (**{}**):\n{}\n{}'.format(
                    card_data['name'], card_data['field'].replace('_', ' '),
                    card_data['text'], row_url)

            output.append(rule_output)

        output = '\n` `\n'.join(sorted(output))
        if output:
            output = '{}\n` `\nDone.'.format(output)
        else:
            output = 'no flavour text issues found'

        return output


    async def _display_names(self, value):
        """ Display potentially unknown or misspelled names for a set.
        """
        data = await read_card_data()

        set_name = re.sub(r'^alep---', '', lotr.normalized_name(value))
        matches = [card for card in data['data'] if re.sub(
            r'^alep---', '',
            lotr.normalized_name(card[lotr.CARD_SET_NAME])) == set_name and
            card[lotr.CARD_TYPE] != 'Presentation' and
            card.get(lotr.CARD_SPHERE) != 'Back']

        if not matches:
            new_set_name = 'the-{}'.format(set_name)
            matches = [card for card in data['data'] if re.sub(
                r'^alep---', '',
                lotr.normalized_name(card[lotr.CARD_SET_NAME])) == new_set_name
                and card[lotr.CARD_TYPE] != 'Presentation'
                and card.get(lotr.CARD_SPHERE) != 'Back']

        if not matches:
            set_code = value.lower()
            matches = [
                card for card in data['data']
                if card.get(lotr.CARD_SET_HOB_CODE, '').lower() == set_code and
                card[lotr.CARD_TYPE] != 'Presentation' and
                card.get(lotr.CARD_SPHERE) != 'Back']
            if not matches:
                return 'no cards found for the set'

        matches.sort(key=lambda card: card[lotr.ROW_COLUMN])
        res = {}
        for card in matches:
            if card.get(lotr.CARD_TEXT) is not None:
                get_unknown_names(
                    card[lotr.CARD_TEXT], lotr.CARD_TEXT, card, res,
                    data['card_names'], data['set_and_quest_names'],
                    data['encounter_set_names'])

            if card.get(lotr.BACK_PREFIX + lotr.CARD_TEXT) is not None:
                get_unknown_names(
                    card[lotr.BACK_PREFIX + lotr.CARD_TEXT],
                         lotr.BACK_PREFIX + lotr.CARD_TEXT, card, res,
                         data['card_names'], data['set_and_quest_names'],
                         data['encounter_set_names'])

            if card.get(lotr.CARD_SHADOW) is not None:
                get_unknown_names(
                    card[lotr.CARD_SHADOW], lotr.CARD_SHADOW, card, res,
                    data['card_names'], data['set_and_quest_names'],
                    data['encounter_set_names'])

            if card.get(lotr.BACK_PREFIX + lotr.CARD_SHADOW) is not None:
                get_unknown_names(
                    card[lotr.BACK_PREFIX + lotr.CARD_SHADOW],
                         lotr.BACK_PREFIX + lotr.CARD_SHADOW, card, res,
                         data['card_names'], data['set_and_quest_names'],
                         data['encounter_set_names'])

        output = []
        for rule, card_list in res.items():
            rule_output = (
                '\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\n**{}**:\n'
                '\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_'.format(rule))
            for card_data in card_list:
                row_url = '<{}&range=A{}>'.format(data['url'],
                                                  card_data['row'])
                rule_output += '\n` `\n*{}* (**{}**):\n{}\n{}'.format(
                    card_data['name'], card_data['field'].replace('_', ' '),
                    card_data['text'], row_url)

            output.append(rule_output)

        output = '\n` `\n'.join(sorted(output))
        if output:
            output = '{}\n` `\nDone.'.format(output)
        else:
            output = 'no unknown names found'

        return output


    async def _display_numbers(self, value):  # pylint: disable=R0912,R0914,R0915
        """ Display potentially incorrect card numbers for a set.
        """
        data = await read_card_data()

        set_name = re.sub(r'^alep---', '', lotr.normalized_name(value))
        matches = [card for card in data['data'] if re.sub(
            r'^alep---', '',
            lotr.normalized_name(card[lotr.CARD_SET_NAME])) == set_name]

        if not matches:
            new_set_name = 'the-{}'.format(set_name)
            matches = [card for card in data['data'] if re.sub(
                r'^alep---', '',
                lotr.normalized_name(card[lotr.CARD_SET_NAME])) ==
                new_set_name]

        if not matches:
            set_code = value.lower()
            matches = [
                card for card in data['data']
                if card.get(lotr.CARD_SET_HOB_CODE, '').lower() == set_code]
            if not matches:
                return 'no cards found for the set'

        matches.sort(key=lambda card: card[lotr.ROW_COLUMN])
        res = {}
        state = 'intro'  # intro|cards|outro
        next_intro_number = '0.1'
        next_cards_number = None
        intro_type_order = [None, 'Presentation', 'Rules', 'Hero']
        last_intro_type = None
        for card in matches:
            if (card[lotr.CARD_TYPE] == 'Presentation' or
                    (card[lotr.CARD_TYPE] == 'Rules' and
                     card.get(lotr.CARD_SPHERE) != 'Back') or
                    'Promo' in lotr.extract_flags(card.get(lotr.CARD_FLAGS))):
                if state != 'intro':
                    precedent = {
                        'name': card[lotr.CARD_NAME],
                        'field': 'card order',
                        'text': '{} cards should be put before other cards'
                            .format('Promo Hero'
                                    if card[lotr.CARD_TYPE] == 'Hero'
                                    else card[lotr.CARD_TYPE]),
                        'row': card[lotr.ROW_COLUMN]}
                    res.setdefault(
                        'Card is out of place', []).append(precedent)
                else:
                    if (card[lotr.CARD_TYPE] in intro_type_order and
                          intro_type_order.index(card[lotr.CARD_TYPE]) <
                          intro_type_order.index(last_intro_type)):
                        precedent = {
                            'name': card[lotr.CARD_NAME],
                            'field': 'card order',
                            'text': '{} cards should be put before {} cards'
                                .format(card[lotr.CARD_TYPE], last_intro_type),
                            'row': card[lotr.ROW_COLUMN]}
                        res.setdefault(
                            'Card is out of place', []).append(precedent)

                    if str(card[lotr.CARD_NUMBER]) != next_intro_number:
                        precedent = {
                            'name': card[lotr.CARD_NAME],
                            'field': lotr.CARD_NUMBER,
                            'text': 'Should be **{}** instead of **{}**'
                                .format(next_intro_number,
                                        card[lotr.CARD_NUMBER]),
                            'row': card[lotr.ROW_COLUMN]}
                        res.setdefault(
                            'Incorrect card number', []).append(precedent)

                    next_intro_number = get_next_card_number(
                        card[lotr.CARD_NUMBER])
                    if card[lotr.CARD_TYPE] in intro_type_order:
                        last_intro_type = card[lotr.CARD_TYPE]
            elif card.get(lotr.CARD_SPHERE) == 'Back':
                if str(card[lotr.CARD_NUMBER]) != '999':
                    precedent = {
                        'name': card[lotr.CARD_NAME],
                        'field': lotr.CARD_NUMBER,
                        'text': 'Should be **999** instead of **{}**'.format(
                            card[lotr.CARD_NUMBER]),
                        'row': card[lotr.ROW_COLUMN]}
                    res.setdefault(
                        'Incorrect card number', []).append(precedent)

                state = 'outro'
            else:
                if state not in ('intro', 'cards'):
                    precedent = {
                        'name': card[lotr.CARD_NAME],
                        'field': 'card order',
                        'text': 'Should be put before the back card',
                        'row': card[lotr.ROW_COLUMN]}
                    res.setdefault(
                        'Card is out of place', []).append(precedent)
                elif (not next_cards_number and
                      not lotr.is_positive_int(card[lotr.CARD_NUMBER])):
                    precedent = {
                        'name': card[lotr.CARD_NAME],
                        'field': lotr.CARD_NUMBER,
                        'text': '**{}** is an incorrect card number'.format(
                            card[lotr.CARD_NUMBER]),
                        'row': card[lotr.ROW_COLUMN]}
                    res.setdefault(
                        'Incorrect card number', []).append(precedent)
                    state = 'cards'
                elif (next_cards_number and
                      str(card[lotr.CARD_NUMBER]) != next_cards_number):
                    precedent = {
                        'name': card[lotr.CARD_NAME],
                        'field': lotr.CARD_NUMBER,
                        'text': 'Should be **{}** instead of **{}**'.format(
                            next_cards_number, card[lotr.CARD_NUMBER]),
                        'row': card[lotr.ROW_COLUMN]}
                    res.setdefault(
                        'Incorrect card number', []).append(precedent)
                    next_cards_number = get_next_card_number(
                        card[lotr.CARD_NUMBER])
                    state = 'cards'
                else:
                    next_cards_number = get_next_card_number(
                        card[lotr.CARD_NUMBER])
                    state = 'cards'

        output = []
        for rule, card_list in res.items():
            rule_output = (
                '\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\n**{}**:\n'
                '\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_'.format(rule))
            for card_data in card_list:
                row_url = '<{}&range=A{}>'.format(data['url'],
                                                  card_data['row'])
                rule_output += '\n` `\n*{}* (**{}**):\n{}\n{}'.format(
                    card_data['name'], card_data['field'].replace('_', ' '),
                    card_data['text'], row_url)

            output.append(rule_output)

        output = '\n` `\n'.join(sorted(output))
        if output:
            output = '{}\n` `\nDone.'.format(output)
        else:
            output = 'card numbers are correct'

        return output


    async def _display_quests(self, value):  # pylint: disable=R0912,R0914
        """ Display possible quest issues for a set.
        """
        data = await read_card_data()

        set_name = re.sub(r'^alep---', '', lotr.normalized_name(value))
        matches = [card for card in data['data'] if re.sub(
            r'^alep---', '',
            lotr.normalized_name(card[lotr.CARD_SET_NAME])) == set_name]

        if not matches:
            new_set_name = 'the-{}'.format(set_name)
            matches = [card for card in data['data'] if re.sub(
                r'^alep---', '',
                lotr.normalized_name(card[lotr.CARD_SET_NAME])) ==
                new_set_name]

        if not matches:
            set_code = value.lower()
            matches = [
                card for card in data['data']
                if card.get(lotr.CARD_SET_HOB_CODE, '').lower() == set_code]
            if not matches:
                return 'no cards found for the set'

        matches.sort(key=lambda card: card[lotr.ROW_COLUMN])
        res = {}
        quest_sets = {}
        for card in matches:
            if (card[lotr.CARD_TYPE] != 'Campaign' and
                    card.get(lotr.CARD_ENCOUNTER_SET) and
                    card.get(lotr.CARD_ADVENTURE) and
                    card[lotr.CARD_ENCOUNTER_SET] !=
                    card[lotr.CARD_ADVENTURE]):
                precedent = {
                    'name': card[lotr.CARD_NAME],
                    'field': lotr.CARD_ADVENTURE,
                    'text': 'Encounter set is "{}" and adventure is "{}"'
                        .format(card[lotr.CARD_ENCOUNTER_SET],
                                card[lotr.CARD_ADVENTURE]),
                    'row': card[lotr.ROW_COLUMN]}
                res.setdefault(
                    'Different encounter set and adventure values', []
                    ).append(precedent)

            if card[lotr.CARD_TYPE] == 'Quest':
                if card.get(lotr.CARD_ENCOUNTER_SET) in quest_sets:
                    if (quest_sets[card.get(lotr.CARD_ENCOUNTER_SET)] !=
                            card.get(lotr.CARD_ADDITIONAL_ENCOUNTER_SETS,
                                     '')):
                        precedent = {
                            'name': card[lotr.CARD_NAME],
                            'field': lotr.CARD_ADDITIONAL_ENCOUNTER_SETS,
                            'text': 'Additional encounter sets are "{}" and '
                                'the first value was "{}"'.format(
                                card.get(lotr.CARD_ADDITIONAL_ENCOUNTER_SETS,
                                         ''),
                                quest_sets[card.get(lotr.CARD_ENCOUNTER_SET)]
                                ),
                            'row': card[lotr.ROW_COLUMN]}
                        res.setdefault(
                            'Different additional encounter sets for the '
                            'quest', []).append(precedent)
                else:
                    quest_sets[card.get(lotr.CARD_ENCOUNTER_SET)] = (
                        card.get(lotr.CARD_ADDITIONAL_ENCOUNTER_SETS, ''))

        output = []
        for rule, card_list in res.items():
            rule_output = (
                '\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\n**{}**:\n'
                '\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_'.format(rule))
            for card_data in card_list:
                row_url = '<{}&range=A{}>'.format(data['url'],
                                                  card_data['row'])
                rule_output += '\n` `\n*{}* (**{}**):\n{}\n{}'.format(
                    card_data['name'], card_data['field'].replace('_', ' '),
                    card_data['text'], row_url)

            output.append(rule_output)

        output = '\n` `\n'.join(sorted(output))
        if output:
            output = '{}\n` `\nDone.'.format(output)
        else:
            output = 'no quest issues found'

        return output


    async def _display_space(self, value):  # pylint: disable=R0914
        """ Display possible spacing issues for a set.
        """
        data = await read_card_data()

        set_name = re.sub(r'^alep---', '', lotr.normalized_name(value))
        matches = [card for card in data['data'] if re.sub(
            r'^alep---', '',
            lotr.normalized_name(card[lotr.CARD_SET_NAME])) == set_name]

        if not matches:
            new_set_name = 'the-{}'.format(set_name)
            matches = [card for card in data['data'] if re.sub(
                r'^alep---', '',
                lotr.normalized_name(card[lotr.CARD_SET_NAME])) ==
                new_set_name]

        if not matches:
            set_code = value.lower()
            matches = [
                card for card in data['data']
                if card.get(lotr.CARD_SET_HOB_CODE, '').lower() == set_code]
            if not matches:
                return 'no cards found for the set'

        matches.sort(key=lambda card: card[lotr.ROW_COLUMN])
        res = {}
        for card in matches:
            if card[lotr.CARD_TYPE] in ('Presentation', 'Rules'):
                continue

            for field in (lotr.CARD_TEXT, lotr.CARD_SHADOW,
                          lotr.BACK_PREFIX + lotr.CARD_TEXT,
                          lotr.BACK_PREFIX + lotr.CARD_SHADOW):
                value = card.get(field, '')
                if re.search(r'\n{3,}', value.replace('[split]', '')
                             .replace('[vspace]', '')):
                    precedent = {
                        'name': card[lotr.CARD_NAME],
                        'field': field,
                        'text': 'Multiple linebreaks in:\n```\n{}\n```'
                            .format(value.replace('\n', '\\n\n')),
                        'row': card[lotr.ROW_COLUMN]}
                    res.setdefault('Multiple linebreaks', []).append(precedent)

                elif re.search(r'[^\n]\n[^\n]', value.replace('[split]', '')
                               .replace('[vspace]', '')):
                    precedent = {
                        'name': card[lotr.CARD_NAME],
                        'field': field,
                        'text': 'Single linebreak in:\n```\n{}\n```'.format(
                            value.replace('\n', '\\n\n')),
                        'row': card[lotr.ROW_COLUMN]}
                    res.setdefault('Single linebreak', []).append(precedent)

        output = []
        for rule, card_list in res.items():
            rule_output = (
                '\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\n**{}**:\n'
                '\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_'.format(rule))
            for card_data in card_list:
                row_url = '<{}&range=A{}>'.format(data['url'],
                                                  card_data['row'])
                rule_output += '\n` `\n*{}* (**{}**):\n{}\n{}'.format(
                    card_data['name'], card_data['field'].replace('_', ' '),
                    card_data['text'], row_url)

            output.append(rule_output)

        output = '\n` `\n'.join(sorted(output))
        if output:
            output = '{}\n` `\nDone.'.format(output)
        else:
            output = 'no spacing issues found'

        return output


    async def _display_text(self, value):  # pylint: disable=R0912,R0914
        """ Display text that may be a subject of editing rules for a set.
        """
        data = await read_card_data()

        set_name = re.sub(r'^alep---', '', lotr.normalized_name(value))
        matches = [card for card in data['data'] if re.sub(
            r'^alep---', '',
            lotr.normalized_name(card[lotr.CARD_SET_NAME])) == set_name and
            card[lotr.CARD_TYPE] != 'Presentation' and
            card.get(lotr.CARD_SPHERE) != 'Back']

        if not matches:
            new_set_name = 'the-{}'.format(set_name)
            matches = [card for card in data['data'] if re.sub(
                r'^alep---', '',
                lotr.normalized_name(card[lotr.CARD_SET_NAME])) == new_set_name
                and card[lotr.CARD_TYPE] != 'Presentation'
                and card.get(lotr.CARD_SPHERE) != 'Back']

        if not matches:
            set_code = value.lower()
            matches = [
                card for card in data['data']
                if card.get(lotr.CARD_SET_HOB_CODE, '').lower() == set_code and
                card[lotr.CARD_TYPE] != 'Presentation' and
                card.get(lotr.CARD_SPHERE) != 'Back']
            if not matches:
                return 'no cards found for the set'

        keywords = [lotr.extract_keywords(card[lotr.CARD_KEYWORDS])
                    for card in data['data'] if card.get(lotr.CARD_KEYWORDS)]
        keywords = [item for sublist in keywords for item in sublist]
        keywords = {lotr.simplify_keyword(k) for k in keywords}
        keywords.union(lotr.COMMON_KEYWORDS)
        keywords_regex = (r'(?<!\.) (' +
                          '|'.join([re.escape(k) for k in keywords]) + r')\b')

        matches.sort(key=lambda card: card[lotr.ROW_COLUMN])
        res = {}
        for card in matches:
            if (card.get(lotr.CARD_NAME) is not None and
                    card.get(lotr.BACK_PREFIX + lotr.CARD_NAME)
                        is not None and
                    card[lotr.CARD_NAME] !=
                        card[lotr.BACK_PREFIX + lotr.CARD_NAME]):
                precedent = {'name': card[lotr.CARD_NAME],
                             'field': lotr.BACK_PREFIX + lotr.CARD_NAME,
                             'text': '__**{}**__ (instead of *{}*)'.format(
                                 card[lotr.BACK_PREFIX + lotr.CARD_NAME],
                                 card[lotr.CARD_NAME]),
                             'row': card[lotr.ROW_COLUMN]}
                res.setdefault('Different card names on each side',
                               []).append(precedent)

            if card.get(lotr.CARD_TEXT) is not None:
                get_rules_precedents(
                    card[lotr.CARD_TEXT], lotr.CARD_TEXT, card, res,
                    keywords_regex, data['card_names'], data['traits'])

            if card.get(lotr.BACK_PREFIX + lotr.CARD_TEXT) is not None:
                get_rules_precedents(
                    card[lotr.BACK_PREFIX + lotr.CARD_TEXT],
                         lotr.BACK_PREFIX + lotr.CARD_TEXT, card, res,
                         keywords_regex, data['card_names'], data['traits'])

            if card.get(lotr.CARD_SHADOW) is not None:
                get_rules_precedents(
                    card[lotr.CARD_SHADOW], lotr.CARD_SHADOW, card, res,
                    keywords_regex, data['card_names'], data['traits'])

            if card.get(lotr.BACK_PREFIX + lotr.CARD_SHADOW) is not None:
                get_rules_precedents(
                    card[lotr.BACK_PREFIX + lotr.CARD_SHADOW],
                         lotr.BACK_PREFIX + lotr.CARD_SHADOW, card, res,
                         keywords_regex, data['card_names'], data['traits'])

        output = []
        for rule, card_list in res.items():
            rule_output = (
                '\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\n**{}**:\n'
                '\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_'.format(rule))
            for card_data in card_list:
                row_url = '<{}&range=A{}>'.format(data['url'],
                                                  card_data['row'])
                rule_output += '\n` `\n*{}* (**{}**):\n{}\n{}'.format(
                    card_data['name'], card_data['field'].replace('_', ' '),
                    card_data['text'], row_url)

            output.append(rule_output)

        output = '\n` `\n'.join(sorted(output))
        if output:
            output = '{}\n` `\nDone.'.format(output)
        else:
            output = 'no text rules precedents found'

        return output


    async def _display_traits(self, value):  # pylint: disable=R0912,R0914
        """ Display possible trait issues for a set.
        """
        data = await read_card_data()

        set_name = re.sub(r'^alep---', '', lotr.normalized_name(value))
        matches = [card for card in data['data'] if re.sub(
            r'^alep---', '',
            lotr.normalized_name(card[lotr.CARD_SET_NAME])) == set_name]

        if not matches:
            new_set_name = 'the-{}'.format(set_name)
            matches = [card for card in data['data'] if re.sub(
                r'^alep---', '',
                lotr.normalized_name(card[lotr.CARD_SET_NAME])) ==
                new_set_name]

        if not matches:
            set_code = value.lower()
            matches = [
                card for card in data['data']
                if card.get(lotr.CARD_SET_HOB_CODE, '').lower() == set_code]
            if not matches:
                return 'no cards found for the set'

        matches.sort(key=lambda card: card[lotr.ROW_COLUMN])
        res = {}
        for card in matches:
            if card.get(lotr.CARD_TRAITS) is not None:
                traits = lotr.extract_traits(card[lotr.CARD_TRAITS])
                unknown_traits = sorted(
                    [t for t in traits if t not in lotr.COMMON_TRAITS])
                if unknown_traits:
                    precedent = {
                        'name': card[lotr.CARD_NAME],
                        'field': lotr.CARD_TRAITS,
                        'text': '__**{}**__ in *{}*'.format(
                            ' '.join(['{}.'.format(t)
                                      for t in unknown_traits]),
                            re.sub(r'\[[^\]]+\]', '', card[lotr.CARD_TRAITS])),
                        'row': card[lotr.ROW_COLUMN]}
                    res.setdefault('Unknown traits', []).append(precedent)
                else:
                    test = lotr.verify_traits_order(
                        re.sub(r'\[[^\]]+\]', '', card[lotr.CARD_TRAITS]))
                    if not test[0]:
                        precedent = {
                            'name': card[lotr.CARD_NAME],
                            'field': lotr.CARD_TRAITS,
                            'text': '__**{}**__ (instead of *{}*)'.format(
                                re.sub(r'\[[^\]]+\]', '',
                                       card[lotr.CARD_TRAITS]), test[1]),
                            'row': card[lotr.ROW_COLUMN]}
                        res.setdefault('Potentially incorrect order of traits',
                                       []).append(precedent)

            if card.get(lotr.BACK_PREFIX + lotr.CARD_TRAITS) is not None:
                traits = lotr.extract_traits(
                    card[lotr.BACK_PREFIX + lotr.CARD_TRAITS])
                unknown_traits = sorted(
                    [t for t in traits if t not in lotr.COMMON_TRAITS])
                if unknown_traits:
                    precedent = {
                        'name': card[lotr.CARD_NAME],
                        'field': lotr.BACK_PREFIX + lotr.CARD_TRAITS,
                        'text': '__**{}**__ in *{}*'.format(
                            ' '.join(['{}.'.format(t)
                                      for t in unknown_traits]),
                            re.sub(r'\[[^\]]+\]', '',
                                   card[lotr.BACK_PREFIX + lotr.CARD_TRAITS])),
                        'row': card[lotr.ROW_COLUMN]}
                    res.setdefault('Unknown traits', []).append(precedent)
                else:
                    test = lotr.verify_traits_order(
                        re.sub(r'\[[^\]]+\]', '',
                               card[lotr.BACK_PREFIX + lotr.CARD_TRAITS]))
                    if not test[0]:
                        precedent = {
                            'name': card[lotr.CARD_NAME],
                            'field': lotr.BACK_PREFIX + lotr.CARD_TRAITS,
                            'text': '__**{}**__ (instead of *{}*)'.format(
                                re.sub(r'\[[^\]]+\]', '',
                                       card[lotr.BACK_PREFIX +
                                            lotr.CARD_TRAITS]),
                                test[1]),
                            'row': card[lotr.ROW_COLUMN]}
                        res.setdefault('Potentially incorrect order of traits',
                                       []).append(precedent)

        output = []
        for rule, card_list in res.items():
            rule_output = (
                '\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\n**{}**:\n'
                '\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_'.format(rule))
            for card_data in card_list:
                row_url = '<{}&range=A{}>'.format(data['url'],
                                                  card_data['row'])
                rule_output += '\n` `\n*{}* (**{}**):\n{}\n{}'.format(
                    card_data['name'], card_data['field'].replace('_', ' '),
                    card_data['text'], row_url)

            output.append(rule_output)

        output = '\n` `\n'.join(sorted(output))
        if output:
            output = '{}\n` `\nDone.'.format(output)
        else:
            output = 'no trait issues found'

        return output


    async def _process_edit_command(self, message):  # pylint: disable=R0911,R0912,R0915
        """ Process an edit command.
        """
        if message.content.lower() == '!edit':
            command = 'help'
        else:
            command = re.sub(r'^!edit ', '', message.content,
                             flags=re.IGNORECASE).split('\n')[0].strip()

        logging.info('Received edit command: %s', command)

        if command.lower().startswith('check traits '):
            try:
                traits = re.sub(r'^check traits ', '', command,
                                flags=re.IGNORECASE)
                res = lotr.verify_traits_order(traits)[1]
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'check traits':
            await self._send_channel(message.channel,
                                     'please specify the traits')
        elif command.lower().startswith('flavour '):
            try:
                set_name = re.sub(r'^flavour ', '', command,
                                  flags=re.IGNORECASE)
                res = await self._display_flavour(set_name)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'flavour':
            await self._send_channel(message.channel, 'please specify the set')
        elif command.lower().startswith('names '):
            try:
                set_name = re.sub(r'^names ', '', command,
                                  flags=re.IGNORECASE)
                res = await self._display_names(set_name)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'names':
            await self._send_channel(message.channel, 'please specify the set')
        elif command.lower().startswith('numbers '):
            try:
                set_name = re.sub(r'^numbers ', '', command,
                                  flags=re.IGNORECASE)
                res = await self._display_numbers(set_name)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'numbers':
            await self._send_channel(message.channel, 'please specify the set')
        elif command.lower().startswith('quests '):
            try:
                set_name = re.sub(r'^quests ', '', command,
                                  flags=re.IGNORECASE)
                res = await self._display_quests(set_name)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'quests':
            await self._send_channel(message.channel, 'please specify the set')
        elif command.lower().startswith('space '):
            try:
                set_name = re.sub(r'^space ', '', command,
                                  flags=re.IGNORECASE)
                res = await self._display_space(set_name)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'space':
            await self._send_channel(message.channel, 'please specify the set')
        elif command.lower().startswith('text '):
            try:
                set_name = re.sub(r'^text ', '', command,
                                  flags=re.IGNORECASE)
                res = await self._display_text(set_name)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'text':
            await self._send_channel(message.channel, 'please specify the set')
        elif command.lower().startswith('traits '):
            try:
                set_name = re.sub(r'^traits ', '', command,
                                  flags=re.IGNORECASE)
                res = await self._display_traits(set_name)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'traits':
            await self._send_channel(message.channel, 'please specify the set')
        elif command.lower().startswith('all '):
            try:
                set_name = re.sub(r'^all ', '', command,
                                  flags=re.IGNORECASE)
                res = []
                res.append(await self._display_flavour(set_name))
                res.append(await self._display_names(set_name))
                res.append(await self._display_numbers(set_name))
                res.append(await self._display_quests(set_name))
                res.append(await self._display_space(set_name))
                res.append(await self._display_text(set_name))
                res.append(await self._display_traits(set_name))
                res = '\n` `\n'.join(res)
            except Exception as exc:
                logging.exception(str(exc))
                await self._send_channel(
                    message.channel,
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'all':
            await self._send_channel(message.channel, 'please specify the set')
        else:
            res = HELP['edit']
            await self._send_channel(message.channel, res)


    async def _process_help_command(self, message):
        """ Process a help command.
        """
        logging.info('Received help command')

        help_keys = sorted([key for key in HELP
                            if key not in ('playtest', 'secret')])
        help_keys.append('playtest')
        res = ''.join(HELP[key] for key in help_keys)
        await asyncio.sleep(CMD_SLEEP_TIME)
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
                  message.content.lower() == '!art' or
                  message.content.lower() == '!asm' or
                  message.content.lower() == '!asbm'):
                await self._process_art_command(message)
            elif (message.content.lower().startswith('!image ') or
                  message.content.lower() == '!image'):
                await self._process_image_command(message)
            elif (message.content.lower().startswith('!stat ') or
                  message.content.lower() == '!stat'):
                await self._process_stat_command(message)
            elif (message.content.lower().startswith('!edit ') or
                  message.content.lower() == '!edit'):
                await self._process_edit_command(message)
            elif message.content.lower().startswith('!secret '):
                await self._process_secret_command(message)
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
