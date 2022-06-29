""" Move images from the nightly pipeline to the destination folder.
"""
import logging
import os
import shutil
import sys


DESTINATION_PATH = '/mnt/volume_postgres/cards/English/'
LOG_PATH = 'images_finish.log'


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')


def main():  # pylint: disable=R0912
    """ Main function.
    """
    if len(sys.argv) <= 1 or not sys.argv[1]:
        logging.error('No folder specified')
        sys.exit(1)

    source_folder = sys.argv[1]
    if not os.path.exists(source_folder):
        logging.error("Folder %s doesn't exist", source_folder)
        sys.exit(1)

    timestamp = os.path.split(source_folder)[-1]
    if not timestamp.isdigit():
        logging.error('Folder %s has incorrect name', source_folder)
        sys.exit(1)

    logging.info('Processing folder %s', source_folder)

    timestamp = int(timestamp)
    parent_folder = os.path.join(*os.path.split(source_folder)[:-1])
    for _, folders, _ in os.walk(parent_folder):
        for folder in folders:
            if folder.isdigit() and int(folder) < timestamp:
                path = os.path.join(parent_folder, folder)
                logging.warning('Removing old folder %s', path)
                shutil.rmtree(path, ignore_errors=True)

        break

    for _, _, filenames in os.walk(source_folder):
        if not filenames:
            logging.warning('No files in %s', source_folder)
            break

        for filename in filenames:
            source_path = os.path.join(source_folder, filename)
            if not filename.endswith('.jpg'):
                logging.warning('Unknown file %s', source_path)
                continue

            destination_path = os.path.join(DESTINATION_PATH, filename)
            if os.path.exists(destination_path):
                mtime = int(os.path.getmtime(destination_path))
                if timestamp > mtime:
                    logging.info('Overwriting existing file %s',
                                 destination_path)
                    shutil.move(source_path, destination_path)
                else:
                    logging.info('Skipping more recent file %s',
                                 destination_path)
            else:
                logging.info('Moving new file %s', destination_path)
                shutil.move(source_path, destination_path)

        break

    shutil.rmtree(source_folder, ignore_errors=True)
    print('Done')


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
