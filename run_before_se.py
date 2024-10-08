""" LotR workflow (Part 1).
"""
import json
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


def get_reprocess_count():
    """ Get the number of reprocessing attempts.
    """
    try:
        with open(lotr.REPROCESS_COUNT_PATH, 'r', encoding='utf-8') as fobj:
            data = json.load(fobj)
    except Exception:  # pylint: disable=W0703
        data = {'value': 0}

    return data.get('value', 0)


def save_reprocess_count(value):
    """ Save the number of reprocessing attempts.
    """
    data = {'value': value}
    with open(lotr.REPROCESS_COUNT_PATH, 'w', encoding='utf-8') as fobj:
        json.dump(data, fobj)


def main(conf=None):  # pylint: disable=R0912,R0914,R0915
    """ Main function.
    """
    timestamp = time.time()

    with open(lotr.RUN_BEFORE_SE_STARTED_PATH, 'w', encoding='utf-8'):
        pass

    if os.path.exists(lotr.SEPROJECT_CREATED_PATH):
        os.remove(lotr.SEPROJECT_CREATED_PATH)

    if not conf:
        if len(sys.argv) > 1:
            conf = lotr.read_conf(sys.argv[1])
        else:
            conf = lotr.read_conf()

    force_reprocessing = False
    if os.path.exists(lotr.REPROCESS_ALL_PATH):
        conf['reprocess_all'] = True
        force_reprocessing = True
        logging.info('Setting "reprocess_all" to "true" for this run')
        os.remove(lotr.REPROCESS_ALL_PATH)

    if (not conf['reprocess_all'] and conf['reprocess_all_on_error'] and
            os.path.exists(lotr.PIPELINE_STARTED_PATH)):
        conf['reprocess_all'] = True
        logging.info('The previous update did not succeed, setting '
                     '"reprocess_all" to "true" for this run')
        count = get_reprocess_count()
        if count >= lotr.REPROCESS_RETRIES:
            logging.info('Maximum number of reprocessing retries exceeded')
        else:
            force_reprocessing = True
            count += 1
            save_reprocess_count(count)
            logging.info('Reprocessing retry #%s', count)

    if (conf['upload_dragncards'] and
            conf['dragncards_hostname'] and
            conf['dragncards_id_rsa_path']):
        lotr.write_remote_dragncards_folder(conf)

    sheet_changes = lotr.download_sheet(conf)
    if force_reprocessing or not conf['exit_if_no_spreadsheet_changes']:
        sheet_changes = True

    if not sheet_changes:
        if os.path.exists(lotr.RUN_BEFORE_SE_STARTED_PATH):
            os.remove(lotr.RUN_BEFORE_SE_STARTED_PATH)

        logging.info('No spreadsheet changes, exiting')
        logging.info('Done (%ss)', round(time.time() - timestamp, 3))
        return False

    with open(lotr.PIPELINE_STARTED_PATH, 'w', encoding='utf-8'):
        pass

    lotr.extract_data(conf)
    sets = lotr.get_sets(conf)

    if conf['stable_data_user'] == 'reader':
        try:
            sets = lotr.sanity_check(conf, sets)
        except lotr.SanityCheckError as exc:
            logging.error(str(exc))
            logging.info(
                'Sanity check failed, retrying with the latest stable data...')
            lotr.read_stable_data(conf)
            lotr.extract_data(conf)
            sets = lotr.get_sets(conf)
            sets = lotr.sanity_check(conf, sets)
    else:
        sets = lotr.sanity_check(conf, sets)

    if conf['stable_data_user'] == 'writer':
        lotr.upload_stable_data()

    lotr.save_data_for_bot(conf, sets)

    if conf['renderer']:
        lotr.expire_dragncards_hashes()

    if conf['output_languages']:
        lotr.verify_images(conf)
        lotr.reset_project_folders(conf)

    eons = False
    changes = False
    renderer_sets = []
    for set_id, set_name in sets:
        scratch = set_id in lotr.FOUND_SCRATCH_SETS
        if conf['octgn_set_xml']:
            lotr.generate_octgn_set_xml(conf, set_id, set_name)

        if conf['octgn_o8d']:
            lotr.generate_octgn_o8d(conf, set_id, set_name)

        if conf['ringsdb_csv']:
            lotr.generate_ringsdb_csv(conf, set_id, set_name)

        if conf['frenchdb_csv']:
            lotr.generate_frenchdb_csv(conf, set_id, set_name)

        if conf['spanishdb_csv']:
            lotr.generate_spanishdb_csv(conf, set_id, set_name)

        if conf['hallofbeorn_json']:
            for lang in (conf['output_languages'] or [lotr.L_ENGLISH]):
                if scratch and lang != lotr.L_ENGLISH:
                    continue

                lotr.generate_hallofbeorn_json(conf, set_id, set_name, lang)

        if conf['output_languages']:
            lotr.copy_custom_images(conf, set_id, set_name)

        xml_generated = False
        xml_changed = False
        for lang in conf['output_languages']:
            if scratch and lang != lotr.L_ENGLISH:
                continue

            eons = True
            if lang == lotr.L_ENGLISH:
                xml_generated = True

            lotr.generate_xml(conf, set_id, set_name, lang)
            lotr.update_xml(conf, set_id, set_name, lang)
            file_changes, dragncards_changes = lotr.calculate_hashes(
                set_id, set_name, lang)
            if file_changes:
                changes = True
                if dragncards_changes and lang == lotr.L_ENGLISH:
                    xml_changed = True

            lotr.copy_raw_images(conf, set_id, set_name, lang)
            lotr.copy_xml(set_id, set_name, lang)

        if conf['renderer'] and not xml_generated:
            lotr.generate_xml(conf, set_id, set_name, lotr.L_ENGLISH)
            lotr.update_xml(conf, set_id, set_name, lotr.L_ENGLISH)
            _, dragncards_changes = lotr.calculate_hashes(set_id, set_name,
                                                          lotr.L_ENGLISH)
            if dragncards_changes:
                xml_changed = True

            xml_generated = True

        if conf['renderer'] and xml_changed:
            renderer_sets.append(set_id)

        if ((conf['renderer_artwork'] or conf['dragncards_json'])
                and not xml_generated):
            lotr.generate_xml(conf, set_id, set_name, lotr.L_ENGLISH)
            lotr.update_xml(conf, set_id, set_name, lotr.L_ENGLISH)
            lotr.calculate_hashes(set_id, set_name, lotr.L_ENGLISH)
            xml_generated = True

        if conf['dragncards_json']:
            lotr.generate_dragncards_json(conf, set_id, set_name)

    if conf['octgn_set_xml'] or conf['octgn_o8d']:
        lotr.copy_octgn_outputs(conf, sets)

    if conf['ringsdb_csv'] and conf['update_ringsdb']:
        lotr.update_ringsdb(conf, sets)

    if renderer_sets:
        lotr.generate_dragncards_proxies(renderer_sets)

    if (conf['upload_dragncards_lightweight'] and
            conf['dragncards_hostname'] and
            conf['dragncards_id_rsa_path']):
        lotr.upload_dragncards_lightweight_outputs(conf, sets)

    if changes:
        lotr.create_project()
        with open(lotr.SEPROJECT_CREATED_PATH, 'w', encoding='utf-8'):
            pass
    else:
        if not conf['renderer_artwork']:
            if os.path.exists(lotr.PIPELINE_STARTED_PATH):
                os.remove(lotr.PIPELINE_STARTED_PATH)

            if os.path.exists(lotr.REPROCESS_COUNT_PATH):
                os.remove(lotr.REPROCESS_COUNT_PATH)

        if eons:
            logging.info('No changes since the last run, skipping creating '
                         'the project')
        else:
            logging.info('No project outputs, skipping creating the project')

    if os.path.exists(lotr.RUN_BEFORE_SE_STARTED_PATH):
        os.remove(lotr.RUN_BEFORE_SE_STARTED_PATH)

    logging.info('Done (%ss)', round(time.time() - timestamp, 3))
    return True


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
