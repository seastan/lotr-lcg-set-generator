# pylint: disable=W0703
""" Discord bot.

You need to install dependency:
pip install discord.py
"""
import logging
import os
import subprocess

import discord
import yaml


DISCORD_CONF_PATH = 'discord.yaml'
LOG_PATH = 'discord_bot.log'
WORKING_DIRECTORY = '/home/homeassistant/lotr-lcg-set-generator/'

SLEEP_TIME = 1


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


def get_log():
    """ Get full log of the last cron execution.
    """
    try:
        res = subprocess.run('./cron_log.sh', capture_output=True, shell=True,
                             check=True)
    except subprocess.CalledProcessError:
        return ''

    res = res.stdout.decode('utf-8').strip()
    return res


def get_errors():
    """ Get errors of the last cron execution.
    """
    try:
        res = subprocess.run('./cron_errors.sh', capture_output=True,
                             shell=True, check=True)
    except subprocess.CalledProcessError:
        return ''

    res = res.stdout.decode('utf-8').strip()
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


class MyClient(discord.Client):
    """ My bot class.
    """

    async def on_ready(self):
        """ Invoked when the client is ready.
        """
        logging.info('Logged in as %s (%s)', self.user.name, self.user.id)

    async def on_message(self, message):
        """ Invoked when a new message posted.
        """
        try:
            if (not message.channel.name == 'cron'
                    or not message.content.startswith('!cron ')
                    or message.author.id == self.user.id):
                return

            command = message.content[6:]
            logging.info('Received command: %s', command)
            if command.lower() == 'hello':
                await message.reply('hello')
            elif command.lower() == 'test':
                await message.reply('passed')
            elif command.lower() == 'thank you':
                await message.reply('uou are welcome')
            elif command.lower() == 'log':
                res = get_log()
                if not res:
                    res = 'no cron log found'

                for chunk in split_result(res):
                    await message.reply(chunk)
            elif command.lower() == 'errors':
                res = get_errors()
                if not res:
                    res = 'no cron log found'

                for chunk in split_result(res):
                    await message.reply(chunk)
            else:
                await message.reply('excuse me?')
        except Exception as exc:
            logging.exception(str(exc))


if __name__ == '__main__':
    os.chdir(WORKING_DIRECTORY)
    init_logging()
    MyClient().run(get_token())
