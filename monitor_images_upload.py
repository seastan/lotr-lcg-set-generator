# pylint: disable=W0703,C0209
# -*- coding: utf8 -*-
""" Monitor uploading images to S3 on the DragnCards host.
"""
from email.header import Header
import json
import logging
import os
import re
import time
import uuid

import yaml

from lotr import monitor_images_upload


DISCORD_CONF_PATH = 'discord.yaml'
ALERT_SUBJECT_TEMPLATE = 'Images Upload Monitoring Cron ALERT: {}'
ERROR_SUBJECT_TEMPLATE = 'Images Upload Monitoring Cron ERROR: {}'
LOG_PATH = 'monitor_images_upload.log'
MAILS_PATH = 'mails'

LOG_LEVEL = logging.INFO


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(filename=LOG_PATH, level=LOG_LEVEL,
                        format='%(asctime)s %(levelname)s: %(message)s')


def is_non_ascii(value):
    """ Check whether the string is ASCII only or not.
    """
    return not all(ord(c) < 128 for c in value)


def create_mail(subject, body=''):
    """ Create mail file.
    """
    subject = re.sub(r'\s+', ' ', subject)
    if len(subject) > 200:
        subject = subject[:200] + '...'

    if is_non_ascii(subject):
        subject = Header(subject, 'utf-8').encode()

    path = os.path.join(MAILS_PATH,
                        '{}_{}'.format(int(time.time()), uuid.uuid4()))
    with open(path, 'w', encoding='utf-8') as fobj:
        json.dump({'subject': subject, 'body': body, 'html': False}, fobj)


def get_images_upload_errors():
    """ Get images upload errors from the DragnCards host.
    """
    with open(DISCORD_CONF_PATH, 'r', encoding='utf-8') as f_conf:
        conf = yaml.safe_load(f_conf)

    res = monitor_images_upload(conf)
    res = res.strip()
    return res


def main():
    """ Main function.
    """
    logging.info('Started')
    try:
        errors = get_images_upload_errors()
        if errors:
            message = 'Found images upload errors'
            logging.info(message)
            logging.info(errors)
            create_mail(ALERT_SUBJECT_TEMPLATE.format(message), errors)
        else:
            logging.info('No errors found')
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
