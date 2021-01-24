""" LotR ALeP workflow (Part 1, before Strange Eons).
"""
import logging
import sys
import time
import lotr

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')


def main():
    """ Main function.
    """
    timestamp = time.time()
    if len(sys.argv) > 1:
        conf = lotr.read_conf(sys.argv[1])
    else:
        conf = lotr.read_conf()

    lotr.reset_project_folders(conf)
    lotr.download_sheet(conf)
    lotr.extract_data(conf)
    sets = lotr.get_sets(conf)
    lotr.sanity_check(sets)

    strange_eons = False
    changes = False
    for set_id, set_name in sets:
        if conf['octgn_set_xml']:
            lotr.generate_octgn_set_xml(conf, set_id, set_name)

        if conf['ringsdb_csv']:
            lotr.generate_ringsdb_csv(set_id, set_name)

        if conf['hallofbeorn_json']:
            lotr.generate_hallofbeorn_json(set_id, set_name)

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

    if changes:
        if conf['octgn_set_xml'] and conf['octgn_destination_path']:
            lotr.copy_octgn_outputs(conf)

        lotr.create_project()
    elif strange_eons:
        logging.info('No changes since the last run, skipping creating '
                     'Strange Eons project')
    else:
        logging.info('No Strange Eons outputs, skipping creating Strange Eons '
                     'project')

    logging.info('Done (%ss)', round(time.time() - timestamp, 3))


if __name__ == '__main__':
    main()
