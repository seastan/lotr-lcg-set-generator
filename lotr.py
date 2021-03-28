# pylint: disable=C0302
# -*- coding: utf8 -*-
""" Helper functions for LotR ALeP workflow.
"""
import codecs
from collections import OrderedDict
import copy
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
import xml.etree.ElementTree as ET
import zipfile

import requests
import unidecode
import yaml

try:
    import png
    import py7zr
    from reportlab.lib.pagesizes import landscape, letter, A4
    from reportlab.lib.units import inch
    from reportlab.pdfgen.canvas import Canvas

    PY7ZR_FILTERS = [{'id': py7zr.FILTER_LZMA2,
                      'preset': py7zr.PRESET_EXTREME}]
except Exception:  # pylint: disable=W0703
    pass


SET_SHEET = 'Sets'
CARD_SHEET = 'Card Data'
SCRATCH_SHEET = 'Scratch Data'

SET_ID = 'GUID'
SET_NAME = 'Name'
SET_RINGSDB_CODE = 'RingsDB Code'
SET_HOB_CODE = 'HoB Code'

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
CARD_SPECIAL_ICON = 'Special Icon'
CARD_TEXT = 'Text'
CARD_SHADOW = 'Shadow'
CARD_FLAVOUR = 'Flavour'
CARD_PRINTED_NUMBER = 'Printed Card Number'
CARD_ARTIST = 'Artist'
CARD_PANX = 'PanX'
CARD_PANY = 'PanY'
CARD_SCALE = 'Scale'
CARD_SIDE_B = 'Side B'
CARD_EASY_MODE = 'Removed for Easy Mode'
CARD_ADDITIONAL_ENCOUNTER_SETS = 'Additional Encounter Sets'
CARD_ADVENTURE = 'Adventure'
CARD_ICON = 'Collection Icon'
CARD_VERSION = 'Version'
CARD_DECK_RULES = 'Deck Rules'
CARD_SELECTED = 'Selected'
CARD_CHANGED = 'Changed'

CARD_SCRATCH = '_Scratch'
CARD_SET_NAME = '_Set Name'
CARD_SET_RINGSDB_CODE = '_Set RingsDB Code'
CARD_SET_HOB_CODE = '_Set HoB Code'
CARD_RINGSDB_CODE = '_RingsDB Code'
CARD_NORMALIZED_NAME = '_Normalized Name'

CARD_DOUBLESIDE = '_Card Side'
CARD_ORIGINAL_NAME = '_Original Name'

MAX_COLUMN = '_Max Column'
ROW_COLUMN = '_Row'

CARD_TYPES = {'Ally', 'Attachment', 'Campaign', 'Contract', 'Enemy',
              'Encounter Side Quest', 'Event', 'Hero', 'Location', 'Nightmare',
              'Objective', 'Objective Ally', 'Objective Hero',
              'Objective Location', 'Player Side Quest', 'Presentation',
              'Quest', 'Rules', 'Ship Enemy', 'Ship Objective', 'Treachery',
              'Treasure'}
CARD_TYPES_DOUBLESIDE_MANDATORY = {'Campaign', 'Nightmare', 'Presentation',
                                   'Quest', 'Rules'}
CARD_TYPES_DOUBLESIDE_OPTIONAL = {'Campaign', 'Contract', 'Nightmare',
                                  'Presentation', 'Quest', 'Rules'}
CARD_TYPES_PLAYER = {'Ally', 'Attachment', 'Contract', 'Event', 'Hero',
                     'Player Side Quest', 'Treasure'}
CARD_TYPES_PLAYER_DECK = {'Ally', 'Attachment', 'Event', 'Player Side Quest'}
CARD_TYPES_ENCOUNTER_SET = {'Campaign', 'Enemy', 'Encounter Side Quest',
                            'Location', 'Nightmare', 'Objective',
                            'Objective Ally', 'Objective Hero',
                            'Objective Location', 'Quest', 'Ship Enemy',
                            'Ship Objective', 'Treachery', 'Treasure'}
CARD_TYPES_ENCOUNTER_SIZE = {'Enemy', 'Location', 'Objective',
                             'Objective Ally', 'Objective Hero',
                             'Objective Location', 'Ship Enemy',
                             'Ship Objective', 'Treachery'}
CARD_TYPES_ADVENTURE = {'Campaign', 'Objective', 'Objective Ally',
                        'Objective Hero', 'Objective Location',
                        'Ship Objective', 'Quest'}
SPHERES = {'Baggins', 'Fellowship', 'Leadership', 'Lore', 'Mastery', 'Neutral',
           'Spirit', 'Tactics', 'Boon', 'Burden', 'Nightmare', 'Upgraded'}
SPHERES_CAMPAIGN = {'Setup'}
SPHERES_RULES = {'Back'}
SPHERES_PRESENTATION = {'Blue', 'Green', 'Purple', 'Red', 'Brown', 'Yellow'}

GIMP_COMMAND = '"{}" -i -b "({} 1 \\"{}\\" \\"{}\\")" -b "(gimp-quit 0)"'
MAGICK_COMMAND_CMYK = '"{}" mogrify -profile USWebCoatedSWOP.icc "{}\\*.jpg"'
MAGICK_COMMAND_LOW = '"{}" mogrify -resize 600x600 -format jpg "{}\\*.png"'
MAGICK_COMMAND_PDF = '"{}" convert "{}\\*o.jpg" "{}"'

IMAGE_MIN_SIZE = 50000

EASY_PREFIX = 'Easy '
IMAGES_CUSTOM_FOLDER = 'custom'
OCTGN_SET_XML = 'set.xml'
PROCESSED_ARTWORK_FOLDER = 'processed'
PROJECT_FOLDER = 'Frogmorton'
TEXT_CHUNK_FLAG = b'tEXt'

JPG300BLEEDDTC = 'jpg300BleedDTC'
JPG800BLEEDMBPRINT = 'jpg800BleedMBPrint'
PNG300BLEED = 'png300Bleed'
PNG300DB = 'png300DB'
PNG300NOBLEED = 'png300NoBleed'
PNG300OCTGN = 'png300OCTGN'
PNG300PDF = 'png300PDF'
PNG800BLEED = 'png800Bleed'
PNG800BLEEDMPC = 'png800BleedMPC'
PNG800BLEEDGENERIC = 'png800BleedGeneric'

CARD_BACKS = {'player': {'mpc': ['playerBackOfficialMPC.png',
                                 'playerBackUnofficialMPC.png'],
                         'dtc': ['playerBackOfficialDTC.jpg',
                                 'playerBackUnofficialDTC.jpg'],
                         'mbprint': ['playerBackOfficialMBPRINT.jpg',
                                     'playerBackUnofficialMBPRINT.jpg'],
                         'genericpng': ['playerBackOfficial.png',
                                        'playerBackUnofficial.png']},
              'encounter': {'mpc': ['encounterBackOfficialMPC.png',
                                    'encounterBackUnofficialMPC.png'],
                            'dtc': ['encounterBackOfficialDTC.jpg',
                                    'encounterBackUnofficialDTC.jpg'],
                            'mbprint': ['encounterBackOfficialMBPRINT.jpg',
                                        'encounterBackUnofficialMBPRINT.jpg'],
                            'genericpng': ['encounterBackOfficial.png',
                                           'encounterBackUnofficial.png']}}

CONFIGURATION_PATH = 'configuration.yaml'
DISCORD_CARD_DATA_PATH = os.path.join('Discord', 'card_data.json')
DOWNLOAD_PATH = 'Download'
IMAGES_BACK_PATH = 'imagesBack'
IMAGES_CUSTOM_PATH = os.path.join(PROJECT_FOLDER, 'imagesCustom')
IMAGES_EONS_PATH = 'imagesEons'
IMAGES_RAW_PATH = os.path.join(PROJECT_FOLDER, 'imagesRaw')
IMAGES_ZIP_PATH = '{}/Export/'.format(os.path.split(PROJECT_FOLDER)[-1])
OCTGN_ZIP_PATH = 'a21af4e8-be4b-4cda-a6b6-534f9717391f/Sets'
OUTPUT_DB_PATH = os.path.join('Output', 'DB')
OUTPUT_DTC_PATH = os.path.join('Output', 'DriveThruCards')
OUTPUT_GENERICPNG_PATH = os.path.join('Output', 'GenericPNG')
OUTPUT_HALLOFBEORN_PATH = os.path.join('Output', 'HallOfBeorn')
OUTPUT_MBPRINT_PATH = os.path.join('Output', 'MBPrint')
OUTPUT_MBPRINT_PDF_PATH = os.path.join('Output', 'MBPrintPDF')
OUTPUT_MPC_PATH = os.path.join('Output', 'MakePlayingCards')
OUTPUT_OCTGN_PATH = os.path.join('Output', 'OCTGN')
OUTPUT_OCTGN_DECKS_PATH = os.path.join('Output', 'OCTGNDecks')
OUTPUT_OCTGN_IMAGES_PATH = os.path.join('Output', 'OCTGNImages')
OUTPUT_PDF_PATH = os.path.join('Output', 'PDF')
OUTPUT_PREVIEW_IMAGES_PATH = os.path.join('Output', 'PreviewImages')
OUTPUT_RINGSDB_PATH = os.path.join('Output', 'RingsDB')
OUTPUT_RINGSDB_IMAGES_PATH = os.path.join('Output', 'RingsDBImages')
PROJECT_PATH = 'setGenerator.seproject'
SET_EONS_PATH = 'setEons'
SET_OCTGN_PATH = 'setOCTGN'
TEMP_ROOT_PATH = 'Temp'
TEMPLATES_SOURCE_PATH = os.path.join('Templates')
TEMPLATES_PATH = os.path.join(PROJECT_FOLDER, 'Templates')
URL_CACHE_PATH = 'urlCache'
XML_PATH = os.path.join(PROJECT_FOLDER, 'XML')

URL_TIMEOUT = 30
URL_RETRIES = 3
URL_SLEEP = 10

O8D_TEMPLATE = """<deck game="a21af4e8-be4b-4cda-a6b6-534f9717391f"
    sleeveid="0">
  <section name="Hero" shared="False" />
  <section name="Ally" shared="False" />
  <section name="Attachment" shared="False" />
  <section name="Event" shared="False" />
  <section name="Side Quest" shared="False" />
  <section name="Sideboard" shared="False" />
  <section name="Quest" shared="True" />
  <section name="Second Quest Deck" shared="True" />
  <section name="Encounter" shared="True" />
  <section name="Special" shared="True" />
  <section name="Second Special" shared="True" />
  <section name="Setup" shared="True" />
  <section name="Staging Setup" shared="True" />
  <section name="Active Setup" shared="True" />
  <notes><![CDATA[]]></notes>
</deck>
"""
SET_XML_TEMPLATE = """<set gameId="a21af4e8-be4b-4cda-a6b6-534f9717391f"
    gameVersion="2.3.6.0">
  <cards />
</set>
"""
XML_TEMPLATE = """<set>
  <cards />
</set>
"""

SHEET_IDS = {}
SETS = {}
DATA = []
TRANSLATIONS = {}
SELECTED_CARDS = set()
FOUND_SETS = set()
FOUND_SCRATCH_SETS = set()
FOUND_INTERSECTED_SETS = set()
IMAGE_CACHE = {}


class SheetError(Exception):
    """ Google Sheet error.
    """


class SanityCheckError(Exception):
    """ Sanity check error.
    """


class ImageMagickError(Exception):
    """ Image Magick error.
    """


def normalized_name(value):
    """ Return a normalized card name.
    """
    value = unidecode.unidecode(value).lower().replace(' ', '-')
    value = re.sub(r'[^a-z0-9\-]', '', value)[:98]
    return value


def is_positive_int(value):
    """ Check whether a value is a positive int or not.
    """
    try:
        if (str(value).isdigit() or int(value) == value) and int(value) > 0:
            return True

        return False
    except (TypeError, ValueError):
        return False


def is_positive_or_zero_int(value):
    """ Check whether a value is a positive int or zero or not.
    """
    try:
        if (str(value).isdigit() or int(value) == value) and int(value) >= 0:
            return True

        return False
    except (TypeError, ValueError):
        return False


def _is_int(value):
    """ Check whether a value is an int or not.
    """
    try:
        if (str(value).isdigit() or
                (len(str(value)) > 1 and str(value)[0] == '-' and
                 str(value)[1:].isdigit()) or
                int(value) == value):
            return True

        return False
    except (TypeError, ValueError):
        return False


def _handle_int(value):
    """ Handle (not always) integer values.
    """
    if _is_int(value):
        return int(value)

    return value


def _handle_int_str(value):
    """ Handle (not always) integer values and convert them to string.
    """
    if _is_int(value):
        return str(int(value))

    return value


def _update_card_text(text):  # pylint: disable=R0915
    """ Update card text for RingsDB and Hall of Beorn.
    """
    text = re.sub(r'\b(Quest Resolution)( \([^\)]+\))?:', '[b]\\1[/b]\\2:', text)
    text = re.sub(r'\b(Valour )?(Resource |Planning |Quest |Travel |Encounter '
                  r'|Combat |Refresh )?(Action):', '[b]\\1\\2\\3[/b]:', text)
    text = re.sub(r'\b(When Revealed|Setup|Forced|Valour Response|Response'
                  r'|Travel|Shadow|Resolution):', '[b]\\1[/b]:', text)
    text = re.sub(r'\b(Condition)\b', '[bi]\\1[/bi]', text)

    text = re.sub(r'\[center\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/center\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[right\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/right\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[bi\]', '<b><i>', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/bi\]', '</i></b>', text, flags=re.IGNORECASE)
    text = re.sub(r'\[b\]', '<b>', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/b\]', '</b>', text, flags=re.IGNORECASE)
    text = re.sub(r'\[i\]', '<i>', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/i\]', '</i>', text, flags=re.IGNORECASE)
    text = re.sub(r'\[u\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/u\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[strike\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/strike\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[red\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/red\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[lotr [^\]]+\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/lotr\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[size [^\]]+\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/size\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[defaultsize [^\]]+\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[img [^\]]+\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[space\]', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\[tab\]', '    ', text, flags=re.IGNORECASE)
    text = re.sub(r'\[nobr\]', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\[inline\]\n', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\[inline\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[lsb\]', '[', text, flags=re.IGNORECASE)
    text = re.sub(r'\[rsb\]', ']', text, flags=re.IGNORECASE)

    text = text.strip()
    text = re.sub(r' +(?=\n)', '', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text


def _update_octgn_card_text(text):
    """ Update card text for OCTGN.
    """
    text = _update_card_text(text)
    text = re.sub(r'(?:<b>|<\/b>|<i>|<\/i>)', '', text, flags=re.IGNORECASE)

    text = text.replace('[willpower]', 'Ò')
    text = text.replace('[threat]', '$')
    text = text.replace('[attack]', 'Û')
    text = text.replace('[defense]', 'Ú')
    text = text.replace('[leadership]', 'Ì')
    text = text.replace('[spirit]', 'Ê')
    text = text.replace('[tactics]', 'Ï')
    text = text.replace('[lore]', 'Î')
    text = text.replace('[baggins]', 'Í')
    text = text.replace('[fellowship]', '☺')
    text = text.replace('[unique]', '‰')
    text = text.replace('[sunny]', 'º')
    text = text.replace('[cloudy]', '¼')
    text = text.replace('[rainy]', '½')
    text = text.replace('[stormy]', '¾')
    text = text.replace('[sailing]', '¹')
    text = text.replace('[eos]', '²')
    text = text.replace('[pp]', '³')
    return text


def _escape_filename(value):
    """ Escape forbidden symbols in a file name.
    """
    return re.sub(r'[<>:\/\\|?*\'"’“”„«»…–—]', ' ', value)


def _escape_octgn_filename(value):
    """ Replace spaces in a file name for OCTGN.
    """
    return value.replace(' ', '-')


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


def read_conf(path=CONFIGURATION_PATH):
    """ Read project configuration.
    """
    logging.info('Reading project configuration (%s)...', path)
    timestamp = time.time()

    with open(path, 'r') as f_conf:
        conf = yaml.safe_load(f_conf)

    conf['all_languages'] = list(conf['outputs'].keys())
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

        if ('mbprint_zip' in conf['outputs'][lang]
                or 'mbprint_7z' in conf['outputs'][lang]
                or 'mbprint_pdf_zip' in conf['outputs'][lang]
                or 'mbprint_pdf_7z' in conf['outputs'][lang]):
            conf['outputs'][lang].add('mbprint')

        if ('genericpng_zip' in conf['outputs'][lang]
                or 'genericpng_7z' in conf['outputs'][lang]):
            conf['outputs'][lang].add('genericpng')

        conf['nobleed'][lang] = ('db' in conf['outputs'][lang]
                                 or 'octgn' in conf['outputs'][lang]
                                 or 'pdf' in conf['outputs'][lang])

    logging.info('...Reading project configuration (%ss)',
                 round(time.time() - timestamp, 3))
    return conf


def reset_project_folders():
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

    for _, _, filenames in os.walk(TEMPLATES_SOURCE_PATH):
        for filename in filenames:
            shutil.copyfile(os.path.join(TEMPLATES_SOURCE_PATH, filename),
                            os.path.join(TEMPLATES_PATH, filename))

        break

    logging.info('...Resetting the project folders (%ss)',
                 round(time.time() - timestamp, 3))


def _get_content(url):
    """ Get URL content.
    """
    for i in range(URL_RETRIES):
        try:
            req = requests.get(url, timeout=URL_TIMEOUT)
            res = req.content
            break
        except Exception:  # pylint: disable=W0703
            if i < URL_RETRIES - 1:
                time.sleep(URL_SLEEP)
            else:
                raise

    return res

def download_sheet(conf):
    """ Download cards spreadsheet from Google Sheets.
    """
    logging.info('Downloading cards spreadsheet from Google Sheets...')
    timestamp = time.time()

    if conf['sheet_gdid']:
        SHEET_IDS.clear()
        sheets = [SET_SHEET, CARD_SHEET, SCRATCH_SHEET]
        for lang in set(conf['languages']).difference(set(['English'])):
            sheets.append(lang)

        url = (
            'https://docs.google.com/spreadsheets/d/{}/export?format=csv'
            .format(conf['sheet_gdid']))
        res = _get_content(url).decode('utf-8')
        if not res or '<html' in res:
            raise SheetError("Can't download the Google Sheet")

        try:
            SHEET_IDS.update(dict(row for row in csv.reader(res.splitlines())))
        except ValueError:
            raise SheetError("Can't download the Google Sheet")

        for sheet in sheets:
            url = (
                'https://docs.google.com/spreadsheets/d/{}/export?format=csv&gid={}'
                .format(conf['sheet_gdid'], SHEET_IDS[sheet]))
            path = os.path.join(DOWNLOAD_PATH, '{}.csv'.format(sheet))
            res = _get_content(url)
            if not res or b'<html' in res:
                raise SheetError("Can't download {} from the Google Sheet"
                                 .format(sheet))

            with open(path, 'wb') as f_sheet:
                f_sheet.write(res)
    else:
        logging.info('No Google Sheets ID found, using a local copy')

    logging.info('...Downloading cards spreadsheet from Google Sheets (%ss)',
                 round(time.time() - timestamp, 3))


def _clean_data(data):  # pylint: disable=R0915
    """ Clean data from the spreadsheet.
    """
    for row in data:
        card_name = (row.get(CARD_NAME) or '').strip()
        card_name_back = (row.get(CARD_SIDE_B) or '').strip()
        for key, value in row.items():
            if isinstance(value, str):
                if key.startswith(BACK_PREFIX):
                    value = value.replace('[name]', card_name_back)
                else:
                    value = value.replace('[name]', card_name)

                value = value.strip()
                value = value.replace('\xa0', ' ')
                value = value.replace('...', '…')
                value = value.replace('---', '—')
                value = value.replace('--', '–')
                value = re.sub(r' -(?=[0-9])', ' –', value)
                value = re.sub(r'\[hyphen\]', '-', value, flags=re.IGNORECASE)
                value = value.replace("'", '’')
                value = value.replace('“', '"')
                value = value.replace('”', '"')
                value = value.replace('„', '"')
                value = value.replace('« ', '"')
                value = value.replace('«', '"')
                value = value.replace(' »', '"')
                value = value.replace('»', '"')
                value = re.sub(r'"([^"]*)"', '“\\1”', value)
                value = value.replace('"', '[unmatched quot]')
                value = re.sub(r'\[lquot\]', '“', value, flags=re.IGNORECASE)
                value = re.sub(r'\[rquot\]', '”', value, flags=re.IGNORECASE)
                value = re.sub(r'\[quot\]', '"', value, flags=re.IGNORECASE)
                value = re.sub(r'\[apos\]', "'", value, flags=re.IGNORECASE)
                while True:
                    value_old = value
                    value = re.sub(r'[“”]([^\[]*)\]', '"\\1]', value)
                    value = re.sub(r'’([^\[]*)\]', "'\\1]", value)
                    if value == value_old:
                        break

                value = re.sub(r'\[unique\]', '[unique]', value,
                               flags=re.IGNORECASE)
                value = re.sub(r'\[threat\]', '[threat]', value,
                               flags=re.IGNORECASE)
                value = re.sub(r'\[attack\]', '[attack]', value,
                               flags=re.IGNORECASE)
                value = re.sub(r'\[defense\]', '[defense]', value,
                               flags=re.IGNORECASE)
                value = re.sub(r'\[willpower\]', '[willpower]', value,
                               flags=re.IGNORECASE)
                value = re.sub(r'\[leadership\]', '[leadership]', value,
                               flags=re.IGNORECASE)
                value = re.sub(r'\[lore\]', '[lore]', value,
                               flags=re.IGNORECASE)
                value = re.sub(r'\[spirit\]', '[spirit]', value,
                               flags=re.IGNORECASE)
                value = re.sub(r'\[tactics\]', '[tactics]', value,
                               flags=re.IGNORECASE)
                value = re.sub(r'\[baggins\]', '[baggins]', value,
                               flags=re.IGNORECASE)
                value = re.sub(r'\[fellowship\]', '[fellowship]', value,
                               flags=re.IGNORECASE)
                value = re.sub(r'\[sunny\]', '[sunny]', value,
                               flags=re.IGNORECASE)
                value = re.sub(r'\[cloudy\]', '[cloudy]', value,
                               flags=re.IGNORECASE)
                value = re.sub(r'\[rainy\]', '[rainy]', value,
                               flags=re.IGNORECASE)
                value = re.sub(r'\[stormy\]', '[stormy]', value,
                               flags=re.IGNORECASE)
                value = re.sub(r'\[sailing\]', '[sailing]', value,
                               flags=re.IGNORECASE)
                value = re.sub(r'\[eos\]', '[eos]', value, flags=re.IGNORECASE)
                value = re.sub(r'\[pp\]', '[pp]', value, flags=re.IGNORECASE)

                value = re.sub(r' +(?=\n)', '', value)
                value = re.sub(r' +', ' ', value)
                row[key] = value


def _update_data(data):
    """ Update card data from the spreadsheet.
    """
    for row in data:
        row[CARD_SET_NAME] = SETS.get(row[CARD_SET], {}).get(SET_NAME, '')
        row[CARD_SET_HOB_CODE] = SETS.get(row[CARD_SET],
                                          {}).get(SET_HOB_CODE, '')
        set_ringsdb_code = SETS.get(row[CARD_SET],
                                    {}).get(SET_RINGSDB_CODE, '')
        row[CARD_SET_RINGSDB_CODE] = (
            int(set_ringsdb_code)
            if is_positive_or_zero_int(set_ringsdb_code)
            else 0)

        if row[CARD_SCRATCH] and row[CARD_SET] in FOUND_INTERSECTED_SETS:
            row[CARD_SET] = '[filtered set]'

        if ((row[CARD_QUANTITY] is None or row[CARD_QUANTITY] in ('0', 0)) and
                row[CARD_TYPE] == 'Rules'):
            row[CARD_QUANTITY] = 1

        if (row[CARD_TYPE] in CARD_TYPES_DOUBLESIDE_MANDATORY and
                row[BACK_PREFIX + CARD_TYPE] is None):
            row[BACK_PREFIX + CARD_TYPE] = row[CARD_TYPE]

        if (row[CARD_TYPE] in CARD_TYPES_DOUBLESIDE_MANDATORY and
                row[CARD_SIDE_B] is None):
            row[CARD_SIDE_B] = row[CARD_NAME]

        if row[CARD_TYPE] == 'Side Quest':
            row[CARD_TYPE] = 'Encounter Side Quest'

        if row[BACK_PREFIX + CARD_TYPE] == 'Side Quest':
            row[BACK_PREFIX + CARD_TYPE] = 'Encounter Side Quest'

        row[BACK_PREFIX + CARD_NAME] = row[CARD_SIDE_B]


def _skip_row(row):
    """ Check whether a row should be skipped or not.
    """
    return row[CARD_SET] in ('0', 0) or row[CARD_ID] in ('0', 0)


def _extract_csv_value(value):
    """ Extract a single value from a CSV file.
    """
    if value == '':
        return None

    if value == 'FALSE':
        return None

    if _is_int(value):
        return int(value)

    return value


def _extract_csv(sheet):
    """ Extract data from a CSV file.
    """
    path = os.path.join(DOWNLOAD_PATH, '{}.csv'.format(sheet))
    data = []
    with open(path, newline='', encoding='utf-8') as obj:
        for row in csv.reader(obj):
            data.append([_extract_csv_value(v) for v in row])

    return data


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

        names[column] = number

    names[MAX_COLUMN] = len(columns) - 1
    return names


def _transform_to_dict(data):
    """ Transform rows to dictionary.
    """
    columns = _extract_column_names(data[0])
    res = []
    for i, row in enumerate(data[1:]):
        row = row[:columns[MAX_COLUMN] + 1]
        if not any(row):
            continue

        row_dict = {}
        row_dict[ROW_COLUMN] = i + 2
        for name, column in columns.items():
            if name == MAX_COLUMN:
                continue

            row_dict[name] = row[column]

        res.append(row_dict)

    return res


def extract_data(conf):  # pylint: disable=R0915
    """ Extract data from the spreadsheet.
    """
    logging.info('Extracting data from the spreadsheet...')
    timestamp = time.time()

    SETS.clear()
    FOUND_SETS.clear()
    FOUND_SCRATCH_SETS.clear()
    FOUND_INTERSECTED_SETS.clear()
    DATA[:] = []
    TRANSLATIONS.clear()
    SELECTED_CARDS.clear()

    data = _extract_csv(SET_SHEET)
    if data:
        data = _transform_to_dict(data)
        _clean_data(data)
        SETS.update({s[SET_ID]: s for s in data})

    data = _extract_csv(CARD_SHEET)
    if data:
        data = _transform_to_dict(data)
        for row in data:
            row[CARD_SCRATCH] = None

        DATA.extend(data)

    data = _extract_csv(SCRATCH_SHEET)
    if data:
        data = _transform_to_dict(data)
        for row in data:
            row[CARD_SCRATCH] = 1

        DATA.extend(data)

    DATA[:] = [row for row in DATA if not _skip_row(row)]

    SELECTED_CARDS.update({row[CARD_ID] for row in DATA if row[CARD_SELECTED]})
    FOUND_SETS.update({row[CARD_SET] for row in DATA
                       if row[CARD_SET] and not row[CARD_SCRATCH]})
    scratch_sets = {row[CARD_SET] for row in DATA if row[CARD_SET]
                    and row[CARD_SCRATCH]}
    FOUND_INTERSECTED_SETS.update(FOUND_SETS.intersection(scratch_sets))
    FOUND_SCRATCH_SETS.update(scratch_sets.difference(FOUND_INTERSECTED_SETS))

    _clean_data(DATA)
    _update_data(DATA)

    DATA[:] = sorted(DATA, key=lambda row: (
        row[CARD_SET_RINGSDB_CODE],
        is_positive_or_zero_int(row[CARD_NUMBER])
        and int(row[CARD_NUMBER]) or 0,
        str(row[CARD_NUMBER]),
        str(row[CARD_NAME])))

    for lang in conf['languages']:
        if lang == 'English':
            continue

        TRANSLATIONS[lang] = {}
        data = _extract_csv(lang)
        if data:
            data = _transform_to_dict(data)
            for row in data:
                row[CARD_SCRATCH] = None

            _clean_data(data)
            _update_data(data)
            for row in data:
                if row[CARD_ID] in TRANSLATIONS[lang]:
                    logging.error(
                        'Duplicate card ID %s in %s translations, '
                        'ignoring', row[CARD_ID], lang)
                else:
                    TRANSLATIONS[lang][row[CARD_ID]] = row

    logging.info('...Extracting data from the spreadsheet (%ss)',
                 round(time.time() - timestamp, 3))


def get_sets(conf):
    """ Get all sets to work on and return list of (set id, set name) tuples.
    """
    logging.info('Getting all sets to work on...')
    timestamp = time.time()

    chosen_sets = set()
    for row in SETS.values():
        if (row[SET_ID] in conf['set_ids'] and
                (row[SET_ID] in FOUND_SETS or
                 row[SET_ID] in FOUND_SCRATCH_SETS)):
            chosen_sets.add(row[SET_ID])

    if 'all' in conf['set_ids']:
        chosen_sets.update(s for s in FOUND_SETS if s in SETS)

    if 'all_scratch' in conf['set_ids']:
        chosen_sets.update(s for s in FOUND_SCRATCH_SETS if s in SETS)

    chosen_sets = list(chosen_sets)
    chosen_sets = [[SETS[s][SET_ID], SETS[s][SET_NAME]] for s in chosen_sets]
    logging.info('...Getting all sets to work on (%ss)',
                 round(time.time() - timestamp, 3))
    return chosen_sets


def sanity_check(conf, sets):  # pylint: disable=R0912,R0914,R0915
    """ Perform a sanity check of the spreadsheet.
    """
    logging.info('Performing a sanity check of the spreadsheet...')
    logging.info('')
    timestamp = time.time()

    errors = []
    card_ids = set()
    card_scratch_ids = set()
    card_set_number_names = set()
    set_ids = [s[0] for s in sets]
    all_set_ids = list(SETS.keys())
    deck_rules = set()
    for row in DATA:  # pylint: disable=R1702
        i = row[ROW_COLUMN]
        set_id = row[CARD_SET]
        card_id = row[CARD_ID]
        card_number = row[CARD_NUMBER]
        card_quantity = row[CARD_QUANTITY]
        card_name = row[CARD_NAME]
        card_unique = row[CARD_UNIQUE]
        card_type = row[CARD_TYPE]
        card_sphere = row[CARD_SPHERE]
        card_unique_back = row[BACK_PREFIX + CARD_UNIQUE]
        card_type_back = row[BACK_PREFIX + CARD_TYPE]
        card_sphere_back = row[BACK_PREFIX + CARD_SPHERE]
        card_easy_mode = row[CARD_EASY_MODE]
        card_scratch = row[CARD_SCRATCH]
        scratch = ' (Scratch)' if card_scratch else ''

        if set_id is None:
            message = 'No set ID for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
        elif set_id == '[filtered set]':
            message = 'Reusing non-scratch set ID for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
        elif set_id not in all_set_ids:
            message = 'Unknown set ID for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)

        if card_id is None:
            message = 'No card ID for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
        elif card_id in card_ids:
            message = 'Duplicate card ID for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
        elif card_id in card_scratch_ids:
            message = 'Duplicate card ID for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)

        if card_scratch:
            card_scratch_ids.add(card_id)
        else:
            card_ids.add(card_id)

        if set_id not in set_ids:
            continue

        if card_number is None:
            message = 'No card number for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)

        if card_quantity is None:
            message = 'No card quantity for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
        elif not is_positive_int(card_quantity):
            message = ('Incorrect format for card quantity for row '
                       '#{}{}'.format(i, scratch))
            logging.error(message)
            if not card_scratch:
                errors.append(message)

        if card_name is None:
            message = 'No card name for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
        elif set_id is not None and card_number is not None:
            if (set_id, card_number, card_name) in card_set_number_names:
                message = ('Duplicate card set, number and name combination '
                           'for row #{}{}'.format(i, scratch))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
            else:
                card_set_number_names.add((set_id, card_number, card_name))

        if card_unique is not None and card_unique not in ('1', 1):
            message = 'Incorrect format for unique for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)

        if card_unique_back is not None and card_unique_back not in ('1', 1):
            message = 'Incorrect format for unique back for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)

        if card_type is None:
            message = 'No card type for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
        elif card_type not in CARD_TYPES:
            message = 'Unknown card type for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)

        if card_type_back is not None and card_type_back not in CARD_TYPES:
            message = 'Unknown card type back for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
        elif (card_type in CARD_TYPES_DOUBLESIDE_OPTIONAL
              and card_type_back is not None and card_type_back != card_type):
            message = 'Incorrect card type back for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
        elif (card_type not in CARD_TYPES_DOUBLESIDE_OPTIONAL
              and card_type_back in CARD_TYPES_DOUBLESIDE_OPTIONAL):
            message = 'Incorrect card type back for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)

        if card_type == 'Campaign':
            spheres = SPHERES_CAMPAIGN
        elif card_type == 'Rules':
            spheres = SPHERES_RULES
        elif card_type == 'Presentation':
            spheres = SPHERES_PRESENTATION
        else:
            spheres = SPHERES

        if (card_sphere is not None and card_sphere not in spheres):
            message = 'Unknown sphere for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)

        if (card_sphere_back is not None and card_sphere_back not in spheres):
            message = 'Unknown sphere back for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)

        if card_easy_mode is not None and not is_positive_int(card_easy_mode):
            message = ('Incorrect format for removed for easy mode for row '
                       '#{}{}'.format(i, scratch))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
        elif card_easy_mode is not None and card_easy_mode > card_quantity:
            message = ('Removed for easy mode is greater than card quantity '
                       'for row #{}{}'.format(i, scratch))
            logging.error(message)
            if not card_scratch:
                errors.append(message)

        for key, value in row.items():
            if isinstance(value, str) and '[unmatched quot]' in value:
                message = ('Unmatched quote symbol in {} column for row '
                           '#{}{}'.format(key, i, scratch))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)

        if (((row[CARD_TYPE] == 'Quest' and row[CARD_ADVENTURE])
             or row[CARD_TYPE] == 'Nightmare')
                and row[CARD_DECK_RULES]):
            quest_id = (row[CARD_SET], row[CARD_ADVENTURE] or row[CARD_NAME])
            if quest_id in deck_rules:
                message = (
                    'Duplicate deck rules for quest {} in row #{}{}'.format(
                        row[CARD_ADVENTURE] or row[CARD_NAME],
                        row[ROW_COLUMN],
                        scratch))
                logging.error(message)
                if conf['octgn_o8d'] and not card_scratch:
                    errors.append(message)
            else:
                deck_rules.add(quest_id)

            prefixes = set()
            for part in row[CARD_DECK_RULES].split('\n\n'):
                rules_list = [r.strip().split(':', 1)
                              for r in part.split('\n')]
                rules_list = [(r[0].lower().strip(),
                               [i.strip() for i in r[1].strip().split(';')])
                              for r in rules_list if len(r) == 2]
                rules = {}
                key_count = {}
                for key, value in rules_list:
                    if key not in (
                            'sets', 'encounter sets', 'prefix', 'external xml',
                            'remove', 'second quest deck', 'special',
                            'second special', 'setup', 'active setup',
                            'staging setup', 'player'):
                        message = (
                            'Unknown key "{}" for deck rules for quest {} in '
                            'row #{}{}'.format(
                                key,
                                row[CARD_ADVENTURE] or row[CARD_NAME],
                                row[ROW_COLUMN],
                                scratch))
                        logging.error(message)
                        if conf['octgn_o8d'] and not card_scratch:
                            errors.append(message)

                        continue

                    if key not in key_count:
                        key_count[key] = 0
                    else:
                        key_count[key] += 1

                    rules[(key, key_count[key])] = value

                for key in ('sets', 'encounter sets', 'prefix', 'external xml'):
                    if key_count.get(key, 0) > 0:
                        message = (
                            'Duplicate key "{}" for deck rules for quest {} '
                            'in row #{}{}'.format(
                                key,
                                row[CARD_ADVENTURE] or row[CARD_NAME],
                                row[ROW_COLUMN],
                                scratch))
                        logging.error(message)
                        if conf['octgn_o8d'] and not card_scratch:
                            errors.append(message)

                prefix = rules.get(('prefix', 0), [''])[0]
                if prefix in prefixes:
                    message = (
                        'Duplicate prefix "{}" for deck rules for quest {} '
                        'in row #{}{}'.format(
                            prefix,
                            row[CARD_ADVENTURE] or row[CARD_NAME],
                            row[ROW_COLUMN],
                            scratch))
                    logging.error(message)
                    if conf['octgn_o8d'] and not card_scratch:
                        errors.append(message)
                else:
                    prefixes.add(prefix)

        for lang in conf['languages']:
            if lang == 'English':
                continue

            if not TRANSLATIONS[lang].get(card_id):
                logging.error(
                    'No card ID %s in %s translations', card_id, lang)
                continue

            if TRANSLATIONS[lang][card_id][CARD_NAME] is None:
                logging.error(
                    'No card name for card ID %s in %s translations, '
                    'row #%s', card_id, lang,
                    TRANSLATIONS[lang][card_id][ROW_COLUMN])

            for key, value in TRANSLATIONS[lang][card_id].items():
                if isinstance(value, str) and '[unmatched quot]' in value:
                    logging.error(
                        'Unmatched quote symbol in %s column for card '
                        'ID %s in %s translations, row #%s', key, card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

    logging.info('')
    if errors:
        raise SanityCheckError('Sanity check failed: {}.'.format(
            '. '.join(errors)))

    logging.info('...Performing a sanity check of the spreadsheet (%ss)',
                 round(time.time() - timestamp, 3))


def save_data_for_bot(conf, sets):
    """ Save the data for the Discord bot.
    """
    logging.info('Saving the data for the Discord bot...')
    timestamp = time.time()

    url = (
        'https://docs.google.com/spreadsheets/d/{}/edit#gid={}'
        .format(conf['sheet_gdid'], SHEET_IDS[CARD_SHEET]))
    set_ids = [s[0] for s in sets]
    data = [{key: value for key, value in row.items() if value is not None}
            for row in DATA if row[CARD_SET] in set_ids
            and not row[CARD_SCRATCH]]
    for row in data:
        row[CARD_NORMALIZED_NAME] = normalized_name(row[CARD_NAME])
        if row.get(BACK_PREFIX + CARD_NAME):
            row[BACK_PREFIX + CARD_NORMALIZED_NAME] = normalized_name(
                row[BACK_PREFIX + CARD_NAME])

        if _needed_for_ringsdb(row):
            row[CARD_RINGSDB_CODE] = _ringsdb_code(row)

    output = {'url': url,
              'data': data}
    with open(DISCORD_CARD_DATA_PATH, 'w', encoding='utf-8') as obj:
        res = json.dumps(output, ensure_ascii=False)
        obj.write(res)

    logging.info('...Saving the data for the Discord bot (%ss)',
                 round(time.time() - timestamp, 3))


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

    if conf['reprocess_all'] and os.path.exists(old_path):
        os.remove(old_path)


def _get_set_xml_property_value(row, name, card_type):  # pylint: disable=R0911,R0912,R0915
    """ Get OCTGN set.xml property value for the given column name.
    """
    value = row[name]
    if value is None:
        value = ''

    if name == CARD_NUMBER:
        if not is_positive_int(value):
            value = 0

        return value

    if name == CARD_QUANTITY:
        if card_type == 'Rules' and not value:
            value = 1

        return value

    if name in (CARD_TYPE, BACK_PREFIX + CARD_TYPE):
        if card_type == 'Presentation':
            value = 'Rules'
        elif card_type in CARD_TYPES_DOUBLESIDE_MANDATORY:
            value = card_type
        elif value == 'Encounter Side Quest':
            value = 'Side Quest'
        elif value == 'Objective Hero':
            value = 'Objective Ally'
        elif value == 'Objective Location':
            value = 'Location'

        return value

    if name in (CARD_SPHERE, BACK_PREFIX + CARD_SPHERE):
        if card_type == 'Treasure':
            value = 'Neutral'
        elif card_type in ('Presentation', 'Rules'):
            value = ''
        elif value == 'Upgraded':
            value = ''
        elif card_type == 'Campaign':
            value = value.upper() if value else 'CAMPAIGN'

        return value

    if name in (CARD_UNIQUE, BACK_PREFIX + CARD_UNIQUE):
        if value:
            value = '‰'

        return value

    if name in (CARD_VICTORY, BACK_PREFIX + CARD_VICTORY):
        if card_type in ('Presentation', 'Rules'):
            value = 'Page {}'.format(value)
        elif is_positive_or_zero_int(value):
            value = 'VICTORY {}'.format(value)

        return value

    if name == CARD_ENCOUNTER_SET:
        if row[CARD_ADVENTURE]:
            value = row[CARD_ADVENTURE]

        return value

    if name == CARD_TEXT and card_type == 'Presentation':
        value = ''
    elif name == BACK_PREFIX + CARD_TEXT and card_type == 'Presentation':
        value = row[CARD_TEXT] or ''
    elif name == CARD_TEXT and row[CARD_KEYWORDS]:
        if row[CARD_SHADOW]:
            value = '{} {}'.format(row[CARD_KEYWORDS], value)
        else:
            value = '{}\n{}'.format(row[CARD_KEYWORDS], value)
    elif name == BACK_PREFIX + CARD_TEXT and row[BACK_PREFIX + CARD_KEYWORDS]:
        if row[BACK_PREFIX + CARD_SHADOW]:
            value = '{} {}'.format(row[BACK_PREFIX + CARD_KEYWORDS], value)
        else:
            value = '{}\n{}'.format(row[BACK_PREFIX + CARD_KEYWORDS], value)

    return value


def _add_set_xml_properties(parent, properties, tab):
    """ Append property elements to OCTGN set.xml.
    """
    parent.text = '\n' + tab + '  '
    for i, (name, value) in enumerate(properties):
        if not name:
            continue

        prop = ET.SubElement(parent, 'property')
        prop.set('name', name)
        prop.set('value', _update_octgn_card_text(str(_handle_int_str(value))))

        if i == len(properties) - 1:
            prop.tail = '\n' + tab
        else:
            prop.tail = '\n' + tab + '  '


def generate_octgn_set_xml(conf, set_id, set_name):  # pylint: disable=R0912,R0914,R0915
    """ Generate set.xml file for OCTGN.
    """
    logging.info('[%s] Generating set.xml file for OCTGN...', set_name)
    timestamp = time.time()

    _backup_previous_octgn_xml(set_id)

    root = ET.fromstring(SET_XML_TEMPLATE)
    root.set('name', set_name)
    root.set('id', set_id)
    root.set('version', SETS[set_id]['Version'])
    cards = root.findall("./cards")[0]

    chosen_data = []
    for row in DATA:
        if row[CARD_ID] is None:
            continue

        if row[CARD_SET] != set_id:
            continue

        if conf['selected_only'] and row[CARD_ID] not in SELECTED_CARDS:
            continue

        chosen_data.append(row)

    tab_appended = False
    for i, row in enumerate(chosen_data):
        if not tab_appended:
            cards.text = '\n    '
            tab_appended = True

        card = ET.SubElement(cards, 'card')
        card.set('id', row[CARD_ID])
        card.set('name', _update_octgn_card_text(row[CARD_NAME] or ''))

        card_type = row[CARD_TYPE]
        if card_type == 'Player Side Quest':
            card_size = 'PlayerQuestCard'
        elif card_type in ('Encounter Side Quest', 'Quest'):
            card_size = 'QuestCard'
        elif (card_type in CARD_TYPES_ENCOUNTER_SIZE or 'Encounter' in (
                row[CARD_KEYWORDS] and
                [k.strip() for k in row[CARD_KEYWORDS].split('.')] or [])):
            card_size = 'EncounterCard'
        else:
            card_size = None

        if card_size:
            card.set('size', card_size)

        properties = []
        for name in (CARD_NUMBER, CARD_QUANTITY, CARD_ENCOUNTER_SET,
                     CARD_UNIQUE, CARD_TYPE, CARD_SPHERE, CARD_TRAITS,
                     CARD_COST, CARD_ENGAGEMENT, CARD_THREAT, CARD_WILLPOWER,
                     CARD_ATTACK, CARD_DEFENSE, CARD_HEALTH, CARD_QUEST,
                     CARD_VICTORY, CARD_TEXT, CARD_SHADOW):
            value = _get_set_xml_property_value(row, name, card_type)
            if value != '':
                properties.append((name, value))

        side_b = (card_type in CARD_TYPES_DOUBLESIDE_MANDATORY
                  or row[CARD_SIDE_B])
        if card_type in ('Campaign', 'Nightmare'):
            properties.append((CARD_ENGAGEMENT, 'A'))
        elif card_type == 'Contract' and side_b:
            properties.append((CARD_ENGAGEMENT, 'A'))

        if properties:
            if side_b:
                properties.append(('', ''))

            _add_set_xml_properties(card, properties, '    ')

        if side_b:
            if (card_type in CARD_TYPES_DOUBLESIDE_MANDATORY
                    and not row[CARD_SIDE_B]):
                alternate_name = row[CARD_NAME]
            else:
                alternate_name = row[CARD_SIDE_B]

            alternate = ET.SubElement(card, 'alternate')
            alternate.set('name',
                          _update_octgn_card_text(alternate_name or ''))
            alternate.set('type', 'B')
            if card_size:
                alternate.set('size', card_size)

            alternate.tail = '\n    '

            properties = []
            value = _get_set_xml_property_value(row, CARD_ENCOUNTER_SET,
                                                card_type)
            if value != '':
                properties.append((CARD_ENCOUNTER_SET, value))

            for name in (CARD_UNIQUE, CARD_TYPE, CARD_SPHERE, CARD_TRAITS,
                         CARD_COST, CARD_ENGAGEMENT, CARD_THREAT,
                         CARD_WILLPOWER, CARD_ATTACK, CARD_DEFENSE,
                         CARD_HEALTH, CARD_QUEST, CARD_VICTORY, CARD_TEXT,
                         CARD_SHADOW):
                value = _get_set_xml_property_value(row, BACK_PREFIX + name,
                                                    card_type)
                if value != '':
                    properties.append((name, value))

            if card_type in ('Campaign', 'Nightmare', 'Contract'):
                properties.append((CARD_ENGAGEMENT, 'B'))

            if properties:
                _add_set_xml_properties(alternate, properties, '      ')

        if i == len(chosen_data) - 1:
            card.tail = '\n  '
        else:
            card.tail = '\n    '

    output_path = os.path.join(SET_OCTGN_PATH, '{}.xml'.format(set_id))
    with open(output_path, 'w', encoding='utf-8') as obj:
        res = ET.tostring(root, encoding='utf-8').decode('utf-8')
        res = res.replace(
            '<set ',
            '<set xmlns:noNamespaceSchemaLocation="CardSet.xsd" ')
        obj.write('<?xml version="1.0" encoding="utf-8" standalone="yes"?>')
        obj.write('\n')
        obj.write(res)

    _copy_octgn_xml(set_id, set_name)
    logging.info('[%s] ...Generating set.xml file for OCTGN (%ss)',
                 set_name, round(time.time() - timestamp, 3))


def _get_cached_content(url):
    """ Find URL's content in the cache first.
    """
    path = os.path.join(URL_CACHE_PATH, '{}.cache'.format(
        re.sub(r'[^A-Za-z0-9_\.\-]', '', url)))
    if os.path.exists(path):
        with open(path, 'br') as obj:
            content = obj.read()
            return content

    content = _get_content(url)
    return content


def _save_content(url, content):
    """ Save URL's content into cache.
    """
    path = os.path.join(URL_CACHE_PATH, '{}.cache'.format(
        re.sub(r'[^A-Za-z0-9_\.\-]', '', url)))
    with open(path, 'bw') as obj:
        obj.write(content)


def _load_external_xml(url, sets, encounter_sets):  # pylint: disable=R0912,R0914,R0915
    """ Load cards from an external XML file.
    """
    res = []
    content = _get_cached_content(url)
    if not content or not b'<?xml' in content:
        logging.error("Can't download XML from %s, ignoring", url)
        return res

    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        logging.error("Can't download XML from %s, ignoring", url)
        return res

    _save_content(url, content)

    set_name = root.attrib['name'].lower()
    if set_name not in sets:
        return res

    for card in root[0]:
        row = {}
        encounter_set = _find_properties(card, 'Encounter Set')
        if encounter_set:
            encounter_set = encounter_set[0].attrib['value'].lower()
            if encounter_set not in encounter_sets:
                continue
        else:
            encounter_set = None

        quantity = _find_properties(card, 'Quantity')
        if not quantity:
            continue

        card_type = _find_properties(card, 'Type')
        if not card_type:
            continue

        traits = _find_properties(card, 'Traits')
        traits = traits[0].attrib['value'] if traits else None

        card_type = card_type[0].attrib['value']
        if card_type == 'Side Quest':
            if encounter_set:
                card_type = 'Encounter Side Quest'
            else:
                card_type = 'Player Side Quest'
        elif card_type == 'Enemy':
            if 'Ship' in [t.strip() for t in traits.split('.')]:
                card_type = 'Ship Enemy'
        elif card_type == 'Objective':
            if 'Ship' in [t.strip() for t in traits.split('.')]:
                card_type = 'Ship Objective'

        sphere = _find_properties(card, 'Sphere')
        sphere = sphere[0].attrib['value'] if sphere else None

        if (not sphere and encounter_set
                and encounter_set.endswith(' - nightmare')
                and card_type in ('Encounter Side Quest', 'Enemy', 'Location',
                                  'Objective', 'Quest', 'Ship Enemy',
                                  'Treachery')):
            sphere = 'Nightmare'
        elif sphere == 'Neutral' and card_type == 'Treasure':
            sphere = None

        keywords = _find_properties(card, 'Keywords')
        keywords = keywords[0].attrib['value'] if keywords else None

        card_number = _find_properties(card, 'Card Number')
        card_number = (
            int(card_number[0].attrib['value'])
            if card_number
            and is_positive_or_zero_int(card_number[0].attrib['value'])
            else 0)

        unique = _find_properties(card, 'Unique')
        unique = 1 if unique else None

        row[CARD_ENCOUNTER_SET] = encounter_set
        row[CARD_ID] = card.attrib['id']
        row[CARD_NUMBER] = card_number
        row[CARD_NAME] = card.attrib['name']
        row[CARD_TYPE] = card_type
        row[CARD_SPHERE] = sphere
        row[CARD_TRAITS] = traits
        row[CARD_KEYWORDS] = keywords
        row[CARD_QUANTITY] = int(quantity[0].attrib['value'])
        row[CARD_SET_NAME] = set_name
        row[CARD_UNIQUE] = unique
        row[CARD_EASY_MODE] = None
        res.append(row)

    return res


def _update_card_for_rules(card):
    """ Update card structure to simplify rules matching.
    """
    if card[CARD_ENCOUNTER_SET]:
        card[CARD_ENCOUNTER_SET] = card[CARD_ENCOUNTER_SET].lower()

    card[CARD_ORIGINAL_NAME] = card[CARD_NAME]
    card[CARD_SET_NAME] = card[CARD_SET_NAME].lower()
    card[CARD_NAME] = card[CARD_NAME].lower() if card[CARD_NAME] else ''
    card[CARD_TYPE] = card[CARD_TYPE].lower() if card[CARD_TYPE] else ''
    card[CARD_SPHERE] = card[CARD_SPHERE].lower() if card[CARD_SPHERE] else ''
    card[CARD_TRAITS] = ([t.lower().strip()
                          for t in card[CARD_TRAITS].split('.') if t]
                         if card[CARD_TRAITS] else [])
    card[CARD_KEYWORDS] = ([k.lower().strip()
                            for k in card[CARD_KEYWORDS].split('.') if k]
                           if card[CARD_KEYWORDS] else [])
    card[CARD_UNIQUE] = '1' if card[CARD_UNIQUE] else '0'
    return card


def _append_cards(parent, cards):
    """ Append card elements to the section element.
    """
    cards = [c for c in cards if _is_int(c[CARD_QUANTITY]) and
             c[CARD_QUANTITY] > 0]
    if cards:
        parent.text = '\n    '

    for i, card in enumerate(cards):
        element = ET.SubElement(parent, 'card')
        element.text = card[CARD_ORIGINAL_NAME]
        element.set('qty', str(int(card[CARD_QUANTITY])))
        element.set('id', card[CARD_ID])
        if i == len(cards) - 1:
            element.tail = '\n  '
        else:
            element.tail = '\n    '


def _test_rule(card, rule):  # pylint: disable=R0911,R0912
    """ Test a deck rule and return the number of affected copies.
    """
    res = re.match(r'^([0-9]+) ', rule)
    if res and _is_int(card[CARD_QUANTITY]):
        qty = min(int(res.groups()[0]), card[CARD_QUANTITY])
        rule = re.sub(r'^[0-9]+ +', '', rule)
    else:
        qty = card[CARD_QUANTITY]

    parts = [p.strip() for p in rule.split('&') if p.strip()]
    for part in parts:
        if re.match(r'^\[[^\]]+\]$', part):
            if part[1:-1] != card[CARD_ENCOUNTER_SET]:
                return 0
        elif re.match(r'^type:', part):
            card_type = re.sub(r'^type:', '', part).strip()
            if card_type == 'side quest':
                card_type = 'encounter side quest'

            if card_type != card[CARD_TYPE]:
                return 0
        elif re.match(r'^sphere:', part):
            if re.sub(r'^sphere:', '', part).strip() != card[CARD_SPHERE]:
                return 0
        elif re.match(r'^set:', part):
            if re.sub(r'^set:', '', part).strip() != card[CARD_SET_NAME]:
                return 0
        elif re.match(r'^unique:', part):
            if re.sub(r'^unique:', '', part).strip() != card[CARD_UNIQUE]:
                return 0
        elif re.match(r'^trait:', part):
            if re.sub(r'^trait:', '', part).strip() not in card[CARD_TRAITS]:
                return 0
        elif re.match(r'^keyword:', part):
            if (re.sub(r'^keyword:', '', part).strip()
                    not in card[CARD_KEYWORDS]):
                return 0
        elif re.match(
                r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-'
                r'[0-9a-f]{12}$', part):
            if part != card[CARD_ID]:
                return 0
        else:
            if part != card[CARD_NAME]:
                return 0

    return qty


def _apply_rules(source_cards, target_cards, rules):
    """ Apply deck rules.
    """
    if not rules:
        return

    rules = [r.lower() for r in rules]
    for card in source_cards:
        for rule in rules:
            qty = _test_rule(card, rule)
            if qty > 0:
                card_copy = card.copy()
                card[CARD_QUANTITY] -= qty
                card_copy[CARD_QUANTITY] = qty
                target_cards.append(card_copy)


def _generate_octgn_o8d_player(conf, set_id, set_name):
    """ Generate .o8d file with player cards for OCTGN.
    """
    rows = [row for row in DATA
            if row[CARD_SET] == set_id
            and row[CARD_TYPE] in CARD_TYPES_PLAYER
            and (not conf['selected_only'] or row[CARD_ID] in SELECTED_CARDS)]
    cards = [_update_card_for_rules(r.copy()) for r in rows]
    root = ET.fromstring(O8D_TEMPLATE)
    _append_cards(root.findall("./section[@name='Hero']")[0], cards)

    output_path = os.path.join(OUTPUT_OCTGN_DECKS_PATH,
                               _escape_filename(set_name))
    filename = _escape_octgn_filename(
        'Player-{}.o8d'.format(_escape_filename(set_name)))
    with open(
            os.path.join(output_path, filename),
            'w', encoding='utf-8') as obj:
        res = ET.tostring(root, encoding='utf-8').decode('utf-8')
        res = res.replace('<notes />', '<notes><![CDATA[]]></notes>')
        obj.write('<?xml version="1.0" encoding="utf-8" standalone="yes"?>')
        obj.write('\n')
        obj.write(res)


def generate_octgn_o8d(conf, set_id, set_name):  # pylint: disable=R0912,R0914,R0915
    """ Generate .o8d files for OCTGN.
    """
    logging.info('[%s] Generating .o8d files for OCTGN...', set_name)
    timestamp = time.time()

    rows = [row for row in DATA
            if row[CARD_SET] == set_id
            and ((row[CARD_TYPE] == 'Quest' and row[CARD_ADVENTURE])
                 or row[CARD_TYPE] == 'Nightmare')
            and (not conf['selected_only'] or row[CARD_ID] in SELECTED_CARDS)]

    quests = {}
    for row in rows:
        quest = quests.setdefault(row[CARD_ADVENTURE] or row[CARD_NAME],
                                  {'name': row[CARD_ADVENTURE]
                                           or row[CARD_NAME],
                                   'sets': set([row[CARD_SET_NAME].lower()]),
                                   'encounter sets': set(),
                                   'prefix': '',
                                   'rules': '',
                                   'modes': ['']})
        if row[CARD_ENCOUNTER_SET]:
            quest['encounter sets'].add(row[CARD_ENCOUNTER_SET].lower())

        if row[CARD_ADDITIONAL_ENCOUNTER_SETS]:
            for encounter_set in [
                    r.lower().strip()
                    for r in row[CARD_ADDITIONAL_ENCOUNTER_SETS].split(';')]:
                quest['encounter sets'].add(encounter_set)

        if row[CARD_DECK_RULES]:
            quest['rules'] = row[CARD_DECK_RULES]

    quests = list(quests.values())
    new_quests = []
    for quest in quests:
        parts = quest['rules'].split('\n\n')
        if len(parts) > 1:
            quest['rules'] = parts.pop(0)
            for part in parts:
                new_quest = copy.deepcopy(quest)
                new_quest['rules'] = part
                new_quests.append(new_quest)

    quests.extend(new_quests)

    output_path = os.path.join(OUTPUT_OCTGN_DECKS_PATH,
                               _escape_filename(set_name))
    _clear_folder(output_path)
    if quests:
        _create_folder(output_path)

    for quest in quests:
        rules_list = [r.strip().split(':', 1)
                      for r in quest['rules'].split('\n')]
        rules_list = [(r[0].lower().strip(),
                       [i.strip() for i in r[1].strip().split(';')])
                      for r in rules_list if len(r) == 2]
        rules = OrderedDict()
        key_count = {}
        for key, value in rules_list:
            if key not in (
                    'sets', 'encounter sets', 'prefix', 'external xml',
                    'remove', 'second quest deck', 'special',
                    'second special', 'setup', 'active setup',
                    'staging setup', 'player'):
                continue

            if key not in key_count:
                key_count[key] = 0
            else:
                key_count[key] += 1

            rules[(key, key_count[key])] = value

        if rules.get(('sets', 0)):
            quest['sets'].update([s.lower() for s in rules[('sets', 0)]])

        if rules.get(('encounter sets', 0)):
            quest['encounter sets'].update(
                [s.lower() for s in rules[('encounter sets', 0)]])

        if rules.get(('prefix', 0)):
            quest['prefix'] = rules[('prefix', 0)][0] + ' '

        cards = [r for r in DATA
                 if (r[CARD_SET_NAME] or '').lower() in quest['sets']
                 and (not r[CARD_ENCOUNTER_SET] or
                      r[CARD_ENCOUNTER_SET].lower()
                      in quest['encounter sets'])]
        for url in rules.get(('external xml', 0), []):
            cards.extend(_load_external_xml(url, quest['sets'],
                                            quest['encounter sets']))

        if [c for c in cards if c[CARD_EASY_MODE]]:
            quest['modes'].append(EASY_PREFIX)

        for mode in quest['modes']:
            other_cards = []
            quest_cards = []
            second_quest_cards = []
            encounter_cards = []
            removed_cards = []
            special_cards = []
            second_special_cards = []
            default_setup_cards = []
            setup_cards = []
            staging_setup_cards = []
            active_setup_cards = []
            chosen_player_cards = []
            hero_cards = []
            ally_cards = []
            attachment_cards = []
            event_cards = []
            side_quest_cards = []
            for card in cards:
                if not card[CARD_ENCOUNTER_SET]:
                    other_cards.append(_update_card_for_rules(card.copy()))
                elif card[CARD_TYPE] in ('Campaign', 'Nightmare', 'Quest'):
                    quest_cards.append(_update_card_for_rules(card.copy()))
                elif card[CARD_TYPE] in ('Presentation', 'Rules'):
                    default_setup_cards.append(
                        _update_card_for_rules(card.copy()))
                elif mode == EASY_PREFIX and card[CARD_EASY_MODE]:
                    card_copy = _update_card_for_rules(card.copy())
                    easy_mode = (int(card_copy[CARD_EASY_MODE])
                                 if _is_int(card_copy[CARD_EASY_MODE]) else 0)
                    card_copy[CARD_QUANTITY] -= easy_mode
                    encounter_cards.append(card_copy)
                else:
                    encounter_cards.append(_update_card_for_rules(card.copy()))

            for (key, _), value in rules.items():
                if key == 'remove':
                    _apply_rules(other_cards, removed_cards, value)
                    _apply_rules(quest_cards, removed_cards, value)
                    _apply_rules(default_setup_cards, removed_cards, value)
                    _apply_rules(encounter_cards, removed_cards, value)
                elif key == 'second quest deck':
                    _apply_rules(quest_cards, second_quest_cards, value)
                elif key == 'special':
                    _apply_rules(encounter_cards, special_cards, value)
                    _apply_rules(other_cards, special_cards, value)
                elif key == 'second special':
                    _apply_rules(encounter_cards, second_special_cards, value)
                    _apply_rules(other_cards, second_special_cards, value)
                elif key == 'setup':
                    _apply_rules(encounter_cards, setup_cards, value)
                    _apply_rules(other_cards, setup_cards, value)
                elif key == 'staging setup':
                    _apply_rules(encounter_cards, staging_setup_cards, value)
                elif key == 'active setup':
                    _apply_rules(encounter_cards, active_setup_cards, value)
                elif key == 'player':
                    _apply_rules(other_cards, chosen_player_cards, value)

            setup_cards.extend(default_setup_cards)

            for section in (
                    quest_cards, second_quest_cards, encounter_cards,
                    special_cards, second_special_cards, setup_cards,
                    staging_setup_cards, active_setup_cards,
                    chosen_player_cards):
                section.sort(key=lambda card: (
                    card[CARD_SET_NAME],
                    is_positive_or_zero_int(card[CARD_NUMBER])
                    and int(card[CARD_NUMBER]) or 0,
                    card[CARD_NUMBER],
                    card[CARD_NAME]))

            for card in chosen_player_cards:
                if card[CARD_TYPE] == 'hero':
                    hero_cards.append(card)
                elif card[CARD_TYPE] == 'ally':
                    ally_cards.append(card)
                elif card[CARD_TYPE] == 'attachment':
                    attachment_cards.append(card)
                elif card[CARD_TYPE] == 'event':
                    event_cards.append(card)
                elif card[CARD_TYPE] == 'player side quest':
                    side_quest_cards.append(card)

            root = ET.fromstring(O8D_TEMPLATE)
            _append_cards(root.findall("./section[@name='Quest']")[0],
                          quest_cards)
            _append_cards(
                root.findall("./section[@name='Second Quest Deck']")[0],
                second_quest_cards)
            _append_cards(root.findall("./section[@name='Encounter']")[0],
                          encounter_cards)
            _append_cards(root.findall("./section[@name='Special']")[0],
                          special_cards)
            _append_cards(root.findall("./section[@name='Second Special']")[0],
                          second_special_cards)
            _append_cards(root.findall("./section[@name='Setup']")[0],
                          setup_cards)
            _append_cards(root.findall("./section[@name='Staging Setup']")[0],
                          staging_setup_cards)
            _append_cards(root.findall("./section[@name='Active Setup']")[0],
                          active_setup_cards)
            _append_cards(root.findall("./section[@name='Hero']")[0],
                          hero_cards)
            _append_cards(root.findall("./section[@name='Ally']")[0],
                          ally_cards)
            _append_cards(root.findall("./section[@name='Attachment']")[0],
                          attachment_cards)
            _append_cards(root.findall("./section[@name='Event']")[0],
                          event_cards)
            _append_cards(root.findall("./section[@name='Side Quest']")[0],
                          side_quest_cards)

            filename = _escape_octgn_filename(
                '{}{}{}.o8d'.format(mode, quest['prefix'],
                                    _escape_filename(quest['name'])))
            with open(
                    os.path.join(output_path, filename),
                    'w', encoding='utf-8') as obj:
                res = ET.tostring(root, encoding='utf-8').decode('utf-8')
                res = res.replace('<notes />', '<notes><![CDATA[]]></notes>')
                obj.write(
                    '<?xml version="1.0" encoding="utf-8" standalone="yes"?>')
                obj.write('\n')
                obj.write(res)

    _generate_octgn_o8d_player(conf, set_id, set_name)

    logging.info('[%s] ...Generating .o8d files for OCTGN (%ss)',
                 set_name, round(time.time() - timestamp, 3))


def _needed_for_ringsdb(row):
    """ Check whether a card is needed for RingsDB or not.
    """
    card_type = ('Treasure' if row.get(CARD_SPHERE) == 'Boon'
                 else row[CARD_TYPE])
    return card_type in CARD_TYPES_PLAYER


def _ringsdb_code(row):
    """ Return the card's RingsDB code.
    """
    card_number = (str(int(row[CARD_NUMBER])).zfill(3)
                   if is_positive_or_zero_int(row[CARD_NUMBER])
                   else '000')
    code = '{}{}'.format(row[CARD_SET_RINGSDB_CODE], card_number)
    return code


def generate_ringsdb_csv(conf, set_id, set_name):  # pylint: disable=R0912,R0914
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
            if (row[CARD_SET] != set_id
                    or not _needed_for_ringsdb(row)
                    or (conf['selected_only']
                        and row[CARD_ID] not in SELECTED_CARDS)):
                continue

            card_type = ('Treasure'
                         if row[CARD_SPHERE] == 'Boon'
                         else row[CARD_TYPE])

            if card_type in CARD_TYPES_PLAYER_DECK:
                limit = re.search(r'limit .*([0-9]+) per deck',
                                  row[CARD_TEXT] or '',
                                  re.I)
                if limit:
                    limit = int(limit.groups()[0])
            else:
                limit = None

            if card_type in ('Contract', 'Treasure'):
                sphere = 'Neutral'
            else:
                sphere = row[CARD_SPHERE]

            if card_type == 'Hero':
                cost = None
                threat = _handle_int(row[CARD_COST])
            else:
                cost = _handle_int(row[CARD_COST])
                threat = None

            quantity = (int(row[CARD_QUANTITY])
                        if _is_int(row[CARD_QUANTITY]) else 0)

            text = _update_card_text('{}\n{}'.format(
                row[CARD_KEYWORDS] or '',
                row[CARD_TEXT] or '')).strip()

            if (row[CARD_SIDE_B] is not None and
                    row[BACK_PREFIX + CARD_TEXT] is not None):
                text_back = _update_card_text('{}\n{}'.format(
                    row[BACK_PREFIX + CARD_KEYWORDS] or '',
                    row[BACK_PREFIX + CARD_TEXT])).strip()
                text = '<b>Side A</b>\n{}\n<b>Side B</b>\n{}'.format(
                    text, text_back)

            flavor = _update_card_text(row[CARD_FLAVOUR] or '')
            if (row[CARD_SIDE_B] is not None and
                    row[BACK_PREFIX + CARD_FLAVOUR] is not None):
                flavor_back = _update_card_text(
                    row[BACK_PREFIX + CARD_FLAVOUR])
                flavor = '{}\n{}'.format(flavor, flavor_back)

            csv_row = {
                'pack': set_name,
                'type': card_type,
                'sphere': sphere,
                'position': _handle_int(row[CARD_NUMBER]),
                'code': _ringsdb_code(row),
                'name': row[CARD_NAME],
                'traits': row[CARD_TRAITS],
                'text': text,
                'flavor': flavor,
                'isUnique': row[CARD_UNIQUE] and int(row[CARD_UNIQUE]),
                'cost': cost,
                'threat': threat,
                'willpower': _handle_int(row[CARD_WILLPOWER]),
                'attack': _handle_int(row[CARD_ATTACK]),
                'defense': _handle_int(row[CARD_DEFENSE]),
                'health': _handle_int(row[CARD_HEALTH]),
                'victory': _handle_int(row[CARD_VICTORY]),
                'quest': _handle_int(row[CARD_QUEST]),
                'quantity': quantity,
                'deckLimit': limit or quantity,
                'illustrator': row[CARD_ARTIST],
                'octgnid': row[CARD_ID],
                'hasErrata': None
                }
            writer.writerow(csv_row)

    logging.info('[%s] ...Generating CSV file for RingsDB (%ss)',
                 set_name, round(time.time() - timestamp, 3))


def generate_hallofbeorn_json(conf, set_id, set_name):  # pylint: disable=R0912,R0914,R0915
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
    card_data = DATA[:]
    for row in DATA:
        card_type = row[CARD_TYPE]
        if (row[CARD_SIDE_B] is not None and
                card_type not in CARD_TYPES_DOUBLESIDE_OPTIONAL):
            new_row = row.copy()
            new_row[CARD_NAME] = new_row[CARD_SIDE_B]
            new_row[CARD_DOUBLESIDE] = 'B'
            for key in new_row.keys():
                if key.startswith(BACK_PREFIX):
                    new_row[key.replace(BACK_PREFIX, '')] = new_row[key]

            card_data.append(new_row)

    for row in card_data:
        if row[CARD_SET] != set_id:
            continue

        if conf['selected_only'] and row[CARD_ID] not in SELECTED_CARDS:
            continue

        card_type = row[CARD_TYPE]
        if card_type in CARD_TYPES_PLAYER_DECK:
            limit = re.search(r'limit .*([0-9]+) per deck',
                              row[CARD_TEXT] or '',
                              re.I)
            if limit:
                limit = int(limit.groups()[0])
        else:
            limit = None

        if card_type == 'Hero':
            cost = None
            threat = _handle_int_str(row[CARD_COST])
            quest_stage = None
            engagement_cost = None
            quest_points = None
            stage_letter = None
            opposite_stage_letter = None
        elif card_type == 'Quest':
            cost = None
            threat = None
            quest_stage = _handle_int(row[CARD_COST])
            engagement_cost = None
            quest_points = _handle_int_str(row[BACK_PREFIX + CARD_QUEST])
            stage_letter = row[CARD_ENGAGEMENT]
            opposite_stage_letter = row[BACK_PREFIX + CARD_ENGAGEMENT]
        else:
            cost = _handle_int_str(row[CARD_COST])
            threat = None
            quest_stage = None
            engagement_cost = _handle_int_str(row[CARD_ENGAGEMENT])
            quest_points = _handle_int_str(row[CARD_QUEST])
            stage_letter = None
            opposite_stage_letter = None

        if card_type in ('Campaign', 'Presentation', 'Rules'):
            sphere = 'None'
        elif card_type in ('Contract', 'Treasure'):
            sphere = 'Neutral'
        elif row[CARD_SPHERE] in ('Nightmare', 'Upgraded'):
            sphere = 'None'
        elif row[CARD_SPHERE] is not None:
            sphere = row[CARD_SPHERE]
        else:
            sphere = 'None'

        if sphere == 'Boon':
            sphere = 'Neutral'
            subtype_name = 'Boon'
        elif sphere == 'Burden':
            sphere = 'None'
            subtype_name = 'Burden'
        else:
            subtype_name = None

        if row.get(CARD_DOUBLESIDE) is not None:
            card_side = row[CARD_DOUBLESIDE]
        elif (row[CARD_SIDE_B] is not None and
              card_type not in CARD_TYPES_DOUBLESIDE_OPTIONAL):
            card_side = 'A'
        else:
            card_side = None

        if (row[CARD_SIDE_B] is not None and
                row[CARD_SIDE_B] != row[CARD_NAME] and
                card_type in CARD_TYPES_DOUBLESIDE_OPTIONAL):
            opposite_title = row[CARD_SIDE_B]
        else:
            opposite_title = None

        keywords = [k.strip() for k in
                    (row[CARD_KEYWORDS] or '').replace('[inline]', ''
                                                       ).split('.') if k != '']
        keywords = [re.sub(r' ([0-9]+)\[pp\]$', ' \\1 Per Player', k, re.I)
                    for k in keywords]
        keywords = [
            k for k in keywords if re.match(
                r'^[a-z]+(?: -?[0-9X]+(?: Per Player)?)?(?: \([^\)]+\))?$',
                k, re.I)]

        traits = [t.strip() for t in
                  (row[CARD_TRAITS] or '').split('.') if t != '']
        position = (int(row[CARD_NUMBER])
                    if is_positive_or_zero_int(row[CARD_NUMBER]) else 0)
        encounter_set = ((row[CARD_ENCOUNTER_SET] or '')
                         if card_type in CARD_TYPES_ENCOUNTER_SET
                         else row[CARD_ENCOUNTER_SET])
        subtitle = ((row[CARD_ADVENTURE] or '')
                    if card_type in CARD_TYPES_ADVENTURE
                    else row[CARD_ADVENTURE])
        if card_type in ('Presentation', 'Rules'):
            type_name = 'Setup'
        elif card_type == 'Nightmare':
            type_name = 'Nightmare Setup'
        else:
            type_name = card_type or ''

        if card_type in ('Presentation', 'Rules'):
            victory_points = None
        elif card_type in CARD_TYPES_DOUBLESIDE_OPTIONAL:
            victory_points = (
                _handle_int_str(row[CARD_VICTORY])
                or _handle_int_str(row[BACK_PREFIX + CARD_VICTORY]))
        else:
            victory_points = _handle_int_str(row[CARD_VICTORY])

        additional_encounter_sets = [
            s.strip() for s in (row[CARD_ADDITIONAL_ENCOUNTER_SETS] or ''
                                ).split(';')
            if s != ''] or None

        text = _update_card_text('{}\n{}'.format(
            row[CARD_KEYWORDS] or '',
            row[CARD_TEXT] or ''
            )).replace('\n', '\r\n').strip()
        if (card_type in ('Presentation', 'Rules') and
                row[CARD_VICTORY] is not None):
            text = '{}\r\n\r\nPage {}'.format(text, row[CARD_VICTORY])

        if (row[CARD_SIDE_B] is not None and
                (row[BACK_PREFIX + CARD_TEXT] is not None or
                 (card_type in ('Presentation', 'Rules')
                  and row[BACK_PREFIX + CARD_VICTORY] is not None)) and
                card_type in CARD_TYPES_DOUBLESIDE_OPTIONAL):
            text_back = _update_card_text(row[BACK_PREFIX + CARD_TEXT] or ''
                                          ).replace('\n', '\r\n').strip()
            if (card_type in ('Presentation', 'Rules') and
                    row[BACK_PREFIX + CARD_VICTORY] is not None):
                text_back = '{}\r\n\r\nPage {}'.format(
                    text_back, row[BACK_PREFIX + CARD_VICTORY])
            text = '<b>Side A</b> {} <b>Side B</b> {}'.format(text, text_back)

        flavor = (_update_card_text(row[CARD_FLAVOUR] or ''
                                    ).replace('\n', '\r\n').strip())
        if (row[CARD_SIDE_B] is not None and
                row[BACK_PREFIX + CARD_FLAVOUR] is not None and
                card_type in CARD_TYPES_DOUBLESIDE_OPTIONAL):
            flavor_back = _update_card_text(BACK_PREFIX + row[CARD_FLAVOUR]
                                            ).replace('\n', '\r\n').strip()
            flavor = 'Side A: {} Side B: {}'.format(flavor, flavor_back)

        quantity = (int(row[CARD_QUANTITY])
                    if _is_int(row[CARD_QUANTITY]) else 0)

        json_row = {
            'code': '{}{}'.format(row[CARD_SET_RINGSDB_CODE],
                                  str(position).zfill(3)),
            'deck_limit': limit or quantity,
            'flavor': flavor,
            'has_errata': False,
            'illustrator': row[CARD_ARTIST] or 'None',
            'imagesrc': '',
            'is_official': False,
            'is_unique': bool(row[CARD_UNIQUE]),
            'keywords': keywords,
            'name': row[CARD_NAME],
            'octgnid': row[CARD_ID],
            'pack_code': row[CARD_SET_HOB_CODE],
            'pack_name': set_name,
            'position': position,
            'quantity': quantity,
            'sphere_code': sphere.lower().replace(' ', '-'),
            'sphere_name': sphere,
            'text': text,
            'traits': traits,
            'type_code': type_name.lower().replace(' ', '-'),
            'type_name': type_name,
            'url': '',
            'additional_encounter_sets': additional_encounter_sets,
            'attack': _handle_int_str(row[CARD_ATTACK]),
            'card_side': card_side,
            'cost': cost,
            'defense': _handle_int_str(row[CARD_DEFENSE]),
            'easy_mode_quantity': _handle_int(row[CARD_EASY_MODE]),
            'encounter_set': encounter_set,
            'engagement_cost': engagement_cost,
            'health': _handle_int_str(row[CARD_HEALTH]),
            'opposite_stage_letter': opposite_stage_letter,
            'opposite_title': opposite_title,
            'quest_points': quest_points,
            'quest_stage': quest_stage,
            'shadow_text': row[CARD_SHADOW] is not None and
                           _update_card_text(row[CARD_SHADOW]
                                             ).replace('\n', '\r\n').strip()
                           or None,
            'stage_letter': stage_letter,
            'subtitle': subtitle,
            'subtype_code': (subtype_name and subtype_name.lower().replace(' ', '-')
                             or None),
            'subtype_name': subtype_name,
            'threat': threat,
            'threat_strength': _handle_int_str(row[CARD_THREAT]),
            'victory_points': victory_points,
            'willpower': _handle_int_str(row[CARD_WILLPOWER])
            }
        json_row = {k:v for k, v in json_row.items() if v is not None}
        json_data.append(json_row)

    with open(output_path, 'w', encoding='utf-8') as obj:
        res = json.dumps(json_data, ensure_ascii=False)
        obj.write(res)

    logging.info('[%s] ...Generating JSON file for Hall of Beorn (%ss)',
                 set_name, round(time.time() - timestamp, 3))


def _get_xml_property_value(row, name, card_type):
    """ Get Strange Eons xml property value for the given column name.
    """
    value = row[name]
    if value is None:
        value = ''

    if name == CARD_QUANTITY:
        if card_type == 'Rules' and not value:
            value = 1

        return value

    if name in (CARD_TYPE, BACK_PREFIX + CARD_TYPE):
        if card_type in CARD_TYPES_DOUBLESIDE_MANDATORY:
            value = card_type

        return value

    if name in (CARD_SPHERE, BACK_PREFIX + CARD_SPHERE):
        if card_type == 'Rules':
            value = ''

        return value

    return value


def _add_xml_properties(parent, properties, tab):
    """ Append property elements to Strange Eons xml.
    """
    parent.text = '\n' + tab + '  '
    for i, (name, value) in enumerate(properties):
        if not name:
            continue

        prop = ET.SubElement(parent, 'property')
        prop.set('name', name)
        prop.set('value', str(_handle_int_str(value)))

        if i == len(properties) - 1:
            prop.tail = '\n' + tab
        else:
            prop.tail = '\n' + tab + '  '


def generate_xml(conf, set_id, set_name, lang):  # pylint: disable=R0912,R0914,R0915
    """ Generate xml file for Strange Eons.
    """
    logging.info('[%s, %s] Generating xml file for Strange Eons...',
                 set_name, lang)
    timestamp = time.time()

    _backup_previous_xml(conf, set_id, lang)

    root = ET.fromstring(XML_TEMPLATE)
    root.set('name', set_name)
    root.set('id', set_id)
    root.set('icon', SETS[set_id]['Collection Icon'] or '')
    root.set('copyright', SETS[set_id]['Copyright'] or '')
    root.set('language', lang)
    cards = root.findall("./cards")[0]

    translated_columns = {
        CARD_NAME, CARD_TRAITS, CARD_KEYWORDS, CARD_VICTORY, CARD_TEXT,
        CARD_SHADOW, CARD_FLAVOUR, CARD_SIDE_B, BACK_PREFIX + CARD_TRAITS,
        BACK_PREFIX + CARD_KEYWORDS, BACK_PREFIX + CARD_VICTORY,
        BACK_PREFIX + CARD_TEXT, BACK_PREFIX + CARD_SHADOW,
        BACK_PREFIX + CARD_FLAVOUR, CARD_ADVENTURE}

    chosen_data = []
    for row in DATA:
        if row[CARD_ID] is None:
            continue

        if row[CARD_SET] != set_id:
            continue

        row_copy = row.copy()
        if lang != 'English' and TRANSLATIONS[lang].get(row[CARD_ID]):
            for key in translated_columns:
                row_copy[key] = TRANSLATIONS[lang][row[CARD_ID]][key]

        chosen_data.append(row_copy)

    tab_appended = False
    for i, row in enumerate(chosen_data):
        if not tab_appended:
            cards.text = '\n    '
            tab_appended = True

        card = ET.SubElement(cards, 'card')
        card.set('id', row[CARD_ID])
        card.set('name', row[CARD_NAME] or '')

        card_type = row[CARD_TYPE]

        properties = []
        for name in (CARD_NUMBER, CARD_QUANTITY, CARD_ENCOUNTER_SET,
                     CARD_UNIQUE, CARD_TYPE, CARD_SPHERE, CARD_TRAITS,
                     CARD_KEYWORDS, CARD_COST, CARD_ENGAGEMENT, CARD_THREAT,
                     CARD_WILLPOWER, CARD_ATTACK, CARD_DEFENSE, CARD_HEALTH,
                     CARD_QUEST, CARD_VICTORY, CARD_SPECIAL_ICON, CARD_TEXT,
                     CARD_SHADOW, CARD_FLAVOUR, CARD_PRINTED_NUMBER,
                     CARD_ARTIST, CARD_PANX, CARD_PANY, CARD_SCALE,
                     CARD_EASY_MODE, CARD_ADDITIONAL_ENCOUNTER_SETS,
                     CARD_ADVENTURE, CARD_ICON, CARD_VERSION):
            value = _get_xml_property_value(row, name, card_type)
            if value != '':
                properties.append((name, value))

        properties.append(('Set Name', set_name))
        properties.append(('Set Icon', SETS[set_id]['Collection Icon'] or ''))
        properties.append(('Set Copyright', SETS[set_id]['Copyright'] or ''))

        side_b = (card_type != 'Presentation' and (
            card_type in CARD_TYPES_DOUBLESIDE_MANDATORY or row[CARD_SIDE_B]))
        if properties:
            if side_b:
                properties.append(('', ''))

            _add_xml_properties(card, properties, '    ')

        if side_b:
            if (card_type in CARD_TYPES_DOUBLESIDE_MANDATORY
                    and not row[CARD_SIDE_B]):
                alternate_name = row[CARD_NAME]
            else:
                alternate_name = row[CARD_SIDE_B]

            alternate = ET.SubElement(card, 'alternate')
            alternate.set('name', alternate_name or '')
            alternate.set('type', 'B')
            alternate.tail = '\n    '

            properties = []
            for name in (CARD_UNIQUE, CARD_TYPE, CARD_SPHERE, CARD_TRAITS,
                         CARD_KEYWORDS, CARD_COST, CARD_ENGAGEMENT,
                         CARD_THREAT, CARD_WILLPOWER, CARD_ATTACK,
                         CARD_DEFENSE, CARD_HEALTH, CARD_QUEST, CARD_VICTORY,
                         CARD_SPECIAL_ICON, CARD_TEXT, CARD_SHADOW,
                         CARD_FLAVOUR, CARD_PRINTED_NUMBER, CARD_ARTIST,
                         CARD_PANX, CARD_PANY, CARD_SCALE):
                value = _get_xml_property_value(row, BACK_PREFIX + name, card_type)
                if value != '':
                    properties.append((name, value))

            if properties:
                _add_xml_properties(alternate, properties, '      ')

        if i == len(chosen_data) - 1:
            card.tail = '\n  '
        else:
            card.tail = '\n    '

    output_path = os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id, lang))
    with open(output_path, 'w', encoding='utf-8') as obj:
        res = ET.tostring(root, encoding='utf-8').decode('utf-8')
        obj.write(res)

    logging.info('[%s, %s] ...Generating xml file for Strange Eons (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def _collect_artwork_images(conf, image_path):
    """ Collect filenames of artwork images.
    """
    if image_path in IMAGE_CACHE:
        return IMAGE_CACHE[image_path]

    images = {}
    for _, _, filenames in os.walk(image_path):
        for filename in filenames:
            if len(filename.split('.')) < 2 or len(filename.split('_')) < 3:
                continue

            if filename.split('.')[-1] in ('jpg', 'png'):
                image_id = '_'.join(filename.split('_')[:2])
                lang = filename.split('.')[-2]
                if lang in conf['all_languages']:
                    image_id = '{}_{}'.format(image_id, lang)

                if image_id in images:
                    logging.error('Duplicate image detected: %s, '
                                  'ignoring', os.path.join(image_path,
                                                           filename))
                else:
                    images[image_id] = os.path.join(image_path, filename)

        break

    IMAGE_CACHE[image_path] = images
    return images


def _collect_custom_images(image_path):
    """ Collect filenames of custom images.
    """
    if image_path in IMAGE_CACHE:
        return IMAGE_CACHE[image_path]

    images = {}
    for _, _, filenames in os.walk(image_path):
        for filename in filenames:
            if len(filename.split('.')) < 2:
                continue

            if filename.split('.')[-1] in ('jpg', 'png'):
                images[filename] = os.path.join(image_path, filename)

        break

    IMAGE_CACHE[image_path] = images
    return images


def _set_outputs(conf, lang, root):
    """ Set required outputs for Strange Eons.
    """
    if conf['nobleed'][lang] or 'drivethrucards' in conf['outputs'][lang]:
        root.set('png300Bleed', '1')

    if ('makeplayingcards' in conf['outputs'][lang]
            or 'mbprint' in conf['outputs'][lang]
            or 'genericpng' in conf['outputs'][lang]):
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


def update_xml(conf, set_id, set_name, lang):  # pylint: disable=R0912,R0914,R0915
    """ Update the Strange Eons xml file with additional data.
    """
    logging.info('[%s, %s] Updating the Strange Eons xml file with additional '
                 'data...', set_name, lang)
    timestamp = time.time()

    artwork_path = _get_artwork_path(conf, set_id)
    images = _collect_artwork_images(conf, artwork_path)
    processed_images = _collect_artwork_images(
        conf, os.path.join(artwork_path, PROCESSED_ARTWORK_FOLDER))
    images = {**images, **processed_images}
    custom_images = _collect_custom_images(
        os.path.join(artwork_path, IMAGES_CUSTOM_FOLDER))
    xml_path = os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id, lang))

    tree = ET.parse(xml_path)
    root = tree.getroot()
    _set_outputs(conf, lang, root)
    encounter_sets = {}
    encounter_cards = {}

    for card in root[0]:
        card_type = _find_properties(card, 'Type')
        card_type = card_type and card_type[0].attrib['value']
        card_sphere = _find_properties(card, 'Sphere')
        card_sphere = card_sphere and card_sphere[0].attrib['value']
        encounter_set = _find_properties(card, 'Encounter Set')

        if (card_type not in ('Campaign', 'Nightmare', 'Quest', 'Rules',
                              'Treasure')
                and card_sphere not in ('Boon', 'Burden') and encounter_set):
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
            filename = images.get('{}_{}_{}'.format(
                card.attrib['id'], 'Top', lang))
            if not filename:
                filename = images.get('{}_{}'.format(card.attrib['id'], 'Top'))

            if filename:
                prop = _get_property(card, 'ArtworkTop')
                prop.set('value', os.path.split(filename)[-1])
                prop = _get_property(card, 'ArtworkTop Size')
                prop.set('value', str(os.path.getsize(filename)))
                prop = _get_property(card, 'ArtworkTop Modified')
                prop.set('value', str(int(os.path.getmtime(filename))))

            filename = images.get('{}_{}_{}'.format(
                card.attrib['id'], 'Bottom', lang))
            if not filename:
                filename = images.get('{}_{}'.format(card.attrib['id'], 'Bottom'))

            if filename:
                prop = _get_property(card, 'ArtworkBottom')
                prop.set('value', os.path.split(filename)[-1])
                prop = _get_property(card, 'ArtworkBottom Size')
                prop.set('value', str(os.path.getsize(filename)))
                prop = _get_property(card, 'ArtworkBottom Modified')
                prop.set('value', str(int(os.path.getmtime(filename))))


        alternate = [a for a in card if a.attrib.get('type') == 'B']
        if alternate:
            alternate = alternate[0]

        filename = images.get('{}_{}'.format(card.attrib['id'], 'B'))
        if alternate and filename:
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

        try:
            text = _find_properties(card, 'Text')[0].attrib['value']
        except IndexError:
            text = ''

        try:
            alternate_text = _find_properties(alternate, 'Text')[0].attrib['value']
        except IndexError:
            alternate_text = ''

        referred_custom_images = []
        res = re.search(r'\[img custom\/([^ ]+)', text + alternate_text, re.I)
        if res:
            referred_custom_images.extend(res.groups())

        res = re.search(r'\[img "custom\/([^"]+)', text + alternate_text, re.I)
        if res:
            referred_custom_images.extend(res.groups())

        for image in referred_custom_images:
            if image in custom_images:
                prop = _get_property(card, 'Custom Image')
                prop.set('value', '{}|{}|{}'.format(
                    image,
                    os.path.getsize(custom_images[image]),
                    int(os.path.getmtime(custom_images[image]))))

    for card in root[0]:
        if card.attrib['id'] in encounter_cards:
            prop = _get_property(card, 'Encounter Set Total')
            prop.set('value', str(
                encounter_sets[encounter_cards[card.attrib['id']]]))

    if conf['selected_only']:
        cards = list(root[0])
        for card in cards:
            if card.attrib['id'] not in SELECTED_CARDS:
                root[0].remove(card)

    tree.write(xml_path)
    logging.info('[%s, %s] ...Updating the Strange Eons xml file with '
                 'additional data (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def calculate_hashes(set_id, set_name, lang):  # pylint: disable=R0914
    """ Update the Strange Eons xml file with hashes and skip flags.
    """
    logging.info('[%s, %s] Updating the Strange Eons xml file with hashes and '
                 'skip flags...', set_name, lang)
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
        for card in root_old[0]:
            old_hashes[card.attrib['id']] = card.attrib['hash']

        changed_cards = set()
        for row in DATA:
            if row[CARD_SET] != set_id:
                continue

            if row[CARD_CHANGED]:
                changed_cards.add(row[CARD_ID])

        if changed_cards:
            old_file_hash = ''

        if old_file_hash == new_file_hash:
            root.set('skip', '1')

        for card in root[0]:
            if (old_hashes.get(card.attrib['id']) == card.attrib['hash'] and
                    card.attrib['id'] not in changed_cards):
                skip_ids.add(card.attrib['id'])
                card.set('skip', '1')

    tree.write(new_path)

    logging.info('[%s, %s] ...Updating the Strange Eons xml file with hashes '
                 'and skip flags (%ss)',
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

    logging.info('[%s] ...Copying custom image files into the project folder '
                 '(%ss)', set_name, round(time.time() - timestamp, 3))


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

    logging.info('[%s, %s] ...Copying raw image files into the project folder '
                 '(%ss)', set_name, lang, round(time.time() - timestamp, 3))


def copy_xml(set_id, set_name, lang):
    """ Copy the Strange Eons xml file into the project.
    """
    logging.info('[%s, %s] Copying the Strange Eons xml file into '
                 'the project...', set_name, lang)
    timestamp = time.time()

    shutil.copyfile(os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id,
                                                                   lang)),
                    os.path.join(XML_PATH, '{}.{}.xml'.format(set_id, lang)))
    logging.info('[%s, %s] ...Copying the Strange Eons xml file into the '
                 'project (%ss)',
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

    logging.info('[%s, %s] ...Generating images without bleed margins '
                 '(%ss)', set_name, lang, round(time.time() - timestamp, 3))


def generate_png300_db(conf, set_id, set_name, lang, skip_ids):  # pylint: disable=R0914
    """ Generate images for all DB outputs.
    """
    logging.info('[%s, %s] Generating images for all DB outputs...',
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
    known_keys = set()
    for _, _, filenames in os.walk(input_path):
        filenames = sorted(filenames)
        for filename in filenames:
            if filename.split('.')[-1] != 'png':
                continue

            key = filename[50:88]
            if key not in known_keys:
                known_keys.add(key)
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
    logging.info('[%s, %s] ...Generating images for all DB outputs '
                 '(%ss)', set_name, lang, round(time.time() - timestamp, 3))


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
    known_keys = set()
    for _, _, filenames in os.walk(input_path):
        filenames = sorted(filenames)
        for filename in filenames:
            if filename.split('.')[-1] != 'png':
                continue

            key = filename[50:88]
            if key not in known_keys:
                known_keys.add(key)
                shutil.copyfile(os.path.join(input_path, filename),
                                os.path.join(output_path, filename))

        break

    logging.info('[%s, %s] ...Generating images for OCTGN outputs '
                 '(%ss)', set_name, lang, round(time.time() - timestamp, 3))


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
    logging.info('[%s, %s] ...Generating images for MakePlayingCards outputs '
                 '(%ss)', set_name, lang, round(time.time() - timestamp, 3))


def generate_jpg300_bleeddtc(conf, set_id, set_name, lang, skip_ids):  # pylint: disable=R0914
    """ Generate images for DriveThruCards outputs.
    """
    logging.info('[%s, %s] Generating images for DriveThruCards outputs...',
                 set_name, lang)
    timestamp = time.time()

    output_path = os.path.join(IMAGES_EONS_PATH,
                               JPG300BLEEDDTC,
                               '{}.{}'.format(set_id, lang))
    _create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)
    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_jpg300_bleeddtc.{}.{}'.format(set_id,
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
        'python-prepare-drivethrucards-jpg-folder',
        temp_path.replace('\\', '\\\\'),
        output_path.replace('\\', '\\\\'))
    res = subprocess.run(cmd, capture_output=True, shell=True, check=True)
    logging.info('[%s, %s] %s', set_name, lang, res)

    _make_cmyk(conf, output_path)
    _delete_folder(temp_path)
    logging.info('[%s, %s] ...Generating images for DriveThruCards outputs '
                 '(%ss)', set_name, lang, round(time.time() - timestamp, 3))


def generate_jpg800_bleedmbprint(conf, set_id, set_name, lang, skip_ids):  # pylint: disable=R0914
    """ Generate images for MBPrint outputs.
    """
    logging.info('[%s, %s] Generating images for MBPrint outputs...',
                 set_name, lang)
    timestamp = time.time()

    output_path = os.path.join(IMAGES_EONS_PATH,
                               JPG800BLEEDMBPRINT,
                               '{}.{}'.format(set_id, lang))
    _create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)
    temp_path = os.path.join(
        TEMP_ROOT_PATH, 'generate_jpg800_bleedmbprint.{}.{}'.format(set_id,
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
        'python-prepare-mbprint-jpg-folder',
        temp_path.replace('\\', '\\\\'),
        output_path.replace('\\', '\\\\'))
    res = subprocess.run(cmd, capture_output=True, shell=True, check=True)
    logging.info('[%s, %s] %s', set_name, lang, res)

    _make_cmyk(conf, output_path)
    _delete_folder(temp_path)
    logging.info('[%s, %s] ...Generating images for MBPrint outputs '
                 '(%ss)', set_name, lang, round(time.time() - timestamp, 3))


def generate_png800_bleedgeneric(conf, set_id, set_name, lang, skip_ids):  # pylint: disable=R0914
    """ Generate generic PNG images.
    """
    logging.info('[%s, %s] Generating generic PNG images...', set_name, lang)
    timestamp = time.time()

    output_path = os.path.join(IMAGES_EONS_PATH, PNG800BLEEDGENERIC,
                               '{}.{}'.format(set_id, lang))
    _create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)
    temp_path = os.path.join(
        TEMP_ROOT_PATH, 'generate_png800_bleedgeneric.{}.{}'.format(set_id,
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
        'python-prepare-generic-png-folder',
        temp_path.replace('\\', '\\\\'),
        output_path.replace('\\', '\\\\'))
    res = subprocess.run(cmd, capture_output=True, shell=True, check=True)
    logging.info('[%s, %s] %s', set_name, lang, res)

    _delete_folder(temp_path)
    logging.info('[%s, %s] ...Generating generic PNG images (%ss)', set_name,
                 lang, round(time.time() - timestamp, 3))


def _make_low_quality(conf, input_path):
    """ Make low quality 600x429 JPG images from PNG inputs.
    """
    cmd = MAGICK_COMMAND_LOW.format(conf['magick_path'], input_path)
    res = subprocess.run(cmd, capture_output=True, shell=True, check=True)
    logging.info(res)

    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            if (filename.endswith('.jpg')
                    and os.path.getsize(os.path.join(input_path, filename)
                                        ) < IMAGE_MIN_SIZE):
                raise ImageMagickError('ImageMagick conversion failed for {}'
                                       .format(os.path.join(input_path,
                                                            filename)))

        break


def generate_db(conf, set_id, set_name, lang, card_data):  # pylint: disable=R0912,R0914
    """ Generate DB, Preview and RingsDB image outputs.
    """
    logging.info('[%s, %s] Generating DB, Preview and RingsDB image '
                 'outputs...', set_name, lang)
    timestamp = time.time()

    input_path = os.path.join(IMAGES_EONS_PATH, PNG300DB,
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_DB_PATH, '{}.{}'.format(
        _escape_filename(set_name), lang))

    known_filenames = set()
    for _, _, filenames in os.walk(input_path):
        if not filenames:
            logging.error('[%s, %s] No cards found', set_name, lang)
            break

        _create_folder(output_path)
        _clear_folder(output_path)
        filenames = sorted(filenames)
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

    ringsdb_cards = {}
    for row in card_data:
        if row[CARD_SET] == set_id and _needed_for_ringsdb(row):
            card_number = str(_handle_int(row[CARD_NUMBER])).zfill(3)
            ringsdb_cards[card_number] = _ringsdb_code(row)

    pairs = []
    if ringsdb_cards and os.path.exists(output_path):
        for _, _, filenames in os.walk(output_path):
            for filename in filenames:
                card_number = filename[:3]
                if card_number in ringsdb_cards:
                    suffix = '-2' if filename.endswith('-2.png') else ''
                    pairs.append((
                        filename,
                        '{}{}.png'.format(ringsdb_cards[card_number], suffix)))

            break

    if pairs:
        ringsdb_output_path = os.path.join(
            OUTPUT_RINGSDB_IMAGES_PATH, '{}.{}'.format(
                _escape_filename(set_name), lang))
        _create_folder(ringsdb_output_path)
        _clear_folder(ringsdb_output_path)
        for source_filename, target_filename in pairs:
            shutil.copyfile(os.path.join(output_path, source_filename),
                            os.path.join(ringsdb_output_path, target_filename))

    if known_filenames:
        preview_output_path = os.path.join(
            OUTPUT_PREVIEW_IMAGES_PATH, '{}.{}'.format(
                _escape_filename(set_name), lang))
        _create_folder(preview_output_path)
        _clear_folder(preview_output_path)

        temp_path = os.path.join(TEMP_ROOT_PATH,
                                 'generate_db.{}.{}'.format(set_id, lang))
        _create_folder(temp_path)
        _clear_folder(temp_path)
        shutil.copytree(output_path, temp_path)
        _make_low_quality(conf, temp_path)

        for _, _, filenames in os.walk(temp_path):
            for filename in filenames:
                if filename.split('.')[-1] != 'jpg':
                    continue

                shutil.copyfile(os.path.join(temp_path, filename),
                                os.path.join(preview_output_path, filename))

            break

        _delete_folder(temp_path)

    logging.info('[%s, %s] ...Generating DB, Preview and RingsDB image '
                 'outputs (%ss)', set_name, lang,
                 round(time.time() - timestamp, 3))


def generate_octgn(conf, set_id, set_name, lang):
    """ Generate OCTGN image outputs.
    """
    logging.info('[%s, %s] Generating OCTGN image outputs...', set_name, lang)
    timestamp = time.time()

    input_path = os.path.join(IMAGES_EONS_PATH, PNG300OCTGN,
                              '{}.{}'.format(set_id, lang))
    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_octgn.{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_OCTGN_IMAGES_PATH, '{}.{}'.format(
        _escape_filename(set_name), lang))

    _create_folder(temp_path)
    _clear_folder(temp_path)
    shutil.copytree(input_path, temp_path)
    _make_low_quality(conf, temp_path)

    pack_path = os.path.join(output_path,
                             _escape_octgn_filename('{}.{}.o8c'.format(
                                 _escape_filename(set_name), lang)))

    known_filenames = set()
    for _, _, filenames in os.walk(temp_path):
        if not filenames:
            logging.error('[%s, %s] No cards found', set_name, lang)
            break

        _create_folder(output_path)
        filenames = sorted(filenames)
        with zipfile.ZipFile(pack_path, 'w') as zip_obj:
            for filename in filenames:
                if filename.split('.')[-1] != 'jpg':
                    continue

                octgn_filename = re.sub(
                    r'-1\.jpg$', '.jpg',
                    re.sub(r'-2\.jpg$', '.B.jpg', filename))[50:]
                if octgn_filename not in known_filenames:
                    known_filenames.add(octgn_filename)
                    zip_obj.write(os.path.join(temp_path, filename),
                                  '{}/{}/Cards/{}'.format(OCTGN_ZIP_PATH,
                                                          set_id,
                                                          octgn_filename))

        break

    _delete_folder(temp_path)

    logging.info('[%s, %s] ...Generating OCTGN image outputs (%ss)',
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
                    logging.error('Missing card back for %s, removing '
                                  'the file', filename)
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
        logging.error('[%s, %s] No cards found', set_name, lang)
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


def _make_cmyk(conf, input_path):
    """ Convert RGB to CMYK.
    """
    cmd = MAGICK_COMMAND_CMYK.format(conf['magick_path'], input_path)
    res = subprocess.run(cmd, capture_output=True, shell=True, check=True)
    logging.info(res)

    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            if (filename.endswith('.jpg')
                    and os.path.getsize(os.path.join(input_path, filename)
                                        ) < IMAGE_MIN_SIZE):
                raise ImageMagickError('ImageMagick conversion failed for {}'
                                       .format(os.path.join(input_path,
                                                            filename)))

        break


def _prepare_printing_images(input_path, output_path, service):  # pylint: disable=R0912
    """ Prepare printing images for various services.
    """
    for _, _, filenames in os.walk(input_path):
        if not filenames:
            return

        file_type = filenames[0].split('.')[-1]
        for filename in filenames:
            parts = filename.split('-')
            if parts[-1] != '1.{}'.format(file_type):
                continue

            back_official_path = os.path.join(input_path, '{}-2.{}'.format(
                '-'.join(parts[:-1]), file_type))
            back_unofficial_path = back_official_path
            if not os.path.exists(back_official_path):
                if parts[2] == 'p':
                    back_official_path = os.path.join(
                        IMAGES_BACK_PATH, CARD_BACKS['player'][service][0])
                    back_unofficial_path = os.path.join(
                        IMAGES_BACK_PATH, CARD_BACKS['player'][service][1])
                elif parts[2] == 'e':
                    back_official_path = os.path.join(
                        IMAGES_BACK_PATH, CARD_BACKS['encounter'][service][0])
                    back_unofficial_path = os.path.join(
                        IMAGES_BACK_PATH, CARD_BACKS['encounter'][service][1])
                else:
                    logging.error('Missing card back for %s, removing '
                                  'the file', filename)
                    continue

            if parts[1] == 'p':
                for i in range(3):
                    parts[1] = str(i + 1)
                    front_output_path = os.path.join(
                        output_path, re.sub(
                            r'-(?:e|p)-', '-',
                            re.sub('-+', '-',
                                   re.sub(r'.{36}-1(?=\.(?:png|jpg))', '-1o',
                                          '-'.join(parts)))))
                    shutil.copyfile(os.path.join(input_path, filename),
                                    front_output_path)
                    back_unofficial_output_path = os.path.join(
                        output_path, re.sub(
                            r'-(?:e|p)-', '-',
                            re.sub('-+', '-',
                                   re.sub(r'.{36}(?=-2u\.(?:png|jpg)$)', '',
                                          '{}-2u.{}'.format(
                                              '-'.join(parts[:-1]),
                                              file_type)))))
                    shutil.copyfile(back_unofficial_path,
                                    back_unofficial_output_path)
                    if service != 'mpc':
                        back_official_output_path = os.path.join(
                            output_path, re.sub(
                                r'-(?:e|p)-', '-',
                                re.sub('-+', '-',
                                       re.sub(r'.{36}(?=-2o\.(?:png|jpg)$)',
                                              '', '{}-2o.{}'.format(
                                                  '-'.join(parts[:-1]),
                                                  file_type)))))
                        shutil.copyfile(back_official_path,
                                        back_official_output_path)

            else:
                front_output_path = os.path.join(
                    output_path, re.sub(
                        r'-(?:e|p)-', '-',
                        re.sub('-+', '-',
                               re.sub(r'.{36}-1(?=\.(?:png|jpg))', '-1o',
                                      '-'.join(parts)))))
                shutil.copyfile(os.path.join(input_path, filename),
                                front_output_path)
                back_unofficial_output_path = os.path.join(
                    output_path, re.sub(
                        r'-(?:e|p)-', '-',
                        re.sub('-+', '-',
                               re.sub(r'.{36}(?=-2u\.(?:png|jpg)$)', '',
                                      '{}-2u.{}'.format(
                                          '-'.join(parts[:-1]),
                                          file_type)))))
                shutil.copyfile(back_unofficial_path,
                                back_unofficial_output_path)
                if service != 'mpc':
                    back_official_output_path = os.path.join(
                        output_path, re.sub(
                            r'-(?:e|p)-', '-',
                            re.sub('-+', '-',
                                   re.sub(r'.{36}(?=-2o\.(?:png|jpg)$)', '',
                                          '{}-2o.{}'.format(
                                              '-'.join(parts[:-1]),
                                              file_type)))))
                    shutil.copyfile(back_official_path,
                                    back_official_output_path)

        break


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
            if filename.endswith('.png'):
                _insert_png_text(os.path.join(input_path, filename), filename)

        break


def _combine_doublesided_rules_cards(set_id, input_path, card_data, service):  # pylint: disable=R0912,R0914
    """ Combine double-sided rules cards.
    """
    card_data = sorted(
        [r for r in card_data if r[CARD_SET] == set_id],
        key=lambda r: (
            (str(int(r[CARD_NUMBER])).zfill(3)
             if is_positive_or_zero_int(r[CARD_NUMBER])
             else str(r[CARD_NUMBER])),
            _escape_filename(r[CARD_NAME])))

    selected = []
    for i, row in enumerate(card_data):
        if (row[CARD_TYPE] == 'Rules' and
                row[CARD_QUANTITY] == 1 and
                row[BACK_PREFIX + CARD_TEXT] is None and
                row[BACK_PREFIX + CARD_VICTORY] is None):
            card_number = (str(int(row[CARD_NUMBER])).zfill(3)
                           if is_positive_or_zero_int(row[CARD_NUMBER])
                           else str(row[CARD_NUMBER]))
            card_name = _escape_filename(row[CARD_NAME])
            selected.append((i, '{}-1-{}'.format(card_number, card_name)))

    if not selected:
        return

    pairs = []
    while len(selected) > 1:
        if selected[1][0] == selected[0][0] + 1:
            pairs.append((selected[0][1], selected[1][1]))
            selected = selected[2:]
        else:
            selected = selected[1:]

    if not pairs:
        return

    for _, _, filenames in os.walk(input_path):
        if not filenames:
            return

        file_type = filenames[0].split('.')[-1]
        break
    else:
        return

    for pair in pairs:
        first_back_unofficial = os.path.join(
            input_path, '{}-2u.{}'.format(pair[0], file_type))
        second_front = os.path.join(input_path,
                                    '{}-1o.{}'.format(pair[1], file_type))
        second_back_unofficial = os.path.join(
            input_path, '{}-2u.{}'.format(pair[1], file_type))
        if not os.path.exists(first_back_unofficial):
            logging.error('Path %s does not exist', first_back_unofficial)
            continue

        if not os.path.exists(second_front):
            logging.error('Path %s does not exist', second_front)
            continue

        if not os.path.exists(second_back_unofficial):
            logging.error('Path %s does not exist', second_back_unofficial)
            continue

        if service != 'mpc':
            first_back_official = os.path.join(
                input_path, '{}-2o.{}'.format(pair[0], file_type))
            second_back_official = os.path.join(
                input_path, '{}-2o.{}'.format(pair[1], file_type))
            if not os.path.exists(first_back_official):
                logging.error('Path %s does not exist', first_back_official)
                continue

            if not os.path.exists(second_back_official):
                logging.error('Path %s does not exist', second_back_official)
                continue

        shutil.move(second_front, first_back_unofficial)
        os.remove(second_back_unofficial)
        if service != 'mpc':
            shutil.copyfile(first_back_unofficial, first_back_official)
            os.remove(second_back_official)


def _prepare_mpc_printing_archive(input_path, obj):
    """ Prepare archive for MakePlayingCards.
    """
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            if filename.endswith('-1o.png'):
                obj.write(os.path.join(input_path, filename),
                          'front/{}'.format(filename))
            elif filename.endswith('-2u.png'):
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
        back_official_cnt = 0
        back_unofficial_cnt = 0
        filenames = sorted(f for f in filenames
                           if f.endswith('-1o.jpg')
                           or f.endswith('-2o.jpg')
                           or f.endswith('-2u.jpg'))
        total_cnt = len(filenames) / 3
        for filename in filenames:
            if filename.endswith('-1o.jpg'):
                front_cnt += 1
                obj.write(os.path.join(input_path, filename),
                          '{}front/{}'.format(_deck_name(front_cnt, total_cnt),
                                              filename))
            elif filename.endswith('-2o.jpg'):
                back_official_cnt += 1
                obj.write(os.path.join(input_path, filename),
                          '{}back_official/{}'.format(
                              _deck_name(back_official_cnt, total_cnt),
                              filename))
            elif filename.endswith('-2u.jpg'):
                back_unofficial_cnt += 1
                obj.write(os.path.join(input_path, filename),
                          '{}back_unofficial/{}'.format(
                              _deck_name(back_unofficial_cnt, total_cnt),
                              filename))

        break


def _prepare_mbprint_printing_archive(input_path, obj):
    """ Prepare archive for MBPrint.
    """
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            if filename.endswith('-1o.jpg'):
                obj.write(os.path.join(input_path, filename),
                          'front/{}'.format(filename))
            elif filename.endswith('-0o.jpg'):
                obj.write(os.path.join(input_path, filename),
                          'back_official/{}'.format(filename))
            elif filename.endswith('-0u.jpg'):
                obj.write(os.path.join(input_path, filename),
                          'back_unofficial/{}'.format(filename))

        break


def _prepare_genericpng_printing_archive(input_path, obj):
    """ Prepare archive of generic PNG images.
    """
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            if filename.endswith('-1o.png'):
                obj.write(os.path.join(input_path, filename),
                          'front/{}'.format(filename))
            elif filename.endswith('-2o.png'):
                obj.write(os.path.join(input_path, filename),
                          'back_official/{}'.format(filename))
            elif filename.endswith('-2u.png'):
                obj.write(os.path.join(input_path, filename),
                          'back_unofficial/{}'.format(filename))

        break


def generate_mpc(conf, set_id, set_name, lang, card_data):
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
            logging.error('[%s, %s] No cards found', set_name, lang)
            logging.info('[%s, %s] ...Generating MakePlayingCards outputs '
                         '(%ss)',
                         set_name, lang, round(time.time() - timestamp, 3))
            return

        break

    _create_folder(output_path)
    _create_folder(temp_path)
    _clear_folder(temp_path)
    _prepare_printing_images(input_path, temp_path, 'mpc')
    _make_unique_png(temp_path)
    _combine_doublesided_rules_cards(set_id, temp_path, card_data, 'mpc')

    if 'makeplayingcards_zip' in conf['outputs'][lang]:
        with zipfile.ZipFile(
                os.path.join(output_path,
                             'MPC.{}.{}.images.zip'.format(
                                 _escape_filename(set_name), lang)),
                'w') as obj:
            _prepare_mpc_printing_archive(temp_path, obj)
            obj.write('MakePlayingCards.pdf', 'MakePlayingCards.pdf')

    if 'makeplayingcards_7z' in conf['outputs'][lang]:
        with py7zr.SevenZipFile(
                os.path.join(output_path,
                             'MPC.{}.{}.images.7z'.format(
                                 _escape_filename(set_name), lang)),
                'w', filters=PY7ZR_FILTERS) as obj:
            _prepare_mpc_printing_archive(temp_path, obj)
            obj.write('MakePlayingCards.pdf', 'MakePlayingCards.pdf')

    _delete_folder(temp_path)
    logging.info('[%s, %s] ...Generating MakePlayingCards outputs (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def generate_dtc(conf, set_id, set_name, lang, card_data):
    """ Generate DriveThruCards outputs.
    """
    logging.info('[%s, %s] Generating DriveThruCards outputs...',
                 set_name, lang)
    timestamp = time.time()

    input_path = os.path.join(IMAGES_EONS_PATH,
                              JPG300BLEEDDTC,
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_DTC_PATH, '{}.{}'.format(
        _escape_filename(set_name), lang))
    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_dtc.{}.{}'.format(set_id, lang))

    for _, _, filenames in os.walk(input_path):
        if not filenames:
            logging.error('[%s, %s] No cards found', set_name, lang)
            logging.info('[%s, %s] ...Generating DriveThruCards outputs (%ss)',
                         set_name, lang, round(time.time() - timestamp, 3))
            return

        break

    _create_folder(output_path)
    _create_folder(temp_path)
    _clear_folder(temp_path)
    _prepare_printing_images(input_path, temp_path, 'dtc')
    _combine_doublesided_rules_cards(set_id, temp_path, card_data, 'dtc')

    if 'drivethrucards_zip' in conf['outputs'][lang]:
        with zipfile.ZipFile(
                os.path.join(output_path,
                             'DTC.{}.{}.images.zip'.format(
                                 _escape_filename(set_name), lang)),
                'w') as obj:
            _prepare_dtc_printing_archive(temp_path, obj)
            obj.write('DriveThruCards.pdf', 'DriveThruCards.pdf')

    if 'drivethrucards_7z' in conf['outputs'][lang]:
        with py7zr.SevenZipFile(
                os.path.join(output_path,
                             'DTC.{}.{}.images.7z'.format(
                                 _escape_filename(set_name), lang)),
                'w', filters=PY7ZR_FILTERS) as obj:
            _prepare_dtc_printing_archive(temp_path, obj)
            obj.write('DriveThruCards.pdf', 'DriveThruCards.pdf')

    _delete_folder(temp_path)
    logging.info('[%s, %s] ...Generating DriveThruCards outputs (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def generate_mbprint(conf, set_id, set_name, lang, card_data):  # pylint: disable=R0914
    """ Generate MBPrint outputs.
    """
    logging.info('[%s, %s] Generating MBPrint outputs...',
                 set_name, lang)
    timestamp = time.time()

    input_path = os.path.join(IMAGES_EONS_PATH,
                              JPG800BLEEDMBPRINT,
                              '{}.{}'.format(set_id, lang))
    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_mbprint.{}.{}'.format(set_id, lang))

    for _, _, filenames in os.walk(input_path):
        if not filenames:
            logging.error('[%s, %s] No cards found', set_name, lang)
            logging.info('[%s, %s] ...Generating MBPrint outputs (%ss)',
                         set_name, lang, round(time.time() - timestamp, 3))
            return

        break

    _create_folder(temp_path)
    _clear_folder(temp_path)
    _prepare_printing_images(input_path, temp_path, 'mbprint')
    _combine_doublesided_rules_cards(set_id, temp_path, card_data, 'mbprint')

    for _, _, filenames in os.walk(temp_path):
        for filename in filenames:
            if filename.endswith('-2o.jpg'):
                os.rename(
                    os.path.join(temp_path, filename),
                    os.path.join(temp_path,
                                 re.sub(r'-2o\.jpg$', '-0o.jpg', filename)))
            elif filename.endswith('-2u.jpg'):
                os.rename(
                    os.path.join(temp_path, filename),
                    os.path.join(temp_path,
                                 re.sub(r'-2u\.jpg$', '-0u.jpg', filename)))

        break

    if ('mbprint_zip' in conf['outputs'][lang] or
            'mbprint_7z' in conf['outputs'][lang]):
        output_path = os.path.join(OUTPUT_MBPRINT_PATH, '{}.{}'.format(
            _escape_filename(set_name), lang))
        _create_folder(output_path)

        if 'mbprint_zip' in conf['outputs'][lang]:
            with zipfile.ZipFile(
                    os.path.join(output_path,
                                 'MBPRINT.{}.{}.images.zip'.format(
                                     _escape_filename(set_name), lang)),
                    'w') as obj:
                _prepare_mbprint_printing_archive(temp_path, obj)
                obj.write('MBPrint.pdf', 'MBPrint.pdf')

        if 'mbprint_7z' in conf['outputs'][lang]:
            with py7zr.SevenZipFile(
                    os.path.join(output_path,
                                 'MBPRINT.{}.{}.images.7z'.format(
                                     _escape_filename(set_name), lang)),
                    'w', filters=PY7ZR_FILTERS) as obj:
                _prepare_mbprint_printing_archive(temp_path, obj)
                obj.write('MBPrint.pdf', 'MBPrint.pdf')

    if ('mbprint_pdf_zip' in conf['outputs'][lang] or
            'mbprint_pdf_7z' in conf['outputs'][lang]):
        pdf_filename = 'MBPRINT.{}.{}.pdf'.format(_escape_filename(set_name),
                                                  lang)
        pdf_path = os.path.join(temp_path, pdf_filename)
        cmd = MAGICK_COMMAND_PDF.format(conf['magick_path'], temp_path,
                                        pdf_path)
        res = subprocess.run(cmd, capture_output=True, shell=True, check=True)
        logging.info(res)

        output_path = os.path.join(OUTPUT_MBPRINT_PDF_PATH, '{}.{}'.format(
            _escape_filename(set_name), lang))
        _create_folder(output_path)

        if 'mbprint_pdf_zip' in conf['outputs'][lang]:
            with zipfile.ZipFile(
                    os.path.join(output_path,
                                 'MBPRINT.{}.{}.pdf.zip'.format(
                                     _escape_filename(set_name), lang)),
                    'w') as obj:
                obj.write(pdf_path, pdf_filename)

        if 'mbprint_pdf_7z' in conf['outputs'][lang]:
            with py7zr.SevenZipFile(
                    os.path.join(output_path,
                                 'MBPRINT.{}.{}.pdf.7z'.format(
                                     _escape_filename(set_name), lang)),
                    'w', filters=PY7ZR_FILTERS) as obj:
                obj.write(pdf_path, pdf_filename)

    _delete_folder(temp_path)
    logging.info('[%s, %s] ...Generating MBPrint outputs (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def generate_genericpng(conf, set_id, set_name, lang, card_data):
    """ Generate generic PNG outputs.
    """
    logging.info('[%s, %s] Generating generic PNG outputs...', set_name, lang)
    timestamp = time.time()

    input_path = os.path.join(IMAGES_EONS_PATH, PNG800BLEEDGENERIC,
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_GENERICPNG_PATH, '{}.{}'.format(
        _escape_filename(set_name), lang))
    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_genericpng.{}.{}'.format(set_id, lang))

    for _, _, filenames in os.walk(input_path):
        if not filenames:
            logging.error('[%s, %s] No cards found', set_name, lang)
            logging.info('[%s, %s] ...Generating generic PNG outputs (%ss)',
                         set_name, lang, round(time.time() - timestamp, 3))
            return

        break

    _create_folder(output_path)
    _create_folder(temp_path)
    _clear_folder(temp_path)
    _prepare_printing_images(input_path, temp_path, 'genericpng')
    _combine_doublesided_rules_cards(set_id, temp_path, card_data,
                                     'genericpng')

    if 'genericpng_zip' in conf['outputs'][lang]:
        with zipfile.ZipFile(
                os.path.join(output_path,
                             'Generic.{}.{}.images.zip'.format(
                                 _escape_filename(set_name), lang)),
                'w') as obj:
            _prepare_genericpng_printing_archive(temp_path, obj)

    if 'genericpng_7z' in conf['outputs'][lang]:
        with py7zr.SevenZipFile(
                os.path.join(output_path,
                             'Generic.{}.{}.images.7z'.format(
                                 _escape_filename(set_name), lang)),
                'w', filters=PY7ZR_FILTERS) as obj:
            _prepare_genericpng_printing_archive(temp_path, obj)

    _delete_folder(temp_path)
    logging.info('[%s, %s] ...Generating generic PNG outputs (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def _copy_octgn_set_xml_outputs(temp_path, destination_path, sets):
    """ Copy OCTGN set.xml files to the destination folder.
    """
    archive_path = os.path.join(temp_path, 'copy_octgn_set_xml_outputs.zip')
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_STORED) as obj:
        for _, folders, _ in os.walk(OUTPUT_OCTGN_PATH):
            for folder in folders:
                for _, subfolders, _ in os.walk(
                        os.path.join(OUTPUT_OCTGN_PATH, folder)):
                    for subfolder in subfolders:
                        if subfolder not in sets:
                            continue

                        xml_path = os.path.join(OUTPUT_OCTGN_PATH, folder,
                                                subfolder, OCTGN_SET_XML)
                        if os.path.exists(xml_path):
                            obj.write(xml_path, '{}/{}'.format(subfolder,
                                                               OCTGN_SET_XML))

                    break

            break

    with zipfile.ZipFile(archive_path) as obj:
        obj.extractall(destination_path)

    os.remove(archive_path)


def _copy_octgn_o8d_outputs(temp_path, destination_path, sets):
    """ Copy OCTGN set.xml files to the destination folder.
    """
    set_folders = {_escape_filename(SETS[s]['Name']) for s in sets}
    archive_path = os.path.join(temp_path, 'copy_octgn_o8d_outputs.zip')
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_STORED) as obj:
        for _, folders, _ in os.walk(OUTPUT_OCTGN_DECKS_PATH):
            for folder in folders:
                if folder not in set_folders:
                    continue

                for _, _, filenames in os.walk(
                        os.path.join(OUTPUT_OCTGN_DECKS_PATH, folder)):

                    for filename in filenames:
                        if not filename.endswith('.o8d'):
                            continue

                        obj.write(os.path.join(OUTPUT_OCTGN_DECKS_PATH, folder,
                                               filename),
                                  filename)

                    break

            break

    with zipfile.ZipFile(archive_path) as obj:
        obj.extractall(destination_path)

    os.remove(archive_path)


def copy_octgn_outputs(conf, sets):
    """ Copy OCTGN outputs to the destination folder.
    """
    logging.info('Copying OCTGN outputs to the destination folder...')
    timestamp = time.time()

    chosen_sets = {s[0] for s in sets}.intersection(FOUND_SETS)
    chosen_scratch_sets = {s[0] for s in sets}.intersection(FOUND_SCRATCH_SETS)

    temp_path = os.path.join(TEMP_ROOT_PATH, 'copy_octgn_outputs')
    _create_folder(temp_path)
    _clear_folder(temp_path)

    if (chosen_sets and conf['octgn_set_xml']
            and conf['octgn_set_xml_destination_path']):
        _copy_octgn_set_xml_outputs(
            temp_path,
            conf['octgn_set_xml_destination_path'],
            chosen_sets)

    if (chosen_scratch_sets and conf['octgn_set_xml']
            and conf['octgn_set_xml_scratch_destination_path']):
        _copy_octgn_set_xml_outputs(
            temp_path,
            conf['octgn_set_xml_scratch_destination_path'],
            chosen_scratch_sets)

    if (chosen_sets and conf['octgn_o8d']
            and conf['octgn_o8d_destination_path']):
        _copy_octgn_o8d_outputs(
            temp_path,
            conf['octgn_o8d_destination_path'],
            chosen_sets)

    if (chosen_scratch_sets and conf['octgn_o8d']
            and conf['octgn_o8d_scratch_destination_path']):
        _copy_octgn_o8d_outputs(
            temp_path,
            conf['octgn_o8d_scratch_destination_path'],
            chosen_scratch_sets)

    _delete_folder(temp_path)

    logging.info('...Copying OCTGN outputs to the destination folder (%ss)',
                 round(time.time() - timestamp, 3))
