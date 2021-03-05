""" LotR ALeP workflow (Part 1, before Strange Eons).
"""
import logging
import sys
import time
import lotr


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')


def main():  # pylint: disable=R0912
    """ Main function.
    """
    timestamp = time.time()
    if len(sys.argv) > 1:
        conf = lotr.read_conf(sys.argv[1])
    else:
        conf = lotr.read_conf()

    lotr.reset_project_folders()
    lotr.download_sheet(conf)
    lotr.extract_data(conf)
    sets = lotr.get_sets(conf)
    lotr.sanity_check(conf, sets)

    strange_eons = False
    changes = False
    for set_id, set_name in sets:
        if conf['octgn_set_xml']:
            lotr.generate_octgn_set_xml(conf, set_id, set_name)

        if conf['octgn_o8d']:
            lotr.generate_octgn_o8d(conf, set_id, set_name)

        if conf['ringsdb_csv']:
            lotr.generate_ringsdb_csv(conf, set_id, set_name)

        if conf['hallofbeorn_json']:
            lotr.generate_hallofbeorn_json(conf, set_id, set_name)

        lotr.copy_custom_images(conf, set_id, set_name)
        for lang in conf['languages']:
            strange_eons = True
            lotr.generate_xml(conf, set_id, set_name, lang)
            lotr.update_xml(conf, set_id, set_name, lang)
            new_hash, old_hash = lotr.calculate_hashes(set_id, set_name, lang)
            if new_hash != old_hash:
                changes = True

            lotr.copy_raw_images(conf, set_id, set_name, lang)
            lotr.copy_xml(set_id, set_name, lang)

    lotr.copy_octgn_outputs(conf, sets)

    if changes:
        lotr.create_project()
    elif strange_eons:
        logging.info('No changes since the last run, skipping creating '
                     'Strange Eons project')
    else:
        logging.info('No Strange Eons outputs, skipping creating Strange Eons '
                     'project')

    logging.info('Done (%ss)', round(time.time() - timestamp, 3))


if __name__ == '__main__':
    init_logging()
    main()
