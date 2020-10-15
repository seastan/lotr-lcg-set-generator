""" LotR ALeP workflow (Part 2, after Strange Eons).
"""
import logging
import signal
import time
from multiprocessing import Pool, cpu_count

import lotr

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')


def generate_db_octgn(conf, set_id, set_name, lang, skip_ids):
    """ Generate DB and OCTGN outputs.
    """
    lotr.generate_jpg300_nobleed(set_id, set_name, lang, skip_ids)
    if 'db' in conf['outputs']:
        lotr.generate_db(set_id, set_name, lang)

    if 'octgn' in conf['outputs']:
        lotr.generate_octgn(set_id, set_name, lang)


def generate_pdf(conf, set_id, set_name, lang, skip_ids):
    """ Generate PDF outputs.
    """
    lotr.generate_png300_pdf(conf, set_id, set_name, lang, skip_ids)
    lotr.generate_pdf(set_id, set_name, lang)


def generate_mpc(conf, set_id, set_name, lang, skip_ids):
    """ Generate MakePlayingCards outputs.
    """
    lotr.generate_png800_bleedmpc(conf, set_id, set_name, lang, skip_ids)
    lotr.generate_mpc(conf, set_id, set_name, lang)


def generate_dtc(conf, set_id, set_name, lang, skip_ids):
    """ Generate DriveThruCards outputs.
    """
    lotr.generate_jpg300_bleeddtc(conf, set_id, set_name, lang, skip_ids)
    lotr.generate_dtc(conf, set_id, set_name, lang)


def run(args):
    """ Run the function.
    """
    func = args.pop(0)
    func(*args)


def initializer():
    """ Ignore CTRL+C in the worker process.
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def main():
    """ Main function.
    """
    timestamp = time.time()
    conf = lotr.read_conf()
    sets = lotr.get_sets(conf)

    tasks = []
    for set_data in sets:
        set_id, set_name, _ = set_data
        for lang in conf['languages']:
            skip_set, skip_ids = lotr.get_skip_info(set_id, set_name, lang)
            if skip_set:
                logging.info('[%s, %s] No changes since the last run,'
                             ' skipping', set_name, lang)
                continue

            if 'db_octgn' in conf['outputs']:
                tasks.append([generate_db_octgn, conf, set_id, set_name, lang,
                              skip_ids])

            if 'pdf' in conf['outputs']:
                tasks.append([generate_pdf, conf, set_id, set_name, lang,
                              skip_ids])

            if 'makeplayingcards' in conf['outputs']:
                tasks.append([generate_mpc, conf, set_id, set_name, lang,
                              skip_ids])

            if 'drivethrucards' in conf['outputs']:
                tasks.append([generate_dtc, conf, set_id, set_name, lang,
                              skip_ids])

    if tasks:
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
                return
    else:
        logging.info('No tasks to run, skipping')

    logging.info('Done (%ss)', round(time.time() - timestamp, 3))


if __name__ == '__main__':
    main()
