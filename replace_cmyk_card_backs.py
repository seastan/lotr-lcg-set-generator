# pylint: disable=C0209
""" Replace CMYK card backs in existing image archives.
"""
import logging
import os
import re
import shutil

import py7zr

import lotr


DOC_PATH = os.path.join('Docs', 'MBPrint.pdf')
ENCOUNTER_CARD_BACK_PATH = os.path.join(
    'imagesBack', 'encounterBackOfficialMBPrint.jpg')
MAGICK_PATH = 'C:\\Program Files\\ImageMagick-7.0.10-Q16-HDRI\\magick.exe'
OUTPUT_PATH = '\\\\MyCloudEX2Ultra\\Public\\Temp'
PLAYER_CARD_BACK_PATH = os.path.join(
    'imagesBack', 'playerBackOfficialMBPrint.jpg')
SEVENZ_PATH = 'c:\\Program Files (x86)\\7-Zip\\7z.exe'
TEMP_FOLDER = os.path.join('Temp', 'replace_cmyk_card_backs')
URLS_PATH = 'replace_cmyk_card_backs.txt'

OLD_ENCOUNTER_CARD_SIZE = 2264175
OLD_PLAYER_CARD_SIZE = 2764269

SEVENZ_READ_COMMAND = '"{}" x -o"{}" "{}"'
SEVENZ_SOURCE_FILENAME = 'source.7z'


def init_logging():
    """ Init logging.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')


def read_urls():
    """ Read the list of URLs.
    """
    with open(URLS_PATH, 'r', encoding='utf-8') as fobj:
        content = fobj.read()

    urls = [u.strip() for u in content.split('\n') if u.strip()]
    return urls


def write_urls(urls):
    """ Write the list of URLs.
    """
    with open(URLS_PATH, 'w', encoding='utf-8') as fobj:
        fobj.write('\n'.join(urls))


def download_archive(url):
    """ Download an image archive.
    """
    path = os.path.join(TEMP_FOLDER, SEVENZ_SOURCE_FILENAME)
    if re.match(r'^https?:', url):
        content = lotr.get_content(url)
        with open(path, 'wb') as fobj:
            fobj.write(content)
    else:
        shutil.copyfile(url, path)


def extract_archive():
    """ Extract the image archive.
    """
    path = os.path.join(TEMP_FOLDER, SEVENZ_SOURCE_FILENAME)
    cmd = SEVENZ_READ_COMMAND.format(SEVENZ_PATH, TEMP_FOLDER, path)
    res = lotr.run_cmd(cmd)
    logging.info(res)


def fix_content():
    """ Fix the content of the image archive.
    """
    folder_path = os.path.join(TEMP_FOLDER, 'back_official')
    player_count = 0
    encounter_count = 0
    for _, _, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(folder_path, filename)
            size = os.path.getsize(file_path)
            if size == OLD_PLAYER_CARD_SIZE:
                shutil.copyfile(PLAYER_CARD_BACK_PATH,
                                file_path)
                player_count += 1
            elif size == OLD_ENCOUNTER_CARD_SIZE:
                shutil.copyfile(ENCOUNTER_CARD_BACK_PATH,
                                file_path)
                encounter_count += 1

        break

    logging.info('Player card backs: %s', player_count)
    logging.info('Encounter card backs: %s', encounter_count)
    shutil.copyfile(DOC_PATH, os.path.join(TEMP_FOLDER, 'MBPrint.pdf'))


def move_image_files():
    """ Move image files to the root folder.
    """
    folder_path = os.path.join(TEMP_FOLDER, 'back_official')
    for _, _, filenames in os.walk(folder_path):
        for filename in filenames:
            shutil.move(os.path.join(folder_path, filename),
                        os.path.join(TEMP_FOLDER, filename))

        break

    folder_path = os.path.join(TEMP_FOLDER, 'back_unofficial')
    for _, _, filenames in os.walk(folder_path):
        for filename in filenames:
            shutil.move(os.path.join(folder_path, filename),
                        os.path.join(TEMP_FOLDER, filename))

        break

    folder_path = os.path.join(TEMP_FOLDER, 'front')
    for _, _, filenames in os.walk(folder_path):
        for filename in filenames:
            shutil.move(os.path.join(folder_path, filename),
                        os.path.join(TEMP_FOLDER, filename))

        break


def create_images_archive(archive_filename):
    """ Create a new image archive.
    """
    with py7zr.SevenZipFile(os.path.join(TEMP_FOLDER, archive_filename), 'w',
                            filters=lotr.PY7ZR_FILTERS) as obj:
        for _, _, filenames in os.walk(TEMP_FOLDER):
            for filename in filenames:
                if filename.endswith('-1o.jpg'):
                    obj.write(os.path.join(TEMP_FOLDER, filename),
                              'front/{}'.format(filename))
                elif filename.endswith('-2o.jpg'):
                    obj.write(os.path.join(TEMP_FOLDER, filename),
                              'back_official/{}'.format(filename))
                elif filename.endswith('-2u.jpg'):
                    obj.write(os.path.join(TEMP_FOLDER, filename),
                              'back_unofficial/{}'.format(filename))

            break

        obj.write(os.path.join(TEMP_FOLDER, 'MBPrint.pdf'), 'MBPrint.pdf')

    shutil.move(os.path.join(TEMP_FOLDER, archive_filename),
                os.path.join(OUTPUT_PATH, archive_filename))


def create_pdf(archive_filename):
    """ Create a new PDF file.
    """
    pdf_filename = archive_filename.replace('images.7z', 'pdf')
    cmd = lotr.MAGICK_COMMAND_MBPRINT_PDF.format(
        MAGICK_PATH, TEMP_FOLDER, os.sep,
        os.path.join(TEMP_FOLDER, pdf_filename))
    res = lotr.run_cmd(cmd)
    logging.info(res)


def create_pdf_archive(archive_filename):
    """ Create a new image archive.
    """
    pdf_filename = archive_filename.replace('images.7z', 'pdf')
    archive_filename = '{}.7z'.format(pdf_filename)
    with py7zr.SevenZipFile(os.path.join(TEMP_FOLDER, archive_filename), 'w',
                            filters=lotr.PY7ZR_FILTERS) as obj:
        obj.write(os.path.join(TEMP_FOLDER, pdf_filename), pdf_filename)


    shutil.move(os.path.join(TEMP_FOLDER, archive_filename),
                os.path.join(OUTPUT_PATH, archive_filename))


def process_archive(url):
    """ Process an image archive.
    """
    download_archive(url)
    extract_archive()
    fix_content()
    move_image_files()
    archive_filename = re.sub(r'\/(?:file)?$', '', url).replace(
        '\\', '/').split('/')[-1].replace('_', ' ')
    create_images_archive(archive_filename)
    create_pdf(archive_filename)
    create_pdf_archive(archive_filename)


def main():
    """ Main function.
    """
    urls = read_urls()
    if urls:
        logging.info('Processing %s URL(s) from the file...', len(urls))

    while urls:
        lotr.delete_folder(TEMP_FOLDER)
        lotr.create_folder(TEMP_FOLDER)
        url = urls.pop(0)
        logging.info('Processing %s...', url)
        process_archive(url)
        write_urls(urls)
        logging.info('...finished')

    lotr.delete_folder(TEMP_FOLDER)
    logging.info('Done')


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_logging()
    main()
