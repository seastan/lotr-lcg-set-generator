# pylint: disable=C0103,C0302,W0703
# -*- coding: utf8 -*-
""" Discord bot.

You need to install dependency:
pip install discord.py

Create discord.yaml (see discord.default.yaml).
"""
import asyncio
import json
import logging
import os
import random
import re

import discord
import yaml

import lotr


CONF_PATH = 'discord.yaml'
LOG_PATH = 'discord_bot.log'
PLAYTEST_PATH = os.path.join('Discord', 'playtest.json')
SLEEP_TIME = 1
WORKING_DIRECTORY = '/home/homeassistant/lotr-lcg-set-generator/'

PLAYTEST_CHANNEL = 'playtesting-checklist'
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
**!playtest remove <target or list of targets separated by space>** - remove a given target or a list of targets (for example: `!playtest remove 11 12`)
**!playtest update <target or list of targets separated by space> <player>** - mark a given target or a list of targets as completed by a given player (for example: `!playtest random 7 Shellin`)
**!playtest random <number>** - generate a random number from 1 to a given number (for example: `!playtest random 10`)
**!playtest help** - display this help message
""",
    'stat': """
List of **!stat** commands:

**!stat channels** - number of Discord channels and free channel slots
**!stat questkeywords <quest>** - display the list of all keywords for a given quest (for example: `!stat questkeywords The Battle for the Beacon`)
**!stat help** - display this help message
"""
}

playtest_lock = asyncio.Lock()


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')


def get_token():
    """ Get Discord token.
    """
    try:
        with open(CONF_PATH, 'r') as f_conf:
            conf = yaml.safe_load(f_conf)

        return conf.get('token', '')
    except Exception as exc:
        logging.exception(str(exc))
        return ''


async def get_log():
    """ Get full log of the last cron execution.
    """
    try:
        proc = await asyncio.create_subprocess_shell(
            './cron_log.sh',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
    except Exception:
        return ''

    res = stdout.decode('utf-8').strip()
    return res


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


async def read_card_data():
    """ Read card data generated by the cron job.
    """
    try:
        with open(lotr.DISCORD_CARD_DATA_PATH, 'r') as obj:
            data = json.load(obj)
    except Exception:
        await asyncio.sleep(SLEEP_TIME)
        with open(lotr.DISCORD_CARD_DATA_PATH, 'r') as obj:
            data = json.load(obj)

    return data


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

    res = f"""{card_unique}{card_name}
{card_sphere}{card_type}{card_cost}{card_engagement}{card_stage}{card_skills}

{card_traits}{card_keywords}{card_text}{card_shadow}{card_victory}{card_special_icon}{card_flavour}"""  # pylint: disable=C0301
    return res


def format_card(card, spreadsheet_url, channel_url):  # pylint: disable=R0914
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
    card_number = '**#{}**'.format(card[lotr.CARD_NUMBER])
    card_id = '*id:* {}'.format(card[lotr.CARD_ID])

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
                       else '```{}```\n'.format(deck_rules))

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


class MyClient(discord.Client):
    """ My bot class.
    """

    channels = {}


    async def on_ready(self):
        """ Invoked when the client is ready.
        """
        logging.info('Logged in as %s (%s)', self.user.name, self.user.id)
        for channel in self.get_all_channels():
            if (not channel.category_id
                    or channel.category.name in GENERAL_CATEGORIES
                    or channel.name in ('general', 'rules')):
                continue

            if channel.name in self.channels:
                logging.warning(
                    'Duplicate channel name detected: %s (categories "%s" '
                    'and "%s")',
                    channel.name,
                    self.channels[channel.name]['category_name'],
                    channel.category.name)
            else:
                self.channels[channel.name] = {
                    'name': channel.name,
                    'id': channel.id,
                    'guild_id': channel.guild.id,
                    'category_id': channel.category_id,
                    'category_name': channel.category.name}

        await self._test_channels()


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
                await asyncio.sleep(SLEEP_TIME)

            await channel.send(chunk)


    async def _process_cron_command(self, message):  #pylint: disable=R0912
        """ Process a cron command.
        """
        command = re.sub(r'^!cron ', '', message.content, flags=re.IGNORECASE
                        ).split('\n')[0]
        logging.info('Received cron command: %s', command)
        if command.lower().startswith('hello'):
            await message.channel.send('hello')
        elif command.lower().startswith('test'):
            await message.channel.send('passed')
        elif (command.lower().startswith('thank you') or
              command.lower().startswith('thanks')):
            await message.channel.send('you are welcome')
        elif command.lower() == 'log':
            res = await get_log()
            if not res:
                res = 'no cron log found'

            await self._send_channel(message.channel, res)
        elif command.lower() == 'errors':
            res = await get_errors()
            if not res:
                res = 'no cron log found'

            await self._send_channel(message.channel, res)
        elif command.lower().startswith('help'):
            res = HELP['cron']
            await self._send_channel(message.channel, res)
        else:
            await message.channel.send('excuse me?')


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
        if PLAYTEST_CHANNEL in self.channels:
            await self._send_channel(
                self.get_channel(self.channels[PLAYTEST_CHANNEL]['id']),
                playtest_message)

        return ''


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
        if PLAYTEST_CHANNEL in self.channels:
            await self._send_channel(
                self.get_channel(self.channels[PLAYTEST_CHANNEL]['id']),
                playtest_message)

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
        if PLAYTEST_CHANNEL in self.channels:
            await self._send_channel(
                self.get_channel(self.channels[PLAYTEST_CHANNEL]['id']),
                playtest_message)

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
        if PLAYTEST_CHANNEL in self.channels:
            await self._send_channel(
                self.get_channel(self.channels[PLAYTEST_CHANNEL]['id']),
                playtest_message)

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
        if PLAYTEST_CHANNEL in self.channels:
            await self._send_channel(
                self.get_channel(self.channels[PLAYTEST_CHANNEL]['id']),
                playtest_message)

        return ''


    async def _process_playtest_command(self, message):  # pylint: disable=R0911,R0912,R0915
        """ Process a playtest command.
        """
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
        elif command.lower().startswith('complete '):
            try:
                num = re.sub(r'^complete ', '', command, flags=re.IGNORECASE)
                user = re.sub(r'#.+$', '', str(message.author))
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
        elif command.lower().startswith('help'):
            res = HELP['playtest']
            await self._send_channel(message.channel, res)
        else:
            await message.channel.send('excuse me?')


    async def _get_quest_keywords(self, quest):
        """ Get all keywords for a quest.
        """
        data = await read_card_data()
        encounter_sets = set()
        for card in data['data']:
            if (card[lotr.CARD_TYPE] == 'Quest' and
                    lotr.normalized_name(card.get(lotr.CARD_ADVENTURE)) ==
                    lotr.normalized_name(quest)):
                encounter_sets.add(card.get(lotr.CARD_ENCOUNTER_SET, ''))
                additional_sets = card.get(lotr.CARD_ADDITIONAL_ENCOUNTER_SETS)
                if additional_sets:
                    encounter_sets = encounter_sets.union(
                        [e.strip() for e in additional_sets.split(';')])

        encounter_sets = {e for e in encounter_sets if e}
        if not encounter_sets:
            return 'No cards for quest "{}" found'.format(quest)

        keywords = set()
        for card in data['data']:
            if (card.get(lotr.CARD_ENCOUNTER_SET) in encounter_sets and
                    card.get(lotr.CARD_KEYWORDS)):
                keywords = keywords.union(
                    lotr.extract_keywords(card[lotr.CARD_KEYWORDS]))

        if not keywords:
            return 'No keywords for quest "{}" found'.format(quest)

        res = '\n'.join(sorted(keywords))
        return res


    async def _get_card(self, command, this):  # pylint: disable=R0912,R0914
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
                           .format(channel['guild_id'], channel['id']))
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
        command = re.sub(r'^!stat ', '', message.content,
                         flags=re.IGNORECASE).split('\n')[0]
        logging.info('Received stat command: %s', command)

        if command.lower().startswith('questkeywords '):
            try:
                quest = re.sub(r'^questkeywords ', '', command,
                               flags=re.IGNORECASE)
                res = await self._get_quest_keywords(quest)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower() == 'channels':
            try:
                num = len(list(self.get_all_channels()))
                res = 'There are {} channels and {} free slots'.format(
                    num, 500 - num)
            except Exception as exc:
                logging.exception(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            await self._send_channel(message.channel, res)
        elif command.lower().startswith('help'):
            res = HELP['stat']
            await self._send_channel(message.channel, res)
        else:
            await message.channel.send('excuse me?')


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

            if message.author.id == self.user.id:
                return

            if message.content.lower().startswith('!cron '):
                await self._process_cron_command(message)
            elif message.content.lower().startswith('!playtest '):
                await self._process_playtest_command(message)
            elif message.content.lower().startswith('!alepcard '):
                await self._process_card_command(message)
            elif message.content.lower().startswith('!stat '):
                await self._process_stat_command(message)
            elif message.content.lower().startswith('!help'):
                await self._process_help_command(message)
        except Exception as exc:
            logging.exception(str(exc))


if __name__ == '__main__':
    os.chdir(WORKING_DIRECTORY)
    init_logging()
    MyClient().run(get_token())
