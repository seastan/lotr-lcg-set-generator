""" Service for LotR ALeP workflow (Part 1, before Strange Eons).

A wrapper around run_before_se_cron.py (see its description.
"""
import os
import time

from lotr import read_conf
from run_before_se_cron import init_logging, run


SLEEP_TIME = 60
WORKING_DIRECTORY = '/home/homeassistant/lotr-lcg-set-generator/'


if __name__ == '__main__':
    os.chdir(WORKING_DIRECTORY)
    init_logging()
    conf = read_conf() # pylint: disable=C0103
    while True:
        run(conf)
        time.sleep(SLEEP_TIME)
