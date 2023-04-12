# pylint: disable=C0209
""" Create mail file from the script arguments.
"""
from email.header import Header
import json
import os.path
import re
import sys
import time
import uuid

MAILS_PATH = 'mails'


def is_non_ascii(value):
    """ Check whether the string is ASCII only or not.
    """
    return not all(ord(c) < 128 for c in value)


def create_mail(subject, body='', html='false'):
    """ Create mail file.
    """
    if os.path.isfile(body):
        with open(body, 'r', encoding='utf-8') as fobj:
            body = fobj.read()

    if subject or body:
        subject = re.sub(r'\s+', ' ', subject)
        if len(subject) > 200:
            subject = subject[:200] + '...'

        if is_non_ascii(subject):
            subject = Header(subject, 'utf-8').encode()

        if len(body) > 10 * 1000 * 1000:
            body = body[:10 * 1000 * 1000]

        html = html.lower() == 'true'
        if not os.path.exists(MAILS_PATH):
            os.mkdir(MAILS_PATH)

        path = os.path.join(MAILS_PATH,
                            '{}_{}'.format(int(time.time()), uuid.uuid4()))
        with open(path, 'w', encoding='utf-8') as fobj:
            json.dump({'subject': subject, 'body': body, 'html': html}, fobj)


def main():
    """ Main function.
    """
    subject = sys.argv[1]
    body = sys.argv[2]
    html = sys.argv[3] if len(sys.argv) > 3 else 'false'
    create_mail(subject, body, html)


if __name__ == '__main__':
    main()
