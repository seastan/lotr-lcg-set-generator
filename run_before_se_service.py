""" Service for LotR workflow (Part 1).

A wrapper around `run_before_se_cron.py`.
"""
import logging
import os
import time

from lotr import read_conf
from run_before_se_cron import init_logging, run


TARGET_SLEEP_TIME = 60


def main():
    """ Main function.
    """
    conf = read_conf()
    while True:
        timestamp = time.time()
        run(conf)
        duration = round(time.time() - timestamp)
        sleep_time = max(0, TARGET_SLEEP_TIME - duration)
        if sleep_time:
            logging.info('Sleeping %s seconds', sleep_time)
            time.sleep(sleep_time)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
