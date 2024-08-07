# pylint: disable=C0209
""" A wrapper around `run_before_se.py` for remote execution.
"""
import logging
import os
import time
import uuid

import yaml

from lotr import CONFIGURATION_PATH, LOG_LIMIT
import run_before_se


LOG_FILE = 'run_before_se_remote.log'
RETRY_SLEEP_TIME = 300
SANITY_CHECK_ERROR_SLEEP_TIME = 3600


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


def run():
    """ Main function.
    """
    execution_id = uuid.uuid4()
    logging.info('Started: %s', execution_id)
    try:
        run_before_se.main()
    except Exception as exc:  # pylint: disable=W0703
        exception_type = type(exc).__name__
        message = 'Script failed, retrying: {}: {}'.format(
            exception_type, str(exc))[:LOG_LIMIT]
        logging.exception(message)
        if exception_type == 'SanityCheckError':
            logging.info('Sleeping before retrying a sanity check error')
            time.sleep(SANITY_CHECK_ERROR_SLEEP_TIME)
        else:
            logging.info('Sleeping before retrying')
            time.sleep(RETRY_SLEEP_TIME)

        try:
            run_before_se.main()
        except Exception as exc_child:  # pylint: disable=W0703
            exception_type = type(exc_child).__name__
            message = 'Script failed, exiting: {}: {}'.format(
                exception_type, str(exc_child))[:LOG_LIMIT]
            logging.exception(message)
    finally:
        logging.info('Finished: %s', execution_id)
        logging.info('')
        logging.info('')


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    run()
