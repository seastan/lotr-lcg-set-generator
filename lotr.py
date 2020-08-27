# pylint: disable=C0302
""" Helper functions for LotR ALeP workflow.
"""
import hashlib
import math
import os
import re
import shutil
import subprocess
import zipfile

import xml.etree.ElementTree as ET
import png
import py7zr
import requests
import xlwings as xw
import yaml

from reportlab.lib.pagesizes import landscape, letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas

GIMP_COMMAND = '"{}" -i -b "({} 1 \\"{}\\" \\"{}\\")" -b "(gimp-quit 0)"'
PROJECT_FOLDER = 'Frogmorton'
SHEET_NAME = 'setExcel'
TEXT_CHUNK_FLAG = b'tEXt'

CONFIGURATION_PATH = 'configuration.yaml'
IMAGES_BACK_PATH = 'imagesBack'
IMAGES_EONS_PATH = 'imagesEons'
IMAGES_RAW_PATH = os.path.join(PROJECT_FOLDER, 'imagesRaw')
IMAGES_ZIP_PATH = '{}/Export/'.format(os.path.split(PROJECT_FOLDER)[-1])
MACROS_PATH = 'macros.xlsm'
MACROS_COPY_PATH = 'macros_copy.xlsm'
OCTGN_ZIP_PATH = 'imagesOCTGN/a21af4e8-be4b-4cda-a6b6-534f9717391f/Sets'
OUTPUT_DB_PATH = os.path.join('Output', 'DB')
OUTPUT_DTC_PATH = os.path.join('Output', 'DriveThruCards')
OUTPUT_MPC_PATH = os.path.join('Output', 'MakePlayingCards')
OUTPUT_OCTGN_PATH = os.path.join('Output', 'OCTGN')
OUTPUT_PDF_PATH = os.path.join('Output', 'PDF')
PROJECT_PATH = 'setGenerator.seproject'
SET_EONS_PATH = 'setEons'
SHEET_ROOT_PATH = ''
TEMP_PATH = 'Temp'
XML_PATH = os.path.join(PROJECT_FOLDER, 'XML')


def _clear_folder(folder):
    """ Clear the folder.
    """
    for _, _, filenames in os.walk(folder):
        for filename in filenames:
            if filename not in ('seproject', '.gitignore'):
                os.remove(os.path.join(folder, filename))

        break


def _get_artwork_path(conf, set_id):
    """ Get path to the folder with the cropped artwork.
    """
    artwork_path = os.path.join(conf['artwork_path'], set_id)
    if not os.path.exists(artwork_path):
        artwork_path = conf['artwork_path']

    return artwork_path


def _find_properties(parent, name):
    """ Find properties with a given name.
    """
    properties = [p for p in parent if p.attrib.get('name') == name]
    return properties


def _create_folder(folder):
    """ Create the folder if needed.
    """
    if not os.path.exists(folder):
        os.mkdir(folder)


def _clear_modified_images(folder, skip_ids):
    """ Delete images for outdated or modified cards inside the folder.
    """
    for _, _, filenames in os.walk(folder):
        for filename in filenames:
            if filename.split('.')[-1] in ('jpg', 'png'):
                card_id = filename[50:86]
                if card_id not in skip_ids:
                    os.remove(os.path.join(folder, filename))

        break


def _update_zip_filename(filename):
    """ Update filename found in the Strange Eons project archive.
    """
    output_filename = os.path.split(filename)[-1]
    output_filename = output_filename.encode('ascii', errors='replace'
                                             ).decode().replace('?', ' ')
    parts = output_filename.split('.')
    output_filename = '.'.join(parts[:-3] + [parts[-1]])
    output_filename = re.sub(r'-2-1(?=\.(?:jpg|png)$)', '-2', output_filename)
    return output_filename


def read_conf():
    """ Read project configuration.
    """
    print('Reading project configuration')
    with open(CONFIGURATION_PATH, 'r') as f_conf:
        conf = yaml.safe_load(f_conf)

    conf['outputs'] = set(conf['outputs'])
    if 'db' in conf['outputs'] or 'octgn' in conf['outputs']:
        conf['outputs'].add('db_octgn')

    if ('makeplayingcards_zip' in conf['outputs']
            or 'makeplayingcards_7z' in conf['outputs']):
        conf['outputs'].add('makeplayingcards')

    if ('drivethrucards_zip' in conf['outputs']
            or 'drivethrucards_7z' in conf['outputs']):
        conf['outputs'].add('drivethrucards')

    return conf


def clear_project_folders():
    """ Clear raw image files and xml files in the project folders.
    """
    print('Clearing the project folders')
    _clear_folder(IMAGES_RAW_PATH)
    _clear_folder(XML_PATH)


def download_sheet(conf):
    """ Download cards spreadsheet from Google Drive.
    """
    print('Downloading cards spreadsheet from Google Drive')
    sheet_path = os.path.join(SHEET_ROOT_PATH,
                              '{}.{}'.format(SHEET_NAME, conf['sheet_type']))
    if conf['sheet_type'] == 'xlsm':
        url = ('https://drive.google.com/uc?export=download&id={}'
               .format(conf['sheet_gdid']))
    else:
        url = ('https://docs.google.com/spreadsheets/d/{}/export?format=xlsx'
               .format(conf['sheet_gdid']))

    with open(sheet_path, 'wb') as f_sheet:
        f_sheet.write(requests.get(url).content)


def get_sets(conf):
    """ Get all sets to work on and return (id, name, row) tuples.
    """
    print('Getting all sets to work on')
    sheet_path = os.path.join(SHEET_ROOT_PATH,
                              '{}.{}'.format(SHEET_NAME, conf['sheet_type']))

    excel_app = xw.App(visible=False, add_book=False)
    try:
        xlwb = excel_app.books.open(sheet_path)
        try:
            sets = []
            sheet = xlwb.sheets['Sets']
            for row in range(3, 103):
                set_id = sheet.range((row, 1)).value
                if set_id and set_id in conf['set_ids']:
                    sets.append((set_id, sheet.range((row, 2)).value, row))
        finally:
            xlwb.close()
    finally:
        excel_app.quit()

    if not sets:
        print('No sets found')

    return sets


def backup_previous_xml(conf, set_id, lang):
    """ Backup a previous Strange Eons xml file.
    """
    print('  Backing up a previous Strange Eons xml file')
    new_path = os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id, lang))
    old_path = os.path.join(SET_EONS_PATH, '{}.{}.xml.old'.format(set_id,
                                                                  lang))
    if os.path.exists(new_path):
        shutil.move(new_path, old_path)

    if conf['from_scratch'] and os.path.exists(old_path):
        os.remove(old_path)


def _run_macro(conf, set_row, callback):
    """ Prepare a context to run an Excel macro and execute the callback.
    """
    shutil.copyfile(MACROS_PATH, MACROS_COPY_PATH)
    sheet_path = os.path.join(SHEET_ROOT_PATH,
                              '{}.{}'.format(SHEET_NAME, conf['sheet_type']))

    excel_app = xw.App(visible=False, add_book=False)
    try:
        xlwb_source = excel_app.books.open(sheet_path)
        try:
            xlwb_target = excel_app.books.open(MACROS_COPY_PATH)
            try:
                data = xlwb_source.sheets['Sets'].range(
                    'A{}:C{}'.format(set_row, set_row)).value  # pylint: disable=W1308
                xlwb_target.sheets['Sets'].range('A3:C3').value = data

                card_sheet = xlwb_target.sheets['Card Data']
                data = xlwb_source.sheets['Card Data'].range('A2:AU1001').value
                card_sheet.range('A2:AU1001').value = data
                card_sheet.range('A2:AU1001').api.Sort(
                    Key1=card_sheet.range('Set').api,
                    Order1=xw.constants.SortOrder.xlAscending,
                    Key2=card_sheet.range('CardNumber').api,
                    Order2=xw.constants.SortOrder.xlAscending)

                callback(xlwb_source, xlwb_target)
                xlwb_target.save()
            finally:
                xlwb_target.close()
        finally:
            xlwb_source.close()
    finally:
        excel_app.quit()


def generate_octgn_xml(conf, set_name, set_row):
    """ Generate set.xml file for OCTGN.
    """
    def _callback(_, xlwb_target):
        xlwb_target.macro('SaveOCTGN')()

    print('Generating set.xml file for OCTGN for set {}'.format(set_name))
    _run_macro(conf, set_row, _callback)


def generate_xml(conf, set_id, set_row, lang):
    """ Generate xml file for Strange Eons.
    """
    def _callback(xlwb_source, xlwb_target):
        if lang != 'English':
            translated = []
            tr_sheet = xlwb_source.sheets[lang]
            for source_row in range(2, 1002):
                if tr_sheet.range((source_row, 1)).value == set_id:
                    card_id = tr_sheet.range((source_row, 2)).value
                    if card_id:
                        translated.append((card_id, source_row))

            tr_ranges = ['G{}:G{}', 'K{}:L{}', 'V{}:X{}', 'Z{}:Z{}',
                         'AD{}:AE{}', 'AO{}:AQ{}', 'AU{}:AU{}']
            api = xlwb_target.sheets['Card Data'].api
            card_sheet = xlwb_target.sheets['Card Data']
            for card_id, source_row in translated:
                cell = api.UsedRange.Find(card_id)
                if cell:
                    target_row = cell.row
                    for tr_range in tr_ranges:
                        source_range = tr_range.format(source_row, source_row)
                        target_range = tr_range.format(target_row, target_row)
                        data = tr_sheet.range(source_range).value
                        card_sheet.range(target_range).value = data

        xlwb_target.sheets['Sets'].range('D3').value = lang
        xlwb_target.macro('SaveXML')()

    print('  Generating xml file for Strange Eons')
    _run_macro(conf, set_row, _callback)


def _collect_artwork_images(artwork_path):
    """ Collect artwork filenames.
    """
    images = {}
    for _, _, filenames in os.walk(artwork_path):
        for filename in filenames:
            if filename.split('.')[-1] in ('jpg', 'png'):
                card_id_side = '_'.join(filename.split('_')[:2])
                images[card_id_side] = filename

        break

    return images


def _set_outputs(conf, root):
    """ Set required outputs for Strange Eons.
    """
    if 'db_octgn' in conf['outputs']:
        root.set('jpg300NoBleed', '1')

    if 'pdf' in conf['outputs']:
        root.set('png300NoBleed', '1')

    if 'pdf' in conf['outputs'] or 'drivethrucards' in conf['outputs']:
        root.set('png300Bleed', '1')

    if 'makeplayingcards' in conf['outputs']:
        root.set('png800Bleed', '1')


def _get_property(parent, name):
    """ Get new or existing property with a given name.
    """
    properties = _find_properties(parent, name)
    if properties:
        prop = properties[0]
    else:
        prop = ET.SubElement(parent, 'property')
        prop.set('name', name)

    return prop


def update_xml(conf, set_id, lang):  # pylint: disable=R0914,R0915
    """ Update the Strange Eons xml file with additional data.
    """
    print('  Updating the Strange Eons xml file with additional data')
    artwork_path = _get_artwork_path(conf, set_id)
    images = _collect_artwork_images(artwork_path)
    xml_path = os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id, lang))

    tree = ET.parse(xml_path)
    root = tree.getroot()
    _set_outputs(conf, root)
    encounter_sets = {}
    encounter_cards = {}

    for card in root[0]:
        card_type = _find_properties(card, 'Type')
        if not card_type:
            print('ERROR: Skipping a card without card type')
            continue

        card_type = card_type[0].attrib['value']
        encounter_set = _find_properties(card, 'Encounter Set')
        if card_type != 'Quest' and encounter_set:
            encounter_set = encounter_set[0].attrib['value']
            encounter_cards[card.attrib['id']] = encounter_set
            prop = _get_property(card, 'Encounter Set Number')
            prop.set('value', str(encounter_sets.get(encounter_set, 0) + 1))
            quantity = int(
                _find_properties(card, 'Quantity')[0].attrib['value'])
            encounter_sets[encounter_set] = (
                encounter_sets.get(encounter_set, 0) + quantity)

        filename = images.get('{}_{}'.format(card.attrib['id'], 'A'))
        if filename:
            prop = _get_property(card, 'Artwork')
            prop.set('value', filename)
            prop = _get_property(card, 'Artwork Size')
            prop.set('value', str(os.path.getsize(os.path.join(artwork_path,
                                                               filename))))
            prop = _get_property(card, 'Artwork Modified')
            prop.set('value', str(int(os.path.getmtime(
                os.path.join(artwork_path, filename)))))

            artist = _find_properties(card, 'Artist')
            if not artist and '_Artist_' in filename:
                prop = _get_property(card, 'Artist')
                prop.set('value', '.'.join(
                    '_Artist_'.join(filename.split('_Artist_')[1:]
                                    ).split('.')[:-1]).replace('_', ' '))

        filename = images.get('{}_{}'.format(card.attrib['id'], 'B'))
        alternate = [a for a in card if a.attrib.get('type') == 'B']
        if filename and alternate:
            alternate = alternate[0]
            prop = _get_property(alternate, 'Artwork')
            prop.set('value', filename)
            prop = _get_property(alternate, 'Artwork Size')
            prop.set('value', str(os.path.getsize(os.path.join(artwork_path,
                                                               filename))))
            prop = _get_property(alternate, 'Artwork Modified')
            prop.set('value', str(int(os.path.getmtime(
                os.path.join(artwork_path, filename)))))

            artist = _find_properties(alternate, 'Artist')
            if not artist and '_Artist_' in filename:
                prop = _get_property(alternate, 'Artist')
                prop.set('value', '.'.join(
                    '_Artist_'.join(filename.split('_Artist_')[1:]
                                    ).split('.')[:-1]).replace('_', ' '))

    for card in root[0]:
        if card.attrib['id'] in encounter_cards:
            prop = _get_property(card, 'Encounter Set Total')
            prop.set('value', str(
                encounter_sets[encounter_cards[card.attrib['id']]]))

    tree.write(xml_path)


def calculate_hashes(set_id, lang):
    """ Update the Strange Eons xml file with hashes and skip flags.
    """
    print('  Updating the Strange Eons xml file with hashes and skip flags')
    new_path = os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id, lang))
    tree = ET.parse(new_path)
    root = tree.getroot()

    for card in root[0]:
        card_hash = hashlib.md5(
            re.sub(r'\n\s*', '', ET.tostring(card, encoding='unicode').strip()
                   ).encode()).hexdigest()
        card.set('hash', card_hash)

    new_file_hash = hashlib.md5(
        re.sub(r'\n\s*', '', ET.tostring(root, encoding='unicode').strip()
               ).encode()).hexdigest()
    root.set('hash', new_file_hash)

    old_file_hash = ''
    old_path = os.path.join(SET_EONS_PATH, '{}.{}.xml.old'.format(set_id,
                                                                  lang))
    if os.path.exists(old_path):
        old_hashes = {}
        skip_ids = set()

        tree_old = ET.parse(old_path)
        root_old = tree_old.getroot()
        old_file_hash = root_old.attrib['hash']
        if old_file_hash == new_file_hash:
            root.set('skip', '1')

        for card in root_old[0]:
            old_hashes[card.attrib['id']] = card.attrib['hash']

        for card in root[0]:
            if old_hashes.get(card.attrib['id']) == card.attrib['hash']:
                skip_ids.add(card.attrib['id'])
                card.set('skip', '1')

    tree.write(new_path)
    return (new_file_hash, old_file_hash)


def copy_raw_images(conf, set_id, lang):
    """ Copy raw image files into the project folder.
    """
    print('  Copying raw image files into the project folder')
    artwork_path = _get_artwork_path(conf, set_id)
    tree = ET.parse(os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id,
                                                                   lang)))
    root = tree.getroot()
    for card in root[0]:
        if card.attrib.get('skip') != '1':
            filename = _find_properties(card, 'Artwork')
            if filename:
                filename = filename[0].attrib['value']
                path = os.path.join(IMAGES_RAW_PATH, filename)
                if not os.path.exists(path):
                    shutil.copyfile(os.path.join(artwork_path, filename), path)

            alternate = [a for a in card if a.attrib.get('type') == 'B']
            if alternate:
                alternate = alternate[0]
                filename = _find_properties(alternate, 'Artwork')
                if filename:
                    filename = filename[0].attrib['value']
                    path = os.path.join(IMAGES_RAW_PATH, filename)
                    if not os.path.exists(path):
                        shutil.copyfile(os.path.join(artwork_path, filename),
                                        path)


def copy_xml(set_id, lang):
    """ Copy the Strange Eons xml file into the project.
    """
    print('  Copying the Strange Eons xml file into the project')
    shutil.copyfile(os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id,
                                                                   lang)),
                    os.path.join(XML_PATH, '{}.{}.xml'.format(set_id, lang)))


def create_project():
    """ Create a Strange Eons project archive.
    """
    print('Creating a Strange Eons project archive')
    with zipfile.ZipFile(PROJECT_PATH, 'w') as zip_obj:
        for root, _, filenames in os.walk(PROJECT_FOLDER):
            for filename in filenames:
                zip_obj.write(os.path.join(root, filename))


def get_skip_cards(set_id, lang):
    """ Get cards to skip.
    """
    print('  Getting cards to skip')
    skip_ids = set()
    tree = ET.parse(os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id,
                                                                   lang)))
    root = tree.getroot()
    for card in root[0]:
        if card.attrib.get('skip') == '1':
            skip_ids.add(card.attrib['id'])

    return skip_ids


def generate_jpg300_nobleed(set_id, lang, skip_ids):
    """ Generate images for DB and OCTGN outputs.
    """
    print('  Generating images for DB and OCTGN outputs')
    output_path = os.path.join(IMAGES_EONS_PATH, 'jpg300NoBleed',
                               '{}.{}'.format(set_id, lang))
    _create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)

    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  'jpg300NoBleed'))
                    and f.split('.')[-1] == 'jpg'
                    and f.split('.')[-2] == lang
                    and f.split('.')[-3] == set_id]
        for filename in filelist:
            output_filename = _update_zip_filename(filename)
            with zip_obj.open(filename) as zip_file:
                with open(os.path.join(output_path, output_filename),
                          'wb') as output_file:
                    shutil.copyfileobj(zip_file, output_file)


def generate_png300_pdf(conf, set_id, lang, skip_ids):
    """ Generate images for PDF outputs.
    """
    print('  Generating images for PDF outputs')
    output_path = os.path.join(IMAGES_EONS_PATH, 'png300PDF',
                               '{}.{}'.format(set_id, lang))
    _create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)
    _clear_folder(TEMP_PATH)

    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  'png300Bleed'))
                    and f.split('.')[-1] == 'png'
                    and f.split('.')[-2] == lang
                    and f.split('.')[-3] == set_id]
        for filename in filelist:
            output_filename = _update_zip_filename(filename)
            if output_filename.endswith('-2.png'):
                with zip_obj.open(filename) as zip_file:
                    with open(os.path.join(TEMP_PATH, output_filename),
                              'wb') as output_file:
                        shutil.copyfileobj(zip_file, output_file)

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-pdf-back-folder',
        TEMP_PATH.replace('\\', '\\\\'),
        output_path.replace('\\', '\\\\'))
    res = subprocess.run(cmd, capture_output=True, shell=True, check=True)
    print('    {}'.format(res))

    _clear_folder(TEMP_PATH)

    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  'png300NoBleed'))
                    and f.split('.')[-1] == 'png'
                    and f.split('.')[-2] == lang
                    and f.split('.')[-3] == set_id]
        for filename in filelist:
            output_filename = _update_zip_filename(filename)
            if output_filename.endswith('-1.png'):
                with zip_obj.open(filename) as zip_file:
                    with open(os.path.join(TEMP_PATH, output_filename),
                              'wb') as output_file:
                        shutil.copyfileobj(zip_file, output_file)

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-pdf-front-folder',
        TEMP_PATH.replace('\\', '\\\\'),
        output_path.replace('\\', '\\\\'))
    res = subprocess.run(cmd, capture_output=True, shell=True, check=True)
    print('    {}'.format(res))

    _clear_folder(TEMP_PATH)


def generate_png800_bleedmpc(conf, set_id, lang, skip_ids):
    """ Generate images for MakePlayingCards outputs.
    """
    print('  Generating images for MakePlayingCards outputs')
    output_path = os.path.join(IMAGES_EONS_PATH, 'png800BleedMPC',
                               '{}.{}'.format(set_id, lang))
    _create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)
    _clear_folder(TEMP_PATH)

    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  'png800Bleed'))
                    and f.split('.')[-1] == 'png'
                    and f.split('.')[-2] == lang
                    and f.split('.')[-3] == set_id]
        for filename in filelist:
            output_filename = _update_zip_filename(filename)
            with zip_obj.open(filename) as zip_file:
                with open(os.path.join(TEMP_PATH, output_filename),
                          'wb') as output_file:
                    shutil.copyfileobj(zip_file, output_file)

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-makeplayingcards-folder',
        TEMP_PATH.replace('\\', '\\\\'),
        output_path.replace('\\', '\\\\'))
    res = subprocess.run(cmd, capture_output=True, shell=True, check=True)
    print('    {}'.format(res))

    _clear_folder(TEMP_PATH)


def generate_jpg300_bleeddtc(conf, set_id, lang, skip_ids):
    """ Generate images for DriveThruCards outputs.
    """
    print('  Generating images for DriveThruCards outputs')
    output_path = os.path.join(IMAGES_EONS_PATH, 'jpg300BleedDTC',
                               '{}.{}'.format(set_id, lang))
    _create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)
    _clear_folder(TEMP_PATH)

    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  'png300Bleed'))
                    and f.split('.')[-1] == 'png'
                    and f.split('.')[-2] == lang
                    and f.split('.')[-3] == set_id]
        for filename in filelist:
            output_filename = _update_zip_filename(filename)
            with zip_obj.open(filename) as zip_file:
                with open(os.path.join(TEMP_PATH, output_filename),
                          'wb') as output_file:
                    shutil.copyfileobj(zip_file, output_file)

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-drivethrucards-folder',
        TEMP_PATH.replace('\\', '\\\\'),
        output_path.replace('\\', '\\\\'))
    res = subprocess.run(cmd, capture_output=True, shell=True, check=True)
    print('    {}'.format(res))

    _clear_folder(TEMP_PATH)


def generate_db(set_id, set_name, lang):
    """ Generate DB outputs.
    """
    print('  Generating DB outputs')
    input_path = os.path.join(IMAGES_EONS_PATH, 'jpg300NoBleed',
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_DB_PATH, '{}.{}'.format(set_name, lang))
    _create_folder(output_path)
    _clear_folder(output_path)

    known_filenames = set()
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            if filename.split('.')[-1] != 'jpg':
                continue

            output_filename = '{}-{}{}{}'.format(
                filename[:3],
                re.sub('-+$', '', filename[8:50]),
                re.sub('-1$', '', filename[86:88]),
                filename[88:])
            if output_filename not in known_filenames:
                known_filenames.add(output_filename)
                shutil.copyfile(os.path.join(input_path, filename),
                                os.path.join(output_path, output_filename))

        break


def generate_octgn(set_id, set_name, lang):
    """ Generate OCTGN outputs.
    """
    print('  Generating OCTGN outputs')
    input_path = os.path.join(IMAGES_EONS_PATH, 'jpg300NoBleed',
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_OCTGN_PATH, set_name)
    _create_folder(output_path)

    known_filenames = set()
    pack_path = os.path.join(output_path, '{}.{}.o8c'.format(set_name, lang))
    with zipfile.ZipFile(pack_path, 'w', zipfile.ZIP_DEFLATED) as zip_obj:
        for _, _, filenames in os.walk(input_path):
            for filename in filenames:
                if filename.split('.')[-1] != 'jpg':
                    continue

                parts = filename.split('.')
                parts[0] = re.sub('-1$', '', re.sub('-2$', '.B', parts[0]))
                octgn_filename = '.'.join(parts)[50:]
                if octgn_filename not in known_filenames:
                    known_filenames.add(octgn_filename)
                    zip_obj.write(os.path.join(input_path, filename),
                                  '{}/{}/Cards/{}'.format(OCTGN_ZIP_PATH,
                                                          set_id,
                                                          octgn_filename))

            break


def _collect_pdf_images(input_path):
    """ Collect image filenames for generated PDF.
    """
    images = {'player': [],
              'encounter': [],
              'custom': []}
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            parts = filename.split('-')
            if parts[-1] != '1.png':
                continue

            back_path = os.path.join(input_path, '{}-2.png'.format(
                '-'.join(parts[:-1])))
            if os.path.exists(back_path):
                back_type = 'custom'
            else:
                if parts[2] == 'p':
                    back_type = 'player'
                    back_path = os.path.join(IMAGES_BACK_PATH,
                                             'playerBackOfficial.png')
                elif parts[2] == 'e':
                    back_type = 'encounter'
                    back_path = os.path.join(IMAGES_BACK_PATH,
                                             'encounterBackOfficial.png')
                else:
                    print('Missing card back for {}, removing the file'
                          .format(filename))
                    continue

            copies = 3 if parts[1] == 'p' else 1
            for _ in range(copies):
                images[back_type].append((
                    os.path.join(input_path, filename), back_path))

        break

    return images


def generate_pdf(set_id, set_name, lang):  # pylint: disable=R0914
    """ Generate PDF outputs.
    """
    print('  Generating PDF outputs')
    input_path = os.path.join(IMAGES_EONS_PATH, 'png300PDF',
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_PDF_PATH, '{}.{}'.format(set_name, lang))
    _create_folder(output_path)

    images = _collect_pdf_images(input_path)
    pages_raw = []
    for key in images:
        pages_raw.extend([(images[key][i * 6:(i + 1) * 6] + [None] * 6)[:6]
                          for i in range(math.ceil(len(images[key]) / 6))])

    pages = []
    for page in pages_raw:
        front_page = [i and i[0] or None for i in page]
        back_page = [i and i[1] or None for i in page]
        back_page = [back_page[2], back_page[1], back_page[0],
                     back_page[5], back_page[4], back_page[3]]
        pages.extend([front_page, back_page])

    formats = {'A4': A4, 'Letter': letter}
    card_width = 2.75 * inch
    card_height = 3.75 * inch

    for page_format in formats:
        canvas = Canvas(
            os.path.join(output_path, '{}.{}.{}.pdf'.format(page_format,
                                                            set_name, lang)),
            pagesize=landscape(formats[page_format]))
        width, height = landscape(formats[page_format])
        width_margin = (width - 3 * card_width) / 2
        height_margin = (height - 2 * card_height) / 2
        for page in pages:
            for i, card in enumerate(page):
                if card:
                    width_pos = (
                        width_margin + i * card_width
                        if i < 6 / 2
                        else width_margin + (i - 6 / 2) * card_width)
                    height_pos = (height_margin + card_height
                                  if i < 6 / 2
                                  else height_margin)
                    canvas.drawImage(card, width_pos, height_pos,
                                     card_width, card_height, anchor='sw')

            canvas.showPage()

        canvas.save()


def _insert_png_text(filepath, text):
    """ Insert text into a PNG file.
    """
    reader = png.Reader(filename=filepath)
    chunk_list = list(reader.chunks())
    chunk_item = tuple([TEXT_CHUNK_FLAG, bytes(text, 'utf-8')])
    chunk_list.insert(1, chunk_item)
    with open(filepath, 'wb') as obj:
        png.write_chunks(obj, chunk_list)


def _make_unique_png(input_path):
    """ Make unique PNG files for MakePlayingCards.
    """
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            if filename.endswith('-1.png') or filename.endswith('-2.png'):
                _insert_png_text(os.path.join(input_path, filename), filename)

        break


def _prepare_printing_images(input_path, output_path, service):
    """ Prepare images for MakePlayingCards/DriveThruCards.
    """
    file_type = 'png' if service == 'mpc' else 'jpg'
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            parts = filename.split('-')
            if parts[-1] not in '1.{}'.format(file_type):
                continue

            back_path = os.path.join(input_path, '{}-2.{}'.format(
                '-'.join(parts[:-1]), file_type))
            if not os.path.exists(back_path):
                if parts[2] == 'p':
                    back_path = os.path.join(
                        IMAGES_BACK_PATH,
                        service == 'mpc' and 'playerBackUnofficialMPC.png'
                        or 'playerBackOfficialDTC.jpg')
                elif parts[2] == 'e':
                    back_path = os.path.join(
                        IMAGES_BACK_PATH,
                        service == 'mpc' and 'encounterBackUnofficialMPC.png'
                        or 'encounterBackOfficialDTC.jpg')
                else:
                    print('Missing card back for {}, removing the file'
                          .format(filename))
                    continue

            if parts[1] == 'p':
                for i in range(3):
                    parts[1] = str(i + 1)
                    front_output_path = os.path.join(
                        output_path, re.sub(
                            r'-(?:e|p)-', '-',
                            re.sub('-+', '-',
                                   re.sub(r'.{36}(?=-1\.(?:png|jpg))', '',
                                          '-'.join(parts)))))
                    back_output_path = os.path.join(
                        output_path, re.sub(
                            r'-(?:e|p)-', '-',
                            re.sub('-+', '-',
                                   re.sub(r'.{36}(?=-2\.(?:png|jpg))', '',
                                          '{}-2.{}'.format(
                                              '-'.join(parts[:-1]),
                                              file_type)))))
                    shutil.copyfile(os.path.join(input_path, filename),
                                    front_output_path)
                    shutil.copyfile(back_path, back_output_path)

            else:
                front_output_path = os.path.join(
                    output_path, re.sub(
                        r'-(?:e|p)-', '-',
                        re.sub('-+', '-',
                               re.sub(r'.{36}(?=-1\.(?:png|jpg))', '',
                                      '-'.join(parts)))))
                back_output_path = os.path.join(
                    output_path, re.sub(
                        r'-(?:e|p)-', '-',
                        re.sub('-+', '-',
                               re.sub(r'.{36}(?=-2\.(?:png|jpg))', '',
                                      '{}-2.{}'.format(
                                          '-'.join(parts[:-1]),
                                          file_type)))))
                shutil.copyfile(os.path.join(input_path, filename),
                                front_output_path)
                shutil.copyfile(back_path, back_output_path)

        break


def _prepare_mpc_printing_archive(input_path, obj):
    """ Prepare archive for MakePlayingCards.
    """
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            if filename.endswith('-1.png'):
                obj.write(os.path.join(input_path, filename),
                          'front/{}'.format(filename))
            elif filename.endswith('-2.png'):
                obj.write(os.path.join(input_path, filename),
                          'back/{}'.format(filename))

        break


def _deck_name(current_cnt, total_cnt):
    """ Get deck name for DriveThruCards.
    """
    if total_cnt > 130:
        return 'deck{}/'.format(min(math.floor((current_cnt - 1) / 120) + 1,
                                    math.ceil((total_cnt - 10) / 120)))

    return ''


def _prepare_dtc_printing_archive(input_path, obj):
    """ Prepare archive for DriveThruCards.
    """
    for _, _, filenames in os.walk(input_path):
        front_cnt = 0
        back_cnt = 0
        filenames = sorted(f for f in filenames if f.endswith('-1.jpg')
                           or f.endswith('-2.jpg'))
        total_cnt = len(filenames) / 2
        for filename in filenames:
            if filename.endswith('-1.jpg'):
                front_cnt += 1
                obj.write(os.path.join(input_path, filename),
                          '{}front/{}'.format(_deck_name(front_cnt, total_cnt),
                                              filename))
            elif filename.endswith('-2.jpg'):
                back_cnt += 1
                obj.write(os.path.join(input_path, filename),
                          '{}back/{}'.format(_deck_name(back_cnt, total_cnt),
                                             filename))

        break


def generate_mpc(conf, set_id, set_name, lang):
    """ Generate MakePlayingCards outputs.
    """
    print('  Generating MakePlayingCards outputs')
    input_path = os.path.join(IMAGES_EONS_PATH, 'png800BleedMPC',
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_MPC_PATH, '{}.{}'.format(set_name, lang))
    _create_folder(output_path)
    _clear_folder(TEMP_PATH)

    _prepare_printing_images(input_path, TEMP_PATH, 'mpc')
    _make_unique_png(TEMP_PATH)

    if 'makeplayingcards_zip' in conf['outputs']:
        with zipfile.ZipFile(
                os.path.join(output_path,
                             'MPC.{}.{}.zip'.format(set_name, lang)),
                'w') as obj:
            _prepare_mpc_printing_archive(TEMP_PATH, obj)
            obj.write('MakePlayingCards.pdf', 'MakePlayingCards.pdf')

    if 'makeplayingcards_7z' in conf['outputs']:
        with py7zr.SevenZipFile(
                os.path.join(output_path,
                             'MPC.{}.{}.7z'.format(set_name, lang)),
                'w') as obj:
            _prepare_mpc_printing_archive(TEMP_PATH, obj)
            obj.write('MakePlayingCards.pdf', 'MakePlayingCards.pdf')

    _clear_folder(TEMP_PATH)


def generate_dtc(conf, set_id, set_name, lang):
    """ Generate DriveThruCards outputs.
    """
    print('  Generating DriveThruCards outputs')
    input_path = os.path.join(IMAGES_EONS_PATH, 'jpg300BleedDTC',
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_DTC_PATH, '{}.{}'.format(set_name, lang))
    _create_folder(output_path)
    _clear_folder(TEMP_PATH)

    _prepare_printing_images(input_path, TEMP_PATH, 'dtc')

    if 'drivethrucards_zip' in conf['outputs']:
        with zipfile.ZipFile(
                os.path.join(output_path,
                             'DTC.{}.{}.zip'.format(set_name, lang)),
                'w') as obj:
            _prepare_dtc_printing_archive(TEMP_PATH, obj)

    if 'drivethrucards_7z' in conf['outputs']:
        with py7zr.SevenZipFile(
                os.path.join(output_path,
                             'DTC.{}.{}.7z'.format(set_name, lang)),
                'w') as obj:
            _prepare_dtc_printing_archive(TEMP_PATH, obj)

    _clear_folder(TEMP_PATH)
