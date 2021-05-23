""" A wrapper around `run_before_se.py` for remote execution.
"""
import logging
import os
import uuid

import yaml

from lotr import CONFIGURATION_PATH, LOG_LIMIT
import run_before_se


LOG_FILE = 'run_before_se_remote.log'


def init_logging():
    """ Init logging.
    """
    with open(CONFIGURATION_PATH, 'r') as f_conf:
        conf = yaml.safe_load(f_conf)

    log_path = conf.get('remote_logs_path', '')
    logging.basicConfig(filename=os.path.join(log_path, LOG_FILE),
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
