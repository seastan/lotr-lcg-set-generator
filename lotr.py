# pylint: disable=C0302
""" Helper functions for LotR ALeP workflow.
"""
import codecs
import csv
import hashlib
import json
import logging
import math
import os
import re
import shutil
import subprocess
import time
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


SET_SHEET = 'Sets'
CARD_SHEET = 'Card Data'
SET_TITLE_ROW = 2
SET_MAX_NUMBER = 1000
CARD_TITLE_ROW = 1
CARD_MAX_NUMBER = 10000
MAX_COLUMN_NUMBER = 100

# Name, Traits:Keywords, Text:Flavour, Side B,
# Traits:Keywords, Text:Flavour, Adventure
TRANSLATION_RANGES = ['F{}:F{}', 'J{}:K{}', 'T{}:W{}', 'AB{}:AB{}',
                      'AF{}:AG{}', 'AP{}:AS{}', 'AZ{}:AZ{}']

SET_ID = 'GUID'
SET_NAME = 'Name'
SET_RINGSDB_CODE = 'RingsDB Code'
SET_HOB_CODE = 'HoB Code'
SET_LANGUAGE = 'Language'
SET_ROW = '_Row'

BACK_PREFIX = 'Back_'
CARD_SET = 'Set'
CARD_ID = 'Card GUID'
CARD_NUMBER = 'Card Number'
CARD_QUANTITY = 'Quantity'
CARD_ENCOUNTER_SET = 'Encounter Set'
CARD_NAME = 'Name'
CARD_UNIQUE = 'Unique'
CARD_TYPE = 'Type'
CARD_SPHERE = 'Sphere'
CARD_TRAITS = 'Traits'
CARD_KEYWORDS = 'Keywords'
CARD_COST = 'Cost'
CARD_ENGAGEMENT = 'Engagement Cost'
CARD_THREAT = 'Threat'
CARD_WILLPOWER = 'Willpower'
CARD_ATTACK = 'Attack'
CARD_DEFENSE = 'Defense'
CARD_HEALTH = 'Health'
CARD_QUEST = 'Quest Points'
CARD_VICTORY = 'Victory Points'
CARD_SHADOW = 'Shadow'
CARD_TEXT = 'Text'
CARD_FLAVOUR = 'Flavour'
CARD_ARTIST = 'Artist'
CARD_EASY_MODE = 'Removed for Easy Mode'
CARD_ADDITIONAL_ENCOUNTER_SETS = 'Additional Encounter Sets'
CARD_SIDE_B = 'Side B'

MAX_COLUMN = '_Max Column'

CARD_TYPES = ('Ally', 'Attachment', 'Contract', 'Enemy',
              'Encounter Side Quest', 'Event', 'Hero', 'Location', 'Objective',
              'Objective Ally', 'Player Side Quest', 'Presentation', 'Quest',
              'Rules', 'Treachery')
CARD_TYPES_DOUBLESIDE = ('Contract', 'Presentation', 'Quest', 'Rules')
CARD_TYPES_PLAYER = ('Ally', 'Attachment', 'Contract', 'Event', 'Hero',
                     'Player Side Quest')
CARD_TYPES_PLAYER_DECK = ('Ally', 'Attachment', 'Event', 'Player Side Quest')
CARD_TYPES_ENCOUNTER_SET = ('Enemy', 'Encounter Side Quest', 'Location',
                            'Objective', 'Objective Ally', 'Quest',
                            'Treachery')

CMYK_COMMAND_JPG = '"{}" mogrify -profile USWebCoatedSWOP.icc "{}\\*.jpg"'
CMYK_COMMAND_TIF = '"{}" mogrify -profile USWebCoatedSWOP.icc -compress lzw ' \
                   '"{}\\*.tif"'
DTC_FILE_TYPE = 'jpg'
GIMP_COMMAND = '"{}" -i -b "({} 1 \\"{}\\" \\"{}\\")" -b "(gimp-quit 0)"'
IMAGE_MIN_SIZE = 100000
IMAGES_CUSTOM_FOLDER = 'custom'
OCTGN_ARCHIVE = 'unzip-me-into-sets-folder.zip'
OCTGN_SET_XML = 'set.xml'
PROCESSED_ARTWORK_FOLDER = 'processed'
PROJECT_FOLDER = 'Frogmorton'
SHEET_NAME = 'setExcel.xlsx'
TEXT_CHUNK_FLAG = b'tEXt'

JPG300BLEEDDTC = 'jpg300BleedDTC'
PNG300BLEED = 'png300Bleed'
PNG300DB = 'png300DB'
PNG300NOBLEED = 'png300NoBleed'
PNG300OCTGN = 'png300OCTGN'
PNG300PDF = 'png300PDF'
PNG800BLEED = 'png800Bleed'
PNG800BLEEDMPC = 'png800BleedMPC'
TIF300BLEEDDTC = 'tif300BleedDTC'

CONFIGURATION_PATH = 'configuration.yaml'
IMAGES_BACK_PATH = 'imagesBack'
IMAGES_CUSTOM_PATH = os.path.join(PROJECT_FOLDER, 'imagesCustom')
IMAGES_EONS_PATH = 'imagesEons'
IMAGES_RAW_PATH = os.path.join(PROJECT_FOLDER, 'imagesRaw')
IMAGES_ZIP_PATH = '{}/Export/'.format(os.path.split(PROJECT_FOLDER)[-1])
MACROS_PATH = 'macros.xlsm'
MACROS_COPY_PATH = 'macros_copy.xlsm'
OCTGN_ZIP_PATH = 'a21af4e8-be4b-4cda-a6b6-534f9717391f/Sets'
OUTPUT_DB_PATH = os.path.join('Output', 'DB')
OUTPUT_DTC_PATH = os.path.join('Output', 'DriveThruCards')
OUTPUT_HALLOFBEORN_PATH = os.path.join('Output', 'HallOfBeorn')
OUTPUT_MPC_PATH = os.path.join('Output', 'MakePlayingCards')
OUTPUT_OCTGN_PATH = os.path.join('Output', 'OCTGN')
OUTPUT_PDF_PATH = os.path.join('Output', 'PDF')
OUTPUT_RINGSDB_PATH = os.path.join('Output', 'RingsDB')
PROJECT_PATH = 'setGenerator.seproject'
SET_EONS_PATH = 'setEons'
SET_OCTGN_PATH = 'setOCTGN'
SHEET_ROOT_PATH = ''
TEMP_ROOT_PATH = 'Temp'
TEMPLATES_SOURCE_PATH = os.path.join('Templates')
TEMPLATES_PATH = os.path.join(PROJECT_FOLDER, 'Templates')
XML_PATH = os.path.join(PROJECT_FOLDER, 'XML')

SET_COLUMNS = {}
CARD_COLUMNS = {}
SETS = {}
DATA = []
ARTWORK_CACHE = {}


def _c2n(column):
    """ Convert column to number.
    """
    res = 0
    multiplier = 1
    column = column.upper()
    for symbol in column[::-1]:
        res += (ord(symbol) - 64) * multiplier
        multiplier *= 26

    return res


def _n2c(number):
    """ Convert number to column.
    """
    res = ''
    while number > 0:
        res = '{}{}'.format(chr((number % 26 or 26) + 64), res)
        number = int((number - (number % 26 or 26)) / 26)

    return res


def _is_positive_int(value):
    """ Check whether a value is a positive int or not.
    """
    try:
        if (str(value).isdigit() or int(value) == value) and int(value) > 0:
            return True

        return False
    except (TypeError, ValueError):
        return False


def _is_positive_or_zero_int(value):
    """ Check whether a value is a positive int or zero or not.
    """
    try:
        if (str(value).isdigit() or int(value) == value) and int(value) >= 0:
            return True

        return False
    except (TypeError, ValueError):
        return False


def _escape_filename(value):
    """ Escape forbidden symbols in a file name.
    """
    return re.sub(r'[<>:"\/\\|?*]', '', value)


def _clear_folder(folder):
    """ Clear the folder.
    """
    if not os.path.exists(folder):
        return

    for _, _, filenames in os.walk(folder):
        for filename in filenames:
            if filename not in ('seproject', '.gitignore'):
                os.remove(os.path.join(folder, filename))

        break


def _create_folder(folder):
    """ Create the folder if needed.
    """
    if not os.path.exists(folder):
        os.mkdir(folder)


def _delete_folder(folder):
    """ Delete the folder.
    """
    if os.path.exists(folder):
        shutil.rmtree(folder, ignore_errors=True)


def _get_artwork_path(conf, set_id):
    """ Get path to the artwork folder.
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


def _clear_modified_images(folder, skip_ids):
    """ Delete images for outdated or modified cards inside the folder.
    """
    for _, _, filenames in os.walk(folder):
        for filename in filenames:
            if filename.split('.')[-1] in ('jpg', 'png', 'tif'):
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
    logging.info('Reading project configuration...')
    timestamp = time.time()

    with open(CONFIGURATION_PATH, 'r') as f_conf:
        conf = yaml.safe_load(f_conf)

    conf['languages'] = [lang for lang in conf['outputs']
                         if conf['outputs'][lang]]
    conf['nobleed'] = {}

    for lang in conf['languages']:
        conf['outputs'][lang] = set(conf['outputs'][lang])

        if ('pdf_a4' in conf['outputs'][lang]
                or 'pdf_letter' in conf['outputs'][lang]):
            conf['outputs'][lang].add('pdf')

        if ('makeplayingcards_zip' in conf['outputs'][lang]
                or 'makeplayingcards_7z' in conf['outputs'][lang]):
            conf['outputs'][lang].add('makeplayingcards')

        if ('drivethrucards_zip' in conf['outputs'][lang]
                or 'drivethrucards_7z' in conf['outputs'][lang]):
            conf['outputs'][lang].add('drivethrucards')

        conf['nobleed'][lang] = ('db' in conf['outputs'][lang]
                                 or 'octgn' in conf['outputs'][lang]
                                 or 'pdf' in conf['outputs'][lang])

    logging.info('...Reading project configuration (%ss)',
                 round(time.time() - timestamp, 3))
    return conf


def reset_project_folders(conf):
    """ Reset the project folders.
    """
    logging.info('Resetting the project folders...')
    timestamp = time.time()

    _clear_folder(IMAGES_CUSTOM_PATH)
    _clear_folder(IMAGES_RAW_PATH)
    _clear_folder(TEMPLATES_PATH)
    _clear_folder(XML_PATH)

    nobleed_folder = os.path.join(IMAGES_EONS_PATH, PNG300NOBLEED)
    for _, subfolders, _ in os.walk(nobleed_folder):
        for subfolder in subfolders:
            _delete_folder(os.path.join(nobleed_folder, subfolder))

        break

    source_path = os.path.join(TEMPLATES_SOURCE_PATH,
                               conf['strange_eons_plugin_version'])
    for _, _, filenames in os.walk(source_path):
        for filename in filenames:
            shutil.copyfile(os.path.join(source_path, filename),
                            os.path.join(TEMPLATES_PATH, filename))

        break

    logging.info('...Resetting the project folders (%ss)',
                 round(time.time() - timestamp, 3))


def download_sheet(conf):
    """ Download cards spreadsheet from Google Drive.
    """
    logging.info('Downloading cards spreadsheet from Google Drive...')
    timestamp = time.time()

    sheet_path = os.path.join(SHEET_ROOT_PATH, SHEET_NAME)
    if conf['sheet_gdid']:
        url = (
            'https://docs.google.com/spreadsheets/d/{}/export?format=xlsx'
            .format(conf['sheet_gdid']))

        with open(sheet_path, 'wb') as f_sheet:
            f_sheet.write(requests.get(url).content)
    else:
        logging.info('No Google Drive ID found, using a local copy')

    logging.info('...Downloading cards spreadsheet from Google Drive (%ss)',
                 round(time.time() - timestamp, 3))


def _extract_column_names(columns):
    """ Extract column names.
    """
    try:
        none_index = columns.index(None)
        columns = columns[:none_index]
    except ValueError:
        pass

    names = {}
    for number, column in enumerate(columns):
        if column in names:
            column = BACK_PREFIX + column

        names[column] = _n2c(number + 1)

    names[MAX_COLUMN] = _n2c(len(columns))
    return names


def _transform_to_dict(data, columns):
    """ Transform rows to dictionary.
    """
    res = []
    for row in data:
        if not any(row):
            break

        row_dict = {}
        for name, column in columns.items():
            if name == MAX_COLUMN:
                continue

            row_dict[name] = row[_c2n(column) - 1]

        res.append(row_dict)

    return res


def extract_data():
    """ Extract data from the spreadsheet.
    """
    logging.info('Extracting data from the spreadsheet...')
    timestamp = time.time()

    sheet_path = os.path.join(SHEET_ROOT_PATH, SHEET_NAME)
    excel_app = xw.App(visible=False, add_book=False)
    try:
        xlwb_source = excel_app.books.open(sheet_path)
        try:
            xlwb_range = '{}{}:{}{}'.format('A',  # pylint: disable=W1308
                                            SET_TITLE_ROW,
                                            _n2c(MAX_COLUMN_NUMBER),
                                            SET_TITLE_ROW)
            data = xlwb_source.sheets[SET_SHEET].range(xlwb_range).value
            SET_COLUMNS.update(_extract_column_names(data))

            xlwb_range = '{}{}:{}{}'.format('A',
                                            SET_TITLE_ROW + 1,
                                            SET_COLUMNS[MAX_COLUMN],
                                            SET_MAX_NUMBER + SET_TITLE_ROW)
            data = xlwb_source.sheets[SET_SHEET].range(xlwb_range).value
            SETS.update({s[SET_ID]: dict(**s,
                                         **{SET_ROW: i + SET_TITLE_ROW + 1})
                         for i, s in
                         enumerate(_transform_to_dict(data, SET_COLUMNS))})

            xlwb_range = '{}{}:{}{}'.format('A',  # pylint: disable=W1308
                                            CARD_TITLE_ROW,
                                            _n2c(MAX_COLUMN_NUMBER),
                                            CARD_TITLE_ROW)
            data = xlwb_source.sheets[CARD_SHEET].range(xlwb_range).value
            CARD_COLUMNS.update(_extract_column_names(data))

            xlwb_range = '{}{}:{}{}'.format('A',
                                            CARD_TITLE_ROW + 1,
                                            CARD_COLUMNS[MAX_COLUMN],
                                            CARD_MAX_NUMBER + CARD_TITLE_ROW)
            data = xlwb_source.sheets[CARD_SHEET].range(xlwb_range).value
            DATA.extend(_transform_to_dict(data, CARD_COLUMNS))
        finally:
            xlwb_source.close()
    finally:
        excel_app.quit()

    logging.info('...Extracting data from the spreadsheet (%ss)',
                 round(time.time() - timestamp, 3))


def _skip_row(row):
    """ Check whether a row should be skipped or not.
    """
    return row[CARD_SET] in ('0', 0) or row[CARD_ID] in ('0', 0)


def sanity_check():  # pylint: disable=R0912,R0914,R0915
    """ Perform a sanity check of the spreadsheet.
    """
    logging.info('Performing a sanity check of the spreadsheet...')
    timestamp = time.time()

    errors_found = False
    card_ids = []
    set_ids = list(SETS.keys())
    for i, row in enumerate(DATA):
        i = i + CARD_TITLE_ROW + 1
        if _skip_row(row):
            continue

        set_id = row[CARD_SET]
        card_id = row[CARD_ID]
        card_number = row[CARD_NUMBER]
        card_quantity = row[CARD_QUANTITY]
        card_unique = row[CARD_UNIQUE]
        card_type = row[CARD_TYPE]
        card_unique_back = row[BACK_PREFIX + CARD_UNIQUE]
        card_type_back = row[BACK_PREFIX + CARD_TYPE]
        card_easy_mode = row[CARD_EASY_MODE]

        if card_type == 'Side Quest':
            if row[CARD_ENCOUNTER_SET] is not None:
                card_type = 'Encounter Side Quest'
            else:
                card_type = 'Player Side Quest'

        if card_type_back == 'Side Quest':
            if row[CARD_ENCOUNTER_SET] is not None:
                card_type_back = 'Encounter Side Quest'
            else:
                card_type_back = 'Player Side Quest'

        if set_id is None:
            logging.error('ERROR: No set ID for row #%s', i)
            errors_found = True
        elif set_id not in set_ids:
            logging.error('ERROR: Unknown set ID for row #%s', i)
            errors_found = True

        if card_id is None:
            logging.error('ERROR: No card ID for row #%s', i)
            errors_found = True
        elif card_id in card_ids:
            logging.error('ERROR: Duplicate card ID for row #%s', i)
            errors_found = True
        else:
            card_ids.append(card_id)

        if card_number is None:
            logging.error('ERROR: No card number for row #%s', i)
            errors_found = True

        if card_quantity is None:
            logging.error('ERROR: No card quantity for row #%s', i)
            errors_found = True
        elif not _is_positive_int(card_quantity):
            logging.error('ERROR: Incorrect format for card quantity'
                          ' for row #%s', i)
            errors_found = True

        if card_unique is not None and card_unique not in ('1', 1):
            logging.error('ERROR: Incorrect format for unique for row #%s', i)
            errors_found = True

        if card_unique_back is not None and card_unique_back not in ('1', 1):
            logging.error('ERROR: Incorrect format for unique back'
                          ' for row #%s', i)
            errors_found = True

        if card_type is None:
            logging.error('ERROR: No card type for row #%s', i)
            errors_found = True
        elif card_type not in CARD_TYPES:
            logging.error('ERROR: Unknown card type for row #%s', i)
            errors_found = True

        if card_type_back is not None and card_type_back not in CARD_TYPES:
            logging.error('ERROR: Unknown card type back for row #%s', i)
            errors_found = True
        elif (card_type in CARD_TYPES_DOUBLESIDE
              and card_type_back is not None and card_type_back != card_type):
            logging.error('ERROR: Incorrect card type back for row #%s', i)
            errors_found = True
        elif (card_type not in CARD_TYPES_DOUBLESIDE
              and card_type_back in CARD_TYPES_DOUBLESIDE):
            logging.error('ERROR: Incorrect card type back for row #%s', i)
            errors_found = True

        if card_easy_mode is not None and not _is_positive_int(card_easy_mode):
            logging.error('ERROR: Incorrect format for removed for easy mode'
                          ' for row #%s', i)
            errors_found = True
        elif card_easy_mode is not None and card_easy_mode > card_quantity:
            logging.error('ERROR: Removed for easy mode is greater than card'
                          ' quantity for row #%s', i)
            errors_found = True

    logging.info('...Performing a sanity check of the spreadsheet (%ss)',
                 round(time.time() - timestamp, 3))
    if errors_found:
        raise ValueError('Sanity check of the spreadsheet failed, '
                         'see error(s) above')


def get_sets(conf):
    """ Get all sets to work on and return list of (set id, set name) tuples.
    """
    logging.info('Getting all sets to work on...')
    timestamp = time.time()

    chosen_sets = []
    for row in SETS.values():
        if row[SET_ID] in conf['set_ids']:
            chosen_sets.append([row[SET_ID], row[SET_NAME]])

    if not chosen_sets:
        logging.error('ERROR: No sets to work on')

    logging.info('...Getting all sets to work on (%ss)',
                 round(time.time() - timestamp, 3))
    return chosen_sets


def _backup_previous_octgn_xml(set_id):
    """ Backup a previous OCTGN xml file.
    """
    new_path = os.path.join(SET_OCTGN_PATH, '{}.xml'.format(set_id))
    old_path = os.path.join(SET_OCTGN_PATH, '{}.xml.old'.format(set_id))
    if os.path.exists(new_path):
        shutil.move(new_path, old_path)


def _copy_octgn_xml(set_id, set_name):
    """ Copy set.xml file to OCTGN output folder.
    """
    output_path = os.path.join(OUTPUT_OCTGN_PATH, _escape_filename(set_name))
    _create_folder(output_path)
    output_path = os.path.join(output_path, set_id)
    _create_folder(output_path)
    shutil.copyfile(os.path.join(SET_OCTGN_PATH, '{}.xml'.format(set_id)),
                    os.path.join(output_path, OCTGN_SET_XML))


def _backup_previous_xml(conf, set_id, lang):
    """ Backup a previous Strange Eons xml file.
    """
    new_path = os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id, lang))
    old_path = os.path.join(SET_EONS_PATH, '{}.{}.xml.old'.format(set_id,
                                                                  lang))
    if os.path.exists(new_path):
        shutil.move(new_path, old_path)

    if conf['from_scratch'] and os.path.exists(old_path):
        os.remove(old_path)


def _run_macro(set_row, callback):
    """ Prepare a context to run an Excel macro and execute the callback.
    """
    shutil.copyfile(MACROS_PATH, MACROS_COPY_PATH)
    sheet_path = os.path.join(SHEET_ROOT_PATH, SHEET_NAME)

    excel_app = xw.App(visible=False, add_book=False)
    try:
        xlwb_source = excel_app.books.open(sheet_path)
        try:
            xlwb_target = excel_app.books.open(MACROS_COPY_PATH)
            try:
                data = xlwb_source.sheets[SET_SHEET].range(
                    '{}{}:{}{}'.format('A',  # pylint: disable=W1308
                                       set_row,
                                       SET_COLUMNS[MAX_COLUMN],
                                       set_row)).value
                xlwb_target.sheets[SET_SHEET].range(
                    '{}{}:{}{}'.format('A',  # pylint: disable=W1308
                                       SET_TITLE_ROW + 1,
                                       SET_COLUMNS[MAX_COLUMN],
                                       SET_TITLE_ROW + 1)
                    ).value = data

                card_sheet = xlwb_target.sheets[CARD_SHEET]
                xlwb_range = '{}{}:{}{}'.format(
                    'A',
                    CARD_TITLE_ROW + 1,
                    CARD_COLUMNS[MAX_COLUMN],
                    CARD_MAX_NUMBER + CARD_TITLE_ROW)
                data = xlwb_source.sheets[CARD_SHEET].range(xlwb_range).value
                card_sheet.range(xlwb_range).value = data
                card_sheet.range(xlwb_range).api.Sort(
                    Key1=card_sheet.range(
                        '{}:{}'.format(CARD_COLUMNS[CARD_SET],  # pylint: disable=W1308
                                       CARD_COLUMNS[CARD_SET])
                    ).api,
                    Order1=xw.constants.SortOrder.xlAscending,
                    Key2=card_sheet.range(
                        '{}:{}'.format(CARD_COLUMNS[CARD_NUMBER],  # pylint: disable=W1308
                                       CARD_COLUMNS[CARD_NUMBER])
                    ).api,
                    Order2=xw.constants.SortOrder.xlAscending)

                callback(xlwb_source, xlwb_target)
                xlwb_target.save()
            finally:
                xlwb_target.close()
        finally:
            xlwb_source.close()
    finally:
        excel_app.quit()


def generate_octgn_set_xml(set_id, set_name):
    """ Generate set.xml file for OCTGN.
    """
    def _callback(_, xlwb_target):
        xlwb_target.macro('SaveOCTGN')()

    logging.info('[%s] Generating set.xml file for OCTGN...', set_name)
    timestamp = time.time()

    _backup_previous_octgn_xml(set_id)
    _run_macro(SETS[set_id][SET_ROW], _callback)
    _copy_octgn_xml(set_id, set_name)
    logging.info('[%s] ...Generating set.xml file for OCTGN (%ss)',
                 set_name, round(time.time() - timestamp, 3))


def _update_card_text(text):  # pylint: disable=R0915
    """ Update card text for RingsDB.
    """
    text = re.sub(r'\b(Quest Resolution)( \([^\)]+\))?:', '[b]\\1[/b]\\2:', text)
    text = re.sub(r'\b(Valour )?(Resource |Planning |Quest |Travel |Encounter '
                  r'|Combat |Refresh )?(Action):', '[b]\\1\\2\\3[/b]:', text)
    text = re.sub(r'\b(When Revealed|Setup|Forced|Valour Response|Response'
                  r'|Travel|Shadow|Resolution):', '[b]\\1[/b]:', text)
    text = re.sub(r'\b(Condition)\b', '[bi]\\1[/bi]', text)
    text = re.sub(r' +(?=\n|$)', '', text)
    text = re.sub(r'\[bi\]', '<b><i>', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/bi\]', '</i></b>', text, flags=re.IGNORECASE)
    text = re.sub(r'\[b\]', '<b>', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/b\]', '</b>', text, flags=re.IGNORECASE)
    text = re.sub(r'\[i\]', '<i>', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/i\]', '</i>', text, flags=re.IGNORECASE)
    text = re.sub(r'\[u\]', '<u>', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/u\]', '</u>', text, flags=re.IGNORECASE)
    text = re.sub(r'\[space\]', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\[h1\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/h1\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[h2\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/h2\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[center\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/center\]\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[right\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/right\]\n?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[strike\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/strike\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[lotr\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/lotr\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[red\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/red\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[tab\]', '    ', text, flags=re.IGNORECASE)
    text = re.sub(r'\[size ([0-9]+)\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/size\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[img ("?)([^\]]+)\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\n+$', '', text)

    text = text.replace('[Unique]', '[unique]')
    text = text.replace('[Threat]', '[threat]')
    text = text.replace('[Attack]', '[attack]')
    text = text.replace('[Defense]', '[defense]')
    text = text.replace('[Willpower]', '[willpower]')
    text = text.replace('[Leadership]', '[leadership]')
    text = text.replace('[Lore]', '[lore]')
    text = text.replace('[Spirit]', '[spirit]')
    text = text.replace('[Tactics]', '[tactics]')
    text = text.replace('[Baggins]', '[baggins]')
    text = text.replace('[Fellowship]', '[fellowship]')
    text = text.replace('[Mastery]', '[mastery]')
    text = text.replace('[Sunny]', '[sunny]')
    text = text.replace('[Cloudy]', '[cloudy]')
    text = text.replace('[Rainy]', '[rainy]')
    text = text.replace('[Stormy]', '[stormy]')
    text = text.replace('[Sailing]', '[sailing]')
    text = text.replace('[PP]', '[pp]')

    return text


def _handle_int(value):
    """ Correctly handle (not always) integer values.
    """
    if _is_positive_or_zero_int(value):
        return int(value)

    return value


def generate_ringsdb_csv(set_id, set_name):  # pylint: disable=R0912
    """ Generate CSV file for RingsDB.
    """
    logging.info('[%s] Generating CSV file for RingsDB...', set_name)
    timestamp = time.time()

    output_path = os.path.join(OUTPUT_RINGSDB_PATH, _escape_filename(set_name))
    _create_folder(output_path)

    output_path = os.path.join(output_path,
                               '{}.csv'.format(_escape_filename(set_name)))
    with open(output_path, 'w', newline='', encoding='utf-8') as obj:
        obj.write(codecs.BOM_UTF8.decode('utf-8'))
        fieldnames = ['pack', 'type', 'sphere', 'position', 'code', 'name',
                      'traits', 'text', 'flavor', 'isUnique', 'cost', 'threat',
                      'willpower', 'attack', 'defense', 'health', 'victory',
                      'quest', 'quantity', 'deckLimit', 'illustrator',
                      'octgnid', 'hasErrata']
        writer = csv.DictWriter(obj, fieldnames=fieldnames)
        writer.writeheader()
        for row in DATA:
            if _skip_row(row) or row[CARD_SET] != set_id:
                continue

            card_type = row[CARD_TYPE]
            if card_type == 'Side Quest':
                if row[CARD_ENCOUNTER_SET] is not None:
                    card_type = 'Encounter Side Quest'
                else:
                    card_type = 'Player Side Quest'

            if card_type not in CARD_TYPES_PLAYER:
                continue

            if card_type in CARD_TYPES_PLAYER_DECK:
                limit = re.search(r'limit .*([0-9]+) per deck',
                                  row[CARD_TEXT] is not None and
                                  str(row[CARD_TEXT]) or '',
                                  re.I)
                if limit:
                    limit = int(limit.groups()[0])
            else:
                limit = None

            code_card_number = (str(int(row[CARD_NUMBER])).zfill(3)
                                if _is_positive_or_zero_int(row[CARD_NUMBER])
                                else '000')
            sphere = 'Neutral' if card_type == 'Contract' else row[CARD_SPHERE]

            if card_type == 'Hero':
                cost = None
                threat = _handle_int(row[CARD_COST])
            else:
                cost = _handle_int(row[CARD_COST])
                threat = None

            csv_row = {
                'pack': set_name,
                'type': card_type,
                'sphere': sphere,
                'position': _handle_int(row[CARD_NUMBER]),
                'code': '{}{}'.format(int(SETS[set_id][SET_RINGSDB_CODE]),
                                      code_card_number),
                'name': row[CARD_NAME],
                'traits': row[CARD_TRAITS],
                'text': '{}\n{}'.format(
                    row[CARD_KEYWORDS] is not None and
                    str(row[CARD_KEYWORDS]) or '',
                    _update_card_text(row[CARD_TEXT] is not None and
                                      str(row[CARD_TEXT]) or '')).strip(),
                'flavor': row[CARD_FLAVOUR],
                'isUnique': row[CARD_UNIQUE] and int(row[CARD_UNIQUE]),
                'cost': cost,
                'threat': threat,
                'willpower': _handle_int(row[CARD_WILLPOWER]),
                'attack': _handle_int(row[CARD_ATTACK]),
                'defense': _handle_int(row[CARD_DEFENSE]),
                'health': _handle_int(row[CARD_HEALTH]),
                'victory': _handle_int(row[CARD_VICTORY]),
                'quest': _handle_int(row[CARD_QUEST]),
                'quantity': int(row[CARD_QUANTITY]),
                'deckLimit': limit or int(row[CARD_QUANTITY]),
                'illustrator': row[CARD_ARTIST],
                'octgnid': row[CARD_ID],
                'hasErrata': None
                }
            writer.writerow(csv_row)

    logging.info('[%s] ...Generating CSV file for RingsDB (%ss)',
                 set_name, round(time.time() - timestamp, 3))


def generate_hallofbeorn_json(set_id, set_name):  # pylint: disable=R0912,R0914,R0915
    """ Generate JSON file for Hall of Beorn.
    """
    logging.info('[%s] Generating JSON file for Hall of Beorn...', set_name)
    timestamp = time.time()

    output_path = os.path.join(OUTPUT_HALLOFBEORN_PATH,
                               _escape_filename(set_name))
    _create_folder(output_path)

    output_path = os.path.join(output_path,
                               '{}.json'.format(_escape_filename(set_name)))
    json_data = []
    input_data = DATA[:]
    for row in DATA:
        card_type = row[CARD_TYPE]
        if card_type == 'Side Quest':
            if row[CARD_ENCOUNTER_SET] is not None:
                card_type = 'Encounter Side Quest'
            else:
                card_type = 'Player Side Quest'

        if (row[CARD_SIDE_B] is not None and
                card_type not in CARD_TYPES_DOUBLESIDE):
            new_row = row.copy()
            new_row[CARD_NAME] = new_row[CARD_SIDE_B]
            for key in new_row.keys():
                if key.startswith(BACK_PREFIX):
                    new_row[key.replace(BACK_PREFIX, '')] = new_row[key]

            input_data.append(new_row)

    for row in input_data:
        if _skip_row(row) or row[CARD_SET] != set_id:
            continue

        card_type = row[CARD_TYPE]
        if card_type == 'Side Quest':
            if row[CARD_ENCOUNTER_SET] is not None:
                card_type = 'Encounter Side Quest'
            else:
                card_type = 'Player Side Quest'

        if card_type in CARD_TYPES_PLAYER_DECK:
            limit = re.search(r'limit .*([0-9]+) per deck',
                              row[CARD_TEXT] is not None and
                              str(row[CARD_TEXT]) or '',
                              re.I)
            if limit:
                limit = int(limit.groups()[0])
        else:
            limit = None

        if card_type == 'Hero':
            cost = None
            threat = _handle_int(row[CARD_COST])
            quest_stage = None
            engagement_cost = None
            quest_points = None
        elif card_type == 'Quest':
            cost = None
            threat = None
            quest_stage = _handle_int(row[CARD_COST])
            engagement_cost = None
            quest_points = _handle_int(row[BACK_PREFIX + CARD_QUEST])
        else:
            cost = _handle_int(row[CARD_COST])
            threat = None
            quest_stage = None
            engagement_cost = _handle_int(row[CARD_ENGAGEMENT])
            quest_points = _handle_int(row[CARD_QUEST])

        if card_type in ('Presentation', 'Rules'):
            sphere = 'None'
        elif card_type == 'Contract':
            sphere = 'Neutral'
        elif row[CARD_SPHERE] is not None:
            sphere = str(row[CARD_SPHERE])
        else:
            sphere = 'None'

        keywords = [k.strip() for k in
                    (row[CARD_KEYWORDS] is not None and
                     str(row[CARD_KEYWORDS]) or '').split('.') if k != '']
        position = (int(row[CARD_NUMBER])
                    if _is_positive_or_zero_int(row[CARD_NUMBER]) else 0)
        encounter_set = ((str(row[CARD_ENCOUNTER_SET])
                          if row[CARD_ENCOUNTER_SET] is not None else '')
                         if card_type in CARD_TYPES_ENCOUNTER_SET
                         else row[CARD_ENCOUNTER_SET])
        type_name = ('Setup' if card_type in ('Presentation', 'Rules')
                     else card_type)
        victory_points = (None if card_type in ('Presentation', 'Rules')
                          else _handle_int(row[CARD_VICTORY]))
        additional_encounter_sets = [
            s.strip() for s in (
                row[CARD_ADDITIONAL_ENCOUNTER_SETS] is not None and
                str(row[CARD_ADDITIONAL_ENCOUNTER_SETS]) or '').split(',')
            if s != ''] or None

        text = '{}\n{}'.format(
            row[CARD_KEYWORDS] is not None and
            str(row[CARD_KEYWORDS]) or '',
            _update_card_text(
                row[CARD_TEXT] is not None and
                str(row[CARD_TEXT]) or '')).replace('\n', '\r\n').strip()
        if (card_type in ('Presentation', 'Rules') and
                row[CARD_VICTORY] is not None):
            text = '{}\r\n\r\nPage {}'.format(text, row[CARD_VICTORY])

        if (row[CARD_SIDE_B] is not None and
                row[BACK_PREFIX + CARD_TEXT] is not None and
                card_type in CARD_TYPES_DOUBLESIDE):
            text_back = _update_card_text(str(row[BACK_PREFIX + CARD_TEXT])
                                          ).replace('\n', '\r\n').strip()
            if (card_type in ('Presentation', 'Rules') and
                    row[BACK_PREFIX + CARD_VICTORY] is not None):
                text_back = '{}\r\n\r\nPage {}'.format(
                    text_back, row[BACK_PREFIX + CARD_VICTORY])
            text = '<b>Side A</b> {} <b>Side B</b> {}'.format(text, text_back)

        flavor = (str(row[CARD_FLAVOUR]).replace('\n', '\r\n').strip()
                  if row[CARD_FLAVOUR] is not None else '')
        if (row[CARD_SIDE_B] is not None and
                row[BACK_PREFIX + CARD_FLAVOUR] is not None and
                card_type in CARD_TYPES_DOUBLESIDE):
            flavor_back = str(row[CARD_FLAVOUR]).replace('\n', '\r\n').strip()
            flavor = 'Side A: {} Side B: {}'.format(flavor, flavor_back)

        json_row = {
            'code': '{}{}'.format(int(SETS[set_id][SET_RINGSDB_CODE]),
                                  str(position).zfill(3)),
            'deck_limit': limit or int(row[CARD_QUANTITY]),
            'flavor': flavor,
            'has_errata': False,
            'illustrator': row[CARD_ARTIST] is not None and
                           str(row[CARD_ARTIST]) or 'None',
            'imagesrc': '',
            'is_official': False,
            'is_unique': bool(row[CARD_UNIQUE]),
            'keywords': keywords,
            'name': row[CARD_NAME],
            'octgnid': row[CARD_ID],
            'pack_code': SETS[set_id][SET_HOB_CODE],
            'pack_name': set_name,
            'position': position,
            'quantity': int(row[CARD_QUANTITY]),
            'sphere_code': sphere.lower().replace(' ', '-'),
            'sphere_name': sphere,
            'text': text,
            'traits': row[CARD_TRAITS] is not None and
                      str(row[CARD_TRAITS]) or '',
            'type_code': type_name.lower().replace(' ', '-'),
            'type_name': type_name,
            'url': '',
            'additional_encounter_sets': additional_encounter_sets,
            'attack': _handle_int(row[CARD_ATTACK]),
            'cost': cost,
            'defense': _handle_int(row[CARD_DEFENSE]),
            'easy_mode_quantity': _handle_int(row[CARD_EASY_MODE]),
            'encounter_set': encounter_set,
            'engagement_cost': engagement_cost,
            'health': _handle_int(row[CARD_HEALTH]),
            'quest_points': quest_points,
            'quest_stage': quest_stage,
            'shadow_text': row[CARD_SHADOW] is not None and
                           _update_card_text(str(row[CARD_SHADOW])
                                             ).replace('\n', '\r\n').strip()
                           or None,
            'threat': threat,
            'threat_strength': _handle_int(row[CARD_THREAT]),
            'victory_points': victory_points,
            'willpower': _handle_int(row[CARD_WILLPOWER])
            }
        json_row = {k:v for k, v in json_row.items() if v is not None}
        json_data.append(json_row)

    with open(output_path, 'w', encoding='utf-8') as obj:
        res = json.dumps(json_data, ensure_ascii=False)
        obj.write(res)

    logging.info('[%s] ...Generating JSON file for Hall of Beorn (%ss)',
                 set_name, round(time.time() - timestamp, 3))


def generate_xml(conf, set_id, set_name, lang):
    """ Generate xml file for Strange Eons.
    """
    def _callback(xlwb_source, xlwb_target):
        if lang != 'English':
            translated = []
            tr_sheet = xlwb_source.sheets[lang]
            for source_row in range(CARD_TITLE_ROW + 1,
                                    CARD_MAX_NUMBER + CARD_TITLE_ROW + 1):
                if tr_sheet.range((source_row,
                                   _c2n(CARD_COLUMNS[CARD_SET]))
                                  ).value == set_id:
                    card_id = tr_sheet.range((source_row,
                                              _c2n(CARD_COLUMNS[CARD_ID]))
                                             ).value
                    if card_id:
                        translated.append((card_id, source_row))

            api = xlwb_target.sheets[CARD_SHEET].api
            card_sheet = xlwb_target.sheets[CARD_SHEET]
            for card_id, source_row in translated:
                cell = api.UsedRange.Find(card_id)
                if cell:
                    target_row = cell.row
                    for tr_range in TRANSLATION_RANGES:
                        source_range = tr_range.format(source_row, source_row)
                        target_range = tr_range.format(target_row, target_row)
                        data = tr_sheet.range(source_range).value
                        card_sheet.range(target_range).value = data

        xlwb_target.sheets[SET_SHEET].range((SET_TITLE_ROW + 1,
                                             _c2n(SET_COLUMNS[SET_LANGUAGE]))
                                            ).value = lang
        xlwb_target.macro('SaveXML')()

    logging.info('[%s, %s] Generating xml file for Strange Eons...',
                 set_name, lang)
    timestamp = time.time()

    _backup_previous_xml(conf, set_id, lang)
    _run_macro(SETS[set_id][SET_ROW], _callback)
    logging.info('[%s, %s] ...Generating xml file for Strange Eons (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def _collect_artwork_images(artwork_path):
    """ Collect artwork filenames.
    """
    if artwork_path in ARTWORK_CACHE:
        return ARTWORK_CACHE[artwork_path]

    images = {}
    for _, _, filenames in os.walk(artwork_path):
        for filename in filenames:
            if len(filename.split('.')) < 2 or len(filename.split('_')) < 3:
                continue

            if filename.split('.')[-1] in ('jpg', 'png'):
                card_id_side = '_'.join(filename.split('_')[:2])
                if card_id_side in images:
                    logging.warning('WARNING: Duplicate card ID detected: %s',
                                    os.path.join(artwork_path, filename))

                images[card_id_side] = os.path.join(artwork_path, filename)

        break

    ARTWORK_CACHE[artwork_path] = images
    return images


def _set_outputs(conf, lang, root):
    """ Set required outputs for Strange Eons.
    """
    if conf['nobleed'][lang]:
        if conf['strange_eons_plugin_version'] == 'new':
            root.set('png300Bleed', '1')
        else:
            root.set('png300NoBleed', '1')

    if ('pdf' in conf['outputs'][lang]
            or 'drivethrucards' in conf['outputs'][lang]):
        root.set('png300Bleed', '1')

    if 'makeplayingcards' in conf['outputs'][lang]:
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


def update_xml(conf, set_id, set_name, lang):  # pylint: disable=R0914,R0915
    """ Update the Strange Eons xml file with additional data.
    """
    logging.info('[%s, %s] Updating the Strange Eons xml file with additional'
                 ' data...', set_name, lang)
    timestamp = time.time()

    artwork_path = _get_artwork_path(conf, set_id)
    images = _collect_artwork_images(artwork_path)
    processed_images = _collect_artwork_images(
        os.path.join(artwork_path, PROCESSED_ARTWORK_FOLDER))
    images = {**images, **processed_images}
    xml_path = os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id, lang))

    tree = ET.parse(xml_path)
    root = tree.getroot()
    root.set('pluginVersion', conf['strange_eons_plugin_version'])
    _set_outputs(conf, lang, root)
    encounter_sets = {}
    encounter_cards = {}

    for card in root[0]:
        card_type = _find_properties(card, 'Type')
        if not card_type:
            logging.error('[%s, %s] ERROR: Skipping a card without card type',
                          set_name, lang)
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
            prop.set('value', os.path.split(filename)[-1])
            prop = _get_property(card, 'Artwork Size')
            prop.set('value', str(os.path.getsize(filename)))
            prop = _get_property(card, 'Artwork Modified')
            prop.set('value', str(int(os.path.getmtime(filename))))

            artist = _find_properties(card, 'Artist')
            if not artist and '_Artist_' in os.path.split(filename)[-1]:
                prop = _get_property(card, 'Artist')
                prop.set('value', '.'.join(
                    '_Artist_'.join(
                        os.path.split(filename)[-1].split('_Artist_')[1:]
                        ).split('.')[:-1]).replace('_', ' '))

        if card_type == 'Presentation':
            filename = images.get('{}_{}'.format(card.attrib['id'], 'Top'))
            if filename:
                prop = _get_property(card, 'ArtworkTop')
                prop.set('value', os.path.split(filename)[-1])
                prop = _get_property(card, 'ArtworkTop Size')
                prop.set('value', str(os.path.getsize(filename)))
                prop = _get_property(card, 'ArtworkTop Modified')
                prop.set('value', str(int(os.path.getmtime(filename))))

            filename = images.get('{}_{}'.format(card.attrib['id'], 'Bottom'))
            if filename:
                prop = _get_property(card, 'ArtworkBottom')
                prop.set('value', os.path.split(filename)[-1])
                prop = _get_property(card, 'ArtworkBottom Size')
                prop.set('value', str(os.path.getsize(filename)))
                prop = _get_property(card, 'ArtworkBottom Modified')
                prop.set('value', str(int(os.path.getmtime(filename))))


        filename = images.get('{}_{}'.format(card.attrib['id'], 'B'))
        alternate = [a for a in card if a.attrib.get('type') == 'B']
        if filename and alternate:
            alternate = alternate[0]
            prop = _get_property(alternate, 'Artwork')
            prop.set('value', os.path.split(filename)[-1])
            prop = _get_property(alternate, 'Artwork Size')
            prop.set('value', str(os.path.getsize(filename)))
            prop = _get_property(alternate, 'Artwork Modified')
            prop.set('value', str(int(os.path.getmtime(filename))))

            artist = _find_properties(alternate, 'Artist')
            if not artist and '_Artist_' in os.path.split(filename)[-1]:
                prop = _get_property(alternate, 'Artist')
                prop.set('value', '.'.join(
                    '_Artist_'.join(
                        os.path.split(filename)[-1].split('_Artist_')[1:]
                        ).split('.')[:-1]).replace('_', ' '))

    for card in root[0]:
        if card.attrib['id'] in encounter_cards:
            prop = _get_property(card, 'Encounter Set Total')
            prop.set('value', str(
                encounter_sets[encounter_cards[card.attrib['id']]]))

    tree.write(xml_path)
    logging.info('[%s, %s] ...Updating the Strange Eons xml file with'
                 ' additional data (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def calculate_hashes(set_id, set_name, lang):  # pylint: disable=R0914
    """ Update the Strange Eons xml file with hashes and skip flags.
    """
    logging.info('[%s, %s] Updating the Strange Eons xml file with hashes and'
                 ' skip flags...', set_name, lang)
    timestamp = time.time()

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

    logging.info('[%s, %s] ...Updating the Strange Eons xml file with hashes'
                 ' and skip flags (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))
    return (new_file_hash, old_file_hash)


def copy_custom_images(conf, set_id, set_name):
    """ Copy custom image files into the project folder.
    """
    logging.info('[%s] Copying custom image files into the project folder...',
                 set_name)
    timestamp = time.time()

    images_path = os.path.join(_get_artwork_path(conf, set_id),
                               IMAGES_CUSTOM_FOLDER)
    if os.path.exists(images_path):
        for _, _, filenames in os.walk(images_path):
            for filename in filenames:
                if filename.split('.')[-1] not in ('jpg', 'png'):
                    continue

                output_filename = '{}_{}'.format(set_id, filename)
                shutil.copyfile(os.path.join(images_path, filename),
                                os.path.join(IMAGES_CUSTOM_PATH,
                                             output_filename))

            break

    logging.info('[%s] ...Copying custom image files into the project folder'
                 ' (%ss)', set_name, round(time.time() - timestamp, 3))


def copy_raw_images(conf, set_id, set_name, lang):
    """ Copy raw image files into the project folder.
    """
    logging.info('[%s, %s] Copying raw image files into the project folder...',
                 set_name, lang)
    timestamp = time.time()

    artwork_path = _get_artwork_path(conf, set_id)
    processed_artwork_path = os.path.join(artwork_path,
                                          PROCESSED_ARTWORK_FOLDER)
    tree = ET.parse(os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id,
                                                                   lang)))
    root = tree.getroot()
    for card in root[0]:
        if card.attrib.get('skip') != '1':
            for prop in ('Artwork', 'ArtworkTop', 'ArtworkBottom'):
                filename = _find_properties(card, prop)
                if filename:
                    filename = filename[0].attrib['value']
                    if os.path.exists(os.path.join(processed_artwork_path,
                                                   filename)):
                        input_path = os.path.join(processed_artwork_path,
                                                  filename)
                    else:
                        input_path = os.path.join(artwork_path, filename)

                    output_path = os.path.join(IMAGES_RAW_PATH, filename)
                    if not os.path.exists(output_path):
                        shutil.copyfile(input_path, output_path)

            alternate = [a for a in card if a.attrib.get('type') == 'B']
            if alternate:
                alternate = alternate[0]
                filename = _find_properties(alternate, 'Artwork')
                if filename:
                    filename = filename[0].attrib['value']
                    if os.path.exists(os.path.join(processed_artwork_path,
                                                   filename)):
                        input_path = os.path.join(processed_artwork_path,
                                                  filename)
                    else:
                        input_path = os.path.join(artwork_path, filename)

                    output_path = os.path.join(IMAGES_RAW_PATH, filename)
                    if not os.path.exists(output_path):
                        shutil.copyfile(input_path, output_path)

    logging.info('[%s, %s] ...Copying raw image files into the project folder'
                 ' (%ss)', set_name, lang, round(time.time() - timestamp, 3))


def copy_xml(set_id, set_name, lang):
    """ Copy the Strange Eons xml file into the project.
    """
    logging.info('[%s, %s] Copying the Strange Eons xml file into'
                 ' the project...', set_name, lang)
    timestamp = time.time()

    shutil.copyfile(os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id,
                                                                   lang)),
                    os.path.join(XML_PATH, '{}.{}.xml'.format(set_id, lang)))
    logging.info('[%s, %s] ...Copying the Strange Eons xml file into the'
                 ' project (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def create_project():
    """ Create a Strange Eons project archive.
    """
    logging.info('Creating a Strange Eons project archive...')
    timestamp = time.time()

    with zipfile.ZipFile(PROJECT_PATH, 'w') as zip_obj:
        for root, _, filenames in os.walk(PROJECT_FOLDER):
            for filename in filenames:
                zip_obj.write(os.path.join(root, filename))

    logging.info('...Creating a Strange Eons project archive (%ss)',
                 round(time.time() - timestamp, 3))


def get_skip_info(set_id, set_name, lang):
    """ Get skip information for the set and individual cards.
    """
    logging.info('[%s, %s] Getting skip information...', set_name, lang)
    timestamp = time.time()

    skip_ids = set()
    tree = ET.parse(os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id,
                                                                   lang)))
    root = tree.getroot()
    skip_set = root.attrib.get('skip') == '1'
    for card in root[0]:
        if card.attrib.get('skip') == '1':
            skip_ids.add(card.attrib['id'])

    logging.info('[%s, %s] ...Getting skip information (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))
    return skip_set, skip_ids


def generate_png300_nobleed(conf, set_id, set_name, lang, skip_ids):  # pylint: disable=R0914
    """ Generate images without bleed margins.
    """
    logging.info('[%s, %s] Generating images without bleed margins...',
                 set_name, lang)
    timestamp = time.time()

    output_path = os.path.join(IMAGES_EONS_PATH, PNG300NOBLEED,
                               '{}.{}'.format(set_id, lang))
    _create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)

    if conf['strange_eons_plugin_version'] == 'new':
        temp_path = os.path.join(
            TEMP_ROOT_PATH, 'generate_png300_nobleed.{}.{}'.format(set_id,
                                                                   lang))
        _create_folder(temp_path)
        _clear_folder(temp_path)

        with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
            filelist = [f for f in zip_obj.namelist()
                        if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                      PNG300BLEED))
                        and f.split('.')[-1] == 'png'
                        and f.split('.')[-2] == lang
                        and f.split('.')[-3] == set_id]
            for filename in filelist:
                output_filename = _update_zip_filename(filename)
                with zip_obj.open(filename) as zip_file:
                    with open(os.path.join(temp_path, output_filename),
                              'wb') as output_file:
                        shutil.copyfileobj(zip_file, output_file)

        cmd = GIMP_COMMAND.format(
            conf['gimp_console_path'],
            'python-cut-bleed-margins-folder',
            temp_path.replace('\\', '\\\\'),
            output_path.replace('\\', '\\\\'))
        res = subprocess.run(cmd, capture_output=True, shell=True, check=True)
        logging.info('[%s, %s] %s', set_name, lang, res)
        _delete_folder(temp_path)
    else:
        with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
            filelist = [f for f in zip_obj.namelist()
                        if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                      PNG300NOBLEED))
                        and f.split('.')[-1] == 'png'
                        and f.split('.')[-2] == lang
                        and f.split('.')[-3] == set_id]
            for filename in filelist:
                output_filename = _update_zip_filename(filename)
                with zip_obj.open(filename) as zip_file:
                    with open(os.path.join(output_path, output_filename),
                              'wb') as output_file:
                        shutil.copyfileobj(zip_file, output_file)

    logging.info('[%s, %s] ...Generating images without bleed margins'
                 ' (%ss)', set_name, lang, round(time.time() - timestamp, 3))


def generate_png300_db(conf, set_id, set_name, lang, skip_ids):
    """ Generate images for DB outputs.
    """
    logging.info('[%s, %s] Generating images for DB outputs...',
                 set_name, lang)
    timestamp = time.time()

    output_path = os.path.join(IMAGES_EONS_PATH, PNG300DB,
                               '{}.{}'.format(set_id, lang))
    _create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)
    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_png300_db.{}.{}'.format(set_id, lang))
    _create_folder(temp_path)
    _clear_folder(temp_path)

    input_path = os.path.join(IMAGES_EONS_PATH, PNG300NOBLEED,
                              '{}.{}'.format(set_id, lang))
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            if filename.split('.')[-1] == 'png':
                shutil.copyfile(os.path.join(input_path, filename),
                                os.path.join(temp_path, filename))

        break

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-db-output-folder',
        temp_path.replace('\\', '\\\\'),
        output_path.replace('\\', '\\\\'))
    res = subprocess.run(cmd, capture_output=True, shell=True, check=True)
    logging.info('[%s, %s] %s', set_name, lang, res)

    _delete_folder(temp_path)
    logging.info('[%s, %s] ...Generating images for DB outputs'
                 ' (%ss)', set_name, lang, round(time.time() - timestamp, 3))


def generate_png300_octgn(set_id, set_name, lang, skip_ids):
    """ Generate images for OCTGN outputs.
    """
    logging.info('[%s, %s] Generating images for OCTGN outputs...',
                 set_name, lang)
    timestamp = time.time()

    output_path = os.path.join(IMAGES_EONS_PATH, PNG300OCTGN,
                               '{}.{}'.format(set_id, lang))
    _create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)

    input_path = os.path.join(IMAGES_EONS_PATH, PNG300NOBLEED,
                              '{}.{}'.format(set_id, lang))
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            if filename.split('.')[-1] == 'png':
                shutil.copyfile(os.path.join(input_path, filename),
                                os.path.join(output_path, filename))

        break

    logging.info('[%s, %s] ...Generating images for OCTGN outputs'
                 ' (%ss)', set_name, lang, round(time.time() - timestamp, 3))


def generate_png300_pdf(conf, set_id, set_name, lang, skip_ids):  # pylint: disable=R0914
    """ Generate images for PDF outputs.
    """
    logging.info('[%s, %s] Generating images for PDF outputs...',
                 set_name, lang)
    timestamp = time.time()

    output_path = os.path.join(IMAGES_EONS_PATH, PNG300PDF,
                               '{}.{}'.format(set_id, lang))
    _create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)
    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_png300_pdf.{}.{}'.format(set_id, lang))
    _create_folder(temp_path)
    _clear_folder(temp_path)

    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  PNG300BLEED))
                    and f.split('.')[-1] == 'png'
                    and f.split('.')[-2] == lang
                    and f.split('.')[-3] == set_id]
        for filename in filelist:
            output_filename = _update_zip_filename(filename)
            if output_filename.endswith('-2.png'):
                with zip_obj.open(filename) as zip_file:
                    with open(os.path.join(temp_path, output_filename),
                              'wb') as output_file:
                        shutil.copyfileobj(zip_file, output_file)

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-pdf-back-folder',
        temp_path.replace('\\', '\\\\'),
        output_path.replace('\\', '\\\\'))
    res = subprocess.run(cmd, capture_output=True, shell=True, check=True)
    logging.info('[%s, %s] %s', set_name, lang, res)

    _clear_folder(temp_path)

    input_path = os.path.join(IMAGES_EONS_PATH, PNG300NOBLEED,
                              '{}.{}'.format(set_id, lang))
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            if filename.endswith('-1.png'):
                shutil.copyfile(os.path.join(input_path, filename),
                                os.path.join(temp_path, filename))

        break

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-pdf-front-folder',
        temp_path.replace('\\', '\\\\'),
        output_path.replace('\\', '\\\\'))
    res = subprocess.run(cmd, capture_output=True, shell=True, check=True)
    logging.info('[%s, %s] %s', set_name, lang, res)

    _delete_folder(temp_path)
    logging.info('[%s, %s] ...Generating images for PDF outputs (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def generate_png800_bleedmpc(conf, set_id, set_name, lang, skip_ids):  # pylint: disable=R0914
    """ Generate images for MakePlayingCards outputs.
    """
    logging.info('[%s, %s] Generating images for MakePlayingCards outputs...',
                 set_name, lang)
    timestamp = time.time()

    output_path = os.path.join(IMAGES_EONS_PATH, PNG800BLEEDMPC,
                               '{}.{}'.format(set_id, lang))
    _create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)
    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_png800_bleedmpc.{}.{}'.format(set_id,
                                                                     lang))
    _create_folder(temp_path)
    _clear_folder(temp_path)

    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  PNG800BLEED))
                    and f.split('.')[-1] == 'png'
                    and f.split('.')[-2] == lang
                    and f.split('.')[-3] == set_id]
        for filename in filelist:
            output_filename = _update_zip_filename(filename)
            with zip_obj.open(filename) as zip_file:
                with open(os.path.join(temp_path, output_filename),
                          'wb') as output_file:
                    shutil.copyfileobj(zip_file, output_file)

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-makeplayingcards-folder',
        temp_path.replace('\\', '\\\\'),
        output_path.replace('\\', '\\\\'))
    res = subprocess.run(cmd, capture_output=True, shell=True, check=True)
    logging.info('[%s, %s] %s', set_name, lang, res)

    _delete_folder(temp_path)
    logging.info('[%s, %s] ...Generating images for MakePlayingCards outputs'
                 ' (%ss)', set_name, lang, round(time.time() - timestamp, 3))


def generate_300_bleeddtc(conf, set_id, set_name, lang, skip_ids,  # pylint: disable=R0913,R0914
                          file_type=DTC_FILE_TYPE):
    """ Generate images for DriveThruCards outputs (either JPG or TIF).
    """
    logging.info('[%s, %s] Generating images for DriveThruCards outputs...',
                 set_name, lang)
    timestamp = time.time()

    output_path = os.path.join(IMAGES_EONS_PATH,
                               TIF300BLEEDDTC if file_type == 'tif'
                               else JPG300BLEEDDTC,
                               '{}.{}'.format(set_id, lang))
    _create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)
    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_300_bleeddtc.{}.{}'.format(set_id,
                                                                  lang))
    _create_folder(temp_path)
    _clear_folder(temp_path)

    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  PNG300BLEED))
                    and f.split('.')[-1] == 'png'
                    and f.split('.')[-2] == lang
                    and f.split('.')[-3] == set_id]
        for filename in filelist:
            output_filename = _update_zip_filename(filename)
            with zip_obj.open(filename) as zip_file:
                with open(os.path.join(temp_path, output_filename),
                          'wb') as output_file:
                    shutil.copyfileobj(zip_file, output_file)

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-drivethrucards-tif-folder' if file_type == 'tif'
        else 'python-prepare-drivethrucards-jpg-folder',
        temp_path.replace('\\', '\\\\'),
        output_path.replace('\\', '\\\\'))
    res = subprocess.run(cmd, capture_output=True, shell=True, check=True)
    logging.info('[%s, %s] %s', set_name, lang, res)

    _delete_folder(temp_path)
    logging.info('[%s, %s] ...Generating images for DriveThruCards outputs'
                 ' (%ss)', set_name, lang, round(time.time() - timestamp, 3))


def generate_db(set_id, set_name, lang):
    """ Generate DB outputs.
    """
    logging.info('[%s, %s] Generating DB outputs...', set_name, lang)
    timestamp = time.time()

    input_path = os.path.join(IMAGES_EONS_PATH, PNG300DB,
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_DB_PATH, '{}.{}'.format(
        _escape_filename(set_name), lang))

    known_filenames = set()
    for _, _, filenames in os.walk(input_path):
        if not filenames:
            logging.error('[%s, %s] ERROR: No cards found', set_name, lang)
            break

        _create_folder(output_path)
        _clear_folder(output_path)
        for filename in filenames:
            if filename.split('.')[-1] != 'png':
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

    logging.info('[%s, %s] ...Generating DB outputs (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def generate_octgn(set_id, set_name, lang):
    """ Generate OCTGN outputs.
    """
    logging.info('[%s, %s] Generating OCTGN outputs...', set_name, lang)
    timestamp = time.time()

    input_path = os.path.join(IMAGES_EONS_PATH, PNG300OCTGN,
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_OCTGN_PATH, _escape_filename(set_name))
    pack_path = os.path.join(output_path, '{}.{}.o8c'.format(
        _escape_filename(set_name), lang))

    known_filenames = set()
    for _, _, filenames in os.walk(input_path):
        if not filenames:
            logging.error('[%s, %s] ERROR: No cards found', set_name, lang)
            break

        _create_folder(output_path)
        with zipfile.ZipFile(pack_path, 'w') as zip_obj:
            for filename in filenames:
                if filename.split('.')[-1] != 'png':
                    continue

                octgn_filename = re.sub(
                    r'-1\.png$', '.png',
                    re.sub(r'-2\.png$', '.B.png', filename))[50:]
                if octgn_filename not in known_filenames:
                    known_filenames.add(octgn_filename)
                    zip_obj.write(os.path.join(input_path, filename),
                                  '{}/{}/Cards/{}'.format(OCTGN_ZIP_PATH,
                                                          set_id,
                                                          octgn_filename))

        break

    logging.info('[%s, %s] ...Generating OCTGN outputs (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def _collect_pdf_images(input_path):
    """ Collect image filenames for generated PDF.
    """
    for _, _, filenames in os.walk(input_path):
        if not filenames:
            return {}

        images = {'player': [],
                  'encounter': [],
                  'custom': []}
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
                    logging.error('ERROR: Missing card back for %s, removing'
                                  ' the file', filename)
                    continue

            copies = 3 if parts[1] == 'p' else 1
            for _ in range(copies):
                images[back_type].append((
                    os.path.join(input_path, filename), back_path))

        break

    return images


def generate_pdf(conf, set_id, set_name, lang):  # pylint: disable=R0914
    """ Generate PDF outputs.
    """
    logging.info('[%s, %s] Generating PDF outputs...', set_name, lang)
    timestamp = time.time()

    input_path = os.path.join(IMAGES_EONS_PATH, PNG300PDF,
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_PDF_PATH, '{}.{}'.format(
        _escape_filename(set_name), lang))

    images = _collect_pdf_images(input_path)
    if not images:
        logging.error('[%s, %s] ERROR: No cards found', set_name, lang)
        logging.info('[%s, %s] ...Generating PDF outputs (%ss)',
                     set_name, lang, round(time.time() - timestamp, 3))
        return

    _create_folder(output_path)
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

    formats = {}
    if 'pdf_a4' in conf['outputs'][lang]:
        formats['A4'] = A4

    if 'pdf_letter' in conf['outputs'][lang]:
        formats['Letter'] = letter

    card_width = 2.75 * inch
    card_height = 3.75 * inch

    for page_format in formats:
        canvas = Canvas(
            os.path.join(output_path, '{}.{}.{}.pdf'.format(
                page_format, _escape_filename(set_name), lang)),
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

    logging.info('[%s, %s] ...Generating PDF outputs (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


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


def _make_cmyk(conf, input_path, file_type=DTC_FILE_TYPE):
    """ Convert RGB to CMYK.
    """
    cmd = (CMYK_COMMAND_TIF if file_type == 'tif' else CMYK_COMMAND_JPG
           ).format(conf['magick_path'], input_path)
    res = subprocess.run(cmd, capture_output=True, shell=True, check=True)
    logging.info(res)

    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            if (filename.endswith('.' + file_type)
                    and os.path.getsize(os.path.join(input_path, filename)
                                        ) < IMAGE_MIN_SIZE):
                raise ValueError('ImageMagick conversion failed for {}'.format(
                    os.path.join(input_path, filename)))

        break


def _flip_first_card(input_path):
    """ Flip first card of the deck.
    """
    for _, _, filenames in os.walk(input_path):
        filenames = sorted(filenames)
        if len(filenames) < 2:
            break

        file_type = filenames[0].split('.')[-1]
        if not (filenames[0].endswith('-1.{}'.format(file_type)) and
                filenames[1].endswith('-2.{}'.format(file_type))):
            break

        if (filenames[0].split('-1.{}'.format(file_type))[0] !=
                filenames[1].split('-2.{}'.format(file_type))[0]):
            break

        temp_name = 'temp_file'
        shutil.move(os.path.join(input_path, filenames[0]),
                    os.path.join(input_path, temp_name))
        shutil.move(os.path.join(input_path, filenames[1]),
                    os.path.join(input_path, filenames[0]))
        shutil.move(os.path.join(input_path, temp_name),
                    os.path.join(input_path, filenames[1]))
        break


def _prepare_printing_images(input_path, output_path, service='dtc',
                             file_type=DTC_FILE_TYPE):
    """ Prepare images for MakePlayingCards/DriveThruCards.
    """
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            parts = filename.split('-')
            if parts[-1] != '1.{}'.format(file_type):
                continue

            back_path = os.path.join(input_path, '{}-2.{}'.format(
                '-'.join(parts[:-1]), file_type))
            if not os.path.exists(back_path):
                if parts[2] == 'p':
                    back_path = os.path.join(
                        IMAGES_BACK_PATH,
                        service == 'mpc' and 'playerBackUnofficialMPC.png'
                        or 'playerBackOfficialDTC.{}'.format(file_type))
                elif parts[2] == 'e':
                    back_path = os.path.join(
                        IMAGES_BACK_PATH,
                        service == 'mpc' and 'encounterBackUnofficialMPC.png'
                        or 'encounterBackOfficialDTC.{}'.format(file_type))
                else:
                    logging.error('ERROR: Missing card back for %s, removing'
                                  ' the file', filename)
                    continue

            if parts[1] == 'p':
                for i in range(3):
                    parts[1] = str(i + 1)
                    front_output_path = os.path.join(
                        output_path, re.sub(
                            r'-(?:e|p)-', '-',
                            re.sub('-+', '-',
                                   re.sub(r'.{36}(?=-1\.(?:png|jpg|tif))', '',
                                          '-'.join(parts)))))
                    back_output_path = os.path.join(
                        output_path, re.sub(
                            r'-(?:e|p)-', '-',
                            re.sub('-+', '-',
                                   re.sub(r'.{36}(?=-2\.(?:png|jpg|tif))', '',
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
                               re.sub(r'.{36}(?=-1\.(?:png|jpg|tif))', '',
                                      '-'.join(parts)))))
                back_output_path = os.path.join(
                    output_path, re.sub(
                        r'-(?:e|p)-', '-',
                        re.sub('-+', '-',
                               re.sub(r'.{36}(?=-2\.(?:png|jpg|tif))', '',
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


def _prepare_dtc_printing_archive(input_path, obj, file_type=DTC_FILE_TYPE):
    """ Prepare archive for DriveThruCards.
    """
    for _, _, filenames in os.walk(input_path):
        front_cnt = 0
        back_cnt = 0
        filenames = sorted(f for f in filenames
                           if f.endswith('-1.{}'.format(file_type))
                           or f.endswith('-2.{}'.format(file_type)))
        total_cnt = len(filenames) / 2
        for filename in filenames:
            if filename.endswith('-1.{}'.format(file_type)):
                front_cnt += 1
                obj.write(os.path.join(input_path, filename),
                          '{}front/{}'.format(_deck_name(front_cnt, total_cnt),
                                              filename))
            elif filename.endswith('-2.{}'.format(file_type)):
                back_cnt += 1
                obj.write(os.path.join(input_path, filename),
                          '{}back/{}'.format(_deck_name(back_cnt, total_cnt),
                                             filename))

        break


def generate_mpc(conf, set_id, set_name, lang):
    """ Generate MakePlayingCards outputs.
    """
    logging.info('[%s, %s] Generating MakePlayingCards outputs...',
                 set_name, lang)
    timestamp = time.time()

    input_path = os.path.join(IMAGES_EONS_PATH, PNG800BLEEDMPC,
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_MPC_PATH, '{}.{}'.format(
        _escape_filename(set_name), lang))
    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_mpc.{}.{}'.format(set_id, lang))

    for _, _, filenames in os.walk(input_path):
        if not filenames:
            logging.error('[%s, %s] ERROR: No cards found', set_name, lang)
            logging.info('[%s, %s] ...Generating MakePlayingCards outputs '
                         '(%ss)',
                         set_name, lang, round(time.time() - timestamp, 3))
            return

        break

    _create_folder(output_path)
    _create_folder(temp_path)
    _clear_folder(temp_path)
    _prepare_printing_images(input_path, temp_path, 'mpc', 'png')
    _make_unique_png(temp_path)
    _flip_first_card(temp_path)

    if 'makeplayingcards_zip' in conf['outputs'][lang]:
        with zipfile.ZipFile(
                os.path.join(output_path,
                             'MPC.{}.{}.zip'.format(
                                 _escape_filename(set_name), lang)),
                'w') as obj:
            _prepare_mpc_printing_archive(temp_path, obj)
            obj.write('MakePlayingCards.pdf', 'MakePlayingCards.pdf')

    if 'makeplayingcards_7z' in conf['outputs'][lang]:
        with py7zr.SevenZipFile(
                os.path.join(output_path,
                             'MPC.{}.{}.7z'.format(
                                 _escape_filename(set_name), lang)),
                'w') as obj:
            _prepare_mpc_printing_archive(temp_path, obj)
            obj.write('MakePlayingCards.pdf', 'MakePlayingCards.pdf')

    _delete_folder(temp_path)
    logging.info('[%s, %s] ...Generating MakePlayingCards outputs (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def generate_dtc(conf, set_id, set_name, lang, file_type=DTC_FILE_TYPE):
    """ Generate DriveThruCards outputs.
    """
    logging.info('[%s, %s] Generating DriveThruCards outputs...',
                 set_name, lang)
    timestamp = time.time()

    input_path = os.path.join(IMAGES_EONS_PATH,
                              TIF300BLEEDDTC if file_type == 'tif'
                              else JPG300BLEEDDTC,
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_DTC_PATH, '{}.{}'.format(
        _escape_filename(set_name), lang))
    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_dtc.{}.{}'.format(set_id, lang))

    for _, _, filenames in os.walk(input_path):
        if not filenames:
            logging.error('[%s, %s] ERROR: No cards found', set_name, lang)
            logging.info('[%s, %s] ...Generating DriveThruCards outputs (%ss)',
                         set_name, lang, round(time.time() - timestamp, 3))
            return

        break

    _create_folder(output_path)
    _create_folder(temp_path)
    _clear_folder(temp_path)
    _prepare_printing_images(input_path, temp_path, 'dtc', file_type)
    _make_cmyk(conf, temp_path, file_type)
    _flip_first_card(temp_path)

    if 'drivethrucards_zip' in conf['outputs'][lang]:
        with zipfile.ZipFile(
                os.path.join(output_path,
                             'DTC.{}.{}.zip'.format(
                                 _escape_filename(set_name), lang)),
                'w') as obj:
            _prepare_dtc_printing_archive(temp_path, obj, file_type)
            obj.write('DriveThruCards.pdf', 'DriveThruCards.pdf')

    if 'drivethrucards_7z' in conf['outputs'][lang]:
        with py7zr.SevenZipFile(
                os.path.join(output_path,
                             'DTC.{}.{}.7z'.format(
                                 _escape_filename(set_name), lang)),
                'w') as obj:
            _prepare_dtc_printing_archive(temp_path, obj, file_type)
            obj.write('DriveThruCards.pdf', 'DriveThruCards.pdf')

    _delete_folder(temp_path)
    logging.info('[%s, %s] ...Generating DriveThruCards outputs (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def _create_octgn_archive(temp_path):
    """ Create OCTGN archive with all set.xml files.
    """
    archive_path = os.path.join(temp_path, OCTGN_ARCHIVE)
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as obj:
        for _, folders, _ in os.walk(OUTPUT_OCTGN_PATH):
            for folder in folders:
                for _, subfolders, _ in os.walk(
                        os.path.join(OUTPUT_OCTGN_PATH, folder)):
                    for subfolder in subfolders:
                        xml_path = os.path.join(OUTPUT_OCTGN_PATH, folder,
                                                subfolder, OCTGN_SET_XML)
                        if os.path.exists(xml_path):
                            obj.write(xml_path, '{}/{}'.format(subfolder,
                                                               OCTGN_SET_XML))

                    break

            break


def _prepare_updated_o8c(temp_path, updates):
    """ Copy all updated o8c files to the temporary folder.
    """
    for _, folders, _ in os.walk(OUTPUT_OCTGN_PATH):
        for folder in folders:
            for _, _, filenames in os.walk(
                    os.path.join(OUTPUT_OCTGN_PATH, folder)):
                for filename in filenames:
                    parts = filename.split('.')
                    if len(parts) != 3:
                        continue

                    if (parts[0], parts[1]) in updates:
                        shutil.copyfile(os.path.join(OUTPUT_OCTGN_PATH,
                                                     folder, filename),
                                        os.path.join(temp_path, filename))

                break

        break


def copy_octgn_outputs(conf, unzip=True, copy_o8c=False, updates=None):
    """ Copy OCTGN outputs to the destination folder.
    """
    logging.info('Copying OCTGN outputs to the destination folder...')
    timestamp = time.time()

    temp_path = os.path.join(TEMP_ROOT_PATH, 'copy_octgn_outputs')
    _create_folder(temp_path)
    _clear_folder(temp_path)
    _create_octgn_archive(temp_path)

    if copy_o8c and updates:
        _prepare_updated_o8c(temp_path, updates)

    for _, _, filenames in os.walk(temp_path):
        for filename in filenames:
            shutil.move(os.path.join(temp_path, filename),
                        os.path.join(conf['octgn_destination_path'], filename))

        break

    _delete_folder(temp_path)

    if unzip:
        for _, _, filenames in os.walk(conf['octgn_destination_path']):
            for filename in filenames:
                if filename.split('.')[-1] == 'zip':
                    with zipfile.ZipFile(
                            os.path.join(conf['octgn_destination_path'],
                                         filename)) as obj:
                        obj.extractall(conf['octgn_destination_path'])

            break

    logging.info('...Copying OCTGN outputs to the destination folder (%ss)',
                 round(time.time() - timestamp, 3))
