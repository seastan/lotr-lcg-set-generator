"""LotR ALeP workflow.
"""
import hashlib
import math
import os
import re
import shutil
import subprocess
import zipfile

import xml.etree.ElementTree as ET
import py7zr
import requests
import xlwings as xw
import yaml

from reportlab.lib.pagesizes import landscape, letter, A4
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

CARDS_RANGE = 'A2:AU1001'
PROJECT_FOLDER = 'Frogmorton'
SET_IDS_ROWS = (3, 102)
SHEET_NAME = 'setExcel'

CONFIGURATION_PATH = 'configuration.yaml'
IMAGES_BACK_PATH = 'imagesBack'
IMAGES_EONS_PATH = 'imagesEons'
IMAGES_RAW_PATH = os.path.join(PROJECT_FOLDER, 'imagesRaw')
IMAGES_ZIP_PATH = '{}/Export/'.format(os.path.split(PROJECT_FOLDER)[-1])
MACROS_PATH = 'macros.xlsm'
MACROS_COPY_PATH = 'macros_copy.xlsm'
OCTGN_ZIP_PATH = 'imagesOCTGN/a21af4e8-be4b-4cda-a6b6-534f9717391f/Sets'
OUTPUT_DB_PATH = os.path.join('Output', 'DB')
OUTPUT_MPC_PATH = os.path.join('Output', 'MakePlayingCards')
OUTPUT_OCTGN_PATH = os.path.join('Output', 'OCTGN')
OUTPUT_PDF_PATH = os.path.join('Output', 'PDF')
PROJECT_PATH = 'setGenerator.seproject'
SET_EONS_PATH = 'setEons'
SHEET_ROOT_PATH = ''
TEMP_PATH = 'Temp'
XML_PATH = os.path.join(PROJECT_FOLDER, 'XML')


def _find_properties(parent, name):
    """ Find properties with a given name.
    """
    properties = [p for p in parent if p.attrib.get('name') == name]
    return properties


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


def clear_folder(folder):
    """ Clear the folder.
    """
    for _, _, filenames in os.walk(folder):
        for filename in filenames:
            if filename not in ('seproject', '.gitignore'):
                os.remove(os.path.join(folder, filename))

        break


def read_conf():
    """ Read project configuration.
    """
    with open(CONFIGURATION_PATH, 'r') as f_conf:
        conf = yaml.safe_load(f_conf)

    return conf


def download_sheet(conf):
    """ Download cards spreadsheet from Google Drive and return the local path.
    """
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

    return sheet_path


def get_sets(conf, sheet_path):
    """ Get all sets to work on (return set id, set name, set row).
    """
    xlwb = xw.Book(sheet_path)
    try:
        sets = []
        sheet = xlwb.sheets['Sets']
        for row in range(*SET_IDS_ROWS):
            set_id = sheet.range((row, 1)).value
            if set_id and set_id in conf['set_ids']:
                sets.append((set_id, sheet.range((row, 2)).value, row))
    finally:
        xlwb.close()

    if not sets:
        print('No sets found')

    return sets


def backup_previous_xml(conf, set_id):
    """ Backup the previous setEons.xml for the set.
    """
    if os.path.exists(os.path.join(SET_EONS_PATH, set_id, 'setEons.xml')):
        shutil.move(os.path.join(SET_EONS_PATH, set_id, 'setEons.xml'),
                    os.path.join(SET_EONS_PATH, set_id, 'setEons.xml.old'))

    if (conf['from_scratch'] and os.path.exists(
            os.path.join(SET_EONS_PATH, set_id, 'setEons.xml.old'))):
        os.remove(os.path.join(SET_EONS_PATH, set_id, 'setEons.xml.old'))


def generate_xmls(sheet_path, set_row):
    """ Generate xml files for StrangeEons and OCTGN.

    Copy the data over to sheet that contains the macros, and run the macros.
    This will create two xml files with the card data.  One is setEons.xml,
    needed by Strange Eons.  The second is set.xml and required by OCTGN.
    """
    shutil.copyfile(MACROS_PATH, MACROS_COPY_PATH)
    xlwb1 = xw.Book(sheet_path)
    try:
        xlwb2 = xw.Book(MACROS_COPY_PATH)
        try:
            data = xlwb1.sheets['Sets'].range(
                'A{}:B{}'.format(set_row, set_row)).value  # pylint: disable=W1308
            xlwb2.sheets['Sets'].range('A3:B3').value = data

            card_sheet = xlwb2.sheets['Card Data']
            data = xlwb1.sheets['Card Data'].range(CARDS_RANGE).value
            card_sheet.range(CARDS_RANGE).value = data

            card_sheet.range(CARDS_RANGE).api.Sort(
                Key1=card_sheet.range('Set').api,
                Order1=xw.constants.SortOrder.xlAscending,
                Key2=card_sheet.range('CardNumber').api,
                Order2=xw.constants.SortOrder.xlAscending)

            xlwb2.macro('SaveOCTGN')()
            xlwb2.macro('SaveXML')()
            xlwb2.save()
        finally:
            xlwb2.close()
    finally:
        xlwb1.close()


def update_xml(conf, set_id):
    # Clear raw image files in the project folder
    clear_folder(IMAGES_RAW_PATH)

    # Parse artwork images
    if os.path.exists(os.path.join(conf['artwork_path'], SET_UUID)):
        artwork_path = os.path.join(conf['artwork_path'], SET_UUID)
    else:
        artwork_path = conf['artwork_path']

    images = {}
    for _, _, filenames in os.walk(artwork_path):
        for filename in filenames:
            if filename.split('.')[-1] in ('jpg', 'png'):
                card_id_side = '_'.join(filename.split('_')[:2])
                images[card_id_side] = filename

        break

    # Update setEons.xml with artwork, artists and encounter set numbers
    tree = ET.parse(os.path.join(SET_EONS_PATH, SET_UUID, 'setEons.xml'))
    root = tree.getroot()
    encounter_sets = {}
    encounter_cards = {}

    for card in root[0]:
        card_type = find_properties(card, 'Type')[0].attrib['value']
        encounter_set = find_properties(card, 'Encounter Set')
        if card_type != 'Quest' and encounter_set:
            encounter_set = encounter_set[0].attrib['value']
            encounter_cards[card.attrib['id']] = encounter_set
            prop = get_property(card, 'Encounter Set Number')
            prop.set('value', str(encounter_sets.get(encounter_set, 0) + 1))
            quantity = int(find_properties(card, 'Quantity')[0].attrib['value'])
            encounter_sets[encounter_set] = encounter_sets.get(encounter_set, 0) + quantity

        filename = images.get('{}_{}'.format(card.attrib['id'], 'A'))
        if filename:
            prop = get_property(card, 'Artwork')
            prop.set('value', filename)
            prop = get_property(card, 'Artwork Size')
            prop.set('value', str(os.path.getsize(os.path.join(artwork_path, filename))))
            prop = get_property(card, 'Artwork Modified')
            prop.set('value', str(int(os.path.getmtime(os.path.join(artwork_path, filename)))))

            artist = find_properties(card, 'Artist')
            if not artist and '_Artist_' in filename:
                artist_value = '.'.join('_Artist_'.join(
                    filename.split('_Artist_')[1:]).split('.')[:-1]).replace('_', ' ')
                prop = get_property(card, 'Artist')
                prop.set('value', artist_value)

        filename = images.get('{}_{}'.format(card.attrib['id'], 'B'))
        alternate = [a for a in card if a.attrib.get('type') == 'B']
        if filename and alternate:
            alternate = alternate[0]
            prop = get_property(alternate, 'Artwork')
            prop.set('value', filename)
            prop = get_property(alternate, 'Artwork Size')
            prop.set('value', str(os.path.getsize(os.path.join(artwork_path, filename))))
            prop = get_property(alternate, 'Artwork Modified')
            prop.set('value', str(int(os.path.getmtime(os.path.join(artwork_path, filename)))))

            artist = find_properties(alternate, 'Artist')
            if not artist and '_Artist_' in filename:
                artist_value = '.'.join('_Artist_'.join(
                    filename.split('_Artist_')[1:]).split('.')[:-1]).replace('_', ' ')
                prop = get_property(alternate, 'Artist')
                prop.set('value', artist_value)

    # Update setEons.xml with encounter set total and card hash
    for card in root[0]:
        if card.attrib['id'] in encounter_cards:
            prop = get_property(card, 'Encounter Set Total')
            prop.set('value', str(encounter_sets[encounter_cards[card.attrib['id']]]))

        card_hash = hashlib.md5(re.sub('\n\s*', '', ET.tostring(card, encoding='unicode').strip()).encode()).hexdigest()
        card.set('hash', card_hash)

    # Mark cards, which were not changed since the previous script run and copy artwork images into the project
    old_hashes = {}
    skip_ids = set()
    if os.path.exists(os.path.join(SET_EONS_PATH, SET_UUID, 'setEons.xml.old')):
        tree_old = ET.parse(os.path.join(SET_EONS_PATH, SET_UUID, 'setEons.xml.old'))
        root_old = tree_old.getroot()
        for card in root_old[0]:
            old_hashes[card.attrib['id']] = card.attrib['hash']

    for card in root[0]:
        if old_hashes.get(card.attrib['id']) == card.attrib['hash']:
            skip_ids.add(card.attrib['id'])
            card.set('skip', '1')
        else:
            filename = find_properties(card, 'Artwork')
            if filename:
                filename = filename[0].attrib['value']
                _ = shutil.copyfile(os.path.join(artwork_path, filename),
                                    os.path.join(IMAGES_RAW_PATH, filename))

            alternate = [a for a in card if a.attrib.get('type') == 'B']
            if alternate:
                alternate = alternate[0]
                filename = find_properties(alternate, 'Artwork')
                if filename:
                    filename = filename[0].attrib['value']
                    _ = shutil.copyfile(os.path.join(artwork_path, filename),
                                        os.path.join(IMAGES_RAW_PATH, filename))

    tree.write(os.path.join(SET_EONS_PATH, SET_UUID, 'setEons.xml'))
