# pylint: disable=W0703,C0301
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


ERROR_SUBJECT = 'LotR ALeP Links Backup Error'
MAILS_PATH = 'mails'
DOCS = {'faq': '10vofbe-ih_m_gDSPPCDvVIH3Pa_IxZKsj-iYZnpnssI'}
SHEETS = {'master': '16NnATw8C5iZ6gGTs5ZWmZmgrbbEoWJAc4PKBp72DGis',
          'player_card': '1_Vm_EqnwL9sCd-0H_lk6CS4HmmKNRSA8J7As3Fu7_NM',
          'encounter_card': '14tIyb3vDTLYj7oKDp3DT77DKrtp8x02QG9qYQGDbd0c'}

MAX_FILES = 5


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
        subject = Header(subject, 'utf8').encode()

    path = os.path.join(MAILS_PATH,
                        '{}_{}'.format(int(time.time()), uuid.uuid4()))
    with open(path, 'w') as fobj:
        json.dump({'subject': subject, 'body': body, 'html': True}, fobj)


def backup_doc(backup_path, name):
    """ Backup a Google Doc.
    """
    filenames = sorted([os.path.join(backup_path, f)
                        for f in os.listdir(backup_path)
                        if f.startswith(name)])
    last_checksum = (os.path.split(filenames[-1])[-1].split('.')[1]
                     if filenames
                     else '')

    url = ('https://docs.google.com/document/u/0/export?format=docx&id={}'
           .format(DOCS[name]))
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


def backup_sheet(backup_path, name):
    """ Backup a Google Sheet.
    """
    filenames = sorted([os.path.join(backup_path, f)
                        for f in os.listdir(backup_path)
                        if f.startswith(name)])
    last_checksum = (os.path.split(filenames[-1])[-1].split('.')[1]
                     if filenames
                     else '')

    url = ('https://docs.google.com/spreadsheets/d/{}/export?format=xlsx'
           .format(SHEETS[name]))
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
    for name in DOCS:
        backup_doc(backup_path, name)

    for name in SHEETS:
        backup_sheet(backup_path, name)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    try:
        main(sys.argv[1])
    except Exception as exc:
        create_mail(ERROR_SUBJECT,
                    'Script failed: {}: {}'.format(type(exc).__name__,
                                                   str(exc)))
