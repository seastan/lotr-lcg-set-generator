# pylint: disable=W0703,C0301
""" Backup Google Spreadsheet.

NOTE: This script heavily relies on my existing smart home environment.

Setup a cron as:
18 8 * * *  python3 /home/homeassistant/lotr-lcg-set-generator/spreadsheet_backup.py >> /home/homeassistant/.homeassistant/cron.log 2>&1
"""
from datetime import datetime
import hashlib
import json
import os
import time
import uuid

import requests


BACKUP_PATH = '/home/homeassistant/.homeassistant/lotr'
ERROR_SUBJECT = 'LotR ALeP Spreadsheet Backup Error'
MAILS_PATH = 'mails'
SHEET_GDID = '16NnATw8C5iZ6gGTs5ZWmZmgrbbEoWJAc4PKBp72DGis'

MAX_FILES = 10


def create_mail(subject, body=''):
    """ Create mail file.
    """
    path = os.path.join(MAILS_PATH,
                        '{}_{}'.format(int(time.time()), uuid.uuid4()))
    with open(path, 'w') as fobj:
        json.dump({'subject': subject, 'body': body, 'html': True}, fobj)


def main():
    """ Main function.
    """
    filenames = [os.path.join(BACKUP_PATH, f) for f in os.listdir(BACKUP_PATH)]
    filenames = sorted([f for f in filenames if os.path.isfile(f)])
    last_checksum = (os.path.split(filenames[-1])[-1].split('.')[1]
                     if filenames
                     else '')

    url = ('https://docs.google.com/spreadsheets/d/{}/export?format=xlsx'
           .format(SHEET_GDID))
    content = requests.get(url).content
    new_checksum = hashlib.md5(content).hexdigest()
    if new_checksum == last_checksum:
        return

    new_filename = os.path.join(
        BACKUP_PATH,
        '{}.{}.xlsx'.format(datetime.today().strftime('%Y-%m-%d-%H-%M-%S'),
                            new_checksum))
    with open(new_filename, 'wb') as f_sheet:
        f_sheet.write(content)

    filenames.append(new_filename)
    old_filenames = filenames[:max(len(filenames) - MAX_FILES, 0)]
    for filename in old_filenames:
        os.remove(filename)

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        create_mail(ERROR_SUBJECT,
                    'Script failed: {}: {}'.format(type(exc).__name__,
                                                   str(exc)))
