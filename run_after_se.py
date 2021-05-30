""" LotR ALeP workflow (Part 2, after Strange Eons).
"""
import logging
import os
import signal
import sys
import time
from functools import wraps
from multiprocessing import Pool, cpu_count

import lotr


RETRIES = 2


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')


def retry():
    """Retry decorator.
    """
    def _wrap(func):
        @wraps(func)
        def _retry(*args, **kwargs):
            for i in range(RETRIES):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:  # pylint: disable=W0703
                    logging.exception('Function %s failed: %s: %s',
                                      func.__name__, type(exc).__name__,
                                      str(exc))
                    if i < RETRIES - 1:
                        logging.info('Retrying function %s...', func.__name__)
                    else:
                        raise

        return _retry

    return _wrap


@retry()
def generate_png300_nobleed(conf, set_id, set_name, lang, skip_ids):
    """ Generate PNG 300 dpi images without bleed margins.
    """
    lotr.generate_png300_nobleed(conf, set_id, set_name, lang, skip_ids)


@retry()
def generate_png800_nobleed(conf, set_id, set_name, lang, skip_ids):
    """ Generate PNG 800 dpi images without bleed margins.
    """
    lotr.generate_png800_nobleed(conf, set_id, set_name, lang, skip_ids)


@retry()
def generate_db(conf, set_id, set_name, lang, skip_ids, card_data):  # pylint: disable=R0913
    """ Generate DB (general purposes) outputs.
    """
    lotr.generate_png300_db(conf, set_id, set_name, lang, skip_ids)
    lotr.generate_db(conf, set_id, set_name, lang, card_data)


@retry()
def generate_octgn(conf, set_id, set_name, lang, skip_ids):
    """ Generate OCTGN outputs.
    """
    lotr.generate_png300_octgn(set_id, set_name, lang, skip_ids)
    lotr.generate_octgn(conf, set_id, set_name, lang)


@retry()
def generate_rules_pdf(conf, set_id, set_name, lang, skip_ids, card_data):  # pylint: disable=R0913
    """ Generate Rules PDF outputs.
    """
    lotr.generate_png300_rules_pdf(set_id, set_name, lang, skip_ids, card_data)
    lotr.generate_rules_pdf(conf, set_id, set_name, lang)


@retry()
def generate_pdf(conf, set_id, set_name, lang, skip_ids):
    """ Generate PDF outputs.
    """
    lotr.generate_png300_pdf(conf, set_id, set_name, lang, skip_ids)
    lotr.generate_pdf(conf, set_id, set_name, lang)


@retry()
def generate_genericpng_pdf(conf, set_id, set_name, lang, skip_ids):
    """ Generate generic PNG PDF outputs.
    """
    lotr.generate_png800_pdf(conf, set_id, set_name, lang, skip_ids)
    lotr.generate_genericpng_pdf(conf, set_id, set_name, lang)


@retry()
def generate_mpc(conf, set_id, set_name, lang, skip_ids, card_data):  # pylint: disable=R0913
    """ Generate MakePlayingCards outputs.
    """
    lotr.generate_png800_bleedmpc(conf, set_id, set_name, lang, skip_ids)
    lotr.generate_mpc(conf, set_id, set_name, lang, card_data)


@retry()
def generate_dtc(conf, set_id, set_name, lang, skip_ids, card_data):  # pylint: disable=R0913
    """ Generate DriveThruCards outputs.
    """
    lotr.generate_jpg300_bleeddtc(conf, set_id, set_name, lang, skip_ids)
    lotr.generate_dtc(conf, set_id, set_name, lang, card_data)


@retry()
def generate_mbprint(conf, set_id, set_name, lang, skip_ids, card_data):  # pylint: disable=R0913
    """ Generate MBPrint outputs.
    """
    lotr.generate_jpg800_bleedmbprint(conf, set_id, set_name, lang, skip_ids)
    lotr.generate_mbprint(conf, set_id, set_name, lang, card_data)


@retry()
def generate_genericpng(conf, set_id, set_name, lang, skip_ids, card_data):  # pylint: disable=R0913
    """ Generate generic PNG outputs.
    """
    lotr.generate_png800_bleedgeneric(conf, set_id, set_name, lang, skip_ids)
    lotr.generate_genericpng(conf, set_id, set_name, lang, card_data)


def run(args):
    """ Run the function.
    """
    func = args.pop(0)
    func(*args)


def initializer():
    """ Ignore CTRL+C in the worker process.
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    init_logging()


def execute_tasks(conf, tasks):
    """ Execute the list of tasks.
    """
    if not tasks:
        logging.info('No tasks to execute, skipping')
        return

    processes = (max(1, cpu_count() - 1)
                 if conf['parallelism'] == 'default'
                 else conf['parallelism'])
    processes = min(processes, len(tasks))
    logging.info('Starting a pull of %s process(es) for %s task(s)',
                 processes, len(tasks))
    with Pool(processes=processes, initializer=initializer) as pool:
        try:
            pool.map(run, tasks)
        except KeyboardInterrupt:
            logging.info('Program was terminated!')
            pool.terminate()
            raise KeyboardInterrupt


def main():  # pylint: disable=R0912
    """ Main function.
    """
    timestamp = time.time()
    if len(sys.argv) > 1:
        conf = lotr.read_conf(sys.argv[1])
    else:
        conf = lotr.read_conf()

    lotr.extract_data(conf)
    sets = lotr.get_sets(conf)

    pre_tasks = []
    tasks = []
    for set_id, set_name in sets:
        for lang in conf['output_languages']:
            skip_set, skip_ids = lotr.get_skip_info(set_id, set_name, lang)
            if skip_set:
                logging.info('[%s, %s] No changes since the last run,'
                             ' skipping', set_name, lang)
                continue

            if conf['nobleed_300'][lang]:
                pre_tasks.append([generate_png300_nobleed, conf, set_id,
                                  set_name, lang, skip_ids])

            if conf['nobleed_800'][lang]:
                pre_tasks.append([generate_png800_nobleed, conf, set_id,
                                  set_name, lang, skip_ids])

            if 'db' in conf['outputs'][lang]:
                tasks.append([generate_db, conf, set_id, set_name, lang,
                              skip_ids, lotr.translated_data(set_id, lang)])

            if 'octgn' in conf['outputs'][lang]:
                tasks.append([generate_octgn, conf, set_id, set_name, lang,
                              skip_ids])

            if 'rules_pdf' in conf['outputs'][lang]:
                tasks.append([generate_rules_pdf, conf, set_id, set_name,
                              lang, skip_ids,
                              lotr.translated_data(set_id, lang)])

            if 'pdf' in conf['outputs'][lang]:
                tasks.append([generate_pdf, conf, set_id, set_name, lang,
                              skip_ids])

            if 'genericpng_pdf' in conf['outputs'][lang]:
                tasks.append([generate_genericpng_pdf, conf, set_id, set_name,
                              lang, skip_ids])

            if 'makeplayingcards' in conf['outputs'][lang]:
                tasks.append([generate_mpc, conf, set_id, set_name, lang,
                              skip_ids, lotr.translated_data(set_id, lang)])

            if 'drivethrucards' in conf['outputs'][lang]:
                tasks.append([generate_dtc, conf, set_id, set_name, lang,
                              skip_ids, lotr.translated_data(set_id, lang)])

            if 'mbprint' in conf['outputs'][lang]:
                tasks.append([generate_mbprint, conf, set_id, set_name, lang,
                              skip_ids, lotr.translated_data(set_id, lang)])

            if 'genericpng' in conf['outputs'][lang]:
                tasks.append([generate_genericpng, conf, set_id, set_name,
                              lang, skip_ids,
                              lotr.translated_data(set_id, lang)])

    execute_tasks(conf, pre_tasks)
    execute_tasks(conf, tasks)

    if (conf['db_destination_path'] and conf['outputs'].get('English') and
            'db' in conf['outputs']['English']):
        lotr.copy_db_outputs(conf, sets)

    if (conf['octgn_image_destination_path'] and
            conf['outputs'].get('English') and
            'octgn' in conf['outputs']['English']):
        lotr.copy_octgn_image_outputs(conf, sets)

    if (conf['upload_dragncards'] and conf['dragncards_hostname'] and
            conf['dragncards_id_rsa_path']):
        lotr.upload_dragncards(conf, sets)

    logging.info('Done (%ss)', round(time.time() - timestamp, 3))


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
