""" Service for LotR ALeP workflow (Part 1, before Strange Eons).

A wrapper around `run_before_se_cron.py` - see its description and deployment
instructions.

Setup a cron for `check_run_before_se_service.sh` (see its description).

Additionally, see `remind_art_backup.sh` and `spreadsheet_backup.py`.

Start it by running `./restart_run_before_se_service.sh`.
"""
import os
import time

from lotr import read_conf
from run_before_se_cron import init_logging, run


SLEEP_TIME = 50
WORKING_DIRECTORY = '/home/homeassistant/lotr-lcg-set-generator/'


if __name__ == '__main__':
    os.chdir(WORKING_DIRECTORY)
    init_logging()
    conf = read_conf() # pylint: disable=C0103
    while True:
        run(conf)
        time.sleep(SLEEP_TIME)
