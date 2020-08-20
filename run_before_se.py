""" LotR ALeP workflow (Part 1, before Strange Eons).
"""
import lotr


def main():
    """ Main function.
    """
    conf = lotr.read_conf()
    lotr.clear_project_folders()
    lotr.download_sheet(conf)
    sets = lotr.get_sets(conf)

    for set_data in sets:
        set_id, set_name, set_row = set_data
        if 'octgn' in conf['outputs']:
            lotr.generate_octgn_xml(conf, set_name, set_row)

        for lang in conf['languages']:
            print('Processing set {} ({}):'.format(set_name, lang))
            lotr.backup_previous_xml(conf, set_id, lang)
            lotr.generate_xml(conf, set_row, lang)
            lotr.update_xml(conf, set_id, lang)
            lotr.calculate_hashes(set_id, lang)
            lotr.copy_raw_images(conf, set_id, lang)
            lotr.copy_xml(set_id, lang)

    lotr.create_project()
    print('Done')


if __name__ == '__main__':
    main()
