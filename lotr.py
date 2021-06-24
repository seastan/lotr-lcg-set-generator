# pylint: disable=C0302
# -*- coding: utf8 -*-
""" Helper functions for LotR ALeP workflow.
"""
import codecs
from collections import OrderedDict
import copy
import csv
from datetime import datetime
import hashlib
from io import StringIO
import json
import logging
import math
import os
import re
import shutil
import ssl
import subprocess
import time
import uuid
import xml.etree.ElementTree as ET
import zipfile

import requests
import unidecode
import urllib3
import yaml

try:
    import paramiko
    import png
    import py7zr
    from reportlab.lib.pagesizes import landscape, letter, A4
    from reportlab.lib.units import inch
    from reportlab.pdfgen.canvas import Canvas
    from scp import SCPClient

    PY7ZR_FILTERS = [{'id': py7zr.FILTER_LZMA2,
                      'preset': 9 | py7zr.PRESET_EXTREME}]
except Exception:  # pylint: disable=W0703
    pass


SET_SHEET = 'Sets'
CARD_SHEET = 'Card Data'
SCRATCH_SHEET = 'Scratch Data'

SET_ID = 'GUID'
SET_NAME = 'Name'
SET_VERSION = 'Version'
SET_COLLECTION_ICON = 'Collection Icon'
SET_RINGSDB_CODE = 'RingsDB Code'
SET_HOB_CODE = 'HoB Code'
SET_DISCORD_PREFIX = 'Discord Prefix'
SET_COPYRIGHT = 'Copyright'
SET_LOCKED = 'Locked'

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
CARD_BACK = 'Card Back'
CARD_VERSION = 'Version'
CARD_DECK_RULES = 'Deck Rules'
CARD_SELECTED = 'Selected'
CARD_CHANGED = 'Changed'
CARD_BOT_DISABLED = 'Bot Disabled'

CARD_SCRATCH = '_Scratch'
CARD_SET_NAME = '_Set Name'
CARD_SET_RINGSDB_CODE = '_Set RingsDB Code'
CARD_SET_HOB_CODE = '_Set HoB Code'
CARD_SET_LOCKED = '_Locked'
CARD_RINGSDB_CODE = '_RingsDB Code'
CARD_NORMALIZED_NAME = '_Normalized Name'
CARD_DISCORD_CHANNEL = '_Discord Channel'
CARD_DISCORD_CATEGORY = '_Discord Category'

CARD_DOUBLESIDE = '_Card Side'
CARD_ORIGINAL_NAME = '_Original Name'

MAX_COLUMN = '_Max Column'
ROW_COLUMN = '_Row'

DISCORD_IGNORE_COLUMNS = {
    CARD_PANX, CARD_PANY, CARD_SCALE, BACK_PREFIX + CARD_PANX,
    BACK_PREFIX + CARD_PANY, BACK_PREFIX + CARD_SCALE, CARD_SIDE_B,
    CARD_SELECTED, CARD_CHANGED, CARD_SCRATCH
}

DISCORD_IGNORE_CHANGES_COLUMNS = {
    CARD_SET, CARD_NUMBER, CARD_SET_NAME, CARD_SET_RINGSDB_CODE,
    CARD_SET_HOB_CODE, CARD_SET_LOCKED, CARD_RINGSDB_CODE, CARD_BOT_DISABLED,
    CARD_NORMALIZED_NAME, BACK_PREFIX + CARD_NORMALIZED_NAME,
    CARD_DISCORD_CHANNEL, CARD_DISCORD_CATEGORY, ROW_COLUMN
}

TRANSLATED_COLUMNS = {
    CARD_NAME, CARD_TRAITS, CARD_KEYWORDS, CARD_VICTORY, CARD_TEXT,
    CARD_SHADOW, CARD_FLAVOUR, CARD_SIDE_B, BACK_PREFIX + CARD_TRAITS,
    BACK_PREFIX + CARD_KEYWORDS, BACK_PREFIX + CARD_VICTORY,
    BACK_PREFIX + CARD_TEXT, BACK_PREFIX + CARD_SHADOW,
    BACK_PREFIX + CARD_FLAVOUR, CARD_ADVENTURE
}

CARD_TYPES = {'Ally', 'Attachment', 'Campaign', 'Contract', 'Enemy',
              'Encounter Side Quest', 'Event', 'Hero', 'Location', 'Nightmare',
              'Objective', 'Objective Ally', 'Objective Hero',
              'Objective Location', 'Player Side Quest', 'Presentation',
              'Quest', 'Rules', 'Ship Enemy', 'Ship Objective', 'Treachery',
              'Treasure'}
CARD_TYPES_LANDSCAPE = {'Encounter Side Quest', 'Player Side Quest', 'Quest'}
CARD_TYPES_DOUBLESIDE_MANDATORY = {'Campaign', 'Nightmare', 'Presentation',
                                   'Quest', 'Rules'}
CARD_TYPES_DOUBLESIDE_OPTIONAL = {'Campaign', 'Contract', 'Nightmare',
                                  'Presentation', 'Quest', 'Rules'}
CARD_TYPES_PLAYER = {'Ally', 'Attachment', 'Contract', 'Event', 'Hero',
                     'Player Side Quest', 'Treasure'}
CARD_TYPES_PLAYER_DECK = {'Ally', 'Attachment', 'Event', 'Player Side Quest'}
CARD_TYPES_PLAYER_SPHERE = {'Ally', 'Attachment', 'Event', 'Hero',
                            'Player Side Quest'}
CARD_TYPES_ENCOUNTER_SET = {'Campaign', 'Enemy', 'Encounter Side Quest',
                            'Location', 'Nightmare', 'Objective',
                            'Objective Ally', 'Objective Hero',
                            'Objective Location', 'Quest', 'Ship Enemy',
                            'Ship Objective', 'Treachery'}
CARD_TYPES_NO_ENCOUNTER_SET = {'Ally', 'Attachment', 'Contract', 'Event',
                               'Hero', 'Player Side Quest'}
CARD_TYPES_ENCOUNTER_SIZE = {'Enemy', 'Location', 'Objective',
                             'Objective Ally', 'Objective Hero',
                             'Objective Location', 'Ship Enemy',
                             'Ship Objective', 'Treachery', 'Treasure'}
CARD_TYPES_TRAITS = {'Ally', 'Enemy', 'Hero', 'Location', 'Objective Ally',
                     'Objective Hero', 'Objective Location', 'Ship Enemy',
                     'Ship Objective', 'Treasure'}
CARD_TYPES_NO_TRAITS = {'Campaign', 'Contract', 'Nightmare', 'Presentation',
                        'Quest', 'Rules'}
CARD_TYPES_NO_KEYWORDS = {'Campaign', 'Contract', 'Nightmare', 'Presentation',
                          'Rules'}
CARD_TYPES_ADVENTURE = {'Campaign', 'Objective', 'Objective Ally',
                        'Objective Hero', 'Objective Location',
                        'Ship Objective', 'Quest'}
CARD_TYPES_UNIQUE = {'Hero', 'Objective Hero'}
CARD_TYPES_NON_UNIQUE = {'Campaign', 'Contract', 'Event', 'Nightmare',
                         'Player Side Quest', 'Presentation', 'Quest', 'Rules',
                         'Treachery', 'Treasure'}
CARD_TYPES_DECK_RULES = {'Nightmare', 'Quest'}
CARD_TYPES_ONE_COPY = {'Campaign', 'Contract', 'Encounter Side Quest', 'Hero',
                       'Nightmare', 'Objective Hero', 'Presentation', 'Quest',
                       'Rules', 'Treasure'}
CARD_TYPES_THREE_COPIES = {'Ally', 'Attachment', 'Event', 'Player Side Quest'}
CARD_TYPES_BOON = {'Attachment', 'Event', 'Objective Ally'}
CARD_TYPES_BURDEN = {'Enemy', 'Objective', 'Treachery'}
CARD_TYPES_NIGHTMARE = {'Encounter Side Quest', 'Enemy', 'Location',
                        'Objective', 'Ship Enemy', 'Treachery', 'Quest'}

SPHERES = set()
SPHERES_CAMPAIGN = {'Setup'}
SPHERES_PLAYER = {'Baggins', 'Fellowship', 'Leadership', 'Lore', 'Neutral',
                  'Spirit', 'Tactics'}
SPHERES_PRESENTATION = {'Blue', 'Green', 'Purple', 'Red', 'Brown', 'Yellow',
                        'Nightmare Blue', 'Nightmare Green',
                        'Nightmare Purple', 'Nightmare Red', 'Nightmare Brown',
                        'Nightmare Yellow'}
SPHERES_RULES = {'Back'}
SPHERES_SHIP_OBJECTIVE = {'Upgraded'}

GIMP_COMMAND = '"{}" -i -b "({} 1 \\"{}\\" \\"{}\\")" -b "(gimp-quit 0)"'
MAGICK_COMMAND_CMYK = '"{}" mogrify -profile USWebCoatedSWOP.icc "{}{}*.jpg"'
MAGICK_COMMAND_LOW = '"{}" mogrify -resize 600x600 -format jpg "{}{}*.png"'
MAGICK_COMMAND_MBPRINT_PDF = '"{}" convert "{}{}*o.jpg" "{}"'
MAGICK_COMMAND_RULES_PDF = '"{}" convert "{}{}*.png" "{}"'

JPG_PREVIEW_MIN_SIZE = 40000
JPG_300_MIN_SIZE = 100000
JPG_800_MIN_SIZE = 1000000
JPG_300CMYK_MIN_SIZE = 1000000
JPG_800CMYK_MIN_SIZE = 4000000
PNG_300_MIN_SIZE = 200000
PNG_800_MIN_SIZE = 2000000

EASY_PREFIX = 'Easy '
IMAGES_CUSTOM_FOLDER = 'custom'
OCTGN_SET_XML = 'set.xml'
PLAYTEST_SUFFIX = '-Playtest'
PROCESSED_ARTWORK_FOLDER = 'processed'
PROJECT_FOLDER = 'Frogmorton'
TEXT_CHUNK_FLAG = b'tEXt'

DECK_PREFIX_REGEX = r'^[QN][A-Z0-9][A-Z0-9]\.[0-9][0-9]?[\- ]'
UUID_REGEX = r'^[0-9a-h]{8}-[0-9a-h]{4}-[0-9a-h]{4}-[0-9a-h]{4}-[0-9a-h]{12}$'

JPG300BLEEDDTC = 'jpg300BleedDTC'
JPG800BLEEDMBPRINT = 'jpg800BleedMBPrint'
PNG300BLEED = 'png300Bleed'
PNG300DB = 'png300DB'
PNG300NOBLEED = 'png300NoBleed'
PNG300OCTGN = 'png300OCTGN'
PNG300PDF = 'png300PDF'
PNG300RULES = 'png300Rules'
PNG800BLEED = 'png800Bleed'
PNG800BLEEDMPC = 'png800BleedMPC'
PNG800BLEEDGENERIC = 'png800BleedGeneric'
PNG800NOBLEED = 'png800NoBleed'
PNG800PDF = 'png800PDF'

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
DISCORD_PATH = 'Discord'
DISCORD_CARD_DATA_PATH = os.path.join(DISCORD_PATH, 'card_data.json')
DOWNLOAD_PATH = 'Download'
IMAGES_BACK_PATH = 'imagesBack'
IMAGES_CUSTOM_PATH = os.path.join(PROJECT_FOLDER, 'imagesCustom')
IMAGES_ICONS_PATH = os.path.join(PROJECT_FOLDER, 'imagesIcons')
IMAGES_EONS_PATH = 'imagesEons'
IMAGES_OTHER_PATH = 'imagesOther'
IMAGES_RAW_PATH = os.path.join(PROJECT_FOLDER, 'imagesRaw')
IMAGES_TTS_PATH = 'imagesTTS'
IMAGES_ZIP_PATH = '{}/Export/'.format(os.path.split(PROJECT_FOLDER)[-1])
MAKECARDS_FINISHED_PATH = 'makeCards_FINISHED'
OCTGN_ZIP_PATH = 'a21af4e8-be4b-4cda-a6b6-534f9717391f/Sets'
OUTPUT_PATH = 'Output'
OUTPUT_DB_PATH = os.path.join(OUTPUT_PATH, 'DB')
OUTPUT_DRAGNCARDS_PATH = os.path.join(OUTPUT_PATH, 'DragnCards')
OUTPUT_DTC_PATH = os.path.join(OUTPUT_PATH, 'DriveThruCards')
OUTPUT_FRENCHDB_PATH = os.path.join(OUTPUT_PATH, 'FrenchDB')
OUTPUT_FRENCHDB_IMAGES_PATH = os.path.join(OUTPUT_PATH, 'FrenchDBImages')
OUTPUT_GENERICPNG_PATH = os.path.join(OUTPUT_PATH, 'GenericPNG')
OUTPUT_GENERICPNG_PDF_PATH = os.path.join(OUTPUT_PATH, 'GenericPNGPDF')
OUTPUT_HALLOFBEORN_PATH = os.path.join(OUTPUT_PATH, 'HallOfBeorn')
OUTPUT_MBPRINT_PATH = os.path.join(OUTPUT_PATH, 'MBPrint')
OUTPUT_MBPRINT_PDF_PATH = os.path.join(OUTPUT_PATH, 'MBPrintPDF')
OUTPUT_MPC_PATH = os.path.join(OUTPUT_PATH, 'MakePlayingCards')
OUTPUT_OCTGN_PATH = os.path.join(OUTPUT_PATH, 'OCTGN')
OUTPUT_OCTGN_DECKS_PATH = os.path.join(OUTPUT_PATH, 'OCTGNDecks')
OUTPUT_OCTGN_IMAGES_PATH = os.path.join(OUTPUT_PATH, 'OCTGNImages')
OUTPUT_PDF_PATH = os.path.join(OUTPUT_PATH, 'PDF')
OUTPUT_PREVIEW_IMAGES_PATH = os.path.join(OUTPUT_PATH, 'PreviewImages')
OUTPUT_RINGSDB_PATH = os.path.join(OUTPUT_PATH, 'RingsDB')
OUTPUT_RINGSDB_IMAGES_PATH = os.path.join(OUTPUT_PATH, 'RingsDBImages')
OUTPUT_RULES_PDF_PATH = os.path.join(OUTPUT_PATH, 'RulesPDF')
OUTPUT_SPANISHDB_PATH = os.path.join(OUTPUT_PATH, 'SpanishDB')
OUTPUT_SPANISHDB_IMAGES_PATH = os.path.join(OUTPUT_PATH, 'SpanishDBImages')
OUTPUT_TTS_PATH = os.path.join(OUTPUT_PATH, 'TTS')
PROJECT_PATH = 'setGenerator.seproject'
PROJECT_CREATED_PATH = 'setGenerator_CREATED'
RINGSDB_COOKIES_PATH = 'ringsdb_cookies.json'
RINGSDB_JSON_PATH = 'ringsdb.json'
RUN_BEFORE_SE_STARTED_PATH = 'runBeforeSE_STARTED'
SET_EONS_PATH = 'setEons'
SET_OCTGN_PATH = 'setOCTGN'
SHEETS_JSON_PATH = 'sheets.json'
TEMP_ROOT_PATH = 'Temp'
PIPELINE_STARTED_PATH = 'pipeline_STARTED'
URL_CACHE_PATH = 'urlCache'
XML_PATH = os.path.join(PROJECT_FOLDER, 'XML')
XML_ZIP_PATH = '{}/XML/'.format(os.path.split(PROJECT_FOLDER)[-1])

TTS_COLUMNS = 10
TTS_SHEET_SIZE = 69

LOG_LIMIT = 5000
URL_TIMEOUT = 15
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

CARD_TYPES_PLAYER_FRENCH = {'Ally', 'Attachment', 'Contract', 'Event', 'Hero',
                            'Player Side Quest', 'Treasure', 'Campaign',
                            'Objective Ally', 'Objective Hero',
                            'Ship Objective'}
CARD_TYPE_FRENCH_IDS = {
    'Ally': 401,
    'Attachment': 403,
    'Campaign': 411,
    'Contract': 418,
    'Enemy': 404,
    'Encounter Side Quest': 413,
    'Event': 402,
    'Hero': 400,
    'Location': 405,
    'Nightmare': 415,
    'Objective': 407,
    'Objective Ally': 409,
    'Objective Hero': 416,
    'Objective Location': 417,
    'Player Side Quest': 412,
    'Quest': 408,
    'Ship Enemy': 404,
    'Ship Objective': 414,
    'Treachery': 406,
    'Treasure': 410
}
CARD_SUBTYPE_FRENCH_IDS = {
    'Boon': 600,
    'Burden': 601
}
CARD_SPHERE_FRENCH_IDS = {
    'Baggins': 306,
    'Fellowship': 305,
    'Leadership': 300,
    'Lore': 301,
    'Neutral': 304,
    'Spirit': 302,
    'Tactics': 303
}
SPANISH = {
    'Ally': 'Aliado',
    'Attachment': 'Vinculada',
    'Campaign': 'Campa\u00f1a',
    'Contract': 'Contrato',
    'Encounter Side Quest': 'Misi\u00f3n Secundaria',
    'Enemy': 'Enemigo',
    'Event': 'Evento',
    'Hero': 'H\u00e9roe',
    'Location': 'Lugar',
    'Nightmare': 'Preparaci\u00f3n',
    'Objective': 'Objetivo',
    'Objective Ally': 'Objetivo-Aliado',
    'Objective Hero': 'H\u00e9roe-Objetivo',
    'Objective Location': 'Lugar-Objetivo',
    'Player Side Quest': 'Misi\u00f3n Secundaria',
    'Quest': 'Misi\u00f3n',
    'Setup': 'Preparaci\u00f3n',
    'Ship Enemy': 'Barco-Enemigo',
    'Ship Objective': 'Barco-Objetivo',
    'Treachery': 'Traici\u00f3n',
    'Treasure': 'Tesoro'
}

CARD_COLUMNS = {}
SHEET_IDS = {}
SETS = {}
DATA = []
TRANSLATIONS = {}
SELECTED_CARDS = set()
FOUND_SETS = set()
FOUND_SCRATCH_SETS = set()
FOUND_INTERSECTED_SETS = set()
IMAGE_CACHE = {}
JSON_CACHE = {}
XML_CACHE = {}
RINGSDB_COOKIES = {}


class SheetError(Exception):
    """ Google Sheet error.
    """


class SanityCheckError(Exception):
    """ Sanity check error.
    """


class GIMPError(Exception):
    """ GIMP error.
    """


class ImageMagickError(Exception):
    """ Image Magick error.
    """


class RingsDBError(Exception):
    """ RingsDB error.
    """


class TLSAdapter(requests.adapters.HTTPAdapter):
    """ TLS adapter to workaround SSL errors.
    """

    def init_poolmanager(self, connections, maxsize, block=False,
                         **pool_kwargs):
        """ Create and initialize the urllib3 PoolManager.
        """
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLS,
            ssl_context=ctx)


def _read_ringsdb_cookies(conf):
    """ Read RingsDB cookies (either from a local cache or from a file).
    """
    if RINGSDB_COOKIES:
        return RINGSDB_COOKIES

    data = {}
    try:
        with open(RINGSDB_COOKIES_PATH, 'r') as fobj:
            data = json.load(fobj)
    except Exception:  # pylint: disable=W0703
        pass

    if data:
        RINGSDB_COOKIES.update(data)
        return data

    if '|' in conf['ringsdb_sessionid']:
        parts = conf['ringsdb_sessionid'].split('|', 1)
        data = {'PHPSESSID': parts[0], 'REMEMBERME': parts[1]}
    else:
        data = {'PHPSESSID': conf['ringsdb_sessionid']}

    _write_ringsdb_cookies(data)
    return data


def _write_ringsdb_cookies(data):
    """ Write RingsDB cookies (to a local cache and to a file).
    """
    RINGSDB_COOKIES.clear()
    RINGSDB_COOKIES.update(data)
    with open(RINGSDB_COOKIES_PATH, 'w') as fobj:
        json.dump(data, fobj)


def normalized_name(value):
    """ Return a normalized card name.
    """
    value = unidecode.unidecode(str(value)).lower().replace(' ', '-')
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


def _to_str(value):
    """ Convert value to string if needed.
    """
    return '' if value is None else str(value)


def _update_card_text(text, lang='English', skip_rules=False,  # pylint: disable=R0915
                      fix_linebreaks=True):
    """ Update card text for RingsDB, Hall of Beorn and Spanish DB.
    """
    text = str(text)
    if lang == 'Spanish' and not skip_rules:
        text = re.sub(r'\b(Resoluci\u00f3n de la misi\u00f3n)( \([^\)]+\))?:',
                      '[b]\\1[/b]\\2:', text)
        text = re.sub(r'\b(Acci\u00f3n)( de Recursos| de Planificaci\u00f3n'
                      r'| de Misi\u00f3n| de Viaje| de Encuentro| de Combate'
                      r'| de Recuperaci\u00f3n)?( de Valor)?:',
                      '[b]\\1\\2\\3[/b]:', text)
        text = re.sub(r'\b(Al ser revelada|Obligado|Respuesta de Valor'
                      r'|Respuesta|Viaje|Sombra|Resoluci\u00f3n):',
                      '[b]\\1[/b]:', text)
        text = re.sub(r'\b(Preparaci\u00f3n)( \([^\)]+\))?:', '[b]\\1[/b]\\2:',
                      text)
        text = re.sub(r'\b(Condici\u00f3n)\b', '[bi]\\1[/bi]', text)
    if lang == 'French' and not skip_rules:
        text = re.sub(r'\b(R\u00e9solution de la qu\u00eate)( \([^\)]+\))? ?:',
                      '[b]\\1[/b]\\2 :', text)
        text = re.sub(r'(\[Vaillance\] )?(\[Ressource\] |\[Organisation\] '
                      r'|\[Qu\u00eate\] |\[Voyage\] |\[Rencontre\] '
                      r'|\[Combat\] |\[Restauration\] )?\b(Action) ?:',
                      '[b]\\1\\2\\3[/b] :', text)
        text = re.sub(r'\b(Une fois r\u00e9v\u00e9l\u00e9e|Forc\u00e9'
                      r'|\[Vaillance\] R\u00e9ponse|R\u00e9ponse|Trajet'
                      r'|Ombre|R\u00e9solution) ?:', '[b]\\1[/b] :', text)
        text = re.sub(r'\b(Mise en place)( \([^\)]+\))? ?:', '[b]\\1[/b]\\2 :',
                      text)
        text = re.sub(r'\b(Condition)\b', '[bi]\\1[/bi]', text)
    elif lang == 'English' and not skip_rules:
        text = re.sub(r'\b(Quest Resolution)( \([^\)]+\))?:', '[b]\\1[/b]\\2:',
                      text)
        text = re.sub(r'\b(Valour )?(Resource |Planning |Quest |Travel '
                      r'|Encounter |Combat |Refresh )?(Action):',
                      '[b]\\1\\2\\3[/b]:', text)
        text = re.sub(r'\b(When Revealed|Forced|Valour Response|Response'
                      r'|Travel|Shadow|Resolution):', '[b]\\1[/b]:', text)
        text = re.sub(r'\b(Setup)( \([^\)]+\))?:', '[b]\\1[/b]\\2:', text)
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
    text = re.sub(r'\[lotrheader [^\]]+\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/lotrheader\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[size [^\]]+\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[\/size\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[defaultsize [^\]]+\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[img [^\]]+\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[space\]', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\[vspace\]', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\[tab\]', '    ', text, flags=re.IGNORECASE)
    text = re.sub(r'\[nobr\]', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\[inline\]\n', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\[inline\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[lsb\]', '[', text, flags=re.IGNORECASE)
    text = re.sub(r'\[rsb\]', ']', text, flags=re.IGNORECASE)

    text = text.strip()
    text = re.sub(r' +(?=\n)', '', text)
    text = re.sub(r' +', ' ', text)

    if fix_linebreaks:
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

    text = re.sub(r'\n+', '\n', text)
    return text


def _update_octgn_card_text(text, fix_linebreaks=True):
    """ Update card text for OCTGN.
    """
    text = _update_card_text(text, fix_linebreaks=fix_linebreaks)
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


def _update_dragncards_card_text(text, fix_linebreaks=True):
    """ Update card text for DragnCards.
    """
    text = _update_card_text(text, fix_linebreaks=fix_linebreaks)
    text = re.sub(r'(?:<b>|<\/b>|<i>|<\/i>)', '', text, flags=re.IGNORECASE)
    return text


def _get_french_icon(name):
    """ Get the icon for the French database.
    """
    return ('<img src="https://sda-src.cgbuilder.fr/images/carte_{}.png" '  # pylint: disable=W1308
            'alt="{}" />'.format(name, name))


def _update_french_card_text(text):
    """ Update card text for French database.
    """
    text = _update_card_text(text, lang='French')
    text = text.replace('\n', '<br>')

    text = text.replace('[willpower]', _get_french_icon('volonte'))
    text = text.replace('[threat]', _get_french_icon('menace'))
    text = text.replace('[attack]', _get_french_icon('attaque'))
    text = text.replace('[defense]', _get_french_icon('defense'))
    text = text.replace('[leadership]', _get_french_icon('commandement'))
    text = text.replace('[spirit]', _get_french_icon('energie'))
    text = text.replace('[tactics]', _get_french_icon('tactique'))
    text = text.replace('[lore]', _get_french_icon('connaissance'))
    text = text.replace('[baggins]', _get_french_icon('sacquet'))
    text = text.replace('[fellowship]', _get_french_icon('communaute'))
    text = text.replace('[unique]', _get_french_icon('unique'))
    text = text.replace('[sunny]', _get_french_icon('soleil'))
    text = text.replace('[cloudy]', _get_french_icon('nuage'))
    text = text.replace('[rainy]', _get_french_icon('pluie'))
    text = text.replace('[stormy]', _get_french_icon('orage'))
    text = text.replace('[sailing]', _get_french_icon('gouvernail'))
    text = text.replace('[eos]', _get_french_icon('oeil'))
    text = text.replace('[pp]', _get_french_icon('parjoueur'))
    return text


def _update_french_non_int(value):
    """ Update non-int values like "X" or "-".
    """
    if value == 'X':
        return 99

    if value == '-':
        return -1

    return value


def escape_filename(value):
    """ Escape forbidden symbols in a file name.
    """
    value = re.sub(r'[<>:\/\\|?*\'"’“”„«»…–—]', ' ', str(value))
    value = value.encode('ascii', errors='replace').decode().replace('?', ' ')
    return value


def escape_octgn_filename(value):
    """ Replace spaces in a file name for OCTGN.
    """
    return value.replace(' ', '-')


def extract_keywords(value):
    """ Extract all keywords from the string.
    """
    keywords = [k.strip() for k in str(value or '').replace(
                '[inline]', '').split('.') if k != '']
    keywords = [re.sub(r' ([0-9]+)\[pp\]$', ' \\1 Per Player', k, re.I)
                for k in keywords]
    keywords = [k for k in keywords if re.match(
                r'^([a-z\u00c0-\u017e]+ )?[a-z\u00c0-\u017e]+'
                r'(?: -?[0-9X]+(?: Per Player)?)?(?: \([^\)]+\))?$',
                k, re.I)]
    return keywords


def clear_folder(folder):
    """ Clear the folder.
    """
    if not os.path.exists(folder):
        return

    for _, _, filenames in os.walk(folder):
        for filename in filenames:
            if filename not in ('seproject', '.gitignore'):
                os.remove(os.path.join(folder, filename))

        break


def create_folder(folder):
    """ Create the folder if needed.
    """
    if not os.path.exists(folder):
        os.mkdir(folder)


def delete_folder(folder):
    """ Delete the folder.
    """
    if os.path.exists(folder):
        shutil.rmtree(folder, ignore_errors=True)


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


def read_conf(path=CONFIGURATION_PATH):  # pylint: disable=R0912
    """ Read project configuration.
    """
    logging.info('Reading project configuration (%s)...', path)
    timestamp = time.time()

    with open(path, 'r') as f_conf:
        conf = yaml.safe_load(f_conf)

    conf['all_languages'] = list(conf['outputs'].keys())
    conf['languages'] = [lang for lang in conf['outputs']
                         if conf['outputs'][lang]]
    if conf['frenchdb_csv'] and 'French' not in conf['languages']:
        conf['languages'].append('French')

    if conf['spanishdb_csv'] and 'Spanish' not in conf['languages']:
        conf['languages'].append('Spanish')

    conf['output_languages'] = [lang for lang in conf['outputs']
                                if conf['outputs'][lang]]
    conf['nobleed_300'] = {}
    conf['nobleed_800'] = {}  # not used at the moment

    if not conf['set_ids']:
        conf['set_ids'] = []

    if not conf['ignore_set_ids']:
        conf['ignore_set_ids'] = []

    if not conf['set_ids_octgn_image_destination']:
        conf['set_ids_octgn_image_destination'] = []

    for lang in conf['output_languages']:
        conf['outputs'][lang] = set(conf['outputs'][lang])

        if ('pdf_a4' in conf['outputs'][lang]
                or 'pdf_letter' in conf['outputs'][lang]):
            conf['outputs'][lang].add('pdf')

        if ('genericpng_pdf_a4_7z' in conf['outputs'][lang]
                or 'genericpng_pdf_letter_7z' in conf['outputs'][lang]
                or 'genericpng_pdf_a4_zip' in conf['outputs'][lang]
                or 'genericpng_pdf_letter_zip' in conf['outputs'][lang]):
            conf['outputs'][lang].add('genericpng_pdf')

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

        if ('tts' in conf['outputs'][lang]
                and 'db' not in conf['outputs'][lang]):
            conf['outputs'][lang].add('db')

        if 'tts' in conf['outputs'][lang] and not conf['octgn_o8d']:
            conf['octgn_o8d'] = True

        conf['nobleed_300'][lang] = ('db' in conf['outputs'][lang]
                                     or 'octgn' in conf['outputs'][lang]
                                     or 'rules_pdf' in conf['outputs'][lang])

        conf['nobleed_800'][lang] = False

    logging.info('...Reading project configuration (%ss)',
                 round(time.time() - timestamp, 3))
    return conf


def reset_project_folders(conf):
    """ Reset the project folders.
    """
    logging.info('Resetting the project folders...')
    timestamp = time.time()

    clear_folder(IMAGES_CUSTOM_PATH)
    clear_folder(IMAGES_ICONS_PATH)
    clear_folder(IMAGES_RAW_PATH)
    clear_folder(XML_PATH)

    nobleed_folder = os.path.join(IMAGES_EONS_PATH, PNG300NOBLEED)
    for _, subfolders, _ in os.walk(nobleed_folder):
        for subfolder in subfolders:
            delete_folder(os.path.join(nobleed_folder, subfolder))

        break

    nobleed_folder = os.path.join(IMAGES_EONS_PATH, PNG800NOBLEED)
    for _, subfolders, _ in os.walk(nobleed_folder):
        for subfolder in subfolders:
            delete_folder(os.path.join(nobleed_folder, subfolder))

        break

    input_path = os.path.join(conf['artwork_path'], 'icons')
    if os.path.exists(input_path):
        for _, _, filenames in os.walk(input_path):
            for filename in filenames:
                if filename.split('.')[-1] != 'png':
                    continue

                shutil.copyfile(os.path.join(input_path, filename),
                                os.path.join(IMAGES_ICONS_PATH, filename))

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


def _fix_csv_value(value):
    """ Extract a single value.
    """
    if value == '':
        return None

    if value == 'FALSE':
        return None

    if _is_int(value):
        return int(value)

    return value


def download_sheet(conf):  # pylint: disable=R0912,R0914,R0915
    """ Download cards spreadsheet from Google Sheets.
    """
    logging.info('Downloading cards spreadsheet from Google Sheets...')
    timestamp = time.time()

    changes = False
    scratch_changes = False
    sheets = [SET_SHEET, CARD_SHEET, SCRATCH_SHEET]
    for lang in set(conf['languages']).difference(set(['English'])):
        sheets.append(lang)

    if [sheet for sheet in sheets if sheet not in SHEET_IDS]:
        logging.info('Obtaining sheet IDs')
        SHEET_IDS.clear()
        url = (
            'https://docs.google.com/spreadsheets/d/{}/export?format=csv'
            .format(conf['sheet_gdid']))
        res = _get_content(url).decode('utf-8')
        if not res or '<html' in res:
            raise SheetError("Can't download the Google Sheet")

        try:
            SHEET_IDS.update(dict(row for row in
                                  csv.reader(res.splitlines())))
        except ValueError:
            raise SheetError("Can't download the Google Sheet")

        missing_sheets = [sheet for sheet in sheets
                          if sheet not in SHEET_IDS]
        if missing_sheets:
            SheetError("Can't find sheet ID(s) for the following "
                       "sheet(s): {}".format(', '.join(missing_sheets)))

    try:
        with open(SHEETS_JSON_PATH, 'r') as fobj:
            old_checksums = json.load(fobj)
    except Exception:  # pylint: disable=W0703
        old_checksums = {}

    new_checksums = {}
    for sheet in sheets:
        url = (
            'https://docs.google.com/spreadsheets/d/{}/export?format=csv&gid={}'
            .format(conf['sheet_gdid'], SHEET_IDS[sheet]))
        res = _get_content(url).decode('utf-8')
        if not res or '<html' in res:
            raise SheetError("Can't download {} from the Google Sheet"
                             .format(sheet))

        try:
            data = list(csv.reader(StringIO(res)))
        except Exception:  # pylint: disable=W0703
            raise SheetError("Can't download {} from the Google Sheet"
                             .format(sheet))

        none_index = data[0].index('')
        data = [row[:none_index] for row in data]
        data = [[_fix_csv_value(v) for v in row] for row in data]
        while not any(data[-1]):
            data.pop()

        JSON_CACHE[sheet] = data
        res = json.dumps(data)
        new_checksums[sheet] = hashlib.md5(res.encode('utf-8')).hexdigest()
        if new_checksums[sheet] != old_checksums.get(sheet, ''):
            logging.info('Sheet %s changed', sheet)
            if sheet != SCRATCH_SHEET:
                changes = True

            if sheet in (SET_SHEET, SCRATCH_SHEET):
                scratch_changes = True

            path = os.path.join(DOWNLOAD_PATH, '{}.json'.format(sheet))
            with open(path, 'w') as fobj:
                fobj.write(res)

    if changes or scratch_changes:
        with open(SHEETS_JSON_PATH, 'w') as fobj:
            json.dump(new_checksums, fobj)

    logging.info('...Downloading cards spreadsheet from Google Sheets (%ss)',
                 round(time.time() - timestamp, 3))
    return (changes, scratch_changes)


def _update_discord_category(category):
    """ Update the name of a Discord category.
    """
    category = re.sub(r'[“”]', '"', category)
    category = re.sub(r'’', "'", category)
    category = re.sub(r'…', '', category)
    category = re.sub(r'[–—]', '-', category)
    return category


def _clean_value(value):  # pylint: disable=R0915
    """ Clean a value from the spreadsheet.
    """
    value = str(value).strip()
    value = value.replace('`', "'")
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
        value = re.sub(r'…([^\[]*)\]', "...\\1]", value)
        value = re.sub(r'—([^\[]*)\]', "---\\1]", value)
        value = re.sub(r'–([^\[]*)\]', "--\\1]", value)
        if value == value_old:
            break

    value = re.sub(r'\[unique\]', '[unique]', value, flags=re.IGNORECASE)
    value = re.sub(r'\[threat\]', '[threat]', value, flags=re.IGNORECASE)
    value = re.sub(r'\[attack\]', '[attack]', value, flags=re.IGNORECASE)
    value = re.sub(r'\[defense\]', '[defense]', value, flags=re.IGNORECASE)
    value = re.sub(r'\[willpower\]', '[willpower]', value, flags=re.IGNORECASE)
    value = re.sub(r'\[leadership\]', '[leadership]', value,
                   flags=re.IGNORECASE)
    value = re.sub(r'\[lore\]', '[lore]', value, flags=re.IGNORECASE)
    value = re.sub(r'\[spirit\]', '[spirit]', value, flags=re.IGNORECASE)
    value = re.sub(r'\[tactics\]', '[tactics]', value, flags=re.IGNORECASE)
    value = re.sub(r'\[baggins\]', '[baggins]', value, flags=re.IGNORECASE)
    value = re.sub(r'\[fellowship\]', '[fellowship]', value,
                   flags=re.IGNORECASE)
    value = re.sub(r'\[sunny\]', '[sunny]', value, flags=re.IGNORECASE)
    value = re.sub(r'\[cloudy\]', '[cloudy]', value, flags=re.IGNORECASE)
    value = re.sub(r'\[rainy\]', '[rainy]', value, flags=re.IGNORECASE)
    value = re.sub(r'\[stormy\]', '[stormy]', value, flags=re.IGNORECASE)
    value = re.sub(r'\[sailing\]', '[sailing]', value, flags=re.IGNORECASE)
    value = re.sub(r'\[eos\]', '[eos]', value, flags=re.IGNORECASE)
    value = re.sub(r'\[pp\]', '[pp]', value, flags=re.IGNORECASE)

    value = re.sub(r' +(?=\n)', '', value)
    value = re.sub(r' +', ' ', value)

    if len(value) == 1:
        value = value.upper()

    return value


def _clean_data(data):
    """ Clean data from the spreadsheet.
    """
    for row in data:
        card_name = str(row.get(CARD_NAME) or '').strip()
        card_name_back = str(row.get(CARD_SIDE_B) or '').strip()
        for key, value in row.items():
            if isinstance(value, str):
                if key.startswith(BACK_PREFIX):
                    value = value.replace('[name]', card_name_back)
                else:
                    value = value.replace('[name]', card_name)

                value = _clean_value(value)
                row[key] = value


def _clean_sets(data):
    """ Clean sets data from the spreadsheet.
    """
    for row in data:
        for key, value in row.items():
            if isinstance(value, str):
                value = _clean_value(value)
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
        if not [v for v in row if v and v != '#REF!']:
            continue

        row_dict = {}
        row_dict[ROW_COLUMN] = i + 2
        for name, column in columns.items():
            if name == MAX_COLUMN:
                continue

            row_dict[name] = row[column]

        res.append(row_dict)

    return res


def _read_sheet_json(sheet):
    """ Read sheet data from a JSON file.
    """
    data = JSON_CACHE.get(sheet)
    if data:
        return data

    path = os.path.join(DOWNLOAD_PATH, '{}.json'.format(sheet))
    if not os.path.exists(path):
        return []

    with open(path, 'r') as fobj:
        data = json.load(fobj)

    JSON_CACHE[sheet] = data
    return data


def extract_data(conf, sheet_changes=True, scratch_changes=True):  # pylint: disable=R0912,R0915
    """ Extract data from the spreadsheet.
    """
    logging.info('Extracting data from the spreadsheet...')
    timestamp = time.time()

    CARD_COLUMNS.clear()
    SETS.clear()
    FOUND_SETS.clear()
    FOUND_SCRATCH_SETS.clear()
    FOUND_INTERSECTED_SETS.clear()
    DATA[:] = []
    TRANSLATIONS.clear()
    SELECTED_CARDS.clear()

    data = _read_sheet_json(SET_SHEET)
    if data:
        data = _transform_to_dict(data)
        _clean_sets(data)
        SETS.update({s[SET_ID]: s for s in data})

    if sheet_changes:
        data = _read_sheet_json(CARD_SHEET)
        if data:
            CARD_COLUMNS.update(_extract_column_names(data[0]))
            data = _transform_to_dict(data)
            for row in data:
                row[CARD_SCRATCH] = None

            DATA.extend(data)

    if scratch_changes:
        data = _read_sheet_json(SCRATCH_SHEET)
        if data:
            if not CARD_COLUMNS:
                CARD_COLUMNS.update(_extract_column_names(data[0]))

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
        data = _read_sheet_json(lang)
        if data:
            data = _transform_to_dict(data)
            for row in data:
                row[CARD_SCRATCH] = None

            _clean_data(data)
            _update_data(data)
            for row in data:
                if row[CARD_ID] in TRANSLATIONS[lang]:
                    logging.error(
                        'Duplicate card ID %s for row #%s in %s translations, '
                        'ignoring', row[CARD_ID], row[ROW_COLUMN], lang)
                else:
                    TRANSLATIONS[lang][row[CARD_ID]] = row

    logging.info('...Extracting data from the spreadsheet (%ss)',
                 round(time.time() - timestamp, 3))


def get_sets(conf, sheet_changes=True, scratch_changes=True):
    """ Get all sets to work on and return list of (set id, set name) tuples.
    """
    logging.info('Getting all sets to work on...')
    timestamp = time.time()

    chosen_sets = set()
    for row in SETS.values():
        if (row[SET_ID] in conf['set_ids'] and
                ((row[SET_ID] in FOUND_SETS and sheet_changes) or
                 (row[SET_ID] in FOUND_SCRATCH_SETS and scratch_changes))):
            chosen_sets.add(row[SET_ID])

    if 'all' in conf['set_ids'] and sheet_changes:
        chosen_sets.update(s for s in FOUND_SETS if s in SETS)

    if 'all_scratch' in conf['set_ids'] and scratch_changes:
        chosen_sets.update(s for s in FOUND_SCRATCH_SETS if s in SETS)

    chosen_sets = list(chosen_sets)
    chosen_sets = [s for s in chosen_sets if s not in conf['ignore_set_ids']]
    chosen_sets = [[SETS[s][SET_ID], SETS[s][SET_NAME]] for s in chosen_sets]
    logging.info('...Getting all sets to work on (%ss)',
                 round(time.time() - timestamp, 3))
    return chosen_sets


def sanity_check(conf, sets):  # pylint: disable=R0912,R0914,R0915
    """ Perform a sanity check of the spreadsheet and return "healthy" sets.
    """
    logging.info('Performing a sanity check of the spreadsheet...')
    logging.info('')
    timestamp = time.time()

    errors = []
    card_ids = set()
    card_scratch_ids = set()
    card_set_numbers = set()
    set_ids = {s[0] for s in sets}
    all_set_ids = set(SETS.keys())
    broken_set_ids = set()
    deck_rules = set()
    card_data = DATA[:]
    card_data = sorted(card_data, key=lambda row: (row[CARD_SCRATCH] or 0,
                                                   row[ROW_COLUMN]))

    for row in card_data:  # pylint: disable=R1702
        i = row[ROW_COLUMN]
        set_id = row[CARD_SET]
        card_id = row[CARD_ID]
        card_number = row[CARD_NUMBER]
        card_quantity = row[CARD_QUANTITY]
        card_encounter_set = row[CARD_ENCOUNTER_SET]
        card_name = row[CARD_NAME]
        card_unique = row[CARD_UNIQUE]
        card_type = row[CARD_TYPE]
        card_sphere = row[CARD_SPHERE]
        card_traits = row[CARD_TRAITS]
        card_keywords = row[CARD_KEYWORDS]
        card_victory = row[CARD_VICTORY]
        card_name_back = row[BACK_PREFIX + CARD_NAME]
        card_unique_back = row[BACK_PREFIX + CARD_UNIQUE]
        card_type_back = row[BACK_PREFIX + CARD_TYPE]
        card_sphere_back = row[BACK_PREFIX + CARD_SPHERE]
        card_traits_back = row[BACK_PREFIX + CARD_TRAITS]
        card_keywords_back = row[BACK_PREFIX + CARD_KEYWORDS]
        card_victory_back = row[BACK_PREFIX + CARD_VICTORY]
        card_easy_mode = row[CARD_EASY_MODE]
        card_adventure = row[CARD_ADVENTURE]
        card_back = row[CARD_BACK]
        card_deck_rules = row[CARD_DECK_RULES]
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
            else:
                broken_set_ids.add(set_id)
        elif card_id in card_ids or card_id in card_scratch_ids:
            message = 'Duplicate card ID for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif not re.match(UUID_REGEX, card_id):
            message = 'Incorrect card ID format for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

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
            else:
                broken_set_ids.add(set_id)
        elif len(_handle_int_str(card_number)) > 3:
            message = 'Card number is too long for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if set_id is not None and card_number is not None:
            if (set_id, card_number) in card_set_numbers:
                message = ('Duplicate card set and card number combination '
                           'for row #{}{}'.format(i, scratch))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            else:
                card_set_numbers.add((set_id, card_number))

        if card_quantity is None:
            message = 'No card quantity for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif not is_positive_int(card_quantity):
            message = ('Incorrect format for card quantity for row '
                       '#{}{}'.format(i, scratch))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif ((card_type in CARD_TYPES_ONE_COPY or card_sphere == 'Boon') and
              card_quantity != 1):
            message = ('Incorrect card quantity for row #{}{}'.format(
                i, scratch))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type in CARD_TYPES_THREE_COPIES and
              card_quantity not in (1, 3)):
            message = ('Incorrect card quantity for row #{}{}'.format(
                i, scratch))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_name is None:
            message = 'No card name for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_encounter_set is None and
                card_type in CARD_TYPES_ENCOUNTER_SET):
            message = 'No encounter set for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_encounter_set is not None and
              card_type in CARD_TYPES_NO_ENCOUNTER_SET):
            message = 'Redundant encounter set for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_unique is not None and card_unique not in ('1', 1):
            message = 'Incorrect format for unique for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if ((card_unique is None and card_type in CARD_TYPES_UNIQUE) or
                (card_unique in ('1', 1) and
                 card_type in CARD_TYPES_NON_UNIQUE)):
            message = 'Incorrect unique value for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_unique_back is not None and card_unique_back not in ('1', 1):
            message = 'Incorrect format for unique back for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if ((card_unique_back is None and
             card_type_back in CARD_TYPES_UNIQUE) or
                (card_unique_back in ('1', 1) and
                 card_type_back in CARD_TYPES_NON_UNIQUE)):
            message = 'Incorrect unique back value for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_type is None:
            message = 'No card type for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_type not in CARD_TYPES:
            message = 'Unknown card type for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_type_back is not None and card_type_back not in CARD_TYPES:
            message = 'Unknown card type back for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type in CARD_TYPES_DOUBLESIDE_OPTIONAL
              and card_type_back is not None and card_type_back != card_type):
            message = 'Incorrect card type back for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type not in CARD_TYPES_DOUBLESIDE_OPTIONAL
              and card_type_back in CARD_TYPES_DOUBLESIDE_OPTIONAL):
            message = 'Incorrect card type back for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_type == 'Campaign':
            spheres = SPHERES_CAMPAIGN
        elif card_type == 'Rules':
            spheres = SPHERES_RULES
        elif card_type == 'Presentation':
            spheres = SPHERES_PRESENTATION
        elif card_type == 'Ship Objective':
            spheres = SPHERES_SHIP_OBJECTIVE
        elif card_type in CARD_TYPES_PLAYER_SPHERE:
            spheres = SPHERES_PLAYER
        else:
            spheres = SPHERES

        if card_type in CARD_TYPES_BOON:
            spheres.add('Boon')

        if card_type in CARD_TYPES_BURDEN:
            spheres.add('Burden')

        if card_type in CARD_TYPES_NIGHTMARE:
            spheres.add('Nightmare')

        if (card_sphere is None and
                (card_type in CARD_TYPES_PLAYER_SPHERE or
                 card_type == 'Presentation')):
            message = 'Missing sphere for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_sphere is not None and card_sphere not in spheres:
            message = 'Unknown sphere for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_type not in CARD_TYPES_DOUBLESIDE_OPTIONAL:
            if card_type_back == 'Ship Objective':
                spheres_back = SPHERES_SHIP_OBJECTIVE
            elif card_type_back in CARD_TYPES_PLAYER_SPHERE:
                spheres_back = SPHERES_PLAYER
            else:
                spheres_back = SPHERES

            if card_type_back in CARD_TYPES_BOON:
                spheres_back.add('Boon')

            if card_type_back in CARD_TYPES_BURDEN:
                spheres_back.add('Burden')

            if card_type_back in CARD_TYPES_NIGHTMARE:
                spheres_back.add('Nightmare')

            if (card_sphere_back is None and
                    card_type_back in CARD_TYPES_PLAYER_SPHERE):
                message = 'Missing sphere back for row #{}{}'.format(i, scratch)
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            elif (card_sphere_back is not None and
                  card_sphere_back not in spheres_back):
                message = 'Unknown sphere back for row #{}{}'.format(
                    i, scratch)
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

        if card_traits is None and card_type in CARD_TYPES_TRAITS:
            message = 'No traits for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_traits is not None and card_type in CARD_TYPES_NO_TRAITS:
            message = 'Redundant traits for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_traits is not None and not card_traits.endswith('.'):
            message = 'Missing period in traits for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_traits_back is None and card_type_back in CARD_TYPES_TRAITS:
            message = 'No traits back for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_traits_back is not None and
              card_type_back in CARD_TYPES_NO_TRAITS):
            message = 'Redundant traits back for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_traits_back is not None and not card_traits_back.endswith('.'):
            message = 'Missing period in traits back for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_keywords is not None and card_type in CARD_TYPES_NO_KEYWORDS:
            message = 'Redundant keywords for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_keywords is not None and not
                (card_keywords.endswith('.') or
                 card_keywords.endswith('.[inline]'))):
            message = 'Missing period in keywords for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_keywords_back is not None and
                card_type_back in CARD_TYPES_NO_KEYWORDS):
            message = 'Redundant keywords back for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_keywords_back is not None and not
                (card_keywords_back.endswith('.') or
                 card_keywords_back.endswith('.[inline]'))):
            message = 'Missing period in keywords back for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_victory is not None and card_type in ('Presentation', 'Rules'):
            if len(str(card_victory).split('/')) != 2:
                message = ('Incorrect format for card victory for row '
                           '#{}{}'.format(i, scratch))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            elif not (is_positive_int(str(card_victory).split('/')[0]) and
                      is_positive_int(str(card_victory).split('/')[1])):
                message = ('Incorrect format for card victory for row '
                           '#{}{}'.format(i, scratch))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

        if (card_victory_back is not None and
                card_type_back in ('Presentation', 'Rules')):
            if len(str(card_victory_back).split('/')) != 2:
                message = ('Incorrect format for card victory back for row '
                           '#{}{}'.format(i, scratch))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            elif not (is_positive_int(str(card_victory_back).split('/')[0]) and
                      is_positive_int(str(card_victory_back).split('/')[1])):
                message = ('Incorrect format for card victory back for row '
                           '#{}{}'.format(i, scratch))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

        if card_easy_mode is not None and not is_positive_int(card_easy_mode):
            message = ('Incorrect format for removed for easy mode for row '
                       '#{}{}'.format(i, scratch))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_easy_mode is not None and card_easy_mode > card_quantity:
            message = ('Removed for easy mode is greater than card quantity '
                       'for row #{}{}'.format(i, scratch))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_back is not None and
                (card_type in CARD_TYPES_DOUBLESIDE_MANDATORY or
                 card_name_back is not None)):
            message = 'Redundant custom card back value for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_back not in (None, 'Encounter', 'Player'):
            message = 'Incorrect custom card back value for row #{}{}'.format(
                i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        for key, value in row.items():
            if isinstance(value, str) and '[unmatched quot]' in value:
                message = ('Unmatched quote symbol in {} column for row '
                           '#{}{}'.format(key, i, scratch))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            elif value == '#REF!':
                message = ('Reference error in {} column for row '
                           '#{}{}'.format(key, i, scratch))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

        if (card_deck_rules is not None and
                card_type not in CARD_TYPES_DECK_RULES):
            message = 'Redundant deck rules for row #{}{}'.format(i, scratch)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_deck_rules is not None and
              ((card_type == 'Quest' and card_adventure) or
               card_type == 'Nightmare')):
            quest_id = (set_id, card_adventure or card_name)
            if quest_id in deck_rules:
                message = (
                    'Duplicate deck rules for quest {} in row #{}{}'.format(
                        card_adventure or card_name, i, scratch))
                logging.error(message)
                if conf['octgn_o8d']:
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)
            else:
                deck_rules.add(quest_id)

            prefixes = set()
            for part in str(card_deck_rules).split('\n\n'):
                if not part:
                    continue

                rules_list = [r.strip().split(':', 1)
                              for r in part.split('\n')]
                rules_list = [(r[0].lower().strip(),
                               [j.strip()
                                for j in r[1].strip().split(';')])
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
                                key, card_adventure or card_name, i, scratch))
                        logging.error(message)
                        if conf['octgn_o8d']:
                            if not card_scratch:
                                errors.append(message)
                            else:
                                broken_set_ids.add(set_id)

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
                                key, card_adventure or card_name, i, scratch))
                        logging.error(message)
                        if conf['octgn_o8d']:
                            if not card_scratch:
                                errors.append(message)
                            else:
                                broken_set_ids.add(set_id)

                prefix = rules.get(('prefix', 0), [''])[0]
                if not prefix:
                    message = (
                        'No prefix for deck rules for quest {} in row #{}{}'
                        .format(card_adventure or card_name, i, scratch))
                    logging.error(message)
                    if conf['octgn_o8d']:
                        if not card_scratch:
                            errors.append(message)
                        else:
                            broken_set_ids.add(set_id)
                elif not re.match(DECK_PREFIX_REGEX, prefix + ' '):
                    message = (
                        'Incorrect prefix "{}" for deck rules for quest {} '
                        'in row #{}{}'.format(
                            prefix, card_adventure or card_name, i, scratch))
                    logging.error(message)
                    if conf['octgn_o8d']:
                        if not card_scratch:
                            errors.append(message)
                        else:
                            broken_set_ids.add(set_id)
                elif prefix in prefixes:
                    message = (
                        'Duplicate prefix "{}" for deck rules for quest {} '
                        'in row #{}{}'.format(
                            prefix, card_adventure or card_name, i, scratch))
                    logging.error(message)
                    if conf['octgn_o8d']:
                        if not card_scratch:
                            errors.append(message)
                        else:
                            broken_set_ids.add(set_id)
                else:
                    prefixes.add(prefix)

        for lang in conf['languages']:
            if lang == 'English':
                continue

            if not TRANSLATIONS[lang].get(card_id):
                logging.error(
                    'No card ID %s in %s translations', card_id, lang)
                continue

            if card_type != TRANSLATIONS[lang][card_id].get(CARD_TYPE):
                logging.error(
                    'Incorrect card type for card '
                    'ID %s in %s translations, row #%s', card_id,
                    lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

            if (card_type_back !=
                    TRANSLATIONS[lang][card_id].get(BACK_PREFIX + CARD_TYPE)):
                logging.error(
                    'Incorrect card type back for card '
                    'ID %s in %s translations, row #%s', card_id,
                    lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

            for key, value in TRANSLATIONS[lang][card_id].items():
                if key not in TRANSLATED_COLUMNS:
                    continue

                if isinstance(value, str) and '[unmatched quot]' in value:
                    logging.error(
                        'Unmatched quote symbol in %s column for card '
                        'ID %s in %s translations, row #%s', key, card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

                if not value and row.get(key):
                    logging.error(
                        'Missing value for %s column for card '
                        'ID %s in %s translations, row #%s', key, card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])
                elif value and not row.get(key):
                    logging.error(
                        'Redundant value for %s column for card '
                        'ID %s in %s translations, row #%s', key, card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

    logging.info('')
    if errors:
        raise SanityCheckError('Sanity check failed: {}.'.format(
            '. '.join(errors)))

    sets = [s for s in sets if s[0] not in broken_set_ids]
    logging.info('...Performing a sanity check of the spreadsheet (%ss)',
                 round(time.time() - timestamp, 3))
    return sets


def _has_discord_channel(card):
    """ Check whether a card has Discord channel or not.
    """
    if (card[CARD_NAME] == 'T.B.D.'
            or card[CARD_TYPE] in ('Rules', 'Presentation')):
        return False

    return True


def _increment_channel_name(channel):
    """ Increment a channel's name.
    """
    if re.search(r'-[0-9]+$', channel):
        parts = channel.split('-')
        channel = '{}-{}'.format('-'.join(parts[:-1]), int(parts[-1]) + 1)
    else:
        channel = '{}-2'.format(channel)

    return channel


def _get_card_diffs(old_card, new_card):
    """ Find differences between two card versions.
    """
    diffs = []
    old_card = old_card.copy()
    new_card = new_card.copy()
    for key in old_card:
        if (key in DISCORD_IGNORE_CHANGES_COLUMNS or
                key in DISCORD_IGNORE_COLUMNS):
            continue

        if key not in new_card:
            diffs.append((key, old_card[key], None))
        elif old_card[key] != new_card[key]:
            diffs.append((key, old_card[key], new_card[key]))

    for key in new_card:
        if (key not in DISCORD_IGNORE_CHANGES_COLUMNS and
                key not in DISCORD_IGNORE_COLUMNS and key not in old_card):
            diffs.append((key, None, new_card[key]))

    diffs.sort(key=lambda d:
               CARD_COLUMNS.get(CARD_SIDE_B
                                if d[0] == BACK_PREFIX + CARD_NAME
                                else d[0], 0))
    return diffs


def save_data_for_bot(conf):  # pylint: disable=R0912,R0914,R0915
    """ Save the data for the Discord bot.
    """
    logging.info('Saving the data for the Discord bot...')
    timestamp = time.time()

    url = (
        'https://docs.google.com/spreadsheets/d/{}/edit#gid={}'
        .format(conf['sheet_gdid'], SHEET_IDS[CARD_SHEET]))
    data = [{key: value for key, value in row.items() if value is not None}
            for row in DATA if not row[CARD_SCRATCH]]
    channels = set()

    for row in data:
        row[CARD_NORMALIZED_NAME] = normalized_name(row[CARD_NAME])
        if row.get(BACK_PREFIX + CARD_NAME):
            row[BACK_PREFIX + CARD_NORMALIZED_NAME] = normalized_name(
                row[BACK_PREFIX + CARD_NAME])

        if _needed_for_ringsdb(row):
            row[CARD_RINGSDB_CODE] = _ringsdb_code(row)

        if _has_discord_channel(row):
            channel = row[CARD_NORMALIZED_NAME]
            while channel in channels:
                channel = _increment_channel_name(channel)

            channels.add(channel)
            row[CARD_DISCORD_CHANNEL] = channel

        locked = str(SETS[row[CARD_SET]].get(SET_LOCKED, '') or '')
        if locked:
            row[CARD_SET_LOCKED] = locked

        card_set = re.sub(r'^ALeP - ', '', row[CARD_SET_NAME])
        discord_prefix = str(SETS[row[CARD_SET]].get(SET_DISCORD_PREFIX, '')
                             or '')
        if discord_prefix:
            discord_prefix = '{} '.format(discord_prefix)

        category = row.get(CARD_ENCOUNTER_SET, '')
        if not category:
            category = 'Player - {}{}'.format(discord_prefix, card_set)
        elif category != card_set:
            category = '{} ({}{})'.format(category, discord_prefix,
                                          card_set)
        else:
            category = '{}{}'.format(discord_prefix, category)

        category = _update_discord_category(category)
        row[CARD_DISCORD_CATEGORY] = category

        for key in list(row.keys()):
            if key in DISCORD_IGNORE_COLUMNS:
                del row[key]

    data.sort(key=lambda row: (
        row[CARD_SET_RINGSDB_CODE],
        is_positive_or_zero_int(row[CARD_NUMBER])
        and int(row[CARD_NUMBER]) or 0,
        row[CARD_NUMBER]))

    try:
        with open(DISCORD_CARD_DATA_PATH, 'r') as obj:
            old_data = json.load(obj)['data']
    except Exception:  # pylint: disable=W0703
        old_data = None

    card_changes = []
    category_diffs = []
    channel_diffs = []
    old_categories = set()
    new_categories = set()
    if old_data:
        old_categories = set(row[CARD_DISCORD_CATEGORY] for row in old_data)
        new_categories = set(row[CARD_DISCORD_CATEGORY] for row in data)
        old_dict = {row[CARD_ID]:row for row in old_data}
        new_dict = {row[CARD_ID]:row for row in data}
        for card_id in new_dict:
            if card_id not in old_dict:
                card_changes.append(('add', card_id, {
                    CARD_NAME: new_dict[card_id][CARD_NAME],
                    CARD_SET_NAME: new_dict[card_id][CARD_SET_NAME],
                    CARD_DISCORD_CATEGORY:
                        new_dict[card_id][CARD_DISCORD_CATEGORY],
                    CARD_DISCORD_CHANNEL: new_dict[card_id].get(
                        CARD_DISCORD_CHANNEL)}))

                if new_dict[card_id].get(CARD_DISCORD_CHANNEL):
                    channel_diffs.append(
                        (None,
                         (new_dict[card_id][CARD_DISCORD_CHANNEL],
                          new_dict[card_id][CARD_DISCORD_CATEGORY])))
            elif old_dict[card_id] != new_dict[card_id]:
                if not new_dict[card_id].get(CARD_BOT_DISABLED):
                    diffs = _get_card_diffs(old_dict[card_id],
                                            new_dict[card_id])
                    if diffs:
                        card_changes.append(('change', card_id, diffs))

                if (old_dict[card_id][CARD_DISCORD_CATEGORY] !=
                        new_dict[card_id][CARD_DISCORD_CATEGORY]):
                    category_diffs.append((
                        old_dict[card_id][CARD_DISCORD_CATEGORY],
                        new_dict[card_id][CARD_DISCORD_CATEGORY]))

                if (old_dict[card_id].get(CARD_DISCORD_CHANNEL) and
                        new_dict[card_id].get(CARD_DISCORD_CHANNEL) and
                        (old_dict[card_id][CARD_DISCORD_CATEGORY] !=
                         new_dict[card_id][CARD_DISCORD_CATEGORY] or
                         old_dict[card_id][CARD_DISCORD_CHANNEL] !=
                         new_dict[card_id][CARD_DISCORD_CHANNEL])):
                    channel_diffs.append((
                        (old_dict[card_id][CARD_DISCORD_CHANNEL],
                         old_dict[card_id][CARD_DISCORD_CATEGORY]),
                        (new_dict[card_id][CARD_DISCORD_CHANNEL],
                         new_dict[card_id][CARD_DISCORD_CATEGORY])))

        for card_id in old_dict:
            if card_id not in new_dict:
                if old_dict[card_id].get(CARD_DISCORD_CHANNEL):
                    channel_diffs.append(
                        ((old_dict[card_id][CARD_DISCORD_CHANNEL],
                          old_dict[card_id][CARD_DISCORD_CATEGORY]),
                         None))

                card_changes.append(('remove', card_id, {
                    CARD_NAME: old_dict[card_id][CARD_NAME],
                    CARD_SET_NAME: old_dict[card_id][CARD_SET_NAME],
                    CARD_DISCORD_CATEGORY:
                        old_dict[card_id][CARD_DISCORD_CATEGORY],
                    CARD_DISCORD_CHANNEL: old_dict[card_id].get(
                        CARD_DISCORD_CHANNEL)}))

        for category in list(old_categories):
            if category in new_categories:
                old_categories.remove(category)
                new_categories.remove(category)

    category_changes = []
    for new_category in new_categories:
        for old_category in list(old_categories):
            if (old_category, new_category) in category_diffs:
                old_categories.remove(old_category)
                category_changes.append(('rename',
                                         (old_category, new_category)))
                break
        else:
            category_changes.append(('add', new_category))

    channel_changes = []
    for diff in channel_diffs:
        if not diff[0]:
            channel_changes.append(('add', diff[1]))
        elif not diff[1]:
            channel_changes.append(('remove', diff[0][0]))
        elif diff[0][0] == diff[1][0]:
            if ('rename', (diff[0][1], diff[1][1])) not in category_changes:
                channel_changes.append(('move', diff[1]))
        elif diff[0][1] == diff[1][1]:
            channel_changes.append(('rename', (diff[0][0], diff[1][0])))
        else:
            if ('rename', (diff[0][1], diff[1][1])) not in category_changes:
                channel_changes.append(('move', (diff[0][0], diff[1][1])))

            channel_changes.append(('rename', (diff[0][0], diff[1][0])))

    set_names = [SETS[set_id][SET_NAME] for set_id in FOUND_SETS]
    output = {'url': url,
              'sets': set_names,
              'data': data}
    with open(DISCORD_CARD_DATA_PATH, 'w', encoding='utf-8') as obj:
        res = json.dumps(output, ensure_ascii=False)
        obj.write(res)

    if category_changes or channel_changes or card_changes:
        output = {'categories': category_changes,
                  'channels': channel_changes,
                  'cards': card_changes}
        path = os.path.join(
            DISCORD_PATH, 'Changes',
            '{}_{}.json'.format(int(time.time()), uuid.uuid4()))
        with open(path, 'w', encoding='utf-8') as obj:
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
    output_path = os.path.join(OUTPUT_OCTGN_PATH, escape_filename(set_name))
    create_folder(output_path)
    output_path = os.path.join(output_path, set_id)
    create_folder(output_path)
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
            value = str(value).upper() if value else 'CAMPAIGN'

        return value

    if name in (CARD_UNIQUE, BACK_PREFIX + CARD_UNIQUE):
        if value:
            value = '‰'

        return value

    if name in (CARD_VICTORY, BACK_PREFIX + CARD_VICTORY):
        if card_type in ('Presentation', 'Rules'):
            if value:
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
            value = '{}\n\n{}'.format(row[CARD_KEYWORDS], value)
    elif name == BACK_PREFIX + CARD_TEXT and row[BACK_PREFIX + CARD_KEYWORDS]:
        if row[BACK_PREFIX + CARD_SHADOW]:
            value = '{} {}'.format(row[BACK_PREFIX + CARD_KEYWORDS], value)
        else:
            value = '{}\n\n{}'.format(row[BACK_PREFIX + CARD_KEYWORDS], value)

    return value


def _add_set_xml_properties(parent, properties, fix_linebreaks, tab):
    """ Append property elements to OCTGN set.xml.
    """
    parent.text = '\n' + tab + '  '
    for i, (name, value) in enumerate(properties):
        if not name:
            continue

        prop = ET.SubElement(parent, 'property')
        prop.set('name', name)
        prop.set('value', _update_octgn_card_text(str(_handle_int_str(value)),
                                                  fix_linebreaks=fix_linebreaks))

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
    root.set('name', str(set_name))
    root.set('id', str(set_id))
    root.set('version', str(SETS[set_id][SET_VERSION]))
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
        card.set('id', str(row[CARD_ID]))
        card.set('name', _update_octgn_card_text(row[CARD_NAME] or ''))

        card_type = row[CARD_TYPE]
        if card_type == 'Player Side Quest':
            card_size = 'PlayerQuestCard'
        elif card_type in ('Encounter Side Quest', 'Quest'):
            card_size = 'QuestCard'
        elif ((card_type in CARD_TYPES_ENCOUNTER_SIZE or
               'Encounter' in (row[CARD_KEYWORDS] or ''
                              ).replace('. ', '.').split('.') or
               row[CARD_BACK] == 'Encounter') and
              row[CARD_BACK] != 'Player'):
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

        fix_linebreaks = card_type not in ('Presentation', 'Rules')

        if properties:
            if side_b:
                properties.append(('', ''))

            _add_set_xml_properties(card, properties, fix_linebreaks, '    ')

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
                _add_set_xml_properties(alternate, properties, fix_linebreaks,
                                        '      ')

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

    return None


def _save_content(url, content):
    """ Save URL's content into cache.
    """
    path = os.path.join(URL_CACHE_PATH, '{}.cache'.format(
        re.sub(r'[^A-Za-z0-9_\.\-]', '', url)))
    with open(path, 'bw') as obj:
        obj.write(content)


def load_external_xml(url, sets=None, encounter_sets=None):  # pylint: disable=R0912,R0914,R0915
    """ Load cards from an external XML file.
    """
    res = []
    if url in XML_CACHE:
        content = XML_CACHE[url]
        root = ET.fromstring(content)
    else:
        content = _get_cached_content(url)
        if content:
            XML_CACHE[url] = content
            root = ET.fromstring(content)
        else:
            content = _get_content(url)
            if not content or not b'<?xml' in content:
                logging.error("Can't download XML from %s, ignoring", url)
                return res

            try:
                root = ET.fromstring(content)
            except ET.ParseError:
                logging.error("Can't download XML from %s, ignoring", url)
                return res

            XML_CACHE[url] = content
            _save_content(url, content)

    set_name = str(root.attrib['name']).lower()
    if sets and set_name not in sets:
        return res

    for card in root[0]:
        row = {}
        encounter_set = _find_properties(card, 'Encounter Set')
        if encounter_set:
            encounter_set = str(encounter_set[0].attrib['value'])
            if encounter_sets and encounter_set.lower() not in encounter_sets:
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
            if 'Ship' in [t.strip() for t in str(traits).split('.')]:
                card_type = 'Ship Enemy'
        elif card_type == 'Objective':
            if 'Ship' in [t.strip() for t in str(traits).split('.')]:
                card_type = 'Ship Objective'

        sphere = _find_properties(card, 'Sphere')
        sphere = sphere[0].attrib['value'] if sphere else None

        if (not sphere and encounter_set
                and encounter_set.lower().endswith(' - nightmare')
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

        if not card.attrib.get('size'):
            row[CARD_BACK] = 'Player'
        elif card.attrib.get('size') == 'EncounterCard':
            row[CARD_BACK] = 'Encounter'
        else:
            row[CARD_BACK] = None

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
        card[CARD_ENCOUNTER_SET] = str(card[CARD_ENCOUNTER_SET]).lower()

    card[CARD_ORIGINAL_NAME] = card[CARD_NAME]
    card[CARD_SET_NAME] = str(card[CARD_SET_NAME]).lower()
    card[CARD_NAME] = str(card[CARD_NAME]).lower() if card[CARD_NAME] else ''
    card[CARD_TYPE] = str(card[CARD_TYPE]).lower() if card[CARD_TYPE] else ''
    card[CARD_SPHERE] = (str(card[CARD_SPHERE]).lower()
                         if card[CARD_SPHERE] else '')
    card[CARD_TRAITS] = ([t.lower().strip()
                          for t in str(card[CARD_TRAITS]).split('.') if t]
                         if card[CARD_TRAITS] else [])
    card[CARD_KEYWORDS] = ([k.lower().strip()
                            for k in str(card[CARD_KEYWORDS]).split('.') if k]
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

    parts = [p.strip() for p in str(rule).split('&') if p.strip()]
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
                r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
                part):
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

    rules = [str(r).lower() for r in rules]
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
    if not rows:
        return

    cards = [_update_card_for_rules(r.copy()) for r in rows]
    root = ET.fromstring(O8D_TEMPLATE)
    _append_cards(root.findall("./section[@name='Hero']")[0], cards)

    output_path = os.path.join(OUTPUT_OCTGN_DECKS_PATH,
                               escape_filename(set_name))
    filename = escape_octgn_filename(
        'Player-{}.o8d'.format(escape_filename(set_name)))
    with open(
            os.path.join(output_path, filename),
            'w', encoding='utf-8') as obj:
        res = ET.tostring(root, encoding='utf-8').decode('utf-8')
        res = res.replace('<notes />', '<notes><![CDATA[]]></notes>')
        obj.write('<?xml version="1.0" encoding="utf-8" standalone="yes"?>')
        obj.write('\n')
        obj.write(res)


def generate_octgn_o8d(conf, set_id, set_name):  # pylint: disable=R0912,R0914,R0915
    """ Generate .o8d files for OCTGN and DragnCards.
    """
    logging.info('[%s] Generating .o8d files for OCTGN and DragnCards...',
                 set_name)
    timestamp = time.time()

    rows = [row for row in DATA
            if row[CARD_SET] == set_id
            and ((row[CARD_TYPE] == 'Quest' and row[CARD_ADVENTURE])
                 or row[CARD_TYPE] == 'Nightmare')
            and row[CARD_DECK_RULES]
            and (not conf['selected_only'] or row[CARD_ID] in SELECTED_CARDS)]

    quests = {}
    for row in rows:
        quest = quests.setdefault(
            row[CARD_ADVENTURE] or row[CARD_NAME],
            {'name': row[CARD_ADVENTURE] or row[CARD_NAME],
             'sets': set([str(row[CARD_SET_NAME]).lower()]),
             'encounter sets': set(),
             'prefix': '',
             'rules': row[CARD_DECK_RULES],
             'modes': ['']})
        if row[CARD_ENCOUNTER_SET]:
            quest['encounter sets'].add(str(row[CARD_ENCOUNTER_SET]).lower())

        if row[CARD_ADDITIONAL_ENCOUNTER_SETS]:
            for encounter_set in [
                    r.lower().strip()
                    for r in
                    str(row[CARD_ADDITIONAL_ENCOUNTER_SETS]).split(';')]:
                quest['encounter sets'].add(encounter_set)

    quests = list(quests.values())
    new_quests = []
    for quest in quests:
        parts = str(quest['rules']).split('\n\n')
        if len(parts) > 1:
            quest['rules'] = parts.pop(0)
            for part in parts:
                new_quest = copy.deepcopy(quest)
                new_quest['rules'] = part
                new_quests.append(new_quest)

    quests.extend(new_quests)

    output_path = os.path.join(OUTPUT_OCTGN_DECKS_PATH,
                               escape_filename(set_name))
    clear_folder(output_path)
    if quests:
        create_folder(output_path)

    for quest in quests:
        if not quest['rules']:
            continue

        rules_list = [r.strip().split(':', 1)
                      for r in str(quest['rules']).split('\n')]
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

        if rules.get(('prefix', 0)):
            quest['prefix'] = rules[('prefix', 0)][0] + ' '
            quest['prefix'] = quest['prefix'][:6].upper() + quest['prefix'][6:]

        if not quest['prefix']:
            continue

        if not re.match(DECK_PREFIX_REGEX, quest['prefix']):
            continue

        if rules.get(('sets', 0)):
            quest['sets'].update([str(s).lower() for s in rules[('sets', 0)]])

        if rules.get(('encounter sets', 0)):
            quest['encounter sets'].update(
                [str(s).lower() for s in rules[('encounter sets', 0)]])

        cards = [r for r in DATA
                 if r[CARD_ID]
                 and str(r[CARD_SET_NAME] or '').lower() in quest['sets']
                 and (not r[CARD_ENCOUNTER_SET] or
                      str(r[CARD_ENCOUNTER_SET]).lower()
                      in quest['encounter sets'])
                 and (r[CARD_TYPE] != 'Rules' or
                      (r.get(CARD_TEXT) or '') not in ('', 'T.B.D.') or
                      (r.get(BACK_PREFIX + CARD_TEXT) or '')
                      not in ('', 'T.B.D.'))]
        for url in rules.get(('external xml', 0), []):
            cards.extend(load_external_xml(url, quest['sets'],
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

            if mode == EASY_PREFIX and quest['prefix'].startswith('Q'):
                filename = escape_octgn_filename(
                    '{}{}{}.o8d'.format('E', quest['prefix'][1:],
                                        escape_filename(quest['name'])))
            else:
                filename = escape_octgn_filename(
                    '{}{}{}.o8d'.format(mode, quest['prefix'],
                                        escape_filename(quest['name'])))
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

    logging.info('[%s] ...Generating .o8d files for OCTGN and DragnCards '
                 '(%ss)', set_name, round(time.time() - timestamp, 3))


def _needed_for_ringsdb(card):
    """ Check whether a card is needed for RingsDB or not.
    """
    card_type = ('Treasure' if card.get(CARD_SPHERE) == 'Boon'
                 else card[CARD_TYPE])
    return card_type in CARD_TYPES_PLAYER


def _needed_for_frenchdb(card):
    """ Check whether a card is needed for the French database or not.
    """
    return card[CARD_TYPE] not in ('Presentation', 'Rules')


def _needed_for_spanishdb(card):
    """ Check whether a card is needed for the Spanish database or not.
    """
    return (card[CARD_TYPE] != 'Presentation' and
            not (card[CARD_TYPE] == 'Rules' and card[CARD_SPHERE] == 'Back'))


def _ringsdb_code(row):
    """ Return the card's RingsDB code.
    """
    card_number = (str(int(row[CARD_NUMBER])).zfill(3)
                   if is_positive_or_zero_int(row[CARD_NUMBER])
                   else '000')
    code = '{}{}'.format(row[CARD_SET_RINGSDB_CODE], card_number)
    return code


def _spanishdb_code(row):
    """ Return the card's Spanish database code.
    """
    card_number = str(_handle_int(row[CARD_NUMBER])).zfill(3)
    code = '{}{}'.format(row[CARD_SET_RINGSDB_CODE], card_number)
    return code


def generate_ringsdb_csv(conf, set_id, set_name):  # pylint: disable=R0912,R0914, R0915
    """ Generate CSV file for RingsDB.
    """
    logging.info('[%s] Generating CSV file for RingsDB...', set_name)
    timestamp = time.time()

    output_path = os.path.join(OUTPUT_RINGSDB_PATH, escape_filename(set_name))
    create_folder(output_path)

    output_path = os.path.join(output_path,
                               '{}.csv'.format(escape_filename(set_name)))
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
                        if _is_int(row[CARD_QUANTITY]) else 1)

            text = _update_card_text('{}\n\n{}'.format(
                row[CARD_KEYWORDS] or '',
                row[CARD_TEXT] or '')).strip()

            if (row[CARD_SIDE_B] is not None and
                    row[BACK_PREFIX + CARD_TEXT] is not None):
                text_back = _update_card_text('{}\n\n{}'.format(
                    row[BACK_PREFIX + CARD_KEYWORDS] or '',
                    row[BACK_PREFIX + CARD_TEXT])).strip()
                text = '<b>Side A</b>\n{}\n<b>Side B</b>\n{}'.format(
                    text, text_back)

            flavor = _update_card_text(row[CARD_FLAVOUR] or '',
                                       skip_rules=True, fix_linebreaks=False)
            if (row[CARD_SIDE_B] is not None and
                    row[BACK_PREFIX + CARD_FLAVOUR] is not None):
                flavor_back = _update_card_text(
                    row[BACK_PREFIX + CARD_FLAVOUR], skip_rules=True,
                    fix_linebreaks=False)
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

            if (csv_row['type'] == 'Ally' and csv_row['isUnique'] == 1 and
                    csv_row['sphere'] != 'Neutral'):
                new_row = csv_row.copy()
                new_row['pack'] = 'Messenger of the King Allies'
                new_row['type'] = 'Hero'
                new_row['code'] = '99{}'.format(new_row['code'])
                new_row['name'] = '(MotK) {}'.format(new_row['name'])
                new_row['cost'] = None
                willpower = (new_row['willpower']
                             if _is_int(new_row['willpower']) else 0)
                attack = (new_row['attack']
                          if _is_int(new_row['attack']) else 0)
                defense = (new_row['defense']
                           if _is_int(new_row['defense']) else 0)
                health = (new_row['health']
                          if _is_int(new_row['health']) else 0)
                new_row['threat'] = willpower + attack + defense + health
                new_row['quantity'] = 1
                new_row['deckLimit'] = 1
                writer.writerow(new_row)

    logging.info('[%s] ...Generating CSV file for RingsDB (%ss)',
                 set_name, round(time.time() - timestamp, 3))


def generate_dragncards_json(conf, set_id, set_name):  # pylint: disable=R0912,R0914,R0915
    """ Generate JSON file for DragnCards.
    """
    logging.info('[%s] Generating JSON file for DragnCards...', set_name)
    timestamp = time.time()

    output_path = os.path.join(OUTPUT_DRAGNCARDS_PATH,
                               escape_filename(set_name))
    create_folder(output_path)

    output_path = os.path.join(
        output_path,
        '{}.json'.format(escape_octgn_filename(escape_filename(set_name))))

    json_data = {}
    for row in DATA:
        if row[CARD_SET] != set_id:
            continue

        if (row[CARD_TYPE] == 'Presentation' or
                (row[CARD_TYPE] == 'Rules' and row[CARD_SPHERE] == 'Back')):
            continue

        if conf['selected_only'] and row[CARD_ID] not in SELECTED_CARDS:
            continue

        if row[CARD_TYPE] == 'Encounter Side Quest':
            card_type = 'Side Quest'
        else:
            card_type = row[CARD_TYPE]

        if row[CARD_TYPE] == 'Treasure':
            sphere = 'Neutral'
        else:
            sphere = row[CARD_SPHERE]

        if row[CARD_TYPE] == 'Rules' and row[CARD_VICTORY]:
            victory = 'Page {}'.format(row[CARD_VICTORY])
        else:
            victory = row[CARD_VICTORY]

        side_a = {
            'name': unidecode.unidecode(_to_str(row[CARD_NAME])),
            'printname': _to_str(row[CARD_NAME]),
            'unique': _to_str(_handle_int(row[CARD_UNIQUE])),
            'type': _to_str(card_type),
            'sphere': _to_str(sphere),
            'traits': _to_str(row[CARD_TRAITS]),
            'keywords': _update_dragncards_card_text(_to_str(
                row[CARD_KEYWORDS])),
            'cost': _to_str(_handle_int(row[CARD_COST])),
            'engagementcost': _to_str(_handle_int(row[CARD_ENGAGEMENT])),
            'threat': _to_str(_handle_int(row[CARD_THREAT])),
            'willpower': _to_str(_handle_int(row[CARD_WILLPOWER])),
            'attack': _to_str(_handle_int(row[CARD_ATTACK])),
            'defense': _to_str(_handle_int(row[CARD_DEFENSE])),
            'hitpoints': _to_str(_handle_int(row[CARD_HEALTH])),
            'questpoints': _to_str(_handle_int(row[CARD_QUEST])),
            'victorypoints': _to_str(_handle_int(victory)),
            'text': _update_dragncards_card_text(_to_str(row[CARD_TEXT])),
            'shadow': _update_dragncards_card_text(_to_str(row[CARD_SHADOW]))
        }

        if row[CARD_SIDE_B]:
            if row[BACK_PREFIX + CARD_TYPE] == 'Encounter Side Quest':
                card_type = 'Side Quest'
            else:
                card_type = row[BACK_PREFIX + CARD_TYPE]

            if row[BACK_PREFIX + CARD_TYPE] == 'Treasure':
                sphere = 'Neutral'
            else:
                sphere = row[BACK_PREFIX + CARD_SPHERE]

            if (row[BACK_PREFIX + CARD_TYPE] == 'Rules' and
                    row[BACK_PREFIX + CARD_VICTORY]):
                victory = 'Page {}'.format(row[BACK_PREFIX + CARD_VICTORY])
            else:
                victory = row[BACK_PREFIX + CARD_VICTORY]

            side_b = {
                'name': unidecode.unidecode(_to_str(row[CARD_SIDE_B])),
                'printname': _to_str(row[CARD_SIDE_B]),
                'unique': _to_str(_handle_int(row[BACK_PREFIX + CARD_UNIQUE])),
                'type': _to_str(card_type),
                'sphere': _to_str(sphere),
                'traits': _to_str(row[BACK_PREFIX + CARD_TRAITS]),
                'keywords': _update_dragncards_card_text(_to_str(
                    row[BACK_PREFIX + CARD_KEYWORDS])),
                'cost': _to_str(_handle_int(row[BACK_PREFIX + CARD_COST])),
                'engagementcost': _to_str(
                    _handle_int(row[BACK_PREFIX + CARD_ENGAGEMENT])),
                'threat': _to_str(_handle_int(row[BACK_PREFIX + CARD_THREAT])),
                'willpower': _to_str(
                    _handle_int(row[BACK_PREFIX + CARD_WILLPOWER])),
                'attack': _to_str(_handle_int(row[BACK_PREFIX + CARD_ATTACK])),
                'defense': _to_str(
                    _handle_int(row[BACK_PREFIX + CARD_DEFENSE])),
                'hitpoints': _to_str(
                    _handle_int(row[BACK_PREFIX + CARD_HEALTH])),
                'questpoints': _to_str(
                    _handle_int(row[BACK_PREFIX + CARD_QUEST])),
                'victorypoints': _to_str(_handle_int(victory)),
                'text': _update_dragncards_card_text(_to_str(
                    row[BACK_PREFIX + CARD_TEXT])),
                'shadow': _update_dragncards_card_text(_to_str(
                    row[BACK_PREFIX + CARD_SHADOW]))
            }
        else:
            if ((row[CARD_TYPE] in CARD_TYPES_PLAYER and
                 'Encounter' not in (row[CARD_KEYWORDS] or ''
                                     ).replace('. ', '.').split('.') and
                 row[CARD_BACK] != 'Encounter') or
                    row[CARD_BACK] == 'Player'):
                default_name = 'player'
            else:
                default_name = 'encounter'

            side_b = {
                'name': default_name,
                'printname': default_name,
                'unique': '',
                'type': '',
                'sphere': '',
                'traits': '',
                'keywords': '',
                'cost': '',
                'engagementcost': '',
                'threat': '',
                'willpower': '',
                'attack': '',
                'defense': '',
                'hitpoints': '',
                'questpoints': '',
                'victorypoints': '',
                'text': '',
                'shadow': ''
            }

        card_data = {
            'sides': {
                'A': side_a,
                'B': side_b
            },
            'cardsetid': _to_str(row[CARD_SET]),
            'cardpackname': _to_str(row[CARD_SET_NAME]),
            'cardid': _to_str(row[CARD_ID]),
            'cardnumber': _to_str(_handle_int(row[CARD_NUMBER])),
            'cardquantity': _to_str(_handle_int(row[CARD_QUANTITY])),
            'cardencounterset': _to_str(row[CARD_ENCOUNTER_SET]),
            'playtest': 1
        }
        json_data[row[CARD_ID]] = card_data

    with open(output_path, 'w', encoding='utf-8') as obj:
        res = json.dumps(json_data, ensure_ascii=True, indent=4)
        obj.write(res)

    logging.info('[%s] ...Generating JSON file for DragnCards (%ss)',
                 set_name, round(time.time() - timestamp, 3))


def generate_hallofbeorn_json(conf, set_id, set_name, lang):  # pylint: disable=R0912,R0914,R0915
    """ Generate JSON file for Hall of Beorn.
    """
    logging.info('[%s, %s] Generating JSON file for Hall of Beorn...',
                 set_name, lang)
    timestamp = time.time()

    output_path = os.path.join(OUTPUT_HALLOFBEORN_PATH,
                               '{}.{}'.format(escape_filename(set_name), lang))
    create_folder(output_path)
    output_path = os.path.join(
        output_path,
        '{}.{}.json'.format(escape_filename(set_name), lang))

    json_data = []
    card_data = DATA[:]
    for row in DATA:
        if (row[CARD_SIDE_B] is not None and
                row[CARD_TYPE] not in CARD_TYPES_DOUBLESIDE_OPTIONAL):
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

        if lang == 'English':
            translated_row = row
        else:
            translated_row = TRANSLATIONS[lang].get(row[CARD_ID], {}).copy()
            if row.get(CARD_DOUBLESIDE):
                translated_row[CARD_NAME] = translated_row.get(CARD_SIDE_B, '')
                for key in translated_row.keys():
                    if key.startswith(BACK_PREFIX):
                        translated_row[key.replace(BACK_PREFIX, '')] = (
                            translated_row[key])

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

        if (translated_row.get(CARD_SIDE_B) is not None and
                translated_row[CARD_SIDE_B] !=
                translated_row.get(CARD_NAME, '') and
                card_type in CARD_TYPES_DOUBLESIDE_OPTIONAL):
            opposite_title = translated_row[CARD_SIDE_B]
        else:
            opposite_title = None

        keywords = extract_keywords(translated_row.get(CARD_KEYWORDS))
        keywords_original = extract_keywords(row.get(CARD_KEYWORDS))
        if len(keywords) != len(keywords_original):
            logging.error('Different number of keywords in %s translation for '
                          'card ID %s', lang, row[CARD_ID])
            logging.error('English: %s', keywords_original)
            logging.error('Translated: %s', keywords)

        traits = [t.strip() for t in
                  str(translated_row.get(CARD_TRAITS) or '').split('.')
                  if t != '']
        traits_original = [t.strip() for t in
                           str(row.get(CARD_TRAITS) or '').split('.')
                           if t != '']
        if len(traits) != len(traits_original):
            logging.error('Different number of traits in %s translation for '
                          'card ID %s', lang, row[CARD_ID])
            logging.error('English: %s', traits_original)
            logging.error('Translated: %s', traits)

        position = (int(row[CARD_NUMBER])
                    if is_positive_or_zero_int(row[CARD_NUMBER]) else 0)
        encounter_set = ((row[CARD_ENCOUNTER_SET] or '')
                         if card_type in CARD_TYPES_ENCOUNTER_SET
                         else row[CARD_ENCOUNTER_SET])
        subtitle = ((translated_row.get(CARD_ADVENTURE) or '')
                    if card_type in CARD_TYPES_ADVENTURE
                    else translated_row.get(CARD_ADVENTURE))
        if subtitle and card_type == 'Hero':
            subtitle = None

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
                _handle_int_str(translated_row.get(CARD_VICTORY))
                or _handle_int_str(translated_row.get(
                    BACK_PREFIX + CARD_VICTORY)))
        else:
            victory_points = _handle_int_str(translated_row.get(CARD_VICTORY))

        additional_encounter_sets = [
            s.strip() for s in str(row[CARD_ADDITIONAL_ENCOUNTER_SETS] or ''
                                   ).split(';')
            if s != ''] or None

        fix_linebreaks = card_type not in ('Presentation', 'Rules')

        text = _update_card_text('{}\n\n{}'.format(
            translated_row.get(CARD_KEYWORDS) or '',
            translated_row.get(CARD_TEXT) or ''
            ), fix_linebreaks=fix_linebreaks).replace('\n', '\r\n').strip()
        if (card_type in ('Presentation', 'Rules') and
                translated_row.get(CARD_VICTORY) is not None):
            text = '{}\r\n\r\nPage {}'.format(text,
                                              translated_row[CARD_VICTORY])

        if (translated_row.get(CARD_SIDE_B) is not None and
                (translated_row.get(BACK_PREFIX + CARD_TEXT) is not None or
                 (card_type in ('Presentation', 'Rules')
                  and translated_row.get(BACK_PREFIX + CARD_VICTORY)
                  is not None)) and
                card_type in CARD_TYPES_DOUBLESIDE_OPTIONAL):
            text_back = _update_card_text(
                translated_row.get(BACK_PREFIX + CARD_TEXT) or '',
                fix_linebreaks=fix_linebreaks
                ).replace('\n', '\r\n').strip()
            if (card_type in ('Presentation', 'Rules') and
                    translated_row.get(BACK_PREFIX + CARD_VICTORY) is not None):
                text_back = '{}\r\n\r\nPage {}'.format(
                    text_back, translated_row[BACK_PREFIX + CARD_VICTORY])
            text = '<b>Side A</b> {} <b>Side B</b> {}'.format(text, text_back)

        flavor = (_update_card_text(translated_row.get(CARD_FLAVOUR) or '',
                                    skip_rules=True,
                                    fix_linebreaks=False
                                    ).replace('\n', '\r\n').strip())
        if (translated_row.get(CARD_SIDE_B) is not None and
                translated_row.get(BACK_PREFIX + CARD_FLAVOUR) is not None and
                card_type in CARD_TYPES_DOUBLESIDE_OPTIONAL):
            flavor_back = _update_card_text(
                translated_row[BACK_PREFIX + CARD_FLAVOUR],
                skip_rules=True,
                fix_linebreaks=False
                ).replace('\n', '\r\n').strip()
            flavor = 'Side A: {} Side B: {}'.format(flavor, flavor_back)

        quantity = (int(row[CARD_QUANTITY])
                    if _is_int(row[CARD_QUANTITY]) else 1)

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
            'keywords_original': keywords_original,
            'name': translated_row.get(CARD_NAME, ''),
            'octgnid': row[CARD_ID],
            'pack_code': row[CARD_SET_HOB_CODE],
            'pack_name': set_name,
            'position': position,
            'quantity': quantity,
            'sphere_code': str(sphere).lower().replace(' ', '-'),
            'sphere_name': sphere,
            'text': text,
            'traits': traits,
            'traits_original': traits_original,
            'type_code': str(type_name).lower().replace(' ', '-'),
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
            'shadow_text': translated_row.get(CARD_SHADOW) is not None and
                           _update_card_text(translated_row[CARD_SHADOW]
                                             ).replace('\n', '\r\n').strip()
                           or None,
            'stage_letter': stage_letter,
            'subtitle': subtitle,
            'subtype_code': (subtype_name and
                             str(subtype_name).lower().replace(' ', '-')
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
        res = json.dumps(json_data, ensure_ascii=False, indent=4)
        obj.write(res)

    logging.info('[%s, %s] ...Generating JSON file for Hall of Beorn (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def generate_frenchdb_csv(conf, set_id, set_name):  # pylint: disable=R0912,R0914,R0915
    """ Generate CSV files for the French database.
    """
    logging.info('[%s] Generating CSV files for the French database...',
                 set_name)
    timestamp = time.time()

    output_folder = os.path.join(OUTPUT_FRENCHDB_PATH,
                                 escape_filename(set_name))
    create_folder(output_folder)

    data = DATA[:]
    data = sorted(
        [row for row in data if row[CARD_SET] == set_id
         and _needed_for_frenchdb(row)
         and (not conf['selected_only'] or row[CARD_ID] in SELECTED_CARDS)
        ], key=lambda r: str(int(r[CARD_NUMBER])).zfill(3)
        if is_positive_or_zero_int(r[CARD_NUMBER])
        else str(r[CARD_NUMBER]))

    output_path = os.path.join(output_folder, 'carte_joueur.csv')
    with open(output_path, 'w', newline='', encoding='utf-8') as obj:
        obj.write(codecs.BOM_UTF8.decode('utf-8'))
        fieldnames = ['id_extension', 'numero_identification', 'id_type_carte',
                      'id_sous_type_carte', 'id_sphere_influence', 'id_octgn',
                      'titre', 'cout', 'menace', 'volonte', 'attaque',
                      'defense', 'point_vie', 'trait', 'texte', 'indic_unique',
                      'indic_recto_verso', 'nb_normal', 'nb_facile',
                      'nb_cauchemar']
        writer = csv.DictWriter(obj, delimiter=';', fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            if row[CARD_TYPE] not in CARD_TYPES_PLAYER_FRENCH:
                continue

            french_row = TRANSLATIONS['French'].get(row[CARD_ID], {}).copy()

            if row[CARD_TYPE] == 'Contract':
                sphere = 'Neutral'
            elif row[CARD_SPHERE] in ('Boon', 'Upgraded'):
                sphere = None
            else:
                sphere = row[CARD_SPHERE]

            if row[CARD_TYPE] == 'Hero':
                cost = None
                threat = _update_french_non_int(_handle_int(row[CARD_COST]))
            else:
                cost = _update_french_non_int(_handle_int(row[CARD_COST]))
                threat = None

            text = _update_french_card_text('{}\n\n{}'.format(
                french_row.get(CARD_KEYWORDS) or '',
                french_row.get(CARD_TEXT) or '')).strip()

            if ((row[CARD_TYPE] in CARD_TYPES_DOUBLESIDE_OPTIONAL or
                 row[CARD_SIDE_B] is not None) and
                    french_row.get(BACK_PREFIX + CARD_TEXT)):
                text_back = _update_french_card_text('{}\n\n{}'.format(
                    french_row.get(BACK_PREFIX + CARD_KEYWORDS) or '',
                    french_row[BACK_PREFIX + CARD_TEXT])).strip()
                text = '<b>Face A</b><br>{}<br><b>Face B</b><br>{}'.format(
                    text, text_back)

            if row[CARD_TYPE] in CARD_TYPES_PLAYER:
                quantity = 0
            else:
                quantity = (int(row[CARD_QUANTITY])
                            if _is_int(row[CARD_QUANTITY])
                            else 1)

            easy_mode = (int(row[CARD_EASY_MODE])
                         if _is_int(row[CARD_EASY_MODE])
                         else 0)

            csv_row = {
                'id_extension': row[CARD_SET_NAME],
                'numero_identification': int(row[CARD_NUMBER])
                                         if _is_int(row[CARD_NUMBER])
                                         else 0,
                'id_type_carte': CARD_TYPE_FRENCH_IDS.get(row[CARD_TYPE], 0),
                'id_sous_type_carte': CARD_SUBTYPE_FRENCH_IDS.get(
                    row[CARD_SPHERE]),
                'id_sphere_influence': CARD_SPHERE_FRENCH_IDS.get(sphere, 0),
                'id_octgn': row[CARD_ID],
                'titre': french_row.get(CARD_NAME, ''),
                'cout': cost,
                'menace': threat,
                'volonte': _update_french_non_int(
                    _handle_int(row[CARD_WILLPOWER])),
                'attaque': _update_french_non_int(
                    _handle_int(row[CARD_ATTACK])),
                'defense': _update_french_non_int(
                    _handle_int(row[CARD_DEFENSE])),
                'point_vie': _update_french_non_int(
                    _handle_int(row[CARD_HEALTH])),
                'trait': french_row.get(CARD_TRAITS),
                'texte': text,
                'indic_unique': int(row[CARD_UNIQUE] or 0),
                'indic_recto_verso': row[CARD_SIDE_B] is not None and 1 or 0,
                'nb_normal': quantity,
                'nb_facile': quantity - easy_mode,
                'nb_cauchemar': 0
                }
            writer.writerow(csv_row)

    output_path = os.path.join(output_folder, 'carte_rencontre.csv')
    with open(output_path, 'w', newline='', encoding='utf-8') as obj:
        obj.write(codecs.BOM_UTF8.decode('utf-8'))
        fieldnames = ['id_extension', 'numero_identification', 'id_type_carte',
                      'id_sous_type_carte', 'id_set_rencontre', 'titre',
                      'cout_engagement', 'menace', 'attaque', 'defense',
                      'point_quete', 'point_vie', 'trait', 'texte',
                      'effet_ombre', 'titre_quete', 'indic_unique',
                      'indic_recto_verso', 'nb_normal', 'nb_facile',
                      'nb_cauchemar']
        writer = csv.DictWriter(obj, delimiter=';', fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            if (row[CARD_TYPE] in CARD_TYPES_PLAYER_FRENCH or
                    row[CARD_TYPE] == 'Quest'):
                continue

            french_row = TRANSLATIONS['French'].get(row[CARD_ID], {}).copy()

            if row[CARD_SPHERE] == 'Setup':
                card_type = 'Nightmare'
            else:
                card_type = row[CARD_TYPE]

            text = _update_french_card_text('{}\n\n{}'.format(
                french_row.get(CARD_KEYWORDS) or '',
                french_row.get(CARD_TEXT) or '')).strip()

            if ((row[CARD_TYPE] in CARD_TYPES_DOUBLESIDE_OPTIONAL
                 or row[CARD_SIDE_B] is not None) and
                    french_row.get(BACK_PREFIX + CARD_TEXT)):
                text_back = _update_french_card_text('{}\n\n{}'.format(
                    french_row.get(BACK_PREFIX + CARD_KEYWORDS) or '',
                    french_row[BACK_PREFIX + CARD_TEXT])).strip()
                text = '<b>Face A</b><br>{}<br><b>Face B</b><br>{}'.format(
                    text, text_back)

            if french_row.get(CARD_SHADOW) is not None:
                shadow = _update_french_card_text(french_row[CARD_SHADOW]
                                                  ).strip()
            else:
                shadow = None

            quantity = (int(row[CARD_QUANTITY])
                        if _is_int(row[CARD_QUANTITY])
                        else 1)
            easy_mode = (int(row[CARD_EASY_MODE])
                         if _is_int(row[CARD_EASY_MODE])
                         else 0)

            csv_row = {
                'id_extension': row[CARD_SET_NAME],
                'numero_identification': int(row[CARD_NUMBER])
                                         if _is_int(row[CARD_NUMBER])
                                         else 0,
                'id_type_carte': CARD_TYPE_FRENCH_IDS.get(card_type, 0),
                'id_sous_type_carte': CARD_SUBTYPE_FRENCH_IDS.get(
                    row[CARD_SPHERE]),
                'id_set_rencontre': row[CARD_ENCOUNTER_SET] or '',
                'titre': french_row.get(CARD_NAME, ''),
                'cout_engagement': _update_french_non_int(
                    _handle_int(row[CARD_ENGAGEMENT])),
                'menace': _update_french_non_int(
                    _handle_int(row[CARD_THREAT])),
                'attaque': _update_french_non_int(
                    _handle_int(row[CARD_ATTACK])),
                'defense': _update_french_non_int(
                    _handle_int(row[CARD_DEFENSE])),
                'point_quete': _update_french_non_int(
                    _handle_int(row[CARD_QUEST])),
                'point_vie': _update_french_non_int(
                    _handle_int(row[CARD_HEALTH])),
                'trait': french_row.get(CARD_TRAITS),
                'texte': text,
                'effet_ombre': shadow,
                'titre_quete': french_row.get(CARD_ADVENTURE),
                'indic_unique': int(row[CARD_UNIQUE] or 0),
                'indic_recto_verso': row[CARD_SIDE_B] is not None and 1 or 0,
                'nb_normal': quantity,
                'nb_facile': quantity - easy_mode,
                'nb_cauchemar': 0
                }
            writer.writerow(csv_row)

    output_path = os.path.join(output_folder, 'carte_quete.csv')
    with open(output_path, 'w', newline='', encoding='utf-8') as obj:
        obj.write(codecs.BOM_UTF8.decode('utf-8'))
        fieldnames = ['id_extension', 'numero_identification',
                      'id_set_rencontre', 'titre', 'sequence', 'texteA',
                      'texteB', 'point_quete', 'nb_normal', 'nb_facile',
                      'nb_cauchemar']

        writer = csv.DictWriter(obj, delimiter=';', fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            if row[CARD_TYPE] != 'Quest':
                continue

            french_row = TRANSLATIONS['French'].get(row[CARD_ID], {})

            name = french_row.get(CARD_NAME, '')
            if french_row.get(CARD_SIDE_B) and french_row[CARD_SIDE_B] != name:
                name = '{} / {}'.format(name, french_row[CARD_SIDE_B])

            text = _update_french_card_text('{}\n\n{}'.format(
                french_row.get(CARD_KEYWORDS) or '',
                french_row.get(CARD_TEXT) or '')).strip()

            text_back = _update_french_card_text('{}\n\n{}'.format(
                french_row.get(BACK_PREFIX + CARD_KEYWORDS) or '',
                french_row.get(BACK_PREFIX + CARD_TEXT) or '')).strip()

            quantity = (int(row[CARD_QUANTITY])
                        if _is_int(row[CARD_QUANTITY])
                        else 1)

            csv_row = {
                'id_extension': row[CARD_SET_NAME],
                'numero_identification': int(row[CARD_NUMBER])
                                         if _is_int(row[CARD_NUMBER])
                                         else 0,
                'id_set_rencontre': row[CARD_ENCOUNTER_SET] or '',
                'titre': name,
                'sequence': str(_handle_int(row[CARD_COST])),
                'texteA': text,
                'texteB': text_back,
                'point_quete': _update_french_non_int(
                    _handle_int(row[BACK_PREFIX + CARD_QUEST])),
                'nb_normal': quantity,
                'nb_facile': quantity,
                'nb_cauchemar': 0
                }
            writer.writerow(csv_row)

    logging.info('[%s] ...Generating CSV files for the French database (%ss)',
                 set_name, round(time.time() - timestamp, 3))


def generate_spanishdb_csv(conf, set_id, set_name):  # pylint: disable=R0912,R0914,R0915
    """ Generate CSV files for the Spanish database.
    """
    logging.info('[%s] Generating CSV files for the Spanish database...',
                 set_name)
    timestamp = time.time()

    output_folder = os.path.join(OUTPUT_SPANISHDB_PATH,
                                 escape_filename(set_name))
    create_folder(output_folder)

    cycle = set_name
    presentations = [row for row in DATA
                     if row[CARD_SET] == set_id and
                     row[CARD_TYPE] == 'Presentation']
    if presentations:
        spanish_name = TRANSLATIONS['Spanish'].get(
            presentations[0][CARD_ID], {}).get(CARD_NAME)
        if spanish_name:
            cycle = spanish_name

    data = DATA[:]
    for row in DATA:
        if (row[CARD_SIDE_B] is not None and
                row[CARD_TYPE] not in CARD_TYPES_DOUBLESIDE_OPTIONAL):
            new_row = row.copy()
            new_row[CARD_NAME] = new_row[CARD_SIDE_B]
            new_row[CARD_DOUBLESIDE] = 'B'
            for key in new_row.keys():
                if key.startswith(BACK_PREFIX):
                    new_row[key.replace(BACK_PREFIX, '')] = new_row[key]

            data.append(new_row)

    data = sorted(
        [row for row in data if row[CARD_SET] == set_id
         and _needed_for_spanishdb(row)
         and (not conf['selected_only'] or row[CARD_ID] in SELECTED_CARDS)
        ], key=lambda r:
        (str(int(r[CARD_NUMBER])).zfill(3)
         if is_positive_or_zero_int(r[CARD_NUMBER])
         else str(r[CARD_NUMBER]), row.get(CARD_DOUBLESIDE, '')))

    output_path = os.path.join(output_folder, 'cartasenc.csv')
    with open(output_path, 'w', newline='', encoding='utf-8') as obj:
        obj.write(codecs.BOM_UTF8.decode('utf-8'))
        fieldnames = ['id', 'pack_id', 'cycle', 'cycle_id', 'octngId',
                      'type_id', 'set', 'set_id', 'position', 'code', 'nombre',
                      'nombreb', 'quantity', 'easy_mode', 'tipo',
                      'enfrentamiento', 'amenaza', 'attack', 'defense',
                      'health', 'mision', 'victory', 'traits', 'text',
                      'sombra']
        writer = csv.DictWriter(obj, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            if (row[CARD_TYPE] in CARD_TYPES_PLAYER or
                    row[CARD_TYPE] == 'Rules'):
                continue

            spanish_row = TRANSLATIONS['Spanish'].get(row[CARD_ID], {}).copy()
            if row.get(CARD_DOUBLESIDE):
                spanish_row[CARD_NAME] = spanish_row.get(CARD_SIDE_B, '')
                for key in spanish_row.keys():
                    if key.startswith(BACK_PREFIX):
                        spanish_row[key.replace(BACK_PREFIX, '')] = (
                            spanish_row[key])

            name = spanish_row.get(CARD_NAME)
            if (row[CARD_TYPE] in CARD_TYPES_DOUBLESIDE_OPTIONAL and
                    spanish_row.get(CARD_SIDE_B) and
                    spanish_row[CARD_SIDE_B] != name):
                name = '{} / {}'.format(name, spanish_row[CARD_SIDE_B])

            quantity = (int(row[CARD_QUANTITY])
                        if _is_int(row[CARD_QUANTITY])
                        else 1)
            easy_mode = (int(row[CARD_EASY_MODE])
                         if _is_int(row[CARD_EASY_MODE])
                         else 0)
            if row[CARD_TYPE] == 'Quest':
                quest_points = _handle_int(row[BACK_PREFIX + CARD_QUEST])
                engagement = _handle_int(row[CARD_COST])
                threat = '{}-{}'.format(
                    row[CARD_ENGAGEMENT] or '',
                    row[BACK_PREFIX + CARD_ENGAGEMENT] or '')
            else:
                quest_points = _handle_int(row[CARD_QUEST])
                engagement = _handle_int(row[CARD_ENGAGEMENT])
                threat = _handle_int(row[CARD_THREAT])

            if row[CARD_TYPE] in CARD_TYPES_DOUBLESIDE_OPTIONAL:
                victory_points = (
                    _handle_int(spanish_row.get(BACK_PREFIX + CARD_VICTORY))
                    if spanish_row.get(BACK_PREFIX + CARD_VICTORY) is not None
                    else _handle_int(spanish_row.get(CARD_VICTORY))
                    )
            else:
                victory_points = _handle_int(spanish_row.get(CARD_VICTORY))

            text = _update_card_text('{}\n\n{}'.format(
                spanish_row.get(CARD_KEYWORDS) or '',
                spanish_row.get(CARD_TEXT) or ''), lang='Spanish').strip()
            if text:
                text = '<p>{}</p>'.format(text.replace('\n', '</p><p>'))

            if spanish_row.get(CARD_SHADOW) is not None:
                shadow = _update_card_text(spanish_row.get(CARD_SHADOW),
                                           lang='Spanish').strip()
            elif (row[CARD_TYPE] in CARD_TYPES_DOUBLESIDE_OPTIONAL and
                  spanish_row.get(BACK_PREFIX + CARD_TEXT) is not None):
                shadow = _update_card_text('{}\n\n{}'.format(
                    spanish_row.get(BACK_PREFIX + CARD_KEYWORDS) or '',
                    spanish_row.get(BACK_PREFIX + CARD_TEXT)),
                                           lang='Spanish').strip()
            else:
                shadow = ''

            if shadow:
                shadow = '<p>{}</p>'.format(shadow.replace('\n', '</p><p>'))

            csv_row = {
                'id': None,
                'pack_id': row[CARD_SET_RINGSDB_CODE],
                'cycle': cycle,
                'cycle_id': None,
                'octngId': row[CARD_ID],
                'type_id': row[CARD_TYPE],
                'set': spanish_row.get(CARD_ENCOUNTER_SET),
                'set_id': None,
                'position': _handle_int(row[CARD_NUMBER]),
                'code': _spanishdb_code(row),
                'nombre': name,
                'nombreb': row[CARD_NAME],
                'quantity': quantity,
                'easy_mode': quantity - easy_mode,
                'tipo': SPANISH.get(row[CARD_TYPE]),
                'enfrentamiento': engagement,
                'amenaza': threat,
                'attack': _handle_int(row[CARD_ATTACK]),
                'defense': _handle_int(row[CARD_DEFENSE]),
                'health': _handle_int(row[CARD_HEALTH]),
                'mision': quest_points,
                'victory': victory_points,
                'traits': spanish_row.get(CARD_TRAITS),
                'text': text,
                'sombra': shadow
                }
            writer.writerow(csv_row)

    output_path = os.path.join(output_folder, 'cards.csv')
    with open(output_path, 'w', newline='', encoding='utf-8') as obj:
        obj.write(codecs.BOM_UTF8.decode('utf-8'))
        fieldnames = ['id', 'pack_id', 'cycle_id', 'type_id', 'sphere_id',
                      'position', 'code', 'name', 'traits', 'text', 'flavor',
                      'is_unique', 'cost', 'threat', 'willpower', 'attack',
                      'defense', 'health', 'victory', 'quest', 'quantity',
                      'deck_limit', 'illustrator', 'octgnid', 'date_creation',
                      'date_update', 'has_errata']
        writer = csv.DictWriter(obj, fieldnames=fieldnames)
        writer.writeheader()
        current_date = time.strftime('%d/%m/%Y').lstrip('0').replace('/0', '/')
        for row in data:
            if (row[CARD_TYPE] not in CARD_TYPES_PLAYER
                    and row[CARD_TYPE] != 'Rules'):
                continue

            spanish_row = TRANSLATIONS['Spanish'].get(row[CARD_ID], {}).copy()
            if row.get(CARD_DOUBLESIDE):
                spanish_row[CARD_NAME] = spanish_row.get(CARD_SIDE_B, '')
                for key in spanish_row.keys():
                    if key.startswith(BACK_PREFIX):
                        spanish_row[key.replace(BACK_PREFIX, '')] = (
                            spanish_row[key])

            if row[CARD_TYPE] in ('Contract', 'Treasure'):
                sphere = 'Neutral'
            else:
                sphere = row[CARD_SPHERE]

            if row[CARD_TYPE] == 'Hero':
                cost = None
                threat = _handle_int(row[CARD_COST])
            else:
                cost = _handle_int(row[CARD_COST])
                threat = None

            text = _update_card_text('{}\n\n{}'.format(
                spanish_row.get(CARD_KEYWORDS) or '',
                spanish_row.get(CARD_TEXT) or ''), lang='Spanish').strip()
            if (row[CARD_TYPE] == 'Rules' and
                    spanish_row.get(CARD_VICTORY) is not None):
                text = '{}\n\nPage {}'.format(text, spanish_row[CARD_VICTORY])

            if text:
                text = '<p>{}</p>'.format(text.replace('\n', '</p><p>'))

            if (row[CARD_TYPE] in CARD_TYPES_DOUBLESIDE_OPTIONAL and
                    spanish_row.get(BACK_PREFIX + CARD_TEXT)):
                text_back = _update_card_text('{}\n\n{}'.format(
                    spanish_row.get(BACK_PREFIX + CARD_KEYWORDS) or '',
                    spanish_row[BACK_PREFIX + CARD_TEXT]),
                                              lang='Spanish').strip()
                if (row[CARD_TYPE] == 'Rules' and
                        spanish_row.get(BACK_PREFIX + CARD_VICTORY)
                        is not None):
                    text_back = '{}\n\nPage {}'.format(
                        text_back, spanish_row[BACK_PREFIX + CARD_VICTORY])

                if text_back:
                    text_back = '<p>{}</p>'.format(
                        text_back.replace('\n', '</p><p>'))

                text = ('<p><b>Lado A.</b></p>\n{}\n<p><b>Lado B.</b></p>\n{}'
                        .format(text, text_back))

            flavour = _update_card_text(spanish_row.get(CARD_FLAVOUR) or '',
                                        lang='Spanish',
                                        skip_rules=True,
                                        fix_linebreaks=False).strip()
            if flavour:
                flavour = '<p>{}</p>'.format(flavour.replace('\n', '</p><p>'))

            if (row[CARD_TYPE] in CARD_TYPES_DOUBLESIDE_OPTIONAL and
                    spanish_row.get(BACK_PREFIX + CARD_FLAVOUR)):
                flavour_back = _update_card_text(
                    spanish_row[BACK_PREFIX + CARD_FLAVOUR], lang='Spanish',
                    skip_rules=True, fix_linebreaks=False).strip()
                if flavour_back:
                    flavour_back = '<p>{}</p>'.format(
                        flavour_back.replace('\n', '</p><p>'))

                flavour = (
                    '<p><b>Lado A.</b></p>\n{}\n<p><b>Lado B.</b></p>\n{}'
                    .format(flavour, flavour_back))

            if row[CARD_TYPE] == 'Rules':
                victory_points = None
            else:
                victory_points = _handle_int(spanish_row.get(CARD_VICTORY))

            quantity = (int(row[CARD_QUANTITY])
                        if _is_int(row[CARD_QUANTITY])
                        else 1)

            if row[CARD_TYPE] in CARD_TYPES_PLAYER_DECK:
                limit = re.search(r'limit .*([0-9]+) per deck',
                                  row[CARD_TEXT] or '',
                                  re.I)
                if limit:
                    limit = int(limit.groups()[0])
            else:
                limit = None

            csv_row = {
                'id': None,
                'pack_id': row[CARD_SET_RINGSDB_CODE],
                'cycle_id': None,
                'type_id': row[CARD_TYPE],
                'sphere_id': sphere,
                'position': _handle_int(row[CARD_NUMBER]),
                'code': _spanishdb_code(row),
                'name': spanish_row.get(CARD_NAME),
                'traits': spanish_row.get(CARD_TRAITS),
                'text': text,
                'flavor': flavour,
                'is_unique': int(row[CARD_UNIQUE] or 0),
                'cost': cost,
                'threat': threat,
                'willpower': _handle_int(row[CARD_WILLPOWER]),
                'attack': _handle_int(row[CARD_ATTACK]),
                'defense': _handle_int(row[CARD_DEFENSE]),
                'health': _handle_int(row[CARD_HEALTH]),
                'victory': victory_points,
                'quest': _handle_int(row[CARD_QUEST]),
                'quantity': quantity,
                'deck_limit': limit or quantity,
                'illustrator': row[CARD_ARTIST],
                'octgnid': row[CARD_ID],
                'date_creation': current_date,
                'date_update': current_date,
                'has_errata': 0
                }
            writer.writerow(csv_row)

    logging.info('[%s] ...Generating CSV files for the Spanish database (%ss)',
                 set_name, round(time.time() - timestamp, 3))


def _get_xml_property_value(row, name, card_type):
    """ Get Strange Eons xml property value for the given column name.
    """
    value = row[name]
    if value is None:
        value = ''

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


def translated_data(set_id, lang):
    """ Get card data with a few translated columns (only the needed ones).
    """
    res = []
    for row in DATA:
        if row[CARD_ID] is None:
            continue

        if row[CARD_SET] != set_id:
            continue

        row_copy = row.copy()
        if lang != 'English' and TRANSLATIONS[lang].get(row[CARD_ID]):
            row_copy[CARD_NAME] = TRANSLATIONS[lang][row[CARD_ID]][CARD_NAME]

        res.append(row_copy)

    return res


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
    root.set('icon', SETS[set_id][SET_COLLECTION_ICON] or '')
    root.set('copyright', SETS[set_id][SET_COPYRIGHT] or '')
    root.set('language', lang)
    cards = root.findall("./cards")[0]

    chosen_data = []
    for row in DATA:
        if row[CARD_ID] is None:
            continue

        if row[CARD_SET] != set_id:
            continue

        row_copy = row.copy()
        if lang != 'English' and TRANSLATIONS[lang].get(row[CARD_ID]):
            for key in TRANSLATED_COLUMNS:
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
                     CARD_ADVENTURE, CARD_ICON, CARD_BACK, CARD_VERSION):
            value = _get_xml_property_value(row, name, card_type)
            if value != '':
                properties.append((name, value))

        properties.append(('Set Name', set_name))
        properties.append(('Set Icon',
                           SETS[set_id][SET_COLLECTION_ICON] or ''))
        properties.append(('Set Copyright', SETS[set_id][SET_COPYRIGHT] or ''))

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
    if os.path.exists(image_path):
        for _, _, filenames in os.walk(image_path):
            for filename in filenames:
                if (len(filename.split('.')) < 2 or
                        len(filename.split('_')) < 3):
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
    if os.path.exists(image_path):
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
    if (conf['nobleed_300'][lang]
            or 'drivethrucards' in conf['outputs'][lang]
            or 'pdf' in conf['outputs'][lang]):
        root.set('png300Bleed', '1')

    if ('makeplayingcards' in conf['outputs'][lang]
            or 'mbprint' in conf['outputs'][lang]
            or 'genericpng' in conf['outputs'][lang]
            or 'genericpng_pdf' in conf['outputs'][lang]):
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

    artwork_path = os.path.join(conf['artwork_path'], set_id)
    images = _collect_artwork_images(conf, artwork_path)
    processed_images = _collect_artwork_images(
        conf, os.path.join(artwork_path, PROCESSED_ARTWORK_FOLDER))
    images = {**images, **processed_images}
    custom_images = _collect_custom_images(
        os.path.join(artwork_path, IMAGES_CUSTOM_FOLDER))
    common_custom_images = _collect_custom_images(
        os.path.join(conf['artwork_path'], IMAGES_CUSTOM_FOLDER))
    custom_images = {**common_custom_images, **custom_images}
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

    images_path = os.path.join(conf['artwork_path'], IMAGES_CUSTOM_FOLDER)
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

    images_path = os.path.join(conf['artwork_path'], set_id,
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

    artwork_path = os.path.join(conf['artwork_path'], set_id)
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

    if os.path.exists(MAKECARDS_FINISHED_PATH):
        os.remove(MAKECARDS_FINISHED_PATH)

    with zipfile.ZipFile(PROJECT_PATH, 'w') as zip_obj:
        for root, _, filenames in os.walk(PROJECT_FOLDER):
            for filename in filenames:
                zip_obj.write(os.path.join(root, filename))

    logging.info('...Creating a Strange Eons project archive (%ss)',
                 round(time.time() - timestamp, 3))


def get_skip_info(set_id, lang):
    """ Get skip information for the set and individual cards.
    """
    skip_ids = set()
    tree = ET.parse(os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id,
                                                                   lang)))
    root = tree.getroot()
    skip_set = root.attrib.get('skip') == '1'
    for card in root[0]:
        if card.attrib.get('skip') == '1':
            skip_ids.add(card.attrib['id'])

    return skip_set, skip_ids


def get_actual_sets():
    """ Get actual sets from the Strange Eons project.
    """
    res = set()
    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith(XML_ZIP_PATH)
                    and f.split('.')[-1] == 'xml']
        for filename in filelist:
            parts = filename.split('/')[-1].split('.')
            if len(parts) != 3:
                continue

            res.add((parts[0], parts[1]))

    return res


def _run_cmd(cmd):
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, shell=True, check=True)
        return res
    except subprocess.CalledProcessError as exc:
        raise RuntimeError('Command "{}" returned error with code {}: {}'
                           .format(cmd, exc.returncode, exc.output))


def generate_png300_nobleed(conf, set_id, set_name, lang, skip_ids):  # pylint: disable=R0914
    """ Generate PNG 300 dpi images without bleed margins.
    """
    logging.info('[%s, %s] Generating PNG 300 dpi images without bleed '
                 'margins...', set_name, lang)
    timestamp = time.time()

    temp_path = os.path.join(
        TEMP_ROOT_PATH, 'generate_png300_nobleed.{}.{}'.format(set_id,
                                                               lang))
    create_folder(temp_path)
    clear_folder(temp_path)

    temp_path2 = os.path.join(
        TEMP_ROOT_PATH, 'generate_png300_nobleed2.{}.{}'.format(set_id,
                                                                lang))
    create_folder(temp_path2)
    clear_folder(temp_path2)

    input_cnt = 0
    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  PNG300BLEED))
                    and f.split('.')[-1] == 'png'
                    and f.split('.')[-2] == lang
                    and f.split('.')[-3] == set_id]
        for filename in filelist:
            input_cnt += 1
            output_filename = _update_zip_filename(filename)
            with zip_obj.open(filename) as zip_file:
                with open(os.path.join(temp_path, output_filename),
                          'wb') as output_file:
                    shutil.copyfileobj(zip_file, output_file)

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-cut-bleed-margins-folder',
        temp_path.replace('\\', '\\\\'),
        temp_path2.replace('\\', '\\\\'))
    res = _run_cmd(cmd)
    logging.info('[%s, %s] %s', set_name, lang, res)

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < PNG_300_MIN_SIZE:
                raise GIMPError('GIMP failed for {}'.format(
                    os.path.join(temp_path2, filename)))

        break

    if output_cnt != input_cnt:
        raise GIMPError('Wrong number of output files: {} instead of {}'
                        .format(output_cnt, input_cnt))

    output_path = os.path.join(IMAGES_EONS_PATH, PNG300NOBLEED,
                               '{}.{}'.format(set_id, lang))
    create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)

    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            shutil.move(os.path.join(temp_path2, filename),
                        os.path.join(output_path, filename))

        break

    delete_folder(temp_path)
    delete_folder(temp_path2)

    logging.info('[%s, %s] ...Generating PNG 300 dpi images without bleed '
                 'margins (%ss)', set_name, lang,
                 round(time.time() - timestamp, 3))


def generate_png800_nobleed(conf, set_id, set_name, lang, skip_ids):  # pylint: disable=R0914
    """ Generate PNG 800 dpi images without bleed margins.

    NOT USED AT THE MOMENT
    """
    logging.info('[%s, %s] Generating PNG 800 dpi images without bleed '
                 'margins...', set_name, lang)
    timestamp = time.time()

    temp_path = os.path.join(
        TEMP_ROOT_PATH, 'generate_png800_nobleed.{}.{}'.format(set_id,
                                                               lang))
    create_folder(temp_path)
    clear_folder(temp_path)

    temp_path2 = os.path.join(
        TEMP_ROOT_PATH, 'generate_png800_nobleed2.{}.{}'.format(set_id,
                                                                lang))
    create_folder(temp_path2)
    clear_folder(temp_path2)

    input_cnt = 0
    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  PNG800BLEED))
                    and f.split('.')[-1] == 'png'
                    and f.split('.')[-2] == lang
                    and f.split('.')[-3] == set_id]
        for filename in filelist:
            input_cnt += 1
            output_filename = _update_zip_filename(filename)
            with zip_obj.open(filename) as zip_file:
                with open(os.path.join(temp_path, output_filename),
                          'wb') as output_file:
                    shutil.copyfileobj(zip_file, output_file)

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-cut-bleed-margins-folder',
        temp_path.replace('\\', '\\\\'),
        temp_path2.replace('\\', '\\\\'))
    res = _run_cmd(cmd)
    logging.info('[%s, %s] %s', set_name, lang, res)

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < PNG_800_MIN_SIZE:
                raise GIMPError('GIMP failed for {}'.format(
                    os.path.join(temp_path2, filename)))

        break

    if output_cnt != input_cnt:
        raise GIMPError('Wrong number of output files: {} instead of {}'
                        .format(output_cnt, input_cnt))

    output_path = os.path.join(IMAGES_EONS_PATH, PNG800NOBLEED,
                               '{}.{}'.format(set_id, lang))
    create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)

    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            shutil.move(os.path.join(temp_path2, filename),
                        os.path.join(output_path, filename))

        break

    delete_folder(temp_path)
    delete_folder(temp_path2)

    logging.info('[%s, %s] ...Generating PNG 800 dpi images without bleed '
                 'margins (%ss)', set_name, lang,
                 round(time.time() - timestamp, 3))


def generate_png300_db(conf, set_id, set_name, lang, skip_ids):  # pylint: disable=R0914
    """ Generate images for all DB outputs.
    """
    logging.info('[%s, %s] Generating images for all DB outputs...',
                 set_name, lang)
    timestamp = time.time()

    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_png300_db.{}.{}'.format(set_id, lang))
    create_folder(temp_path)
    clear_folder(temp_path)

    temp_path2 = os.path.join(TEMP_ROOT_PATH,
                              'generate_png300_db2.{}.{}'.format(set_id, lang))
    create_folder(temp_path2)
    clear_folder(temp_path2)

    input_path = os.path.join(IMAGES_EONS_PATH, PNG300NOBLEED,
                              '{}.{}'.format(set_id, lang))
    known_keys = set()
    input_cnt = 0
    for _, _, filenames in os.walk(input_path):
        filenames = sorted(filenames)
        for filename in filenames:
            if filename.split('.')[-1] != 'png':
                continue

            key = filename[50:88]
            if key not in known_keys:
                input_cnt += 1
                known_keys.add(key)
                shutil.copyfile(os.path.join(input_path, filename),
                                os.path.join(temp_path, filename))

        break

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-db-output-folder',
        temp_path.replace('\\', '\\\\'),
        temp_path2.replace('\\', '\\\\'))
    res = _run_cmd(cmd)
    logging.info('[%s, %s] %s', set_name, lang, res)

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < PNG_300_MIN_SIZE:
                raise GIMPError('GIMP failed for {}'.format(
                    os.path.join(temp_path2, filename)))

        break

    if output_cnt != input_cnt:
        raise GIMPError('Wrong number of output files: {} instead of {}'
                        .format(output_cnt, input_cnt))

    output_path = os.path.join(IMAGES_EONS_PATH, PNG300DB,
                               '{}.{}'.format(set_id, lang))
    create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)

    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            shutil.move(os.path.join(temp_path2, filename),
                        os.path.join(output_path, filename))

        break

    delete_folder(temp_path)
    delete_folder(temp_path2)

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
    create_folder(output_path)
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


def generate_png300_rules_pdf(set_id, set_name, lang, skip_ids, card_data):  # pylint: disable=R0914
    """ Generate images for Rules PDF outputs.
    """
    logging.info('[%s, %s] Generating images for Rules PDF outputs...',
                 set_name, lang)
    timestamp = time.time()

    output_path = os.path.join(IMAGES_EONS_PATH, PNG300RULES,
                               '{}.{}'.format(set_id, lang))
    create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)

    input_path = os.path.join(IMAGES_EONS_PATH, PNG300NOBLEED,
                              '{}.{}'.format(set_id, lang))
    known_keys = set()
    rules_cards = {c[CARD_ID]:c for c in card_data
                   if c[CARD_SET] == set_id and
                   c[CARD_TYPE] == 'Rules' and c[CARD_SPHERE] != 'Back'}
    for _, _, filenames in os.walk(input_path):
        filenames = sorted(filenames)
        for filename in filenames:
            if filename.split('.')[-1] != 'png':
                continue

            key = filename[50:88]
            if key in known_keys:
                continue

            known_keys.add(key)
            card_id = filename[50:86]
            if card_id not in rules_cards:
                continue

            card = rules_cards[card_id]
            side = filename[87]
            if (side == '1' and card[CARD_TEXT] is None and
                    card[CARD_VICTORY] is None):
                continue

            if (side == '2' and card[BACK_PREFIX + CARD_TEXT] is None and
                    card[BACK_PREFIX + CARD_VICTORY] is None):
                continue

            shutil.copyfile(os.path.join(input_path, filename),
                            os.path.join(output_path, filename))

        break

    logging.info('[%s, %s] ...Generating images for Rules PDF outputs '
                 '(%ss)', set_name, lang, round(time.time() - timestamp, 3))


def generate_png300_pdf(conf, set_id, set_name, lang, skip_ids):  # pylint: disable=R0912,R0914,R0915
    """ Generate images for PDF outputs.
    """
    logging.info('[%s, %s] Generating images for PDF outputs...',
                 set_name, lang)
    timestamp = time.time()

    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_png300_pdf.{}.{}'.format(set_id, lang))
    create_folder(temp_path)
    clear_folder(temp_path)

    temp_path2 = os.path.join(TEMP_ROOT_PATH,
                              'generate_png300_pdf2.{}.{}'.format(set_id,
                                                                  lang))
    create_folder(temp_path2)
    clear_folder(temp_path2)

    input_cnt = 0
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
                input_cnt += 1
                with zip_obj.open(filename) as zip_file:
                    with open(os.path.join(temp_path, output_filename),
                              'wb') as output_file:
                        shutil.copyfileobj(zip_file, output_file)

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-pdf-back-folder',
        temp_path.replace('\\', '\\\\'),
        temp_path2.replace('\\', '\\\\'))
    res = _run_cmd(cmd)
    logging.info('[%s, %s] %s', set_name, lang, res)

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < PNG_300_MIN_SIZE:
                raise GIMPError('GIMP failed for {}'.format(
                    os.path.join(temp_path2, filename)))

        break

    if output_cnt != input_cnt:
        raise GIMPError('Wrong number of output files: {} instead of {}'
                        .format(output_cnt, input_cnt))

    clear_folder(temp_path)

    temp_path3 = os.path.join(TEMP_ROOT_PATH,
                              'generate_png300_pdf3.{}.{}'.format(set_id,
                                                                  lang))
    create_folder(temp_path3)
    clear_folder(temp_path3)

    input_cnt = 0
    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  PNG300BLEED))
                    and f.split('.')[-1] == 'png'
                    and f.split('.')[-2] == lang
                    and f.split('.')[-3] == set_id]
        for filename in filelist:
            output_filename = _update_zip_filename(filename)
            if output_filename.endswith('-1.png'):
                input_cnt += 1
                with zip_obj.open(filename) as zip_file:
                    with open(os.path.join(temp_path, output_filename),
                              'wb') as output_file:
                        shutil.copyfileobj(zip_file, output_file)

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-pdf-front-folder',
        temp_path.replace('\\', '\\\\'),
        temp_path3.replace('\\', '\\\\'))
    res = _run_cmd(cmd)
    logging.info('[%s, %s] %s', set_name, lang, res)

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path3):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path3, filename)
                               ) < PNG_300_MIN_SIZE:
                raise GIMPError('GIMP failed for {}'.format(
                    os.path.join(temp_path3, filename)))

        break

    if output_cnt != input_cnt:
        raise GIMPError('Wrong number of output files: {} instead of {}'
                        .format(output_cnt, input_cnt))

    output_path = os.path.join(IMAGES_EONS_PATH, PNG300PDF,
                               '{}.{}'.format(set_id, lang))
    create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)

    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            shutil.move(os.path.join(temp_path2, filename),
                        os.path.join(output_path, filename))

        break

    for _, _, filenames in os.walk(temp_path3):
        for filename in filenames:
            shutil.move(os.path.join(temp_path3, filename),
                        os.path.join(output_path, filename))

        break

    delete_folder(temp_path)
    delete_folder(temp_path2)
    delete_folder(temp_path3)

    logging.info('[%s, %s] ...Generating images for PDF outputs (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def generate_png800_pdf(conf, set_id, set_name, lang, skip_ids):  # pylint: disable=R0912,R0914,R0915
    """ Generate images for generic PNG PDF outputs.
    """
    logging.info('[%s, %s] Generating images for generic PNG PDF outputs...',
                 set_name, lang)
    timestamp = time.time()

    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_png800_pdf.{}.{}'.format(set_id, lang))
    create_folder(temp_path)
    clear_folder(temp_path)

    temp_path2 = os.path.join(TEMP_ROOT_PATH,
                              'generate_png800_pdf2.{}.{}'.format(set_id,
                                                                  lang))
    create_folder(temp_path2)
    clear_folder(temp_path2)

    input_cnt = 0
    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  PNG800BLEED))
                    and f.split('.')[-1] == 'png'
                    and f.split('.')[-2] == lang
                    and f.split('.')[-3] == set_id]
        for filename in filelist:
            output_filename = _update_zip_filename(filename)
            if output_filename.endswith('-2.png'):
                input_cnt += 1
                with zip_obj.open(filename) as zip_file:
                    with open(os.path.join(temp_path, output_filename),
                              'wb') as output_file:
                        shutil.copyfileobj(zip_file, output_file)

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-pdf-back-folder',
        temp_path.replace('\\', '\\\\'),
        temp_path2.replace('\\', '\\\\'))
    res = _run_cmd(cmd)
    logging.info('[%s, %s] %s', set_name, lang, res)

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < PNG_800_MIN_SIZE:
                raise GIMPError('GIMP failed for {}'.format(
                    os.path.join(temp_path2, filename)))

        break

    if output_cnt != input_cnt:
        raise GIMPError('Wrong number of output files: {} instead of {}'
                        .format(output_cnt, input_cnt))

    clear_folder(temp_path)

    temp_path3 = os.path.join(TEMP_ROOT_PATH,
                              'generate_png800_pdf3.{}.{}'.format(set_id,
                                                                  lang))
    create_folder(temp_path3)
    clear_folder(temp_path3)

    input_cnt = 0
    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  PNG800BLEED))
                    and f.split('.')[-1] == 'png'
                    and f.split('.')[-2] == lang
                    and f.split('.')[-3] == set_id]
        for filename in filelist:
            output_filename = _update_zip_filename(filename)
            if output_filename.endswith('-1.png'):
                input_cnt += 1
                with zip_obj.open(filename) as zip_file:
                    with open(os.path.join(temp_path, output_filename),
                              'wb') as output_file:
                        shutil.copyfileobj(zip_file, output_file)

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-pdf-front-folder',
        temp_path.replace('\\', '\\\\'),
        temp_path3.replace('\\', '\\\\'))
    res = _run_cmd(cmd)
    logging.info('[%s, %s] %s', set_name, lang, res)

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path3):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path3, filename)
                               ) < PNG_800_MIN_SIZE:
                raise GIMPError('GIMP failed for {}'.format(
                    os.path.join(temp_path3, filename)))

        break

    if output_cnt != input_cnt:
        raise GIMPError('Wrong number of output files: {} instead of {}'
                        .format(output_cnt, input_cnt))

    output_path = os.path.join(IMAGES_EONS_PATH, PNG800PDF,
                               '{}.{}'.format(set_id, lang))
    create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)

    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            shutil.move(os.path.join(temp_path2, filename),
                        os.path.join(output_path, filename))

        break

    for _, _, filenames in os.walk(temp_path3):
        for filename in filenames:
            shutil.move(os.path.join(temp_path3, filename),
                        os.path.join(output_path, filename))

        break

    delete_folder(temp_path)
    delete_folder(temp_path2)
    delete_folder(temp_path3)

    logging.info('[%s, %s] ...Generating images for generic PNG PDF outputs '
                 '(%ss)', set_name, lang, round(time.time() - timestamp, 3))


def generate_png800_bleedmpc(conf, set_id, set_name, lang, skip_ids):  # pylint: disable=R0914
    """ Generate images for MakePlayingCards outputs.
    """
    logging.info('[%s, %s] Generating images for MakePlayingCards outputs...',
                 set_name, lang)
    timestamp = time.time()

    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_png800_bleedmpc.{}.{}'.format(set_id,
                                                                     lang))
    create_folder(temp_path)
    clear_folder(temp_path)

    temp_path2 = os.path.join(TEMP_ROOT_PATH,
                              'generate_png800_bleedmpc2.{}.{}'.format(set_id,
                                                                       lang))
    create_folder(temp_path2)
    clear_folder(temp_path2)

    input_cnt = 0
    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  PNG800BLEED))
                    and f.split('.')[-1] == 'png'
                    and f.split('.')[-2] == lang
                    and f.split('.')[-3] == set_id]
        for filename in filelist:
            input_cnt += 1
            output_filename = _update_zip_filename(filename)
            with zip_obj.open(filename) as zip_file:
                with open(os.path.join(temp_path, output_filename),
                          'wb') as output_file:
                    shutil.copyfileobj(zip_file, output_file)

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-makeplayingcards-folder',
        temp_path.replace('\\', '\\\\'),
        temp_path2.replace('\\', '\\\\'))
    res = _run_cmd(cmd)
    logging.info('[%s, %s] %s', set_name, lang, res)

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < PNG_800_MIN_SIZE:
                raise GIMPError('GIMP failed for {}'.format(
                    os.path.join(temp_path2, filename)))

        break

    if output_cnt != input_cnt:
        raise GIMPError('Wrong number of output files: {} instead of {}'
                        .format(output_cnt, input_cnt))

    output_path = os.path.join(IMAGES_EONS_PATH, PNG800BLEEDMPC,
                               '{}.{}'.format(set_id, lang))
    create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)

    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            shutil.move(os.path.join(temp_path2, filename),
                        os.path.join(output_path, filename))

        break

    delete_folder(temp_path)
    delete_folder(temp_path2)

    logging.info('[%s, %s] ...Generating images for MakePlayingCards outputs '
                 '(%ss)', set_name, lang, round(time.time() - timestamp, 3))


def generate_jpg300_bleeddtc(conf, set_id, set_name, lang, skip_ids):  # pylint: disable=R0914
    """ Generate images for DriveThruCards outputs.
    """
    logging.info('[%s, %s] Generating images for DriveThruCards outputs...',
                 set_name, lang)
    timestamp = time.time()

    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_jpg300_bleeddtc.{}.{}'.format(set_id,
                                                                     lang))
    create_folder(temp_path)
    clear_folder(temp_path)

    temp_path2 = os.path.join(TEMP_ROOT_PATH,
                              'generate_jpg300_bleeddtc2.{}.{}'.format(set_id,
                                                                       lang))
    create_folder(temp_path2)
    clear_folder(temp_path2)

    input_cnt = 0
    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  PNG300BLEED))
                    and f.split('.')[-1] == 'png'
                    and f.split('.')[-2] == lang
                    and f.split('.')[-3] == set_id]
        for filename in filelist:
            input_cnt += 1
            output_filename = _update_zip_filename(filename)
            with zip_obj.open(filename) as zip_file:
                with open(os.path.join(temp_path, output_filename),
                          'wb') as output_file:
                    shutil.copyfileobj(zip_file, output_file)

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-drivethrucards-jpg-folder',
        temp_path.replace('\\', '\\\\'),
        temp_path2.replace('\\', '\\\\'))
    res = _run_cmd(cmd)
    logging.info('[%s, %s] %s', set_name, lang, res)

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < JPG_300_MIN_SIZE:
                raise GIMPError('GIMP failed for {}'.format(
                    os.path.join(temp_path2, filename)))

        break

    if output_cnt != input_cnt:
        raise GIMPError('Wrong number of output files: {} instead of {}'
                        .format(output_cnt, input_cnt))

    _make_cmyk(conf, temp_path2, JPG_300CMYK_MIN_SIZE)

    output_path = os.path.join(IMAGES_EONS_PATH,
                               JPG300BLEEDDTC,
                               '{}.{}'.format(set_id, lang))
    create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)

    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            shutil.move(os.path.join(temp_path2, filename),
                        os.path.join(output_path, filename))

        break

    delete_folder(temp_path)
    delete_folder(temp_path2)

    logging.info('[%s, %s] ...Generating images for DriveThruCards outputs '
                 '(%ss)', set_name, lang, round(time.time() - timestamp, 3))


def generate_jpg800_bleedmbprint(conf, set_id, set_name, lang, skip_ids):  # pylint: disable=R0914
    """ Generate images for MBPrint outputs.
    """
    logging.info('[%s, %s] Generating images for MBPrint outputs...',
                 set_name, lang)
    timestamp = time.time()

    temp_path = os.path.join(
        TEMP_ROOT_PATH, 'generate_jpg800_bleedmbprint.{}.{}'.format(set_id,
                                                                    lang))
    create_folder(temp_path)
    clear_folder(temp_path)

    temp_path2 = os.path.join(
        TEMP_ROOT_PATH, 'generate_jpg800_bleedmbprint2.{}.{}'.format(set_id,
                                                                     lang))
    create_folder(temp_path2)
    clear_folder(temp_path2)

    input_cnt = 0
    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  PNG800BLEED))
                    and f.split('.')[-1] == 'png'
                    and f.split('.')[-2] == lang
                    and f.split('.')[-3] == set_id]
        for filename in filelist:
            input_cnt += 1
            output_filename = _update_zip_filename(filename)
            with zip_obj.open(filename) as zip_file:
                with open(os.path.join(temp_path, output_filename),
                          'wb') as output_file:
                    shutil.copyfileobj(zip_file, output_file)

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-mbprint-jpg-folder',
        temp_path.replace('\\', '\\\\'),
        temp_path2.replace('\\', '\\\\'))
    res = _run_cmd(cmd)
    logging.info('[%s, %s] %s', set_name, lang, res)

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < JPG_800_MIN_SIZE:
                raise GIMPError('GIMP failed for {}'.format(
                    os.path.join(temp_path2, filename)))

        break

    if output_cnt != input_cnt:
        raise GIMPError('Wrong number of output files: {} instead of {}'
                        .format(output_cnt, input_cnt))

    _make_cmyk(conf, temp_path2, JPG_800CMYK_MIN_SIZE)

    output_path = os.path.join(IMAGES_EONS_PATH,
                               JPG800BLEEDMBPRINT,
                               '{}.{}'.format(set_id, lang))
    create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)

    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            shutil.move(os.path.join(temp_path2, filename),
                        os.path.join(output_path, filename))

        break

    delete_folder(temp_path)
    delete_folder(temp_path2)

    logging.info('[%s, %s] ...Generating images for MBPrint outputs '
                 '(%ss)', set_name, lang, round(time.time() - timestamp, 3))


def generate_png800_bleedgeneric(conf, set_id, set_name, lang, skip_ids):  # pylint: disable=R0914
    """ Generate generic PNG images.
    """
    logging.info('[%s, %s] Generating generic PNG images...', set_name, lang)
    timestamp = time.time()

    temp_path = os.path.join(
        TEMP_ROOT_PATH, 'generate_png800_bleedgeneric.{}.{}'.format(set_id,
                                                                    lang))
    create_folder(temp_path)
    clear_folder(temp_path)

    temp_path2 = os.path.join(
        TEMP_ROOT_PATH, 'generate_png800_bleedgeneric2.{}.{}'.format(set_id,
                                                                     lang))
    create_folder(temp_path2)
    clear_folder(temp_path2)

    input_cnt = 0
    with zipfile.ZipFile(PROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  PNG800BLEED))
                    and f.split('.')[-1] == 'png'
                    and f.split('.')[-2] == lang
                    and f.split('.')[-3] == set_id]
        for filename in filelist:
            input_cnt += 1
            output_filename = _update_zip_filename(filename)
            with zip_obj.open(filename) as zip_file:
                with open(os.path.join(temp_path, output_filename),
                          'wb') as output_file:
                    shutil.copyfileobj(zip_file, output_file)

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-generic-png-folder',
        temp_path.replace('\\', '\\\\'),
        temp_path2.replace('\\', '\\\\'))
    res = _run_cmd(cmd)
    logging.info('[%s, %s] %s', set_name, lang, res)

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < PNG_800_MIN_SIZE:
                raise GIMPError('GIMP failed for {}'.format(
                    os.path.join(temp_path2, filename)))

        break

    if output_cnt != input_cnt:
        raise GIMPError('Wrong number of output files: {} instead of {}'
                        .format(output_cnt, input_cnt))

    output_path = os.path.join(IMAGES_EONS_PATH, PNG800BLEEDGENERIC,
                               '{}.{}'.format(set_id, lang))
    create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)

    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            shutil.move(os.path.join(temp_path2, filename),
                        os.path.join(output_path, filename))

        break

    delete_folder(temp_path)
    delete_folder(temp_path2)

    logging.info('[%s, %s] ...Generating generic PNG images (%ss)', set_name,
                 lang, round(time.time() - timestamp, 3))


def _make_low_quality(conf, input_path):
    """ Make low quality 600x429 JPG images from PNG inputs.
    """
    input_cnt = 0
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            input_cnt += 1

        break

    if input_cnt:
        cmd = MAGICK_COMMAND_LOW.format(conf['magick_path'], input_path,
                                        os.sep)
        res = _run_cmd(cmd)
        logging.info(res)

    output_cnt = 0
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(input_path, filename)
                               ) < JPG_PREVIEW_MIN_SIZE:
                raise ImageMagickError('ImageMagick failed for {}'.format(
                    os.path.join(input_path, filename)))

        break

    if output_cnt != input_cnt * 2:
        raise ImageMagickError('Wrong number of output files: {} instead of {}'
                               .format(output_cnt, input_cnt))


def full_card_dict():
    """ Get card dictionary with both spreadsheet and external data.
    """
    card_dict = {}
    for _, _, filenames in os.walk(URL_CACHE_PATH):
        for filename in filenames:
            if filename.endswith('.cache'):
                data = load_external_xml(re.sub(r'\.cache$', '', filename))
                card_dict.update({r[CARD_ID]:r for r in data})

        break

    card_dict.update({r[CARD_ID]:r for r in DATA})
    return card_dict


def _generate_tts_sheets(deck_path, output_path, image_path, card_dict,  # pylint: disable=R0912,R0914
                         scratch):
    """ Generate TTS sheets for the deck.
    """
    deck_name = re.sub(r'\.o8d$', '', os.path.split(deck_path)[-1])
    is_player = deck_name.startswith('Player-')
    scratch = ' (Scratch)' if scratch else ''

    tree = ET.parse(deck_path)
    root = tree.getroot()
    cards = {'portrait': {'front_player': [],
                          'front_encounter': [],
                          'front_custom': [],
                          'back_custom': []},
             'landscape': {'front_player': [],
                           'front_encounter': [],
                           'front_custom': [],
                           'back_custom': []}}
    for section in root:
        for card_element in section:
            card_id = card_element.attrib.get('id')
            if card_id not in card_dict:
                logging.error('Card %s not found in the card list (deck "%s")'
                              '%s', card_id, deck_name, scratch)
                continue

            card_path = os.path.join(image_path, '{}.png'.format(card_id))
            if not os.path.exists(card_path):
                logging.error(
                    'Card %s not found in the image cache (deck "%s")%s',
                    card_id, deck_name, scratch)
                continue

            quantity = card_element.attrib.get('qty') if not is_player else 1
            if card_dict[card_id][CARD_TYPE] in CARD_TYPES_LANDSCAPE:
                orientation = 'landscape'
            else:
                orientation = 'portrait'

            back_path = os.path.join(image_path, '{}-2.png'.format(card_id))
            if os.path.exists(back_path):
                for _ in range(int(quantity)):
                    cards[orientation]['front_custom'].append(
                        {'id': card_id, 'path': card_path})
                    cards[orientation]['back_custom'].append(
                        {'id': card_id, 'path': back_path})
            elif ((card_dict[card_id][CARD_TYPE] in CARD_TYPES_PLAYER and
                   'Encounter' not in (card_dict[card_id][CARD_KEYWORDS] or ''
                                      ).replace('. ', '.').split('.') and
                   card_dict[card_id][CARD_BACK] != 'Encounter') or
                  card_dict[card_id][CARD_BACK] == 'Player'):
                for _ in range(int(quantity)):
                    cards[orientation]['front_player'].append(
                        {'id': card_id, 'path': card_path})
            else:
                for _ in range(int(quantity)):
                    cards[orientation]['front_encounter'].append(
                        {'id': card_id, 'path': card_path})

    cnt = 0
    for orientation in ('portrait', 'landscape'):
        for side in ('front_player', 'front_encounter', 'front_custom',
                     'back_custom'):
            chunks = [
                cards[orientation][side][
                    i * TTS_SHEET_SIZE:(i + 1) * TTS_SHEET_SIZE]
                for i in range(
                    (len(cards[orientation][side]) + TTS_SHEET_SIZE - 1) //
                    TTS_SHEET_SIZE)]
            total_chunks = len(chunks)
            for i, chunk in enumerate(chunks):
                num = len(chunk)
                rows = math.ceil(num / TTS_COLUMNS)
                name = '{}_{}_{}_{}_{}_{}_{}_{}'.format(
                    deck_name, orientation, side, TTS_COLUMNS, rows, num,
                    i + 1, total_chunks)
                cnt += 1
                shutil.copyfile(
                    os.path.join(IMAGES_OTHER_PATH, 'tts_template.jpg'),
                    os.path.join(output_path, '{}.jpg'.format(name)))
                with open(os.path.join(output_path, '{}.json'.format(name)),
                          'w') as fobj:
                    res = json.dumps(chunk, indent=4)
                    fobj.write(res)

    return cnt


def generate_tts(conf, set_id, set_name, lang, card_dict, scratch):  # pylint: disable=R0913,R0914
    """ Generate TTS outputs.
    """
    logging.info('[%s, %s] Generating TTS outputs...', set_name, lang)
    timestamp = time.time()

    output_path = os.path.join(OUTPUT_TTS_PATH, '{}.{}'.format(
        escape_filename(set_name), lang))
    create_folder(output_path)
    clear_folder(output_path)

    decks_path = os.path.join(OUTPUT_OCTGN_DECKS_PATH,
                              escape_filename(set_name))
    image_path = os.path.join(IMAGES_TTS_PATH, lang)
    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_tts.{}.{}'.format(set_id, lang))
    create_folder(temp_path)
    clear_folder(temp_path)

    input_cnt = 0
    for _, _, filenames in os.walk(decks_path):
        for filename in filenames:
            cnt = _generate_tts_sheets(os.path.join(decks_path, filename),
                                       temp_path, image_path, card_dict,
                                       scratch)
            input_cnt += cnt

        break

    cmd = GIMP_COMMAND.format(
        conf['gimp_console_path'],
        'python-prepare-tts-folder',
        temp_path.replace('\\', '\\\\'),
        output_path.replace('\\', '\\\\'))
    res = _run_cmd(cmd)
    logging.info('[%s, %s] %s', set_name, lang, res)

    output_cnt = 0
    for _, _, filenames in os.walk(output_path):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(output_path, filename)
                               ) < JPG_300_MIN_SIZE:
                raise GIMPError('GIMP failed for {}'.format(
                    os.path.join(output_path, filename)))

        break

    if output_cnt != input_cnt:
        raise GIMPError('Wrong number of output files: {} instead of {}'
                        .format(output_cnt, input_cnt))

    delete_folder(temp_path)

    logging.info('[%s, %s] ...Generating TTS outputs (%ss)', set_name, lang,
                 round(time.time() - timestamp, 3))


def generate_db(conf, set_id, set_name, lang, card_data):  # pylint: disable=R0912,R0914,R0915
    """ Generate DB, Preview and RingsDB image outputs.
    """
    logging.info('[%s, %s] Generating DB, Preview and RingsDB image '
                 'outputs...', set_name, lang)
    timestamp = time.time()

    input_path = os.path.join(IMAGES_EONS_PATH, PNG300DB,
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_DB_PATH, '{}.{}'.format(
        escape_filename(set_name), lang))

    known_filenames = set()
    for _, _, filenames in os.walk(input_path):
        if not filenames:
            logging.error('[%s, %s] No cards found', set_name, lang)
            break

        create_folder(output_path)
        clear_folder(output_path)
        filenames = sorted(filenames)
        for filename in filenames:
            if filename.split('.')[-1] != 'png':
                continue

            output_filename = '{}-{}----{}{}{}'.format(
                filename[:3],
                re.sub('-+$', '', filename[8:50]),
                filename[50:86],
                re.sub('-1$', '', filename[86:88]),
                filename[88:])
            if output_filename not in known_filenames:
                known_filenames.add(output_filename)
                shutil.copyfile(os.path.join(input_path, filename),
                                os.path.join(output_path, output_filename))

        break

    if 'tts' in conf['outputs'][lang] and known_filenames:
        tts_path = os.path.join(IMAGES_TTS_PATH, lang)
        create_folder(tts_path)
        for _, _, filenames in os.walk(output_path):
            for filename in filenames:
                shutil.copyfile(
                    os.path.join(output_path, filename),
                    os.path.join(tts_path, filename.split('----')[1]))

            break

    empty_rules_backs = {
        row[CARD_ID] for row in card_data
        if row[CARD_SET] == set_id and
        row[CARD_TYPE] == 'Rules' and
        row[BACK_PREFIX + CARD_TEXT] is None and
        row[BACK_PREFIX + CARD_VICTORY] is None}

    if known_filenames:
        preview_output_path = os.path.join(
            OUTPUT_PREVIEW_IMAGES_PATH, '{}.{}'.format(
                escape_filename(set_name), lang))
        create_folder(preview_output_path)
        clear_folder(preview_output_path)

        temp_path = os.path.join(TEMP_ROOT_PATH,
                                 'generate_db.{}.{}'.format(set_id, lang))
        create_folder(temp_path)
        clear_folder(temp_path)
        for _, _, filenames in os.walk(output_path):
            for filename in filenames:
                if (filename.endswith('-2.png') and '----' in filename and
                        filename.split('----')[1][:36] in empty_rules_backs):
                    continue

                shutil.copyfile(os.path.join(output_path, filename),
                                os.path.join(temp_path, filename))

            break

        _make_low_quality(conf, temp_path)

        for _, _, filenames in os.walk(temp_path):
            for filename in filenames:
                if filename.split('.')[-1] != 'jpg':
                    continue

                if filename.endswith('-2.jpg'):
                    output_filename = filename.split('----')[0] + '-2.jpg'
                else:
                    output_filename = filename.split('----')[0] + '.jpg'

                shutil.copyfile(os.path.join(temp_path, filename),
                                os.path.join(preview_output_path,
                                             output_filename))

            break

        delete_folder(temp_path)

    if lang == 'English':
        cards = {}
        for row in card_data:
            if row[CARD_SET] == set_id and _needed_for_ringsdb(row):
                card_number = str(_handle_int(row[CARD_NUMBER])).zfill(3)
                cards[card_number] = _ringsdb_code(row)

        pairs = []
        if cards and known_filenames:
            for _, _, filenames in os.walk(output_path):
                for filename in filenames:
                    card_number = filename[:3]
                    if card_number in cards:
                        suffix = '-2' if filename.endswith('-2.png') else ''
                        pairs.append((
                            filename,
                            '{}{}.png'.format(cards[card_number], suffix)))

                break

        if pairs:
            ringsdb_output_path = os.path.join(
                OUTPUT_RINGSDB_IMAGES_PATH, '{}.{}'.format(
                    escape_filename(set_name), lang))
            create_folder(ringsdb_output_path)
            clear_folder(ringsdb_output_path)
            for source_filename, target_filename in pairs:
                shutil.copyfile(os.path.join(output_path, source_filename),
                                os.path.join(ringsdb_output_path,
                                             target_filename))
    elif lang == 'French':  # pylint: disable=R1702
        cards = {}
        for row in card_data:
            if row[CARD_SET] == set_id and _needed_for_frenchdb(row):
                card_number = str(_handle_int(row[CARD_NUMBER])).zfill(3)
                cards[card_number] = row[CARD_NUMBER]

        pairs = []
        if cards and known_filenames:
            for _, _, filenames in os.walk(output_path):
                for filename in filenames:
                    card_number = filename[:3]
                    if card_number in cards:
                        if filename.endswith('-2.png'):
                            suffix = 'B'
                        elif os.path.exists(
                                os.path.join(output_path,
                                             re.sub(r'\.png$', '-2.png', filename))):
                            suffix = 'A'
                        else:
                            suffix = ''
                        pairs.append((
                            filename,
                            '{}{}.png'.format(cards[card_number], suffix)))

                break

        if pairs:
            frenchdb_output_path = os.path.join(
                OUTPUT_FRENCHDB_IMAGES_PATH, '{}.{}'.format(
                    escape_filename(set_name), lang))
            create_folder(frenchdb_output_path)
            clear_folder(frenchdb_output_path)
            for source_filename, target_filename in pairs:
                shutil.copyfile(os.path.join(output_path, source_filename),
                                os.path.join(frenchdb_output_path,
                                             target_filename))
    elif lang == 'Spanish':
        cards = {}
        for row in card_data:
            if (row[CARD_SET] == set_id and
                    (_needed_for_spanishdb(row) or
                     row[CARD_TYPE] == 'Presentation')):
                card_number = str(_handle_int(row[CARD_NUMBER])).zfill(3)
                cards[card_number] = _spanishdb_code(row)

        pairs = []
        if cards and known_filenames:
            for _, _, filenames in os.walk(output_path):
                for filename in filenames:
                    if (filename.endswith('-2.png') and
                            '----' in filename and
                            filename.split('----')[1][:36]
                            in empty_rules_backs):
                        continue

                    card_number = filename[:3]
                    if card_number in cards:
                        suffix = '-2' if filename.endswith('-2.png') else ''
                        pairs.append((
                            filename,
                            '{}{}.png'.format(cards[card_number], suffix)))

                break

        if pairs:
            spanishdb_output_path = os.path.join(
                OUTPUT_SPANISHDB_IMAGES_PATH, '{}.{}'.format(
                    escape_filename(set_name), lang))
            create_folder(spanishdb_output_path)
            clear_folder(spanishdb_output_path)
            for source_filename, target_filename in pairs:
                shutil.copyfile(os.path.join(output_path, source_filename),
                                os.path.join(spanishdb_output_path,
                                             target_filename))

    logging.info('[%s, %s] ...Generating DB, Preview and RingsDB image '
                 'outputs (%ss)', set_name, lang,
                 round(time.time() - timestamp, 3))


def generate_octgn(conf, set_id, set_name, lang):
    """ Generate OCTGN and DragnCards image outputs.
    """
    logging.info('[%s, %s] Generating OCTGN and DragnCards image outputs...',
                 set_name, lang)
    timestamp = time.time()

    input_path = os.path.join(IMAGES_EONS_PATH, PNG300OCTGN,
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_OCTGN_IMAGES_PATH, '{}.{}'.format(
        escape_filename(set_name), lang))

    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_octgn.{}.{}'.format(set_id, lang))
    create_folder(temp_path)
    clear_folder(temp_path)
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            shutil.copyfile(os.path.join(input_path, filename),
                            os.path.join(temp_path, filename))

        break

    _make_low_quality(conf, temp_path)

    pack_path = os.path.join(output_path,
                             escape_octgn_filename('{}.{}.o8c'.format(
                                 escape_filename(set_name), lang)))

    known_filenames = set()
    for _, _, filenames in os.walk(temp_path):
        if not filenames:
            logging.error('[%s, %s] No cards found', set_name, lang)
            break

        create_folder(output_path)
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

    delete_folder(temp_path)

    logging.info('[%s, %s] ...Generating OCTGN and DragnCards image outputs '
                 '(%ss)', set_name, lang, round(time.time() - timestamp, 3))


def generate_rules_pdf(conf, set_id, set_name, lang):
    """ Generate Rules PDF outputs.
    """
    logging.info('[%s, %s] Generating Rules PDF outputs...',
                 set_name, lang)
    timestamp = time.time()

    input_path = os.path.join(IMAGES_EONS_PATH,
                              PNG300RULES,
                              '{}.{}'.format(set_id, lang))
    for _, _, filenames in os.walk(input_path):
        if not filenames:
            logging.error('[%s, %s] No cards found', set_name, lang)
            logging.info('[%s, %s] ...Generating Rules PDF outputs (%ss)',
                         set_name, lang, round(time.time() - timestamp, 3))
            return

        break

    output_path = os.path.join(OUTPUT_RULES_PDF_PATH, '{}.{}'.format(
        escape_filename(set_name), lang))
    create_folder(output_path)
    pdf_filename = 'Rules.{}.{}.pdf'.format(escape_filename(set_name),
                                            lang)
    pdf_path = os.path.join(output_path, pdf_filename)
    cmd = MAGICK_COMMAND_RULES_PDF.format(conf['magick_path'], input_path,
                                          os.sep, pdf_path)
    res = _run_cmd(cmd)
    logging.info(res)

    logging.info('[%s, %s] ...Generating Rules PDF outputs (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def _collect_pdf_images(input_path, set_id, card_data):
    """ Collect image filenames for generated PDF.
    """
    for _, _, filenames in os.walk(input_path):
        if not filenames:
            return {}

        empty_rules_backs = {
            row[CARD_ID] for row in card_data
            if row[CARD_SET] == set_id and
            row[CARD_TYPE] == 'Rules' and
            row[BACK_PREFIX + CARD_TEXT] is None and
            row[BACK_PREFIX + CARD_VICTORY] is None}
        images = {'player': [],
                  'encounter': [],
                  'rules': [],
                  'custom': []}

        for filename in filenames:
            parts = filename.split('-')
            if parts[-1] != '1.png':
                continue

            back_path = os.path.join(input_path, '{}-2.png'.format(
                '-'.join(parts[:-1])))
            if filename[50:86] in empty_rules_backs:
                back_type = 'rules'
            elif os.path.exists(back_path):
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


def generate_pdf(conf, set_id, set_name, lang, card_data):  # pylint: disable=R0914
    """ Generate PDF outputs.
    """
    logging.info('[%s, %s] Generating PDF outputs...', set_name, lang)
    timestamp = time.time()

    input_path = os.path.join(IMAGES_EONS_PATH, PNG300PDF,
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_PDF_PATH, '{}.{}'.format(
        escape_filename(set_name), lang))

    images = _collect_pdf_images(input_path, set_id, card_data)
    if not images:
        logging.error('[%s, %s] No cards found', set_name, lang)
        logging.info('[%s, %s] ...Generating PDF outputs (%ss)',
                     set_name, lang, round(time.time() - timestamp, 3))
        return

    create_folder(output_path)
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
    mark_length = 0.2 * inch

    top_image = os.path.join(IMAGES_OTHER_PATH, 'top_marks.png')
    bottom_image = os.path.join(IMAGES_OTHER_PATH, 'bottom_marks.png')
    left_image = os.path.join(IMAGES_OTHER_PATH, 'left_marks.png')
    right_image = os.path.join(IMAGES_OTHER_PATH, 'right_marks.png')

    for page_format in formats:
        canvas = Canvas(
            os.path.join(output_path, 'Home.{}.{}.{}.pdf'.format(
                page_format, escape_filename(set_name), lang)),
            pagesize=landscape(formats[page_format]))
        width, height = landscape(formats[page_format])
        width_margin = (width - 3 * card_width) / 2
        height_margin = (height - 2 * card_height) / 2
        for num, page in enumerate(pages):
            if num % 2 == 0:
                canvas.drawImage(
                    top_image, width_margin,
                    height_margin + 2 * card_height, 3 * card_width,
                    mark_length, anchor='sw')
                canvas.drawImage(
                    bottom_image, width_margin, height_margin - mark_length,
                    3 * card_width, mark_length, anchor='sw')
                canvas.drawImage(
                    left_image, width_margin - mark_length, height_margin,
                    mark_length, 2 * card_height, anchor='sw')
                canvas.drawImage(
                    right_image, width_margin + 3 * card_width, height_margin,
                    mark_length, 2 * card_height, anchor='sw')

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


def generate_genericpng_pdf(conf, set_id, set_name, lang, card_data):  # pylint: disable=R0912,R0914,R0915
    """ Generate generic PNG PDF outputs.
    """
    logging.info('[%s, %s] Generating generic PNG PDF outputs...', set_name,
                 lang)
    timestamp = time.time()

    input_path = os.path.join(IMAGES_EONS_PATH, PNG800PDF,
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_GENERICPNG_PDF_PATH, '{}.{}'.format(
        escape_filename(set_name), lang))
    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_genericpng_pdf.{}.{}'.format(set_id,
                                                                    lang))

    images = _collect_pdf_images(input_path, set_id, card_data)
    if not images:
        logging.error('[%s, %s] No cards found', set_name, lang)
        logging.info('[%s, %s] ...Generating generic PNG PDF outputs (%ss)',
                     set_name, lang, round(time.time() - timestamp, 3))
        return

    create_folder(temp_path)
    clear_folder(temp_path)
    create_folder(output_path)
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
    if ('genericpng_pdf_a4_zip' in conf['outputs'][lang] or
            'genericpng_pdf_a4_7z' in conf['outputs'][lang]):
        formats['A4'] = [A4, []]
        if 'genericpng_pdf_a4_zip' in conf['outputs'][lang]:
            formats['A4'][1].append('zip')

        if 'genericpng_pdf_a4_7z' in conf['outputs'][lang]:
            formats['A4'][1].append('7z')

    if ('genericpng_pdf_letter_zip' in conf['outputs'][lang] or
            'genericpng_pdf_letter_7z' in conf['outputs'][lang]):
        formats['Letter'] = [letter, []]
        if 'genericpng_pdf_letter_zip' in conf['outputs'][lang]:
            formats['Letter'][1].append('zip')

        if 'genericpng_pdf_letter_7z' in conf['outputs'][lang]:
            formats['Letter'][1].append('7z')

    card_width = 2.75 * inch
    card_height = 3.75 * inch
    mark_length = 0.2 * inch

    top_image = os.path.join(IMAGES_OTHER_PATH, 'top_marks.png')
    bottom_image = os.path.join(IMAGES_OTHER_PATH, 'bottom_marks.png')
    left_image = os.path.join(IMAGES_OTHER_PATH, 'left_marks.png')
    right_image = os.path.join(IMAGES_OTHER_PATH, 'right_marks.png')

    for page_format in formats:
        pdf_filename = '800dpi.{}.{}.{}.pdf'.format(
            page_format, escape_filename(set_name), lang)
        pdf_path = os.path.join(temp_path, pdf_filename)
        canvas = Canvas(pdf_path, pagesize=landscape(formats[page_format][0]))
        width, height = landscape(formats[page_format][0])
        width_margin = (width - 3 * card_width) / 2
        height_margin = (height - 2 * card_height) / 2
        for num, page in enumerate(pages):
            if num % 2 == 0:
                canvas.drawImage(
                    top_image, width_margin,
                    height_margin + 2 * card_height, 3 * card_width,
                    mark_length, anchor='sw')
                canvas.drawImage(
                    bottom_image, width_margin, height_margin - mark_length,
                    3 * card_width, mark_length, anchor='sw')
                canvas.drawImage(
                    left_image, width_margin - mark_length, height_margin,
                    mark_length, 2 * card_height, anchor='sw')
                canvas.drawImage(
                    right_image, width_margin + 3 * card_width, height_margin,
                    mark_length, 2 * card_height, anchor='sw')

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

        if 'zip' in formats[page_format][1]:
            with zipfile.ZipFile(
                    os.path.join(output_path, '{}.zip'.format(pdf_filename)),
                    'w') as obj:
                obj.write(pdf_path, pdf_filename)

        if '7z' in formats[page_format][1]:
            with py7zr.SevenZipFile(
                    os.path.join(output_path, '{}.7z'.format(pdf_filename)),
                    'w', filters=PY7ZR_FILTERS) as obj:
                obj.write(pdf_path, pdf_filename)

    delete_folder(temp_path)
    logging.info('[%s, %s] ...Generating generic PNG PDF outputs (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def _make_cmyk(conf, input_path, min_size):
    """ Convert RGB to CMYK.
    """
    input_cnt = 0
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            input_cnt += 1

        break

    if input_cnt:
        cmd = MAGICK_COMMAND_CMYK.format(conf['magick_path'], input_path,
                                         os.sep)
        res = _run_cmd(cmd)
        logging.info(res)

    output_cnt = 0
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(input_path, filename)
                               ) < min_size:
                raise ImageMagickError('ImageMagick failed for {}'.format(
                    os.path.join(input_path, filename)))

        break

    if output_cnt != input_cnt:
        raise ImageMagickError('Wrong number of output files: {} instead of {}'
                               .format(output_cnt, input_cnt))


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
            escape_filename(r[CARD_NAME])))

    selected = []
    for i, row in enumerate(card_data):
        if (row[CARD_TYPE] == 'Rules' and
                row[BACK_PREFIX + CARD_TEXT] is None and
                row[BACK_PREFIX + CARD_VICTORY] is None):
            card_number = (str(int(row[CARD_NUMBER])).zfill(3)
                           if is_positive_or_zero_int(row[CARD_NUMBER])
                           else str(row[CARD_NUMBER]))
            card_name = escape_filename(row[CARD_NAME])
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
            elif filename.endswith('-2o.jpg'):
                obj.write(os.path.join(input_path, filename),
                          'back_official/{}'.format(filename))
            elif filename.endswith('-2u.jpg'):
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
        escape_filename(set_name), lang))
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

    create_folder(output_path)
    create_folder(temp_path)
    clear_folder(temp_path)
    _prepare_printing_images(input_path, temp_path, 'mpc')
    _make_unique_png(temp_path)
    _combine_doublesided_rules_cards(set_id, temp_path, card_data, 'mpc')

    if 'makeplayingcards_zip' in conf['outputs'][lang]:
        with zipfile.ZipFile(
                os.path.join(output_path,
                             'MPC.{}.{}.images.zip'.format(
                                 escape_filename(set_name), lang)),
                'w') as obj:
            _prepare_mpc_printing_archive(temp_path, obj)
            obj.write('MakePlayingCards.pdf', 'MakePlayingCards.pdf')

    if 'makeplayingcards_7z' in conf['outputs'][lang]:
        with py7zr.SevenZipFile(
                os.path.join(output_path,
                             'MPC.{}.{}.images.7z'.format(
                                 escape_filename(set_name), lang)),
                'w', filters=PY7ZR_FILTERS) as obj:
            _prepare_mpc_printing_archive(temp_path, obj)
            obj.write('MakePlayingCards.pdf', 'MakePlayingCards.pdf')

    delete_folder(temp_path)
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
        escape_filename(set_name), lang))
    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_dtc.{}.{}'.format(set_id, lang))

    for _, _, filenames in os.walk(input_path):
        if not filenames:
            logging.error('[%s, %s] No cards found', set_name, lang)
            logging.info('[%s, %s] ...Generating DriveThruCards outputs (%ss)',
                         set_name, lang, round(time.time() - timestamp, 3))
            return

        break

    create_folder(output_path)
    create_folder(temp_path)
    clear_folder(temp_path)
    _prepare_printing_images(input_path, temp_path, 'dtc')
    _combine_doublesided_rules_cards(set_id, temp_path, card_data, 'dtc')

    if 'drivethrucards_zip' in conf['outputs'][lang]:
        with zipfile.ZipFile(
                os.path.join(output_path,
                             'DTC.{}.{}.images.zip'.format(
                                 escape_filename(set_name), lang)),
                'w') as obj:
            _prepare_dtc_printing_archive(temp_path, obj)
            obj.write('DriveThruCards.pdf', 'DriveThruCards.pdf')

    if 'drivethrucards_7z' in conf['outputs'][lang]:
        with py7zr.SevenZipFile(
                os.path.join(output_path,
                             'DTC.{}.{}.images.7z'.format(
                                 escape_filename(set_name), lang)),
                'w', filters=PY7ZR_FILTERS) as obj:
            _prepare_dtc_printing_archive(temp_path, obj)
            obj.write('DriveThruCards.pdf', 'DriveThruCards.pdf')

    delete_folder(temp_path)
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

    create_folder(temp_path)
    clear_folder(temp_path)
    _prepare_printing_images(input_path, temp_path, 'mbprint')
    _combine_doublesided_rules_cards(set_id, temp_path, card_data, 'mbprint')

    if ('mbprint_zip' in conf['outputs'][lang] or
            'mbprint_7z' in conf['outputs'][lang]):
        output_path = os.path.join(OUTPUT_MBPRINT_PATH, '{}.{}'.format(
            escape_filename(set_name), lang))
        create_folder(output_path)

        if 'mbprint_zip' in conf['outputs'][lang]:
            with zipfile.ZipFile(
                    os.path.join(output_path,
                                 'MBPRINT.{}.{}.images.zip'.format(
                                     escape_filename(set_name), lang)),
                    'w') as obj:
                _prepare_mbprint_printing_archive(temp_path, obj)
                obj.write('MBPrint.pdf', 'MBPrint.pdf')

        if 'mbprint_7z' in conf['outputs'][lang]:
            with py7zr.SevenZipFile(
                    os.path.join(output_path,
                                 'MBPRINT.{}.{}.images.7z'.format(
                                     escape_filename(set_name), lang)),
                    'w', filters=PY7ZR_FILTERS) as obj:
                _prepare_mbprint_printing_archive(temp_path, obj)
                obj.write('MBPrint.pdf', 'MBPrint.pdf')

    if ('mbprint_pdf_zip' in conf['outputs'][lang] or
            'mbprint_pdf_7z' in conf['outputs'][lang]):
        pdf_filename = 'MBPRINT.{}.{}.pdf'.format(escape_filename(set_name),
                                                  lang)
        pdf_path = os.path.join(temp_path, pdf_filename)
        cmd = MAGICK_COMMAND_MBPRINT_PDF.format(conf['magick_path'], temp_path,
                                                os.sep, pdf_path)
        res = _run_cmd(cmd)
        logging.info(res)

        output_path = os.path.join(OUTPUT_MBPRINT_PDF_PATH, '{}.{}'.format(
            escape_filename(set_name), lang))
        create_folder(output_path)

        if 'mbprint_pdf_zip' in conf['outputs'][lang]:
            with zipfile.ZipFile(
                    os.path.join(output_path,
                                 'MBPRINT.{}.{}.pdf.zip'.format(
                                     escape_filename(set_name), lang)),
                    'w') as obj:
                obj.write(pdf_path, pdf_filename)

        if 'mbprint_pdf_7z' in conf['outputs'][lang]:
            with py7zr.SevenZipFile(
                    os.path.join(output_path,
                                 'MBPRINT.{}.{}.pdf.7z'.format(
                                     escape_filename(set_name), lang)),
                    'w', filters=PY7ZR_FILTERS) as obj:
                obj.write(pdf_path, pdf_filename)

    delete_folder(temp_path)
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
        escape_filename(set_name), lang))
    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_genericpng.{}.{}'.format(set_id, lang))

    for _, _, filenames in os.walk(input_path):
        if not filenames:
            logging.error('[%s, %s] No cards found', set_name, lang)
            logging.info('[%s, %s] ...Generating generic PNG outputs (%ss)',
                         set_name, lang, round(time.time() - timestamp, 3))
            return

        break

    create_folder(output_path)
    create_folder(temp_path)
    clear_folder(temp_path)
    _prepare_printing_images(input_path, temp_path, 'genericpng')
    _combine_doublesided_rules_cards(set_id, temp_path, card_data,
                                     'genericpng')

    if 'genericpng_zip' in conf['outputs'][lang]:
        with zipfile.ZipFile(
                os.path.join(output_path,
                             'PNG.{}.{}.images.zip'.format(
                                 escape_filename(set_name), lang)),
                'w') as obj:
            _prepare_genericpng_printing_archive(temp_path, obj)

    if 'genericpng_7z' in conf['outputs'][lang]:
        with py7zr.SevenZipFile(
                os.path.join(output_path,
                             'PNG.{}.{}.images.7z'.format(
                                 escape_filename(set_name), lang)),
                'w', filters=PY7ZR_FILTERS) as obj:
            _prepare_genericpng_printing_archive(temp_path, obj)

    delete_folder(temp_path)
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
    """ Copy OCTGN .o8d files to the destination folder.
    """
    set_folders = {escape_filename(SETS[s]['Name']) for s in sets}
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
    create_folder(temp_path)
    clear_folder(temp_path)

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

    delete_folder(temp_path)

    logging.info('...Copying OCTGN outputs to the destination folder (%ss)',
                 round(time.time() - timestamp, 3))


def copy_db_outputs(conf, sets):
    """ Copy DB outputs to the destination folder.
    """
    logging.info('Copying DB outputs to the destination folder...')
    timestamp = time.time()

    for _, set_name in sets:
        output_path = os.path.join(OUTPUT_DB_PATH, '{}.English'.format(
            escape_filename(set_name)))
        destination_path = os.path.join(conf['db_destination_path'],
                                        '{}.English'.format(
                                            escape_filename(set_name)))
        create_folder(destination_path)
        clear_folder(destination_path)
        for _, _, filenames in os.walk(output_path):
            for filename in filenames:
                shutil.copyfile(os.path.join(output_path, filename),
                                os.path.join(destination_path, filename))

            break

        logging.info('Copied DB outputs for %s', set_name)

    logging.info('...Copying DB outputs to the destination folder (%ss)',
                 round(time.time() - timestamp, 3))


def copy_octgn_image_outputs(conf, sets):
    """ Copy OCTGN image outputs to the destination folder.
    """
    logging.info('Copying OCTGN image outputs to the destination folder...')
    timestamp = time.time()

    for set_id, set_name in sets:
        if set_id not in conf['set_ids_octgn_image_destination']:
            continue

        output_path = os.path.join(
            OUTPUT_OCTGN_IMAGES_PATH,
            '{}.English'.format(escape_filename(set_name)))
        destination_path = os.path.join(conf['octgn_image_destination_path'],
                                        'a21af4e8-be4b-4cda-a6b6-534f9717391f')
        create_folder(destination_path)
        destination_path = os.path.join(destination_path,
                                        'Sets')
        create_folder(destination_path)
        destination_path = os.path.join(destination_path,
                                        set_id)
        create_folder(destination_path)
        destination_path = os.path.join(destination_path,
                                        'Cards')
        create_folder(destination_path)
        clear_folder(destination_path)
        for _, _, filenames in os.walk(output_path):
            for filename in filenames:
                shutil.copyfile(
                    os.path.join(output_path, filename),
                    os.path.join(conf['octgn_image_destination_path'],
                                 filename))
                with zipfile.ZipFile(os.path.join(
                        conf['octgn_image_destination_path'],
                        filename)) as obj:
                    obj.extractall(conf['octgn_image_destination_path'])

            break

        logging.info('Copied OCTGN image outputs for %s', set_name)

    logging.info('...Copying OCTGN image outputs to the destination folder '
                 '(%ss)', round(time.time() - timestamp, 3))


def copy_tts_outputs(conf, sets):
    """ Copy TTS outputs to the destination folder.
    """
    logging.info('Copying TTS outputs to the destination folder...')
    timestamp = time.time()

    for _, set_name in sets:
        output_path = os.path.join(OUTPUT_TTS_PATH, '{}.English'.format(
            escape_filename(set_name)))
        destination_path = os.path.join(conf['tts_destination_path'],
                                        '{}.English'.format(
                                            escape_filename(set_name)))
        create_folder(destination_path)
        clear_folder(destination_path)
        for _, _, filenames in os.walk(output_path):
            for filename in filenames:
                shutil.copyfile(os.path.join(output_path, filename),
                                os.path.join(destination_path, filename))

            break

        logging.info('Copied TTS outputs for %s', set_name)

    logging.info('...Copying TTS outputs to the destination folder (%ss)',
                 round(time.time() - timestamp, 3))


def _get_ssh_client(conf):
    """ Get SCP client.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    parts = conf['dragncards_hostname'].split('@')
    client.connect(parts[1], username=parts[0],
                   key_filename=conf['dragncards_id_rsa_path'],
                   timeout=30)
    return client


def upload_dragncards(conf, sets, updated_sets):
    """ Uploading outputs to DragnCards.
    """
    logging.info('Uploading outputs to DragnCards...')
    timestamp = time.time()

    client = _get_ssh_client(conf)
    try:  # pylint: disable=R1702
        scp_client = SCPClient(client.get_transport())
        for set_id, set_name in sets:
            output_path = os.path.join(
                OUTPUT_OCTGN_IMAGES_PATH,
                '{}.English'.format(escape_filename(set_name)),
                '{}.English.o8c'.format(
                    escape_octgn_filename(escape_filename(set_name))))
            if (conf['dragncards_remote_image_path'] and
                    'English' in conf['output_languages'] and
                    'octgn' in conf['outputs']['English'] and
                    set_id in [s[0] for s in updated_sets] and
                    os.path.exists(output_path)):
                temp_path = os.path.join(
                    TEMP_ROOT_PATH,
                    'upload_dragncards_{}'.format(escape_filename(set_name)))
                create_folder(temp_path)
                clear_folder(temp_path)
                with zipfile.ZipFile(output_path) as obj:
                    obj.extractall(temp_path)

                output_path = os.path.join(
                    temp_path,
                    'a21af4e8-be4b-4cda-a6b6-534f9717391f',
                    'Sets',
                    set_id,
                    'Cards')
                if os.path.exists(output_path):
                    for _, _, filenames in os.walk(output_path):
                        for filename in filenames:
                            scp_client.put(
                                os.path.join(output_path, filename),
                                conf['dragncards_remote_image_path'])

                        break

                    logging.info('Uploaded images for %s to DragnCards host',
                                 set_name)

                delete_folder(temp_path)

            output_path = os.path.join(
                OUTPUT_DRAGNCARDS_PATH,
                escape_filename(set_name),
                '{}.json'.format(escape_octgn_filename(
                    escape_filename(set_name))))
            if (conf['dragncards_remote_json_path'] and
                    conf['dragncards_json'] and
                    os.path.exists(output_path)):
                scp_client.put(output_path,
                               conf['dragncards_remote_json_path'])
                logging.info('Uploaded %s to DragnCards host',
                             '{}.json'.format(escape_filename(set_name)))

            output_path = os.path.join(OUTPUT_OCTGN_DECKS_PATH,
                                       escape_filename(set_name))
            if (conf['dragncards_remote_deck_path'] and conf['octgn_o8d'] and
                    os.path.exists(output_path)):
                temp_path = os.path.join(
                    TEMP_ROOT_PATH,
                    'upload_dragncards_{}'.format(escape_filename(set_name)))
                create_folder(temp_path)
                clear_folder(temp_path)
                for _, _, filenames in os.walk(output_path):
                    for filename in filenames:
                        if filename.startswith('Player-'):
                            continue

                        new_filename = re.sub(r'\.o8d$',
                                              '{}.o8d'.format(PLAYTEST_SUFFIX),
                                              filename)
                        shutil.copyfile(os.path.join(output_path, filename),
                                        os.path.join(temp_path, new_filename))

                        scp_client.put(os.path.join(temp_path, new_filename),
                                       conf['dragncards_remote_deck_path'])
                        logging.info('Uploaded %s to DragnCards host',
                                     filename)

                    break

                delete_folder(temp_path)

    finally:
        client.close()

    logging.info('...Uploading outputs to DragnCards (%ss)',
                 round(time.time() - timestamp, 3))


def update_ringsdb(conf, sets):
    """ Update test.ringsdb.com.
    """
    logging.info('Updating test.ringsdb.com...')
    timestamp = time.time()

    try:
        with open(RINGSDB_JSON_PATH, 'r') as fobj:
            checksums = json.load(fobj)
    except Exception:  # pylint: disable=W0703
        checksums = {}

    changes = False
    sets = [s for s in sets if s[0] in FOUND_SETS]
    for set_id, set_name in sets:
        if not SETS[set_id].get(SET_HOB_CODE):
            continue

        path = os.path.join(OUTPUT_RINGSDB_PATH, escape_filename(set_name),
                            '{}.csv'.format(escape_filename(set_name)))
        if not os.path.exists(path):
            continue

        with open(path, 'br') as fobj:
            content = fobj.read()

        checksum = hashlib.md5(content).hexdigest()
        if checksum == checksums.get(set_id):
            continue

        changes = True
        checksums[set_id] = checksum

        logging.info('Uploading %s to %s', set_name, conf['ringsdb_url'])
        cookies = _read_ringsdb_cookies(conf)
        session = requests.Session()
        session.cookies.update(cookies)
        if conf['ringsdb_url'].startswith('https://'):
            session.mount('https://', TLSAdapter())

        res = session.post(
            '{}/admin/csv/upload'.format(conf['ringsdb_url']),
            files={'upfile': open(path, 'br')},
            data={'code': SETS[set_id][SET_HOB_CODE], 'name': set_name})
        res = res.content.decode('utf-8')
        if res != 'Done':
            raise RingsDBError('Error uploading {} to test.ringsdb.com: {}'
                               .format(set_name, res[:LOG_LIMIT]))

        cookies = session.cookies.get_dict()
        _write_ringsdb_cookies(cookies)

    if changes:
        with open(RINGSDB_JSON_PATH, 'w') as fobj:
            json.dump(checksums, fobj)

    logging.info('...Updating test.ringsdb.com (%ss)',
                 round(time.time() - timestamp, 3))


def get_last_image_timestamp():
    """ Get timestamp of the last generated image output.

    NOT USED AT THE MOMENT
    """
    max_ts = 0
    for root, _, filenames in os.walk(OUTPUT_PATH):
        for filename in filenames:
            if filename.split('.')[-1] in ('png', 'jpg', 'pdf', 'o8c', '7z'):
                file_ts = int(os.path.getmtime(os.path.join(root, filename)))
                if file_ts > max_ts:
                    max_ts = file_ts

    max_ts = datetime.fromtimestamp(max_ts).strftime('%Y-%m-%d %H:%M:%S')
    return max_ts
