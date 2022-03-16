""" Service for LotR workflow (Part 1).

A wrapper around `run_before_se_cron.py`.
"""
import os
import time

from lotr import read_conf
from run_before_se_cron import init_logging, run


SLEEP_TIME = 45


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    conf = read_conf() # pylint: disable=C0103
    while True:
        run(conf)
        time.sleep(SLEEP_TIME)
