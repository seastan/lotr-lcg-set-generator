# pylint: disable=C0103,W0703
""" Discord bot.

You need to install dependency:
pip install discord.py
"""
import asyncio
import logging
import os
import re

import discord
import yaml


DISCORD_CONF_PATH = 'discord.yaml'
LOG_PATH = 'discord_bot.log'
WORKING_DIRECTORY = '/home/homeassistant/lotr-lcg-set-generator/'

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


async def save_new_target(content):
    """ Save new playtesting target.
    """
    lines = content.split('\n')
    if len(lines) == 1:
        return False

    lines = lines[1:]
    for line in lines:
        if not re.match(r'^[0-9]+[\. ]', line):
            return False

    return True


class MyClient(discord.Client):
    """ My bot class.
    """

    async def on_ready(self):
        """ Invoked when the client is ready.
        """
        logging.info('Logged in as %s (%s)', self.user.name, self.user.id)

    async def _process_cron_command(self, message):
        """ Process a cron command.
        """
        if not message.channel.name == 'cron':
            return

        command = message.content.split('\n')[0][6:]
        logging.info('Received cron command: %s', command)
        if command.lower() == 'hello':
            await message.reply('hello')
        elif command.lower() == 'test':
            await message.reply('passed')
        elif command.lower() == 'thank you':
            await message.reply('you are welcome')
        elif command.lower() == 'log':
            res = await get_log()
            if not res:
                res = 'no cron log found'

            for chunk in split_result(res):
                await message.reply(chunk)
        elif command.lower() == 'errors':
            res = await get_errors()
            if not res:
                res = 'no cron log found'

            for chunk in split_result(res):
                await message.reply(chunk)
        else:
            await message.reply('excuse me?')

    async def _process_playtest_command(self, message):
        """ Process a playtest command.
        """
        command = message.content.split('\n')[0][10:]
        logging.info('Received playtest command: %s', command)
        if command.lower() == 'new':
            res = await save_new_target(message.content)
            if not res:
                await message.reply(
                    """incorrect command format, try something like:
!playtest new
1. Escape From Dol Guldur (solo)
2. Frogs deck
""")
                return

            await message.reply('done')
        else:
            await message.reply('excuse me?')

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
