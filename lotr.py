# pylint: disable=C0209,C0302,W0703
# -*- coding: utf8 -*-
""" Helper functions for LotR workflow.
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

import paramiko
import requests
from scp import SCPClient
import unidecode
import urllib3
import yaml

try:
    import png  # pylint: disable=E0401
except ModuleNotFoundError:
    pass

try:
    import py7zr  # pylint: disable=E0401
    PY7ZR_FILTERS = [{'id': py7zr.FILTER_LZMA2,
                      'preset': 9 | py7zr.PRESET_EXTREME}]
except ModuleNotFoundError:
    PY7ZR_FILTERS = None

try:
    from reportlab.lib.pagesizes import landscape, letter, A4  # pylint: disable=E0401
    from reportlab.lib.units import inch  # pylint: disable=E0401
    from reportlab.pdfgen.canvas import Canvas  # pylint: disable=E0401
except ModuleNotFoundError:
    pass


SET_SHEET = 'Sets'
CARD_SHEET = 'Card Data'
SCRATCH_SHEET = 'Scratch Data'

SET_ID = 'GUID'
SET_NAME = 'Name'
SET_COLLECTION_ICON = 'Collection Icon'
SET_RINGSDB_CODE = 'RingsDB Code'
SET_HOB_CODE = 'HoB Code'
SET_DISCORD_PREFIX = 'Discord Prefix'
SET_COPYRIGHT = 'Copyright'
SET_LOCKED = 'Locked'
SET_IGNORE = 'Ignore'
SET_CHANGED = 'Changed'

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
CARD_ENCOUNTER_SET_NUMBER = 'Encounter Set Number'
CARD_ENCOUNTER_SET_ICON = 'Encounter Set Icon'
CARD_FLAGS = 'Flags'
CARD_ARTIST = 'Artist'
CARD_PANX = 'PanX'
CARD_PANY = 'PanY'
CARD_SCALE = 'Scale'
CARD_PORTRAIT_SHADOW = 'Portrait Shadow'
CARD_SIDE_B = 'Side B'
CARD_EASY_MODE = 'Removed for Easy Mode'
CARD_ADDITIONAL_ENCOUNTER_SETS = 'Additional Encounter Sets'
CARD_ADVENTURE = 'Adventure'
CARD_ICON = 'Collection Icon'
CARD_COPYRIGHT = 'Copyright'
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
    CARD_PANX, CARD_PANY, CARD_SCALE, CARD_PORTRAIT_SHADOW,
    BACK_PREFIX + CARD_PANX, BACK_PREFIX + CARD_PANY,
    BACK_PREFIX + CARD_SCALE, BACK_PREFIX + CARD_PORTRAIT_SHADOW, CARD_SIDE_B,
    CARD_SELECTED, CARD_CHANGED, CARD_SCRATCH
}
DISCORD_IGNORE_CHANGES_COLUMNS = {
    CARD_SET, CARD_NUMBER, CARD_SET_NAME, CARD_SET_RINGSDB_CODE,
    CARD_SET_HOB_CODE, CARD_SET_LOCKED, CARD_RINGSDB_CODE, CARD_BOT_DISABLED,
    CARD_NORMALIZED_NAME, BACK_PREFIX + CARD_NORMALIZED_NAME,
    CARD_DISCORD_CHANNEL, CARD_DISCORD_CATEGORY, ROW_COLUMN
}
ONE_LINE_COLUMNS = {
    CARD_ENCOUNTER_SET, CARD_NAME, CARD_TRAITS, CARD_KEYWORDS, CARD_VICTORY,
    CARD_PRINTED_NUMBER, CARD_ENCOUNTER_SET_NUMBER, CARD_ENCOUNTER_SET_ICON,
    CARD_ARTIST, BACK_PREFIX + CARD_ENCOUNTER_SET, BACK_PREFIX + CARD_NAME,
    BACK_PREFIX + CARD_TRAITS, BACK_PREFIX + CARD_KEYWORDS,
    BACK_PREFIX + CARD_VICTORY, BACK_PREFIX + CARD_PRINTED_NUMBER,
    BACK_PREFIX + CARD_ENCOUNTER_SET_NUMBER,
    BACK_PREFIX + CARD_ENCOUNTER_SET_ICON, BACK_PREFIX + CARD_ARTIST,
    CARD_ADDITIONAL_ENCOUNTER_SETS, CARD_ADVENTURE, CARD_ICON, CARD_COPYRIGHT}
TRANSLATED_COLUMNS = {
    CARD_NAME, CARD_TRAITS, CARD_KEYWORDS, CARD_VICTORY, CARD_TEXT,
    CARD_SHADOW, CARD_FLAVOUR, BACK_PREFIX + CARD_NAME,
    BACK_PREFIX + CARD_TRAITS, BACK_PREFIX + CARD_KEYWORDS,
    BACK_PREFIX + CARD_VICTORY, BACK_PREFIX + CARD_TEXT,
    BACK_PREFIX + CARD_SHADOW, BACK_PREFIX + CARD_FLAVOUR, CARD_ADVENTURE
}

CARD_TYPES = {'Ally', 'Attachment', 'Campaign', 'Contract',
              'Encounter Side Quest', 'Enemy', 'Event', 'Full Art Landscape',
              'Full Art Portrait', 'Hero', 'Location', 'Nightmare',
              'Objective', 'Objective Ally', 'Objective Hero',
              'Objective Location', 'Player Objective', 'Player Side Quest',
              'Presentation', 'Quest', 'Rules', 'Ship Enemy', 'Ship Objective',
              'Treachery', 'Treasure'}
CARD_TYPES_LANDSCAPE = {'Encounter Side Quest', 'Full Art Landscape',
                        'Player Side Quest', 'Quest'}
CARD_TYPES_DOUBLESIDE_MANDATORY = {'Campaign', 'Nightmare', 'Presentation',
                                   'Quest', 'Rules'}
CARD_TYPES_DOUBLESIDE_OPTIONAL = {'Campaign', 'Contract', 'Nightmare',
                                  'Presentation', 'Quest', 'Rules'}
CARD_TYPES_PLAYER = {'Ally', 'Attachment', 'Contract', 'Event', 'Hero',
                     'Player Objective', 'Player Side Quest', 'Treasure'}
CARD_TYPES_PLAYER_DECK = {'Ally', 'Attachment', 'Event', 'Player Objective',
                          'Player Side Quest'}
CARD_TYPES_ENCOUNTER_SIZE = {'Enemy', 'Location', 'Objective',
                             'Objective Ally', 'Objective Hero',
                             'Objective Location', 'Ship Enemy',
                             'Ship Objective', 'Treachery', 'Treasure'}
CARD_TYPES_ENCOUNTER_SET = {'Campaign', 'Encounter Side Quest', 'Enemy',
                            'Location', 'Nightmare', 'Objective',
                            'Objective Ally', 'Objective Hero',
                            'Objective Location', 'Quest', 'Ship Enemy',
                            'Ship Objective', 'Treachery', 'Treasure'}
CARD_TYPES_NO_ENCOUNTER_SET = {'Ally', 'Attachment', 'Contract', 'Event',
                               'Full Art Landscape', 'Full Art Portrait',
                               'Hero', 'Player Objective', 'Player Side Quest',
                               'Presentation'}
CARD_TYPES_UNIQUE = {'Hero', 'Objective Hero', 'Treasure'}
CARD_TYPES_NO_UNIQUE = {'Campaign', 'Contract', 'Event', 'Full Art Landscape',
                        'Full Art Portrait', 'Nightmare', 'Player Side Quest',
                        'Presentation', 'Quest', 'Rules'}
CARD_TYPES_PLAYER_SPHERE = {'Ally', 'Attachment', 'Event', 'Hero',
                            'Player Side Quest'}
CARD_TYPES_TRAITS = {'Ally', 'Enemy', 'Hero', 'Location', 'Objective Ally',
                     'Objective Hero', 'Objective Location', 'Ship Enemy',
                     'Ship Objective', 'Treasure'}
CARD_TYPES_NO_TRAITS = {'Campaign', 'Contract', 'Full Art Landscape',
                        'Full Art Portrait', 'Nightmare', 'Presentation',
                        'Quest', 'Rules'}
CARD_SPHERES_TRAITS = {'Region'}
CARD_TYPES_NO_KEYWORDS = {'Campaign', 'Contract', 'Full Art Landscape',
                          'Full Art Portrait', 'Nightmare', 'Presentation',
                          'Rules'}
CARD_TYPES_COST = {'Hero', 'Ally', 'Attachment', 'Event', 'Player Objective',
                   'Player Side Quest', 'Treasure', 'Quest'}
CARD_TYPES_ENGAGEMENT = {'Enemy', 'Ship Enemy', 'Quest'}
CARD_TYPES_THREAT = {'Enemy', 'Location', 'Ship Enemy'}
CARD_TYPES_WILLPOWER = {'Ally', 'Hero', 'Objective Ally', 'Objective Hero',
                        'Ship Objective'}
CARD_TYPES_COMBAT = {'Ally', 'Enemy', 'Hero', 'Objective Ally',
                     'Objective Hero', 'Ship Enemy', 'Ship Objective'}
CARD_TYPES_QUEST = {'Encounter Side Quest', 'Location', 'Objective Location',
                    'Player Side Quest'}
CARD_TYPES_QUEST_BACK = {'Quest'}
CARD_SPHERES_NO_QUEST = {'Cave', 'NoProgress', 'Region'}
CARD_TYPES_VICTORY = {'Ally', 'Attachment', 'Encounter Side Quest', 'Enemy',
                      'Event', 'Location', 'Objective', 'Objective Ally',
                      'Objective Location', 'Player Objective',
                      'Player Side Quest', 'Ship Enemy', 'Ship Objective',
                      'Treachery', 'Treasure'}
CARD_TYPES_VICTORY_BACK = {'Quest'}
CARD_SPHERES_NO_VICTORY = {'Cave', 'NoStat', 'Region'}
CARD_TYPES_SPECIAL_ICON = {'Enemy', 'Location', 'Objective', 'Objective Ally',
                           'Objective Location', 'Ship Enemy',
                           'Ship Objective', 'Treachery'}
CARD_SPHERES_NO_SPECIAL_ICON = {'NoStat'}
CARD_TYPES_NO_PERIOD_CHECK = {'Campaign', 'Nightmare', 'Presentation', 'Rules'}
CARD_TYPES_TEXT = {}
#CARD_TYPES_TEXT = {'Attachment', 'Campaign', 'Contract',
#                   'Encounter Side Quest', 'Event', 'Hero', 'Location',
#                   'Nightmare', 'Objective', 'Objective Ally',
#                   'Objective Hero', 'Objective Location', 'Player Objective',
#                   'Player Side Quest', 'Presentation', 'Rules', 'Ship Enemy',
#                   'Ship Objective', 'Treasure'}
CARD_TYPES_NO_TEXT = {'Full Art Landscape', 'Full Art Portrait'}
CARD_TYPES_TEXT_BACK = {}
#CARD_TYPES_TEXT_BACK = {'Attachment', 'Campaign', 'Encounter Side Quest',
#                        'Event', 'Hero', 'Location', 'Nightmare', 'Objective',
#                        'Objective Ally', 'Objective Hero',
#                        'Objective Location', 'Player Objective',
#                        'Player Side Quest', 'Quest', 'Ship Enemy',
#                        'Ship Objective', 'Treasure'}
CARD_TYPES_NO_TEXT_BACK = {'Full Art Landscape', 'Full Art Portrait',
                           'Presentation'}
CARD_SPHERES_NO_TEXT = {'Region'}
CARD_TYPES_SHADOW = {'Enemy', 'Location', 'Objective', 'Objective Ally',
                     'Objective Hero', 'Objective Location', 'Ship Enemy',
                     'Ship Objective', 'Treachery'}
CARD_TYPES_SHADOW_ENCOUNTER = {'Ally', 'Attachment', 'Event',
                               'Player Objective'}
CARD_TYPES_NO_FLAVOUR = {'Full Art Landscape', 'Full Art Portrait',
                         'Presentation', 'Rules'}
CARD_SPHERES_NO_FLAVOUR = {'Region'}
CARD_TYPES_NO_FLAVOUR_BACK = {'Full Art Landscape', 'Full Art Portrait',
                              'Nightmare', 'Presentation', 'Rules'}
CARD_TYPES_NO_PRINTED_NUMBER = {'Full Art Landscape', 'Full Art Portrait',
                                'Presentation', 'Rules'}
CARD_TYPES_NO_PRINTED_NUMBER_BACK = {'Campaign', 'Full Art Landscape',
                                     'Full Art Portrait', 'Nightmare',
                                     'Presentation', 'Rules'}
CARD_TYPES_ENCOUNTER_SET_NUMBER = {'Encounter Side Quest', 'Enemy', 'Location',
                                   'Objective', 'Objective Ally',
                                   'Objective Hero', 'Objective Location',
                                   'Ship Enemy', 'Ship Objective', 'Treachery'}
CARD_TYPES_ENCOUNTER_SET_ICON = {'Campaign', 'Encounter Side Quest', 'Enemy',
                                 'Location', 'Nightmare', 'Objective',
                                 'Objective Ally', 'Objective Hero',
                                 'Objective Location', 'Quest', 'Ship Enemy',
                                 'Ship Objective', 'Treachery', 'Treasure'}
CARD_TYPES_FLAGS = {'NoTraits':
                    {'Ally', 'Enemy', 'Hero', 'Location', 'Objective Ally',
                     'Objective Hero', 'Objective Location', 'Ship Enemy',
                     'Ship Objective', 'Treasure'},
                    'Promo': {'Hero'},
                    'BlueRing':
                    {'Encounter Side Quest', 'Enemy', 'Location', 'Objective',
                     'Objective Ally', 'Objective Hero', 'Objective Location',
                     'Ship Enemy', 'Ship Objective', 'Treachery'},
                    'GreenRing':
                    {'Encounter Side Quest', 'Enemy', 'Location', 'Objective',
                     'Objective Ally', 'Objective Hero', 'Objective Location',
                     'Ship Enemy', 'Ship Objective', 'Treachery'},
                    'RedRing':
                    {'Encounter Side Quest', 'Enemy', 'Location', 'Objective',
                     'Objective Ally', 'Objective Hero', 'Objective Location',
                     'Ship Enemy', 'Ship Objective', 'Treachery'}}
CARD_TYPES_FLAGS_BACK = {'NoTraits':
                         {'Ally', 'Enemy', 'Hero', 'Location',
                          'Objective Ally', 'Objective Hero',
                          'Objective Location', 'Ship Enemy', 'Ship Objective',
                          'Treasure'},
                         'Promo': {'Hero'},
                         'BlueRing':
                         {'Encounter Side Quest', 'Enemy', 'Location',
                          'Objective', 'Objective Ally', 'Objective Hero',
                          'Objective Location', 'Ship Enemy', 'Ship Objective',
                          'Treachery'},
                         'GreenRing':
                         {'Encounter Side Quest', 'Enemy', 'Location',
                          'Objective', 'Objective Ally', 'Objective Hero',
                          'Objective Location', 'Ship Enemy', 'Ship Objective',
                          'Treachery'},
                         'RedRing':
                         {'Encounter Side Quest', 'Enemy', 'Location',
                          'Objective', 'Objective Ally', 'Objective Hero',
                          'Objective Location', 'Ship Enemy', 'Ship Objective',
                          'Treachery'}}
CARD_TYPES_NO_FLAGS = {'Asterisk': {'Full Art Landscape', 'Full Art Portrait',
                                    'Presentation', 'Rules'},
                       'IgnoreName': {'Full Art Landscape',
                                      'Full Art Portrait', 'Presentation',
                                      'Rules'},
                       'IgnoreRules': {'Full Art Landscape',
                                       'Full Art Portrait', 'Presentation'},
                       'NoArtist': {'Presentation', 'Rules'},
                       'NoCopyright': {'Presentation', 'Rules'}}
CARD_TYPES_NO_FLAGS_BACK = {
    'Asterisk': {'Campaign', 'Full Art Landscape', 'Full Art Portrait',
                 'Nightmare', 'Presentation', 'Rules'},
    'IgnoreName': {'Full Art Landscape', 'Full Art Portrait', 'Presentation',
                   'Rules'},
    'IgnoreRules': {'Full Art Landscape', 'Full Art Portrait', 'Presentation'},
    'NoArtist': {'Campaign', 'Nightmare', 'Presentation', 'Rules'},
    'NoCopyright': {'Campaign', 'Nightmare', 'Presentation', 'Rules'}}
CARD_SPHERES_NO_FLAGS = {'BlueRing': {'Cave', 'NoStat', 'Region'},
                         'GreenRing': {'Cave', 'NoStat', 'Region'},
                         'RedRing': {'Cave', 'NoStat', 'Region'}}
CARD_TYPES_NO_ARTIST = {'Presentation', 'Rules'}
CARD_TYPES_NO_ARTIST_BACK = {'Campaign', 'Nightmare', 'Presentation', 'Rules'}
CARD_TYPES_NO_ARTWORK = {'Rules'}
CARD_TYPES_NO_ARTWORK_BACK = {'Campaign', 'Nightmare', 'Presentation', 'Rules'}
CARD_TYPES_EASY_MODE = {'Encounter Side Quest', 'Enemy', 'Location',
                        'Ship Enemy', 'Treachery'}
CARD_SPHERES_NO_EASY_MODE = {'Boon', 'Burden', 'Cave', 'NoStat', 'Region'}
CARD_TYPES_ADDITIONAL_ENCOUNTER_SETS = {'Quest'}
CARD_TYPES_ADVENTURE = {'Campaign', 'Objective', 'Objective Ally',
                        'Objective Hero', 'Objective Location',
                        'Quest', 'Ship Objective'}
CARD_TYPES_SUBTITLE = {'Campaign', 'Objective', 'Objective Ally',
                       'Objective Hero', 'Objective Location',
                       'Quest', 'Ship Objective'}
CARD_TYPES_NO_ICON = {'Full Art Landscape', 'Full Art Portrait', 'Rules'}
CARD_TYPES_NO_COPYRIGHT = {'Presentation', 'Rules'}
CARD_TYPES_DECK_RULES = {'Nightmare', 'Quest'}
CARD_TYPES_ONE_COPY = {'Campaign', 'Contract', 'Encounter Side Quest',
                       'Full Art Landscape', 'Full Art Portrait', 'Hero',
                       'Nightmare', 'Objective Hero', 'Presentation', 'Quest',
                       'Rules', 'Treasure'}
CARD_TYPES_THREE_COPIES = {'Ally', 'Attachment', 'Event', 'Player Objective',
                           'Player Side Quest'}
CARD_TYPES_BOON = {'Ally', 'Attachment', 'Event', 'Objective Ally'}
CARD_TYPES_BURDEN = {'Encounter Side Quest', 'Enemy', 'Objective', 'Treachery'}
CARD_TYPES_NIGHTMARE = {'Encounter Side Quest', 'Enemy', 'Location',
                        'Objective', 'Ship Enemy', 'Treachery', 'Quest'}
CARD_TYPES_NOSTAT = {'Enemy'}
CARD_TYPES_NO_DISCORD_CHANNEL = {'Full Art Landscape', 'Full Art Portrait',
                                 'Rules', 'Presentation'}
CARD_TYPES_NO_NAME_TAG = {'Campaign', 'Nightmare', 'Presentation', 'Rules'}

FLAGS = {'AdditionalCopies', 'Asterisk', 'IgnoreName', 'IgnoreRules',
         'NoArtist', 'NoCopyright', 'NoTraits', 'Promo', 'BlueRing',
         'GreenRing', 'RedRing'}
RING_FLAGS = {'BlueRing', 'GreenRing', 'RedRing'}
SPHERES = set()
SPHERES_CAMPAIGN = {'Setup'}
SPHERES_PLAYER = {'Baggins', 'Fellowship', 'Leadership', 'Lore', 'Neutral',
                  'Spirit', 'Tactics'}
SPHERES_PRESENTATION = {'Blue', 'Green', 'Purple', 'Red', 'Brown', 'Yellow',
                        'BlueNightmare', 'GreenNightmare', 'PurpleNightmare',
                        'RedNightmare', 'BrownNightmare', 'YellowNightmare'}
SPHERES_RULES = {'Back'}
SPHERES_SHIP_OBJECTIVE = {'Upgraded'}
SPHERES_SIDE_QUEST = {'Cave', 'NoProgress', 'Region', 'SmallTextArea'}
SPECIAL_ICONS = {'eye of sauron', 'eye of sauronx2', 'eye of sauronx3',
                 'sailing', 'sailingx2'}

DRAGNCARDS_PLAYER_CARDS_STAT_COMMAND = \
    '/home/webhost/python/AR/player_cards_stat.sh "{}" "{}" "{}"'
DRAGNCARDS_ALL_PLAYS_COMMAND = \
    '/home/webhost/python/AR/all_plays.sh "{}" "{}" "{}"'
DRAGNCARDS_PLAYS_STAT_COMMAND = \
    '/home/webhost/python/AR/plays_stat.sh "{}" "{}" "{}"'
DRAGNCARDS_QUESTS_STAT_COMMAND = \
    '/home/webhost/python/AR/quests_stat.sh "{}"'
DRAGNCARDS_BUILD_STAT_COMMAND = \
    '/var/www/dragncards.com/dragncards/frontend/buildStat.sh'
DRAGNCARDS_BUILD_TRIGGER_COMMAND = \
    '/var/www/dragncards.com/dragncards/frontend/buildTrigger.sh'
DRAGNCARDS_IMAGES_FINISH_COMMAND = \
    '/var/www/dragncards.com/dragncards/frontend/imagesFinish.sh'
DRAGNCARDS_IMAGES_START_COMMAND = \
    '/var/www/dragncards.com/dragncards/frontend/imagesStart.sh'
GENERATE_DRAGNCARDS_COMMAND = './generate_dragncards.sh {}'
GIMP_COMMAND = '"{}" -i -b "({} 1 \\"{}\\" \\"{}\\")" -b "(gimp-quit 0)"'
MAGICK_COMMAND_CMYK = '"{}" mogrify -profile USWebCoatedSWOP.icc "{}{}*.jpg"'
MAGICK_COMMAND_JPG = '"{}" mogrify -format jpg "{}{}*.png"'
MAGICK_COMMAND_LOW = '"{}" mogrify -resize 600x600 -format jpg "{}{}*.png"'
MAGICK_COMMAND_MBPRINT_PDF = '"{}" convert "{}{}*o.jpg" "{}"'
MAGICK_COMMAND_RULES_PDF = '"{}" convert "{}{}*.png" "{}"'

JPG_PREVIEW_MIN_SIZE = 20000
JPG_300_MIN_SIZE = 50000
JPG_480_MIN_SIZE = 150000
JPG_800_MIN_SIZE = 1000000
JPG_300CMYK_MIN_SIZE = 1000000
JPG_800CMYK_MIN_SIZE = 4000000
PNG_300_MIN_SIZE = 50000
PNG_480_MIN_SIZE = 300000
PNG_800_MIN_SIZE = 2000000

EASY_PREFIX = 'Easy '
GENERATED_FOLDER = 'generated'
IMAGES_CUSTOM_FOLDER = 'custom'
IMAGES_ICONS_FOLDER = 'icons'
OCTGN_SET_XML = 'set.xml'
PLAYTEST_SUFFIX = '-Playtest'
SCRATCH_FOLDER = '_Scratch'
TEXT_CHUNK_FLAG = b'tEXt'

DECK_PREFIX_REGEX = r'^[QN][A-Z0-9][A-Z0-9]\.[0-9][0-9]?[\- ]'
KEYWORDS_REGEX = (r'^(?: ?[A-Z][A-Za-z\'\-]+(?: [0-9X]+(?:\[pp\])?)?\.|'
                  r' ?Guarded \(enemy\)\.| ?Guarded \(location\)\.|'
                  r' ?Guarded \(enemy or location\)\.| ?Fate -1\.)+$')
UUID_REGEX = r'^[0-9a-h]{8}-[0-9a-h]{4}-[0-9a-h]{4}-[0-9a-h]{4}-[0-9a-h]{12}$'

JPG300BLEEDDTC = 'jpg300BleedDTC'
JPG800BLEEDMBPRINT = 'jpg800BleedMBPrint'
PNG300BLEED = 'png300Bleed'
PNG300DB = 'png300DB'
PNG300NOBLEED = 'png300NoBleed'
PNG300OCTGN = 'png300OCTGN'
PNG300PDF = 'png300PDF'
PNG300RULES = 'png300Rules'
PNG480BLEED = 'png480Bleed'
PNG480DRAGNCARDSHQ = 'png480DragnCardsHQ'
PNG480NOBLEED = 'png480NoBleed'
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

DATA_PATH = 'Data'
DISCORD_PATH = 'Discord'
DOCS_PATH = 'Docs'
OUTPUT_PATH = 'Output'
PROJECT_PATH = 'Frogmorton'
RENDERER_PATH = 'Renderer'
TEMP_ROOT_PATH = 'Temp'

CONFIGURATION_PATH = 'configuration.yaml'
DISCORD_CARD_DATA_PATH = os.path.join(DISCORD_PATH, 'Data', 'card_data.json')
DISCORD_TIMESTAMPS_PATH = os.path.join(DISCORD_PATH, 'Data', 'timestamps.json')
DOWNLOAD_PATH = 'Download'
DOWNLOAD_TIME_PATH = os.path.join(DATA_PATH, 'download_time.txt')
DRAGNCARDS_FILES_JSON_PATH = os.path.join(DATA_PATH, 'dragncards_files.json')
DRAGNCARDS_FOLDER_PATH = os.path.join(TEMP_ROOT_PATH, 'dragncards_folder.txt')
DRAGNCARDS_TIMESTAMPS_JSON_PATH = os.path.join(DATA_PATH,
                                               'dragncards_timestamps.json')
DRIVETHRUCARDS_PDF = os.path.join(DOCS_PATH, 'DriveThruCards.pdf')
EXPIRE_DRAGNCARDS_JSON_PATH = os.path.join(TEMP_ROOT_PATH,
                                           'expire_dragncards.json')
GENERATE_DRAGNCARDS_JSON_PATH = os.path.join(DATA_PATH,
                                             'generate_dragncards.json')
GENERATE_DRAGNCARDS_LOG_PATH = os.path.join(RENDERER_PATH, 'Output',
                                            'generate_dragncards.txt')
IMAGES_BACK_PATH = 'imagesBack'
IMAGES_CUSTOM_PATH = os.path.join(PROJECT_PATH, 'imagesCustom')
IMAGES_ICONS_PATH = os.path.join(PROJECT_PATH, 'imagesIcons')
IMAGES_EONS_PATH = 'imagesEons'
IMAGES_OTHER_PATH = 'imagesOther'
IMAGES_RAW_PATH = os.path.join(PROJECT_PATH, 'imagesRaw')
IMAGES_TTS_PATH = 'imagesTTS'
IMAGES_ZIP_PATH = '{}/Export/'.format(os.path.split(PROJECT_PATH)[-1])
MAKECARDS_FINISHED_PATH = 'makeCards_FINISHED'
MAKEPLAYINGCARDS_PDF = os.path.join(DOCS_PATH, 'MakePlayingCards.pdf')
MBPRINT_PDF = os.path.join(DOCS_PATH, 'MBPrint.pdf')
MESSAGES_ZIP_PATH = '{}/Messages/'.format(os.path.split(PROJECT_PATH)[-1])
OCTGN_ZIP_PATH = 'a21af4e8-be4b-4cda-a6b6-534f9717391f/Sets'
OUTPUT_DB_PATH = os.path.join(OUTPUT_PATH, 'DB')
OUTPUT_DRAGNCARDS_PATH = os.path.join(OUTPUT_PATH, 'DragnCards')
OUTPUT_DRAGNCARDS_HQ_PATH = os.path.join(OUTPUT_PATH, 'DragnCardsHQ')
OUTPUT_DTC_PATH = os.path.join(OUTPUT_PATH, 'DriveThruCards')
OUTPUT_FRENCHDB_PATH = os.path.join(OUTPUT_PATH, 'FrenchDB')
OUTPUT_FRENCHDB_IMAGES_PATH = os.path.join(OUTPUT_PATH, 'FrenchDBImages')
OUTPUT_GENERICPNG_PATH = os.path.join(OUTPUT_PATH, 'GenericPNG')
OUTPUT_GENERICPNG_PDF_PATH = os.path.join(OUTPUT_PATH, 'GenericPNGPDF')
OUTPUT_HALLOFBEORN_PATH = os.path.join(OUTPUT_PATH, 'HallOfBeorn')
OUTPUT_HALLOFBEORN_IMAGES_PATH = os.path.join(OUTPUT_PATH, 'HallOfBeornImages')
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
PIPELINE_STARTED_PATH = 'pipeline_STARTED'
RENDERER_GENERATED_IMAGES_PATH = os.path.join(RENDERER_PATH, 'GeneratedImages')
RENDERER_OUTPUT_PATH = os.path.join(RENDERER_PATH, 'Output')
REPROCESS_ALL_PATH = 'REPROCESS_ALL'
REPROCESS_COUNT_PATH = os.path.join(TEMP_ROOT_PATH, 'reprocess_count.json')
RINGSDB_COOKIES_PATH = 'ringsdb_test_cookies.json'
RINGSDB_JSON_PATH = os.path.join(DATA_PATH, 'ringsdb_sets.json')
RUN_BEFORE_SE_STARTED_PATH = 'runBeforeSE_STARTED'
SEPROJECT_PATH = 'setGenerator.seproject'
SEPROJECT_CREATED_PATH = 'setGenerator_CREATED'
SET_EONS_PATH = 'setEons'
SET_OCTGN_PATH = 'setOCTGN'
SHEETS_JSON_PATH = os.path.join(DATA_PATH, 'sheets.json')
URL_CACHE_PATH = 'urlCache'
XML_PATH = os.path.join(PROJECT_PATH, 'XML')
XML_ZIP_PATH = '{}/XML/'.format(os.path.split(PROJECT_PATH)[-1])

TTS_COLUMNS = 10
TTS_SHEET_SIZE = 69

REPROCESS_RETRIES = 5
LOG_LIMIT = 5000
SCP_RETRIES = 5
SCP_SLEEP = 30
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

CARD_TYPE_SUFFIX_HALLOFBEORN = {
    'Campaign': 'Setup',
    'Contract': 'Side',
    'Nightmare': 'Setup',
    'Presentation': 'Setup',
    'Rules': 'Setup'
}

CARD_TYPES_PLAYER_FRENCH = {'Ally', 'Attachment', 'Contract', 'Event', 'Hero',
                            'Player Objective', 'Player Side Quest',
                            'Treasure', 'Campaign', 'Objective Ally',
                            'Objective Hero', 'Ship Objective'}
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
    'Player Objective': 419,
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
    'Player Objective': 'Objetivo',
    'Player Side Quest': 'Misi\u00f3n Secundaria',
    'Quest': 'Misi\u00f3n',
    'Setup': 'Preparaci\u00f3n',
    'Ship Enemy': 'Barco-Enemigo',
    'Ship Objective': 'Barco-Objetivo',
    'Treachery': 'Traici\u00f3n',
    'Treasure': 'Tesoro'
}
RESTRICTED_TRANSLATION = {
    'English': 'Restricted',
    'French': 'Restreint',
    'German': 'Eingeschränkt',
    'Italian': 'Limitato',
    'Polish': 'Ograniczenie',
    'Portuguese': 'Restrito',
    'Spanish': 'Restringido'
}

KNOWN_BOOKS = {
    'The Hobbit', 'The Fellowship of the Ring', 'The Two Towers',
    'The Return of the King', 'The Silmarillion', 'The Fall of Gondolin'}
AUXILIARY_TRAITS = {
    'Abroad', 'Basic', 'Broken', 'Corrupt', 'Cursed', 'Elite', 'Epic',
    'Massing', 'Reforged', 'Standard', 'Suspicious', 'Upgraded'}
DESCRIPTIVE_LAST_TRAITS = {
    'Boar', 'Boar Clan', 'Captain', 'Flame', 'Lieutenant', 'Olog-hai',
    'Raven', 'Raven Clan', 'Uruk-hai', 'Wolf', 'Wolf Clan', 'Wolf-cult'}
DESCRIPTIVE_TRAITS = {
    'Archer', 'Assault', 'Attack', 'Besieger', 'Black Speech',
    'Brigand', 'Burglar', 'Capture', 'Captured', 'Champion', 'Clue',
    'Corruption', 'Craftsman', 'Cultist', 'Damaged', 'Defense', 'Despair',
    'Disaster', 'Doom', 'Enchantment', 'Escape', 'Fear', 'Fellowship', 'Food',
    'Found', 'Gossip', 'Guardian', 'Hazard', 'Healer', 'Hungry', 'Inferno',
    'Information', 'Instrument', 'Key', 'Light', 'Master', 'Mathom',
    'Minstrel', 'Mission', 'Mustering', 'Night', 'Panic', 'Party',
    'Pillager', 'Pipe', 'Pipeweed', 'Plot', 'Poison', 'Raider', 'Ranger',
    'Record', 'Refuge', 'Ring-bearer', 'Ruffian', 'Sack', 'Scheme', 'Scout',
    'Scroll', 'Search', 'Servant', 'Shadow', 'Sharkey', 'Shirriff', 'Song',
    'Sorcerer', 'Sorcery', 'Spy', 'Staff', 'Stalking', 'Steward', 'Summoned',
    'Summoner', 'Tantrum', 'Thaurdir', 'Thug', 'Time', 'Tools', 'Traitor',
    'Treasure', 'Villain', 'Warden', 'Warrior', 'Weather', 'Wound'}
LOCATION_SUBTYPE_TRAITS = {
    'Battleground', 'Besieged', 'Camp', 'Castle', 'Dark', 'Deck', 'Downs',
    'Fords', 'Fortification', 'Garrison', 'Gate', 'Hideout', 'Highlands',
    'Inn', 'Lair', 'Lawn', 'Marsh', 'Marshland', 'Pier', 'Polluted',
    'Riverland', 'Siege', 'Snow', 'Stair', 'Wasteland'}
LOCATION_TYPE_FIRST_TRAITS = {
    'Barrow', 'Blight', 'City', 'Desert', 'Forest', 'Mountain', 'Plains',
    'Ruins', 'Underground', 'Underwater', 'Village'}
LOCATION_TYPE_TRAITS = {
    'Bridge', 'Cave', 'Coastland', 'Dungeon', 'Grotto', 'Hills', 'Lake',
    'Ocean', 'River', 'Road', 'Ship', 'Stream', 'Swamp', 'Town', 'Vale',
    'Valley'}
NOBLE_TRAITS = {'Noble'}
RACE_FIRST_TRAITS = {'Creature', 'Nazgûl', 'Orc', 'Undead'}
RACE_TRAITS = {
    'Balrog', 'Beorning', 'Body', 'Corsair', 'Dale', 'Dorwinion', 'Dragon',
    'Dúnedain', 'Dunland', 'Dwarf', 'Eagle', 'Easterling', 'Ent', 'Giant',
    'Goblin', 'Gollum', 'Gondor', 'Harad', 'Hobbit', 'Huorn', 'Insect',
    'Istari', 'Legend', 'Mearas', 'Nameless', 'Noldor', 'Oathbreaker',
    'Outlands', 'Pony', 'Rat', 'Rohan', 'Silvan', 'Snaga', 'Spider', 'Spirit',
    'Tentacle', 'Tree', 'Troll', 'Uruk', 'Warg', 'Werewolf', 'Wight',
    'Woodman', 'Wose', 'Wraith'}
REGION_TRAITS = {
    'Aldburg', 'Angmar', 'Arnor', 'Blackroot Vale', 'Bree', 'Cair Andros',
    'Carn Dûm', 'Cirith Ungol', 'Dead Marshes', 'Dol Amroth', 'Dol Guldur',
    'East Bank', 'Eastfarthing', 'Emyn Muil', 'Enedwaith', 'Erebor',
    'Esgaroth', 'Ettenmoors', 'Fornost', 'Grey Havens', 'Helm’s Deep',
    'Isengard', 'Ithilien', 'Lake-town', 'Lossoth', 'Lórien', 'Minas Tirith',
    'Mirkwood', 'Mordor', 'Osgiliath', 'Ost-in-Edhil', 'Pelennor',
    'Shire', 'Trollshaws', 'Umbar', 'Underworld', 'West Bank',
    'Western Lands', 'Westfarthing', 'Westfold', 'Wilderlands'}
TYPE_FIRST_TRAITS = {
    'Artifact', 'Item', 'Suspect', 'Stronghold'}
TYPE_TRAITS = {
    'Adaptation', 'Armor', 'Assassin', 'Boon', 'Captive', 'Condition', 'Favor',
    'Gift', 'Morgul', 'Mount', 'Ring', 'Signal', 'Skill', 'Spell', 'Tale',
    'Title', 'Trap', 'Weapon'}
TRAITS_ORDER = [TYPE_FIRST_TRAITS, TYPE_TRAITS, RACE_FIRST_TRAITS,
                RACE_TRAITS, REGION_TRAITS, LOCATION_TYPE_FIRST_TRAITS,
                LOCATION_TYPE_TRAITS, LOCATION_SUBTYPE_TRAITS, NOBLE_TRAITS,
                DESCRIPTIVE_TRAITS, DESCRIPTIVE_LAST_TRAITS, AUXILIARY_TRAITS]
COMMON_TRAITS = set.union(*(TRAITS_ORDER + [{'Trait', 'Traits'}]))

ALLOWED_CAMPAIGN_NAMES = {
    'Campaign Mode'
}
ALLOWED_RULES_NAMES = {
    'Difficulty'
}
ALLOWED_FIRST_WORDS = {
    'A',
    'Add',
    'After',
    'All',
    'Allies',
    'Any',
    'At',
    'Attach',
    'Attached',
    'Attachments',
    'Attacking',
    'Before',
    'Cancel',
    'Cannot',
    'Characters',
    'Choose',
    'Counts',
    'Damage',
    'Deal',
    'Decrease',
    'Defending',
    'Discard',
    'Draw',
    'During',
    'Each',
    'Either',
    'End',
    'Enemies',
    'Engage',
    'Enters',
    'Excess',
    'Exhaust',
    'Flip',
    'For',
    'Heal',
    'Heroes',
    'If',
    'Its',
    'Immune',
    'Increase',
    'Instead',
    'Limit',
    'Locations',
    'Make',
    'Move',
    'Name',
    'One',
    'Only',
    'Otherwise',
    'Pay',
    'Place',
    'Play',
    'Player',
    'Players',
    'Progress',
    'Put',
    'Raise',
    'Randomly',
    'Ready',
    'Reduce',
    'Remove',
    'Replace',
    'Resolve',
    'Return',
    'Reveal',
    'Search',
    'Set',
    'Skip',
    'Shuffle',
    'Spend',
    'The',
    'Then',
    'ThenIf',
    'There',
    'They',
    'That',
    'This',
    'Treat',
    'Turn',
    'Until',
    'When',
    'While',
    'You',
    'Your'
}
COMMON_ACCENTS = {'Annuminas', 'Cuarthol', 'Din', 'Druadan', 'Druedain',
                  'Dum', 'dum', 'Dunedain', 'Iarion', 'Lorien', 'Mumakil',
                  'Nazgul', 'Nin', 'Numenor', 'Rhun'}
COMMON_KEYWORDS = {'Devoted', 'Doomed', 'Encounter', 'Guarded', 'Ranged',
                   'Restricted', 'Secrecy', 'Sentinel', 'Surge'}
LOWERCASE_WORDS = {
    'a', 'an', 'the', 'and', 'as', 'at', 'but', 'by', 'for', 'from', 'if',
    'in', 'into', 'nor', 'of', 'on', 'onto', 'or', 'out', 'so', 'than',
    'that', 'to', 'up', 'with', 'am', 'are', 'is', 'was', 'were', 'sonof_'}

CARD_COLUMNS = {}
SHEET_IDS = {}
SETS = {}
DATA = []
ACCENTS = set()
ALL_NAMES = set()
ALL_SET_AND_QUEST_NAMES = set()
ALL_ENCOUNTER_SET_NAMES = set()
ALL_CARD_NAMES = set()
ALL_SCRATCH_CARD_NAMES = set()
ALL_TRAITS = set()
ALL_SCRATCH_TRAITS = set()
PRE_SANITY_CHECK = {}
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


class DragnCardsError(Exception):
    """ DragnCards error.
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
        with open(RINGSDB_COOKIES_PATH, 'r', encoding='utf-8') as fobj:
            data = json.load(fobj)
    except Exception:
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
    with open(RINGSDB_COOKIES_PATH, 'w', encoding='utf-8') as fobj:
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


def is_int(value):
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


def _is_float(value):
    """ Check whether a value is a float or not.
    """
    try:
        value = float(value)
        return True
    except (TypeError, ValueError):
        return False


def _is_positive_float(value):
    """ Check whether a value is a positive float or not.
    """
    try:
        value = float(value)
        return value > 0
    except (TypeError, ValueError):
        return False


def handle_int(value):
    """ Handle (not always) integer values.
    """
    if is_int(value):
        return int(value)

    return value


def _handle_int_str(value):
    """ Handle (not always) integer values and convert them to string.
    """
    if is_int(value):
        return str(int(value))

    return value


def _to_str(value):
    """ Convert value to string if needed.
    """
    return '' if value is None else str(value)


def _detect_unmatched_tags(text):
    """ Detect unmatched tags.
    """
    errors = []
    text_copy = text
    # 'right' is removed from the list to make the life of translators easier
    for tag in ('center', 'b', 'i', 'bi', 'u', 'strike', 'red'):
        text = text_copy
        text = re.sub(r'\[{}\].+?\[\/{}\]'.format(tag, tag), '', text,  # pylint: disable=W1308
                      flags=re.DOTALL)
        open_tag = '[{}]'.format(tag)
        if open_tag in text:
            errors.append(open_tag)

        close_tag = '[/{}]'.format(tag)
        if close_tag in text:
            errors.append(close_tag)

    for tag in ('lotr', 'lotrheader', 'size'):
        text = text_copy
        text = re.sub(r'\[{} .+?\[\/{}\]'.format(tag, tag), '', text,  # pylint: disable=W1308
                      flags=re.DOTALL)
        if '[{} '.format(tag) in text:
            errors.append('[{}]'.format(tag))

        close_tag = '[/{}]'.format(tag)
        if close_tag in text:
            errors.append(close_tag)

    return errors


def _clean_tags(text):  # pylint: disable=R0915
    """ Clean known tags from the text.
    """
    text = text.replace('[center]', '')
    text = text.replace('[/center]', '')
    text = text.replace('[right]', '')
    text = text.replace('[/right]', '')
    text = text.replace('[b]', '')
    text = text.replace('[/b]', '')
    text = text.replace('[i]', '')
    text = text.replace('[/i]', '')
    text = text.replace('[bi]', '')
    text = text.replace('[/bi]', '')
    text = text.replace('[u]', '')
    text = text.replace('[/u]', '')
    text = text.replace('[strike]', '')
    text = text.replace('[/strike]', '')
    text = text.replace('[red]', '')
    text = text.replace('[/red]', '')
    text = text.replace('[space]', '')
    text = text.replace('[vspace]', '')
    text = text.replace('[tab]', '')
    text = text.replace('[nobr]', '')
    text = text.replace('[inline]', '')
    text = text.replace('[lsb]', '')
    text = text.replace('[rsb]', '')
    text = text.replace('[lfb]', '')
    text = text.replace('[rfb]', '')
    text = text.replace('[split]', '')

    text = re.sub(r'\[lotr [^\]]+\]', '', text)
    text = re.sub(r'\[lotrheader [^\]]+\]', '', text)
    text = re.sub(r'\[size [^\]]+\]', '', text)
    text = re.sub(r'\[defaultsize [^\]]+\]', '', text)
    text = re.sub(r'\[img [^\]]+\]', '', text)

    text = text.replace('[/lotr]', '')
    text = text.replace('[/lotrheader]', '')
    text = text.replace('[/size]', '')

    text = text.replace('[unique]', '')
    text = text.replace('[threat]', '')
    text = text.replace('[attack]', '')
    text = text.replace('[defense]', '')
    text = text.replace('[willpower]', '')
    text = text.replace('[leadership]', '')
    text = text.replace('[lore]', '')
    text = text.replace('[spirit]', '')
    text = text.replace('[tactics]', '')
    text = text.replace('[baggins]', '')
    text = text.replace('[fellowship]', '')
    text = text.replace('[sunny]', '')
    text = text.replace('[cloudy]', '')
    text = text.replace('[rainy]', '')
    text = text.replace('[stormy]', '')
    text = text.replace('[sailing]', '')
    text = text.replace('[eos]', '')
    text = text.replace('[pp]', '')

    text = text.replace('[unmatched quot]', '')
    return text


def _update_card_text(text, lang='English', skip_rules=False,  # pylint: disable=R0915
                      fix_linebreaks=True):
    """ Update card text for RingsDB, Hall of Beorn, French and Spanish DBs.
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

    text = text.replace('[center]', '')
    text = text.replace('[/center]', '')
    text = text.replace('[right]', '')
    text = text.replace('[/right]', '')
    text = text.replace('[bi]', '<b><i>')
    text = text.replace('[/bi]', '</i></b>')
    text = text.replace('[b]', '<b>')
    text = text.replace('[/b]', '</b>')
    text = text.replace('[i]', '<i>')
    text = text.replace('[/i]', '</i>')
    text = text.replace('[u]', '')
    text = text.replace('[/u]', '')
    text = text.replace('[strike]', '')
    text = text.replace('[/strike]', '')
    text = text.replace('[red]', '')
    text = text.replace('[/red]', '')
    text = text.replace('[space]', ' ')
    text = text.replace('[vspace]', ' ')
    text = text.replace('[tab]', '    ')
    text = text.replace('[nobr]', ' ')
    text = text.replace('[lsb]', '[')
    text = text.replace('[rsb]', ']')
    text = text.replace('[split]', '')

    text = re.sub(r'\[lotr [^\]]+\]', '', text)
    text = re.sub(r'\[lotrheader [^\]]+\]', '', text)
    text = re.sub(r'\[size [^\]]+\]', '', text)
    text = re.sub(r'\[defaultsize [^\]]+\]', '', text)
    text = re.sub(r'\[img [^\]]+\]', '', text)
    text = re.sub(r'\[inline\]\n+', ' ', text)

    text = text.replace('[inline]', '')
    text = text.replace('[/lotr]', '')
    text = text.replace('[/lotrheader]', '')
    text = text.replace('[/size]', '')

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
    text = re.sub(r'(?:<b>|<\/b>|<i>|<\/i>)', '', text)

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
    text = re.sub(r'(?:<b>|<\/b>|<i>|<\/i>)', '', text)
    return text


def _get_french_icon(name):
    """ Get the icon for the French database.
    """
    return ('<img src="https://sda-src.cgbuilder.fr/images/carte_{}.png" '  # pylint: disable=W1308
            'alt="{}" />'.format(name, name))


def _update_french_card_text(text):
    """ Update card text for French DB.
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
    """ Escape forbidden characters in a file name.
    """
    value = re.sub(r'[<>:\/\\|?*\'"’“”„«»…–—¡¿]', ' ', str(value))
    value = value.encode('ascii', errors='replace').decode().replace('?', ' ')
    value = value.strip()
    return value


def escape_octgn_filename(value):
    """ Replace spaces in a file name for OCTGN.
    """
    return value.replace(' ', '-')


def _escape_hallofbeorn_filename(value):
    """ Escape forbidden characters in a Hall of Beorn file name.
    """
    value = re.sub(r'[.,!<>:\/\\|?*"“”„«»…¡¿]', '', str(value))
    value = (value.replace(' - ', '-').replace('’', "'").replace('_', '-')
             .replace('–', '-').replace('—', '-').replace('&', 'and'))
    value = value.strip()
    value = value.replace(' ', '-')
    value = re.sub(r'(png|jpg)$', '.\\1', value)
    return value


def _escape_icon_filename(value):
    """ Escape forbidden characters in an icon file name.
    """
    value = re.sub(r'[<>:\/\\|?*\'"’“”„«»…–—¡¿]', '', str(value))
    value = value.strip()
    value = value.replace(' ', '-')
    return value


def simplify_keyword(keyword):
    """ Simplify a given keyword.
    """
    keyword = re.sub(r' \([^)]+\)$', '',
                     re.sub(r' [0-9X]+$', '',
                            keyword.replace(' Per Player', '')))
    return keyword


def extract_keywords(value):
    """ Extract all keywords from the string.
    """
    keywords = [k.strip() for k in str(value or '').replace(
                '[inline]', '').split('.') if k.strip() != '']
    keywords = [re.sub(r' ([0-9]+)\[pp\]$', ' \\1 Per Player', k, re.I)
                for k in keywords]
    return keywords


def extract_traits(value):
    """ Extract all traits from the string.
    """
    value = re.sub(r'\[[^\]]+\]', '', str(value or ''))
    traits = [t.strip() for t in value.split('.') if t.strip() != '']
    return traits


def verify_traits_order(traits):
    """ Verify the order of card traits.
    """
    if not traits:
        return (True, [])

    traits = [t.strip() for t in traits.split('.') if t.strip()]
    ordered_traits = []
    for trait_type in TRAITS_ORDER:
        ordered_traits.extend(sorted([t for t in traits if t in trait_type]))

    ordered_traits_formatted = ' '.join(['{}.'.format(t)
                                         for t in ordered_traits])
    if not ordered_traits_formatted:
        ordered_traits_formatted = '-'

    return (traits == ordered_traits, ordered_traits_formatted)


def clear_folder(folder):
    """ Clear the folder.
    """
    if not os.path.exists(folder):
        return

    for _, _, filenames in os.walk(folder):
        for filename in filenames:
            if filename not in ('seproject', '.gitignore', 'desktop.ini'):
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
            if filename.endswith('.jpg') or filename.endswith('.png'):
                card_id = filename[50:86]
                if card_id not in skip_ids:
                    os.remove(os.path.join(folder, filename))

        break


def _update_zip_filename(filename):
    """ Update filename found in the project archive.
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

    with open(path, 'r', encoding='utf-8') as f_conf:
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
    conf['nobleed_480'] = {}
    conf['nobleed_800'] = {}  # not used at the moment

    if not conf['set_ids']:
        conf['set_ids'] = []

    if not conf['ignore_set_ids']:
        conf['ignore_set_ids'] = []

    if not conf['set_ids_octgn_image_destination']:
        conf['set_ids_octgn_image_destination'] = []

    if not 'offline_mode' in conf:
        conf['offline_mode'] = False

    conf['validate_missing_images'] = False

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

        if ('pdf' in conf['outputs'][lang]  # pylint: disable=R0916
                or 'mbprint' in conf['outputs'][lang]
                or 'makeplayingcards' in conf['outputs'][lang]
                or 'drivethrucards' in conf['outputs'][lang]
                or 'dragncards_hq' in conf['outputs'][lang]
                or 'genericpng' in conf['outputs'][lang]
                or 'genericpng_pdf' in conf['outputs'][lang]):
            conf['validate_missing_images'] = True

        conf['nobleed_300'][lang] = ('db' in conf['outputs'][lang]
                                     or 'octgn' in conf['outputs'][lang]
                                     or 'rules_pdf' in conf['outputs'][lang])
        conf['nobleed_480'][lang] = 'dragncards_hq' in conf['outputs'][lang]
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

    nobleed_folder = os.path.join(IMAGES_EONS_PATH, PNG480NOBLEED)
    for _, subfolders, _ in os.walk(nobleed_folder):
        for subfolder in subfolders:
            delete_folder(os.path.join(nobleed_folder, subfolder))

        break

    nobleed_folder = os.path.join(IMAGES_EONS_PATH, PNG800NOBLEED)
    for _, subfolders, _ in os.walk(nobleed_folder):
        for subfolder in subfolders:
            delete_folder(os.path.join(nobleed_folder, subfolder))

        break

    input_path = os.path.join(conf['artwork_path'], IMAGES_ICONS_FOLDER)
    if os.path.exists(input_path):
        for _, _, filenames in os.walk(input_path):
            for filename in filenames:
                if not filename.endswith('.png'):
                    continue

                shutil.copyfile(os.path.join(input_path, filename),
                                os.path.join(IMAGES_ICONS_PATH, filename))

            break

    logging.info('...Resetting the project folders (%ss)',
                 round(time.time() - timestamp, 3))


def get_content(url):
    """ Get URL content.
    """
    for i in range(URL_RETRIES):
        try:
            req = requests.get(url, timeout=URL_TIMEOUT)
            res = req.content
            break
        except Exception:
            if i < URL_RETRIES - 1:
                time.sleep(URL_SLEEP * (i + 1))
            else:
                raise

    return res


def _get_cached_content(url, content_type):
    """ Find URL's content in the cache first.
    """
    path = os.path.join(URL_CACHE_PATH, '{}.{}.cache'.format(
        re.sub(r'[^A-Za-z0-9_\.\-]', '', url), content_type))
    if os.path.exists(path):
        with open(path, 'rb') as obj:
            content = obj.read()
            return content

    return None


def _save_content(url, content, content_type):
    """ Save URL's content into cache.
    """
    path = os.path.join(URL_CACHE_PATH, '{}.{}.cache'.format(
        re.sub(r'[^A-Za-z0-9_\.\-]', '', url), content_type))
    with open(path, 'wb') as obj:
        obj.write(content)


def _fix_csv_value(value):
    """ Extract a single value.
    """
    if value == '':
        return None

    if value == 'FALSE':
        return None

    if is_int(value):
        return int(value)

    return value


def download_sheet(conf):  # pylint: disable=R0912,R0914,R0915
    """ Download cards spreadsheet from Google Sheets.
    """
    logging.info('Downloading cards spreadsheet from Google Sheets...')
    timestamp = time.time()

    utc_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    changes = False
    scratch_changes = False
    sheets = [SET_SHEET, CARD_SHEET, SCRATCH_SHEET]
    for lang in set(conf['languages']).difference(set(['English'])):
        sheets.append(lang)

    if conf['offline_mode']:
        logging.info('SWITCHING TO OFFLINE MODE')

    if [sheet for sheet in sheets if sheet not in SHEET_IDS]:
        logging.info('Obtaining sheet IDs')
        SHEET_IDS.clear()
        url = (
            'https://docs.google.com/spreadsheets/d/{}/export?format=csv'
            .format(conf['sheet_gdid']))
        res = _get_cached_content(url, 'csv') if conf['offline_mode'] else None
        if res:
            res = res.decode('utf-8')
            SHEET_IDS.update(dict(row for row in csv.reader(res.splitlines())))
        else:
            res_raw = get_content(url)
            res = res_raw.decode('utf-8')
            if not res or '<html' in res:
                raise SheetError("Can't download the Google Sheet")

            try:
                SHEET_IDS.update(dict(row for row in
                                      csv.reader(res.splitlines())))
            except ValueError as exc:
                raise SheetError("Can't download the Google Sheet") from exc

            if conf['offline_mode']:
                _save_content(url, res_raw, 'csv')

        missing_sheets = [sheet for sheet in sheets
                          if sheet not in SHEET_IDS and sheet != SCRATCH_SHEET]
        if missing_sheets:
            raise SheetError("Can't find sheet ID(s) for the following "
                             "sheet(s): {}".format(', '.join(missing_sheets)))

    try:
        with open(SHEETS_JSON_PATH, 'r', encoding='utf-8') as fobj:
            old_checksums = json.load(fobj)
    except Exception:
        old_checksums = {}

    new_checksums = {}
    for sheet in sheets:
        if sheet not in SHEET_IDS:
            data = []
        else:
            url = (
                'https://docs.google.com/spreadsheets/d/{}/export?'
                'format=csv&gid={}'.format(conf['sheet_gdid'],
                                           SHEET_IDS[sheet]))
            res = (_get_cached_content(url, 'csv') if conf['offline_mode']
                   else None)
            if res:
                res = res.decode('utf-8')
                data = list(csv.reader(StringIO(res)))
                none_index = (data[0].index('') if '' in data[0]
                              else len(data[0]))
            else:
                res_raw = get_content(url)
                res = res_raw.decode('utf-8')
                if not res or '<html' in res:
                    raise SheetError("Can't download {} from the Google Sheet"
                                     .format(sheet))

                try:
                    data = list(csv.reader(StringIO(res)))
                    none_index = (data[0].index('') if '' in data[0]
                                  else len(data[0]))
                except Exception as exc:
                    raise SheetError("Can't download {} from the Google Sheet"
                                     .format(sheet)) from exc

                if conf['offline_mode']:
                    _save_content(url, res_raw, 'csv')

        data = [row[:none_index] for row in data]
        data = [[_fix_csv_value(v) for v in row] for row in data]
        while data and not any(data[-1]):
            data.pop()

        JSON_CACHE[sheet] = data
        res = json.dumps(data)
        new_checksums[sheet] = hashlib.md5(res.encode('utf-8')).hexdigest()
        if new_checksums[sheet] != old_checksums.get(sheet, ''):
            logging.info('Sheet %s changed', sheet)

            # we can't do that, because we need to include scratch artwork ids
            # into card_data.json
            # if sheet != SCRATCH_SHEET:
            #     changes = True
            # if sheet in (SET_SHEET, SCRATCH_SHEET):
            #    scratch_changes = True

            changes = True
            scratch_changes = True

            path = os.path.join(DOWNLOAD_PATH, '{}.json'.format(sheet))
            with open(path, 'w', encoding='utf-8') as fobj:
                fobj.write(res)

    if changes or scratch_changes:
        with open(SHEETS_JSON_PATH, 'w', encoding='utf-8') as fobj:
            json.dump(new_checksums, fobj)

        with open(DOWNLOAD_TIME_PATH, 'w', encoding='utf-8') as fobj:
            fobj.write(utc_time)

    logging.info('...Downloading cards spreadsheet from Google Sheets (%ss)',
                 round(time.time() - timestamp, 3))
    return (changes, scratch_changes)


def _update_discord_category(category):
    """ Update the name of a Discord category.
    """
    category = category.replace('“', '"')
    category = category.replace('”', '"')
    category = category.replace('’', "'")
    category = category.replace('…', '')
    category = category.replace('–', '-')
    category = category.replace('—', '-')
    return category


def _extract_all_card_names(data):
    """ Collect all card names from the spreadsheet.
    """
    ALL_CARD_NAMES.clear()
    ALL_SCRATCH_CARD_NAMES.clear()
    for row in data:
        if row[CARD_TYPE] in CARD_TYPES_NO_NAME_TAG:
            continue

        if row[CARD_SCRATCH]:
            clean_value = _clean_value(row[CARD_NAME])
            if clean_value:
                ALL_SCRATCH_CARD_NAMES.add(clean_value)

            clean_value = _clean_value(row[CARD_SIDE_B])
            if clean_value:
                ALL_SCRATCH_CARD_NAMES.add(clean_value)
        else:
            clean_value = _clean_value(row[CARD_NAME])
            if clean_value:
                ALL_CARD_NAMES.add(clean_value)

            clean_value = _clean_value(row[CARD_SIDE_B])
            if clean_value:
                ALL_CARD_NAMES.add(clean_value)


def _extract_all_set_and_quest_names(data):
    """ Collect all set and quest names from the spreadsheet.
    """
    ALL_SET_AND_QUEST_NAMES.clear()
    for row in data:
        if not row[CARD_SCRATCH]:
            if row[CARD_SET_NAME]:
                ALL_SET_AND_QUEST_NAMES.add(re.sub(r'^ALeP - ', '',
                                                   row[CARD_SET_NAME]))

            if (row[CARD_ADVENTURE] and
                    row[CARD_ADVENTURE] not in ('[space]', '[nobr]') and
                    row[CARD_TYPE] != 'Campaign'):
                ALL_SET_AND_QUEST_NAMES.add(row[CARD_ADVENTURE])


def _extract_all_encounter_set_names(data):
    """ Collect all encounter set names from the spreadsheet.
    """
    ALL_ENCOUNTER_SET_NAMES.clear()
    for row in data:
        if not row[CARD_SCRATCH]:
            if row[CARD_ENCOUNTER_SET]:
                ALL_ENCOUNTER_SET_NAMES.add(row[CARD_ENCOUNTER_SET])


def _extract_all_traits(data):
    """ Collect all traits from the spreadsheet.
    """
    ALL_TRAITS.clear()
    ALL_SCRATCH_TRAITS.clear()
    for row in data:
        if row[CARD_SCRATCH]:
            if row[CARD_TRAITS]:
                ALL_SCRATCH_TRAITS.update(extract_traits(row[CARD_TRAITS]))

            if row[BACK_PREFIX + CARD_TRAITS]:
                ALL_SCRATCH_TRAITS.update(
                    extract_traits(row[BACK_PREFIX + CARD_TRAITS]))
        else:
            if row[CARD_TRAITS]:
                ALL_TRAITS.update(extract_traits(row[CARD_TRAITS]))

            if row[BACK_PREFIX + CARD_TRAITS]:
                ALL_TRAITS.update(
                    extract_traits(row[BACK_PREFIX + CARD_TRAITS]))


def _extract_all_names():
    """ Collect all names from the spreadsheet.
    """
    ALL_NAMES.clear()
    ALL_NAMES.update(ALL_CARD_NAMES)
    ALL_NAMES.update(ALL_SET_AND_QUEST_NAMES)
    ALL_NAMES.update(ALL_ENCOUNTER_SET_NAMES)
    ALL_NAMES.update(ALL_TRAITS)


def _get_accents(name):
    """ Get words with accents from the name.
    """
    words = re.findall(r'\w+', name)
    words = [unidecode.unidecode(w) for w in words
             if not re.match(r'^[a-z0-9]+$', w, flags=re.IGNORECASE)]
    return set(words)


def _extract_all_accents():
    """ Collect all known words with accents.
    """
    ACCENTS.clear()
    ACCENTS.update(COMMON_ACCENTS)
    for name in ALL_NAMES:
        ACCENTS.update(_get_accents(name))


def _clean_value(value):  # pylint: disable=R0915
    """ Clean a value from the spreadsheet.
    """
    if not value:
        return None

    value = str(value).strip()
    value = value.replace('\t', ' ')
    value = value.replace('\r\n', '\n')
    value = value.replace('\r', '\n')
    value = value.replace('{', '[bi]')
    value = value.replace('}', '[/bi]')
    value = value.replace('[lfb]', '{')
    value = value.replace('[rfb]', '}')
    value = value.replace('`', "'")
    value = value.replace('\xa0', ' ')
    value = value.replace('...', '…')
    value = value.replace('---', '—')
    value = value.replace('--', '–')
    value = value.replace('−', '-')
    value = re.sub(r' -(?=[0-9X])', ' –', value)
    value = re.sub(r' —(?=[0-9X])', ' –', value)
    value = value.replace('[hyphen]', '-')
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
    value = value.replace('[lquot]', '“')
    value = value.replace('[rquot]', '”')
    value = value.replace('[lfquot]', '«')
    value = value.replace('[rfquot]', '»')
    value = value.replace('[quot]', '"')
    value = value.replace('[apos]', "'")
    while True:
        value_old = value
        value = re.sub(r'[“”]([^\[]*)\]', '"\\1]', value)
        value = re.sub(r'’([^\[]*)\]', "'\\1]", value)
        value = re.sub(r'…([^\[]*)\]', "...\\1]", value)
        value = re.sub(r'—([^\[]*)\]', "---\\1]", value)
        value = re.sub(r'–([^\[]*)\]', "--\\1]", value)
        if value == value_old:
            break

    value = re.sub(r' +(?=\n)', '', value)
    value = re.sub(r' +', ' ', value)

    if len(value) == 1:
        value = value.upper()

    if value == '':
        value = None

    return value


def get_similar_names(value, card_names, scratch_card_names=None):
    """ Get similar card names.
    """
    value_regex = r'\b' + re.escape(value) + r'\b'
    res = {n for n in card_names if re.search(value_regex, n) and value != n}
    if scratch_card_names:
        res_scratch = {n for n in scratch_card_names
                       if re.search(value_regex, n) and value != n}
        res.update(res_scratch)

    return res


def parse_flavour(value):
    """ Parse the flavour text and detect possible issues.
    """
    separator = ' '
    is_valid_quote = False
    errors = []
    if (value.count('—') > 1 or re.search(r'\s-', value) or
            re.search(r'-\s', value)):
        parts = [value]
        errors.append('Incorrectly formatted flavour text: {}'.format(value))
        return (parts, errors, is_valid_quote, separator)

    parts = re.split(r'[—–]', value[::-1], maxsplit=1)
    parts = [p[::-1] for p in parts][::-1]
    if len(parts) == 2 and parts[0].endswith('\n'):
        separator = '\n'

    parts = [p.strip() for p in parts]
    if len(parts) == 2:
        false_split = '—' not in value and re.search(r' –\s[a-z][^–]+$', value)
        source_parts = [p.strip() for p in parts[-1].split(', ')]
        if len(source_parts) > 2:
            if false_split:
                parts = [value]
            else:
                errors.append(
                    'Incorrectly formatted flavour text: {}'.format(value))
        else:
            if source_parts[-1] not in KNOWN_BOOKS:
                if false_split:
                    parts = [value]
                else:
                    errors.append('Unknown book: {}'.format(value))
                    if len(source_parts) == 2:
                        parts = [parts[0], source_parts[0], source_parts[1]]
            else:
                is_valid_quote = True
                if len(source_parts) == 2:
                    parts = [parts[0], source_parts[0], source_parts[1]]

    return (parts, errors, is_valid_quote, separator)


def _clean_data(data, lang):  # pylint: disable=R0912,R0914,R0915
    """ Clean data from the spreadsheet.
    """
    PRE_SANITY_CHECK.clear()

    auto_page_rows = []
    for i, row in enumerate(data):  # pylint: disable=R1702
        card_name = _clean_value(row.get(CARD_NAME)) or ''
        if len(card_name) == 1:
            card_name = card_name.upper()

        card_name_back = _clean_value(row.get(CARD_SIDE_B)) or ''
        if len(card_name_back) == 1:
            card_name_back = card_name_back.upper()

        if not card_name_back:
            card_name_back = card_name

        if (lang == 'English' and card_name and  # pylint: disable=R0916
                (not row[CARD_SCRATCH] or
                 card_name not in ALL_SCRATCH_TRAITS) and
                row[CARD_TYPE] not in CARD_TYPES_NO_NAME_TAG and
                not (row[CARD_FLAGS] and
                     'IgnoreName' in extract_flags(row[CARD_FLAGS]))):
            card_name_regex = r'(?<!\[bi\])\b' + re.escape(card_name) + r'\b'
        else:
            card_name_regex = None

        if (lang == 'English' and card_name_back and  # pylint: disable=R0916
                (not row[CARD_SCRATCH] or
                 card_name_back not in ALL_SCRATCH_TRAITS) and
                row[BACK_PREFIX + CARD_TYPE] not in CARD_TYPES_NO_NAME_TAG and
                not (row[BACK_PREFIX + CARD_FLAGS] and
                     'IgnoreName' in
                     extract_flags(row[BACK_PREFIX + CARD_FLAGS]))):
            card_name_regex_back = (
                r'(?<!\[bi\])\b' + re.escape(card_name) + r'\b')
        else:
            card_name_regex_back = None

        for key, value in row.items():
            if not isinstance(value, str):
                continue

            value = _clean_value(value)
            if not value:
                row[key] = value
                continue

            if card_name_regex:
                if key == CARD_TEXT and re.search(card_name_regex, value):
                    prepared_value = value
                    similar_names = get_similar_names(
                        card_name, ALL_CARD_NAMES,
                        row[CARD_SCRATCH] and ALL_SCRATCH_CARD_NAMES or None)
                    for similar_name in similar_names:
                        similar_name_regex = (
                            r'(?<!\[bi\])\b' + re.escape(similar_name) +
                            r'\b')
                        prepared_value = re.sub(similar_name_regex, '',
                                                prepared_value)

                    if re.search(card_name_regex, prepared_value):
                        error = ('Hardcoded card name instead of [name] '
                                 'in text')
                        PRE_SANITY_CHECK.setdefault(
                            (row[ROW_COLUMN], row[CARD_SCRATCH]),
                            []).append(error)
                elif (key == CARD_SHADOW and
                      re.search(card_name_regex, value)):
                    prepared_value = value
                    similar_names = get_similar_names(
                        card_name, ALL_CARD_NAMES,
                        row[CARD_SCRATCH] and ALL_SCRATCH_CARD_NAMES or None)
                    for similar_name in similar_names:
                        similar_name_regex = (
                            r'(?<!\[bi\])\b' + re.escape(similar_name) +
                            r'\b')
                        prepared_value = re.sub(similar_name_regex, '',
                                                prepared_value)

                    if re.search(card_name_regex, prepared_value):
                        error = ('Hardcoded card name instead of [name] '
                                 'in shadow')
                        PRE_SANITY_CHECK.setdefault(
                            (row[ROW_COLUMN], row[CARD_SCRATCH]),
                            []).append(error)

            if card_name_regex_back:
                if (key == BACK_PREFIX + CARD_TEXT and
                        re.search(card_name_regex_back, value)):
                    prepared_value = value
                    similar_names = get_similar_names(
                        card_name_back, ALL_CARD_NAMES,
                        row[CARD_SCRATCH] and ALL_SCRATCH_CARD_NAMES or None)
                    for similar_name in similar_names:
                        similar_name_regex = (
                            r'(?<!\[bi\])\b' + re.escape(similar_name) +
                            r'\b')
                        prepared_value = re.sub(similar_name_regex, '',
                                                prepared_value)

                    if re.search(card_name_regex_back, prepared_value):
                        error = ('Hardcoded card name instead of [name] '
                                 'in text back')
                        PRE_SANITY_CHECK.setdefault(
                            (row[ROW_COLUMN], row[CARD_SCRATCH]),
                            []).append(error)
                elif (key == BACK_PREFIX + CARD_SHADOW and
                          re.search(card_name_regex_back, value)):
                    prepared_value = value
                    similar_names = get_similar_names(
                        card_name_back, ALL_CARD_NAMES,
                        row[CARD_SCRATCH] and ALL_SCRATCH_CARD_NAMES or None)
                    for similar_name in similar_names:
                        similar_name_regex = (
                            r'(?<!\[bi\])\b' + re.escape(similar_name) +
                            r'\b')
                        prepared_value = re.sub(similar_name_regex, '',
                                                prepared_value)

                    if re.search(card_name_regex_back, prepared_value):
                        error = ('Hardcoded card name instead of [name] '
                                 'in shadow back')
                        PRE_SANITY_CHECK.setdefault(
                            (row[ROW_COLUMN], row[CARD_SCRATCH]),
                            []).append(error)

            if key != CARD_DECK_RULES:
                if key.startswith(BACK_PREFIX):
                    value = value.replace('[name]', card_name_back)
                else:
                    value = value.replace('[name]', card_name)

            if (lang == 'English' and
                    key in (CARD_FLAVOUR, BACK_PREFIX + CARD_FLAVOUR)):
                parts, _, is_valid_quote, separator = parse_flavour(value)
                if is_valid_quote:
                    if len(parts) == 2:
                        value = '{}{}—{}'.format(
                            parts[0],
                            separator,
                            re.sub(r'\s', '[nobr]', parts[1]))
                    elif len(parts) == 3:
                        value = '{}{}—{},[nobr]{}'.format(
                            parts[0],
                            separator,
                            re.sub(r'\s', '[nobr]', parts[1]),
                            re.sub(r'\s', '[nobr]', parts[2]))

            row[key] = value

        if row.get(CARD_TYPE) == 'Rules' and row.get(CARD_VICTORY) == 'auto':
            auto_page_rows.append(i)
        elif auto_page_rows:
            _fill_auto_pages(data, auto_page_rows)
            auto_page_rows = []

    if auto_page_rows:
        _fill_auto_pages(data, auto_page_rows)


def _fill_auto_pages(data, auto_page_rows):
    """ Automatically fill page numbers.
    """
    total = len(auto_page_rows)
    for page, i in enumerate(auto_page_rows):
        data[i][CARD_VICTORY] = '{}/{}'.format(page + 1, total)


def _clean_sets(data):
    """ Clean sets data from the spreadsheet.
    """
    for row in data:
        for key, value in row.items():
            if isinstance(value, str):
                row[key] = _clean_value(value)


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

        if row[CARD_TYPE] == 'Side Quest':
            row[CARD_TYPE] = 'Encounter Side Quest'

        if row[BACK_PREFIX + CARD_TYPE] == 'Side Quest':
            row[BACK_PREFIX + CARD_TYPE] = 'Encounter Side Quest'

        if (row[CARD_TYPE] in CARD_TYPES_DOUBLESIDE_MANDATORY and
                row[BACK_PREFIX + CARD_TYPE] is None):
            row[BACK_PREFIX + CARD_TYPE] = row[CARD_TYPE]

        if (row[CARD_TYPE] in CARD_TYPES_DOUBLESIDE_MANDATORY and
                row[CARD_SIDE_B] is None):
            row[CARD_SIDE_B] = row[CARD_NAME]

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

    with open(path, 'r', encoding='utf-8') as fobj:
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
        set_names = set()
        for row in data:
            if row[SET_ID] is None:
                logging.error('No set ID for row #%s, skipping',
                              row[ROW_COLUMN])
                continue

            if row[SET_ID] in SETS:
                logging.error('Duplicate set ID for row #%s, skipping',
                              row[ROW_COLUMN])
                continue

            if row[SET_NAME] is None:
                logging.error('No set name for row #%s, skipping',
                              row[ROW_COLUMN])
                continue

            if row[SET_NAME] in set_names:
                logging.error('Duplicate set name for row #%s, skipping',
                              row[ROW_COLUMN])
                continue

            if (row[SET_RINGSDB_CODE] is not None and
                    not is_positive_or_zero_int(row[SET_RINGSDB_CODE])):
                logging.error('Incorrect set ringsdb code for row #%s',
                              row[ROW_COLUMN])

            SETS[row[SET_ID]] = row
            set_names.add(row[SET_NAME])

    if sheet_changes or scratch_changes:
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
    _extract_all_card_names(DATA)
    _clean_data(DATA, 'English')

    SELECTED_CARDS.update({row[CARD_ID] for row in DATA if row[CARD_SELECTED]})
    FOUND_SETS.update({row[CARD_SET] for row in DATA
                       if row[CARD_SET] and not row[CARD_SCRATCH] and
                       row[CARD_SET] in SETS})
    scratch_sets = {row[CARD_SET] for row in DATA
                    if row[CARD_SET] and row[CARD_SCRATCH] and
                    row[CARD_SET] in SETS}
    FOUND_INTERSECTED_SETS.update(FOUND_SETS.intersection(scratch_sets))
    FOUND_SCRATCH_SETS.update(scratch_sets.difference(FOUND_INTERSECTED_SETS))
    _update_data(DATA)

    _extract_all_set_and_quest_names(DATA)
    _extract_all_encounter_set_names(DATA)
    _extract_all_traits(DATA)
    _extract_all_names()
    _extract_all_accents()

    card_types = {row[CARD_ID]: (row[CARD_TYPE], row[BACK_PREFIX + CARD_TYPE])
                  for row in DATA}
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
                if row[CARD_ID] in card_types:
                    row[CARD_TYPE] = card_types[row[CARD_ID]][0]
                    row[BACK_PREFIX + CARD_TYPE] = card_types[row[CARD_ID]][1]

            _clean_data(data, lang)
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
        chosen_sets.update(s for s in FOUND_SETS if not SETS[s][SET_IGNORE])

    if 'all_scratch' in conf['set_ids'] and scratch_changes:
        chosen_sets.update(s for s in FOUND_SCRATCH_SETS
                           if not SETS[s][SET_IGNORE])

    unknown_sets = (set(conf['set_ids']) - set(SETS.keys()) -
                    set(['all', 'all_scratch']))
    for unknown_set in unknown_sets:
        logging.error('Unknown set_id in configuration: %s', unknown_set)

    chosen_sets = list(chosen_sets)
    chosen_sets = [s for s in chosen_sets if s not in conf['ignore_set_ids']]
    chosen_sets = [[SETS[s][SET_ID], SETS[s][SET_NAME]] for s in chosen_sets]
    logging.info('...Getting all sets to work on (%ss)',
                 round(time.time() - timestamp, 3))
    return chosen_sets


def extract_flags(value):
    """ Extract flags from a string value.
    """
    return [f.strip() for f in
            str(value or '').replace(';', '\n').split('\n') if f.strip()]


def _verify_period(value):
    """ Verify period at the end of the paragraph.
    """
    res = True
    paragraphs = value.split('\n\n')
    for paragraph in paragraphs:
        paragraph = paragraph.replace('[/size]', '')
        if not (re.search(
                    r'\.\)?”?(?:\[\/b\]|\[\/i\]|\[\/bi\])?$', paragraph) or
                re.search(
                    r'\.”\)(?:\[\/b\]|\[\/i\]|\[\/bi\])?$', paragraph) or
                paragraph.endswith('[vspace]')):
            res = False
            break

    return res


def is_capitalized(word):
    """ Check whether the word is capitalized or not.
    """
    res = word and (word[0] != word[0].lower() or
                    re.match(r'[0-9_]', word[0]))
    return res


def _get_capitalization_errors(text):  # pylint: disable=R0912
    """ Detect capitalization errors.
    """
    errors = []
    if text in ('[space]', '[nobr]'):
        return errors

    text = re.sub(r'\[[^\]]+\]', '', text)
    text = text.replace(' son of ', ' sonof_ ')
    parts = text.split(' ')
    parts = [re.sub(r'^[…“]', '',
                    re.sub(r'[,.?!”…]$', '', p)) for p in parts
             if p not in ('-', '+')]
    if '' in parts:
        errors.append('"an empty word"')

    parts = [p for p in parts if p]
    if len(parts) > 0:
        if not is_capitalized(parts[0]):
            errors.append('"first word ({}) should be capitalized"'
                          .format(parts[0]))

    if len(parts) > 1:
        if not is_capitalized(parts[-1]):
            errors.append('"last word ({}) should be capitalized"'
                          .format(parts[-1]))

    if len(parts) > 2:
        for part in parts[1:-1]:
            capitalized = is_capitalized(part)
            if capitalized and part.lower() in LOWERCASE_WORDS:
                errors.append('"{} should not be capitalized"'.format(part))
            elif not capitalized and part.lower() not in LOWERCASE_WORDS:
                errors.append('"{} should be capitalized"'.format(part))

    for part in parts:
        for character in re.findall(r'(?<=’).', part):
            if character != character.lower():
                errors.append('"use lowercase after \' in {}"'.format(part))
                break

        for character in re.findall(
                r'(?<=-).',
                re.sub(r'-[a-zàáâãäąæçćĉèéêëęìíîïłñńòóôõöœśßùúûüźż]+-', '',
                       part)):
            if character != character.lower():
                errors.append('"use lowercase after - in {}"'.format(part))
                break

    return errors


def _get_rules_errors(text, field, card):  # pylint: disable=R0912,R0915
    """ Detect text rules errors.
    """
    errors = []
    text = re.sub(r'(^|\n)(?:\[[^\]]+\])*\[i\](?!\[b\]Rumor\[\/b\]|Example:)'
                  r'.+?\[\/i\](?:\[[^\]]+\])*(?:\n|$)', '\\1',
                  text, flags=re.DOTALL)

    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
    if not paragraphs:
        return errors

    for paragraph in paragraphs:
        paragraph = paragraph.replace('\n', ' ')
        if re.search(r'limit once per',
                     re.sub(r'\(Limit once per .+\.\)”?$', '', paragraph),
                     flags=re.IGNORECASE):
            errors.append('"(Limit once per _.)"')

        if re.search(r'limit (?:twice|two times|2 times) per',
                     re.sub(r'\(Limit twice per .+\.\)”?$', '', paragraph),
                     flags=re.IGNORECASE):
            errors.append('"(Limit twice per _.)"')

        if re.search(r'limit (?:thrice|three times|3 times) per',
                     re.sub(r'\(Limit 3 times per .+\.\)”?$', '', paragraph),
                     flags=re.IGNORECASE):
            errors.append('"(Limit 3 times per _.)"')

        if ' to travel here' in paragraph:
            errors.append('redundant: "to travel here"')

        if re.search(r' he (?:or she|commit|controls|deals|(?:just )?discard|'
                     'is eliminated|must|owns|puts|raises)', paragraph):
            errors.append('"they"')

        if re.search(r' his (?:or her|(?:eligible )?characters|choice|control|'
                     'deck|discard pile|hand|hero|out-of-play deck|own|'
                     'play area|threat)', paragraph):
            errors.append('"their"')

        if (' him or her' in paragraph or
                'engaged with him' in paragraph or
                'in front of him' in paragraph):
            errors.append('"them"')

        if re.search(r'encounter deck[^.]+from the top of the encounter deck',
                     paragraph):
            errors.append('redundant: "from the top of the encounter deck"')

        if re.search(r'encounter deck[^.]+from the encounter deck', paragraph):
            errors.append('redundant: "from the encounter deck"')

        if re.search(r'discards? (?:[^ ]+ )?cards? from the top of the '
                     'encounter deck', paragraph, flags=re.IGNORECASE):
            errors.append('"from the encounter deck"')

        if re.search(r' gets? [^+–]', paragraph):
            errors.append('"gain(s)" a non-stat modification')

        if re.search(r' gains? [+–]', paragraph):
            errors.append('"get(s)" a stat modification')

        if re.search(r'discards? . cards? at random', paragraph,
                     flags=re.IGNORECASE):
            errors.append('"discard(s) _ random card(s)"')

        if re.search(r'\(Counts as a (?:\[bi\])?Condition', paragraph):
            errors.append('"While attached... counts as a {Condition} '
                          'attachment with the text:"')

        if ' by this effect' in paragraph:
            errors.append('"this way" instead of "by this effect"')

        if re.search(r'may trigger this (?:action|response)',
                     paragraph, flags=re.IGNORECASE):
            errors.append('"may trigger this effect"')
        elif re.search(r'\(any player may trigger this effect',
                     paragraph, flags=re.IGNORECASE):
            errors.append('"Any player may trigger this effect"')

        if ('cannot be chosen as the current quest'
                in paragraph.replace('cannot be chosen as the current quest '
                                     'during the quest phase', '')):
            errors.append('"cannot be chosen as the current quest during '
                          'the quest phase"')

        if 'active quest' in paragraph or 'current quest stage' in paragraph:
            errors.append('"current quest"')

        if re.search(r'adds? [0-9X](?:\[pp\])? resources? to ',
                     re.sub(r'adds? [0-9X](?:\[pp\])? resources? to [^.]+ '
                            r'pool', '', paragraph, flags=re.IGNORECASE),
                     flags=re.IGNORECASE):
            errors.append('"place(s) _ resource token(s) on"')

        if re.search(r'adds? [0-9X](?:\[pp\])? resource tokens? to [^.]+ pool',
                     paragraph, flags=re.IGNORECASE):
            errors.append('"add(s) _ resource(s) to _ resource pool"')
        elif re.search(r'adds? [0-9X](?:\[pp\])? resource tokens? to ',
                       paragraph, flags=re.IGNORECASE):
            errors.append('"place(s) _ resource token(s) on"')

        if re.search(r'places? [0-9X](?:\[pp\])? resources? on [^.]+ pool',
                     paragraph, flags=re.IGNORECASE):
            errors.append('"add(s) _ resource(s) to _ resource pool"')
        elif re.search(r'places? [0-9X](?:\[pp\])? resources? on ',
                       paragraph, flags=re.IGNORECASE):
            errors.append('"place(s) _ resource token(s) on"')

        if re.search(
                r'places? [0-9X](?:\[pp\])? resource tokens? on [^.]+ pool',
                paragraph, flags=re.IGNORECASE):
            errors.append('"add(s) _ resource(s) to _ resource pool"')

        if 'per player' in re.sub(r'limit [^.]+\.', '', paragraph,
                                  flags=re.IGNORECASE):
            errors.append('"[pp]"')

        if re.search(r'step is completed?',
                     paragraph.replace('complete rules', '')):
            errors.append('redundant: "is complete(d)"')
        elif re.search(r'\bcomplete[ds]?\b',
                       paragraph.replace('complete rules', ''),
                       flags=re.IGNORECASE):
            errors.append('"defeat(ed)"')
        elif re.search(r'explore (?:this |a quest )?stage', paragraph,
                       flags=re.IGNORECASE):
            errors.append('"defeat(ed)"')
        elif re.search(r'(?:stage|quest) (?:is|is not|cannot be) explored',
                       paragraph):
            errors.append('"defeat(ed)"')
        elif re.search(r'\b(?:clear|cleared)\b', paragraph,
                       flags=re.IGNORECASE):
            errors.append('"defeat(ed)"')

        if re.search(r'play only after',
                     paragraph, flags=re.IGNORECASE):
            errors.append('"Response: At the end of _" instead of '
                          '"play only after"')

        if 'cancelled' in paragraph:
            errors.append('"canceled"')

        if re.search(
                r' (?:leadership|lore|spirit|tactics|baggins|fellowship)\b',
                paragraph):
            errors.append('"[sphere name] as tag"')

        if (re.search(
                r'more than [0-9]+(?!\[pp\])',
                re.sub(r'no more', '', paragraph, flags=re.IGNORECASE),
                flags=re.IGNORECASE) and
                not re.search(r'cannot[^.]+more than [0-9]+(?!\[pp\])',
                              re.sub(r'cannot[^.]+unless', '', paragraph,
                                     flags=re.IGNORECASE),
                              flags=re.IGNORECASE)):
            errors.append('"_ or more (greater)"')
        elif (re.search(
                r'greater than [0-9]+(?!\[pp\])', paragraph,
                flags=re.IGNORECASE) and
                not re.search(r'cannot[^.]+greater than [0-9]+(?!\[pp\])',
                              re.sub(r'cannot[^.]+unless', '', paragraph,
                                     flags=re.IGNORECASE),
                              flags=re.IGNORECASE)):
            errors.append('"_ or more (greater)"')

        if (re.search(r'fewer than [0-9]+(?!\[pp\])', paragraph,
                      flags=re.IGNORECASE) and
                not re.search(r'cannot[^.]+fewer than [0-9]+(?!\[pp\])',
                              re.sub(r'cannot[^.]+unless', '', paragraph,
                                     flags=re.IGNORECASE),
                              flags=re.IGNORECASE)):
            errors.append('"_ or fewer (less)"')
        elif (re.search(r'less than [0-9]+(?!\[pp\])', paragraph,
                        flags=re.IGNORECASE) and
                not re.search(r'cannot[^.]+less than [0-9]+(?!\[pp\])',
                              re.sub(r'cannot[^.]+unless', '', paragraph,
                                     flags=re.IGNORECASE),
                              flags=re.IGNORECASE)):
            errors.append('"_ or fewer (less)"')

        if (re.search(r'cannot[^.]+ [0-9]+ or (?:more|greater)',
                      re.sub(r'cannot[^.]+unless', '', paragraph,
                             flags=re.IGNORECASE), flags=re.IGNORECASE)):
            errors.append('"more (greater) than _"')

        if (re.search(r'cannot[^.]+ [0-9]+ or (?:less|fewer)',
                      re.sub(r'cannot[^.]+unless', '', paragraph,
                             flags=re.IGNORECASE), flags=re.IGNORECASE)):
            errors.append('"fewer (less) than _"')

        if re.search(r' defense\b', paragraph):
            errors.append('"[defense] as tag"')

        if re.search(r' willpower\b', paragraph):
            errors.append('"[willpower] as tag"')

        if re.search(r' (?:[+–][0-9X]+|printed) attack\b', paragraph):
            errors.append('"[attack] as tag"')

        if re.search(
                r' (?:[+–][0-9X]+|printed) threat\b',
                paragraph.replace('threat cost', '').replace('threat penalty',
                                                             '')):
            errors.append('"[threat] as tag"')

        if re.search(r'[Cc]hoose[^:]*?: Either', paragraph):
            errors.append('"choose: either"')

        if re.search(r'\bheal[^.]+?\bon\b',
                     re.sub(r'\bfrom\b[^.]+?\bon\b', '', paragraph,
                            flags=re.IGNORECASE),
                     flags=re.IGNORECASE):
            errors.append('"heal _ from"')

        if 'quest card' in paragraph:
            errors.append('redundant: "card(s)" after "quest"')

        if 'set-aside' in paragraph:
            errors.append('"set aside"')

        if re.search(r'is a \[bi\][^\[]+\[\/bi\](?! trait| \[bi\]trait)',
                     paragraph, flags=re.IGNORECASE):
            errors.append('"has the {Trait} trait"')
        elif re.search(r'(?<!the )(?:printed )?\[bi\][^\[]+\[\/bi\]'
                     r'(?:(?:, | or | and )\[bi\][^\[]+\[\/bi\])* traits?\b',
                     re.sub(r'the (?:printed )?\[bi\][^\[]+\[\/bi\]'
                            r'(?:(?:, | or | and )\[bi\][^\[]+\[\/bi\])* '
                            r'traits?\b', '', paragraph), flags=re.IGNORECASE):
            errors.append('"the {Trait} trait"')

        if re.search(r'\[\/bi\] Traits?\b', paragraph):
            errors.append('lowercase "trait(s)" after "{Trait}"')
        elif re.search(r'\[\/bi\] \[bi\]traits?\b', paragraph,
                       flags=re.IGNORECASE):
            errors.append('remove tags around "trait(s)" after "{Trait}"')

        if re.search(r'(?<!\[\/bi\] )traits?\b', paragraph):
            errors.append('uppercase "Trait(s)"')
        elif re.search(r'(?<!\[\/bi\] )(?<!\[bi\])Traits?\b', paragraph,
                       flags=re.IGNORECASE):
            errors.append('add {} around "Trait(s)"')

        if (field in (CARD_SHADOW, BACK_PREFIX + CARD_SHADOW) and
                re.search(r'\bdefending player\b', paragraph,
                          flags=re.IGNORECASE)):
            errors.append('"you" (instead of "defending player")')
        elif re.search(r'\bshadow\b[^.]+ defending player\b', paragraph,
                       flags=re.IGNORECASE):
            errors.append('"you" (instead of "defending player")')
        elif re.search(
                r'\b(?:after|when) [^.]+ attacks[^.]+ defending player\b',
                paragraph, flags=re.IGNORECASE):
            errors.append('"you" (instead of "defending player")')

        if (field in (CARD_SHADOW, BACK_PREFIX + CARD_SHADOW) and
                re.search(r'\bafter this attack[^.]* attacking enemy engages '
                          r'the next player[^.]* makes an immediate attack\b',
                          paragraph, flags=re.IGNORECASE) and
                not re.search(r'\bafter this attack, attacking enemy engages '
                              r'the next player, then makes an immediate '
                              r'attack\b', paragraph, flags=re.IGNORECASE)):
            errors.append('"After this attack, attacking enemy engages the '
                          'next player, then makes an immediate attack"')
        if (re.search(r'\bshadow\b[^.]+ after this attack[^.]* attacking '
                      r'enemy engages the next player[^.]* makes an immediate '
                      r'attack\b', paragraph, flags=re.IGNORECASE) and
                not re.search(r'\bafter this attack, attacking enemy engages '
                              r'the next player, then makes an immediate '
                              r'attack\b', paragraph, flags=re.IGNORECASE)):
            errors.append('"After this attack, attacking enemy engages the '
                          'next player, then makes an immediate attack"')

        if re.search(r'advance to stage [0-9]+\b', paragraph,
                     flags=re.IGNORECASE):
            errors.append('"advance to stage _A(B)")')

        if re.search(r'(?<!\bstage )[2-90X] card\b', paragraph,
                     flags=re.IGNORECASE):
            errors.append('"cards" not "card"')

        if re.search(r'^\[b\]Rumor\[\/b\]:', paragraph):
            errors.append('Rumor text must be inside [i] tags')

        if (re.search(r'(?:\[bi\]forced\[\/bi\]|forced|"forced") effect',
                      paragraph, flags=re.IGNORECASE) or
                '[b]forced[/b] effect' in paragraph):
            errors.append('"[b]Forced[/b]"')

        if (re.search(r'(?:\[bi\]travel\[\/bi\]|travel|"travel") effect',
                      paragraph, flags=re.IGNORECASE) or
                '[b]travel[/b] effect' in paragraph):
            errors.append('"[b]Travel[/b]"')

        if (re.search(r'(?:\[bi\]rumor\[\/bi\]|rumor|"rumor") effect',
                      paragraph, flags=re.IGNORECASE) or
                '[b]rumor[/b] effect' in paragraph):
            errors.append('"[b]Rumor[/b]"')

        if (re.search(r'(?:\[bi\]shadow\[\/bi\]|\[b\]shadow\[\/b\]|"shadow") '
                      r'effect', paragraph, flags=re.IGNORECASE) or
                re.search(r'(?<!\.) Shadow effect\b', paragraph)):
            errors.append('"shadow"')

        if (re.search(r'(?:\[bi\]when revealed\[\/bi\]|'
                      r'\[b\]when revealed\[\/b\]|when revealed) effect',
                      paragraph, flags=re.IGNORECASE) or
                '"When Revealed" effect' in paragraph or
                '"When revealed" effect' in paragraph):
            errors.append('"when revealed" in double-quotes')

        if 'When revealed:' in paragraph:
            errors.append('"When Revealed:"')

        updated_paragraph = re.sub(
            r'\b(?:Valour )?(?:Resource |Planning |Quest |Travel |Encounter '
            r'|Combat |Refresh )?(?:Action):', '', paragraph)
        updated_paragraph = re.sub(r'\b(?:Valour Response|Response):', '',
                                   updated_paragraph)

        if (re.search(r'(?:\[bi\]action\[\/bi\]|\[b\]action\[\/b\]|"action")',
                      updated_paragraph, flags=re.IGNORECASE) or
                re.search(r'(?<!\.) Action\b', updated_paragraph)):
            errors.append('"action"')

        if (re.search(r'(?:\[bi\]response\[\/bi\]|\[b\]response\[\/b\]|'
                      r'"response")', updated_paragraph,
                      flags=re.IGNORECASE) or
                re.search(r'(?<!\.) Response\b', updated_paragraph)):
            errors.append('"response"')

        if field == CARD_TEXT and card[CARD_TYPE] == 'Quest':
            name_regex = (r'(?<!\[bi\])\b' + re.escape(card[CARD_NAME]) +
                          r'\b(?!\[\/bi\])')
            if (re.search(name_regex, paragraph) or
                    re.search(r'\bthis quest\b', paragraph,
                              flags=re.IGNORECASE)):
                errors.append('"this stage"')

        if (field == BACK_PREFIX + CARD_TEXT and
                card[BACK_PREFIX + CARD_TYPE] == 'Quest'):
            name_regex = (r'(?<!\[bi\])\b' +
                          re.escape(card[BACK_PREFIX + CARD_NAME]) +
                          r'\b(?!\[\/bi\])')
            if (re.search(name_regex, paragraph) or
                    re.search(r'\bthis quest\b', paragraph,
                              flags=re.IGNORECASE)):
                errors.append('"this stage"')

        if (field == CARD_TEXT and card[CARD_TYPE] in
                ('Encounter Side Quest', 'Player Side Quest')):
            name_regex = (r'(?<!\[bi\])\b' + re.escape(card[CARD_NAME]) +
                          r'\b(?!\[\/bi\]| (?:is )?in the victory display)')
            if (re.search(name_regex, paragraph) or
                    re.search(r'\bthis stage\b', paragraph,
                              flags=re.IGNORECASE)):
                errors.append('"this quest"')

        if (field == BACK_PREFIX + CARD_TEXT and
                card[BACK_PREFIX + CARD_TYPE] in
                ('Encounter Side Quest', 'Player Side Quest')):
            name_regex = (r'(?<!\[bi\])\b' +
                          re.escape(card[BACK_PREFIX + CARD_NAME]) +
                          r'\b(?!\[\/bi\]| (?:is )?in the victory display)')
            if (re.search(name_regex, paragraph) or
                    re.search(r'\bthis stage\b', paragraph,
                              flags=re.IGNORECASE)):
                errors.append('"this quest"')

    if (field == CARD_TEXT and card[CARD_TYPE] == 'Quest'
            and str(card[CARD_COST]) == '1'):
        if 'When Revealed' in text:
            errors.append('"Setup" instead of "When Revealed"')

    if ((field == CARD_TEXT and
         card[CARD_TYPE] not in CARD_TYPES_NO_KEYWORDS) or
            (field == BACK_PREFIX + CARD_TEXT and
             card[BACK_PREFIX + CARD_TYPE] not in CARD_TYPES_NO_KEYWORDS)):
        if re.match(KEYWORDS_REGEX,
                    paragraphs[0].replace('Immune to player card effects.', '')
                    .replace('Cannot have attachments.', '').replace('  ', '')
                    .strip()):
            errors.append('first line of the text looks like keyword(s)')

    return errors


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

    accents_regex = (r'\b(?:' + '|'.join([re.escape(a) for a in ACCENTS]) +
                     r')\b')

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
        card_cost = row[CARD_COST]
        card_engagement = row[CARD_ENGAGEMENT]
        card_threat = row[CARD_THREAT]
        card_willpower = row[CARD_WILLPOWER]
        card_attack = row[CARD_ATTACK]
        card_defense = row[CARD_DEFENSE]
        card_health = row[CARD_HEALTH]
        card_quest = row[CARD_QUEST]
        card_victory = row[CARD_VICTORY]
        card_text = row[CARD_TEXT]
        card_shadow = row[CARD_SHADOW]
        card_flavour = row[CARD_FLAVOUR]
        card_printed_number = row[CARD_PRINTED_NUMBER]
        card_encounter_set_number = row[CARD_ENCOUNTER_SET_NUMBER]
        card_encounter_set_icon = row[CARD_ENCOUNTER_SET_ICON]
        card_flags = row[CARD_FLAGS]
        card_artist = row[CARD_ARTIST]
        card_panx = row[CARD_PANX]
        card_pany = row[CARD_PANY]
        card_scale = row[CARD_SCALE]
        card_portrait_shadow = row[CARD_PORTRAIT_SHADOW]
        card_special_icon = row[CARD_SPECIAL_ICON]

        card_name_back = row[BACK_PREFIX + CARD_NAME]
        card_unique_back = row[BACK_PREFIX + CARD_UNIQUE]
        card_type_back = row[BACK_PREFIX + CARD_TYPE]
        card_sphere_back = row[BACK_PREFIX + CARD_SPHERE]
        card_traits_back = row[BACK_PREFIX + CARD_TRAITS]
        card_keywords_back = row[BACK_PREFIX + CARD_KEYWORDS]
        card_cost_back = row[BACK_PREFIX + CARD_COST]
        card_engagement_back = row[BACK_PREFIX + CARD_ENGAGEMENT]
        card_threat_back = row[BACK_PREFIX + CARD_THREAT]
        card_willpower_back = row[BACK_PREFIX + CARD_WILLPOWER]
        card_attack_back = row[BACK_PREFIX + CARD_ATTACK]
        card_defense_back = row[BACK_PREFIX + CARD_DEFENSE]
        card_health_back = row[BACK_PREFIX + CARD_HEALTH]
        card_quest_back = row[BACK_PREFIX + CARD_QUEST]
        card_victory_back = row[BACK_PREFIX + CARD_VICTORY]
        card_text_back = row[BACK_PREFIX + CARD_TEXT]
        card_shadow_back = row[BACK_PREFIX + CARD_SHADOW]
        card_flavour_back = row[BACK_PREFIX + CARD_FLAVOUR]
        card_printed_number_back = row[BACK_PREFIX + CARD_PRINTED_NUMBER]
        card_encounter_set_number_back = row[
            BACK_PREFIX + CARD_ENCOUNTER_SET_NUMBER]
        card_encounter_set_icon_back = row[
            BACK_PREFIX + CARD_ENCOUNTER_SET_ICON]
        card_flags_back = row[BACK_PREFIX + CARD_FLAGS]
        card_artist_back = row[BACK_PREFIX + CARD_ARTIST]
        card_panx_back = row[BACK_PREFIX + CARD_PANX]
        card_pany_back = row[BACK_PREFIX + CARD_PANY]
        card_scale_back = row[BACK_PREFIX + CARD_SCALE]
        card_portrait_shadow_back = row[BACK_PREFIX + CARD_PORTRAIT_SHADOW]
        card_special_icon_back = row[BACK_PREFIX + CARD_SPECIAL_ICON]

        card_easy_mode = row[CARD_EASY_MODE]
        card_additional_encounter_sets = row[CARD_ADDITIONAL_ENCOUNTER_SETS]
        card_adventure = row[CARD_ADVENTURE]
        card_icon = row[CARD_ICON]
        card_copyright = row[CARD_COPYRIGHT]
        card_back = row[CARD_BACK]
        card_deck_rules = row[CARD_DECK_RULES]
        card_scratch = row[CARD_SCRATCH]
        row_info = '{}{}{}'.format(
            ', {}'.format(card_name) if card_name else '',
            ' ({})'.format(row[CARD_SET_NAME]) if row[CARD_SET_NAME] else '',
            ' (Scratch)' if card_scratch else '')

        if set_id is None:
            message = 'No set ID for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
        elif set_id == '[filtered set]':
            message = 'Reusing non-scratch set ID for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
        elif set_id not in all_set_ids:
            message = 'Unknown set ID for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)

        if card_id is None:
            message = 'No card ID for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_id in card_ids or card_id in card_scratch_ids:
            message = 'Duplicate card ID for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif not re.match(UUID_REGEX, card_id):
            message = 'Incorrect card ID format for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_scratch:
            card_scratch_ids.add(card_id)
        else:
            card_ids.add(card_id)

        if not conf['run_sanity_check_for_all_sets'] and set_id not in set_ids:
            continue

        if (i, card_scratch) in PRE_SANITY_CHECK:
            for error in PRE_SANITY_CHECK[(i, card_scratch)]:
                message = ('{} for row #{}{} (use IgnoreName flag to ignore)'
                           .format(error, i, row_info))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)

        if card_number is None:
            message = 'No card number for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif len(_handle_int_str(card_number)) > 3:
            message = 'Card number is too long for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if set_id is not None and card_number is not None:
            if (set_id, card_number) in card_set_numbers:
                message = ('Duplicate card set and card number combination '
                           'for row #{}{}'.format(i, row_info))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            else:
                card_set_numbers.add((set_id, card_number))

        if card_quantity is None:
            message = 'No card quantity for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif not is_positive_int(card_quantity):
            message = ('Incorrect format for card quantity for row '
                       '#{}{}'.format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type in CARD_TYPES_ONE_COPY and card_quantity != 1 and
              not (card_flags and
                   'AdditionalCopies' in extract_flags(card_flags))):
            message = ('Incorrect card quantity for row #{}{}'.format(
                i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type in CARD_TYPES_THREE_COPIES and
              card_sphere != 'Boon' and card_quantity not in (1, 3) and
              not (card_flags and
                   'AdditionalCopies' in extract_flags(card_flags))):
            message = ('Incorrect card quantity for row #{}{}'.format(
                i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_encounter_set is None and
                ((card_type in CARD_TYPES_ENCOUNTER_SET and
                  card_sphere != 'Boon') or
                 (card_type_back in CARD_TYPES_ENCOUNTER_SET and
                  card_sphere_back != 'Boon'))):
            message = 'No encounter set for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_encounter_set is not None and  # pylint: disable=R0916
              (card_type in CARD_TYPES_NO_ENCOUNTER_SET
               or card_sphere == 'Boon') and
              (card_type_back in CARD_TYPES_NO_ENCOUNTER_SET or
               card_type_back is None or card_sphere_back == 'Boon')):
            message = 'Redundant encounter set for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_encounter_set is not None and
              not (card_flags and 'IgnoreName' in extract_flags(card_flags))):
            capitalization_errors = _get_capitalization_errors(
                card_encounter_set)
            if capitalization_errors:
                message = (
                    'Capitalization error(s) in encounter set for row #{}{}: '
                    '{} (use IgnoreName flag to ignore)'.format(
                        i, row_info, ', '.join(capitalization_errors)))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

        if card_name is None:
            message = 'No card name for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_name is not None and
              not (card_flags and 'IgnoreName' in extract_flags(card_flags))):
            capitalization_errors = _get_capitalization_errors(card_name)
            if capitalization_errors:
                message = (
                    'Capitalization error(s) in card name for row #{}{}: {} '
                    '(use IgnoreName flag to ignore)'.format(
                        i, row_info, ', '.join(capitalization_errors)))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

        if card_name_back is not None and card_type_back is None:
            message = 'Redundant card name back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_name_back is None and card_type_back is not None:
            message = 'No card name back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_name_back is not None and
              not (card_flags_back and
                   'IgnoreName' in extract_flags(card_flags_back))):
            capitalization_errors = _get_capitalization_errors(card_name_back)
            if capitalization_errors:
                message = (
                    'Capitalization error(s) in card name back for row #{}{}: '
                    '{} (use IgnoreName flag to ignore)'.format(
                        i, row_info, ', '.join(capitalization_errors)))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

        if card_unique is not None and card_unique not in ('1', 1):
            message = 'Incorrect format for unique for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif ((card_unique is None and card_type in CARD_TYPES_UNIQUE) or
              (card_unique in ('1', 1) and
               card_type in CARD_TYPES_NO_UNIQUE)):
            message = 'Incorrect unique value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_unique_back is not None and card_type_back is None:
            message = 'Redundant unique back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_unique_back is not None and card_unique_back not in ('1', 1):
            message = 'Incorrect format for unique back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif ((card_unique_back is None and
               card_type_back in CARD_TYPES_UNIQUE) or
              (card_unique_back in ('1', 1) and
               card_type_back in CARD_TYPES_NO_UNIQUE)):
            message = 'Incorrect unique back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_type is None:
            message = 'No card type for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_type not in CARD_TYPES:
            message = 'Unknown card type for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_type_back is not None and card_type_back not in CARD_TYPES:
            message = 'Unknown card type back for row #{}{}'.format(i,
                                                                    row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type in CARD_TYPES_DOUBLESIDE_OPTIONAL
              and card_type_back is not None and card_type_back != card_type):
            message = 'Incorrect card type back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type not in CARD_TYPES_DOUBLESIDE_OPTIONAL
              and card_type_back in CARD_TYPES_DOUBLESIDE_OPTIONAL):
            message = 'Incorrect card type back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_type == 'Campaign':
            spheres = SPHERES_CAMPAIGN.copy()
        elif card_type == 'Encounter Side Quest':
            spheres = SPHERES_SIDE_QUEST.copy()
        elif card_type == 'Rules':
            spheres = SPHERES_RULES.copy()
        elif card_type == 'Presentation':
            spheres = SPHERES_PRESENTATION.copy()
        elif card_type == 'Ship Objective':
            spheres = SPHERES_SHIP_OBJECTIVE.copy()
        elif card_type in CARD_TYPES_PLAYER_SPHERE:
            spheres = SPHERES_PLAYER.copy()
        else:
            spheres = SPHERES.copy()

        if card_type in CARD_TYPES_BOON:
            spheres.add('Boon')

        if card_type in CARD_TYPES_BURDEN:
            spheres.add('Burden')

        if card_type in CARD_TYPES_NIGHTMARE:
            spheres.add('Nightmare')

        if card_type in CARD_TYPES_NOSTAT:
            spheres.add('NoStat')

        if (card_sphere is None and
                (card_type in CARD_TYPES_PLAYER_SPHERE or
                 card_type == 'Presentation')):
            message = 'No sphere for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_sphere is not None and card_sphere not in spheres:
            message = 'Unknown sphere for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_type not in CARD_TYPES_DOUBLESIDE_OPTIONAL:
            if card_type_back == 'Ship Objective':
                spheres_back = SPHERES_SHIP_OBJECTIVE.copy()
            elif card_type_back in CARD_TYPES_PLAYER_SPHERE:
                spheres_back = SPHERES_PLAYER.copy()
            else:
                spheres_back = SPHERES.copy()

            if card_type_back in CARD_TYPES_BOON:
                spheres_back.add('Boon')

            if card_type_back in CARD_TYPES_BURDEN:
                spheres_back.add('Burden')

            if card_type_back in CARD_TYPES_NIGHTMARE:
                spheres_back.add('Nightmare')

            if card_type_back in CARD_TYPES_NOSTAT:
                spheres_back.add('NoStat')

            if card_sphere_back is not None and card_type_back is None:
                message = 'Redundant sphere back for row #{}{}'.format(
                    i, row_info)
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            elif (card_sphere_back is None and
                  card_type_back in CARD_TYPES_PLAYER_SPHERE):
                message = 'No sphere back for row #{}{}'.format(i, row_info)
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            elif (card_sphere_back is not None and
                  card_sphere_back not in spheres_back):
                message = 'Unknown sphere back for row #{}{}'.format(
                    i, row_info)
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

        if (card_traits is None and
                card_type in CARD_TYPES_TRAITS and
                not (card_flags and 'NoTraits' in extract_flags(card_flags))):
            message = 'No traits for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_traits is not None and card_type in CARD_TYPES_NO_TRAITS:
            message = 'Redundant traits for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_traits is None and
              card_sphere in CARD_SPHERES_TRAITS and
              not (card_flags and 'NoTraits' in extract_flags(card_flags))):
            message = 'No traits for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_traits is not None and
              not str(card_traits).endswith('.') and
              not str(card_traits).endswith('.[/size]')):
            message = 'Missing period in traits for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_traits is not None and
              re.sub(r'\[[^\]]+\]', '', card_traits.replace('.', '')
                     .replace(' ', '')) == ''):
            message = 'Incorrect traits for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_traits is not None and
              not (card_flags and 'IgnoreName' in extract_flags(card_flags))):
            capitalization_errors = _get_capitalization_errors(
                re.sub(r'\[[^\]]+\]', '', card_traits))
            if capitalization_errors:
                message = (
                    'Capitalization error(s) in traits for row #{}{}: {} '
                    '(use IgnoreName flag to ignore)'.format(
                        i, row_info, ', '.join(capitalization_errors)))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

        if card_traits_back is not None and card_type_back is None:
            message = 'Redundant traits back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_traits_back is None and
              card_type_back in CARD_TYPES_TRAITS and
              not (card_flags_back and
                   'NoTraits' in extract_flags(card_flags_back))):
            message = 'No traits back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_traits_back is not None and
              card_type_back in CARD_TYPES_NO_TRAITS):
            message = 'Redundant traits back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_traits_back is None and
              card_sphere_back in CARD_SPHERES_TRAITS and
              not (card_flags_back and
                   'NoTraits' in extract_flags(card_flags_back))):
            message = 'No traits back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_traits_back is not None and
              not str(card_traits_back).endswith('.') and
              not str(card_traits_back).endswith('.[/size]')):
            message = 'Missing period in traits back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_traits_back is not None and
              re.sub(r'\[[^\]]+\]', '', card_traits_back.replace('.', '')
                     .replace(' ', '')) == ''):
            message = 'Incorrect traits back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_traits_back is not None and
              not (card_flags_back and
                   'IgnoreName' in extract_flags(card_flags_back))):
            capitalization_errors = _get_capitalization_errors(
                re.sub(r'\[[^\]]+\]', '', card_traits_back))
            if capitalization_errors:
                message = (
                    'Capitalization error(s) in traits back for row #{}{}: {} '
                    '(use IgnoreName flag to ignore)'.format(
                        i, row_info, ', '.join(capitalization_errors)))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

        if card_keywords is not None and card_type in CARD_TYPES_NO_KEYWORDS:
            message = 'Redundant keywords for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_keywords is not None and
              not str(card_keywords).endswith('.') and
              not str(card_keywords).endswith('.[inline]')):
            message = 'Missing period in keywords for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_keywords is not None and
              card_keywords.replace('[inline]', '').replace('.', '')
              .replace(' ', '') == ''):
            message = 'Incorrect keywords for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_keywords is not None and not
              re.match(KEYWORDS_REGEX,
                       card_keywords.replace('[inline]', ''))):
            message = 'Incorrect keywords for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_keywords_back is not None and card_type_back is None:
            message = 'Redundant keywords back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_keywords_back is not None and
              card_type_back in CARD_TYPES_NO_KEYWORDS):
            message = 'Redundant keywords back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_keywords_back is not None and
              not str(card_keywords_back).endswith('.') and
              not str(card_keywords_back).endswith('.[inline]')):
            message = 'Missing period in keywords back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_keywords_back is not None and
              card_keywords_back.replace('[inline]', '').replace('.', '')
              .replace(' ', '') == ''):
            message = 'Incorrect keywords back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_keywords_back is not None and not
              re.match(KEYWORDS_REGEX,
                       card_keywords_back.replace('[inline]', ''))):
            message = 'Incorrect keywords back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_cost is None and card_type in CARD_TYPES_COST:
            message = 'No cost for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_cost is not None and card_type not in CARD_TYPES_COST:
            message = 'Redundant cost for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type == 'Hero' and
              not re.match('^[1-9]?[0-9]$', str(card_cost))):
            message = 'Incorrect cost value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_type == 'Quest' and not re.match('^[1-9]$', str(card_cost)):
            message = 'Incorrect cost value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type not in ('Hero', 'Quest') and card_cost is not None and
              not re.match('^[1-9]?[0-9]$', str(card_cost)) and
              card_cost != '-' and card_cost != 'X'):
            message = 'Incorrect cost value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type not in ('Hero', 'Quest') and card_cost is not None and
              ('Encounter' in extract_keywords(card_keywords) or
               card_back == 'Encounter') and
              card_cost != '-'):
            message = 'Incorrect cost value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_cost_back is not None and card_type_back is None:
            message = 'Redundant cost back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_cost_back is None and card_type_back in CARD_TYPES_COST:
            message = 'No cost back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_cost_back is not None and
              card_type_back not in CARD_TYPES_COST):
            message = 'Redundant cost back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type_back == 'Hero' and
              not re.match('^[1-9]?[0-9]$', str(card_cost_back))):
            message = 'Incorrect cost back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type_back == 'Quest' and
              not re.match('^[1-9]$', str(card_cost_back))):
            message = 'Incorrect cost back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type_back not in ('Hero', 'Quest') and
              card_cost_back is not None and
              not re.match('^[1-9]?[0-9]$', str(card_cost_back)) and
              card_cost_back != '-' and card_cost_back != 'X'):
            message = 'Incorrect cost back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type_back not in ('Hero', 'Quest') and
              card_cost_back is not None and
              'Encounter' in extract_keywords(card_keywords_back) and
              card_cost_back != '-'):
            message = 'Incorrect cost back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_engagement is None and card_type in CARD_TYPES_ENGAGEMENT:
            message = 'No engagement cost for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_engagement is not None and
              card_type not in CARD_TYPES_ENGAGEMENT):
            message = 'Redundant engagement cost for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type == 'Quest' and
              not re.match('^[ACEG]$', str(card_engagement))):
            message = 'Incorrect engagement cost value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type != 'Quest' and card_engagement is not None and
              not re.match('^[1-9]?[0-9]$', str(card_engagement)) and
              card_engagement != '-' and card_engagement != 'X'):
            message = 'Incorrect engagement cost value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_engagement_back is not None and card_type_back is None:
            message = 'Redundant engagement cost back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_engagement_back is None and
              card_type_back in CARD_TYPES_ENGAGEMENT):
            message = 'No engagement cost back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_engagement_back is not None and
              card_type_back not in CARD_TYPES_ENGAGEMENT):
            message = 'Redundant engagement cost back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type_back == 'Quest' and
              not re.match('^[BDFH]$', str(card_engagement_back))):
            message = ('Incorrect engagement cost back value for row #{}{}'
                       .format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type_back != 'Quest' and
              card_engagement_back is not None and
              not re.match('^[1-9]?[0-9]$', str(card_engagement_back)) and
              card_engagement_back != '-' and card_engagement_back != 'X'):
            message = (
                'Incorrect engagement cost back value for row #{}{}'.format(
                    i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_threat is None and card_type in CARD_TYPES_THREAT:
            message = 'No threat for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_threat is not None and card_type not in CARD_TYPES_THREAT:
            message = 'Redundant threat for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_threat is not None and
              not re.match('^[1-9]?[0-9]$', str(card_threat)) and
              card_threat != '-' and card_threat != 'X'):
            message = 'Incorrect threat value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_threat_back is not None and card_type_back is None:
            message = 'Redundant threat back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_threat_back is None and card_type_back in CARD_TYPES_THREAT:
            message = 'No threat back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_threat_back is not None and
              card_type_back not in CARD_TYPES_THREAT):
            message = 'Redundant threat back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_threat_back is not None and
              not re.match('^[1-9]?[0-9]$', str(card_threat_back)) and
              card_threat_back != '-' and card_threat_back != 'X'):
            message = 'Incorrect threat back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_willpower is None and card_type in CARD_TYPES_WILLPOWER:
            message = 'No willpower for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_willpower is not None and
              card_type not in CARD_TYPES_WILLPOWER):
            message = 'Redundant willpower for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_willpower is not None and
              not re.match('^[1-9]?[0-9]$', str(card_willpower)) and
              card_willpower != '-' and card_willpower != 'X'):
            message = 'Incorrect willpower value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_willpower_back is not None and card_type_back is None:
            message = 'Redundant willpower back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_willpower_back is None and
              card_type_back in CARD_TYPES_WILLPOWER):
            message = 'No willpower back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_willpower_back is not None and
              card_type_back not in CARD_TYPES_WILLPOWER):
            message = 'Redundant willpower back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_willpower_back is not None and
              not re.match('^[1-9]?[0-9]$', str(card_willpower_back)) and
              card_willpower_back != '-' and card_willpower_back != 'X'):
            message = 'Incorrect willpower back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_attack is None and card_type in CARD_TYPES_COMBAT:
            message = 'No attack for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_attack is not None and
              card_type not in CARD_TYPES_COMBAT):
            message = 'Redundant attack for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_attack is not None and
              not re.match('^[1-9]?[0-9]$', str(card_attack)) and
              card_attack != '-' and card_attack != 'X'):
            message = 'Incorrect attack value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_attack_back is not None and card_type_back is None:
            message = 'Redundant attack back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_attack_back is None and
              card_type_back in CARD_TYPES_COMBAT):
            message = 'No attack back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_attack_back is not None and
              card_type_back not in CARD_TYPES_COMBAT):
            message = 'Redundant attack back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_attack_back is not None and
              not re.match('^[1-9]?[0-9]$', str(card_attack_back)) and
              card_attack_back != '-' and card_attack_back != 'X'):
            message = 'Incorrect attack back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_defense is None and card_type in CARD_TYPES_COMBAT:
            message = 'No defense for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_defense is not None and
              card_type not in CARD_TYPES_COMBAT):
            message = 'Redundant defense for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_defense is not None and
              not re.match('^[1-9]?[0-9]$', str(card_defense)) and
              card_defense != '-' and card_defense != 'X'):
            message = 'Incorrect defense value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_defense_back is not None and card_type_back is None:
            message = 'Redundant defense back for row #{}{}'.format(i,
                                                                    row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_defense_back is None and
              card_type_back in CARD_TYPES_COMBAT):
            message = 'No defense back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_defense_back is not None and
              card_type_back not in CARD_TYPES_COMBAT):
            message = 'Redundant defense back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_defense_back is not None and
              not re.match('^[1-9]?[0-9]$', str(card_defense_back)) and
              card_defense_back != '-' and card_defense_back != 'X'):
            message = 'Incorrect defense back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_health is None and card_type in CARD_TYPES_COMBAT:
            message = 'No health for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_health is not None and
              card_type not in CARD_TYPES_COMBAT):
            message = 'Redundant health for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_health is not None and
              not re.match('^[1-9]?[0-9]$', str(card_health)) and
              card_health != '-' and card_health != 'X'):
            message = 'Incorrect health value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_health_back is not None and card_type_back is None:
            message = 'Redundant health back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_health_back is None and
              card_type_back in CARD_TYPES_COMBAT):
            message = 'No health back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_health_back is not None and
              card_type_back not in CARD_TYPES_COMBAT):
            message = 'Redundant health back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_health_back is not None and
              not re.match('^[1-9]?[0-9]$', str(card_health_back)) and
              card_health_back != '-' and card_health_back != 'X'):
            message = 'Incorrect health back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_quest is None and card_type in CARD_TYPES_QUEST and
                card_sphere not in CARD_SPHERES_NO_QUEST):
            message = 'No quest points for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_quest is not None and
              (card_type not in CARD_TYPES_QUEST or
               card_sphere in CARD_SPHERES_NO_QUEST)):
            message = 'Redundant quest points for row #{}{}'.format(i,
                                                                    row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_quest is not None and
              not re.match('^[1-9]?[0-9]$', str(card_quest)) and
              card_quest != '-' and card_quest != 'X'):
            message = 'Incorrect quest points value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_quest_back is not None and card_type_back is None:
            message = 'Redundant quest points back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_quest_back is None and (
                card_type_back in CARD_TYPES_QUEST
                or card_type in CARD_TYPES_QUEST_BACK) and
              card_sphere_back not in CARD_SPHERES_NO_QUEST):
            message = 'No quest points back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_quest_back is not None and
              (card_type_back not in CARD_TYPES_QUEST or
               card_sphere_back in CARD_SPHERES_NO_QUEST) and
              card_type not in CARD_TYPES_QUEST_BACK):
            message = 'Redundant quest points back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_quest_back is not None and
              not re.match('^[1-9]?[0-9]$', str(card_quest_back)) and
              card_quest_back != '-' and card_quest_back != 'X'):
            message = 'Incorrect quest points back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_victory is not None and card_type in ('Presentation', 'Rules'):
            if len(str(card_victory).split('/')) != 2:
                message = ('Incorrect format for victory points for row '
                           '#{}{}'.format(i, row_info))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            elif not (is_positive_int(str(card_victory)
                                      .split('/', maxsplit=1)[0]) and
                      is_positive_int(str(card_victory).split('/')[1])):
                message = ('Incorrect format for victory points for row '
                           '#{}{}'.format(i, row_info))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
        elif card_victory is not None and card_type not in CARD_TYPES_VICTORY:
            message = 'Redundant victory points for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_victory is not None and
              card_sphere in CARD_SPHERES_NO_VICTORY):
            message = 'Redundant victory points for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_victory_back is not None and card_type_back is None:
            message = 'Redundant victory points back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_victory_back is not None and card_type_back == 'Rules':
            if len(str(card_victory_back).split('/')) != 2:
                message = ('Incorrect format for victory points back for row '
                           '#{}{}'.format(i, row_info))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            elif not (is_positive_int(str(card_victory_back)
                                      .split('/', maxsplit=1)[0]) and
                      is_positive_int(str(card_victory_back).split('/')[1])):
                message = ('Incorrect format for victory points back for row '
                           '#{}{}'.format(i, row_info))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
        elif (card_victory_back is not None and
              card_type_back not in CARD_TYPES_VICTORY and
              card_type not in CARD_TYPES_VICTORY_BACK):
            message = 'Redundant victory points back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_victory_back is not None and
              card_sphere_back in CARD_SPHERES_NO_VICTORY):
            message = 'Redundant victory points back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_special_icon is not None and
                card_special_icon.lower() not in SPECIAL_ICONS):
            message = 'Incorrect format for special icon for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_special_icon is not None and
              card_type not in CARD_TYPES_SPECIAL_ICON):
            message = 'Redundant special icon for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_special_icon is not None and
              card_sphere in CARD_SPHERES_NO_SPECIAL_ICON):
            message = 'Redundant special icon for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_special_icon_back is not None and card_type_back is None:
            message = 'Redundant special icon back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_special_icon_back is not None and
              card_special_icon_back.lower() not in SPECIAL_ICONS):
            message = ('Incorrect format for special icon back for row #{}{}'
                       .format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_special_icon_back is not None and
              card_type_back not in CARD_TYPES_SPECIAL_ICON):
            message = 'Redundant special icon back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_special_icon_back is not None and
              card_sphere_back in CARD_SPHERES_NO_SPECIAL_ICON):
            message = 'Redundant special icon back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_text is None and card_type in CARD_TYPES_TEXT:
            message = 'No text for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_text is not None and card_type in CARD_TYPES_NO_TEXT:
            message = 'Redundant text for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_text is not None and card_sphere in CARD_SPHERES_NO_TEXT:
            message = 'Redundant text for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_text is not None and card_text != 'TBD' and
              card_type not in CARD_TYPES_NO_PERIOD_CHECK and
              not _verify_period(card_text)):
            message = ('Missing period at the end of the text paragraph for '
                       'row #{}{}'.format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_text is not None and
              card_type != 'Presentation' and card_sphere != 'Back' and
              not (card_flags and 'IgnoreRules' in extract_flags(card_flags))):
            rules_errors = _get_rules_errors(card_text, CARD_TEXT, row)
            if rules_errors:
                message = (
                    'Rules error(s) in text for row #{}{}: {} (use '
                    'IgnoreRules flag to ignore)'.format(
                        i, row_info, ', '.join(rules_errors)))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

        if card_text_back is not None and card_type_back is None:
            message = 'Redundant text back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_text_back is None and
              card_type_back in CARD_TYPES_TEXT_BACK):
            message = 'No text back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_text_back is not None and
              card_type_back in CARD_TYPES_NO_TEXT_BACK):
            message = 'Redundant text back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_text_back is not None and
              card_sphere_back in CARD_SPHERES_NO_TEXT):
            message = 'Redundant text back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_text_back is not None and card_text_back != 'TBD' and
              card_type_back not in CARD_TYPES_NO_PERIOD_CHECK and
              not _verify_period(card_text_back)):
            message = ('Missing period at the end of the text back paragraph '
                       'for row #{}{}'.format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_text_back is not None and
              card_type_back != 'Presentation' and
              card_sphere != 'Back' and
              not (card_flags_back and
                   'IgnoreRules' in extract_flags(card_flags_back))):
            rules_errors = _get_rules_errors(card_text_back,
                                             BACK_PREFIX + CARD_TEXT, row)
            if rules_errors:
                message = (
                    'Rules error(s) in text back for row #{}{}: {} (use '
                    'IgnoreRules flag to ignore)'.format(
                        i, row_info, ', '.join(rules_errors)))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

        if (card_text is not None and '[split]' in card_text and
                card_sphere != 'Cave'):
            message = 'Invalid [split] tag in text for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_text_back is not None and '[split]' in card_text_back and
                card_sphere_back != 'Cave'):
            message = 'Invalid [split] tag in text back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_shadow is not None and card_type not in CARD_TYPES_SHADOW and
                not (card_type in CARD_TYPES_SHADOW_ENCOUNTER and
                     ('Encounter' in extract_keywords(card_keywords) or
                      card_back == 'Encounter'))):
            message = 'Redundant shadow for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_shadow is not None and card_shadow != 'TBD' and
              not _verify_period(card_shadow)):
            message = ('Missing period at the end of shadow for row #{}{}'
                       .format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_shadow is not None and
              not (card_flags and 'IgnoreRules' in extract_flags(card_flags))):
            rules_errors = _get_rules_errors(card_shadow, CARD_SHADOW, row)
            if rules_errors:
                message = (
                    'Rules error(s) in shadow for row #{}{}: {} (use '
                    'IgnoreRules flag to ignore)'.format(
                        i, row_info, ', '.join(rules_errors)))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

        if card_shadow_back is not None and card_type_back is None:
            message = 'Redundant shadow back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_shadow_back is not None:
            message = 'Redundant shadow back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_shadow_back is not None and card_shadow_back != 'TBD' and
              not _verify_period(card_shadow_back)):
            message = ('Missing period at the end of shadow back for row '
                       '#{}{}'.format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_shadow_back is not None and
              not (card_flags_back and
                   'IgnoreRules' in extract_flags(card_flags_back))):
            rules_errors = _get_rules_errors(card_shadow_back,
                                             BACK_PREFIX + CARD_SHADOW, row)
            if rules_errors:
                message = (
                    'Rules error(s) in shadow back for row #{}{}: {} (use '
                    'IgnoreRules flag to ignore)'.format(
                        i, row_info, ', '.join(rules_errors)))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

        if (card_flavour is not None and
                (card_type in CARD_TYPES_NO_FLAVOUR or
                 card_sphere in CARD_SPHERES_NO_FLAVOUR)):
            message = 'Redundant flavour for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_flavour_back is not None and card_type_back is None:
            message = 'Redundant flavour back for row #{}{}'.format(i,
                                                                    row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_flavour_back is not None and
              (card_type_back in CARD_TYPES_NO_FLAVOUR_BACK or
               card_sphere_back in CARD_SPHERES_NO_FLAVOUR)):
            message = 'Redundant flavour back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_printed_number is not None and
                card_type in CARD_TYPES_NO_PRINTED_NUMBER):
            message = 'Redundant printed number for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_printed_number_back is not None and card_type_back is None:
            message = 'Redundant printed number back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_printed_number_back is not None and
              card_type_back in CARD_TYPES_NO_PRINTED_NUMBER_BACK):
            message = 'Redundant printed number back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_encounter_set_number is not None and
                (card_type not in CARD_TYPES_ENCOUNTER_SET_NUMBER or
                 card_sphere in ('Boon', 'Burden'))):
            message = 'Redundant encounter set number for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_encounter_set_number_back is not None and
                card_type_back is None):
            message = ('Redundant encounter set number back for row #{}{}'
                       .format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_encounter_set_number_back is not None and
              (card_type_back not in CARD_TYPES_ENCOUNTER_SET_NUMBER or
               card_sphere_back in ('Boon', 'Burden'))):
            message = ('Redundant encounter set number back for row #{}{}'
                       .format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_encounter_set_icon is not None and
                (card_type not in CARD_TYPES_ENCOUNTER_SET_ICON or
                 card_sphere == 'Boon')):
            message = 'Redundant encounter set icon for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_encounter_set_icon_back is not None and
                card_type_back is None):
            message = ('Redundant encounter set icon back for row #{}{}'
                       .format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_encounter_set_icon_back is not None and
              (card_type_back not in CARD_TYPES_ENCOUNTER_SET_ICON or
               card_sphere_back == 'Boon')):
            message = ('Redundant encounter set icon back for row #{}{}'
                       .format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_flags is not None:
            flags = extract_flags(card_flags)
            if not flags:
                message = 'Incorrect flags for row #{}{}'.format(i, row_info)
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            elif len(flags) != len(set(flags)):
                message = 'Duplicate flags for row #{}{}'.format(i, row_info)
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            elif [f for f in flags if f not in FLAGS]:
                message = 'Incorrect flags for row #{}{}'.format(i, row_info)
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

            found_ring_flag = False
            for flag in flags:
                if ((flag in CARD_TYPES_FLAGS and  # pylint: disable=R0916
                     card_type not in CARD_TYPES_FLAGS[flag]) or
                        (flag in CARD_TYPES_NO_FLAGS and
                         card_type in CARD_TYPES_NO_FLAGS[flag]) or
                        (flag in CARD_SPHERES_NO_FLAGS and
                         card_sphere in CARD_SPHERES_NO_FLAGS[flag])):
                    message = 'Redundant flag "{}" for row #{}{}'.format(
                        flag, i, row_info)
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)
                elif flag in RING_FLAGS:
                    if found_ring_flag:
                        message = ('More than one ring flag for row #{}{}'
                                   .format(i, row_info))
                        logging.error(message)
                        if not card_scratch:
                            errors.append(message)
                        else:
                            broken_set_ids.add(set_id)
                    else:
                        found_ring_flag = True

        if card_flags_back is not None:
            flags = extract_flags(card_flags_back)
            if not flags:
                message = 'Incorrect flags back for row #{}{}'.format(i,
                                                                      row_info)
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            elif len(flags) != len(set(flags)):
                message = 'Duplicate flags back for row #{}{}'.format(i,
                                                                      row_info)
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            elif [f for f in flags if f not in FLAGS]:
                message = 'Incorrect flags back for row #{}{}'.format(i,
                                                                      row_info)
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

            found_ring_flag = False
            for flag in flags:
                if ((flag in CARD_TYPES_FLAGS_BACK and  # pylint: disable=R0916
                     card_type_back not in CARD_TYPES_FLAGS_BACK[flag]) or
                        (flag in CARD_TYPES_NO_FLAGS_BACK and
                         card_type_back in CARD_TYPES_NO_FLAGS_BACK[flag]) or
                        (flag in CARD_SPHERES_NO_FLAGS and
                         card_sphere_back in CARD_SPHERES_NO_FLAGS[flag])):
                    message = 'Redundant flag back "{}" for row #{}{}'.format(
                        flag, i, row_info)
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)
                elif flag in RING_FLAGS:
                    if found_ring_flag:
                        message = ('More than one ring flag back for row #{}{}'
                                   .format(i, row_info))
                        logging.error(message)
                        if not card_scratch:
                            errors.append(message)
                        else:
                            broken_set_ids.add(set_id)
                    else:
                        found_ring_flag = True

        if (card_artist is not None and
                card_type in CARD_TYPES_NO_ARTIST):
            message = 'Redundant artist for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_artist is not None and 'Hogdson' in card_artist:
            message = 'Hodgson not Hogdson in row #{}{}!'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_artist_back is not None and card_type_back is None:
            message = 'Redundant artist back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_artist_back is not None and
              card_type_back in CARD_TYPES_NO_ARTIST_BACK):
            message = 'Redundant artist back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_artist_back is not None and 'Hogdson' in card_artist_back:
            message = 'Hodgson not Hogdson in row #{}{}!'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_panx is not None and
                card_type in CARD_TYPES_NO_ARTWORK):
            message = 'Redundant panx for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_panx is None and
              (card_pany is not None or card_scale is not None)):
            message = 'No panx for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_panx is not None and not _is_float(card_panx):
            message = 'Incorrect format for panx for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_panx_back is not None and card_type_back is None:
            message = 'Redundant panx back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_panx_back is not None and
              card_type_back in CARD_TYPES_NO_ARTWORK_BACK):
            message = 'Redundant panx back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_panx_back is None and
              (card_pany_back is not None or card_scale_back is not None)):
            message = 'No panx back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_panx_back is not None and not _is_float(card_panx_back):
            message = 'Incorrect format for panx back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_pany is not None and
                card_type in CARD_TYPES_NO_ARTWORK):
            message = 'Redundant pany for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_pany is None and
              (card_panx is not None or card_scale is not None)):
            message = 'No pany for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_pany is not None and not _is_float(card_pany):
            message = 'Incorrect format for pany for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_pany_back is not None and card_type_back is None:
            message = 'Redundant pany back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_pany_back is not None and
              card_type_back in CARD_TYPES_NO_ARTWORK_BACK):
            message = 'Redundant pany back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_pany_back is None and
              (card_panx_back is not None or card_scale_back is not None)):
            message = 'No pany back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_pany_back is not None and not _is_float(card_pany_back):
            message = 'Incorrect format for pany back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_scale is not None and
                card_type in CARD_TYPES_NO_ARTWORK):
            message = 'Redundant scale for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_scale is None and
              (card_panx is not None or card_pany is not None)):
            message = 'No scale for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_scale is not None and not _is_positive_float(card_scale):
            message = 'Incorrect format for scale for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_scale_back is not None and card_type_back is None:
            message = 'Redundant scale back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_scale_back is not None and
              card_type_back in CARD_TYPES_NO_ARTWORK_BACK):
            message = 'Redundant scale back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_scale_back is None and
              (card_panx_back is not None or card_pany_back is not None)):
            message = 'No scale back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_scale_back is not None and
              not _is_positive_float(card_scale_back)):
            message = 'Incorrect format for scale back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_portrait_shadow is not None and
                card_type not in CARD_TYPES_LANDSCAPE):
            message = 'Redundant portrait shadow for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_portrait_shadow not in (None, 'Black', 'PortraitTint'):
            message = ('Incorrect value for portrait shadow for row #{}{}'
                       .format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_type != 'Quest' and card_portrait_shadow == 'PortraitTint':
            message = ('Incorrect value for portrait shadow for row #{}{}'
                       .format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_portrait_shadow_back is not None and card_type_back is None:
            message = 'Redundant portrait shadow back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_portrait_shadow_back is not None and
              card_type_back not in CARD_TYPES_LANDSCAPE):
            message = 'Redundant portrait shadow back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_portrait_shadow_back not in (None, 'Black'):
            message = ('Incorrect value for portrait shadow back for row '
                       '#{}{}'.format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_easy_mode is not None and  # pylint: disable=R0916
                (card_type not in CARD_TYPES_EASY_MODE
                 or card_sphere in CARD_SPHERES_NO_EASY_MODE) and
                (card_type_back not in CARD_TYPES_EASY_MODE or
                 card_type_back is None or
                 card_sphere_back in CARD_SPHERES_NO_EASY_MODE)):
            message = 'Redundant removed for easy mode for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_easy_mode is not None and
              not is_positive_int(card_easy_mode)):
            message = ('Incorrect format for removed for easy mode for row '
                       '#{}{}'.format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_easy_mode is not None and
              is_positive_int(card_quantity) and
              int(card_easy_mode) > int(card_quantity)):
            message = ('Removed for easy mode is greater than card quantity '
                       'for row #{}{}'.format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_additional_encounter_sets is not None and
                card_type not in CARD_TYPES_ADDITIONAL_ENCOUNTER_SETS):
            message = ('Redundant additional encounter sets for row #{}{}'
                       .format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_additional_encounter_sets is not None and
              len([s.strip() for s in card_additional_encounter_sets.split(';')
                   if s.strip()]) > 5):
            message = ('Too many additional encounter sets for row #{}{}'
                       .format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_adventure is not None and
                card_type not in CARD_TYPES_ADVENTURE and
                (card_type_back not in CARD_TYPES_ADVENTURE or
                 card_type_back is None)):
            message = 'Redundant adventure for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_adventure is None and
              (card_type in CARD_TYPES_SUBTITLE or
               card_type_back in CARD_TYPES_SUBTITLE)):
            message = 'No adventure for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_adventure is not None and
              not (card_flags and 'IgnoreName' in extract_flags(card_flags))):
            capitalization_errors = _get_capitalization_errors(card_adventure)
            if capitalization_errors:
                message = (
                    'Capitalization error(s) in adventure for row #{}{}: '
                    '{} (use IgnoreName flag to ignore)'.format(
                        i, row_info, ', '.join(capitalization_errors)))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

        if card_icon is not None and card_type in CARD_TYPES_NO_ICON:
            message = 'Redundant collection icon for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_copyright is not None and card_type in CARD_TYPES_NO_COPYRIGHT:
            message = 'Redundant copyright for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_back is not None and
                (card_type in CARD_TYPES_DOUBLESIDE_MANDATORY or
                 card_type_back is not None)):
            message = 'Redundant custom card back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_back not in (None, 'Encounter', 'Player'):
            message = 'Incorrect custom card back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        for key, value in row.items():
            if value == '#REF!':
                message = ('Reference error in {} column for row '
                           '#{}{}'.format(key.replace(BACK_PREFIX, 'Back '), i,
                                          row_info))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            elif isinstance(value, str) and '[unmatched quot]' in value:
                message = ('Unmatched quote character in {} column for row '
                           '#{}{}'.format(key.replace(BACK_PREFIX, 'Back '), i,
                                          row_info))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

            if (key in ONE_LINE_COLUMNS and isinstance(value, str) and
                    '\n' in value):
                message = ('Line break in {} column for row #{}{}'.format(
                    key.replace(BACK_PREFIX, 'Back '), i, row_info))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

            if key != CARD_DECK_RULES and isinstance(value, str):
                cleaned_value = _clean_tags(value)
                if key == CARD_SET:
                    cleaned_value = cleaned_value.replace('[filtered set]', '')
                elif key in (CARD_FLAVOUR, BACK_PREFIX + CARD_FLAVOUR):
                    cleaned_value = cleaned_value.replace('[...]', '')

                unknown_tags = re.findall(r'\[[^\]\n]+\]', cleaned_value)
                if unknown_tags:
                    message = ('Unknown tag(s) in {} column for row #{}{}: {}'
                               .format(key.replace(BACK_PREFIX, 'Back '), i,
                                       row_info, ', '.join(unknown_tags)))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)
                elif '[' in cleaned_value or ']' in cleaned_value:
                    message = ('Unmatched square bracket(s) in {} '
                               'column for row #{}{} (use "[lsb]" and "[rsb]" '
                               'tags if needed)'.format(
                                   key.replace(BACK_PREFIX, 'Back '), i,
                                   row_info))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

                unmatched_tags = _detect_unmatched_tags(value)
                if unmatched_tags:
                    message = ('Unmatched tag(s) in {} column for row #{}{}: '
                               '{}'.format(key.replace(BACK_PREFIX, 'Back '),
                                           i, row_info,
                                           ', '.join(unmatched_tags)))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

                if re.search(r'[0-9X]\[(?:attack|defense|willpower|threat)\]',
                             value):
                    message = (
                        'No space before [attack|defense|willpower|threat] '
                        'in {} column for row #{}{}'
                        .format(key.replace(BACK_PREFIX, 'Back '), i, row_info))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

                if re.search(r'[0-9X] \[pp\]', value):
                    message = (
                        'Redundant space before [pp] in {} column for row '
                        '#{}{}'.format(
                            key.replace(BACK_PREFIX, 'Back '), i, row_info))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

                if 'Middle-Earth' in value:
                    message = (
                        '"Middle-earth" not "Middle-Earth" in {} column for '
                        'row #{}{}'.format(
                            key.replace(BACK_PREFIX, 'Back '), i, row_info))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

                ignore_accents = False
                if key.startswith(BACK_PREFIX):
                    if (card_flags_back and
                            'IgnoreName' in extract_flags(card_flags_back)):
                        ignore_accents = True
                else:
                    if (card_flags and
                            'IgnoreName' in extract_flags(card_flags)):
                        ignore_accents = True

                if not ignore_accents:
                    accents = set(re.findall(accents_regex, value))
                    if accents:
                        message = (
                            'Missing accents in {} column for row #{}{}: {} '
                            '(use IgnoreName flag to ignore)'
                            .format(key.replace(BACK_PREFIX, 'Back '), i,
                                    row_info, ', '.join(accents)))
                        logging.error(message)
                        if not card_scratch:
                            errors.append(message)
                        else:
                            broken_set_ids.add(set_id)

        if (card_deck_rules is not None and
                card_type not in CARD_TYPES_DECK_RULES):
            message = 'Redundant deck rules for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_deck_rules is not None and
              card_type in CARD_TYPES_DECK_RULES):
            quest_id = (set_id, card_adventure or card_name)
            if quest_id in deck_rules:
                message = (
                    'Duplicate deck rules for quest {} in row #{}{}'.format(
                        card_adventure or card_name, i, row_info))
                logging.error(message)
                if conf['octgn_o8d']:
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)
            else:
                deck_rules.add(quest_id)

            deck_rules_errors = _generate_octgn_o8d_quest(row)[1]
            for error in deck_rules_errors:
                message = '{} in deck rules in row #{}{}'.format(
                    error, i, row_info)
                logging.error(message)
                if conf['octgn_o8d']:
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

        for lang in conf['languages']:
            if lang == 'English' or card_scratch:
                continue

            if not TRANSLATIONS[lang].get(card_id):
                logging.error(
                    'No card ID %s in %s translations', card_id, lang)
                continue

            for key, value in TRANSLATIONS[lang][card_id].items():
                if key not in TRANSLATED_COLUMNS:
                    continue

                if value == '#REF!':
                    logging.error(
                        'Reference error in %s column for card ID %s in %s '
                        'translations, row #%s', key.replace(BACK_PREFIX,
                                                             'Back '),
                        card_id, lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])
                elif isinstance(value, str) and '[unmatched quot]' in value:
                    logging.error(
                        'Unmatched quote character in %s column for card '
                        'ID %s in %s translations, row #%s',
                        key.replace(BACK_PREFIX, 'Back '), card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

                if (key in ONE_LINE_COLUMNS and isinstance(value, str) and
                        '\n' in value):
                    logging.error(
                        'Line break in %s column for card ID %s in %s '
                        'translations, row #%s',
                        key.replace(BACK_PREFIX, 'Back '), card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

                if isinstance(value, str):
                    cleaned_value = _clean_tags(value)
                    if key in (CARD_FLAVOUR, BACK_PREFIX + CARD_FLAVOUR):
                        cleaned_value = cleaned_value.replace('[...]', '')

                    if lang == 'French':
                        cleaned_value = re.sub(
                            r'(?:\[Vaillance\]|\[Ressource\]|\[Organisation\]|'
                            r'\[Qu\u00eate\]|\[Voyage\]|\[Rencontre\]|'
                            r'\[Combat\]|\[Restauration\]) ', '',
                            cleaned_value)

                    unknown_tags = re.findall(r'\[[^\]\n]+\]', cleaned_value)
                    if unknown_tags:
                        logging.error(
                            'Unknown tag(s) in %s column for card ID %s in %s '
                            'translations, row #%s: %s',
                            key.replace(BACK_PREFIX, 'Back '), card_id, lang,
                            TRANSLATIONS[lang][card_id][ROW_COLUMN],
                            ', '.join(unknown_tags))
                    elif '[' in cleaned_value or ']' in cleaned_value:
                        logging.error(
                            'Unmatched square bracket(s) in %s '
                            'column for card ID %s in %s translations, '
                            'row #%s (use "[lsb]" and "[rsb]" tags if needed)',
                            key.replace(BACK_PREFIX, 'Back '), card_id,
                            lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

                    unmatched_tags = _detect_unmatched_tags(value)
                    if unmatched_tags:
                        logging.error(
                            'Unmatched tag(s) in %s column for card ID %s in '
                            '%s translations, row #%s: %s',
                            key.replace(BACK_PREFIX, 'Back '), card_id, lang,
                            TRANSLATIONS[lang][card_id][ROW_COLUMN],
                            ', '.join(unmatched_tags))


                    if re.search(
                            r'[0-9X]\[(?:attack|defense|willpower|threat)\]',
                            value):
                        logging.error(
                            'No space before [attack|defense|willpower|threat]'
                            ' in %s column for card ID %s in %s translations,'
                            ' row #%s',
                            key.replace(BACK_PREFIX, 'Back '), card_id, lang,
                            TRANSLATIONS[lang][card_id][ROW_COLUMN])

                    if re.search(r'[0-9X] \[pp\]', value):
                        logging.error(
                            'Redundant space before [pp] in %s column for card'
                            ' ID %s in %s translations, row #%s',
                            key.replace(BACK_PREFIX, 'Back '), card_id, lang,
                            TRANSLATIONS[lang][card_id][ROW_COLUMN])

                if not value and row.get(key):
                    logging.error(
                        'Missing value for %s column for card '
                        'ID %s in %s translations, row #%s',
                        key.replace(BACK_PREFIX, 'Back '), card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])
                elif value and not row.get(key):
                    logging.error(
                        'Redundant value for %s column for card '
                        'ID %s in %s translations, row #%s',
                        key.replace(BACK_PREFIX, 'Back '), card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

            if card_traits is not None:
                card_traits_tr = TRANSLATIONS[lang][card_id].get(
                    CARD_TRAITS, '')
                if (len(extract_traits(card_traits_tr)) !=
                        len(extract_traits(card_traits))):
                    logging.error(
                        'Incorrect number of traits for card '
                        'ID %s in %s translations, row #%s', card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])
                elif (not str(card_traits_tr).endswith('.') and
                      not str(card_traits_tr).endswith('.[/size]')):
                    logging.error(
                        'Missing period in traits for card '
                        'ID %s in %s translations, row #%s', card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

            if card_traits_back is not None:
                card_traits_back_tr = TRANSLATIONS[lang][card_id].get(
                    BACK_PREFIX + CARD_TRAITS, '')
                if (len(extract_traits(card_traits_back_tr)) !=
                        len(extract_traits(card_traits_back))):
                    logging.error(
                        'Incorrect number of traits back for card '
                        'ID %s in %s translations, row #%s', card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])
                elif (not str(card_traits_back_tr).endswith('.') and
                      not str(card_traits_back_tr).endswith('.[/size]')):
                    logging.error(
                        'Missing period in traits back for card '
                        'ID %s in %s translations, row #%s', card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

            if card_keywords is not None:
                card_keywords_tr = TRANSLATIONS[lang][card_id].get(
                    CARD_KEYWORDS, '')
                if (len(extract_keywords(card_keywords_tr)) !=
                        len(extract_keywords(card_keywords))):
                    logging.error(
                        'Incorrect number of keywords for card '
                        'ID %s in %s translations, row #%s', card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])
                elif not (str(card_keywords_tr).endswith('.') or
                          str(card_keywords_tr).endswith('.[inline]')):
                    logging.error(
                        'Missing period in keywords for card '
                        'ID %s in %s translations, row #%s', card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

            if card_keywords_back is not None:
                card_keywords_back_tr = TRANSLATIONS[lang][card_id].get(
                    BACK_PREFIX + CARD_KEYWORDS, '')
                if (len(extract_keywords(card_keywords_back_tr)) !=
                        len(extract_keywords(card_keywords_back))):
                    logging.error(
                        'Incorrect number of keywords back for card '
                        'ID %s in %s translations, row #%s', card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])
                elif not (str(card_keywords_back_tr).endswith('.') or
                          str(card_keywords_back_tr).endswith('.[inline]')):
                    logging.error(
                        'Missing period in keywords back for card '
                        'ID %s in %s translations, row #%s', card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

            if (card_victory is not None and
                    (is_positive_or_zero_int(card_victory) or
                     card_type in ('Presentation', 'Rules')) and
                    card_victory !=
                    TRANSLATIONS[lang][card_id].get(CARD_VICTORY, '')):
                logging.error(
                    'Incorrect victory points for card '
                    'ID %s in %s translations, row #%s', card_id,
                    lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

            if (card_victory_back is not None and
                    (is_positive_or_zero_int(card_victory_back) or
                     card_type == 'Rules') and
                    card_victory_back != TRANSLATIONS[lang][card_id].get(
                        BACK_PREFIX + CARD_VICTORY, '')):
                logging.error(
                    'Incorrect victory points back for card '
                    'ID %s in %s translations, row #%s', card_id,
                    lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

            if card_text is not None:
                card_text_tr = TRANSLATIONS[lang][card_id].get(CARD_TEXT, '')
                if (card_type not in CARD_TYPES_NO_PERIOD_CHECK and
                      not _verify_period(card_text_tr)):
                    logging.error(
                        'Missing period at the end of the text paragraph for '
                        'card ID %s in %s translations, row #%s', card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

                if '[split]' in card_text and '[split]' not in card_text_tr:
                    logging.error(
                        'Missing [split] tag in text for card ID %s in %s '
                        'translations, row #%s', card_id, lang,
                        TRANSLATIONS[lang][card_id][ROW_COLUMN])
                elif '[split]' not in card_text and '[split]' in card_text_tr:
                    logging.error(
                        'Invalid [split] tag in text for card ID %s in %s '
                        'translations, row #%s', card_id, lang,
                        TRANSLATIONS[lang][card_id][ROW_COLUMN])

            if card_text_back is not None:
                card_text_back_tr = TRANSLATIONS[lang][card_id].get(
                    BACK_PREFIX + CARD_TEXT, '')
                if (card_type_back not in CARD_TYPES_NO_PERIOD_CHECK and
                      not _verify_period(card_text_back_tr)):
                    logging.error(
                        'Missing period at the end of the text back paragraph '
                        'for card ID %s in %s translations, row #%s', card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

                if ('[split]' in card_text_back and
                        '[split]' not in card_text_back_tr):
                    logging.error(
                        'Missing [split] tag in text back for card ID %s in '
                        '%s translations, row #%s', card_id, lang,
                        TRANSLATIONS[lang][card_id][ROW_COLUMN])
                elif ('[split]' not in card_text_back and
                      '[split]' in card_text_back_tr):
                    logging.error(
                        'Invalid [split] tag in text back for card ID %s in '
                        '%s translations, row #%s', card_id, lang,
                        TRANSLATIONS[lang][card_id][ROW_COLUMN])

            if card_shadow is not None:
                card_shadow_tr = TRANSLATIONS[lang][card_id].get(
                    CARD_SHADOW, '')
                if not _verify_period(card_shadow_tr):
                    logging.error(
                        'Missing period at the end of shadow for card ID %s '
                        'in %s translations, row #%s', card_id, lang,
                        TRANSLATIONS[lang][card_id][ROW_COLUMN])

            if card_shadow_back is not None:
                card_shadow_back_tr = TRANSLATIONS[lang][card_id].get(
                    BACK_PREFIX + CARD_SHADOW, '')
                if not _verify_period(card_shadow_back_tr):
                    logging.error(
                        'Missing period at the end of shadow back for card ID '
                        '%s in %s translations, row #%s', card_id, lang,
                        TRANSLATIONS[lang][card_id][ROW_COLUMN])

    logging.info('')
    if errors:
        raise SanityCheckError('Sanity check failed:\n{}'.format(
            '\n'.join(errors)))

    sets = [s for s in sets if s[0] not in broken_set_ids]
    logging.info('...Performing a sanity check of the spreadsheet (%ss)',
                 round(time.time() - timestamp, 3))
    return sets


def _has_discord_channel(card):
    """ Check whether a card has Discord channel or not.
    """
    if (card[CARD_NAME] == 'T.B.D.'
            or card[CARD_TYPE] in CARD_TYPES_NO_DISCORD_CHANNEL):
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


def save_data_for_bot(conf, sets):  # pylint: disable=R0912,R0914,R0915
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
        with open(DISCORD_CARD_DATA_PATH, 'r', encoding='utf-8') as obj:
            old_data = json.load(obj)['data']
    except Exception:
        old_data = None

    modified_card_ids = []
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
                modified_card_ids.append(card_id)
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
                          new_dict[card_id][CARD_DISCORD_CATEGORY]),
                         (card_id, None, new_dict[card_id][CARD_SET])))
            elif old_dict[card_id] != new_dict[card_id]:
                diffs = _get_card_diffs(old_dict[card_id], new_dict[card_id])
                if diffs:
                    modified_card_ids.append(card_id)
                    if not new_dict[card_id].get(CARD_BOT_DISABLED):
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
                         new_dict[card_id][CARD_DISCORD_CATEGORY]),
                        (card_id, old_dict[card_id][CARD_SET],
                         new_dict[card_id][CARD_SET])))

        for card_id in old_dict:
            if card_id not in new_dict:
                if old_dict[card_id].get(CARD_DISCORD_CHANNEL):
                    channel_diffs.append(
                        ((old_dict[card_id][CARD_DISCORD_CHANNEL],
                          old_dict[card_id][CARD_DISCORD_CATEGORY]),
                         None,
                         (card_id, old_dict[card_id][CARD_SET], None)))

                modified_card_ids.append(card_id)
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
            channel_changes.append(('add', diff[1], None))
        elif not diff[1]:
            channel_changes.append(
                ('remove', diff[0][0],
                 {'card_id': diff[2][0],
                  'old_set_id': diff[2][1],
                  'new_set_id': diff[2][2]}))
        elif diff[0][0] == diff[1][0]:
            if ('rename', (diff[0][1], diff[1][1])) not in category_changes:
                channel_changes.append(
                    ('move', diff[1],
                     {'card_id': diff[2][0],
                      'old_set_id': diff[2][1],
                      'new_set_id': diff[2][2]}))
        elif diff[0][1] == diff[1][1]:
            channel_changes.append(('rename', (diff[0][0], diff[1][0]), None))
        else:
            if ('rename', (diff[0][1], diff[1][1])) not in category_changes:
                channel_changes.append(
                    ('move', (diff[0][0], diff[1][1]),
                     {'card_id': diff[2][0],
                      'old_set_id': diff[2][1],
                      'new_set_id': diff[2][2]}))

            channel_changes.append(('rename', (diff[0][0], diff[1][0]), None))

    set_names = [SETS[set_id][SET_NAME] for set_id in FOUND_SETS]
    set_ids = {set_id:SETS[set_id][SET_NAME] for set_id in FOUND_SETS}
    set_codes = {
        (SETS[set_id][SET_HOB_CODE] or '').lower():SETS[set_id][SET_NAME]
        for set_id in FOUND_SETS}
    valid_set_ids = {s[0] for s in sets}
    artwork_ids = {
        row[CARD_ID]:{
            CARD_SET: row[CARD_SET],
            CARD_NAME: row[CARD_NAME],
            CARD_TYPE: row[CARD_TYPE],
            BACK_PREFIX + CARD_NAME: row[BACK_PREFIX + CARD_NAME],
            BACK_PREFIX + CARD_TYPE: row[BACK_PREFIX + CARD_TYPE]}
        for row in DATA if row[CARD_SET] in valid_set_ids and
        row[CARD_TYPE] not in CARD_TYPES_NO_ARTWORK and
        not SETS[row[CARD_SET]].get(SET_LOCKED)}
    for card_id in artwork_ids:
        if not artwork_ids[card_id][BACK_PREFIX + CARD_NAME]:
            del artwork_ids[card_id][BACK_PREFIX + CARD_NAME]

        if not artwork_ids[card_id][BACK_PREFIX + CARD_TYPE]:
            del artwork_ids[card_id][BACK_PREFIX + CARD_TYPE]

    output = {'url': url,
              'sets': set_names,
              'set_ids': set_ids,
              'set_codes': set_codes,
              'set_and_quest_names': list(ALL_SET_AND_QUEST_NAMES),
              'encounter_set_names': list(ALL_ENCOUNTER_SET_NAMES),
              'card_names': list(ALL_CARD_NAMES),
              'traits': list(ALL_TRAITS),
              'artwork_ids': artwork_ids,
              'data': data}
    with open(DISCORD_CARD_DATA_PATH, 'w', encoding='utf-8') as obj:
        res = json.dumps(output, ensure_ascii=False)
        obj.write(res)

    utc_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    if (category_changes or channel_changes or card_changes or
            modified_card_ids):
        output = {'categories': category_changes,
                  'channels': channel_changes,
                  'cards': card_changes,
                  'card_ids': modified_card_ids,
                  'utc_time': utc_time}
        path = os.path.join(
            DISCORD_PATH, 'Changes',
            '{}_{}.json'.format(int(time.time()), uuid.uuid4()))
        with open(path, 'w', encoding='utf-8') as obj:
            res = json.dumps(output, ensure_ascii=False)
            obj.write(res)

    if modified_card_ids:
        try:
            with open(DISCORD_TIMESTAMPS_PATH, 'r', encoding='utf-8') as obj:
                timestamps = json.load(obj)
        except Exception:
            timestamps = {}

        for card_id in modified_card_ids:
            timestamps[card_id] = utc_time

        with open(DISCORD_TIMESTAMPS_PATH, 'w', encoding='utf-8') as obj:
            res = json.dumps(timestamps)
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
    """ Backup a previous xml file.
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
        if card_type in ('Player Objective', 'Treasure'):
            value = 'Neutral'
        elif card_type in ('Presentation', 'Rules'):
            value = ''
        elif value in ('Cave', 'NoProgress', 'NoStat', 'Region',
                       'SmallTextArea', 'Upgraded'):
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
        prop.set('value', _update_octgn_card_text(_to_str(handle_int(value)),
                                                  fix_linebreaks=fix_linebreaks))

        if i == len(properties) - 1:
            prop.tail = '\n' + tab
        else:
            prop.tail = '\n' + tab + '  '


def _needed_for_octgn(card):
    """ Check whether a card is needed for OCTGN or not.
    """
    return ('Promo' not in extract_flags(card[CARD_FLAGS]) and
            card[CARD_TYPE] not in ('Full Art Landscape',
                                    'Full Art Portrait', 'Presentation') and
            not (card[CARD_TYPE] == 'Rules' and card[CARD_SPHERE] == 'Back'))


def _needed_for_dragncards(card):
    """ Check whether a card is needed for DragnCards or not.
    """
    return ('Promo' not in extract_flags(card[CARD_FLAGS]) and
            card[CARD_TYPE] not in ('Full Art Landscape',
                                    'Full Art Portrait', 'Presentation') and
            not (card[CARD_TYPE] == 'Rules' and card[CARD_SPHERE] == 'Back'))


def generate_octgn_set_xml(conf, set_id, set_name):  # pylint: disable=R0912,R0914,R0915
    """ Generate set.xml file for OCTGN.
    """
    logging.info('[%s] Generating set.xml file for OCTGN...', set_name)
    timestamp = time.time()

    _backup_previous_octgn_xml(set_id)

    root = ET.fromstring(SET_XML_TEMPLATE)
    root.set('name', str(set_name))
    root.set('id', str(set_id))
    root.set('version', '1.0')
    cards = root.findall("./cards")[0]

    chosen_data = []
    for row in DATA:
        if (row[CARD_ID] is None
                or row[CARD_SET] != set_id
                or not _needed_for_octgn(row)
                or (conf['selected_only']
                    and row[CARD_ID] not in SELECTED_CARDS)):
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
               'Encounter' in extract_keywords(row[CARD_KEYWORDS]) or
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
                  or row[BACK_PREFIX + CARD_NAME])
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
                    and not row[BACK_PREFIX + CARD_NAME]):
                alternate_name = row[CARD_NAME]
            else:
                alternate_name = row[BACK_PREFIX + CARD_NAME]

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


def load_external_xml(url, sets=None, encounter_sets=None):  # pylint: disable=R0912,R0914,R0915
    """ Load cards from an external XML file.
    """
    res = []
    if url in XML_CACHE:
        content = XML_CACHE[url]
        root = ET.fromstring(content)
    else:
        content = _get_cached_content(url, 'xml')
        if content:
            XML_CACHE[url] = content
            root = ET.fromstring(content)
        else:
            content = get_content(url)
            if not content or not b'<?xml' in content:
                logging.error("Can't download XML from %s, ignoring", url)
                return res

            try:
                root = ET.fromstring(content)
            except ET.ParseError:
                logging.error("Can't download XML from %s, ignoring", url)
                return res

            if not root.attrib.get('name'):
                logging.error("Can't find the set name in XML from %s, "
                              "ignoring", url)
                return res

            XML_CACHE[url] = content
            _save_content(url, content, 'xml')

    set_name = str(root.attrib.get('name', '')).lower()
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

        text = _find_properties(card, 'Text')
        text = text[0].attrib['value'] if text else ''
        if ' Restricted.' in text or '\nRestricted.' in text:
            if keywords:
                keywords = 'Restricted. {}'.format(keywords)
            else:
                keywords = 'Restricted.'

        card_number = _find_properties(card, 'Card Number')
        card_number = (
            int(card_number[0].attrib['value'])
            if card_number
            and is_positive_or_zero_int(card_number[0].attrib['value'])
            else 0)

        unique = _find_properties(card, 'Unique')
        unique = 1 if unique else None

        cost = _find_properties(card, 'Cost')
        cost = handle_int(cost[0].attrib['value']) if cost else None

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
        row[CARD_COST] = cost
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
    card[CARD_TRAITS] = (
        [t.lower().strip()
         for t in re.sub(r'\[[^\]]+\]', '', str(card[CARD_TRAITS])).split('.')
         if t] if card[CARD_TRAITS] else [])
    card[CARD_KEYWORDS] = ([k.lower().strip()
                            for k in str(card[CARD_KEYWORDS]).replace(
                                '[inline]', '').split('.') if k]
                           if card[CARD_KEYWORDS] else [])
    card[CARD_UNIQUE] = '1' if card[CARD_UNIQUE] else '0'
    return card


def _append_cards(parent, cards):
    """ Append card elements to the section element.
    """
    cards = [c for c in cards if is_int(c[CARD_QUANTITY]) and
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
    if res and is_int(card[CARD_QUANTITY]):
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


def _apply_rules(source_cards, target_cards, rules, rule_type):
    """ Apply deck rules.
    """
    errors = []
    if not rules:
        errors.append('No "{}" rules specified'.format(rule_type.title()))
        return errors

    for rule in rules:
        total_qty = 0
        for card in source_cards:
            qty = _test_rule(card, str(rule).lower())
            if qty > 0:
                total_qty += qty
                card_copy = card.copy()
                card[CARD_QUANTITY] -= qty
                card_copy[CARD_QUANTITY] = qty
                target_cards.append(card_copy)
                res = re.match(r'^([0-9]+) ', str(rule).lower())
                if res:
                    target_qty = int(res.groups()[0])
                    if qty < target_qty:
                        errors.append(
                            'Rule "{}:{}" matches only {} not {} cards'.
                            format(rule_type.title(), rule, qty, target_qty))

        if not total_qty:
            errors.append('Rule "{}:{}" doesn\'t match any cards'
                          .format(rule_type.title(), rule))

    return errors


def _generate_octgn_o8d_player(conf, set_id, set_name):
    """ Generate .o8d file with player cards for OCTGN.
    """
    rows = [row for row in DATA
            if row[CARD_ID] is not None
            and _needed_for_octgn(row)
            and row[CARD_SET] == set_id
            and row[CARD_TYPE] in CARD_TYPES_PLAYER
            and (not conf['selected_only'] or row[CARD_ID] in SELECTED_CARDS)]
    if not rows:
        return

    cards = [_update_card_for_rules(r.copy()) for r in rows]
    root = ET.fromstring(O8D_TEMPLATE)
    _append_cards(root.findall("./section[@name='Hero']")[0], cards)

    output_path = os.path.join(OUTPUT_OCTGN_DECKS_PATH,
                               escape_filename(set_name))
    create_folder(output_path)
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


def _generate_octgn_o8d_quest(row):  # pylint: disable=R0912,R0914,R0915
    """ Generate .o8d file for the quest(s).
    """
    errors = []
    files = []

    quests = []
    quest = {'name': row[CARD_ADVENTURE] or row[CARD_NAME],
             'sets': set([str(row[CARD_SET_NAME]).lower()]),
             'encounter sets': set(),
             'prefix': '',
             'rules': row[CARD_DECK_RULES],
             'modes': ['']}
    if row[CARD_ENCOUNTER_SET]:
        quest['encounter sets'].add(str(row[CARD_ENCOUNTER_SET]).lower())

    if row[CARD_ADDITIONAL_ENCOUNTER_SETS]:
        for encounter_set in [
                r.lower().strip()
                for r in
                str(row[CARD_ADDITIONAL_ENCOUNTER_SETS]).split(';')
                if r.lower().strip()]:
            quest['encounter sets'].add(encounter_set)

    quests.append(quest)
    parts = str(quest['rules']).split('\n\n')
    parts = [part for part in parts if part]
    if len(parts) > 1:
        quest['rules'] = parts.pop(0)
        for part in parts:
            new_quest = copy.deepcopy(quest)
            new_quest['rules'] = part
            quests.append(new_quest)

    prefixes = set()
    for quest in quests:
        rules_list = [r.split(':', 1)
                      for r in str(quest['rules']).split('\n')]
        incorrect_rules = [':'.join(r) for r in rules_list if len(r) != 2]
        for item in incorrect_rules:
            errors.append('Incorrect rule "{}"'.format(item))

        rules_list = [(r[0].strip(),
                       [i.strip() for i in r[1].strip().split(';')
                        if i.strip()])
                      for r in rules_list if len(r) == 2]
        rules = OrderedDict()
        key_count = {}
        for key, value in rules_list:
            if key.lower() not in (
                    'sets', 'encounter sets', 'prefix', 'external xml',
                    'remove', 'second quest deck', 'special',
                    'second special', 'setup', 'active setup',
                    'staging setup', 'player'):
                errors.append('Unknown key "{}"'.format(key))
                continue

            if key.lower() not in key_count:
                key_count[key.lower()] = 0
            else:
                key_count[key.lower()] += 1

            if (key.lower() in ('sets', 'encounter sets', 'prefix',
                                'external xml') and
                    key_count.get(key.lower(), 0) > 0):
                errors.append('Duplicate key "{}"'.format(key))

            rules[(key.lower(), key_count[key.lower()])] = value

        if rules.get(('prefix', 0)):
            quest['prefix'] = rules[('prefix', 0)][0] + ' '
            quest['prefix'] = quest['prefix'][:6].upper() + quest['prefix'][6:]

        if not quest['prefix']:
            errors.append('No prefix')
            continue

        if not re.match(DECK_PREFIX_REGEX, quest['prefix']):
            errors.append('Incorrect prefix "{}"'
                          .format(rules.get(('prefix', 0), [''])[0]))
            continue

        if quest['prefix'] in prefixes:
            errors.append('Duplicate prefix "{}"'
                          .format(rules.get(('prefix', 0), [''])[0]))
            continue

        prefixes.add(quest['prefix'])

        if rules.get(('sets', 0)):
            quest['sets'].update([str(s).lower() for s in rules[('sets', 0)]])

        if rules.get(('encounter sets', 0)):
            quest['encounter sets'].update(
                [str(s).lower() for s in rules[('encounter sets', 0)]])

        cards = [r for r in DATA
                 if r[CARD_ID] is not None
                 and _needed_for_octgn(r)
                 and str(r[CARD_SET_NAME] or '').lower() in quest['sets']
                 and (not r[CARD_ENCOUNTER_SET] or
                      str(r[CARD_ENCOUNTER_SET]).lower()
                      in quest['encounter sets'])
                 and (r[CARD_TYPE] != 'Rules' or
                      (r.get(CARD_TEXT) or '') not in ('', 'T.B.D.') or
                      (r.get(BACK_PREFIX + CARD_TEXT) or '')
                      not in ('', 'T.B.D.'))]

        for url in rules.get(('external xml', 0), []):
            res = load_external_xml(url, quest['sets'],
                                    quest['encounter sets'])
            if res:
                cards.extend(res)
            else:
                errors.append('URL {} doesn\'t match any cards'.format(url))

        redundant_sets = [
            s for s in rules.get(('sets', 0), [])
            if str(s).lower() not in [str(c[CARD_SET_NAME] or '').lower()
                                      for c in cards]]
        for item in redundant_sets:
            errors.append('Set "{}" doesn\'t match any cards'.format(item))

        redundant_encounter_sets = [
            s for s in rules.get(('encounter sets', 0), [])
            if str(s).lower() not in [str(c[CARD_ENCOUNTER_SET] or '').lower()
                                      for c in cards]]
        for item in redundant_encounter_sets:
            errors.append('Encounter set "{}" doesn\'t match any cards'
                          .format(item))

        if [c for c in cards if c[CARD_EASY_MODE]]:
            quest['modes'].append(EASY_PREFIX)

        for mode in quest['modes']:
            mode_errors = []
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
                                 if is_int(card_copy[CARD_EASY_MODE]) else 0)
                    card_copy[CARD_QUANTITY] -= easy_mode
                    encounter_cards.append(card_copy)
                else:
                    encounter_cards.append(_update_card_for_rules(card.copy()))

            for (key, _), value in rules.items():
                if key == 'remove':
                    mode_errors.extend(_apply_rules(
                        quest_cards + default_setup_cards + encounter_cards +
                        other_cards, removed_cards, value, key))
                elif key == 'second quest deck':
                    mode_errors.extend(_apply_rules(
                        quest_cards, second_quest_cards, value, key))
                elif key == 'special':
                    mode_errors.extend(_apply_rules(
                        encounter_cards + other_cards, special_cards, value,
                        key))
                elif key == 'second special':
                    mode_errors.extend(_apply_rules(
                        encounter_cards + other_cards, second_special_cards,
                        value, key))
                elif key == 'setup':
                    mode_errors.extend(_apply_rules(
                        encounter_cards + other_cards, setup_cards, value,
                        key))
                elif key == 'staging setup':
                    mode_errors.extend(_apply_rules(
                        encounter_cards, staging_setup_cards, value, key))
                elif key == 'active setup':
                    mode_errors.extend(_apply_rules(
                        encounter_cards, active_setup_cards, value, key))
                elif key == 'player':
                    mode_errors.extend(_apply_rules(
                        other_cards, chosen_player_cards, value, key))

            setup_cards.extend(default_setup_cards)

            for section in (
                    encounter_cards, special_cards, second_special_cards,
                    setup_cards, staging_setup_cards, active_setup_cards,
                    chosen_player_cards):
                section.sort(key=lambda card: (
                    card[CARD_TYPE] not in ('presentation', 'rules'),
                    card[CARD_TYPE],
                    card[CARD_SET_NAME],
                    is_positive_or_zero_int(card[CARD_NUMBER])
                    and int(card[CARD_NUMBER]) or 0,
                    card[CARD_NUMBER],
                    card[CARD_NAME]))

            for section in (quest_cards, second_quest_cards):
                section.sort(key=lambda card: (
                    card[CARD_TYPE] not in ('campaign', 'nightmare'),
                    card[CARD_TYPE],
                    card[CARD_COST] or 0,
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
                elif card[CARD_TYPE] in ('attachment', 'player objective'):
                    attachment_cards.append(card)
                elif card[CARD_TYPE] == 'event':
                    event_cards.append(card)
                elif card[CARD_TYPE] == 'player side quest':
                    side_quest_cards.append(card)
                else:
                    mode_errors.append(
                        'Card "{}" with type "{}" can\'t be added to the deck'
                        .format(card[CARD_ORIGINAL_NAME],
                                card[CARD_TYPE].title()))

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

            res = ET.tostring(root, encoding='utf-8').decode('utf-8')
            res = res.replace('<notes />', '<notes><![CDATA[]]></notes>')
            files.append((filename, res))

            if mode == EASY_PREFIX:
                mode_errors = ['{} in easy mode'.format(e)
                               for e in mode_errors]

            errors.extend(mode_errors)

    return (files, errors)


def generate_octgn_o8d(conf, set_id, set_name):
    """ Generate .o8d files for OCTGN and DragnCards.
    """
    logging.info('[%s] Generating .o8d files for OCTGN and DragnCards...',
                 set_name)
    timestamp = time.time()

    files = []
    rows = [row for row in DATA
            if row[CARD_SET] == set_id
            and row[CARD_TYPE] in CARD_TYPES_DECK_RULES
            and row[CARD_DECK_RULES]
            and (not conf['selected_only'] or row[CARD_ID] in SELECTED_CARDS)]
    for row in rows:
        files.extend(_generate_octgn_o8d_quest(row)[0])

    output_path = os.path.join(OUTPUT_OCTGN_DECKS_PATH,
                               escape_filename(set_name))
    clear_folder(output_path)
    if files:
        create_folder(output_path)

    for filename, res in files:
        with open(
                os.path.join(output_path, filename),
                'w', encoding='utf-8') as obj:
            obj.write(
                '<?xml version="1.0" encoding="utf-8" standalone="yes"?>')
            obj.write('\n')
            obj.write(res)

    # not needed at the moment
    # _generate_octgn_o8d_player(conf, set_id, set_name)

    logging.info('[%s] ...Generating .o8d files for OCTGN and DragnCards '
                 '(%ss)', set_name, round(time.time() - timestamp, 3))


def _needed_for_ringsdb(card):
    """ Check whether a card is needed for RingsDB or not.
    """
    return ((card.get(CARD_TYPE) in CARD_TYPES_PLAYER or
             card.get(CARD_SPHERE) in ('Boon', 'Burden')) and
            'Promo' not in extract_flags(card.get(CARD_FLAGS)))


def _needed_for_frenchdb(card):
    """ Check whether a card is needed for the French database or not.
    """
    return (card[CARD_TYPE] not in
            ('Full Art Landscape', 'Full Art Portrait', 'Presentation',
             'Rules') and
            'Promo' not in extract_flags(card[CARD_FLAGS]))


def _needed_for_frenchdb_images(card):
    """ Check whether a card is needed for the French database images or not.
    """
    return (card[CARD_TYPE] not in
            ('Full Art Landscape', 'Full Art Portrait', 'Presentation') and
            not (card[CARD_TYPE] == 'Rules' and
                 card[CARD_SPHERE] == 'Back') and
            'Promo' not in extract_flags(card[CARD_FLAGS]))


def _needed_for_spanishdb(card):
    """ Check whether a card is needed for the Spanish database or not.
    """
    return (card[CARD_TYPE] not in
            ('Full Art Landscape', 'Full Art Portrait', 'Presentation') and
            not (card[CARD_TYPE] == 'Rules' and
                 card[CARD_SPHERE] == 'Back') and
            'Promo' not in extract_flags(card[CARD_FLAGS]))


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
    card_number = _to_str(handle_int(row[CARD_NUMBER])).zfill(3)
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
            if (row[CARD_ID] is None
                    or row[CARD_SET] != set_id
                    or not _needed_for_ringsdb(row)
                    or (conf['selected_only']
                        and row[CARD_ID] not in SELECTED_CARDS)):
                continue

            if row[CARD_TYPE] in CARD_TYPES_PLAYER_DECK:
                limit = re.search(r'limit .*([0-9]+) per deck',
                                  row[CARD_TEXT] or '',
                                  re.I)
                if limit:
                    limit = int(limit.groups()[0])
            else:
                limit = None

            if row[CARD_TYPE] == 'Hero':
                cost = None
                threat = handle_int(row[CARD_COST])
            else:
                cost = handle_int(row[CARD_COST])
                threat = None

            if row[CARD_SPHERE] == 'Burden':
                willpower = handle_int(row[CARD_THREAT])
            else:
                willpower = handle_int(row[CARD_WILLPOWER])

            if (row[CARD_TYPE] in ('Contract', 'Player Objective',
                                   'Treasure') or
                    row[CARD_SPHERE] in ('Boon', 'Burden')):
                sphere = 'Neutral'
            else:
                sphere = row[CARD_SPHERE]

            if row[CARD_TYPE] in ('Contract', 'Player Objective'):
                card_type = 'Other'
            elif (row[CARD_TYPE] == 'Treasure' or
                  row[CARD_SPHERE] in ('Boon', 'Burden')):
                card_type = 'Campaign'
            else:
                card_type = row[CARD_TYPE]

            quantity = (int(row[CARD_QUANTITY])
                        if is_int(row[CARD_QUANTITY]) else 1)

            text = _update_card_text('{}\n\n{}'.format(
                row[CARD_KEYWORDS] or '',
                row[CARD_TEXT] or '')).strip()

            if (row[BACK_PREFIX + CARD_NAME] is not None and
                    row[BACK_PREFIX + CARD_TEXT] is not None):
                text_back = _update_card_text('{}\n\n{}'.format(
                    row[BACK_PREFIX + CARD_KEYWORDS] or '',
                    row[BACK_PREFIX + CARD_TEXT])).strip()
                text = '<b>Side A</b>\n{}\n<b>Side B</b>\n{}'.format(
                    text, text_back)

            flavor = _update_card_text(row[CARD_FLAVOUR] or '',
                                       skip_rules=True, fix_linebreaks=False)
            if (row[BACK_PREFIX + CARD_NAME] is not None and
                    row[BACK_PREFIX + CARD_FLAVOUR] is not None):
                flavor_back = _update_card_text(
                    row[BACK_PREFIX + CARD_FLAVOUR], skip_rules=True,
                    fix_linebreaks=False)
                flavor = '{}\n{}'.format(flavor, flavor_back)

            position = (int(row[CARD_NUMBER])
                        if is_positive_or_zero_int(row[CARD_NUMBER]) else 0)
            position = (row[CARD_PRINTED_NUMBER]
                        if (row[CARD_PRINTED_NUMBER] is not None and
                            is_positive_or_zero_int(row[CARD_PRINTED_NUMBER]))
                        else position)

            csv_row = {
                'pack': set_name,
                'type': card_type,
                'sphere': sphere,
                'position': position,
                'code': _ringsdb_code(row),
                'name': row[CARD_NAME].replace('’', "'"),
                'traits': _update_card_text(row[CARD_TRAITS] or '',
                                            skip_rules=True,
                                            fix_linebreaks=False),
                'text': text,
                'flavor': flavor,
                'isUnique': row[CARD_UNIQUE] and int(row[CARD_UNIQUE]),
                'cost': cost,
                'threat': threat,
                'willpower': willpower,
                'attack': handle_int(row[CARD_ATTACK]),
                'defense': handle_int(row[CARD_DEFENSE]),
                'health': handle_int(row[CARD_HEALTH]),
                'victory': handle_int(row[CARD_VICTORY]),
                'quest': handle_int(row[CARD_QUEST]),
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
                new_row['pack'] = 'ALeP - Messenger of the King Allies'
                new_row['type'] = 'Hero'
                new_row['code'] = '99{}'.format(new_row['code'])
                new_row['name'] = '(MotK) {}'.format(new_row['name'])
                new_row['cost'] = None
                willpower = (new_row['willpower']
                             if is_int(new_row['willpower']) else 0)
                attack = (new_row['attack']
                          if is_int(new_row['attack']) else 0)
                defense = (new_row['defense']
                           if is_int(new_row['defense']) else 0)
                health = (new_row['health']
                          if is_int(new_row['health']) else 0)
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
        output_path, '{}.json'.format(set_id))

    try:
        with open(DRAGNCARDS_TIMESTAMPS_JSON_PATH, 'r',
                  encoding='utf-8') as fobj:
            dragncards_timestamps = json.load(fobj)
    except Exception:
        dragncards_timestamps = {}

    try:
        with open(DOWNLOAD_TIME_PATH, 'r', encoding='utf-8') as fobj:
            download_time = fobj.read()
    except Exception:
        download_time = None

    xml_path = os.path.join(SET_EONS_PATH, '{}.English.xml'.format(set_id))
    if download_time and os.path.exists(xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for card in root[0]:
            if (card.attrib.get('id') and
                    not card.attrib.get('skip') and
                    not card.attrib.get('skipDragncards') and
                    not card.attrib.get('noDragncards')):
                dragncards_timestamps[card.attrib['id']] = download_time

    json_data = {}
    for row in DATA:
        if (row[CARD_ID] is None
                or row[CARD_SET] != set_id
                or not _needed_for_dragncards(row)
                or (conf['selected_only']
                    and row[CARD_ID] not in SELECTED_CARDS)):
            continue

        if row[CARD_TYPE] == 'Encounter Side Quest':
            card_type = 'Side Quest'
        else:
            card_type = row[CARD_TYPE]

        if row[CARD_TYPE] in ('Player Objective', 'Treasure'):
            sphere = 'Neutral'
        elif row[CARD_SPHERE] in ('Cave', 'NoProgress', 'NoStat', 'Region',
                                  'Setup', 'SmallTextArea', 'Upgraded'):
            sphere = ''
        else:
            sphere = row[CARD_SPHERE]

        if row[CARD_TYPE] == 'Rules' and row[CARD_VICTORY]:
            victory = 'Page {}'.format(row[CARD_VICTORY])
        else:
            victory = row[CARD_VICTORY]

        side_a = {
            'name': unidecode.unidecode(_to_str(row[CARD_NAME])),
            'printname': _to_str(row[CARD_NAME]),
            'unique': _to_str(handle_int(row[CARD_UNIQUE])),
            'type': _to_str(card_type),
            'sphere': _to_str(sphere),
            'traits': _update_dragncards_card_text(_to_str(row[CARD_TRAITS])),
            'keywords': _update_dragncards_card_text(_to_str(
                row[CARD_KEYWORDS])),
            'cost': _to_str(handle_int(row[CARD_COST])),
            'engagementcost': _to_str(handle_int(row[CARD_ENGAGEMENT])),
            'threat': _to_str(handle_int(row[CARD_THREAT])),
            'willpower': _to_str(handle_int(row[CARD_WILLPOWER])),
            'attack': _to_str(handle_int(row[CARD_ATTACK])),
            'defense': _to_str(handle_int(row[CARD_DEFENSE])),
            'hitpoints': _to_str(handle_int(row[CARD_HEALTH])),
            'questpoints': _to_str(handle_int(row[CARD_QUEST])),
            'victorypoints': _to_str(handle_int(victory)),
            'text': _update_dragncards_card_text(_to_str(row[CARD_TEXT])),
            'shadow': _update_dragncards_card_text(_to_str(row[CARD_SHADOW]))
        }

        if row[BACK_PREFIX + CARD_NAME]:
            if row[BACK_PREFIX + CARD_TYPE] == 'Encounter Side Quest':
                card_type = 'Side Quest'
            else:
                card_type = row[BACK_PREFIX + CARD_TYPE]

            if row[BACK_PREFIX + CARD_TYPE] in ('Player Objective',
                                                'Treasure'):
                sphere = 'Neutral'
            elif row[BACK_PREFIX + CARD_SPHERE] in (
                    'Cave', 'NoProgress', 'NoStat', 'Region', 'Setup',
                    'SmallTextArea', 'Upgraded'):
                sphere = ''
            else:
                sphere = row[BACK_PREFIX + CARD_SPHERE]

            if (row[BACK_PREFIX + CARD_TYPE] == 'Rules' and
                    row[BACK_PREFIX + CARD_VICTORY]):
                victory = 'Page {}'.format(row[BACK_PREFIX + CARD_VICTORY])
            else:
                victory = row[BACK_PREFIX + CARD_VICTORY]

            side_b = {
                'name': unidecode.unidecode(_to_str(
                    row[BACK_PREFIX + CARD_NAME])),
                'printname': _to_str(row[BACK_PREFIX + CARD_NAME]),
                'unique': _to_str(handle_int(row[BACK_PREFIX + CARD_UNIQUE])),
                'type': _to_str(card_type),
                'sphere': _to_str(sphere),
                'traits': _update_dragncards_card_text(
                    _to_str(row[BACK_PREFIX + CARD_TRAITS])),
                'keywords': _update_dragncards_card_text(_to_str(
                    row[BACK_PREFIX + CARD_KEYWORDS])),
                'cost': _to_str(handle_int(row[BACK_PREFIX + CARD_COST])),
                'engagementcost': _to_str(
                    handle_int(row[BACK_PREFIX + CARD_ENGAGEMENT])),
                'threat': _to_str(handle_int(row[BACK_PREFIX + CARD_THREAT])),
                'willpower': _to_str(
                    handle_int(row[BACK_PREFIX + CARD_WILLPOWER])),
                'attack': _to_str(handle_int(row[BACK_PREFIX + CARD_ATTACK])),
                'defense': _to_str(
                    handle_int(row[BACK_PREFIX + CARD_DEFENSE])),
                'hitpoints': _to_str(
                    handle_int(row[BACK_PREFIX + CARD_HEALTH])),
                'questpoints': _to_str(
                    handle_int(row[BACK_PREFIX + CARD_QUEST])),
                'victorypoints': _to_str(handle_int(victory)),
                'text': _update_dragncards_card_text(_to_str(
                    row[BACK_PREFIX + CARD_TEXT])),
                'shadow': _update_dragncards_card_text(_to_str(
                    row[BACK_PREFIX + CARD_SHADOW]))
            }
        else:
            if ((row[CARD_TYPE] in CARD_TYPES_PLAYER and
                 'Encounter' not in extract_keywords(row[CARD_KEYWORDS]) and
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
            'cardnumber': _to_str(handle_int(row[CARD_NUMBER])),
            'cardquantity': _to_str(handle_int(row[CARD_QUANTITY])),
            'cardencounterset': _to_str(row[CARD_ENCOUNTER_SET]),
            'playtest': 1
        }
        if dragncards_timestamps.get(row[CARD_ID]):
            card_data['modifiedtimeutc'] = dragncards_timestamps[row[CARD_ID]]

        json_data[row[CARD_ID]] = card_data

    with open(output_path, 'w', encoding='utf-8') as obj:
        res = json.dumps(json_data, ensure_ascii=True, indent=4)
        obj.write(res)

    for card in json_data.values():
        if 'playtest' in card:
            del card['playtest']

        if 'modifiedtimeutc' in card:
            del card['modifiedtimeutc']

    output_path = '{}.release'.format(output_path)
    with open(output_path, 'w', encoding='utf-8') as obj:
        res = json.dumps(json_data, ensure_ascii=True, indent=4)
        obj.write(res)

    with open(DRAGNCARDS_TIMESTAMPS_JSON_PATH, 'w', encoding='utf-8') as fobj:
        json.dump(dragncards_timestamps, fobj)

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
        if (row[BACK_PREFIX + CARD_NAME] is not None and
                row[CARD_TYPE] not in CARD_TYPES_DOUBLESIDE_OPTIONAL):
            new_row = row.copy()
            new_row[CARD_NAME] = new_row[BACK_PREFIX + CARD_NAME]
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
                translated_row[CARD_NAME] = translated_row.get(
                    BACK_PREFIX + CARD_NAME, '')
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
            quest_stage = handle_int(row[CARD_COST])
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

        if card_type in ('Contract', 'Player Objective', 'Treasure'):
            sphere = 'Neutral'
        elif card_type in ('Campaign', 'Presentation', 'Rules'):
            sphere = 'None'
        elif row[CARD_SPHERE] in ('Cave', 'Nightmare', 'NoProgress', 'NoStat',
                                  'Region', 'SmallTextArea', 'Upgraded'):
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
        elif (row[BACK_PREFIX + CARD_NAME] is not None and
              card_type not in CARD_TYPES_DOUBLESIDE_OPTIONAL):
            card_side = 'A'
        else:
            card_side = None

        if (translated_row.get(BACK_PREFIX + CARD_NAME) is not None and
                translated_row[BACK_PREFIX + CARD_NAME] !=
                translated_row.get(CARD_NAME, '') and
                card_type in CARD_TYPES_DOUBLESIDE_OPTIONAL):
            opposite_title = translated_row[BACK_PREFIX + CARD_NAME]
        else:
            opposite_title = None

        keywords = extract_keywords(translated_row.get(CARD_KEYWORDS))
        keywords_original = extract_keywords(row.get(CARD_KEYWORDS))

        if (row.get(CARD_TEXT) and
                (' Restricted.' in row[CARD_TEXT] or
                 '\nRestricted.' in row[CARD_TEXT])):
            keywords_original.append('Restricted')
            keywords.append(RESTRICTED_TRANSLATION[lang])

        traits = extract_traits(translated_row.get(CARD_TRAITS))
        traits_original = extract_traits(row.get(CARD_TRAITS))

        code = _ringsdb_code(row)
        position = (int(row[CARD_NUMBER])
                    if is_positive_or_zero_int(row[CARD_NUMBER]) else 0)
        position = (row[CARD_PRINTED_NUMBER]
                    if (row[CARD_PRINTED_NUMBER] is not None and
                        is_positive_or_zero_int(row[CARD_PRINTED_NUMBER]))
                    else position)

        encounter_set = ((row[CARD_ENCOUNTER_SET] or '')
                         if card_type in CARD_TYPES_ENCOUNTER_SET
                         else row[CARD_ENCOUNTER_SET])
        subtitle = ((translated_row.get(CARD_ADVENTURE) or '')
                    if card_type in CARD_TYPES_SUBTITLE
                    else translated_row.get(CARD_ADVENTURE))

        if card_type in ('Presentation', 'Rules'):
            type_name = 'Setup'
        elif card_type == 'Nightmare':
            type_name = 'Nightmare Setup'
        elif card_type in ('Full Landscape', 'Full Art Portrait'):
            type_name = 'None'
        elif (card_type == 'Encounter Side Quest' and
              row[CARD_SPHERE] == 'Cave'):
            type_name = 'Cave'
        elif (card_type == 'Encounter Side Quest' and
              row[CARD_SPHERE] == 'Region'):
            type_name = 'Region'
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

        tokens = []
        if row[CARD_SPECIAL_ICON] is not None:
            tokens.append(row[CARD_SPECIAL_ICON])

        if victory_points is not None and not is_int(victory_points):
            tokens.append(victory_points)
            victory_points = None

        if not tokens:
            tokens = None

        additional_encounter_sets = [
            s.strip() for s in str(row[CARD_ADDITIONAL_ENCOUNTER_SETS] or ''
                                   ).split(';')
            if s.strip()] or None

        fix_linebreaks = card_type not in ('Presentation', 'Rules')

        text = _update_card_text('{}\n\n{}'.format(
            translated_row.get(CARD_KEYWORDS) or '',
            translated_row.get(CARD_TEXT) or ''
            ), fix_linebreaks=fix_linebreaks).replace('\n', '\r\n').strip()
        if (card_type in ('Presentation', 'Rules') and
                translated_row.get(CARD_VICTORY) is not None):
            text = '{}\r\n\r\nPage {}'.format(text,
                                              translated_row[CARD_VICTORY])

        if (translated_row.get(BACK_PREFIX + CARD_NAME) is not None and
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
                    translated_row.get(BACK_PREFIX + CARD_VICTORY)
                    is not None):
                text_back = '{}\r\n\r\nPage {}'.format(
                    text_back, translated_row[BACK_PREFIX + CARD_VICTORY])
            text = '<b>Side A</b> {} <b>Side B</b> {}'.format(text, text_back)

        flavor = (_update_card_text(translated_row.get(CARD_FLAVOUR) or '',
                                    skip_rules=True,
                                    fix_linebreaks=False
                                    ).replace('\n', '\r\n').strip())
        if (translated_row.get(BACK_PREFIX + CARD_NAME) is not None and
                translated_row.get(BACK_PREFIX + CARD_FLAVOUR) is not None and
                card_type in CARD_TYPES_DOUBLESIDE_OPTIONAL):
            flavor_back = _update_card_text(
                translated_row[BACK_PREFIX + CARD_FLAVOUR],
                skip_rules=True,
                fix_linebreaks=False
                ).replace('\n', '\r\n').strip()
            flavor = 'Side A: {} Side B: {}'.format(flavor, flavor_back)

        quantity = (int(row[CARD_QUANTITY])
                    if is_int(row[CARD_QUANTITY]) else 1)

        json_row = {
            'code': code,
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
            'easy_mode_quantity': handle_int(row[CARD_EASY_MODE]),
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
            'tokens': tokens,
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

            if row[CARD_TYPE] in ('Contract', 'Player Objective'):
                sphere = 'Neutral'
            elif row[CARD_SPHERE] in ('Boon', 'Upgraded'):
                sphere = None
            else:
                sphere = row[CARD_SPHERE]

            if row[CARD_TYPE] == 'Hero':
                cost = None
                threat = _update_french_non_int(handle_int(row[CARD_COST]))
            else:
                cost = _update_french_non_int(handle_int(row[CARD_COST]))
                threat = None

            text = _update_french_card_text('{}\n\n{}'.format(
                french_row.get(CARD_KEYWORDS) or '',
                french_row.get(CARD_TEXT) or '')).strip()

            if ((row[CARD_TYPE] in CARD_TYPES_DOUBLESIDE_OPTIONAL or
                 row[BACK_PREFIX + CARD_NAME] is not None) and
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
                            if is_int(row[CARD_QUANTITY])
                            else 1)

            easy_mode = (int(row[CARD_EASY_MODE])
                         if is_int(row[CARD_EASY_MODE])
                         else 0)

            csv_row = {
                'id_extension': row[CARD_SET_NAME],
                'numero_identification': int(row[CARD_NUMBER])
                                         if is_int(row[CARD_NUMBER])
                                         else 0,
                'id_type_carte': CARD_TYPE_FRENCH_IDS.get(row[CARD_TYPE], 0),
                'id_sous_type_carte': CARD_SUBTYPE_FRENCH_IDS.get(
                    row[CARD_SPHERE]),
                'id_sphere_influence': CARD_SPHERE_FRENCH_IDS.get(sphere, 0),
                'id_octgn': row[CARD_ID],
                'titre': french_row.get(CARD_NAME) or '',
                'cout': cost,
                'menace': threat,
                'volonte': _update_french_non_int(
                    handle_int(row[CARD_WILLPOWER])),
                'attaque': _update_french_non_int(
                    handle_int(row[CARD_ATTACK])),
                'defense': _update_french_non_int(
                    handle_int(row[CARD_DEFENSE])),
                'point_vie': _update_french_non_int(
                    handle_int(row[CARD_HEALTH])),
                'trait': _update_french_card_text(
                    french_row.get(CARD_TRAITS) or ''),
                'texte': text,
                'indic_unique': int(row[CARD_UNIQUE] or 0),
                'indic_recto_verso': row[BACK_PREFIX + CARD_NAME] is not None
                                     and 1 or 0,
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
                 or row[BACK_PREFIX + CARD_NAME] is not None) and
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
                        if is_int(row[CARD_QUANTITY])
                        else 1)
            easy_mode = (int(row[CARD_EASY_MODE])
                         if is_int(row[CARD_EASY_MODE])
                         else 0)

            csv_row = {
                'id_extension': row[CARD_SET_NAME],
                'numero_identification': int(row[CARD_NUMBER])
                                         if is_int(row[CARD_NUMBER])
                                         else 0,
                'id_type_carte': CARD_TYPE_FRENCH_IDS.get(card_type, 0),
                'id_sous_type_carte': CARD_SUBTYPE_FRENCH_IDS.get(
                    row[CARD_SPHERE]),
                'id_set_rencontre': row[CARD_ENCOUNTER_SET] or '',
                'titre': french_row.get(CARD_NAME) or '',
                'cout_engagement': _update_french_non_int(
                    handle_int(row[CARD_ENGAGEMENT])),
                'menace': _update_french_non_int(
                    handle_int(row[CARD_THREAT])),
                'attaque': _update_french_non_int(
                    handle_int(row[CARD_ATTACK])),
                'defense': _update_french_non_int(
                    handle_int(row[CARD_DEFENSE])),
                'point_quete': _update_french_non_int(
                    handle_int(row[CARD_QUEST])),
                'point_vie': _update_french_non_int(
                    handle_int(row[CARD_HEALTH])),
                'trait': _update_french_card_text(
                    french_row.get(CARD_TRAITS) or ''),
                'texte': text,
                'effet_ombre': shadow,
                'titre_quete': french_row.get(CARD_ADVENTURE),
                'indic_unique': int(row[CARD_UNIQUE] or 0),
                'indic_recto_verso': row[BACK_PREFIX + CARD_NAME] is not None
                                     and 1 or 0,
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

            name = french_row.get(CARD_NAME) or ''
            if (french_row.get(BACK_PREFIX + CARD_NAME) and
                    french_row[BACK_PREFIX + CARD_NAME] != name):
                name = '{} / {}'.format(name,
                                        french_row[BACK_PREFIX + CARD_NAME])

            text = _update_french_card_text('{}\n\n{}'.format(
                french_row.get(CARD_KEYWORDS) or '',
                french_row.get(CARD_TEXT) or '')).strip()

            text_back = _update_french_card_text('{}\n\n{}'.format(
                french_row.get(BACK_PREFIX + CARD_KEYWORDS) or '',
                french_row.get(BACK_PREFIX + CARD_TEXT) or '')).strip()

            quantity = (int(row[CARD_QUANTITY])
                        if is_int(row[CARD_QUANTITY])
                        else 1)

            csv_row = {
                'id_extension': row[CARD_SET_NAME],
                'numero_identification': int(row[CARD_NUMBER])
                                         if is_int(row[CARD_NUMBER])
                                         else 0,
                'id_set_rencontre': row[CARD_ENCOUNTER_SET] or '',
                'titre': name,
                'sequence': _to_str(handle_int(row[CARD_COST])),
                'texteA': text,
                'texteB': text_back,
                'point_quete': _update_french_non_int(
                    handle_int(row[BACK_PREFIX + CARD_QUEST])),
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
        if (row[BACK_PREFIX + CARD_NAME] is not None and
                row[CARD_TYPE] not in CARD_TYPES_DOUBLESIDE_OPTIONAL):
            new_row = row.copy()
            new_row[CARD_NAME] = new_row[BACK_PREFIX + CARD_NAME]
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
                spanish_row[CARD_NAME] = spanish_row.get(
                    BACK_PREFIX + CARD_NAME, '')
                for key in spanish_row.keys():
                    if key.startswith(BACK_PREFIX):
                        spanish_row[key.replace(BACK_PREFIX, '')] = (
                            spanish_row[key])

            name = spanish_row.get(CARD_NAME)
            if (row[CARD_TYPE] in CARD_TYPES_DOUBLESIDE_OPTIONAL and
                    spanish_row.get(BACK_PREFIX + CARD_NAME) and
                    spanish_row[BACK_PREFIX + CARD_NAME] != name):
                name = '{} / {}'.format(name,
                                        spanish_row[BACK_PREFIX + CARD_NAME])

            quantity = (int(row[CARD_QUANTITY])
                        if is_int(row[CARD_QUANTITY])
                        else 1)
            easy_mode = (int(row[CARD_EASY_MODE])
                         if is_int(row[CARD_EASY_MODE])
                         else 0)
            if row[CARD_TYPE] == 'Quest':
                quest_points = handle_int(row[BACK_PREFIX + CARD_QUEST])
                engagement = handle_int(row[CARD_COST])
                threat = '{}-{}'.format(
                    row[CARD_ENGAGEMENT] or '',
                    row[BACK_PREFIX + CARD_ENGAGEMENT] or '')
            else:
                quest_points = handle_int(row[CARD_QUEST])
                engagement = handle_int(row[CARD_ENGAGEMENT])
                threat = handle_int(row[CARD_THREAT])

            if row[CARD_TYPE] in CARD_TYPES_DOUBLESIDE_OPTIONAL:
                victory_points = (
                    handle_int(spanish_row.get(BACK_PREFIX + CARD_VICTORY))
                    if spanish_row.get(BACK_PREFIX + CARD_VICTORY) is not None
                    else handle_int(spanish_row.get(CARD_VICTORY))
                    )
            else:
                victory_points = handle_int(spanish_row.get(CARD_VICTORY))

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
                'position': handle_int(row[CARD_NUMBER]),
                'code': _spanishdb_code(row),
                'nombre': name,
                'nombreb': row[CARD_NAME],
                'quantity': quantity,
                'easy_mode': quantity - easy_mode,
                'tipo': SPANISH.get(row[CARD_TYPE]),
                'enfrentamiento': engagement,
                'amenaza': threat,
                'attack': handle_int(row[CARD_ATTACK]),
                'defense': handle_int(row[CARD_DEFENSE]),
                'health': handle_int(row[CARD_HEALTH]),
                'mision': quest_points,
                'victory': victory_points,
                'traits': _update_card_text(
                    spanish_row.get(CARD_TRAITS) or ''),
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
                spanish_row[CARD_NAME] = spanish_row.get(
                    BACK_PREFIX + CARD_NAME, '')
                for key in spanish_row.keys():
                    if key.startswith(BACK_PREFIX):
                        spanish_row[key.replace(BACK_PREFIX, '')] = (
                            spanish_row[key])

            if row[CARD_TYPE] in ('Contract', 'Player Objective', 'Treasure'):
                sphere = 'Neutral'
            else:
                sphere = row[CARD_SPHERE]

            if row[CARD_TYPE] == 'Hero':
                cost = None
                threat = handle_int(row[CARD_COST])
            else:
                cost = handle_int(row[CARD_COST])
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

            flavor = _update_card_text(spanish_row.get(CARD_FLAVOUR) or '',
                                       lang='Spanish',
                                       skip_rules=True,
                                       fix_linebreaks=False).strip()
            if flavor:
                flavor = '<p>{}</p>'.format(flavor.replace('\n', '</p><p>'))

            if (row[CARD_TYPE] in CARD_TYPES_DOUBLESIDE_OPTIONAL and
                    spanish_row.get(BACK_PREFIX + CARD_FLAVOUR)):
                flavor_back = _update_card_text(
                    spanish_row[BACK_PREFIX + CARD_FLAVOUR], lang='Spanish',
                    skip_rules=True, fix_linebreaks=False).strip()
                if flavor_back:
                    flavor_back = '<p>{}</p>'.format(
                        flavor_back.replace('\n', '</p><p>'))

                flavor = (
                    '<p><b>Lado A.</b></p>\n{}\n<p><b>Lado B.</b></p>\n{}'
                    .format(flavor, flavor_back))

            if row[CARD_TYPE] == 'Rules':
                victory_points = None
            else:
                victory_points = handle_int(spanish_row.get(CARD_VICTORY))

            quantity = (int(row[CARD_QUANTITY])
                        if is_int(row[CARD_QUANTITY])
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
                'position': handle_int(row[CARD_NUMBER]),
                'code': _spanishdb_code(row),
                'name': spanish_row.get(CARD_NAME),
                'traits': _update_card_text(
                    spanish_row.get(CARD_TRAITS) or ''),
                'text': text,
                'flavor': flavor,
                'is_unique': int(row[CARD_UNIQUE] or 0),
                'cost': cost,
                'threat': threat,
                'willpower': handle_int(row[CARD_WILLPOWER]),
                'attack': handle_int(row[CARD_ATTACK]),
                'defense': handle_int(row[CARD_DEFENSE]),
                'health': handle_int(row[CARD_HEALTH]),
                'victory': victory_points,
                'quest': handle_int(row[CARD_QUEST]),
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
    """ Get an xml property value for the given column name.
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
    """ Append property elements to the xml.
    """
    parent.text = '\n' + tab + '  '
    for i, (name, value) in enumerate(properties):
        if not name:
            continue

        prop = ET.SubElement(parent, 'property')
        prop.set('name', name)
        prop.set('value', _to_str(handle_int(value)))

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
            row_copy[BACK_PREFIX + CARD_NAME] = (
                TRANSLATIONS[lang][row[CARD_ID]][BACK_PREFIX + CARD_NAME])

        res.append(row_copy)

    return res


def generate_xml(conf, set_id, set_name, lang):  # pylint: disable=R0912,R0914,R0915
    """ Generate the xml file.
    """
    logging.info('[%s, %s] Generating the xml file...', set_name, lang)
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
        if not _needed_for_dragncards(row):
            card.set('noDragncards', '1')

        dragncards_values = []
        dragncards_values.append(str(row[CARD_NAME] or ''))
        dragncards_properties = {CARD_UNIQUE, CARD_TYPE, CARD_SPHERE,
                                 CARD_TRAITS, CARD_KEYWORDS, CARD_COST,
                                 CARD_ENGAGEMENT, CARD_THREAT, CARD_WILLPOWER,
                                 CARD_ATTACK, CARD_DEFENSE, CARD_HEALTH,
                                 CARD_QUEST, CARD_VICTORY, CARD_SPECIAL_ICON,
                                 CARD_TEXT, CARD_SHADOW}

        card_type = row[CARD_TYPE]
        properties = []
        for name in (CARD_NUMBER, CARD_QUANTITY, CARD_ENCOUNTER_SET,
                     CARD_UNIQUE, CARD_TYPE, CARD_SPHERE, CARD_TRAITS,
                     CARD_KEYWORDS, CARD_COST, CARD_ENGAGEMENT, CARD_THREAT,
                     CARD_WILLPOWER, CARD_ATTACK, CARD_DEFENSE, CARD_HEALTH,
                     CARD_QUEST, CARD_VICTORY, CARD_SPECIAL_ICON, CARD_TEXT,
                     CARD_SHADOW, CARD_FLAVOUR, CARD_PRINTED_NUMBER,
                     CARD_ENCOUNTER_SET_NUMBER, CARD_ENCOUNTER_SET_ICON,
                     CARD_FLAGS, CARD_ARTIST, CARD_PANX, CARD_PANY, CARD_SCALE,
                     CARD_PORTRAIT_SHADOW, CARD_EASY_MODE,
                     CARD_ADDITIONAL_ENCOUNTER_SETS, CARD_ADVENTURE, CARD_ICON,
                     CARD_COPYRIGHT, CARD_BACK, CARD_VERSION):
            value = _get_xml_property_value(row, name, card_type)
            if value != '':
                properties.append((name, value))

            if name in dragncards_properties:
                dragncards_values.append(str(value))

        properties.append(('Set Name', set_name))
        properties.append(('Set Icon',
                           SETS[set_id][SET_COLLECTION_ICON] or ''))
        properties.append(('Set Copyright', SETS[set_id][SET_COPYRIGHT] or ''))

        side_b = (card_type != 'Presentation' and (
            card_type in CARD_TYPES_DOUBLESIDE_MANDATORY or
            row[BACK_PREFIX + CARD_NAME]))
        if properties:
            if side_b:
                properties.append(('', ''))

            _add_xml_properties(card, properties, '    ')

        if side_b:
            if (card_type in CARD_TYPES_DOUBLESIDE_MANDATORY
                    and not row[BACK_PREFIX + CARD_NAME]):
                alternate_name = row[CARD_NAME]
            else:
                alternate_name = row[BACK_PREFIX + CARD_NAME]

            alternate = ET.SubElement(card, 'alternate')
            alternate.set('name', alternate_name or '')
            alternate.set('type', 'B')
            alternate.tail = '\n    '

            dragncards_values.append(str(alternate_name or ''))

            properties = []
            for name in (CARD_UNIQUE, CARD_TYPE, CARD_SPHERE, CARD_TRAITS,
                         CARD_KEYWORDS, CARD_COST, CARD_ENGAGEMENT,
                         CARD_THREAT, CARD_WILLPOWER, CARD_ATTACK,
                         CARD_DEFENSE, CARD_HEALTH, CARD_QUEST, CARD_VICTORY,
                         CARD_SPECIAL_ICON, CARD_TEXT, CARD_SHADOW,
                         CARD_FLAVOUR, CARD_PRINTED_NUMBER,
                         CARD_ENCOUNTER_SET_NUMBER, CARD_ENCOUNTER_SET_ICON,
                         CARD_FLAGS, CARD_ARTIST, CARD_PANX, CARD_PANY,
                         CARD_SCALE, CARD_PORTRAIT_SHADOW):
                value = _get_xml_property_value(row, BACK_PREFIX + name,
                                                card_type)
                if value != '':
                    properties.append((name, value))

                if name in dragncards_properties:
                    dragncards_values.append(str(value))

            if properties:
                _add_xml_properties(alternate, properties, '      ')

        if i == len(chosen_data) - 1:
            card.tail = '\n  '
        else:
            card.tail = '\n    '

        dragncards_hash = hashlib.md5('|'.join(dragncards_values).encode()
                                      ).hexdigest()
        card.set('hashDragncards', dragncards_hash)

    output_path = os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id, lang))
    with open(output_path, 'w', encoding='utf-8') as obj:
        res = ET.tostring(root, encoding='utf-8').decode('utf-8')
        obj.write(res)

    logging.info('[%s, %s] ...Generating the xml file (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def _collect_artwork_images(conf, image_path):
    """ Collect filenames of artwork images.
    """
    if image_path in IMAGE_CACHE:
        return IMAGE_CACHE[image_path]

    images = {}
    if os.path.exists(image_path):
        sorted_filenames = []
        for _, _, filenames in os.walk(image_path):
            for filename in filenames:
                if (len(filename.split('.')) < 2 or
                        len(filename.split('_')) < 3):
                    continue

                if filename.split('.')[-1] in ('jpg', 'png'):
                    sorted_filenames.append((
                        filename,
                        int(os.path.getmtime(
                            os.path.join(image_path, filename)))))

            break

        sorted_filenames.sort(key=lambda f: (f[1], f[0]), reverse=True)
        sorted_filenames = [f[0] for f in sorted_filenames]

        for filename in sorted_filenames:
            image_id = '_'.join(filename.split('_')[:2])
            lang = filename.split('.')[-2]
            if lang in conf['all_languages']:
                image_id = '{}_{}'.format(image_id, lang)

            if image_id in images:
                logging.error('Duplicate image detected: %s, '
                              'ignoring', os.path.join(image_path, filename))
            else:
                images[image_id] = os.path.join(image_path, filename)

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
    """ Set required outputs.
    """
    if (conf['nobleed_300'].get(lang)
            or 'drivethrucards' in (conf['outputs'][lang] or [])
            or 'pdf' in (conf['outputs'][lang] or [])):
        root.set('png300Bleed', '1')

    if conf['nobleed_480'].get(lang):
        root.set('png480Bleed', '1')

    if ('makeplayingcards' in (conf['outputs'][lang] or [])
            or 'mbprint' in (conf['outputs'][lang] or [])
            or 'genericpng' in (conf['outputs'][lang] or [])
            or 'genericpng_pdf' in (conf['outputs'][lang] or [])):
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
    """ Update the xml file with additional data.
    """
    logging.info('[%s, %s] Updating the xml file with additional data...',
                 set_name, lang)
    timestamp = time.time()

    artwork_path = os.path.join(conf['artwork_path'], set_id)
    images = _collect_artwork_images(conf, artwork_path)
    images = {k:[v, False] for k, v in images.items()}
    custom_images = _collect_custom_images(
        os.path.join(artwork_path, IMAGES_CUSTOM_FOLDER))
    common_custom_images = _collect_custom_images(
        os.path.join(conf['artwork_path'], IMAGES_CUSTOM_FOLDER))
    custom_images = {**common_custom_images, **custom_images}
    icon_images = _collect_custom_images(os.path.join(conf['artwork_path'],
                                                      IMAGES_ICONS_FOLDER))
    xml_path = os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id, lang))

    tree = ET.parse(xml_path)
    root = tree.getroot()
    _set_outputs(conf, lang, root)
    encounter_sets = {}
    encounter_cards = {}

    external_data = {}
    external_path = os.path.join(RENDERER_GENERATED_IMAGES_PATH,
                                 'artists_{}.json'.format(set_id))
    if conf['renderer'] and os.path.exists(external_path):
        with open(external_path, 'r', encoding='utf-8') as fobj:
            external_data = json.load(fobj)

    for card in root[0]:
        card_type = _find_properties(card, 'Type')
        card_type = card_type and card_type[0].attrib['value']
        card_sphere = _find_properties(card, 'Sphere')
        card_sphere = card_sphere and card_sphere[0].attrib['value']
        encounter_set = _find_properties(card, 'Encounter Set')
        if encounter_set:
            encounter_set = encounter_set[0].attrib['value']

        properties = [p for p in card]  # pylint: disable=R1721
        if properties:
            properties[-1].tail = '{}  '.format(properties[-1].tail)

        if (card_type not in ('Campaign', 'Nightmare', 'Quest', 'Rules',
                              'Treasure')
                and card_sphere not in ('Boon', 'Burden') and encounter_set):
            encounter_cards[card.attrib['id']] = encounter_set
            prop = _get_property(card, 'Encounter Set Number Start')
            prop.set('value', str(encounter_sets.get(encounter_set, 0) + 1))
            prop.tail = '\n      '
            quantity = int(
                _find_properties(card, 'Quantity')[0].attrib['value'])
            encounter_sets[encounter_set] = (
                encounter_sets.get(encounter_set, 0) + quantity)

        image_id = '{}_{}'.format(card.attrib['id'], 'A')
        if image_id in images:
            filename = images[image_id][0]
            images[image_id][1] = True
            prop = _get_property(card, 'Artwork')
            prop.set('value', os.path.split(filename)[-1])
            prop.tail = '\n      '
            prop = _get_property(card, 'Artwork Size')
            prop.set('value', str(os.path.getsize(filename)))
            prop.tail = '\n      '
            prop = _get_property(card, 'Artwork Modified')
            prop.set('value', str(int(os.path.getmtime(filename))))
            prop.tail = '\n      '

            artist = _find_properties(card, 'Artist')
            if not artist and '_Artist_' in os.path.split(filename)[-1]:
                prop = _get_property(card, 'Artist')
                prop.set('value', '.'.join(
                    '_Artist_'.join(
                        os.path.split(filename)[-1].split('_Artist_')[1:]
                        ).split('.')[:-1]).replace('_', ' '))
                prop.tail = '\n      '
        elif card_type != 'Rules' and conf['validate_missing_images']:
            logging.error('No image detected for card %s (%s)',
                          card.attrib['id'], card.attrib['name'])

        artist = _find_properties(card, 'Artist')
        if not artist and card.attrib['id'] in external_data:
            prop = _get_property(card, 'Artist')
            prop.set('value', external_data[card.attrib['id']])
            prop.tail = '\n      '

        if card_type == 'Presentation':
            image_id = '{}_{}_{}'.format(card.attrib['id'], 'Top', lang)
            if image_id not in images:
                image_id = '{}_{}'.format(card.attrib['id'], 'Top')

            if image_id in images:
                filename = images[image_id][0]
                images[image_id][1] = True
                prop = _get_property(card, 'ArtworkTop')
                prop.set('value', os.path.split(filename)[-1])
                prop.tail = '\n      '
                prop = _get_property(card, 'ArtworkTop Size')
                prop.set('value', str(os.path.getsize(filename)))
                prop.tail = '\n      '
                prop = _get_property(card, 'ArtworkTop Modified')
                prop.set('value', str(int(os.path.getmtime(filename))))
                prop.tail = '\n      '
            elif conf['validate_missing_images']:
                logging.error('No top image detected for card %s (%s)',
                              card.attrib['id'], card.attrib['name'])

            image_id = '{}_{}_{}'.format(card.attrib['id'], 'Bottom', lang)
            if image_id not in images:
                image_id = '{}_{}'.format(card.attrib['id'], 'Bottom')

            if image_id in images:
                filename = images[image_id][0]
                images[image_id][1] = True
                prop = _get_property(card, 'ArtworkBottom')
                prop.set('value', os.path.split(filename)[-1])
                prop.tail = '\n      '
                prop = _get_property(card, 'ArtworkBottom Size')
                prop.set('value', str(os.path.getsize(filename)))
                prop.tail = '\n      '
                prop = _get_property(card, 'ArtworkBottom Modified')
                prop.set('value', str(int(os.path.getmtime(filename))))
                prop.tail = '\n      '
            elif conf['validate_missing_images']:
                logging.error('No bottom image detected for card %s (%s)',
                              card.attrib['id'], card.attrib['name'])

        alternate = [a for a in card if a.attrib.get('type') == 'B']
        if alternate:
            alternate = alternate[0]

        image_id = '{}_{}'.format(card.attrib['id'], 'B')
        if alternate:
            if image_id in images:
                filename = images[image_id][0]
                images[image_id][1] = True
                properties = [p for p in alternate]  # pylint: disable=R1721
                if properties:
                    properties[-1].tail = '{}  '.format(properties[-1].tail)

                prop = _get_property(alternate, 'Artwork')
                prop.set('value', os.path.split(filename)[-1])
                prop.tail = '\n        '
                prop = _get_property(alternate, 'Artwork Size')
                prop.set('value', str(os.path.getsize(filename)))
                prop.tail = '\n        '
                prop = _get_property(alternate, 'Artwork Modified')
                prop.set('value', str(int(os.path.getmtime(filename))))
                prop.tail = '\n        '

                artist = _find_properties(alternate, 'Artist')
                if not artist and '_Artist_' in os.path.split(filename)[-1]:
                    prop = _get_property(alternate, 'Artist')
                    prop.set('value', '.'.join(
                        '_Artist_'.join(
                            os.path.split(filename)[-1].split('_Artist_')[1:]
                            ).split('.')[:-1]).replace('_', ' '))
                    prop.tail = '\n        '

            artist = _find_properties(alternate, 'Artist')
            artist_id = '{}.B'.format(card.attrib['id'])
            if not artist and artist_id in external_data:
                prop = _get_property(alternate, 'Artist')
                prop.set('value', external_data[artist_id])
                prop.tail = '\n      '

            properties = [p for p in alternate]  # pylint: disable=R1721
            if properties:
                properties[-1].tail = re.sub(r'  $', '', properties[-1].tail)

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

        image_counter = 0
        for image in referred_custom_images:
            if image in custom_images:
                prop = _get_property(card,
                                     'Custom Image_{}'.format(image_counter))
                image_counter += 1
                prop.set('value', '{}|{}|{}'.format(
                    image,
                    os.path.getsize(custom_images[image]),
                    int(os.path.getmtime(custom_images[image]))))
                prop.tail = '\n      '

        if card_type in CARD_TYPES_NO_ICON:
            continue

        target_icon_images = []
        collection_icon = _find_properties(card, 'Collection Icon')
        if collection_icon:
            collection_icon = collection_icon[0].attrib['value']
            target_icon_images.append(collection_icon)
            target_icon_images.append('{}_stroke'.format(collection_icon))
        else:
            set_icon = root.attrib.get('icon')
            if set_icon:
                target_icon_images.append(set_icon)
                target_icon_images.append('{}_stroke'.format(set_icon))
            else:
                target_icon_images.append(set_name)
                target_icon_images.append('{}_stroke'.format(set_name))

        if encounter_set and card_sphere != 'Boon':
            target_icon_images.append(encounter_set)

        additional_sets = _find_properties(card, 'Additional Encounter Sets')
        if additional_sets:
            additional_sets = additional_sets[0].attrib['value']
            for additional_set in additional_sets.split(';'):
                if additional_set.strip():
                    target_icon_images.append(additional_set.strip())

        target_icon_images = [_escape_icon_filename('{}.png'.format(i))
                              for i in target_icon_images]
        image_counter = 0
        for image in target_icon_images:
            if image in icon_images:
                prop = _get_property(card, 'Icon_{}'.format(image_counter))
                image_counter += 1
                prop.set('value', '{}|{}|{}'.format(
                    image,
                    os.path.getsize(icon_images[image]),
                    int(os.path.getmtime(icon_images[image]))))
                prop.tail = '\n      '

    for filename, is_used in images.values():
        if is_used:
            continue

        parts = filename.split('_')
        if len(parts) == 3 and parts[2] != lang:
            continue

        logging.error('Unused image detected: %s', filename)

    for card in root[0]:
        if card.attrib['id'] in encounter_cards:
            prop = _get_property(card, 'Encounter Set Total')
            prop.set('value', str(
                encounter_sets[encounter_cards[card.attrib['id']]]))
            prop.tail = '\n      '

        properties = [p for p in card]  # pylint: disable=R1721
        if properties:
            properties[-1].tail = re.sub(r'  $', '', properties[-1].tail)

    if conf['selected_only']:
        cards = list(root[0])
        for card in cards:
            if card.attrib['id'] not in SELECTED_CARDS:
                root[0].remove(card)

    tree.write(xml_path)
    logging.info('[%s, %s] ...Updating the xml file with additional data '
                 '(%ss)', set_name, lang, round(time.time() - timestamp, 3))


def expire_dragncards_hashes():
    """ Expire Dragncards hashes requested by Discord bot.
    """
    logging.info('Expiring Dragncards hashes')
    timestamp = time.time()

    try:
        with open(EXPIRE_DRAGNCARDS_JSON_PATH, 'r',
                  encoding='utf-8') as fobj:
            expired_hashes = json.load(fobj)
    except Exception:
        expired_hashes = []

    if expired_hashes:
        try:
            with open(GENERATE_DRAGNCARDS_JSON_PATH, 'r',
                      encoding='utf-8') as fobj:
                dragncards_hashes = json.load(fobj)
        except Exception:
            pass
        else:
            for card_id in expired_hashes:
                if card_id in dragncards_hashes:
                    dragncards_hashes[card_id] = 'expired'

            if os.path.exists(GENERATE_DRAGNCARDS_JSON_PATH):
                shutil.copyfile(
                    GENERATE_DRAGNCARDS_JSON_PATH,
                    re.sub(r'\.json$', '.json.backup',
                           GENERATE_DRAGNCARDS_JSON_PATH))

            with open(GENERATE_DRAGNCARDS_JSON_PATH, 'w',
                      encoding='utf-8') as fobj:
                json.dump(dragncards_hashes, fobj)

        if os.path.exists(EXPIRE_DRAGNCARDS_JSON_PATH):
            os.remove(EXPIRE_DRAGNCARDS_JSON_PATH)

    logging.info(' ...Expiring Dragncards hashes (%ss)',
                 round(time.time() - timestamp, 3))


def calculate_hashes(set_id, set_name, lang):  # pylint: disable=R0912,R0914
    """ Update the xml file with hashes and skip flags.
    """
    logging.info('[%s, %s] Updating the xml file with hashes and skip '
                 'flags...', set_name, lang)
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

    try:
        with open(GENERATE_DRAGNCARDS_JSON_PATH, 'r',
                  encoding='utf-8') as fobj:
            old_dragncards_hashes = json.load(fobj)
    except Exception:
        old_dragncards_hashes = {}

    dragncards_changes = False
    for card in root[0]:
        if (old_dragncards_hashes.get(card.attrib['id']) ==
                card.attrib['hashDragncards']):
            card.set('skipDragncards', '1')
        elif not card.attrib.get('noDragncards'):
            dragncards_changes = True

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

            if row[CARD_CHANGED] or SETS[set_id].get(SET_CHANGED):
                changed_cards.add(row[CARD_ID])

        if changed_cards:
            old_file_hash = ''

        if old_file_hash == new_file_hash:
            root.set('skip', '1')

        for card in root[0]:
            if (old_hashes.get(card.attrib['id']) == card.attrib['hash'] and
                    card.attrib['id'] not in changed_cards and
                    old_dragncards_hashes.get(card.attrib['id']) != 'expired'):
                skip_ids.add(card.attrib['id'])
                card.set('skip', '1')

    tree.write(new_path)

    logging.info('[%s, %s] ...Updating the xml file with hashes and skip '
                 'flags (%ss)', set_name, lang,
                 round(time.time() - timestamp, 3))
    return (old_file_hash != new_file_hash, dragncards_changes)


def verify_images(conf):
    """ Verify images from Google Drive.
    """
    logging.info('Verifying image from Google Drive...')
    logging.info('')
    timestamp = time.time()

    if os.path.exists(conf['artwork_path']):
        for root, _, filenames in os.walk(conf['artwork_path']):
            if root == os.path.join(conf['artwork_path'], SCRATCH_FOLDER):
                continue

            for filename in filenames:
                if (filename.endswith(' (1).png') or
                        filename.endswith(' (1).jpg') or
                        filename.endswith(' (2).png') or
                        filename.endswith(' (2).jpg')):
                    logging.error('Google Drive sync issues with file %s',
                                  os.path.join(root, filename))

    logging.info('')
    logging.info('...Verifying images from Google Drive (%ss)',
                 round(time.time() - timestamp, 3))


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
                if (not filename.endswith('.jpg') and
                        not filename.endswith('.png')):
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
                if (not filename.endswith('.jpg') and
                        not filename.endswith('.png')):
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
    tree = ET.parse(os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id,
                                                                   lang)))
    root = tree.getroot()
    for card in root[0]:
        if card.attrib.get('skip') != '1':
            for prop in ('Artwork', 'ArtworkTop', 'ArtworkBottom'):
                filename = _find_properties(card, prop)
                if filename:
                    filename = filename[0].attrib['value']
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
                    input_path = os.path.join(artwork_path, filename)
                    output_path = os.path.join(IMAGES_RAW_PATH, filename)
                    if not os.path.exists(output_path):
                        shutil.copyfile(input_path, output_path)

    logging.info('[%s, %s] ...Copying raw image files into the project folder '
                 '(%ss)', set_name, lang, round(time.time() - timestamp, 3))


def copy_xml(set_id, set_name, lang):
    """ Copy the xml file into the project.
    """
    logging.info('[%s, %s] Copying the xml file into the project...',
                 set_name, lang)
    timestamp = time.time()

    shutil.copyfile(os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id,
                                                                   lang)),
                    os.path.join(XML_PATH, '{}.{}.xml'.format(set_id, lang)))
    logging.info('[%s, %s] ...Copying the xml file into the project (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


def generate_dragncards_proxies(sets):
    """ Generate DragnCards proxies.
    """
    logging.info('Generating DragnCards proxies...')
    timestamp = time.time()

    cmd = GENERATE_DRAGNCARDS_COMMAND.format(','.join(sets))
    res = _run_cmd(cmd)
    logging.info(res)

    if os.path.exists(GENERATE_DRAGNCARDS_LOG_PATH):
        with open(GENERATE_DRAGNCARDS_LOG_PATH, 'r', encoding='utf-8') as fobj:
            content = fobj.read()

        card_ids = {c.split('/')[-1].split('.')[0]
                    for c in content.split('\n') if c}
        cards = {}
        for set_id in sets:
            xml_path = os.path.join(SET_EONS_PATH,
                                    '{}.English.xml'.format(set_id))
            if not os.path.exists(xml_path):
                continue

            tree = ET.parse(xml_path)
            root = tree.getroot()
            for card in root[0]:
                if (card.attrib.get('id') in card_ids and
                        card.attrib.get('hashDragncards')):
                    cards[card.attrib['id']] = card.attrib['hashDragncards']
                    card_ids.remove(card.attrib['id'])

        if card_ids:
            logging.warning('No DragnCards hashes for the following '
                            'generated cards: %s', ', '.join(card_ids))

        if cards:
            try:
                with open(GENERATE_DRAGNCARDS_JSON_PATH, 'r',
                          encoding='utf-8') as fobj:
                    old_cards = json.load(fobj)
            except Exception:
                old_cards = {}

            if os.path.exists(GENERATE_DRAGNCARDS_JSON_PATH):
                shutil.copyfile(
                    GENERATE_DRAGNCARDS_JSON_PATH,
                    re.sub(r'\.json$', '.json.backup',
                           GENERATE_DRAGNCARDS_JSON_PATH))

            cards = {**old_cards, **cards}
            with open(GENERATE_DRAGNCARDS_JSON_PATH, 'w',
                      encoding='utf-8') as fobj:
                json.dump(cards, fobj)

    logging.info('...Generating DragnCards proxies (%ss)',
                 round(time.time() - timestamp, 3))


def create_project():
    """ Create a project archive.
    """
    logging.info('Creating a project archive...')
    timestamp = time.time()

    if os.path.exists(MAKECARDS_FINISHED_PATH):
        os.remove(MAKECARDS_FINISHED_PATH)

    with zipfile.ZipFile(SEPROJECT_PATH, 'w') as zip_obj:
        for root, _, filenames in os.walk(PROJECT_PATH):
            for filename in filenames:
                zip_obj.write(os.path.join(root, filename))

    logging.info('...Creating a project archive (%ss)',
                 round(time.time() - timestamp, 3))


def get_skip_info(set_id, lang):
    """ Get skip information for the set and individual cards.
    """
    path = os.path.join(SET_EONS_PATH, '{}.{}.xml'.format(set_id, lang))
    if not os.path.exists(path):
        return True, set()

    tree = ET.parse(path)
    root = tree.getroot()
    skip_set = root.attrib.get('skip') == '1'
    skip_ids = set()
    for card in root[0]:
        if card.attrib.get('skip') == '1':
            skip_ids.add(card.attrib['id'])

    return skip_set, skip_ids


def get_actual_sets():
    """ Get actual sets from the project.
    """
    res = set()
    with zipfile.ZipFile(SEPROJECT_PATH) as zip_obj:
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
    logging.info('Running the command: %s', cmd)
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, shell=True, check=True)
        return res
    except subprocess.CalledProcessError as exc:
        raise RuntimeError('Command "{}" returned error with code {}: {}'
                           .format(cmd, exc.returncode, exc.output)) from exc

def check_messages():
    """ Check messages in the archive and log them.
    """
    logging.info('Checking messages in the archive...')
    timestamp = time.time()

    with zipfile.ZipFile(SEPROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith(MESSAGES_ZIP_PATH)
                    and f.split('.')[-1] == 'overflow']
        for filename in filelist:
            logging.error('Too long text for card %s',
                          filename.split('/')[-1].split('.')[0])

    logging.info('...Checking messages in the archive (%ss)',
                 round(time.time() - timestamp, 3))


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
    with zipfile.ZipFile(SEPROJECT_PATH) as zip_obj:
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


def generate_png480_nobleed(conf, set_id, set_name, lang, skip_ids):  # pylint: disable=R0914
    """ Generate PNG 480 dpi images without bleed margins.
    """
    logging.info('[%s, %s] Generating PNG 480 dpi images without bleed '
                 'margins...', set_name, lang)
    timestamp = time.time()

    temp_path = os.path.join(
        TEMP_ROOT_PATH, 'generate_png480_nobleed.{}.{}'.format(set_id,
                                                               lang))
    create_folder(temp_path)
    clear_folder(temp_path)

    temp_path2 = os.path.join(
        TEMP_ROOT_PATH, 'generate_png480_nobleed2.{}.{}'.format(set_id,
                                                                lang))
    create_folder(temp_path2)
    clear_folder(temp_path2)

    input_cnt = 0
    with zipfile.ZipFile(SEPROJECT_PATH) as zip_obj:
        filelist = [f for f in zip_obj.namelist()
                    if f.startswith('{}{}'.format(IMAGES_ZIP_PATH,
                                                  PNG480BLEED))
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
                               ) < PNG_480_MIN_SIZE:
                raise GIMPError('GIMP failed for {}'.format(
                    os.path.join(temp_path2, filename)))

        break

    if output_cnt != input_cnt:
        raise GIMPError('Wrong number of output files: {} instead of {}'
                        .format(output_cnt, input_cnt))

    output_path = os.path.join(IMAGES_EONS_PATH, PNG480NOBLEED,
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

    logging.info('[%s, %s] ...Generating PNG 480 dpi images without bleed '
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
    with zipfile.ZipFile(SEPROJECT_PATH) as zip_obj:
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
            if not filename.endswith('.png'):
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


def generate_png480_dragncards_hq(set_id, set_name, lang, skip_ids):
    """ Generate images for DragnCards HQ outputs.
    """
    logging.info('[%s, %s] Generating images for DragnCards HQ outputs...',
                 set_name, lang)
    timestamp = time.time()

    output_path = os.path.join(IMAGES_EONS_PATH, PNG480DRAGNCARDSHQ,
                               '{}.{}'.format(set_id, lang))
    create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)

    input_path = os.path.join(IMAGES_EONS_PATH, PNG480NOBLEED,
                              '{}.{}'.format(set_id, lang))
    known_keys = set()
    for _, _, filenames in os.walk(input_path):
        filenames = sorted(filenames)
        for filename in filenames:
            if not filename.endswith('.png'):
                continue

            key = filename[50:88]
            if key not in known_keys:
                known_keys.add(key)
                shutil.copyfile(os.path.join(input_path, filename),
                                os.path.join(output_path, filename))

        break

    logging.info('[%s, %s] ...Generating images for DragnCards HQ outputs '
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
            if not filename.endswith('.png'):
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
            if not filename.endswith('.png'):
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
    with zipfile.ZipFile(SEPROJECT_PATH) as zip_obj:
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
    with zipfile.ZipFile(SEPROJECT_PATH) as zip_obj:
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
    with zipfile.ZipFile(SEPROJECT_PATH) as zip_obj:
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
    with zipfile.ZipFile(SEPROJECT_PATH) as zip_obj:
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
    with zipfile.ZipFile(SEPROJECT_PATH) as zip_obj:
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
    with zipfile.ZipFile(SEPROJECT_PATH) as zip_obj:
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
    with zipfile.ZipFile(SEPROJECT_PATH) as zip_obj:
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
    with zipfile.ZipFile(SEPROJECT_PATH) as zip_obj:
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


def _make_jpg(conf, input_path, min_size):
    """ Make JPG images from PNG inputs.
    """
    input_cnt = 0
    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            input_cnt += 1

        break

    if input_cnt:
        cmd = MAGICK_COMMAND_JPG.format(conf['magick_path'], input_path,
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

    if output_cnt != input_cnt * 2:
        raise ImageMagickError('Wrong number of output files: {} instead of {}'
                               .format(output_cnt, input_cnt))


def full_card_dict():
    """ Get card dictionary with both spreadsheet and external data.
    """
    card_dict = {}
    for _, _, filenames in os.walk(URL_CACHE_PATH):
        for filename in filenames:
            if filename.endswith('.xml.cache'):
                data = load_external_xml(re.sub(r'\.xml\.cache$', '',
                                                filename))
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
                   'Encounter' not in extract_keywords(
                    card_dict[card_id][CARD_KEYWORDS]) and
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
                          'w', encoding='utf-8') as fobj:
                    res = json.dumps(chunk, indent=4)
                    fobj.write(res)

    return cnt


def generate_tts(conf, set_id, set_name, lang, card_dict, scratch):  # pylint: disable=R0913,R0914
    """ Generate TTS outputs.
    """
    logging.info('[%s, %s] Generating TTS outputs...', set_name, lang)
    timestamp = time.time()

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
            if not filename.endswith('.o8d'):
                continue

            cnt = _generate_tts_sheets(os.path.join(decks_path, filename),
                                       temp_path, image_path, card_dict,
                                       scratch)
            input_cnt += cnt

        break

    if input_cnt > 0:
        output_path = os.path.join(OUTPUT_TTS_PATH, '{}.{}'.format(
            escape_filename(set_name), lang))
        create_folder(output_path)
        clear_folder(output_path)

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
                if not filename.endswith('.jpg'):
                    continue

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


def _extract_image_properties(root):
    """ Extract image properties from the XML file.
    """
    artwork_path = _find_properties(root, 'Artwork')
    artwork_path = artwork_path and artwork_path[0].attrib['value']
    if not artwork_path:
        return None

    artwork_size = _find_properties(root, 'Artwork Size')
    artwork_size = (int(artwork_size[0].attrib['value'])
                    if artwork_size else 0)
    artwork_modified = _find_properties(root, 'Artwork Modified')
    artwork_modified = (int(artwork_modified[0].attrib['value'])
                        if artwork_modified else 0)
    panx = _find_properties(root, 'PanX')
    panx = float(panx[0].attrib['value']) if panx else 0
    pany = _find_properties(root, 'PanY')
    pany = float(pany[0].attrib['value']) if pany else 0
    scale = _find_properties(root, 'Scale')
    scale = float(scale[0].attrib['value']) if scale else 0
    card_type = _find_properties(root, 'Type')
    card_type = card_type[0].attrib['value'] if card_type else ''
    card_sphere = _find_properties(root, 'Sphere')
    card_sphere = card_sphere[0].attrib['value'] if card_sphere else ''
    data = {'path': artwork_path,
            'card_type': card_type,
            'card_sphere': card_sphere,
            'panx': panx,
            'pany': pany,
            'scale': scale,
            'snapshot': (panx, pany, scale, artwork_size, artwork_modified)}
    return data


def _extract_artist_name(root):
    """ Extract the artist name from the XML file.
    """
    artwork_path = _find_properties(root, 'Artwork')
    artwork_path = artwork_path and artwork_path[0].attrib['value']
    if not artwork_path or not '_Artist_' in artwork_path:
        return None

    artist = '.'.join('_Artist_'.join(artwork_path.split('_Artist_')[1:])
                      .split('.')[:-1]).replace('_', ' ')
    return artist


def _extract_custom_images(root):
    """ Extract information about custom images from the XML file.
    """
    images = set()
    i = 0
    while True:
        custom_image = _find_properties(root, 'Custom Image_{}'.format(i))
        if not custom_image:
            break

        images.add(custom_image[0].attrib['value'].split('|')[0])
        i += 1

    return images


def generate_renderer_artwork(conf, set_id, set_name):  # pylint: disable=R0912,R0914,R0915
    """ Generate artwork and artist names for DragnCards proxy images.
    """
    logging.info('[%s] Generating artwork and artist names for DragnCards '
                 'proxy images...', set_name)
    timestamp = time.time()

    xml_path = os.path.join(SET_EONS_PATH, '{}.English.xml'.format(set_id))
    if not os.path.exists(xml_path):
        logging.info('[%s] No XML found for the set', set_name)
        logging.info('[%s] ...Generating artwork and artist names for '
                     'DragnCards proxy images (%ss)', set_name,
                     round(time.time() - timestamp, 3))
        return

    images = {}
    custom_images = set()
    artists = {}
    tree = ET.parse(xml_path)
    root = tree.getroot()
    for card in root[0]:
        if 'skip' in card.attrib or 'noDragncards' in card.attrib:
            continue

        card_id = card.attrib['id']
        custom_images = custom_images.union(_extract_custom_images(card))
        data = _extract_image_properties(card)
        if data:
            images[card_id] = data

        artist = _extract_artist_name(card)
        if artist:
            artists[card_id] = artist

        alternate = [a for a in card if a.attrib.get('type') == 'B']
        if alternate:
            alternate = alternate[0]
            custom_images = custom_images.union(
                _extract_custom_images(alternate))
            data_back = _extract_image_properties(alternate)
            if data_back:
                images['{}.B'.format(card_id)] = data_back
            elif data and data['card_type'] in ('Quest', 'Contract'):
                images['{}.B'.format(card_id)] = data.copy()

            artist_back = _extract_artist_name(alternate)
            if artist_back:
                artists['{}.B'.format(card_id)] = artist_back
            elif (artist and data and
                  data['card_type'] in ('Quest', 'Contract')):
                artists['{}.B'.format(card_id)] = artist

    old_xml_path = os.path.join(SET_EONS_PATH,
                                '{}.English.xml.old'.format(set_id))
    if os.path.exists(old_xml_path):
        tree = ET.parse(old_xml_path)
        root = tree.getroot()
        for card in root[0]:
            card_id = card.attrib['id']
            data = _extract_image_properties(card)
            if (card_id in images and data and
                    data['snapshot'] == images[card_id]['snapshot']):
                del images[card_id]

            alternate = [a for a in card if a.attrib.get('type') == 'B']
            if alternate and '{}.B'.format(card_id) in images:
                alternate = alternate[0]
                data_back = _extract_image_properties(alternate)
                if (not data_back and data and
                        data['card_type'] in ('Quest', 'Contract')):
                    data_back = data

                if (data_back and data_back['snapshot'] ==
                        images['{}.B'.format(card_id)]['snapshot']):
                    del images['{}.B'.format(card_id)]

    output_path = os.path.join(conf['artwork_path'], GENERATED_FOLDER)
    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_renderer_artwork.{}'.format(set_id))
    create_folder(temp_path)
    clear_folder(temp_path)

    if images:
        images_cnt = len(images.keys())
        for value in images.values():
            value['path'] = os.path.join(conf['artwork_path'], set_id,
                                         value['path'])
            del value['snapshot']

        json_path = os.path.join(temp_path, 'images.json')
        with open(json_path, 'w',
                  encoding='utf-8') as fobj:
            res = json.dumps(images, indent=4)
            fobj.write(res)

        cmd = GIMP_COMMAND.format(
            conf['gimp_console_path'],
            'python-generate-renderer-artwork',
            json_path.replace('\\', '\\\\'),
            temp_path.replace('\\', '\\\\'))
        res = _run_cmd(cmd)
        logging.info('[%s] %s', set_name, res)

        output_cnt = 0
        for _, _, filenames in os.walk(temp_path):
            for filename in filenames:
                if not filename.endswith('.jpg'):
                    continue

                output_cnt += 1

            break

        if output_cnt != images_cnt:
            raise GIMPError('Wrong number of output files: {} instead of {}'
                            .format(output_cnt, images_cnt))

        for _, _, filenames in os.walk(temp_path):
            for filename in filenames:
                if not filename.endswith('.jpg'):
                    continue

                shutil.move(os.path.join(temp_path, filename),
                            os.path.join(output_path, filename))

            break

    if custom_images:
        clear_folder(temp_path)
        found_images = False
        input_path = os.path.join(conf['artwork_path'], set_id,
                                  IMAGES_CUSTOM_FOLDER)
        for _, _, filenames in os.walk(input_path):
            for filename in filenames:
                if filename in custom_images:
                    shutil.copyfile(
                        os.path.join(input_path, filename),
                        os.path.join(temp_path,
                                     '{}_{}'.format(set_id, filename)))
                    found_images = True

            break

        if found_images:
            cmd = GIMP_COMMAND.format(
                conf['gimp_console_path'],
                'python-generate-renderer-custom-image-folder',
                temp_path.replace('\\', '\\\\'),
                temp_path.replace('\\', '\\\\'))
            res = _run_cmd(cmd)
            logging.info('[%s] %s', set_name, res)

            for _, _, filenames in os.walk(temp_path):
                for filename in filenames:
                    if (not filename.endswith('.jpg') and
                            not filename.endswith('.png')):
                        continue

                    shutil.move(os.path.join(temp_path, filename),
                                os.path.join(output_path, filename))

                break

    if artists:
        artists_filename = 'artists_{}.json'.format(set_id)
        with open(os.path.join(temp_path, artists_filename), 'w',
                  encoding='utf-8') as fobj:
            json.dump(artists, fobj)

        shutil.move(os.path.join(temp_path, artists_filename),
                    os.path.join(output_path, artists_filename))

    delete_folder(temp_path)

    logging.info('[%s] ...Generating artwork and artist names for DragnCards '
                 'proxy images (%ss)', set_name,
                 round(time.time() - timestamp, 3))


def generate_db(conf, set_id, set_name, lang, card_data):  # pylint: disable=R0912,R0914,R0915
    """ Generate DB, Preview, Hall of Beorn and RingsDB image outputs.
    """
    logging.info('[%s, %s] Generating DB, Preview, Hall of Beorn and RingsDB '
                 'image outputs...', set_name, lang)
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
            if not filename.endswith('.png'):
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
                if not filename.endswith('.png'):
                    continue

                shutil.copyfile(
                    os.path.join(output_path, filename),
                    os.path.join(tts_path, filename.split('----')[1]))

            break

    card_dict = {row[CARD_ID]:row for row in card_data}
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
                if not filename.endswith('.png'):
                    continue

                if (filename.endswith('-2.png') and '----' in filename and
                        filename.split('----')[1][:36] in empty_rules_backs):
                    continue

                shutil.copyfile(os.path.join(output_path, filename),
                                os.path.join(temp_path, filename))

            break

        _make_low_quality(conf, temp_path)

        for _, _, filenames in os.walk(temp_path):
            for filename in filenames:
                if not filename.endswith('.jpg'):
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

    if known_filenames:
        hallofbeorn_output_path = os.path.join(
            OUTPUT_HALLOFBEORN_IMAGES_PATH, '{}.{}'.format(
                escape_filename(set_name), lang))
        create_folder(hallofbeorn_output_path)
        clear_folder(hallofbeorn_output_path)

        known_output_filenames = set()
        for _, _, filenames in os.walk(output_path):
            for filename in filenames:
                if not filename.endswith('.png'):
                    continue

                if '----' not in filename:
                    continue

                card_id = filename.split('----')[1][:36]
                if filename.endswith('-2.png'):
                    card_type = card_dict[card_id][BACK_PREFIX + CARD_TYPE]
                    if card_type in CARD_TYPES_DOUBLESIDE_OPTIONAL:
                        card_name = card_dict[card_id][CARD_NAME]
                        side = (
                            card_dict[card_id][BACK_PREFIX + CARD_ENGAGEMENT]
                            or '' if card_type == 'Quest' else 'B')
                    else:
                        card_name = card_dict[card_id][BACK_PREFIX + CARD_NAME]
                        side = ''
                elif (os.path.exists(os.path.join(
                        output_path, re.sub(r'\.png$', '-2.png', filename)))
                      and card_id not in empty_rules_backs):
                    card_type = card_dict[card_id][CARD_TYPE]
                    card_name = card_dict[card_id][CARD_NAME]
                    if card_type in CARD_TYPES_DOUBLESIDE_OPTIONAL:
                        side = (card_dict[card_id][CARD_ENGAGEMENT] or ''
                                if card_type == 'Quest' else 'A')
                    else:
                        side = ''
                else:
                    card_type = card_dict[card_id][CARD_TYPE]
                    card_name = card_dict[card_id][CARD_NAME]
                    side = ''

                if side == 'B' and card_id in empty_rules_backs:
                    continue

                if card_type == 'Quest':
                    if filename.endswith('-2.png'):
                        card_suffix = (
                            card_dict[card_id][BACK_PREFIX + CARD_COST] or '')
                    else:
                        card_suffix = card_dict[card_id][CARD_COST] or ''
                else:
                    card_suffix = CARD_TYPE_SUFFIX_HALLOFBEORN.get(card_type,
                                                                   '')

                if card_suffix and side:
                    output_filename = '{}-{}{}.png'.format(
                        card_name, card_suffix, side)
                else:
                    output_filename = '{}.png'.format(card_name)

                output_filename = _escape_hallofbeorn_filename(output_filename)
                while output_filename.lower() in known_output_filenames:
                    match = re.search(r'\-([0-9]+)\.png$', output_filename)
                    if match:
                        num = int(match.groups()[0]) + 1
                        output_filename = re.sub(
                            r'\-[0-9]+\.png$', '-{}.png'.format(num),
                            output_filename)
                    else:
                        output_filename = re.sub(r'\.png$', '-2.png',
                                                 output_filename)

                known_output_filenames.add(output_filename.lower())
                shutil.copyfile(os.path.join(output_path, filename),
                                os.path.join(hallofbeorn_output_path,
                                             output_filename))

            break

    if lang == 'English':  # pylint: disable=R1702
        cards = {}
        for row in card_data:
            if row[CARD_SET] == set_id and _needed_for_ringsdb(row):
                card_number = _to_str(handle_int(row[CARD_NUMBER])).zfill(3)
                code = _ringsdb_code(row)
                cards[card_number] = [code]
                if (row[CARD_TYPE] == 'Ally' and row[CARD_UNIQUE] and
                        row[CARD_SPHERE] != 'Neutral'):
                    cards[card_number].append('99{}'.format(code))

        pairs = []
        if cards and known_filenames:
            for _, _, filenames in os.walk(output_path):
                for filename in filenames:
                    if not filename.endswith('.png'):
                        continue

                    card_number = filename[:3]
                    if card_number in cards:
                        suffix = '-2' if filename.endswith('-2.png') else ''
                        for code in cards[card_number]:
                            pairs.append((filename, '{}{}.png'.format(
                                code, suffix)))

                break

        if pairs:
            ringsdb_output_path = os.path.join(
                OUTPUT_RINGSDB_IMAGES_PATH, escape_filename(set_name))
            create_folder(ringsdb_output_path)
            clear_folder(ringsdb_output_path)
            for source_filename, target_filename in pairs:
                shutil.copyfile(os.path.join(output_path, source_filename),
                                os.path.join(ringsdb_output_path,
                                             target_filename))

            back_sides = []
            for _, _, filenames in os.walk(ringsdb_output_path):
                for filename in filenames:
                    if not filename.endswith('.png'):
                        continue

                    if filename.endswith('-2.png'):
                        back_sides.append(filename)

                for filename in back_sides:
                    back_path = os.path.join(ringsdb_output_path, filename)
                    front_path = os.path.join(
                        ringsdb_output_path,
                        filename.replace('-2.png', '.png'))
                    copy_path = os.path.join(
                        ringsdb_output_path,
                        filename.replace('-2.png', '-1.png'))
                    shutil.copyfile(front_path, copy_path)
                    cmd = GIMP_COMMAND.format(
                        conf['gimp_console_path'],
                        'python-glue-ringsdb-images',
                        front_path.replace('\\', '\\\\'),
                        back_path.replace('\\', '\\\\'))
                    res = _run_cmd(cmd)
                    logging.info('[%s, %s] %s', set_name, lang, res)

                break

    elif lang == 'French':  # pylint: disable=R1702
        cards = {}
        for row in card_data:
            if row[CARD_SET] == set_id and _needed_for_frenchdb_images(row):
                card_number = _to_str(handle_int(row[CARD_NUMBER])).zfill(3)
                cards[card_number] = row[CARD_NUMBER]

        pairs = []
        if cards and known_filenames:
            for _, _, filenames in os.walk(output_path):
                for filename in filenames:
                    if not filename.endswith('.png'):
                        continue

                    if (filename.endswith('-2.png') and
                            '----' in filename and
                            filename.split('----')[1][:36]
                            in empty_rules_backs):
                        continue

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
                card_number = _to_str(handle_int(row[CARD_NUMBER])).zfill(3)
                cards[card_number] = _spanishdb_code(row)

        pairs = []
        if cards and known_filenames:
            for _, _, filenames in os.walk(output_path):
                for filename in filenames:
                    if not filename.endswith('.png'):
                        continue

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

    logging.info('[%s, %s] ...Generating DB, Preview, Hall of Beorn and '
                 'RingsDB image outputs (%ss)', set_name, lang,
                 round(time.time() - timestamp, 3))


def generate_dragncards_hq(conf, set_id, set_name, lang, card_data):  # pylint: disable=R0914
    """ Generate DragnCards HQ image outputs.
    """
    logging.info('[%s, %s] Generating DragnCards HQ image outputs...',
                 set_name, lang)
    timestamp = time.time()

    input_path = os.path.join(IMAGES_EONS_PATH, PNG480DRAGNCARDSHQ,
                              '{}.{}'.format(set_id, lang))
    output_path = os.path.join(OUTPUT_DRAGNCARDS_HQ_PATH, '{}.{}'.format(
        escape_filename(set_name), lang))

    temp_path = os.path.join(TEMP_ROOT_PATH,
                             'generate_dragncards_hq.{}.{}'.format(set_id,
                                                                   lang))
    create_folder(temp_path)
    clear_folder(temp_path)

    card_ids = {row[CARD_ID] for row in card_data
                if row[CARD_SET] == set_id
                and _needed_for_octgn(row)}

    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            if not filename.endswith('.png'):
                continue

            if filename[50:86] not in card_ids:
                continue

            shutil.copyfile(os.path.join(input_path, filename),
                            os.path.join(temp_path, filename))

        break

    _make_jpg(conf, temp_path, JPG_480_MIN_SIZE)

    known_filenames = set()
    for _, _, filenames in os.walk(temp_path):
        if not filenames:
            logging.error('[%s, %s] No cards found', set_name, lang)
            break

        create_folder(output_path)
        filenames = sorted(filenames)
        for filename in filenames:
            if filename.split('.')[-1] != 'jpg':
                continue

            output_filename = re.sub(
                r'-1\.jpg$', '.jpg',
                re.sub(r'-2\.jpg$', '.B.jpg', filename))[50:]
            if output_filename not in known_filenames:
                known_filenames.add(output_filename)
                shutil.copyfile(os.path.join(temp_path, filename),
                                os.path.join(output_path, output_filename))

        break

    delete_folder(temp_path)

    logging.info('[%s, %s] ...Generating DragnCards HQ image outputs '
                 '(%ss)', set_name, lang, round(time.time() - timestamp, 3))


def generate_octgn(conf, set_id, set_name, lang, card_data):  # pylint: disable=R0914
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

    card_ids = {row[CARD_ID] for row in card_data
                if row[CARD_SET] == set_id
                and _needed_for_octgn(row)}

    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            if not filename.endswith('.png'):
                continue

            if filename[50:86] not in card_ids:
                continue

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
    for value in images.values():
        pages_raw.extend([(value[i * 6:(i + 1) * 6] + [None] * 6)[:6]
                          for i in range(math.ceil(len(value) / 6))])

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

    for page_format, obj in formats.items():
        canvas = Canvas(
            os.path.join(output_path, 'Home.{}.{}.{}.pdf'.format(
                page_format, escape_filename(set_name), lang)),
            pagesize=landscape(obj))
        width, height = landscape(obj)
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
    for value in images.values():
        pages_raw.extend([(value[i * 6:(i + 1) * 6] + [None] * 6)[:6]
                          for i in range(math.ceil(len(value) / 6))])

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

    for page_format, format_data in formats.items():
        pdf_filename = '800dpi.{}.{}.{}.pdf'.format(
            page_format, escape_filename(set_name), lang)
        pdf_path = os.path.join(temp_path, pdf_filename)
        canvas = Canvas(pdf_path, pagesize=landscape(format_data[0]))
        width, height = landscape(format_data[0])
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

        if 'zip' in format_data[1]:
            with zipfile.ZipFile(
                    os.path.join(output_path, '{}.zip'.format(pdf_filename)),
                    'w') as obj:
                obj.write(pdf_path, pdf_filename)

        if '7z' in format_data[1]:
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
        filenames = [f for f in filenames
                     if f.endswith('.jpg') or f.endswith('.png')]
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
            logging.warning('Path %s does not exist', first_back_unofficial)
            continue

        if not os.path.exists(second_front):
            logging.warning('Path %s does not exist', second_front)
            continue

        if not os.path.exists(second_back_unofficial):
            logging.warning('Path %s does not exist', second_back_unofficial)
            continue

        if service != 'mpc':
            first_back_official = os.path.join(
                input_path, '{}-2o.{}'.format(pair[0], file_type))
            second_back_official = os.path.join(
                input_path, '{}-2o.{}'.format(pair[1], file_type))
            if not os.path.exists(first_back_official):
                logging.warning('Path %s does not exist', first_back_official)
                continue

            if not os.path.exists(second_back_official):
                logging.warning('Path %s does not exist', second_back_official)
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
            obj.write(MAKEPLAYINGCARDS_PDF, 'MakePlayingCards.pdf')

    if 'makeplayingcards_7z' in conf['outputs'][lang]:
        with py7zr.SevenZipFile(
                os.path.join(output_path,
                             'MPC.{}.{}.images.7z'.format(
                                 escape_filename(set_name), lang)),
                'w', filters=PY7ZR_FILTERS) as obj:
            _prepare_mpc_printing_archive(temp_path, obj)
            obj.write(MAKEPLAYINGCARDS_PDF, 'MakePlayingCards.pdf')

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
            obj.write(DRIVETHRUCARDS_PDF, 'DriveThruCards.pdf')

    if 'drivethrucards_7z' in conf['outputs'][lang]:
        with py7zr.SevenZipFile(
                os.path.join(output_path,
                             'DTC.{}.{}.images.7z'.format(
                                 escape_filename(set_name), lang)),
                'w', filters=PY7ZR_FILTERS) as obj:
            _prepare_dtc_printing_archive(temp_path, obj)
            obj.write(DRIVETHRUCARDS_PDF, 'DriveThruCards.pdf')

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
                obj.write(MBPRINT_PDF, 'MBPrint.pdf')

        if 'mbprint_7z' in conf['outputs'][lang]:
            with py7zr.SevenZipFile(
                    os.path.join(output_path,
                                 'MBPRINT.{}.{}.images.7z'.format(
                                     escape_filename(set_name), lang)),
                    'w', filters=PY7ZR_FILTERS) as obj:
                _prepare_mbprint_printing_archive(temp_path, obj)
                obj.write(MBPRINT_PDF, 'MBPrint.pdf')

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
                if not filename.endswith('.png'):
                    continue

                shutil.copyfile(os.path.join(output_path, filename),
                                os.path.join(destination_path, filename))

            break

        shutil.copyfile(
            DOWNLOAD_TIME_PATH,
            os.path.join(destination_path,
                         os.path.split(DOWNLOAD_TIME_PATH)[-1]))

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
                if not filename.endswith('.o8c'):
                    continue

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
                if not filename.endswith('.jpg'):
                    continue

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
    parts = conf.get('dragncards_hostname', '').split('@')
    client.connect(parts[1], username=parts[0],
                   key_filename=conf.get('dragncards_id_rsa_path', ''),
                   timeout=30)
    return client


def trigger_dragncards_build(conf):
    """ Trigger a DragnCards build.
    """
    logging.info('Running remote command: %s',
                 DRAGNCARDS_BUILD_TRIGGER_COMMAND)
    client = _get_ssh_client(conf)
    try:
        client.exec_command(DRAGNCARDS_BUILD_TRIGGER_COMMAND, timeout=30)
    finally:
        try:
            client.close()
        except Exception:
            pass


def get_dragncards_build(conf):
    """ Get information about the latest DragnCards build.
    """
    logging.info('Running remote command: %s', DRAGNCARDS_BUILD_STAT_COMMAND)
    client = _get_ssh_client(conf)
    try:
        _, res, _ = client.exec_command(DRAGNCARDS_BUILD_STAT_COMMAND,
                                        timeout=30)
        res = res.read().decode('utf-8').strip()
        return res
    finally:
        try:
            client.close()
        except Exception:
            pass


def get_dragncards_player_cards_stat(conf, card_ids, start_date, end_date):
    """ Get DragnCards player cards statistics for the set.
    """
    command = DRAGNCARDS_PLAYER_CARDS_STAT_COMMAND.format(
        card_ids, start_date, end_date)
    logging.info('Running remote command: %s', command)
    client = _get_ssh_client(conf)
    try:
        _, res, _ = client.exec_command(command, timeout=120)
        res = res.read().decode('utf-8').strip()
        return res
    finally:
        try:
            client.close()
        except Exception:
            pass


def get_dragncards_all_plays(conf, quest, start_date, end_date):
    """ Get information about all DragnCards plays for the quest.
    """
    command = DRAGNCARDS_ALL_PLAYS_COMMAND.format(quest, start_date, end_date)
    logging.info('Running remote command: %s', command)
    client = _get_ssh_client(conf)
    try:
        _, res, _ = client.exec_command(command, timeout=120)
        res = res.read().decode('utf-8').strip()
        return res
    finally:
        try:
            client.close()
        except Exception:
            pass


def get_dragncards_plays_stat(conf, quest, start_date, end_date):
    """ Get aggregated DragnCards plays statistics for the quest.
    """
    command = DRAGNCARDS_PLAYS_STAT_COMMAND.format(quest, start_date, end_date)
    logging.info('Running remote command: %s', command)
    client = _get_ssh_client(conf)
    try:
        _, res, _ = client.exec_command(command, timeout=120)
        res = res.read().decode('utf-8').strip()
        return res
    finally:
        try:
            client.close()
        except Exception:
            pass


def get_dragncards_quests_stat(conf, quests):
    """ Get aggregated DragnCards statistics for all released ALeP quests.
    """
    command = DRAGNCARDS_QUESTS_STAT_COMMAND.format(quests)
    logging.info('Running remote command: %s', command)
    client = _get_ssh_client(conf)
    try:
        _, res, _ = client.exec_command(command, timeout=120)
        res = res.read().decode('utf-8').strip()
        return res
    finally:
        try:
            client.close()
        except Exception:
            pass


def _get_remote_dragncards_folder(conf):
    """ Get remote DragnCards folder.
    """
    logging.info('Running remote command: %s', DRAGNCARDS_IMAGES_START_COMMAND)
    client = _get_ssh_client(conf)
    try:
        _, res, _ = client.exec_command(DRAGNCARDS_IMAGES_START_COMMAND,
                                        timeout=30)
        res = res.read().decode('utf-8').strip()
        if not res:
            raise DragnCardsError(
                'Error getting remote folder from DragnCards')

        return res
    finally:
        try:
            client.close()
        except Exception:
            pass


def _finish_uploading_dragncards_images(conf, remote_folder):
    """ Finish uploading images to DragnCards.
    """
    logging.info('Running remote command: %s %s',
                 DRAGNCARDS_IMAGES_FINISH_COMMAND, remote_folder)
    client = _get_ssh_client(conf)
    try:
        _, res, _ = client.exec_command(
            '{} {}'.format(DRAGNCARDS_IMAGES_FINISH_COMMAND, remote_folder),
            timeout=30)
        res = res.read().decode('utf-8').strip()
        if res != 'Done':
            raise DragnCardsError('Error uploading images to DragnCards: {}'
                                  .format(res))
    finally:
        try:
            client.close()
        except Exception:
            pass


def write_remote_dragncards_folder(conf):
    """ Write remote DragnCards folder to a local file.
    """
    remote_folder = _get_remote_dragncards_folder(conf)
    with open(DRAGNCARDS_FOLDER_PATH, 'w', encoding='utf-8') as fobj:
        fobj.write(remote_folder)


def _read_remote_dragncards_folder():
    """ Read remote DragnCards folder from the local file.
    """
    if not os.path.exists(DRAGNCARDS_FOLDER_PATH):
        raise DragnCardsError(
            'Error reading remote DragnCards folder from the local file')

    with open(DRAGNCARDS_FOLDER_PATH, 'r', encoding='utf-8') as fobj:
        remote_folder = fobj.read()

    os.remove(DRAGNCARDS_FOLDER_PATH)
    if not remote_folder:
        raise DragnCardsError(
            'Error reading remote DragnCards folder from the local file')

    return remote_folder


def _scp_upload(client, scp_client, conf, source_path, destination_path):
    """ Upload a file to DragnCards host using SCP.
    """
    logging.info('Uploading %s', source_path)
    for i in range(SCP_RETRIES):
        try:
            scp_client.put(source_path, destination_path)
            break
        except Exception:
            if i < SCP_RETRIES - 1:
                try:
                    client.close()
                except Exception:
                    pass

                time.sleep(SCP_SLEEP * (i + 1))
                client = _get_ssh_client(conf)
                scp_client = SCPClient(client.get_transport())
            else:
                raise

    return (client, scp_client)


def upload_dragncards_images(conf, sets):
    """ Uploading pixel-perfect images to DragnCards.
    """
    logging.info('Uploading pixel-perfect images to DragnCards...')
    timestamp = time.time()

    remote_folder = _read_remote_dragncards_folder()
    images_uploaded = False
    client = _get_ssh_client(conf)
    try:  # pylint: disable=R1702
        scp_client = SCPClient(client.get_transport())
        for set_id, set_name in sets:
            output_path = os.path.join(
                OUTPUT_OCTGN_IMAGES_PATH,
                '{}.English'.format(escape_filename(set_name)),
                '{}.English.o8c'.format(
                    escape_octgn_filename(escape_filename(set_name))))
            if ('English' in conf['output_languages'] and
                    'octgn' in conf['outputs']['English'] and
                    os.path.exists(output_path)):
                temp_path = os.path.join(
                    TEMP_ROOT_PATH,
                    'upload_dragncards_images_{}'.format(
                        escape_filename(set_name)))
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
                        if filenames:
                            images_uploaded = True

                        for filename in filenames:
                            client, scp_client = _scp_upload(
                                client,
                                scp_client,
                                conf,
                                os.path.join(output_path, filename),
                                remote_folder)

                        break

                    logging.info('Successfully uploaded images for %s to '
                                 'DragnCards host', set_name)

                delete_folder(temp_path)

        if images_uploaded:
            _finish_uploading_dragncards_images(conf, remote_folder)
            trigger_dragncards_build(conf)

    finally:
        try:
            client.close()
        except Exception:
            pass

    logging.info('...Uploading pixel-perfect images to DragnCards (%ss)',
                 round(time.time() - timestamp, 3))


def _upload_dragncards_rendered_images(conf):
    """ Uploading rendered images to DragnCards.
    """
    images_uploaded = False
    client = _get_ssh_client(conf)
    try:
        scp_client = SCPClient(client.get_transport())
        for _, _, filenames in os.walk(RENDERER_OUTPUT_PATH):
            filenames = [f for f in filenames if f.endswith('.jpg')]
            if filenames:
                images_uploaded = True

            for filename in filenames:
                client, scp_client = _scp_upload(
                    client,
                    scp_client,
                    conf,
                    os.path.join(RENDERER_OUTPUT_PATH, filename),
                    conf['dragncards_remote_image_path'])
                os.remove(os.path.join(RENDERER_OUTPUT_PATH, filename))

            break
    finally:
        try:
            client.close()
        except Exception:
            pass

    return images_uploaded


def _upload_dragncards_decks_and_json(conf, sets):  # pylint: disable=R0912,R0914,R0915
    """ Uploading decks and JSON files to DragnCards.
    """
    try:
        with open(DRAGNCARDS_FILES_JSON_PATH, 'r', encoding='utf-8') as fobj:
            checksums = json.load(fobj)
    except Exception:
        checksums = {}

    changes = False
    client = _get_ssh_client(conf)
    try:  # pylint: disable=R1702
        scp_client = SCPClient(client.get_transport())
        for _, set_name in sets:
            output_path = os.path.join(OUTPUT_OCTGN_DECKS_PATH,
                                       escape_filename(set_name))
            if (conf['dragncards_remote_deck_path'] and conf['octgn_o8d'] and
                    os.path.exists(output_path)):
                temp_path = os.path.join(
                    TEMP_ROOT_PATH,
                    'upload_dragncards_decks_and_json_{}'.format(
                        escape_filename(set_name)))
                create_folder(temp_path)
                clear_folder(temp_path)
                for _, _, filenames in os.walk(output_path):
                    for filename in filenames:
                        if not filename.endswith('.o8d'):
                            continue

                        if filename.startswith('Player-'):
                            continue

                        file_path = os.path.join(output_path, filename)
                        with open(file_path, 'rb') as fobj:
                            content = fobj.read()

                        checksum = hashlib.md5(content).hexdigest()
                        if checksum == checksums.get(file_path):
                            continue

                        changes = True
                        checksums[file_path] = checksum

                        new_filename = re.sub(r'\.o8d$',
                                              '{}.o8d'.format(PLAYTEST_SUFFIX),
                                              filename)
                        shutil.copyfile(file_path,
                                        os.path.join(temp_path, new_filename))
                        client, scp_client = _scp_upload(
                            client,
                            scp_client,
                            conf,
                            os.path.join(temp_path, new_filename),
                            conf['dragncards_remote_deck_path'])

                    break

                delete_folder(temp_path)

        for set_id, set_name in sets:
            output_path = os.path.join(
                OUTPUT_DRAGNCARDS_PATH,
                escape_filename(set_name),
                '{}.json'.format(set_id))
            if (conf['dragncards_remote_json_path'] and
                    conf['dragncards_json'] and
                    os.path.exists(output_path)):
                with open(output_path, 'rb') as fobj:
                    content = fobj.read()

                checksum = hashlib.md5(content).hexdigest()
                if checksum == checksums.get(output_path):
                    continue

                changes = True
                checksums[output_path] = checksum

                client, scp_client = _scp_upload(
                    client,
                    scp_client,
                    conf,
                    output_path,
                    conf['dragncards_remote_json_path'])
    finally:
        try:
            client.close()
        except Exception:
            pass

    if changes:
        with open(DRAGNCARDS_FILES_JSON_PATH, 'w', encoding='utf-8') as fobj:
            json.dump(checksums, fobj)

    return changes


def upload_dragncards_lightweight_outputs(conf, sets):
    """ Uploading lightweight outputs to DragnCards.
    """
    logging.info('Uploading lightweight outputs to DragnCards...')
    timestamp = time.time()

    changes_rendered_images = _upload_dragncards_rendered_images(conf)
    changes_decks_and_json = _upload_dragncards_decks_and_json(conf, sets)
    if changes_rendered_images or changes_decks_and_json:
        trigger_dragncards_build(conf)

    logging.info('...Uploading lightweight outputs to DragnCards (%ss)',
                 round(time.time() - timestamp, 3))


def update_ringsdb(conf, sets):
    """ Update ringsdb.com.
    """
    logging.info('Updating ringsdb.com...')
    timestamp = time.time()

    try:
        with open(RINGSDB_JSON_PATH, 'r', encoding='utf-8') as fobj:
            checksums = json.load(fobj)
    except Exception:
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

        with open(path, 'rb') as fobj:
            content = fobj.read()

        checksum = hashlib.md5(content).hexdigest()
        if checksum == checksums.get(set_id):
            continue

        if (len([p for p in content.decode('utf-8').split('\n')
                if p.strip()]) <= 1):
            continue

        changes = True
        checksums[set_id] = checksum

        logging.info('Uploading %s to %s', set_name, conf['ringsdb_url'])
        cookies = _read_ringsdb_cookies(conf)
        session = requests.Session()
        session.cookies.update(cookies)
        if conf['ringsdb_url'].startswith('https://'):
            session.mount('https://', TLSAdapter())

        with open(path, 'rb') as fobj:
            res = session.post(
                '{}/admin/csv/upload'.format(conf['ringsdb_url']),
                files={'upfile': fobj},
                data={'code': SETS[set_id][SET_HOB_CODE], 'name': set_name})

        res = res.content.decode('utf-8').strip()
        if res != 'Done':
            raise RingsDBError('Error uploading {} to ringsdb.com: {}'
                               .format(set_name, res[:LOG_LIMIT]))

        cookies = session.cookies.get_dict()
        _write_ringsdb_cookies(cookies)

    if changes:
        with open(RINGSDB_JSON_PATH, 'w', encoding='utf-8') as fobj:
            json.dump(checksums, fobj)

    logging.info('...Updating ringsdb.com (%ss)',
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
