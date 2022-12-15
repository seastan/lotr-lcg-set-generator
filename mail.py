# pylint: disable=C0209,W0703
""" Reliably send email messages.
"""
from datetime import datetime
import json
import logging
import os
import smtplib
import time
import yaml

from create_mail import create_mail


CONF_PATH = 'mail.yaml'
INTERNET_SENSOR_PATH = 'internet_state'
LOG_PATH = 'mail.log'
MAILS_PATH = 'mails'

EMAIL_SLEEP_TIME = 1
ITERATION_SLEEP_TIME = 1
LOG_LEVEL = logging.WARNING
MAX_FAIL_COUNT = 30
SMTP_TIMEOUT = 30


def init_logging():
    """ Init logging.
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
        return True


def run(account, to_address):  # pylint: disable=R0912,R0915
    """ Run an iteration.
    """
    try:
        filenames = [os.path.join(MAILS_PATH, f)
                     for f in os.listdir(MAILS_PATH)]
        filenames = sorted([f for f in filenames if os.path.isfile(f)])
    except Exception as exc:
        logging.error(exc)
        return True
    else:
        logging.info('%s file(s) to process', len(filenames))

    if not filenames:
        return True

    try:
        server = smtplib.SMTP_SSL(account['server'], 465, timeout=SMTP_TIMEOUT)
    except Exception as exc:
        logging.error('Init: %s', exc)
        return False

    try:
        try:
            server.ehlo()
        except Exception as exc:
            logging.error('Ehlo: %s', exc)
            return False

        try:
            server.login(account['email'], account['password'])
        except Exception as exc:
            logging.error('Login: %s', exc)
            return False

        sent_count = 0
        first_file = True
        for filename in filenames:
            if first_file:
                first_file = False
            else:
                time.sleep(EMAIL_SLEEP_TIME)

            try:
                with open(filename, 'r', encoding='utf-8') as fobj:
                    content = json.load(fobj)

                if content.get('html', False):
                    content_type = '\nContent-Type: text/html; charset=utf-8'
                else:
                    content_type = ''

                subject = content.get('subject', 'No subject')
                email_text = """\
From: LotR Mail Service <{}>
To: {}
Subject: {}{}

{}
""".format(account['email'],
           to_address,
           subject,
           content_type,
           content.get('body', '')).encode('utf-8')[:9500000]
                server.sendmail(account['email'], to_address, email_text)
            except Exception as exc:
                logging.error('Send: %s', exc)
            else:
                sent_count += 1
                logging.info('Email from %s successfully sent', filename)
                try:
                    os.remove(filename)
                except Exception as exc:
                    logging.error(exc)

        res = sent_count > 0
        return res
    finally:
        try:
            server.close()
        except Exception as exc:
            logging.error('Close: %s', exc)


def main():
    """ Main function.
    """
    try:
        with open(CONF_PATH, 'r', encoding='utf-8') as f_conf:
            conf = yaml.safe_load(f_conf)
    except Exception:
        logging.error('No configuration found')
        return

    accounts = []
    if conf.get('email'):
        accounts.append(
            {'email': conf['email'],
             'password': conf.get('password', ''),
             'server': conf.get('server', '')})

    if conf.get('email_backup'):
        accounts.append(
            {'email': conf['email_backup'],
             'password': conf.get('password_backup', ''),
             'server': conf.get('server_backup', '')})

    if not accounts:
        logging.error('No email accounts found')
        return

    if not os.path.exists(MAILS_PATH):
        os.mkdir(MAILS_PATH)

    timestr = time.strftime('%Y-%m-%d %H:%M:%S:{}%z'
                            .format(datetime.now().microsecond))
    create_mail('Starting Email Service with {} account at {}'
                .format(accounts[0]['email'], timestr))
    logging.info('Starting Email Service with %s account',
                 accounts[0]['email'])

    fail_count = 0
    while True:
        res = run(accounts[0], conf.get('to_address', ''))
        if internet_state() and not res:
            fail_count += 1
            if fail_count >= MAX_FAIL_COUNT:
                timestr = time.strftime('%Y-%m-%d %H:%M:%S:{}%z'
                                        .format(datetime.now().microsecond))
                create_mail('Switching email account from {} to {} at {}'
                            .format(accounts[0]['email'], accounts[1]['email'],
                                    timestr))
                logging.warning('Switching email account from %s to %s',
                                accounts[0]['email'], accounts[1]['email'])
                accounts.insert(0, accounts.pop())
                fail_count = 0

        time.sleep(ITERATION_SLEEP_TIME)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
