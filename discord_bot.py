# pylint: disable=C0103,W0703
""" Discord bot.

You need to install dependency:
pip install discord.py
"""
import asyncio
import json
import logging
import os
import re

import discord
import yaml


DISCORD_CONF_PATH = 'discord.yaml'
LOG_PATH = 'discord_bot.log'
WORKING_DIRECTORY = '/home/homeassistant/lotr-lcg-set-generator/'

PLAYTESTING_CHANNEL_ID = 821853410084651048
PLAYTEST_FILE = 'discord_playtest.json'

SLEEP_TIME = 1


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
        with open(DISCORD_CONF_PATH, 'r') as f_conf:
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
    for line in data:
        completed = '~~' if line['completed'] else ''
        user = ' ({})'.format(line['user']) if line['user'] else ''
        res += '{}{}. {}{}{}\n'.format(completed,  # pylint: disable=W1308
                                       line['num'],
                                       line['title'],
                                       completed,
                                       user)

    res = res.strip()
    return res


class MyClient(discord.Client):
    """ My bot class.
    """

    async def on_ready(self):
        """ Invoked when the client is ready.
        """
        logging.info('Logged in as %s (%s)', self.user.name, self.user.id)

    async def _process_cron_command(self, message):  #pylint: disable=R0912
        """ Process a cron command.
        """
        command = re.sub(r'^!crom ', '', message.content).split('\n')[0]
        command = message.content.split('\n')[0][6:]
        logging.info('Received cron command: %s', command)
        if command == 'hello':
            await message.channel.send('hello')
        elif command == 'test':
            await message.channel.send('passed')
        elif command == 'thank you':
            await message.channel.send('you are welcome')
        elif command == 'log':
            res = await get_log()
            if not res:
                res = 'no cron log found'

            for i, chunk in enumerate(split_result(res)):
                if i > 0:
                    await asyncio.sleep(SLEEP_TIME)

                await message.channel.send(chunk)
        elif command == 'errors':
            res = await get_errors()
            if not res:
                res = 'no cron log found'

            for i, chunk in enumerate(split_result(res)):
                if i > 0:
                    await asyncio.sleep(SLEEP_TIME)

                await message.channel.send(chunk)
        else:
            await message.channel.send('excuse me?')

    async def _add_new_target(self, content):
        """ Add new playtesting target.
        """
        error_message = """incorrect command format: {}
try something like:
!playtest new
1. Escape From Dol Guldur (solo)
2. Frogs deck
"""
        lines = content.split('\n')
        if len(lines) == 1:
            return error_message.format('no targets specified')

        lines = [line.strip() for line in lines[1:]]
        nums = set()
        data = []
        for line in lines:
            if not re.match(r'^[0-9]+\.? ', line):
                return error_message.format('no number for a target')

            if '~~' in line:
                return error_message.format('a target is already crossed out')

            num, title = line.split(' ', 1)
            num = re.sub(r'\.$', '', num)
            if num in nums:
                return error_message.format(
                    'a duplicate target number "{}"'.format(num))

            nums.add(num)
            data.append({'num': num,
                         'title': title,
                         'completed': False,
                         'user': None})

        async with playtest_lock:
            with open(PLAYTEST_FILE, 'w') as obj:
                json.dump(data, obj)

        playtest_message = """----------
New playtesting targets:
{}""".format(format_playtest_message(data))
        await self.get_channel(PLAYTESTING_CHANNEL_ID).send(playtest_message)
        return ''

    async def _complete_target(self, content, num, user, url):
        """ Complete playtesting target.
        """
        if not re.match(r'^[0-9]+$', num):
            return 'target number "{}" doesn\'t look correct'.format(num)

        if len(content.split('\n', 1)) == 1:
            return 'please add a playtesting report'

        async with playtest_lock:
            with open(PLAYTEST_FILE, 'r+') as obj:
                data = json.load(obj)

                nums = [target['num'] for target in data]
                if num not in nums:
                    return 'target "{}" not found'.format(num)

                nums = [target['num'] for target in data
                        if not target['completed']]
                if num not in nums:
                    return 'target "{}" already completed'.format(num)

                for target in data:
                    if target['num'] == num:
                        target['completed'] = True
                        target['user'] = user
                        break

                obj.seek(0)
                obj.truncate()
                json.dump(data, obj)

        all_targets = ('All targets completed now!'
                       if all(target['completed'] for target in data)
                       else '')
        playtest_message = """----------
Target "{}" completed. Link: {}
{}
{}""".format(num, url, format_playtest_message(data), all_targets)
        await self.get_channel(PLAYTESTING_CHANNEL_ID).send(playtest_message)
        return ''

    async def _update_target(self, params):
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
            with open(PLAYTEST_FILE, 'r+') as obj:
                data = json.load(obj)

                existing_nums = set(target['num'] for target in data)
                for num in nums:
                    if num not in existing_nums:
                        return 'target "{}" not found'.format(num)

                for target in data:
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
                       if all(target['completed'] for target in data)
                       else '')
        playtest_message = """----------
Targets updated.
{}
{}""".format(format_playtest_message(data), all_targets)
        await self.get_channel(PLAYTESTING_CHANNEL_ID).send(playtest_message)
        return ''

    async def _process_playtest_command(self, message):
        """ Process a playtest command.
        """
        command = re.sub(r'^!playtest ', '', message.content).split('\n')[0]
        logging.info('Received playtest command: %s', command)
        if command == 'new':
            try:
                error = await self._add_new_target(message.content)
            except Exception as exc:
                logging.error(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await message.channel.send(error)
                return

            await message.channel.send('done')
        elif command.startswith('complete '):
            try:
                num = re.sub(r'^complete ', '', command)
                user = re.sub(r'#.+$', '', str(message.author))
                error = await self._complete_target(message.content, num, user,
                                                    message.jump_url)
            except Exception as exc:
                logging.error(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await message.channel.send(error)
                return

            await message.channel.send('done')
        elif command.startswith('update '):
            try:
                params = re.sub(r'^update ', '', command).split(' ')
                error = await self._update_target(params)
            except Exception as exc:
                logging.error(str(exc))
                await message.channel.send(
                    'unexpected error: {}'.format(str(exc)))
                return

            if error:
                await message.channel.send(error)
                return

            await message.channel.send('done')
        else:
            await message.channel.send('excuse me?')

    async def on_message(self, message):
        """ Invoked when a new message posted.
        """
        try:
            if message.author.id == self.user.id:
                return

            if message.content.startswith('!cron '):
                await self._process_cron_command(message)
            elif message.content.startswith('!playtest '):
                await self._process_playtest_command(message)
        except Exception as exc:
            logging.exception(str(exc))


if __name__ == '__main__':
    os.chdir(WORKING_DIRECTORY)
    init_logging()
    MyClient().run(get_token())
