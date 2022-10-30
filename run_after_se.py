""" LotR workflow (Part 2).
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

            return None

        return _retry

    return _wrap


@retry()
def generate_png300_nobleed(conf, set_id, set_name, lang, skip_ids):
    """ Generate PNG 300 dpi images without bleed margins.
    """
    lotr.generate_png300_nobleed(conf, set_id, set_name, lang, skip_ids)


@retry()
def generate_png480_nobleed(conf, set_id, set_name, lang, skip_ids):
    """ Generate PNG 480 dpi images without bleed margins.
    """
    lotr.generate_png480_nobleed(conf, set_id, set_name, lang, skip_ids)


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
def generate_dragncards_hq(conf, set_id, set_name, lang, skip_ids,  # pylint: disable=R0913
                           card_data):
    """ Generate DragnCards HQ outputs.
    """
    lotr.generate_png480_dragncards_hq(set_id, set_name, lang, skip_ids)
    lotr.generate_dragncards_hq(conf, set_id, set_name, lang, card_data)


@retry()
def generate_octgn(conf, set_id, set_name, lang, skip_ids, card_data):  # pylint: disable=R0913
    """ Generate OCTGN outputs.
    """
    lotr.generate_png300_octgn(set_id, set_name, lang, skip_ids)
    lotr.generate_octgn(conf, set_id, set_name, lang, card_data)


@retry()
def generate_rules_pdf(conf, set_id, set_name, lang, skip_ids, card_data):  # pylint: disable=R0913
    """ Generate Rules PDF outputs.
    """
    lotr.generate_png300_rules_pdf(set_id, set_name, lang, skip_ids, card_data)
    lotr.generate_rules_pdf(conf, set_id, set_name, lang)


@retry()
def generate_pdf(conf, set_id, set_name, lang, skip_ids, card_data):  # pylint: disable=R0913
    """ Generate PDF outputs.
    """
    lotr.generate_png300_pdf(conf, set_id, set_name, lang, skip_ids)
    lotr.generate_pdf(conf, set_id, set_name, lang, card_data)


@retry()
def generate_genericpng_pdf(conf, set_id, set_name, lang, skip_ids, card_data):  # pylint: disable=R0913
    """ Generate generic PNG PDF outputs.
    """
    lotr.generate_png800_pdf(conf, set_id, set_name, lang, skip_ids)
    lotr.generate_genericpng_pdf(conf, set_id, set_name, lang, card_data)


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


@retry()
def generate_tts(conf, set_id, set_name, lang, card_dict, scratch):  # pylint: disable=R0913
    """ Generate TTS outputs.
    """
    lotr.generate_tts(conf, set_id, set_name, lang, card_dict, scratch)


@retry()
def generate_renderer_artwork(conf, set_id, set_name):
    """ Generate artwork for DragnCards proxy images.
    """
    lotr.generate_renderer_artwork(conf, set_id, set_name)


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

    processes = (min(4, max(1, cpu_count() - 1))
                 if conf['parallelism'] == 'default'
                 else conf['parallelism'])
    processes = min(processes, len(tasks))
    if processes == 1:
        for task in tasks:
            run(task)
    else:
        logging.info('Starting a pool of %s process(es) for %s task(s)',
                     processes, len(tasks))
        with Pool(processes=processes, initializer=initializer) as pool:
            try:
                pool.map(run, tasks)
            except KeyboardInterrupt as exc:
                logging.info('Program was terminated!')
                pool.terminate()
                raise KeyboardInterrupt from exc


def main():  # pylint: disable=R0912,R0914,R0915
    """ Main function.
    """
    timestamp = time.time()
    if len(sys.argv) > 1:
        conf = lotr.read_conf(sys.argv[1])
    else:
        conf = lotr.read_conf()

    lotr.extract_data(conf)
    sets = lotr.get_sets(conf)
    if os.path.exists(lotr.PROJECT_PATH):
        actual_sets = lotr.get_actual_sets()
    else:
        actual_sets = []

    pre_tasks = []
    tasks = []
    post_tasks = []
    for set_id, set_name in sets:
        scratch = set_id in lotr.FOUND_SCRATCH_SETS
        for lang in conf['output_languages']:
            if scratch and lang != 'English':
                continue

            skip_set, skip_ids = lotr.get_skip_info(set_id, lang)
            if skip_set:
                logging.info('[%s, %s] No changes since the last run,'
                             ' skipping', set_name, lang)
                continue

            if (set_id, lang) not in actual_sets:
                logging.error('[%s, %s] Not found in the project file,'
                              ' skipping', set_name, lang)
                continue

            card_data = lotr.translated_data(set_id, lang)
            card_dict = lotr.full_card_dict()

            if conf['nobleed_300'][lang]:
                pre_tasks.append([generate_png300_nobleed, conf, set_id,
                                  set_name, lang, skip_ids])

            if conf['nobleed_480'][lang]:
                pre_tasks.append([generate_png480_nobleed, conf, set_id,
                                  set_name, lang, skip_ids])

            if conf['nobleed_800'][lang]:
                pre_tasks.append([generate_png800_nobleed, conf, set_id,
                                  set_name, lang, skip_ids])

            if 'db' in conf['outputs'][lang]:
                tasks.append([generate_db, conf, set_id, set_name, lang,
                              skip_ids, card_data])

            if 'dragncards_hq' in conf['outputs'][lang]:
                tasks.append([generate_dragncards_hq, conf, set_id, set_name,
                              lang, skip_ids, card_data])

            if 'octgn' in conf['outputs'][lang]:
                tasks.append([generate_octgn, conf, set_id, set_name, lang,
                              skip_ids, card_data])

            if 'rules_pdf' in conf['outputs'][lang]:
                tasks.append([generate_rules_pdf, conf, set_id, set_name,
                              lang, skip_ids, card_data])

            if 'pdf' in conf['outputs'][lang]:
                tasks.append([generate_pdf, conf, set_id, set_name, lang,
                              skip_ids, card_data])

            if 'genericpng_pdf' in conf['outputs'][lang]:
                tasks.append([generate_genericpng_pdf, conf, set_id, set_name,
                              lang, skip_ids, card_data])

            if 'makeplayingcards' in conf['outputs'][lang]:
                tasks.append([generate_mpc, conf, set_id, set_name, lang,
                              skip_ids, card_data])

            if 'drivethrucards' in conf['outputs'][lang]:
                tasks.append([generate_dtc, conf, set_id, set_name, lang,
                              skip_ids, card_data])

            if 'mbprint' in conf['outputs'][lang]:
                tasks.append([generate_mbprint, conf, set_id, set_name, lang,
                              skip_ids, card_data])

            if 'genericpng' in conf['outputs'][lang]:
                tasks.append([generate_genericpng, conf, set_id, set_name,
                              lang, skip_ids, card_data])

            if 'tts' in conf['outputs'][lang]:
                post_tasks.append([generate_tts, conf, set_id, set_name, lang,
                                   card_dict, scratch])

        if conf['renderer_artwork']:
            post_tasks.append([generate_renderer_artwork, conf, set_id,
                               set_name])

    execute_tasks(conf, pre_tasks)
    execute_tasks(conf, tasks)
    execute_tasks(conf, post_tasks)

    lotr.check_messages()

    if 'English' in conf['output_languages']:
        updated_sets = [s for s in sets
                        if (s[0], 'English') in actual_sets
                        and not lotr.get_skip_info(s[0], 'English')[0]]
    else:
        updated_sets = []

    if (conf['db_destination_path'] and
            'English' in conf['output_languages'] and
            'db' in conf['outputs']['English'] and
            updated_sets):
        lotr.copy_db_outputs(conf, updated_sets)

    if (conf['octgn_image_destination_path'] and
            'English' in conf['output_languages'] and
            'octgn' in conf['outputs']['English'] and
            updated_sets):
        lotr.copy_octgn_image_outputs(conf, updated_sets)

    if (conf['tts_destination_path'] and
            'English' in conf['output_languages'] and
            'tts' in conf['outputs']['English'] and
            updated_sets):
        lotr.copy_tts_outputs(conf, updated_sets)

    if (updated_sets and
            conf['upload_dragncards'] and
            conf['dragncards_hostname'] and
            conf['dragncards_id_rsa_path']):
        lotr.upload_dragncards_images(conf, updated_sets)

    if os.path.exists(lotr.PIPELINE_STARTED_PATH):
        os.remove(lotr.PIPELINE_STARTED_PATH)

    if os.path.exists(lotr.REPROCESS_COUNT_PATH):
        os.remove(lotr.REPROCESS_COUNT_PATH)

    logging.info('Done (%ss)', round(time.time() - timestamp, 3))


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
