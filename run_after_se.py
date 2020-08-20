""" LotR ALeP workflow (Part 2, after Strange Eons).
"""
import lotr


def main():  # pylint: disable=R0912
    """ Main function.
    """
    conf = lotr.read_conf()
    sets = lotr.get_sets(conf)

    for set_data in sets:
        set_id, set_name, _ = set_data
        for lang in conf['languages']:
            print('Processing set {} ({}):'.format(set_name, lang))
            skip_ids = lotr.get_skip_cards(set_id, lang)

            if 'db_octgn' in conf['outputs']:
                lotr.generate_jpg300_nobleed(set_id, skip_ids)
            if 'pdf' in conf['outputs']:
                lotr.generate_png300_pdf(conf, set_id, skip_ids)
            if 'makeplayingcards' in conf['outputs']:
                lotr.generate_png800_bleedmpc(conf, set_id, skip_ids)
            if 'drivethrucards' in conf['outputs']:
                lotr.generate_png300_bleeddtc(conf, set_id, skip_ids)

            if 'db' in conf['outputs']:
                lotr.generate_db(set_id, set_name)
            if 'octgn' in conf['outputs']:
                lotr.generate_octgn(set_id, set_name)
            if 'pdf' in conf['outputs']:
                lotr.generate_pdf(set_id, set_name)
            if 'makeplayingcards_zip' in conf['outputs']:
                lotr.generate_mpc_zip(set_id, set_name)
            if 'makeplayingcards_7z' in conf['outputs']:
                lotr.generate_mpc_7z(set_id, set_name)
            if 'drivethrucards_zip' in conf['outputs']:
                lotr.generate_dtc_zip(set_id, set_name)
            if 'drivethrucards_7z' in conf['outputs']:
                lotr.generate_dtc_7z(set_id, set_name)

    print('Done')


if __name__ == '__main__':
    main()
