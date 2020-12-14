""" LotR ALeP workflow (Part 2, after Strange Eons).
"""
import logging
import signal
import time
from multiprocessing import Pool, cpu_count

import lotr

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')


def generate_png300_nobleed(conf, set_id, set_name, lang, skip_ids):
    """ Generate images without bleed margins.
    """
    lotr.generate_png300_nobleed(conf, set_id, set_name, lang, skip_ids)


def generate_db(conf, set_id, set_name, lang, skip_ids):
    """ Generate DB outputs.
    """
    lotr.generate_png300_db(conf, set_id, set_name, lang, skip_ids)
    lotr.generate_db(set_id, set_name, lang)


def generate_octgn(set_id, set_name, lang, skip_ids):
    """ Generate OCTGN outputs.
    """
    lotr.generate_png300_octgn(set_id, set_name, lang, skip_ids)
    lotr.generate_octgn(set_id, set_name, lang)


def generate_pdf(conf, set_id, set_name, lang, skip_ids):
    """ Generate PDF outputs.
    """
    lotr.generate_png300_pdf(conf, set_id, set_name, lang, skip_ids)
    lotr.generate_pdf(conf, set_id, set_name, lang)


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
    conf = lotr.read_conf()
    sets = lotr.get_sets(conf)

    pre_tasks = []
    tasks = []
    for set_data in sets:
        set_id, set_name, _ = set_data
        for lang in conf['languages']:
            skip_set, skip_ids = lotr.get_skip_info(set_id, set_name, lang)
            if skip_set:
                logging.info('[%s, %s] No changes since the last run,'
                             ' skipping', set_name, lang)
                continue

            if conf['nobleed'][lang]:
                pre_tasks.append([generate_png300_nobleed, conf, set_id,
                                  set_name, lang, skip_ids])

            if 'db' in conf['outputs'][lang]:
                tasks.append([generate_db, conf, set_id, set_name, lang,
                              skip_ids])

            if 'octgn' in conf['outputs'][lang]:
                tasks.append([generate_octgn, set_id, set_name, lang,
                              skip_ids])

            if 'pdf' in conf['outputs'][lang]:
                tasks.append([generate_pdf, conf, set_id, set_name, lang,
                              skip_ids])

            if 'makeplayingcards' in conf['outputs'][lang]:
                tasks.append([generate_mpc, conf, set_id, set_name, lang,
                              skip_ids])

            if 'drivethrucards' in conf['outputs'][lang]:
                tasks.append([generate_dtc, conf, set_id, set_name, lang,
                              skip_ids])

    execute_tasks(conf, pre_tasks)
    execute_tasks(conf, tasks)
    logging.info('Done (%ss)', round(time.time() - timestamp, 3))


if __name__ == '__main__':
    main()
