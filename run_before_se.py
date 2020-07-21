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
        set_id, _, set_row = set_data
        print('Processing set ID {}:'.format(set_id))
        lotr.backup_previous_xml(conf, set_id)
        lotr.generate_xml(conf, set_row)
        lotr.update_xml(conf, set_id)
        lotr.calculate_hashes(set_id)
        lotr.copy_raw_images(conf, set_id)
        lotr.copy_xml(set_id)

    lotr.create_project()
    print('Done')


if __name__ == '__main__':
    main()
