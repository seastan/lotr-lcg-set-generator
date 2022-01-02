""" Print current date.
"""
import time
import requests


URL = 'http://ipecho.net/plain'
URL_TIMEOUT = 10
URL_RETRIES = 3
URL_SLEEP = 10


def get_content(url):
    """ Get URL content.
    """
    res = ''
    for i in range(URL_RETRIES):
        try:
            req = requests.get(url, timeout=URL_TIMEOUT)
            res = req.content.decode()
            break
        except Exception:  # pylint: disable=W0703
            if i < URL_RETRIES - 1:
                time.sleep(URL_SLEEP)

    return res


if __name__ == '__main__':
    print(get_content(URL))
