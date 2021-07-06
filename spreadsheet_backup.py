# pylint: disable=W0703,C0301
""" Backup Google Spreadsheet.
"""
from datetime import datetime
import hashlib
import json
import os
import sys
import time
import uuid

import requests


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


def main(backup_path):
    """ Main function.
    """
    filenames = [os.path.join(backup_path, f)
                 for f in os.listdir(backup_path)]
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
        backup_path,
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
        main(sys.argv[1])
    except Exception as exc:
        create_mail(ERROR_SUBJECT,
                    'Script failed: {}: {}'.format(type(exc).__name__,
                                                   str(exc)))
