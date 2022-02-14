""" LotR ALeP workflow (Part 1, before Strange Eons).
"""
import logging
import os
import sys
import time
import lotr


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')


def main(conf=None):  # pylint: disable=R0912,R0915
    """ Main function.
    """
    timestamp = time.time()

    with open(lotr.RUN_BEFORE_SE_STARTED_PATH, 'w', encoding='utf-8'):
        pass

    if os.path.exists(lotr.PROJECT_CREATED_PATH):
        os.remove(lotr.PROJECT_CREATED_PATH)

    if not conf:
        if len(sys.argv) > 1:
            conf = lotr.read_conf(sys.argv[1])
        else:
            conf = lotr.read_conf()

    if (not conf['reprocess_all'] and conf['reprocess_all_on_error'] and
            os.path.exists(lotr.PIPELINE_STARTED_PATH)):
        conf['reprocess_all'] = True
        logging.info('The previous update did not succeed, setting '
                     '"reprocess_all" to "true" for this run')

    sheet_changes, scratch_changes = lotr.download_sheet(conf)
    if not conf['exit_if_no_spreadsheet_changes']:
        sheet_changes = True
        scratch_changes = True

    if not sheet_changes and not scratch_changes:
        if os.path.exists(lotr.RUN_BEFORE_SE_STARTED_PATH):
            os.remove(lotr.RUN_BEFORE_SE_STARTED_PATH)

        logging.info('No spreadsheet changes, exiting')
        logging.info('Done (%ss)', round(time.time() - timestamp, 3))
        return (sheet_changes, scratch_changes)

    with open(lotr.PIPELINE_STARTED_PATH, 'w', encoding='utf-8'):
        pass

    lotr.extract_data(conf, sheet_changes, scratch_changes)
    sets = lotr.get_sets(conf, sheet_changes, scratch_changes)
    sets = lotr.sanity_check(conf, sets)
    if sheet_changes:
        lotr.save_data_for_bot(conf)

    if conf['output_languages']:
        lotr.verify_images(conf)
        lotr.reset_project_folders(conf)

    strange_eons = False
    changes = False
    for set_id, set_name in sets:
        scratch = set_id in lotr.FOUND_SCRATCH_SETS
        if conf['octgn_set_xml']:
            lotr.generate_octgn_set_xml(conf, set_id, set_name)

        if conf['octgn_o8d']:
            lotr.generate_octgn_o8d(conf, set_id, set_name)

        if conf['ringsdb_csv']:
            lotr.generate_ringsdb_csv(conf, set_id, set_name)

        if conf['dragncards_json']:
            lotr.generate_dragncards_json(conf, set_id, set_name)

        if conf['frenchdb_csv']:
            lotr.generate_frenchdb_csv(conf, set_id, set_name)

        if conf['spanishdb_csv']:
            lotr.generate_spanishdb_csv(conf, set_id, set_name)

        if conf['hallofbeorn_json']:
            for lang in (conf['output_languages'] or ['English']):
                if scratch and lang != 'English':
                    continue

                lotr.generate_hallofbeorn_json(conf, set_id, set_name, lang)

        if conf['output_languages']:
            lotr.copy_custom_images(conf, set_id, set_name)

        for lang in conf['output_languages']:
            if scratch and lang != 'English':
                continue

            strange_eons = True
            lotr.generate_xml(conf, set_id, set_name, lang)
            lotr.update_xml(conf, set_id, set_name, lang)
            new_hash, old_hash = lotr.calculate_hashes(set_id, set_name, lang)
            if new_hash != old_hash:
                changes = True

            lotr.copy_raw_images(conf, set_id, set_name, lang)
            lotr.copy_xml(set_id, set_name, lang)

    if conf['octgn_set_xml'] or conf['octgn_o8d']:
        lotr.copy_octgn_outputs(conf, sets)

    if conf['ringsdb_csv'] and conf['update_ringsdb']:
        lotr.update_ringsdb(conf, sets)

    if changes:
        lotr.create_project()
        with open(lotr.PROJECT_CREATED_PATH, 'w', encoding='utf-8'):
            pass
    else:
        if os.path.exists(lotr.PIPELINE_STARTED_PATH):
            os.remove(lotr.PIPELINE_STARTED_PATH)

        if strange_eons:
            logging.info('No changes since the last run, skipping creating '
                         'Strange Eons project')
        else:
            logging.info('No Strange Eons outputs, skipping creating Strange '
                         'Eons project')

    if os.path.exists(lotr.RUN_BEFORE_SE_STARTED_PATH):
        os.remove(lotr.RUN_BEFORE_SE_STARTED_PATH)

    logging.info('Done (%ss)', round(time.time() - timestamp, 3))
    return (sheet_changes, scratch_changes)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
