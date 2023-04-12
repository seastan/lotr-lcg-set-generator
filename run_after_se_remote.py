# pylint: disable=C0209
""" A wrapper around `run_after_se.py` for remote execution.
"""
import logging
import os
import uuid

import yaml

from lotr import CONFIGURATION_PATH, LOG_LIMIT
import run_after_se


LOG_FILE = 'run_after_se_remote.log'


def init_logging():
    """ Init logging.
    """
    with open(CONFIGURATION_PATH, 'r', encoding='utf-8') as f_conf:
        conf = yaml.safe_load(f_conf)

    log_path = conf.get('remote_logs_path', '')
    logging.basicConfig(
        handlers=[logging.FileHandler(
            filename=os.path.join(log_path, LOG_FILE),
            encoding='utf-8',
            mode='a')],
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s')



run_after_se.init_logging = init_logging


def run():
    """ Main function.
    """
    execution_id = uuid.uuid4()
    logging.info('Started: %s', execution_id)
    try:
        run_after_se.main()
    except Exception as exc:  # pylint: disable=W0703
        message = 'Script failed: {}: {}'.format(
            type(exc).__name__, str(exc))[:LOG_LIMIT]
        logging.exception(message)
    finally:
        logging.info('Finished: %s', execution_id)
        logging.info('')
        logging.info('')


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    run()
