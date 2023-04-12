# pylint: disable=W0703,C0209,C0301
""" Backup Google Docs and Google Sheets links.
"""
from datetime import datetime
from email.header import Header
import hashlib
import json
import os
import re
import sys
import time
import uuid

import requests


CONF_PATH = 'scheduled_backup.json'
ERROR_SUBJECT = 'LotR Links Backup Error'
MAILS_PATH = 'mails'
MAX_FILES = 5


class ConfigurationError(Exception):
    """ Configuration error.
    """


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
        json.dump({'subject': subject, 'body': body, 'html': True}, fobj)


def backup_doc(backup_path, name, doc_id):
    """ Backup a Google Doc.
    """
    filenames = sorted([os.path.join(backup_path, f)
                        for f in os.listdir(backup_path)
                        if f.startswith(name)])
    last_checksum = (os.path.split(filenames[-1])[-1].split('.')[1]
                     if filenames
                     else '')

    url = ('https://docs.google.com/document/u/0/export?format=docx&id={}'
           .format(doc_id))
    content = requests.get(url).content
    new_checksum = hashlib.md5(content).hexdigest()
    if new_checksum == last_checksum:
        return

    new_filename = os.path.join(
        backup_path,
        '{}_{}.{}.docx'.format(name,
                               datetime.today().strftime('%Y-%m-%d-%H-%M-%S'),
                               new_checksum))
    with open(new_filename, 'wb') as f_sheet:
        f_sheet.write(content)

    filenames.append(new_filename)
    old_filenames = filenames[:max(len(filenames) - MAX_FILES, 0)]
    for filename in old_filenames:
        os.remove(filename)


def backup_sheet(backup_path, name, sheet_id):
    """ Backup a Google Sheet.
    """
    filenames = sorted([os.path.join(backup_path, f)
                        for f in os.listdir(backup_path)
                        if f.startswith(name)])
    last_checksum = (os.path.split(filenames[-1])[-1].split('.')[1]
                     if filenames
                     else '')

    url = ('https://docs.google.com/spreadsheets/d/{}/export?format=xlsx'
           .format(sheet_id))
    content = requests.get(url).content
    new_checksum = hashlib.md5(content).hexdigest()
    if new_checksum == last_checksum:
        return

    new_filename = os.path.join(
        backup_path,
        '{}_{}.{}.xlsx'.format(name,
                               datetime.today().strftime('%Y-%m-%d-%H-%M-%S'),
                               new_checksum))
    with open(new_filename, 'wb') as f_sheet:
        f_sheet.write(content)

    filenames.append(new_filename)
    old_filenames = filenames[:max(len(filenames) - MAX_FILES, 0)]
    for filename in old_filenames:
        os.remove(filename)


def main(backup_path):
    """ Main function.
    """
    try:
        with open(CONF_PATH, 'r', encoding='utf-8') as fobj:
            data = json.load(fobj)
    except Exception as exc:
        raise ConfigurationError('No configuration found') from exc

    for name in data['docs']:
        backup_doc(backup_path, name, data['docs'][name])

    for name in data['sheets']:
        backup_sheet(backup_path, name, data['sheets'][name])


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    try:
        main(sys.argv[1])
    except Exception as main_exc:
        create_mail(ERROR_SUBJECT,
                    'Script failed: {}: {}'.format(type(main_exc).__name__,
                                                   str(main_exc)))
