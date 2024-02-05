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

re._MAXCACHE = 1000  # pylint: disable=W0212


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
BACK_PREFIX_LOG = 'Back '

CARD_SET = 'Set'
CARD_ID = 'Card GUID'
CARD_UPDATED = 'Updated'
CARD_DIFF = 'Diff'
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
CARD_TEXT = 'Text'
CARD_SHADOW = 'Shadow'
CARD_FLAVOUR = 'Flavour'
CARD_PRINTED_NUMBER = 'Printed Card Number'
CARD_ENCOUNTER_SET_NUMBER = 'Encounter Set Number'
CARD_ENCOUNTER_SET_ICON = 'Encounter Set Icon'
CARD_FLAGS = 'Flags'
CARD_ICONS = 'Icons'
CARD_INFO = 'Info'
CARD_ARTIST = 'Artist'
CARD_PANX = 'PanX'
CARD_PANY = 'PanY'
CARD_SCALE = 'Scale'
CARD_PORTRAIT_SHADOW = 'Portrait Shadow'
CARD_SIDE_B = 'Side B'
CARD_EASY_MODE = 'Removed for Easy Mode'
CARD_ADDITIONAL_ENCOUNTER_SETS = 'Additional Encounter Sets'
CARD_ADVENTURE = 'Adventure'
CARD_COLLECTION_ICON = 'Collection Icon'
CARD_COPYRIGHT = 'Copyright'
CARD_BACK = 'Card Back'
CARD_DECK_RULES = 'Deck Rules'
CARD_SELECTED = 'Selected'
CARD_CHANGED = 'Changed'
CARD_BOT_DISABLED = 'Bot Disabled'
CARD_LAST_DESIGN_CHANGE_DATE = 'Last Design Change Date'

CARD_SCRATCH = '_Scratch'
CARD_SET_NAME = '_Set Name'
CARD_SET_RINGSDB_CODE = '_Set RingsDB Code'
CARD_SET_HOB_CODE = '_Set HoB Code'
CARD_SET_LOCKED = '_Locked'
CARD_RINGSDB_CODE = '_RingsDB Code'
CARD_NORMALIZED_NAME = '_Normalized Name'
CARD_DISCORD_CHANNEL = '_Discord Channel'
CARD_DISCORD_CATEGORY = '_Discord Category'

CARD_ENCOUNTER_SET_NUMBER_START = '_Encounter Set Number Start'
CARD_ENCOUNTER_SET_TOTAL = '_Encounter Set Total'
CARD_PRINTED_NUMBER_AUTO = '_Printed Card Number Auto'

CARD_DOUBLESIDE = '_Card Side'
CARD_ORIGINAL_NAME = '_Original Name'

MAX_COLUMN = '_Max Column'
ROW_COLUMN = '_Row'

DISCORD_IGNORE_COLUMNS = {
    CARD_UPDATED, CARD_DIFF, CARD_PANX, CARD_PANY, CARD_SCALE,
    CARD_PORTRAIT_SHADOW, BACK_PREFIX + CARD_PANX, BACK_PREFIX + CARD_PANY,
    BACK_PREFIX + CARD_SCALE, BACK_PREFIX + CARD_PORTRAIT_SHADOW, CARD_SIDE_B,
    CARD_SELECTED, CARD_CHANGED, CARD_SCRATCH,
    CARD_ENCOUNTER_SET_NUMBER_START, CARD_ENCOUNTER_SET_TOTAL
}
DISCORD_IGNORE_CHANGES_COLUMNS = {
    CARD_SET, CARD_NUMBER, CARD_SET_NAME, CARD_SET_RINGSDB_CODE,
    CARD_SET_HOB_CODE, CARD_SET_LOCKED, CARD_RINGSDB_CODE, CARD_BOT_DISABLED,
    CARD_LAST_DESIGN_CHANGE_DATE, CARD_NORMALIZED_NAME,
    BACK_PREFIX + CARD_NORMALIZED_NAME, CARD_DISCORD_CHANNEL,
    CARD_DISCORD_CATEGORY, CARD_PRINTED_NUMBER_AUTO, ROW_COLUMN
}
ONE_LINE_COLUMNS = {
    CARD_ENCOUNTER_SET, CARD_NAME, CARD_TRAITS, CARD_KEYWORDS, CARD_VICTORY,
    CARD_PRINTED_NUMBER, CARD_ENCOUNTER_SET_NUMBER, CARD_ENCOUNTER_SET_ICON,
    CARD_ICONS, CARD_INFO, CARD_ARTIST, BACK_PREFIX + CARD_NAME,
    BACK_PREFIX + CARD_TRAITS, BACK_PREFIX + CARD_KEYWORDS,
    BACK_PREFIX + CARD_VICTORY, BACK_PREFIX + CARD_PRINTED_NUMBER,
    BACK_PREFIX + CARD_ENCOUNTER_SET_NUMBER,
    BACK_PREFIX + CARD_ENCOUNTER_SET_ICON, BACK_PREFIX + CARD_ICONS,
    BACK_PREFIX + CARD_INFO, BACK_PREFIX + CARD_ARTIST,
    CARD_ADDITIONAL_ENCOUNTER_SETS, CARD_ADVENTURE, CARD_COLLECTION_ICON,
    CARD_COPYRIGHT}
TRANSLATED_COLUMNS = {
    CARD_NAME, CARD_TRAITS, CARD_KEYWORDS, CARD_VICTORY, CARD_TEXT,
    CARD_SHADOW, CARD_FLAVOUR, BACK_PREFIX + CARD_NAME,
    BACK_PREFIX + CARD_TRAITS, BACK_PREFIX + CARD_KEYWORDS,
    BACK_PREFIX + CARD_VICTORY, BACK_PREFIX + CARD_TEXT,
    BACK_PREFIX + CARD_SHADOW, BACK_PREFIX + CARD_FLAVOUR, CARD_ADVENTURE
}

T_ALLY = 'Ally'
T_ATTACHMENT = 'Attachment'
T_CAMPAIGN = 'Campaign'
T_CONTRACT = 'Contract'
T_ENCOUNTER_SIDE_QUEST = 'Encounter Side Quest'
T_ENEMY = 'Enemy'
T_EVENT = 'Event'
T_FULL_ART_LANDSCAPE = 'Full Art Landscape'
T_FULL_ART_PORTRAIT = 'Full Art Portrait'
T_HERO = 'Hero'
T_LOCATION = 'Location'
T_NIGHTMARE = 'Nightmare'
T_OBJECTIVE = 'Objective'
T_OBJECTIVE_ALLY = 'Objective Ally'
T_OBJECTIVE_HERO = 'Objective Hero'
T_OBJECTIVE_LOCATION = 'Objective Location'
T_PLAYER_OBJECTIVE = 'Player Objective'
T_PLAYER_SIDE_QUEST = 'Player Side Quest'
T_PRESENTATION = 'Presentation'
T_QUEST = 'Quest'
T_RULES = 'Rules'
T_SHIP_ENEMY = 'Ship Enemy'
T_SHIP_OBJECTIVE = 'Ship Objective'
T_TREACHERY = 'Treachery'
T_TREASURE = 'Treasure'
T_ALIAS_SIDE_QUEST = 'Side Quest'

S_BACK = 'Back'
S_BAGGINS = 'Baggins'
S_BOON = 'Boon'
S_BOONLEADERSHIP = 'BoonLeadership'
S_BOONLORE = 'BoonLore'
S_BOONSPIRIT = 'BoonSpirit'
S_BOONTACTICS = 'BoonTactics'
S_BURDEN = 'Burden'
S_CAVE = 'Cave'
S_FELLOWSHIP = 'Fellowship'
S_LEADERSHIP = 'Leadership'
S_LORE = 'Lore'
S_NEUTRAL = 'Neutral'
S_NIGHTMARE = 'Nightmare'
S_NOICON = 'NoIcon'
S_NOPROGRESS = 'NoProgress'
S_NOSTAT = 'NoStat'
S_REGION = 'Region'
S_SETUP = 'Setup'
S_SMALLTEXTAREA = 'SmallTextArea'
S_SPIRIT = 'Spirit'
S_TACTICS = 'Tactics'
S_UPGRADED = 'Upgraded'

F_ADDITIONALCOPIES = 'AdditionalCopies'
F_IGNORENAME = 'IgnoreName'
F_IGNORERULES = 'IgnoreRules'
F_NOARTIST = 'NoArtist'
F_NOCOPYRIGHT = 'NoCopyright'
F_NOTRAITS = 'NoTraits'
F_PROMO = 'Promo'
F_STAR = 'Star'
F_BLUERING = 'BlueRing'
F_GREENRING = 'GreenRing'
F_REDRING = 'RedRing'

B_ENCOUNTER = 'Encounter'
B_PLAYER = 'Player'

L_ENGLISH = 'English'
L_FRENCH = 'French'
L_GERMAN = 'German'
L_ITALIAN = 'Italian'
L_POLISH = 'Polish'
L_PORTUGUESE = 'Portuguese'
L_SPANISH = 'Spanish'

CARD_TYPES = {T_ALLY, T_ATTACHMENT, T_CAMPAIGN, T_CONTRACT,
              T_ENCOUNTER_SIDE_QUEST, T_ENEMY, T_EVENT, T_FULL_ART_LANDSCAPE,
              T_FULL_ART_PORTRAIT, T_HERO, T_LOCATION, T_NIGHTMARE,
              T_OBJECTIVE, T_OBJECTIVE_ALLY, T_OBJECTIVE_HERO,
              T_OBJECTIVE_LOCATION, T_PLAYER_OBJECTIVE, T_PLAYER_SIDE_QUEST,
              T_PRESENTATION, T_QUEST, T_RULES, T_SHIP_ENEMY, T_SHIP_OBJECTIVE,
              T_TREACHERY, T_TREASURE}
CARD_TYPES_LANDSCAPE = {T_ENCOUNTER_SIDE_QUEST, T_FULL_ART_LANDSCAPE,
                        T_PLAYER_SIDE_QUEST, T_QUEST}
CARD_TYPES_DOUBLESIDE_DEFAULT = {T_CAMPAIGN, T_NIGHTMARE, T_PRESENTATION,
                                 T_QUEST, T_RULES}
CARD_TYPES_PLAYER = {T_ALLY, T_ATTACHMENT, T_CONTRACT, T_EVENT, T_HERO,
                     T_PLAYER_OBJECTIVE, T_PLAYER_SIDE_QUEST, T_TREASURE}
CARD_TYPES_PLAYER_DECK = {T_ALLY, T_ATTACHMENT, T_EVENT, T_PLAYER_SIDE_QUEST}
CARD_TYPES_ENCOUNTER_SIZE = {T_ENEMY, T_LOCATION, T_OBJECTIVE,
                             T_OBJECTIVE_ALLY, T_OBJECTIVE_HERO,
                             T_OBJECTIVE_LOCATION, T_SHIP_ENEMY,
                             T_SHIP_OBJECTIVE, T_TREACHERY, T_TREASURE}
CARD_TYPES_ENCOUNTER_SET = {T_CAMPAIGN, T_ENCOUNTER_SIDE_QUEST, T_ENEMY,
                            T_LOCATION, T_NIGHTMARE, T_OBJECTIVE,
                            T_OBJECTIVE_ALLY, T_OBJECTIVE_HERO,
                            T_OBJECTIVE_LOCATION, T_QUEST, T_SHIP_ENEMY,
                            T_SHIP_OBJECTIVE, T_TREACHERY, T_TREASURE}
CARD_TYPES_NO_ENCOUNTER_SET = {T_ALLY, T_ATTACHMENT, T_CONTRACT, T_EVENT,
                               T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT,
                               T_HERO, T_PLAYER_OBJECTIVE, T_PLAYER_SIDE_QUEST,
                               T_PRESENTATION}
CARD_TYPES_UNIQUE = {T_HERO, T_OBJECTIVE_HERO, T_PLAYER_OBJECTIVE, T_TREASURE}
CARD_TYPES_NO_UNIQUE = {T_CAMPAIGN, T_EVENT, T_FULL_ART_LANDSCAPE,
                        T_FULL_ART_PORTRAIT, T_NIGHTMARE, T_PRESENTATION,
                        T_QUEST, T_RULES}
CARD_TYPES_PLAYER_SPHERE = {T_ALLY, T_ATTACHMENT, T_EVENT, T_HERO,
                            T_PLAYER_SIDE_QUEST}
CARD_TYPES_TRAITS = {T_ALLY, T_ATTACHMENT, T_ENEMY, T_HERO, T_LOCATION,
                     T_OBJECTIVE_ALLY, T_OBJECTIVE_HERO, T_OBJECTIVE_LOCATION,
                     T_SHIP_ENEMY, T_SHIP_OBJECTIVE, T_TREASURE}
CARD_TYPES_NO_TRAITS = {T_CAMPAIGN, T_CONTRACT, T_FULL_ART_LANDSCAPE,
                        T_FULL_ART_PORTRAIT, T_NIGHTMARE, T_PRESENTATION,
                        T_QUEST, T_RULES}
CARD_SPHERES_TRAITS = {S_REGION}
CARD_TYPES_NO_KEYWORDS = {T_CAMPAIGN, T_CONTRACT, T_FULL_ART_LANDSCAPE,
                          T_FULL_ART_PORTRAIT, T_NIGHTMARE, T_PRESENTATION,
                          T_RULES}
CARD_TYPES_COST = {T_ALLY, T_ATTACHMENT, T_EVENT, T_HERO, T_PLAYER_SIDE_QUEST,
                   T_QUEST, T_TREASURE}
CARD_TYPES_ENGAGEMENT = {T_ENEMY, T_QUEST, T_SHIP_ENEMY}
CARD_TYPES_THREAT = {T_ENEMY, T_LOCATION, T_SHIP_ENEMY}
CARD_TYPES_WILLPOWER = {T_ALLY, T_HERO, T_OBJECTIVE_ALLY, T_OBJECTIVE_HERO,
                        T_SHIP_OBJECTIVE}
CARD_TYPES_COMBAT = {T_ALLY, T_ENEMY, T_HERO, T_OBJECTIVE_ALLY,
                     T_OBJECTIVE_HERO, T_SHIP_ENEMY, T_SHIP_OBJECTIVE}
CARD_TYPES_QUEST = {T_ENCOUNTER_SIDE_QUEST, T_LOCATION, T_OBJECTIVE_LOCATION,
                    T_PLAYER_SIDE_QUEST}
CARD_TYPES_QUEST_BACK = {T_QUEST}
CARD_SPHERES_NO_QUEST = {S_CAVE, S_NOPROGRESS, S_REGION}
CARD_TYPES_VICTORY = {T_ALLY, T_ATTACHMENT, T_ENCOUNTER_SIDE_QUEST, T_ENEMY,
                      T_EVENT, T_HERO, T_LOCATION, T_OBJECTIVE,
                      T_OBJECTIVE_ALLY, T_OBJECTIVE_HERO, T_OBJECTIVE_LOCATION,
                      T_PLAYER_OBJECTIVE, T_PLAYER_SIDE_QUEST, T_SHIP_ENEMY,
                      T_SHIP_OBJECTIVE, T_TREACHERY, T_TREASURE}
CARD_TYPES_VICTORY_BACK = {T_QUEST}
CARD_SPHERES_NO_VICTORY = {S_CAVE, S_NOSTAT, S_REGION}
CARD_TYPES_NO_PERIOD_CHECK = {T_CAMPAIGN, T_NIGHTMARE, T_PRESENTATION, T_RULES}
CARD_TYPES_NO_TEXT = {T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT}
CARD_TYPES_NO_TEXT_BACK = {T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT,
                           T_PRESENTATION}
CARD_SPHERES_NO_TEXT = {S_REGION}
CARD_TYPES_SHADOW = {T_ENEMY, T_LOCATION, T_OBJECTIVE, T_OBJECTIVE_ALLY,
                     T_OBJECTIVE_HERO, T_OBJECTIVE_LOCATION, T_SHIP_ENEMY,
                     T_SHIP_OBJECTIVE, T_TREACHERY}
CARD_TYPES_SHADOW_ENCOUNTER = {T_ALLY, T_ATTACHMENT, T_EVENT}
CARD_TYPES_NO_FLAVOUR = {T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT,
                         T_PRESENTATION, T_RULES}
CARD_SPHERES_NO_FLAVOUR = {S_REGION}
CARD_TYPES_NO_FLAVOUR_BACK = {T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT,
                              T_NIGHTMARE, T_PRESENTATION, T_RULES}
CARD_TYPES_NO_PRINTED_NUMBER = {T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT,
                                T_PRESENTATION, T_RULES}
CARD_TYPES_NO_PRINTED_NUMBER_BACK = {T_CAMPAIGN, T_FULL_ART_LANDSCAPE,
                                     T_FULL_ART_PORTRAIT, T_NIGHTMARE,
                                     T_PRESENTATION, T_RULES}
CARD_TYPES_ENCOUNTER_SET_NUMBER = {T_ENCOUNTER_SIDE_QUEST, T_ENEMY, T_LOCATION,
                                   T_OBJECTIVE, T_OBJECTIVE_ALLY,
                                   T_OBJECTIVE_HERO, T_OBJECTIVE_LOCATION,
                                   T_SHIP_ENEMY, T_SHIP_OBJECTIVE, T_TREACHERY}
CARD_SPHERES_NO_ENCOUNTER_SET_NUMBER = {S_BOON, S_BURDEN, S_NOICON}
CARD_TYPES_ENCOUNTER_SET_ICON = {T_CAMPAIGN, T_ENCOUNTER_SIDE_QUEST, T_ENEMY,
                                 T_LOCATION, T_NIGHTMARE, T_OBJECTIVE,
                                 T_OBJECTIVE_ALLY, T_OBJECTIVE_HERO,
                                 T_OBJECTIVE_LOCATION, T_QUEST, T_SHIP_ENEMY,
                                 T_SHIP_OBJECTIVE, T_TREACHERY, T_TREASURE}
CARD_SPHERES_NO_ENCOUNTER_SET_ICON = {S_BOON, S_NOICON}
CARD_TYPES_FLAGS = {F_NOTRAITS:
                    {T_ALLY, T_ENEMY, T_HERO, T_LOCATION, T_OBJECTIVE_ALLY,
                     T_OBJECTIVE_HERO, T_OBJECTIVE_LOCATION, T_SHIP_ENEMY,
                     T_SHIP_OBJECTIVE, T_TREASURE},
                    F_PROMO: {T_HERO},
                    F_BLUERING:
                    {T_ENCOUNTER_SIDE_QUEST, T_ENEMY, T_LOCATION, T_OBJECTIVE,
                     T_OBJECTIVE_ALLY, T_OBJECTIVE_HERO, T_OBJECTIVE_LOCATION,
                     T_SHIP_ENEMY, T_SHIP_OBJECTIVE, T_TREACHERY},
                    F_GREENRING:
                    {T_ENCOUNTER_SIDE_QUEST, T_ENEMY, T_LOCATION, T_OBJECTIVE,
                     T_OBJECTIVE_ALLY, T_OBJECTIVE_HERO, T_OBJECTIVE_LOCATION,
                     T_SHIP_ENEMY, T_SHIP_OBJECTIVE, T_TREACHERY},
                    F_REDRING:
                    {T_ENCOUNTER_SIDE_QUEST, T_ENEMY, T_LOCATION, T_OBJECTIVE,
                     T_OBJECTIVE_ALLY, T_OBJECTIVE_HERO, T_OBJECTIVE_LOCATION,
                     T_SHIP_ENEMY, T_SHIP_OBJECTIVE, T_TREACHERY}}
CARD_TYPES_FLAGS_BACK = {F_NOTRAITS:
                         {T_ALLY, T_ENEMY, T_HERO, T_LOCATION,
                          T_OBJECTIVE_ALLY, T_OBJECTIVE_HERO,
                          T_OBJECTIVE_LOCATION, T_SHIP_ENEMY, T_SHIP_OBJECTIVE,
                          T_TREASURE},
                         F_PROMO: {T_HERO},
                         F_BLUERING:
                         {T_ENCOUNTER_SIDE_QUEST, T_ENEMY, T_LOCATION,
                          T_OBJECTIVE, T_OBJECTIVE_ALLY, T_OBJECTIVE_HERO,
                          T_OBJECTIVE_LOCATION, T_SHIP_ENEMY, T_SHIP_OBJECTIVE,
                          T_TREACHERY},
                         F_GREENRING:
                         {T_ENCOUNTER_SIDE_QUEST, T_ENEMY, T_LOCATION,
                          T_OBJECTIVE, T_OBJECTIVE_ALLY, T_OBJECTIVE_HERO,
                          T_OBJECTIVE_LOCATION, T_SHIP_ENEMY, T_SHIP_OBJECTIVE,
                          T_TREACHERY},
                         F_REDRING:
                         {T_ENCOUNTER_SIDE_QUEST, T_ENEMY, T_LOCATION,
                          T_OBJECTIVE, T_OBJECTIVE_ALLY, T_OBJECTIVE_HERO,
                          T_OBJECTIVE_LOCATION, T_SHIP_ENEMY, T_SHIP_OBJECTIVE,
                          T_TREACHERY}}
CARD_TYPES_NO_FLAGS = {F_STAR: {T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT,
                                T_PRESENTATION, T_RULES},
                       F_IGNORENAME: {T_FULL_ART_LANDSCAPE,
                                      T_FULL_ART_PORTRAIT, T_PRESENTATION,
                                      T_RULES},
                       F_IGNORERULES: {T_FULL_ART_LANDSCAPE,
                                       T_FULL_ART_PORTRAIT, T_PRESENTATION},
                       F_NOARTIST: {T_PRESENTATION, T_RULES},
                       F_NOCOPYRIGHT: {T_PRESENTATION, T_RULES}}
CARD_TYPES_NO_FLAGS_BACK = {
    F_STAR: {T_CAMPAIGN, T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT,
             T_NIGHTMARE, T_PRESENTATION, T_RULES},
    F_IGNORENAME: {T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT, T_PRESENTATION,
                   T_RULES},
    F_IGNORERULES: {T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT, T_PRESENTATION},
    F_NOARTIST: {T_CAMPAIGN, T_NIGHTMARE, T_PRESENTATION, T_RULES},
    F_NOCOPYRIGHT: {T_CAMPAIGN, T_NIGHTMARE, T_PRESENTATION, T_RULES}}
CARD_SPHERES_NO_FLAGS = {F_BLUERING: {S_CAVE, S_NOSTAT, S_REGION},
                         F_GREENRING: {S_CAVE, S_NOSTAT, S_REGION},
                         F_REDRING: {S_CAVE, S_NOSTAT, S_REGION}}
CARD_TYPES_ICONS = {T_ENEMY, T_LOCATION, T_OBJECTIVE, T_OBJECTIVE_ALLY,
                    T_OBJECTIVE_HERO, T_OBJECTIVE_LOCATION, T_SHIP_ENEMY,
                    T_SHIP_OBJECTIVE, T_TREACHERY}
CARD_SPHERES_NO_ICONS = {S_NOSTAT}
CARD_TYPES_NO_INFO = {T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT,
                      T_PRESENTATION, T_RULES}
CARD_TYPES_NO_INFO_BACK = {T_CAMPAIGN, T_FULL_ART_LANDSCAPE,
                           T_FULL_ART_PORTRAIT, T_NIGHTMARE, T_PRESENTATION,
                           T_RULES}
CARD_TYPES_NO_ARTIST = {T_PRESENTATION, T_RULES}
CARD_TYPES_NO_ARTIST_BACK = {T_CAMPAIGN, T_NIGHTMARE, T_PRESENTATION, T_RULES}
CARD_TYPES_NO_ARTWORK = {T_RULES}
CARD_TYPES_NO_ARTWORK_BACK = {T_CAMPAIGN, T_NIGHTMARE, T_PRESENTATION, T_RULES}
CARD_TYPES_EASY_MODE = {T_ENCOUNTER_SIDE_QUEST, T_ENEMY, T_LOCATION,
                        T_SHIP_ENEMY, T_TREACHERY}
CARD_SPHERES_NO_EASY_MODE = {S_BOON, S_BURDEN, S_CAVE, S_NOICON, S_NOSTAT,
                             S_REGION}
CARD_TYPES_ADDITIONAL_ENCOUNTER_SETS = {T_QUEST}
CARD_TYPES_ADVENTURE = {T_CAMPAIGN, T_OBJECTIVE, T_OBJECTIVE_ALLY,
                        T_OBJECTIVE_HERO, T_OBJECTIVE_LOCATION,
                        T_QUEST, T_SHIP_OBJECTIVE}
CARD_SPHERES_NO_ADVENTURE = {S_NOICON}
CARD_TYPES_SUBTITLE = {T_CAMPAIGN, T_OBJECTIVE, T_OBJECTIVE_ALLY,
                       T_OBJECTIVE_HERO, T_OBJECTIVE_LOCATION,
                       T_QUEST, T_SHIP_OBJECTIVE}
CARD_TYPES_NO_COLLECTION_ICON = {T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT,
                                 T_RULES}
CARD_TYPES_NO_COPYRIGHT = {T_PRESENTATION, T_RULES}
CARD_TYPES_DECK_RULES = {T_NIGHTMARE, T_QUEST}
CARD_TYPES_ONE_COPY = {T_CAMPAIGN, T_CONTRACT, T_ENCOUNTER_SIDE_QUEST,
                       T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT, T_HERO,
                       T_NIGHTMARE, T_OBJECTIVE_HERO, T_PLAYER_OBJECTIVE,
                       T_PRESENTATION, T_QUEST, T_RULES, T_TREASURE}
CARD_TYPES_THREE_COPIES = {T_ALLY, T_ATTACHMENT, T_EVENT, T_PLAYER_SIDE_QUEST}
CARD_TYPES_BOON = {T_ALLY, T_ATTACHMENT, T_EVENT, T_OBJECTIVE_ALLY}
CARD_TYPES_BOON_SPHERE = {T_ATTACHMENT, T_EVENT}
CARD_SPHERES_BOON = {S_BOON, S_BOONLEADERSHIP, S_BOONLORE, S_BOONSPIRIT,
                     S_BOONTACTICS}
CARD_TYPES_BURDEN = {T_ENCOUNTER_SIDE_QUEST, T_ENEMY, T_OBJECTIVE,
                     T_SHIP_ENEMY, T_TREACHERY}
CARD_TYPES_NIGHTMARE = {T_ENCOUNTER_SIDE_QUEST, T_ENEMY, T_LOCATION,
                        T_OBJECTIVE, T_QUEST, T_SHIP_ENEMY, T_TREACHERY}
CARD_TYPES_NOSTAT = {T_ENEMY}
CARD_TYPES_NO_DISCORD_CHANNEL = {T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT,
                                 T_PRESENTATION, T_RULES}
CARD_TYPES_NO_NAME_TAG = {T_CAMPAIGN, T_NIGHTMARE, T_PRESENTATION, T_RULES}
CARD_TYPES_PAGES = {T_PRESENTATION, T_RULES}

FLAGS = {F_ADDITIONALCOPIES, F_IGNORENAME, F_IGNORERULES, F_NOARTIST,
         F_NOCOPYRIGHT, F_NOTRAITS, F_PROMO, F_STAR, F_BLUERING, F_GREENRING,
         F_REDRING}
RING_FLAGS = {F_BLUERING, F_GREENRING, F_REDRING}
SPHERES = set()
SPHERES_CAMPAIGN = {S_SETUP}
SPHERES_OBJECTIVE = {S_NOICON}
SPHERES_PLAYER = {S_BAGGINS, S_FELLOWSHIP, S_LEADERSHIP, S_LORE, S_NEUTRAL,
                  S_SPIRIT, S_TACTICS}
SPHERES_PRESENTATION = {'Blue', 'Green', 'Purple', 'Red', 'Brown', 'Yellow',
                        'BlueNightmare', 'GreenNightmare', 'PurpleNightmare',
                        'RedNightmare', 'BrownNightmare', 'YellowNightmare'}
SPHERES_RULES = {S_BACK}
SPHERES_SHIP_OBJECTIVE = {S_UPGRADED}
SPHERES_SIDE_QUEST = {S_CAVE, S_NOPROGRESS, S_REGION, S_SMALLTEXTAREA}

COPY_STABLE_DATA_COMMAND = "rclone copy '{}' 'ALePStableData:/'"
DRAGNCARDS_PLAYER_CARDS_STAT_COMMAND = \
    '/home/webhost/python/AR/player_cards_stat.sh "{}" "{}" "{}"'
DRAGNCARDS_ALL_PLAYS_COMMAND = \
    '/home/webhost/python/AR/all_plays.sh "{}" "{}" "{}"'
DRAGNCARDS_PLAYS_STAT_COMMAND = \
    '/home/webhost/python/AR/plays_stat.sh "{}" "{}" "{}"'
DRAGNCARDS_QUESTS_STAT_COMMAND = \
    '/home/webhost/python/AR/quests_stat.sh "{}"'
DRAGNCARDS_FILES_COMMAND = '/home/webhost/python/AR/list_files.sh'
DRAGNCARDS_BUILD_STAT_COMMAND = \
    '/var/www/dragncards.com/dragncards/frontend/buildStat.sh'
DRAGNCARDS_BUILD_TRIGGER_COMMAND = \
    '/var/www/dragncards.com/dragncards/frontend/buildTrigger.sh'
DRAGNCARDS_IMAGES_FINISH_COMMAND = \
    '/var/www/dragncards.com/dragncards/frontend/imagesFinish.sh'
DRAGNCARDS_IMAGES_START_COMMAND = \
    '/var/www/dragncards.com/dragncards/frontend/imagesStart.sh'
DRAGNCARDS_MONITOR_IMAGES_UPLOAD_COMMAND = \
    '/var/www/dragncards.com/dragncards/frontend/monitorImagesUpload.sh'
GENERATE_DRAGNCARDS_COMMAND = './generate_dragncards.sh {}'
GIMP_COMMAND = '"{}" -i -b "({} 1 \\"{}\\" \\"{}\\")" -b "(gimp-quit 0)"'
MAGICK_COMMAND_CMYK = '"{}" mogrify -profile USWebCoatedSWOP.icc "{}{}*.jpg"'
MAGICK_COMMAND_JPG = '"{}" mogrify -format jpg "{}{}*.png"'
MAGICK_COMMAND_LOW = '"{}" mogrify -resize 600x600 -format jpg "{}{}*.png"'
MAGICK_COMMAND_MBPRINT_PDF = '"{}" convert "{}{}*o.jpg" "{}"'
MAGICK_COMMAND_RULES_PDF = '"{}" convert "{}{}*.jpg" "{}"'

JPG_PREVIEW_MIN_SIZE = 20000
JPG_300_MIN_SIZE = 50000
JPG_480_MIN_SIZE = 150000
JPG_800_MIN_SIZE = 1000000
JPG_300CMYK_MIN_SIZE = 1000000
JPG_800CMYK_MIN_SIZE = 4000000
PNG_300_MIN_SIZE = 50000
PNG_480_MIN_SIZE = 300000
PNG_800_MIN_SIZE = 2000000

DRAGNCARDS_MENU_LABEL = 'ALeP - Playtest'
EASY_PREFIX = 'Easy '
GENERATED_FOLDER = 'generated'
IMAGES_CUSTOM_FOLDER = 'custom'
IMAGES_ICONS_FOLDER = 'icons'
OCTGN_SET_XML = 'set.xml'
PLAYTEST_SUFFIX = '-Playtest'
SCRATCH_FOLDER = '_Scratch'
TEXT_CHUNK_FLAG = b'tEXt'

TAGS_WITH_NUMBERS_REGEX = r'\[[^\]]*[0-9][^\]]*\]'
ANCHORS_REGEX = (
    r'(?:[1-9][AB]|\b(?:[1-9][0-9][0-9]|[1-9][0-9]|[2-9]|0|X)\b'
    r'(?:\[pp\]| \[threat\]| \[attack\]| \[defense\]| \[willpower\]'
    r'| \[leadership\]| \[lore\]| \[spirit\]| \[tactics\])?'
    r'|\[unique\]|\[threat\]|\[attack\]|\[defense\]|\[willpower\]'
    r'|\[leadership\]|\[lore\]|\[spirit\]|\[tactics\]|\[baggins\]'
    r'|\[fellowship\]|\[sunny\]|\[cloudy\]|\[rainy\]|\[stormy\]|\[sailing\]'
    r'|\[eos\]|\[pp\])')
CARD_NAME_REFERENCE_REGEX = r'\[\[([^\]]+)\]\]'
DECK_PREFIX_REGEX = r'^[QN][A-Z0-9][A-Z0-9]\.[0-9][0-9]?(?:-|$)'
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
PNG480BLEED = 'png480Bleed'
PNG480DRAGNCARDSHQ = 'png480DragnCardsHQ'
PNG480NOBLEED = 'png480NoBleed'
PNG800BLEED = 'png800Bleed'
PNG800BLEEDMPC = 'png800BleedMPC'
PNG800BLEEDGENERIC = 'png800BleedGeneric'
PNG800NOBLEED = 'png800NoBleed'
PNG800PDF = 'png800PDF'
PNG800RULES = 'png800Rules'

CARD_BACKS = {'player': {'mpc': ['playerBackOfficialMPC.png',
                                 'playerBackUnofficialMPC.png'],
                         'dtc': ['playerBackOfficialDTC.jpg',
                                 'playerBackUnofficialDTC.jpg'],
                         'mbprint': ['playerBackOfficialMBPrint.jpg',
                                     'playerBackUnofficialMBPrint.jpg'],
                         'genericpng': ['playerBackOfficial.png',
                                        'playerBackUnofficial.png']},
              'encounter': {'mpc': ['encounterBackOfficialMPC.png',
                                    'encounterBackUnofficialMPC.png'],
                            'dtc': ['encounterBackOfficialDTC.jpg',
                                    'encounterBackUnofficialDTC.jpg'],
                            'mbprint': ['encounterBackOfficialMBPrint.jpg',
                                        'encounterBackUnofficialMBPrint.jpg'],
                            'genericpng': ['encounterBackOfficial.png',
                                           'encounterBackUnofficial.png']}}

DATA_PATH = 'Data'
DISCORD_PATH = 'Discord'
DOCS_PATH = 'Docs'
OUTPUT_PATH = 'Output'
PROJECT_PATH = 'Frogmorton'
RENDERER_PATH = 'Renderer'
TEMP_ROOT_PATH = 'Temp'
UTC_TIMESTAMP_PATH = 'utc_timestamp.txt'

CHOSEN_SETS_PATH = os.path.join(DATA_PATH, 'chosen_sets.json')
CONFIGURATION_PATH = 'configuration.yaml'
DISCORD_CARD_DATA_PATH = os.path.join(DISCORD_PATH, 'Data', 'card_data.json')
DISCORD_CARD_DATA_RAW_PATH = os.path.join(DISCORD_PATH, 'Data',
                                          'card_data_raw.json')
DISCORD_TIMESTAMPS_PATH = os.path.join(DISCORD_PATH, 'Data', 'timestamps.json')
DOWNLOAD_PATH = 'Download'
DOWNLOAD_TIME_PATH = os.path.join(DATA_PATH, 'download_time.txt')
DRAGNCARDS_FILES_CHECKSUM_PATH = os.path.join(DATA_PATH, 'dragncards_files.json')
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
SANITY_CHECK_PATH = os.path.join(DATA_PATH, 'sanity_check.txt')
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

DRIVE_TIMESTAMP_MAX_DIFF = 3660
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
    T_CAMPAIGN: 'Setup',
    T_CONTRACT: 'Side',
    T_NIGHTMARE: 'Setup',
    T_PLAYER_OBJECTIVE: 'Side',
    T_PRESENTATION: 'Setup',
    T_RULES: 'Setup'
}

CARD_TYPES_PLAYER_FRENCH = {
    T_ALLY, T_ATTACHMENT, T_CAMPAIGN, T_CONTRACT, T_EVENT, T_HERO,
    T_OBJECTIVE_ALLY, T_OBJECTIVE_HERO, T_PLAYER_OBJECTIVE,
    T_PLAYER_SIDE_QUEST, T_SHIP_OBJECTIVE, T_TREASURE}
CARD_TYPE_FRENCH_IDS = {
    T_ALLY: 401,
    T_ATTACHMENT: 403,
    T_CAMPAIGN: 411,
    T_CONTRACT: 418,
    T_ENCOUNTER_SIDE_QUEST: 413,
    T_ENEMY: 404,
    T_EVENT: 402,
    T_HERO: 400,
    T_LOCATION: 405,
    T_NIGHTMARE: 415,
    T_OBJECTIVE: 407,
    T_OBJECTIVE_ALLY: 409,
    T_OBJECTIVE_HERO: 416,
    T_OBJECTIVE_LOCATION: 417,
    T_PLAYER_OBJECTIVE: 419,
    T_PLAYER_SIDE_QUEST: 412,
    T_QUEST: 408,
    T_SHIP_ENEMY: 404,
    T_SHIP_OBJECTIVE: 414,
    T_TREACHERY: 406,
    T_TREASURE: 410
}
CARD_SUBTYPE_FRENCH_IDS = {
    S_BOON: 600,
    S_BOONLEADERSHIP: 600,
    S_BOONLORE: 600,
    S_BOONSPIRIT: 600,
    S_BOONTACTICS: 600,
    S_BURDEN: 601
}
CARD_SPHERE_FRENCH_IDS = {
    S_BAGGINS: 306,
    S_FELLOWSHIP: 305,
    S_LEADERSHIP: 300,
    S_LORE: 301,
    S_NEUTRAL: 304,
    S_SPIRIT: 302,
    S_TACTICS: 303
}
SPANISH = {
    T_ALLY: 'Aliado',
    T_ATTACHMENT: 'Vinculada',
    T_CAMPAIGN: 'Campa\u00f1a',
    T_CONTRACT: 'Contrato',
    T_ENCOUNTER_SIDE_QUEST: 'Misi\u00f3n Secundaria',
    T_ENEMY: 'Enemigo',
    T_EVENT: 'Evento',
    T_HERO: 'H\u00e9roe',
    T_LOCATION: 'Lugar',
    T_NIGHTMARE: 'Preparaci\u00f3n',
    T_OBJECTIVE: 'Objetivo',
    T_OBJECTIVE_ALLY: 'Objetivo-Aliado',
    T_OBJECTIVE_HERO: 'H\u00e9roe-Objetivo',
    T_OBJECTIVE_LOCATION: 'Lugar-Objetivo',
    T_PLAYER_OBJECTIVE: 'Objetivo de Jugador',
    T_PLAYER_SIDE_QUEST: 'Misi\u00f3n Secundaria',
    T_QUEST: 'Misi\u00f3n',
    T_SHIP_ENEMY: 'Barco-Enemigo',
    T_SHIP_OBJECTIVE: 'Barco-Objetivo',
    T_TREACHERY: 'Traici\u00f3n',
    T_TREASURE: 'Tesoro'
}
NUMBER_TRANSLATIONS = {
    '2' : {
        L_ENGLISH: ['two'],
        L_FRENCH: ['deux'],
        L_GERMAN: ['zwei'],
        L_ITALIAN: ['due'],
        L_POLISH: ['dwa'],
        L_PORTUGUESE: ['duas', 'dois'],
        L_SPANISH: ['dos']
    },
    '3' : {
        L_ENGLISH: ['three'],
        L_FRENCH: ['trois'],
        L_GERMAN: ['drei'],
        L_ITALIAN: ['tre'],
        L_POLISH: ['trzy'],
        L_PORTUGUESE: ['três'],
        L_SPANISH: ['tres']
    }
}
RESTRICTED_TRANSLATION = {
    L_ENGLISH: 'Restricted',
    L_FRENCH: 'Restreint',
    L_GERMAN: 'Eingeschränkt',
    L_ITALIAN: 'Limitato',
    L_POLISH: 'Ograniczenie',
    L_PORTUGUESE: 'Restrito',
    L_SPANISH: 'Restringido'
}

KNOWN_BOOKS = {
    L_ENGLISH: [
        'The Hobbit', 'The Fellowship of the Ring', 'The Two Towers',
        'The Return of the King', 'The Silmarillion', 'The Fall of Gondolin'],
    L_FRENCH: [
        'Le Hobbit', 'La Communauté de l’Anneau', 'Les Deux Tours',
        'Le Retour du Roi', 'Le Silmarillion', 'La Chute de Gondolin'],
    L_GERMAN: [
        'Der kleine Hobbit', 'Die Gefährten', 'Die zwei Türme',
        'Die Rückkehr des Königs', 'Das Silmarillion',
        'Der Fall von Gondolin'],
    L_ITALIAN: [
        'Lo Hobbit', 'La Compagnia dell’Anello', 'Le Due Torri',
        'Il Ritorno del Re', 'Il Silmarillion', 'La Caduta di Gondolin'],
    L_POLISH: [
        'Hobbit', 'Drużyna Pierścienia', 'Dwie Wieże',
        'Powrót Króla', 'Silmarillion', 'Upadek Gondolinu'],
    L_SPANISH: [
        'El Hobbit', 'La Comunidad del Anillo', 'Las Dos Torres',
        'El Retorno del Rey', 'El Silmarillion', 'La Caída de Gondolin'],
    }
AUXILIARY_TRAITS = {
    'Abroad', 'Basic', 'Broken', 'Corrupt', 'Cursed', 'Elite', 'Epic',
    'Massing', 'Reforged', 'Standard', 'Suspicious', 'Upgraded'}
DESCRIPTIVE_LAST_TRAITS = {
    'Boar', 'Boar Clan', 'Captain', 'Flame', 'Lieutenant', 'Olog-hai',
    'Raven', 'Raven Clan', 'Uruk-hai', 'Wolf', 'Wolf Clan', 'Wolf-cult'}
DESCRIPTIVE_TRAITS = {
    'Advice', 'Archer', 'Assault', 'Attack', 'Besieger', 'Black Speech',
    'Brigand', 'Burglar', 'Capture', 'Captured', 'Champion', 'Clue',
    'Corruption', 'Craftsman', 'Cultist', 'Damaged', 'Defense', 'Despair',
    'Disaster', 'Distracting', 'Doom', 'Enchantment', 'Escape', 'Fear',
    'Fellowship', 'Food', 'Found', 'Gossip', 'Guardian', 'Hazard', 'Healer',
    'Hungry', 'Inferno', 'Information', 'Instrument', 'Key', 'Light', 'Master',
    'Mathom', 'Minstrel', 'Mission', 'Mustering', 'Night', 'Panic', 'Party',
    'Pillager', 'Pipe', 'Pipeweed', 'Plot', 'Poison', 'Raider', 'Ranger',
    'Record', 'Refuge', 'Ring-bearer', 'Ruffian', 'Sack', 'Scheme', 'Scout',
    'Scroll', 'Search', 'Servant', 'Shadow', 'Sharkey', 'Shirriff', 'Sorcerer',
    'Sorcery', 'Spy', 'Staff', 'Stalking', 'Steward', 'Summoned', 'Summoner',
    'Tantrum', 'Thaurdir', 'Thug', 'Time', 'Tools', 'Traitor', 'Treasure',
    'Villain', 'Warden', 'Warrior', 'Weather', 'Wound'}
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
    'Balrog', 'Beorning', 'Body', 'Chicken', 'Corsair', 'Dale', 'Dorwinion',
    'Dragon', 'Dúnedain', 'Dunland', 'Dwarf', 'Eagle', 'Easterling', 'Ent',
    'Giant', 'Goblin', 'Gollum', 'Gondor', 'Harad', 'Hobbit', 'Huorn',
    'Insect', 'Istari', 'Legend', 'Mearas', 'Nameless', 'Noldor',
    'Oathbreaker', 'Outlands', 'Pony', 'Rat', 'Rohan', 'Silvan', 'Snaga',
    'Spider', 'Spirit', 'Tentacle', 'Tree', 'Troll', 'Uruk', 'Warg',
    'Werewolf', 'Wight', 'Woodman', 'Wose', 'Wraith'}
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
    'Gift', 'Morgul', 'Mount', 'Ring', 'Signal', 'Skill', 'Song', 'Spell',
    'Tale', 'Title', 'Trap', 'Weapon'}
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
    'Ignore',
    'It',
    'Its',
    'Immune',
    'Increase',
    'Instead',
    'Limit',
    'Locations',
    'Make',
    'Move',
    'Name',
    'Non-unique',
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
    'Those',
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

TRANSLATION_MATCH = [
    [r'Valour Resource Action', {
        L_ENGLISH: r'\bValour Resource Action',
        L_FRENCH: r'\[Vaillance\] \[Ressource\] Action\b',
        L_GERMAN: r'\bEhrenvolle Ressourcenaktion\b',
        L_ITALIAN: r'\bAzione Valorosa di Risorse\b',
        L_POLISH: r'\bAkcja Zasob\u00f3w M\u0119stwa\b',
        L_PORTUGUESE: r'\bA\u00e7\u00e3o Valorosa de Recursos\b',
        L_SPANISH: r'\bAcci\u00f3n de Recursos de Valor\b'}],
    [r'Valour Planning Action', {
        L_ENGLISH: r'\bValour Planning Action',
        L_FRENCH: r'\[Vaillance\] \[Organisation\] Action\b',
        L_GERMAN: r'\bEhrenvolle Planungsaktion\b',
        L_ITALIAN: r'\bAzione Valorosa di Pianificazione\b',
        L_POLISH: r'\bAkcja Planowania M\u0119stwa\b',
        L_PORTUGUESE: r'\bA\u00e7\u00e3o Valorosa de Planejamento\b',
        L_SPANISH: r'\bAcci\u00f3n de Planificaci\u00f3n de Valor\b'}],
    [r'Valour Quest Action', {
        L_ENGLISH: r'\bValour Quest Action',
        L_FRENCH: r'\[Vaillance\] \[Qu\u00eate\] Action\b',
        L_GERMAN: r'\bEhrenvolle Abenteueraktion\b',
        L_ITALIAN: r'\bAzione Valorosa di Ricerca\b',
        L_POLISH: r'\bAkcja Wyprawy M\u0119stwa\b',
        L_PORTUGUESE: r'\bA\u00e7\u00e3o Valorosa de Miss\u00e3o\b',
        L_SPANISH: r'\bAcci\u00f3n de Misi\u00f3n de Valor\b'}],
    [r'Valour Travel Action', {
        L_ENGLISH: r'\bValour Travel Action',
        L_FRENCH: r'\[Vaillance\] \[Voyage\] Action\b',
        L_GERMAN: r'\bEhrenvolle Reiseaktion\b',
        L_ITALIAN: r'\bAzione Valorosa di Viaggio\b',
        L_POLISH: r'\bAkcja Podr\u00f3\u017cy M\u0119stwa\b',
        L_PORTUGUESE: r'\bA\u00e7\u00e3o Valorosa de Viagem\b',
        L_SPANISH: r'\bAcci\u00f3n de Viaje de Valor\b'}],
    [r'Valour Encounter Action', {
        L_ENGLISH: r'\bValour Encounter Action',
        L_FRENCH: r'\[Vaillance\] \[Rencontre\] Action\b',
        L_GERMAN: r'\bEhrenvolle Begegnungsaktion\b',
        L_ITALIAN: r'\bAzione Valorosa di Incontri\b',
        L_POLISH: r'\bAkcja Spotkania M\u0119stwa\b',
        L_PORTUGUESE: r'\bA\u00e7\u00e3o Valorosa de Encontro\b',
        L_SPANISH: r'\bAcci\u00f3n de Encuentro de Valor\b'}],
    [r'Valour Combat Action', {
        L_ENGLISH: r'\bValour Combat Action',
        L_FRENCH: r'\[Vaillance\] \[Combat\] Action\b',
        L_GERMAN: r'\bEhrenvolle Kampfaktion\b',
        L_ITALIAN: r'\bAzione Valorosa di Combattimento\b',
        L_POLISH: r'\bAkcja Walki M\u0119stwa\b',
        L_PORTUGUESE: r'\bA\u00e7\u00e3o Valorosa de Combate\b',
        L_SPANISH: r'\bAcci\u00f3n de Combate de Valor\b'}],
    [r'Valour Refresh Action', {
        L_ENGLISH: r'\bValour Refresh Action',
        L_FRENCH: r'\[Vaillance\] \[Restauration\] Action\b',
        L_GERMAN: r'\bEhrenvolle Auffrischungsaktion\b',
        L_ITALIAN: r'\bAzione Valorosa di Riordino\b',
        L_POLISH: r'\bAkcja Odpoczynku M\u0119stwa\b',
        L_PORTUGUESE: r'\bA\u00e7\u00e3o Valorosa de Renova\u00e7\u00e3o\b',
        L_SPANISH: r'\bAcci\u00f3n de Recuperaci\u00f3n de Valor\b'}],
    [r'Valour Action', {
        L_ENGLISH: r'\bValour Action',
        L_FRENCH: r'\[Vaillance\] Action\b',
        L_GERMAN: r'\bEhrenvolle Aktion\b',
        L_ITALIAN: r'\bAzione Valorosa\b',
        L_POLISH: r'\bAkcja M\u0119stwa\b',
        L_PORTUGUESE: r'\bA\u00e7\u00e3o Valorosa\b',
        L_SPANISH: r'\bAcci\u00f3n de Valor\b'}],
    [r'Resource Action', {
        L_ENGLISH: r'\bResource Action',
        L_FRENCH: r'\[Ressource\] Action\b',
        L_GERMAN: r'\bRessourcenaktion\b',
        L_ITALIAN: r'\bAzione di Risorse\b',
        L_POLISH: r'\bAkcja Zasob\u00f3w\b',
        L_PORTUGUESE: r'\bA\u00e7\u00e3o de Recursos\b',
        L_SPANISH: r'\bAcci\u00f3n de Recursos\b'}],
    [r'Planning Action', {
        L_ENGLISH: r'\bPlanning Action',
        L_FRENCH: r'\[Organisation\] Action\b',
        L_GERMAN: r'\bPlanungsaktion\b',
        L_ITALIAN: r'\bAzione di Pianificazione\b',
        L_POLISH: r'\bAkcja Planowania\b',
        L_PORTUGUESE: r'\bA\u00e7\u00e3o de Planejamento\b',
        L_SPANISH: r'\bAcci\u00f3n de Planificaci\u00f3n\b'}],
    [r'Quest Action', {
        L_ENGLISH: r'\bQuest Action',
        L_FRENCH: r'\[Qu\u00eate\] Action\b',
        L_GERMAN: r'\bAbenteueraktion\b',
        L_ITALIAN: r'\bAzione di Ricerca\b',
        L_POLISH: r'\bAkcja Wyprawy\b',
        L_PORTUGUESE: r'\bA\u00e7\u00e3o de Miss\u00e3o\b',
        L_SPANISH: r'\bAcci\u00f3n de Misi\u00f3n\b'}],
    [r'Travel Action', {
        L_ENGLISH: r'\bTravel Action',
        L_FRENCH: r'\[Voyage\] Action\b',
        L_GERMAN: r'\bReiseaktion\b',
        L_ITALIAN: r'\bAzione di Viaggio\b',
        L_POLISH: r'\bAkcja Podr\u00f3\u017cy\b',
        L_PORTUGUESE: r'\bA\u00e7\u00e3o de Viagem\b',
        L_SPANISH: r'\bAcci\u00f3n de Viaje\b'}],
    [r'Encounter Action', {
        L_ENGLISH: r'\bEncounter Action',
        L_FRENCH: r'\[Rencontre\] Action\b',
        L_GERMAN: r'\bBegegnungsaktion\b',
        L_ITALIAN: r'\bAzione di Incontri\b',
        L_POLISH: r'\bAkcja Spotkania\b',
        L_PORTUGUESE: r'\bA\u00e7\u00e3o de Encontro\b',
        L_SPANISH: r'\bAcci\u00f3n de Encuentro\b'}],
    [r'Combat Action', {
        L_ENGLISH: r'\bCombat Action',
        L_FRENCH: r'\[Combat\] Action\b',
        L_GERMAN: r'\bKampfaktion\b',
        L_ITALIAN: r'\bAzione di Combattimento\b',
        L_POLISH: r'\bAkcja Walki\b',
        L_PORTUGUESE: r'\bA\u00e7\u00e3o de Combate\b',
        L_SPANISH: r'\bAcci\u00f3n de Combate\b'}],
    [r'Refresh Action', {
        L_ENGLISH: r'\bRefresh Action',
        L_FRENCH: r'\[Restauration\] Action\b',
        L_GERMAN: r'\bAuffrischungsaktion\b',
        L_ITALIAN: r'\bAzione di Riordino\b',
        L_POLISH: r'\bAkcja Odpoczynku\b',
        L_PORTUGUESE: r'\bA\u00e7\u00e3o de Renova\u00e7\u00e3o\b',
        L_SPANISH: r'\bAcci\u00f3n de Recuperaci\u00f3n\b'}],
    [r'Action', {
        L_ENGLISH: r'\bAction',
        L_FRENCH: r'\bAction\b',
        L_GERMAN: r'\bAktion\b',
        L_ITALIAN: r'\bAzione\b',
        L_POLISH: r'\bAkcja\b',
        L_PORTUGUESE: r'\bA\u00e7\u00e3o\b',
        L_SPANISH: r'\bAcci\u00f3n\b'}],
    [r'When Revealed', {
        L_ENGLISH: r'\bRevealed',
        L_FRENCH: r'\bUne fois r\u00e9v\u00e9l\u00e9e\b',
        L_GERMAN: r'\bWenn aufgedeckt\b',
        L_ITALIAN: r'\bQuando Rivelata\b',
        L_POLISH: r'\bPo odkryciu\b',
        L_PORTUGUESE: r'\bEfeito Revelado\b',
        L_SPANISH: r'\bAl ser revelada\b'}],
    [r'Forced', {
        L_ENGLISH: r'\bForced',
        L_FRENCH: r'\bForc\u00e9\b',
        L_GERMAN: r'\bErzwungen\b',
        L_ITALIAN: r'\bObbligato\b',
        L_POLISH: r'\bWymuszony\b',
        L_PORTUGUESE: r'\bEfeito For\u00e7ado\b',
        L_SPANISH: r'\bObligado\b'}],
    [r'Valour Response', {
        L_ENGLISH: r'\bValour Response',
        L_FRENCH: r'\[Vaillance\] R\u00e9ponse\b',
        L_GERMAN: r'\bEhrenvolle Reaktion\b',
        L_ITALIAN: r'\bRisposta Valorosa\b',
        L_POLISH: r'\bOdpowied\u017a M\u0119stwa\b',
        L_PORTUGUESE: r'\bResposta Valorosa\b',
        L_SPANISH: r'\bRespuesta de Valor\b'}],
    [r'Response', {
        L_ENGLISH: r'\bResponse',
        L_FRENCH: r'\bR\u00e9ponse\b',
        L_GERMAN: r'\bReaktion\b',
        L_ITALIAN: r'\bRisposta\b',
        L_POLISH: r'\bOdpowied\u017a\b',
        L_PORTUGUESE: r'\bResposta\b',
        L_SPANISH: r'\bRespuesta\b'}],
    [r'Travel', {
        L_ENGLISH: r'\b(Travel|Journey)',
        L_FRENCH: r'\b(Trajet|Voyage)\b',
        L_GERMAN: r'\bReise',
        L_ITALIAN: r'\bViaggio\b',
        L_POLISH: r'\b[Pp]odr\u00f3\u017cy?\b',
        L_PORTUGUESE: r'\bViagem\b',
        L_SPANISH: r'\bViaje\b'}],
    [r'Resolution', {
        L_ENGLISH: r'\b(Resolution|Conclusion)',
        L_FRENCH: r'\bR\u00e9solution\b',
        L_GERMAN: r'\bAufl\u00f6sung\b',
        L_ITALIAN: r'\bRisoluzione\b',
        L_POLISH: r'\bNast\u0119pstwa\b',
        L_PORTUGUESE: r'\bResolu\u00e7\u00e3o\b',
        L_SPANISH: r'\bResoluci\u00f3n\b'}],
    [r'Setup', {
        L_ENGLISH: r'\b(Setup|Set Up|Setting Up|Staging)',
        L_FRENCH: r'\bMise en place\b',
        L_GERMAN: r'\bVorbereitung\b',
        L_ITALIAN: r'\bPreparazione\b',
        L_POLISH: r'\bPrzygotowanie\b(?! polskiej)',
        L_PORTUGUESE: r'\bPrepara\u00e7\u00e3o\b',
        L_SPANISH: r'\bPreparaci\u00f3n\b'}],
    [r'Condition', {
        L_ENGLISH: r'\bCondition',
        L_FRENCH: r'\bCondition\b',
        L_GERMAN: r'\bZustand\b',
        L_ITALIAN: r'\bCondizione\b',
        L_POLISH: r'\bStan\b',
        L_PORTUGUESE: r'\bCondi\u00e7\u00e3o\b',
        L_SPANISH: r'\bEstado\b'}]
]

CARD_COLUMNS = {}
DATA = []
SETS = {}
SHEET_IDS = {}

ACCENTS = set()
ALL_CARD_NAMES = {L_ENGLISH: set()}
ALL_ENCOUNTER_SET_NAMES = set()
ALL_NAMES = set()
ALL_SCRATCH_CARD_NAMES = set()
ALL_SCRATCH_TRAITS = set()
ALL_SET_AND_QUEST_NAMES = set()
ALL_TRAITS = set()
CHOSEN_SETS = []
FLAVOUR_BOOKS = {}
FLAVOUR_WARNINGS = {'missing_quotes': set(), 'redundant_quotes': set()}
FOUND_SCRATCH_SETS = set()
FOUND_SETS = set()
IMAGE_CACHE = {}
JSON_CACHE = {}
PRE_SANITY_CHECK = {'name': {}, 'ref': {}, 'flavour': {}, 'shadow': {}}
RINGSDB_COOKIES = {}
SELECTED_CARDS = set()
TRANSLATIONS = {}
XML_CACHE = {}


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

class GoogleDriveError(Exception):
    """ Google Drive error.
    """


class TLSAdapter(requests.adapters.HTTPAdapter):  # pylint: disable=R0903
    """ TLS adapter to workaround SSL errors.
    """

    def init_poolmanager(self, connections, maxsize, block=False, **_):
        """ Create and initialize the urllib3 PoolManager.
        """
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = urllib3.poolmanager.PoolManager(  # pylint: disable=W0201
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
    str_value = str(value)
    try:
        if (str_value.isdigit() or
                (len(str_value) > 1 and str_value[0] == '-' and
                 str_value[1:].isdigit()) or
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
        open_tag = '[{}]'.format(tag)
        close_tag = '[/{}]'.format(tag)
        diff = text_copy.count(open_tag) - text_copy.count(close_tag)
        if diff > 0:
            errors.append(open_tag)
            continue

        if diff < 0:
            errors.append(close_tag)
            continue

        text = text_copy
        text = re.sub(r'\[{}\].+?\[\/{}\]'.format(tag, tag), '', text,  # pylint: disable=W1308
                      flags=re.DOTALL)
        if open_tag in text:
            errors.append(open_tag)

        if close_tag in text:
            errors.append(close_tag)

    for tag in ('lotr', 'lotrheader', 'size'):
        open_tag = '[{}]'.format(tag)
        close_tag = '[/{}]'.format(tag)
        diff = text_copy.count('[{} '.format(tag)) - text_copy.count(close_tag)
        if diff > 0:
            errors.append(open_tag)
            continue

        if diff < 0:
            errors.append(close_tag)
            continue

        text = text_copy
        text = re.sub(r'\[{} .+?\[\/{}\]'.format(tag, tag), '', text,  # pylint: disable=W1308
                      flags=re.DOTALL)
        if '[{} '.format(tag) in text:
            errors.append(open_tag)

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
    text = text.replace('[br]', '')
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


def _update_card_text(text, lang=L_ENGLISH, skip_rules=False,  # pylint: disable=R0915
                      fix_linebreaks=True):
    """ Update card text for RingsDB, Hall of Beorn, French and Spanish DBs.
    """
    text = str(text)
    if lang == L_SPANISH and not skip_rules:
        text = re.sub(r'\b(Acci\u00f3n)( de Recursos| de Planificaci\u00f3n'
                      r'| de Misi\u00f3n| de Viaje| de Encuentro| de Combate'
                      r'| de Recuperaci\u00f3n)?( de Valor)?:',
                      '[b]\\1\\2\\3[/b]:', text)
        text = re.sub(r'\b(Al ser revelada|Obligado|Respuesta de Valor'
                      r'|Respuesta|Viaje|Sombra|Resoluci\u00f3n):',
                      '[b]\\1[/b]:', text)
        text = re.sub(r'\b(Preparaci\u00f3n)( \([^\)]+\))?:', '[b]\\1[/b]\\2:',
                      text)
        text = re.sub(r'\b(Estado)\b', '[bi]\\1[/bi]', text)
    if lang == L_FRENCH and not skip_rules:
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
    elif lang == L_ENGLISH and not skip_rules:
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
    text = text.replace('[br]', '')
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

    text = text.replace('<b><b>', '<b>')
    text = text.replace('</b></b>', '</b>')
    text = text.replace('<i><i>', '<i>')
    text = text.replace('</i></i>', '</i>')
    text = text.replace('<b><i><b><i>', '<b><i>')
    text = text.replace('</i></b></i></b>', '</i></b>')

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
    text = _update_card_text(text, lang=L_FRENCH)
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
            if filename not in {'seproject', '.gitignore', 'desktop.ini'}:
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
    if conf['frenchdb_csv'] and L_FRENCH not in conf['languages']:
        conf['languages'].append(L_FRENCH)

    if conf['spanishdb_csv'] and L_SPANISH not in conf['languages']:
        conf['languages'].append(L_SPANISH)

    conf['output_languages'] = [lang for lang in conf['outputs']
                                if conf['outputs'][lang]]
    conf['nobleed_300'] = {}
    conf['nobleed_480'] = {}
    conf['nobleed_800'] = {}

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
                                     or 'octgn' in conf['outputs'][lang])
        conf['nobleed_480'][lang] = 'dragncards_hq' in conf['outputs'][lang]
        conf['nobleed_800'][lang] = 'rules_pdf' in conf['outputs'][lang]

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
    sheets = [SET_SHEET, CARD_SHEET, SCRATCH_SHEET]
    for lang in set(conf['languages']).difference(set([L_ENGLISH])):
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
            changes = True
            path = os.path.join(DOWNLOAD_PATH, '{}.json'.format(sheet))
            with open(path, 'w', encoding='utf-8') as fobj:
                fobj.write(res)

    if changes:
        with open(SHEETS_JSON_PATH, 'w', encoding='utf-8') as fobj:
            json.dump(new_checksums, fobj)

        with open(DOWNLOAD_TIME_PATH, 'w', encoding='utf-8') as fobj:
            fobj.write(utc_time)

    logging.info('...Downloading cards spreadsheet from Google Sheets (%ss)',
                 round(time.time() - timestamp, 3))
    return changes


def _verify_drive_timestamp(folder_path):
    """ Verify Google Drive timestamp of a particular folder.
    """
    path = os.path.join(folder_path, UTC_TIMESTAMP_PATH)
    try:
        with open(path, 'r', encoding='utf-8') as fobj:
            timestamp = fobj.read().strip()

        diff = (datetime.utcnow().timestamp() -
                datetime.strptime(timestamp, '%a %d %b %H:%M:%S %Z %Y')
                .timestamp())
    except Exception as exc:
        raise GoogleDriveError(
            "Can't read Google Drive timestamp for {} folder"
            .format(os.path.split(folder_path)[-1])) from exc

    if diff > DRIVE_TIMESTAMP_MAX_DIFF:
        raise GoogleDriveError(
            'No Google Drive updates for {} folder for {} seconds'
            .format(os.path.split(folder_path)[-1], int(diff)))


def upload_stable_data():
    """ Upload the latest stable data to Google Drive.
    """
    logging.info('Uploading the latest stable data to Google Drive...')
    timestamp = time.time()

    cmd = COPY_STABLE_DATA_COMMAND.format(
        os.path.join(DOWNLOAD_PATH, '{}.json'.format(CARD_SHEET)))
    run_cmd(cmd)

    logging.info('...Uploading the latest stable data to Google Drive (%ss)',
                 round(time.time() - timestamp, 3))


def read_stable_data(conf):
    """ Read the latest stable data.
    """
    logging.info('Reading the latest stable data...')
    timestamp = time.time()

    if conf['verify_drive_timestamp']:
        _verify_drive_timestamp(conf['stable_data_path'])

    stable_data_path = os.path.join(conf['stable_data_path'],
                                    '{}.json'.format(CARD_SHEET))
    try:
        with open(stable_data_path, 'r', encoding='utf-8') as fobj:
            stable_data = fobj.read()
    except Exception as exc:
        raise SheetError("Can't read stable data from {}"
                         .format(stable_data_path)) from exc

    JSON_CACHE[CARD_SHEET] = json.loads(stable_data)
    download_path = os.path.join(DOWNLOAD_PATH,
                                 '{}.json'.format(CARD_SHEET))
    shutil.copyfile(stable_data_path, download_path)

    try:
        with open(SHEETS_JSON_PATH, 'r', encoding='utf-8') as fobj:
            checksums = json.load(fobj)
    except Exception:
        checksums = {}

    checksums[CARD_SHEET] = hashlib.md5(
        stable_data.encode('utf-8')).hexdigest()

    with open(SHEETS_JSON_PATH, 'w', encoding='utf-8') as fobj:
        json.dump(checksums, fobj)

    logging.info('...Reading the latest stable data (%ss)',
                 round(time.time() - timestamp, 3))


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


def _extract_all_card_names(data, lang):
    """ Collect all card names from the spreadsheet.
    """
    ALL_CARD_NAMES[lang] = set()
    for row in data:
        if row[CARD_TYPE] in CARD_TYPES_NO_NAME_TAG:
            continue

        if not row[CARD_SCRATCH]:
            clean_value = _clean_value(row[CARD_NAME])
            if clean_value:
                ALL_CARD_NAMES[lang].add(clean_value)

            clean_value = _clean_value(row[CARD_SIDE_B])
            if clean_value:
                ALL_CARD_NAMES[lang].add(clean_value)

    if lang == L_ENGLISH:
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
                    row[CARD_ADVENTURE] not in {'[space]', '[nobr]'} and
                    row[CARD_TYPE] != T_CAMPAIGN):
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
    ALL_NAMES.update(ALL_CARD_NAMES[L_ENGLISH])
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
    value = re.sub(r'(?<![A-Za-z0-9])[-—](?=[0-9]|X\b)', '–', value)
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

    value = value.replace('[[', '\t')
    value = value.replace(']]', '\r')
    while True:
        value_old = value
        value = re.sub(r'[“”]([^\[]*)\]', '"\\1]', value)
        value = re.sub(r'’([^\[]*)\]', "'\\1]", value)
        value = re.sub(r'…([^\[]*)\]', "...\\1]", value)
        value = re.sub(r'—([^\[]*)\]', "---\\1]", value)
        value = re.sub(r'–([^\[]*)\]', "--\\1]", value)
        if value == value_old:
            break

    value = value.replace('\t', '[[')
    value = value.replace('\r', ']]')

    value = re.sub(r' +(?=\n)', '', value)
    value = re.sub(r' +', ' ', value)

    if len(value) == 1:
        value = value.upper()

    if value == '':
        value = None

    return value


def _get_regex(value):
    """ Get a regex to match the string value.
    """
    value_regex = re.escape(value)
    if re.search(r'^\w', value):
        value_regex = r'\b' + value_regex

    if re.search(r'\w$', value):
        value_regex = value_regex + r'\b'

    return value_regex


def get_similar_names_regex(value, card_names, scratch_card_names=None):
    """ Get similar card names regex.
    """
    value_regex = _get_regex(value)

    res = {n for n in card_names if re.search(value_regex, n) and value != n}
    if scratch_card_names:
        res_scratch = {n for n in scratch_card_names
                       if re.search(value_regex, n) and value != n}
        res.update(res_scratch)

    names = []
    for name in res:
        name_regex = _get_regex(name)
        name_regex = r'(?<!\[bi\])' + name_regex
        names.append(name_regex)

    return names


def parse_flavour(value, lang, value_id=None):  # pylint: disable=R0912,R0915
    """ Parse the flavour text and detect possible issues.
    """
    errors = []
    value = value.strip()
    value = re.sub(r'\n +', '\n', value)
    original_value = value
    if lang in {L_GERMAN, L_POLISH, L_SPANISH}:
        value = re.sub(r'\[right\](\s*[—–].+?)(?:\[\/right\])?$', '\\1', value,
                       flags=re.DOTALL)

    if lang in {L_FRENCH, L_POLISH}:
        value = re.sub(r'([—–])\[nobr\]([^—–]+)$', '\\1 \\2', value)

    if (lang not in {L_GERMAN, L_ITALIAN} and
            (re.search(r'\s-', value) or re.search(r'-\s', value))):
        errors.append('Incorrectly used short dashes')

    if lang in {L_ITALIAN, L_SPANISH}:
        default_separator = '\n'
    else:
        default_separator = ' '

    parts = re.split(r'[—–]', value[::-1], maxsplit=1)
    parts = [p[::-1] for p in parts][::-1]
    if len(parts) == 2:
        if parts[0].endswith('\n\n'):
            separator = '\n\n'
        elif parts[0].endswith('\n'):
            separator = '\n'
        elif parts[0].endswith('[nobr]'):
            separator = '[nobr]'
        else:
            separator = default_separator
    else:
        separator = default_separator

    if lang in {L_ENGLISH, L_ITALIAN, L_SPANISH}:
        false_split = '—' not in value and re.search(r'\s–\s[^–]+$', value)
    else:
        false_split = False

    parts = [p.strip() for p in parts]
    if len(parts) == 2 and parts[1].count(', ') > 1:
        parts = [original_value]
        if not false_split:
            errors.append('Possibly too many commas in the source')

    source_book = None
    if len(parts) == 2:  # pylint: disable=R1702
        source_parts = parts[1][::-1].split(' ,', maxsplit=1)
        source_parts = [p[::-1].strip() for p in source_parts][::-1]
        source_book = re.sub(r'\[[^\]]+\]$', '', source_parts[-1])
        if not KNOWN_BOOKS.get(lang):
            parts = [original_value]
        elif source_book not in KNOWN_BOOKS[lang]:
            parts = [original_value]
            if not false_split:
                errors.append('Possibly unknown source book: {}'.format(
                    source_book))
        else:
            if lang == L_ENGLISH and value_id:
                FLAVOUR_BOOKS[value_id] = KNOWN_BOOKS[lang].index(source_book)

            if len(source_parts) == 2:
                parts = [parts[0], source_parts[0], source_parts[1]]

            parts[0] = re.sub(r'\[nobr\]$', '',
                              re.sub(r'^\[nobr\]', '', parts[0])).strip()
            parts[1] = re.sub(r'\[nobr\]$', '',
                              re.sub(r'^\[nobr\]', '', parts[1])).strip()
            parts[1] = re.sub(r'\s+', '[nobr]', parts[1])
            if len(parts) > 2:
                parts[2] = re.sub(r'\[nobr\]$', '',
                                  re.sub(r'^\[nobr\]', '', parts[2])).strip()
                parts[2] = re.sub(r'\s+', '[nobr]', parts[2])

            if lang == L_POLISH:
                if not parts[0].startswith('“'):
                    parts[0] = '“{}'.format(parts[0])

                if not parts[0].endswith('”'):
                    parts[0] = '{}”'.format(parts[0])
            else:
                if len(source_parts) == 2:
                    if (not parts[0].startswith('“') and
                            not parts[0].endswith('”')):
                        if lang == L_ENGLISH:
                            errors.append('Possibly missing double quotes')
                            if value_id:
                                FLAVOUR_WARNINGS['missing_quotes'].add(
                                    value_id)
                        elif (not value_id or
                              value_id not in
                              FLAVOUR_WARNINGS['missing_quotes']):
                            errors.append('Possibly missing double quotes')
                elif (parts[0].startswith('“') or
                      parts[0].endswith('”')):
                    if lang == L_ENGLISH:
                        errors.append('Possibly redundant double quotes')
                        if value_id:
                            FLAVOUR_WARNINGS['redundant_quotes'].add(value_id)
                    elif (not value_id or
                          value_id not in
                          FLAVOUR_WARNINGS['redundant_quotes']):
                        errors.append('Possibly redundant double quotes')

            if lang == L_ENGLISH:
                parts[0] = parts[0].replace('—', '–')
            elif lang == L_ITALIAN:
                parts[0] = parts[0].replace('—', '-')

    if lang != L_ENGLISH and KNOWN_BOOKS.get(lang) and value_id:
        if source_book and source_book in KNOWN_BOOKS[lang]:
            book_index = KNOWN_BOOKS[lang].index(source_book)
        else:
            book_index = -1

        if book_index != FLAVOUR_BOOKS.get(value_id, -1):
            errors.append('Different source book from the English version')

    if lang == L_GERMAN:
        dash = '–'
    else:
        dash = '—'

    if lang in {L_FRENCH, L_POLISH}:
        dash = '{}[nobr]'.format(dash)

    if (lang in {L_GERMAN, L_POLISH, L_SPANISH} and
            separator in {'\n\n', '\n'} and len(parts) >= 2):
        dash = '[right]{}'.format(dash)
        parts[-1] = '{}[/right]'.format(parts[-1])

    if lang in {L_ENGLISH, L_GERMAN}:
        parts[0] = parts[0].replace('—', '–')
    elif lang in {L_FRENCH, L_SPANISH}:
        parts[0] = parts[0].replace('–', '—')
    elif lang == L_ITALIAN:
        parts[0] = parts[0].replace('–', '-')

    return (errors, parts, separator, dash)


def _clean_data(conf, data, lang):  # pylint: disable=R0912,R0914,R0915
    """ Clean data from the spreadsheet.
    """
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

        if (lang == L_ENGLISH and card_name and  # pylint: disable=R0916
                (not row[CARD_SCRATCH] or
                 card_name not in ALL_SCRATCH_TRAITS) and
                row[CARD_TYPE] not in CARD_TYPES_NO_NAME_TAG and
                not (row[CARD_FLAGS] and
                     F_IGNORENAME in extract_flags(
                         row[CARD_FLAGS], conf['ignore_ignore_flags']))):
            card_name_regex = _get_regex(card_name)
            card_name_regex = r'(?<!\[bi\])\b' + card_name_regex
        else:
            card_name_regex = None

        if (lang == L_ENGLISH and card_name_back and  # pylint: disable=R0916
                (not row[CARD_SCRATCH] or
                 card_name_back not in ALL_SCRATCH_TRAITS) and
                row[BACK_PREFIX + CARD_TYPE] not in CARD_TYPES_NO_NAME_TAG and
                not (row[BACK_PREFIX + CARD_FLAGS] and
                     F_IGNORENAME in
                     extract_flags(row[BACK_PREFIX + CARD_FLAGS],
                                   conf['ignore_ignore_flags']))):
            card_name_regex_back = _get_regex(card_name_back)
            card_name_regex_back = r'(?<!\[bi\])\b' + card_name_regex_back
        else:
            card_name_regex_back = None

        for key, value in row.items():
            if not isinstance(value, str):
                continue

            value = _clean_value(value)
            if not value:
                row[key] = value
                continue

            if ALL_CARD_NAMES.get(lang):
                refs = re.findall(CARD_NAME_REFERENCE_REGEX, value)
                for ref in refs:
                    if ref not in ALL_CARD_NAMES[lang]:
                        error = (
                            'Invalid reference [[{}]] in {} column: there is '
                            'no card with that name'.format(
                                ref, key.replace(BACK_PREFIX,
                                                 BACK_PREFIX_LOG)))
                        PRE_SANITY_CHECK['ref'].setdefault(
                            (row[ROW_COLUMN], row[CARD_SCRATCH], lang),
                            []).append(error)

            value = re.sub(CARD_NAME_REFERENCE_REGEX, '\\1', value)

            if card_name_regex:
                if key == CARD_TEXT and re.search(card_name_regex, value):
                    prepared_value = value
                    similar_names = get_similar_names_regex(
                        card_name, ALL_CARD_NAMES[L_ENGLISH],
                        row[CARD_SCRATCH] and ALL_SCRATCH_CARD_NAMES or None)
                    for similar_name in similar_names:
                        prepared_value = re.sub(similar_name, '',
                                                prepared_value)

                    if re.search(card_name_regex, prepared_value):
                        error = (
                            'Hardcoded card name "{}" instead of [name] in '
                            'text'.format(card_name))
                        PRE_SANITY_CHECK['name'].setdefault(
                            (row[ROW_COLUMN], row[CARD_SCRATCH]),
                            []).append(error)
                elif (key == CARD_SHADOW and
                      re.search(card_name_regex, value)):
                    prepared_value = value
                    similar_names = get_similar_names_regex(
                        card_name, ALL_CARD_NAMES[L_ENGLISH],
                        row[CARD_SCRATCH] and ALL_SCRATCH_CARD_NAMES or None)
                    for similar_name in similar_names:
                        prepared_value = re.sub(similar_name, '',
                                                prepared_value)

                    if re.search(card_name_regex, prepared_value):
                        error = (
                            'Hardcoded card name "{}" instead of [name] in '
                            'shadow'.format(card_name))
                        PRE_SANITY_CHECK['name'].setdefault(
                            (row[ROW_COLUMN], row[CARD_SCRATCH]),
                            []).append(error)

            if card_name_regex_back:
                if (key == BACK_PREFIX + CARD_TEXT and
                        re.search(card_name_regex_back, value)):
                    prepared_value = value
                    similar_names = get_similar_names_regex(
                        card_name_back, ALL_CARD_NAMES[L_ENGLISH],
                        row[CARD_SCRATCH] and ALL_SCRATCH_CARD_NAMES or None)
                    for similar_name in similar_names:
                        prepared_value = re.sub(similar_name, '',
                                                prepared_value)

                    if re.search(card_name_regex_back, prepared_value):
                        error = (
                            'Hardcoded card name "{}" instead of [name] in '
                            'text back'.format(card_name_back))
                        PRE_SANITY_CHECK['name'].setdefault(
                            (row[ROW_COLUMN], row[CARD_SCRATCH]),
                            []).append(error)
                elif (key == BACK_PREFIX + CARD_SHADOW and
                          re.search(card_name_regex_back, value)):
                    prepared_value = value
                    similar_names = get_similar_names_regex(
                        card_name_back, ALL_CARD_NAMES[L_ENGLISH],
                        row[CARD_SCRATCH] and ALL_SCRATCH_CARD_NAMES or None)
                    for similar_name in similar_names:
                        prepared_value = re.sub(similar_name, '',
                                                prepared_value)

                    if re.search(card_name_regex_back, prepared_value):
                        error = (
                            'Hardcoded card name "{} instead of [name] in '
                            'shadow back'.format(card_name_back))
                        PRE_SANITY_CHECK['name'].setdefault(
                            (row[ROW_COLUMN], row[CARD_SCRATCH]),
                            []).append(error)

            if key.startswith(BACK_PREFIX):
                value = value.replace('[name]', card_name_back)
            else:
                value = value.replace('[name]', card_name)

            if key in {CARD_FLAVOUR, BACK_PREFIX + CARD_FLAVOUR}:
                errors, parts, separator, dash = parse_flavour(
                    value, lang, (row[CARD_ID], key))
                if errors and lang in conf['output_languages']:
                    for error in errors:
                        error = '{} in {}'.format(
                            error,
                            'flavour' if key == CARD_FLAVOUR else 'flavour back')
                        PRE_SANITY_CHECK['flavour'].setdefault(
                            (row[ROW_COLUMN], row[CARD_SCRATCH], lang),
                            []).append(error)

                if len(parts) == 3:
                    value = '{}{}{}{},[nobr]{}'.format(
                        parts[0],
                        separator,
                        dash,
                        parts[1],
                        parts[2])
                elif len(parts) == 2:
                    value = '{}{}{}{}'.format(
                        parts[0],
                        separator,
                        dash,
                        parts[1])
                else:
                    value = parts[0]

            if key in {CARD_SHADOW, BACK_PREFIX + CARD_SHADOW}:
                field = 'shadow' if key == CARD_SHADOW else 'shadow back'
                if (lang == L_ENGLISH and
                        not re.search(r'^(?:\[[^\]]+\])?Shadow(?:\[[^\]]+\])?:',
                                      value)):
                    value = 'Shadow: {}'.format(value)
                    error = ('Appending missing "Shadow:" text to the {} '
                             'effect'.format(field))
                    PRE_SANITY_CHECK['shadow'].setdefault(
                        (row[ROW_COLUMN], row[CARD_SCRATCH], lang),
                        []).append(error)
                elif (lang == L_FRENCH and
                        not re.search(r'^(?:\[[^\]]+\])?Ombre(?:\[[^\]]+\])? ?:',
                                      value)):
                    value = 'Ombre: {}'.format(value)
                    error = ('Appending missing "Ombre:" text to the {} '
                             'effect'.format(field))
                    PRE_SANITY_CHECK['shadow'].setdefault(
                        (row[ROW_COLUMN], row[CARD_SCRATCH], lang),
                        []).append(error)
                elif (lang == L_GERMAN and
                        not re.search(r'^(?:\[[^\]]+\])?Schatten(?:\[[^\]]+\])? ?:',
                                      value)):
                    value = 'Schatten: {}'.format(value)
                    error = ('Appending missing "Schatten:" text to the {} '
                             'effect'.format(field))
                    PRE_SANITY_CHECK['shadow'].setdefault(
                        (row[ROW_COLUMN], row[CARD_SCRATCH], lang),
                        []).append(error)
                elif (lang == L_ITALIAN and
                        not re.search(r'^(?:\[[^\]]+\])?Ombra(?:\[[^\]]+\])? ?:',
                                      value)):
                    value = 'Ombra: {}'.format(value)
                    error = ('Appending missing "Ombra:" text to the {} '
                             'effect'.format(field))
                    PRE_SANITY_CHECK['shadow'].setdefault(
                        (row[ROW_COLUMN], row[CARD_SCRATCH], lang),
                        []).append(error)
                elif (lang == L_POLISH and
                        not re.search(r'^(?:\[[^\]]+\])?Cień(?:\[[^\]]+\])? ?:',
                                      value)):
                    value = 'Cień: {}'.format(value)
                    error = ('Appending missing "Cień:" text to the {} '
                             'effect'.format(field))
                    PRE_SANITY_CHECK['shadow'].setdefault(
                        (row[ROW_COLUMN], row[CARD_SCRATCH], lang),
                        []).append(error)
                elif (lang == L_SPANISH and
                        not re.search(r'^(?:\[[^\]]+\])?Sombra(?:\[[^\]]+\])? ?:',
                                      value)):
                    value = 'Sombra: {}'.format(value)
                    error = ('Appending missing "Sombra:" text to the {} '
                             'effect'.format(field))
                    PRE_SANITY_CHECK['shadow'].setdefault(
                        (row[ROW_COLUMN], row[CARD_SCRATCH], lang),
                        []).append(error)

            row[key] = value

        if row.get(CARD_TYPE) == T_RULES and row.get(CARD_VICTORY) == 'auto':
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


def is_doubleside(card_type, card_type_back):
    """ Check whether the card is double-sided or not.
    """
    if card_type in CARD_TYPES_DOUBLESIDE_DEFAULT:
        return True

    if card_type == card_type_back == T_CONTRACT:
        return True

    if card_type == card_type_back == T_PLAYER_OBJECTIVE:
        return True

    return False


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

        if ((row[CARD_QUANTITY] is None or row[CARD_QUANTITY] in {'0', 0}) and
                row[CARD_TYPE] == T_RULES):
            row[CARD_QUANTITY] = 1

        if row[CARD_TYPE] == T_ALIAS_SIDE_QUEST:
            row[CARD_TYPE] = T_ENCOUNTER_SIDE_QUEST

        if row[BACK_PREFIX + CARD_TYPE] == T_ALIAS_SIDE_QUEST:
            row[BACK_PREFIX + CARD_TYPE] = T_ENCOUNTER_SIDE_QUEST

        if (row[CARD_TYPE] in CARD_TYPES_DOUBLESIDE_DEFAULT and
                row[BACK_PREFIX + CARD_TYPE] is None):
            row[BACK_PREFIX + CARD_TYPE] = row[CARD_TYPE]

        if (row[CARD_TYPE] in CARD_TYPES_DOUBLESIDE_DEFAULT and
                row[CARD_SIDE_B] is None):
            row[CARD_SIDE_B] = row[CARD_NAME]

        row[BACK_PREFIX + CARD_NAME] = row[CARD_SIDE_B]

        if (not is_doubleside(row[CARD_TYPE], row[BACK_PREFIX + CARD_TYPE]) and  # pylint: disable=R0916
                row[CARD_TYPE] not in CARD_TYPES_NO_PRINTED_NUMBER and
                row[CARD_TYPE] not in CARD_TYPES_NO_PRINTED_NUMBER_BACK and
                row[BACK_PREFIX + CARD_TYPE] is not None and
                row[CARD_NUMBER] is not None and
                row[CARD_PRINTED_NUMBER] is None and
                row[BACK_PREFIX + CARD_PRINTED_NUMBER] is None):
            row[CARD_PRINTED_NUMBER] = '{}a'.format(row[CARD_NUMBER])
            row[BACK_PREFIX + CARD_PRINTED_NUMBER] = '{}b'.format(
                row[CARD_NUMBER])
            row[CARD_PRINTED_NUMBER_AUTO] = True


def _set_encounter_set_numbers(data):
    """ Set encounter set numbers.
    """
    encounter_sets = {}
    for row in data:
        if (row[CARD_SET] in SETS and  # pylint: disable=R0916
                row[CARD_ENCOUNTER_SET] is not None and
                is_positive_int(row[CARD_QUANTITY]) and
                ((row[CARD_TYPE] in CARD_TYPES_ENCOUNTER_SET_NUMBER and
                  row[CARD_SPHERE] not in
                  CARD_SPHERES_NO_ENCOUNTER_SET_NUMBER) or
                 (row[BACK_PREFIX + CARD_TYPE] in
                  CARD_TYPES_ENCOUNTER_SET_NUMBER and
                  row[BACK_PREFIX + CARD_SPHERE] not in
                  CARD_SPHERES_NO_ENCOUNTER_SET_NUMBER))):
            row[CARD_ENCOUNTER_SET_NUMBER_START] = (
                encounter_sets.get((row[CARD_SET],
                                    row[CARD_ENCOUNTER_SET]), 0) + 1)
            encounter_sets[(row[CARD_SET], row[CARD_ENCOUNTER_SET])] = (
                encounter_sets.get((row[CARD_SET],
                                    row[CARD_ENCOUNTER_SET]), 0) +
                row[CARD_QUANTITY])
        else:
            row[CARD_ENCOUNTER_SET_NUMBER_START] = None
            row[CARD_ENCOUNTER_SET_TOTAL] = None

    for row in data:
        if (row[CARD_SET] in SETS and  # pylint: disable=R0916
                row[CARD_ENCOUNTER_SET] is not None and
                is_positive_int(row[CARD_QUANTITY]) and
                ((row[CARD_TYPE] in CARD_TYPES_ENCOUNTER_SET_NUMBER and
                  row[CARD_SPHERE] not in
                  CARD_SPHERES_NO_ENCOUNTER_SET_NUMBER) or
                 (row[BACK_PREFIX + CARD_TYPE] in
                  CARD_TYPES_ENCOUNTER_SET_NUMBER and
                  row[BACK_PREFIX + CARD_SPHERE] not in
                  CARD_SPHERES_NO_ENCOUNTER_SET_NUMBER))):
            row[CARD_ENCOUNTER_SET_TOTAL] = encounter_sets.get(
                (row[CARD_SET], row[CARD_ENCOUNTER_SET]), 0)


def _update_selected_rows(data):
    """ Update selected rows.
    """
    selected_sets = {row[CARD_SELECTED] for row in data
                     if row[CARD_SELECTED] in SETS and
                     row[CARD_SET] in SETS and
                     not row[CARD_SCRATCH]}
    scratch_sets = {row[CARD_SELECTED] for row in data
                    if row[CARD_SELECTED] in SETS and row[CARD_SET] in SETS and
                    row[CARD_SCRATCH]}
    intersected_sets = selected_sets.intersection(scratch_sets)
    selected_scratch_sets = scratch_sets.difference(intersected_sets)
    selected_card_numbers = {}
    for row in data:
        if row[CARD_SELECTED] in SETS and row[CARD_SET] in SETS:
            if row[CARD_SCRATCH] and row[CARD_SELECTED] in intersected_sets:
                continue

            if (row[CARD_TYPE] not in CARD_TYPES_NO_COLLECTION_ICON and
                    row[CARD_COLLECTION_ICON] is None):
                if SETS.get(row[CARD_SET], {}).get(SET_COLLECTION_ICON):
                    row[CARD_COLLECTION_ICON] = (
                        SETS[row[CARD_SET]][SET_COLLECTION_ICON])
                elif SETS.get(row[CARD_SET], {}).get(SET_NAME):
                    row[CARD_COLLECTION_ICON] = SETS[row[CARD_SET]][SET_NAME]

            if (row[CARD_TYPE] not in CARD_TYPES_NO_COPYRIGHT and
                    row[CARD_COPYRIGHT] is None):
                if SETS.get(row[CARD_SET], {}).get(SET_COPYRIGHT):
                    row[CARD_COPYRIGHT] = SETS[row[CARD_SET]][SET_COPYRIGHT]

            if (row[CARD_TYPE] not in CARD_TYPES_NO_PRINTED_NUMBER and
                    row[CARD_PRINTED_NUMBER] is None):
                row[CARD_PRINTED_NUMBER] = row[CARD_NUMBER]

            if (row[CARD_TYPE] not in CARD_TYPES_NO_PRINTED_NUMBER_BACK and
                    row[BACK_PREFIX + CARD_TYPE] is not None and
                    row[BACK_PREFIX + CARD_PRINTED_NUMBER] is None):
                row[BACK_PREFIX + CARD_PRINTED_NUMBER] = row[CARD_NUMBER]

            row[CARD_SET] = row[CARD_SELECTED]
            row[CARD_SET_NAME] = SETS[row[CARD_SET]].get(SET_NAME, '')
            row[CARD_NUMBER] = selected_card_numbers.get(row[CARD_SELECTED], 1)
            selected_card_numbers[row[CARD_SELECTED]] = row[CARD_NUMBER] + 1

    return selected_sets, selected_scratch_sets


def _skip_row(row):
    """ Check whether a row should be skipped or not.
    """
    return row[CARD_SET] in {'0', 0} or row[CARD_ID] in {'0', 0}


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


def extract_data(conf):  # pylint: disable=R0912,R0915
    """ Extract data from the spreadsheet.
    """
    logging.info('Extracting data from the spreadsheet...')
    timestamp = time.time()

    CARD_COLUMNS.clear()
    SETS.clear()
    FOUND_SETS.clear()
    FOUND_SCRATCH_SETS.clear()
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

    data = _read_sheet_json(CARD_SHEET)
    if data:
        CARD_COLUMNS.update(_extract_column_names(data[0]))
        data = _transform_to_dict(data)
        for row in data:
            row[CARD_SCRATCH] = None

        DATA.extend(data)

    data = _read_sheet_json(SCRATCH_SHEET)
    if data:
        if not CARD_COLUMNS:
            CARD_COLUMNS.update(_extract_column_names(data[0]))

        data = _transform_to_dict(data)
        for row in data:
            row[CARD_SCRATCH] = 1

        DATA.extend(data)

    DATA[:] = [row for row in DATA if not _skip_row(row)]
    PRE_SANITY_CHECK['name'] = {}
    PRE_SANITY_CHECK['ref'] = {}
    PRE_SANITY_CHECK['flavour'] = {}
    PRE_SANITY_CHECK['shadow'] = {}
    FLAVOUR_BOOKS.clear()
    FLAVOUR_WARNINGS['missing_quotes'] = set()
    FLAVOUR_WARNINGS['redundant_quotes'] = set()
    _extract_all_card_names(DATA, L_ENGLISH)
    _clean_data(conf, DATA, L_ENGLISH)

    SELECTED_CARDS.update({row[CARD_ID] for row in DATA if row[CARD_SELECTED]})
    FOUND_SETS.update({row[CARD_SET] for row in DATA
                       if row[CARD_SET] in SETS and not row[CARD_SCRATCH]})
    scratch_sets = {row[CARD_SET] for row in DATA
                    if row[CARD_SET] in SETS and row[CARD_SCRATCH]}
    intersected_sets = FOUND_SETS.intersection(scratch_sets)
    FOUND_SCRATCH_SETS.update(scratch_sets.difference(intersected_sets))
    for row in DATA:
        if row[CARD_SCRATCH] and row[CARD_SET] in intersected_sets:
            row[CARD_SET] = '[filtered set]'

    _update_data(DATA)
    DATA[:] = sorted(DATA, key=lambda row: (
        row[CARD_SET_RINGSDB_CODE],
        is_positive_or_zero_int(row[CARD_NUMBER])
        and int(row[CARD_NUMBER]) or 0,
        str(row[CARD_NUMBER]),
        str(row[CARD_NAME])))
    _set_encounter_set_numbers(DATA)
    if conf['selected_only']:
        selected_sets, selected_scratch_sets = _update_selected_rows(DATA)
        FOUND_SETS.update(selected_sets)
        FOUND_SCRATCH_SETS.update(selected_scratch_sets)

    _extract_all_set_and_quest_names(DATA)
    _extract_all_encounter_set_names(DATA)
    _extract_all_traits(DATA)
    _extract_all_names()
    _extract_all_accents()
    card_types = {row[CARD_ID]: row[CARD_TYPE] for row in DATA}

    for lang in conf['languages']:
        if lang == L_ENGLISH:
            continue

        TRANSLATIONS[lang] = {}
        data = _read_sheet_json(lang)
        if data:
            data = _transform_to_dict(data)
            for row in data:
                row[CARD_SCRATCH] = None

            _extract_all_card_names(data, lang)
            _clean_data(conf, data, lang)
            for row in data:
                if row[CARD_ID] in TRANSLATIONS[lang]:
                    logging.error(
                        'Duplicate card ID %s for row #%s in %s translations, '
                        'ignoring', row[CARD_ID], row[ROW_COLUMN], lang)
                else:
                    if (card_types.get(row[CARD_ID]) in
                            CARD_TYPES_DOUBLESIDE_DEFAULT and
                            row[CARD_SIDE_B] is None):
                        row[CARD_SIDE_B] = row[CARD_NAME]

                    row[BACK_PREFIX + CARD_NAME] = row[CARD_SIDE_B]
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
        chosen_sets.update(s for s in FOUND_SETS if not SETS[s][SET_IGNORE])

    if 'all_scratch' in conf['set_ids']:
        chosen_sets.update(s for s in FOUND_SCRATCH_SETS
                           if not SETS[s][SET_IGNORE])

    unknown_sets = (set(conf['set_ids']) - set(SETS.keys()) -
                    set(['all', 'all_scratch']))
    for unknown_set in unknown_sets:
        logging.error('Unknown set_id in configuration: %s', unknown_set)

    chosen_sets = list(chosen_sets)
    chosen_sets = [s for s in chosen_sets if s not in conf['ignore_set_ids']]
    chosen_sets = [[SETS[s][SET_ID], SETS[s][SET_NAME]] for s in chosen_sets]
    CHOSEN_SETS[:] = chosen_sets
    with open(CHOSEN_SETS_PATH, 'w', encoding='utf-8') as obj:
        res = json.dumps(chosen_sets, ensure_ascii=False)
        obj.write(res)

    logging.info('...Getting all sets to work on (%ss)',
                 round(time.time() - timestamp, 3))
    return chosen_sets


def extract_flags(value, ignore_flags=False):
    """ Extract flags from a string value.
    """
    flags = [f.strip() for f in
             str(value or '').replace(';', '\n').split('\n') if f.strip()]
    if ignore_flags:
        flags = [f for f in flags if f not in {F_IGNORENAME, F_IGNORERULES}]

    return flags


def _verify_period(value):
    """ Verify period at the end of the paragraph.
    """
    if not value:
        return True

    res = True
    paragraphs = value.split('\n\n')
    for pos, paragraph in enumerate(paragraphs):
        paragraph = (paragraph.replace('[vspace]', '').replace('[br]', '')
                     .strip())
        if not paragraph:
            continue

        paragraph = paragraph.replace('[/size]', '')
        if pos != len(paragraphs) - 1:
            paragraph = paragraph.replace(':', '.')

        if not (re.search(
                    r'\.\)?”? ?(?:\[\/b\]|\[\/i\]|\[\/bi\])?$', paragraph) or
                re.search(
                    r'\.”\) ?(?:\[\/b\]|\[\/i\]|\[\/bi\])?$', paragraph)):
            res = False
            break

    return res


def is_capitalized(word):
    """ Check whether the word is capitalized or not.
    """
    res = word and (word[0] != word[0].lower() or
                    re.match(r'^[0-9_]', word[0]))
    return res


def _get_capitalization_errors(text):  # pylint: disable=R0912
    """ Detect capitalization errors.
    """
    errors = []
    if text in {'[space]', '[nobr]'}:
        return errors

    text = re.sub(r'\[[^\]]+\]', '', text)
    text = text.replace(' son of ', ' sonof_ ')
    parts = text.split(' ')
    parts = [re.sub(r'^[…“’]', '',
                    re.sub(r'[,.?!”’…]$', '', p)) for p in parts
             if p not in {'-', '+'}]
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
                  r'.+?\[\/i\](?:\[[^\]]+\])*(?:\n\n|$)', '\\1',
                  text, flags=re.DOTALL)

    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
    if not paragraphs:
        return errors

    for paragraph in paragraphs:
        paragraph = paragraph.replace('\n', ' ')
        if re.search(r'limit once per',
                     re.sub(r'\(Limit once per .+\.\)”?$', '', paragraph),
                     flags=re.IGNORECASE):
            errors.append('use "(Limit once per _.)" format')

        if re.search(r'limit (?:twice|two times|2 times) per',
                     re.sub(r'\(Limit twice per .+\.\)”?$', '', paragraph),
                     flags=re.IGNORECASE):
            errors.append('use "(Limit twice per _.)" format')

        if re.search(r'limit (?:thrice|three times|3 times) per',
                     re.sub(r'\(Limit 3 times per .+\.\)”?$', '', paragraph),
                     flags=re.IGNORECASE):
            errors.append('use "(Limit 3 times per _.)" format')

        if ' to travel here' in paragraph:
            errors.append('redundant "to travel here" statement')

        if re.search(r' he (?:commit|controls|deals|(?:just )?discard|'
                     'is eliminated|must|owns|puts|raises)', paragraph):
            errors.append('"they" not "he"')

        if ' he or she' in paragraph:
            errors.append('"they" not "he or she"')

        if re.search(r' his (?:(?:eligible )?characters|choice|control|'
                     'deck|discard pile|hand|hero|out-of-play deck|own|'
                     'play area|threat)', paragraph):
            errors.append('"their" not "his"')

        if ' his or her' in paragraph:
            errors.append('"their" not "his or her"')

        if 'engaged with him' in paragraph or 'in front of him' in paragraph:
            errors.append('"them" not "him"')

        if ' him or her' in paragraph:
            errors.append('"them" not "him or her"')

        if re.search(r'encounter deck[^.]+from the top of the encounter deck',
                     paragraph):
            errors.append('redundant "from the top of the encounter deck" '
                          'statement')

        if re.search(r'encounter deck[^.]+from the encounter deck', paragraph):
            errors.append('redundant "from the encounter deck" statement')

        if re.search(r'discards? (?:[^ ]+ )?cards? from the top of the '
                     'encounter deck', paragraph, flags=re.IGNORECASE):
            errors.append('"from the encounter deck" not "from the top of the '
                          'encounter deck"')

        if re.search(r' gets? [^+–]', paragraph):
            errors.append('"gain" not "get" a non-stat modification')

        if re.search(r' gains? [+–]', paragraph):
            errors.append('"get" not "gain" a stat modification')

        if re.search(r'discards? . cards? at random', paragraph,
                     flags=re.IGNORECASE):
            errors.append('use "discard(s) ... random card(s)" format')

        if re.search(r'\(Counts as a (?:\[bi\])?Condition', paragraph):
            errors.append('use "While attached ... counts as a {Condition} '
                          'attachment with the text:" format')

        if ' by this effect' in paragraph:
            errors.append('"this way" not "by this effect"')

        match = re.search(r'may trigger this (action|response)',
                          paragraph, flags=re.IGNORECASE)
        if match:
            errors.append('"may trigger this effect" not "may trigger this {}"'
                          .format(match.groups()[0]))

        if re.search(r'\(any player may trigger this effect',
                     paragraph, flags=re.IGNORECASE):
            errors.append('use "Any player may trigger this effect" '
                          '(without parenthesis)')

        if ('cannot be chosen as the current quest'
                in paragraph.replace('cannot be chosen as the current quest '
                                     'during the quest phase', '')):
            errors.append('use "cannot be chosen as the current quest during '
                          'the quest phase"')

        if 'active quest' in paragraph:
            errors.append('"current quest" not "active quest"')

        if 'current quest stage' in paragraph:
            errors.append('"current quest" not "current quest stage"')

        if re.search(r'adds? [0-9X](?:\[pp\])? resources? to ',
                     re.sub(r'adds? [0-9X](?:\[pp\])? resources? to [^.]+ '
                            r'pool', '', paragraph, flags=re.IGNORECASE),
                     flags=re.IGNORECASE):
            errors.append('use "place(s) ... resource token(s) on" format')

        if re.search(r'adds? [0-9X](?:\[pp\])? resource tokens? to [^.]+ pool',
                     paragraph, flags=re.IGNORECASE):
            errors.append('use "add(s) ... resource(s) to ... resource pool" '
                          'format')
        elif re.search(r'adds? [0-9X](?:\[pp\])? resource tokens? to ',
                       paragraph, flags=re.IGNORECASE):
            errors.append('use "place(s) ... resource token(s) on" format')

        if re.search(r'places? [0-9X](?:\[pp\])? resources? on [^.]+ pool',
                     paragraph, flags=re.IGNORECASE):
            errors.append('use "add(s) ... resource(s) to ... resource pool" '
                          'format')
        elif re.search(r'places? [0-9X](?:\[pp\])? resources? on ',
                       paragraph, flags=re.IGNORECASE):
            errors.append('use "place(s) ... resource token(s) on" format')

        if re.search(
                r'places? [0-9X](?:\[pp\])? resource tokens? on [^.]+ pool',
                paragraph, flags=re.IGNORECASE):
            errors.append('use "add(s) ... resource(s) to ... resource pool" '
                          'format')

        if 'per player' in re.sub(r'limit [^.]+\.', '', paragraph,
                                  flags=re.IGNORECASE):
            errors.append('"[pp]" tag not "per player" text')

        if 'step is completed' in paragraph.replace('complete rules', ''):
            errors.append('redundant "is completed" statement')
        elif 'step is complete' in paragraph.replace('complete rules', ''):
            errors.append('redundant "is complete" statement')
        elif re.search(r'\bcomplete[ds]?\b',
                       paragraph.replace('complete rules', ''),
                       flags=re.IGNORECASE):
            errors.append('"defeat" not "complete"')
        elif re.search(r'explore (?:this |a quest )?stage', paragraph,
                       flags=re.IGNORECASE):
            errors.append('"defeat stage" not "explore stage"')
        elif re.search(r'stage (?:is|is not|cannot be) explored', paragraph):
            errors.append('"defeat stage" not "explore stage"')
        elif re.search(r'quest (?:is|is not|cannot be) explored', paragraph):
            errors.append('"defeat quest" not "explore quest"')
        elif re.search(r'\b(?:clear|cleared)\b', paragraph,
                       flags=re.IGNORECASE):
            errors.append('"defeat" not "clear"')

        if re.search(r'play only after',
                     paragraph, flags=re.IGNORECASE):
            errors.append('"Response: At the end of" not "play only after"')

        if 'cancelled' in paragraph:
            errors.append('"canceled" not "cancelled"')

        match = re.search(
            r' (leadership|lore|spirit|tactics|baggins|fellowship)\b',
            paragraph)
        if match:
            errors.append('"[{}]" tag not "{}" text'.format(match.groups()[0],
                                                            match.groups()[0]))

        if (re.search(
                r'more than [0-9]+(?!\[pp\])',
                re.sub(r'no more', '', paragraph, flags=re.IGNORECASE),
                flags=re.IGNORECASE) and
                not re.search(r'cannot[^.]+more than [0-9]+(?!\[pp\])',
                              re.sub(r'cannot[^.]+unless', '', paragraph,
                                     flags=re.IGNORECASE),
                              flags=re.IGNORECASE)):
            errors.append('use "... or more" rather than "more than ..."')
        elif (re.search(
                r'greater than [0-9]+(?!\[pp\])', paragraph,
                flags=re.IGNORECASE) and
                not re.search(r'cannot[^.]+greater than [0-9]+(?!\[pp\])',
                              re.sub(r'cannot[^.]+unless', '', paragraph,
                                     flags=re.IGNORECASE),
                              flags=re.IGNORECASE)):
            errors.append(
                'use "... or greater" rather than "greater than ..."')

        if (re.search(r'fewer than [0-9]+(?!\[pp\])', paragraph,
                      flags=re.IGNORECASE) and
                not re.search(r'cannot[^.]+fewer than [0-9]+(?!\[pp\])',
                              re.sub(r'cannot[^.]+unless', '', paragraph,
                                     flags=re.IGNORECASE),
                              flags=re.IGNORECASE)):
            errors.append('use "... or fewer" rather than "fewer than ..."')
        elif (re.search(r'less than [0-9]+(?!\[pp\])', paragraph,
                        flags=re.IGNORECASE) and
                not re.search(r'cannot[^.]+less than [0-9]+(?!\[pp\])',
                              re.sub(r'cannot[^.]+unless', '', paragraph,
                                     flags=re.IGNORECASE),
                              flags=re.IGNORECASE)):
            errors.append('use "... or less" rather than "less than ..."')

        if (re.search(r'cannot[^.]+ [0-9]+ or more',
                      re.sub(r'cannot[^.]+unless', '', paragraph,
                             flags=re.IGNORECASE), flags=re.IGNORECASE)):
            errors.append('use "more than ..." rather than "... or more"')
        elif (re.search(r'cannot[^.]+ [0-9]+ or greater',
                      re.sub(r'cannot[^.]+unless', '', paragraph,
                             flags=re.IGNORECASE), flags=re.IGNORECASE)):
            errors.append(
                'use "greater than ..." rather than "... or greater"')

        if (re.search(r'cannot[^.]+ [0-9]+ or less',
                      re.sub(r'cannot[^.]+unless', '', paragraph,
                             flags=re.IGNORECASE), flags=re.IGNORECASE)):
            errors.append('use "less than ..." rather than "... or less"')
        elif (re.search(r'cannot[^.]+ [0-9]+ or fewer',
                      re.sub(r'cannot[^.]+unless', '', paragraph,
                             flags=re.IGNORECASE), flags=re.IGNORECASE)):
            errors.append('use "fewer than ..." rather than "... or fewer"')

        if re.search(r' defense\b', paragraph):
            errors.append('"[defense]" tag not "defense" text')

        if re.search(r' willpower\b', paragraph):
            errors.append('"[willpower]" tag not "willpower" text')

        if re.search(r' (?:[+–][0-9X]+|printed) attack\b', paragraph):
            errors.append('"[attack]" tag not "attack" text')

        if re.search(
                r' (?:[+–][0-9X]+|printed) threat\b',
                paragraph.replace('threat cost', '').replace('threat penalty',
                                                             '')):
            errors.append('"[threat]" tag not "threat" text')

        if re.search(r'[Cc]hoose[^:]*?: Either', paragraph):
            errors.append('"either" must be in lower case')

        if re.search(r'\bheal[^.]+?\bon\b',
                     re.sub(r'\bfrom\b[^.]+?\bon\b', '', paragraph,
                            flags=re.IGNORECASE),
                     flags=re.IGNORECASE):
            errors.append('"heal ... from" not "heal ... on"')

        if 'quest card' in paragraph:
            errors.append('"quest" not "quest card"')

        if re.search(
                r'\b(?:1|2|a|all|any|another|both|each|more|the|those|your)'
                r'(?: facedown| previously| random| remaining)? set aside',
                paragraph):
            errors.append('"set-aside" not "set aside"')

        if 'set-aside' in re.sub(
                r'\b(?:1|2|a|all|any|another|both|each|more|the|those|your)'
                r'(?: facedown| previously| random| remaining)? set-aside', '',
                paragraph):
            print(re.sub(
                r'\b(?:1|2|a|all|any|another|both|each|more|the|those|your)'
                r'(?: facedown| previously| random| remaining)? set-aside', '',
                paragraph))
            errors.append('"set aside" not "set-aside"')

        if re.search(r'[Ww]hile [^\.]+ is the active location, it gains[^\.]+'
                     r'(?:Forced|Response)[^\.]+ [Aa]fter [^\.]+ is explored',
                     paragraph):
            errors.append(
                'use "After [name] is explored as the active location" format '
                '(without "While..." phrase)')

        if re.search(r' gains “(?:\[[^\]]+\])?[A-Z]', paragraph):
            errors.append('add ":" after "gains"')

        if re.search(r' text “(?:\[[^\]]+\])?[A-Z]', paragraph):
            errors.append('add ":" after "text"')

        if re.search(r'is a \[bi\][^\[]+\[\/bi\](?! trait| \[bi\]trait)',
                     paragraph, flags=re.IGNORECASE):
            errors.append('use "has the {Trait} trait"')
        elif re.search(
            r'(?<!the )(?:printed )?\[bi\][^\[]+\[\/bi\]'
            r'(?:(?:, | or |, or | and |, and )\[bi\][^\[]+\[\/bi\])* '
            r'traits?\b',
            re.sub(r'the (?:printed )?\[bi\][^\[]+\[\/bi\]'
                   r'(?:(?:, | or |, or | and |, and )\[bi\][^\[]+\[\/bi\])* '
                   r'traits?\b', '', paragraph), flags=re.IGNORECASE):
            errors.append('use "the {Trait} trait"')

        if re.search(r'\[\/bi\] Traits\b', paragraph):
            errors.append('"traits" must be in lower case')
        elif re.search(r'\[\/bi\] Trait\b', paragraph):
            errors.append('"trait" must be in lower case')
        elif re.search(r'\[\/bi\] \[bi\]traits\b', paragraph,
                       flags=re.IGNORECASE):
            errors.append('remove tags around "traits"')
        elif re.search(r'\[\/bi\] \[bi\]trait\b', paragraph,
                       flags=re.IGNORECASE):
            errors.append('remove tags around "trait"')

        if re.search(r'(?<!\[\/bi\] )traits\b', paragraph):
            errors.append('"Traits" must be capitalized')
        if re.search(r'(?<!\[\/bi\] )trait\b', paragraph):
            errors.append('"Trait" must be capitalized')
        elif re.search(r'(?<!\[\/bi\] )(?<!\[bi\])Traits\b', paragraph,
                       flags=re.IGNORECASE):
            errors.append('add {} around "Traits"')
        elif re.search(r'(?<!\[\/bi\] )(?<!\[bi\])Trait\b', paragraph,
                       flags=re.IGNORECASE):
            errors.append('add {} around "Trait"')

        if (field in {CARD_SHADOW, BACK_PREFIX + CARD_SHADOW} and
                re.search(r'\bdefending player\b', paragraph,
                          flags=re.IGNORECASE)):
            errors.append('"you" not "defending player"')
        elif re.search(r'\bshadow\b[^.]+ defending player\b', paragraph,
                       flags=re.IGNORECASE):
            errors.append('"you" not "defending player"')
        elif re.search(
                r'\b(?:after|when) [^.]+ attacks[^.]+ defending player\b',
                paragraph, flags=re.IGNORECASE):
            errors.append('"you" not "defending player"')

        if (field in {CARD_SHADOW, BACK_PREFIX + CARD_SHADOW} and
                re.search(r'\bafter this attack[^.]* attacking enemy engages '
                          r'the next player[^.]* makes an immediate attack\b',
                          paragraph, flags=re.IGNORECASE) and
                not re.search(r'\bafter this attack, attacking enemy engages '
                              r'the next player, then makes an immediate '
                              r'attack\b', paragraph, flags=re.IGNORECASE)):
            errors.append(
                'use "After this attack, attacking enemy engages the next '
                'player, then makes an immediate attack"')
        if (re.search(r'\bshadow\b[^.]+ after this attack[^.]* attacking '
                      r'enemy engages the next player[^.]* makes an immediate '
                      r'attack\b', paragraph, flags=re.IGNORECASE) and
                not re.search(r'\bafter this attack, attacking enemy engages '
                              r'the next player, then makes an immediate '
                              r'attack\b', paragraph, flags=re.IGNORECASE)):
            errors.append(
                'use "After this attack, attacking enemy engages the next '
                'player, then makes an immediate attack"')

        match = re.search(r'advance to stage ([0-9]+)\b', paragraph,
                          flags=re.IGNORECASE)
        if match:
            errors.append('use "advance to stage {}A(B)" format'
                          .format(match.groups()[0]))

        match = re.search(r'(?<!\bstage )([2-90X]) card\b', paragraph,
                          flags=re.IGNORECASE)
        if match:
            errors.append('"{} cards" not "{} card"'.format(match.groups()[0],
                                                            match.groups()[0]))

        if re.search(r'^\[b\]Rumor\[\/b\]:', paragraph):
            errors.append(
                'rumor text must be inside [i] tags '
                '(including "[b]Rumor[/b]:")')
        elif re.search(r'^Rumor:', paragraph):
            errors.append(
                '"Rumor" must be inside [b] tags, rumor text must be inside '
                '[i] tags (including "[b]Rumor[/b]:")')

        if re.search(r'^(?:\[bi\])?Last Gasp(?:\[\/bi\])?:', paragraph):
            errors.append('"Last Gasp" must be inside [b] tags')

        if re.search(r'^(?:\[bi\])?Fowl(?:\[\/bi\])?:', paragraph):
            errors.append('"Fowl" must be inside [b] tags')

        if (re.search(r'(?:\[bi\]forced\[\/bi\]|forced|"forced") effect',
                      paragraph, flags=re.IGNORECASE) or
                '[b]forced[/b] effect' in paragraph):
            errors.append('use [b]Forced[/b] in the middle of the text')

        if (re.search(r'(?:\[bi\]travel\[\/bi\]|travel|"travel") effect',
                      paragraph, flags=re.IGNORECASE) or
                '[b]travel[/b] effect' in paragraph):
            errors.append('use [b]Travel[/b] in the middle of the text')

        if (re.search(r'(?:\[bi\]rumor\[\/bi\]|rumor|"rumor") effect',
                      paragraph, flags=re.IGNORECASE) or
                '[b]rumor[/b] effect' in paragraph):
            errors.append('use [b]Rumor[/b] in the middle of the text')

        if (re.search(
                r'(?:\[bi\]last gasp\[\/bi\]|last gasp|"last gasp") effect',
                paragraph, flags=re.IGNORECASE) or
                '[b]last gasp[/b] effect' in paragraph or
                '[b]Last gasp[/b] effect' in paragraph):
            errors.append('use [b]Last Gasp[/b] in the middle of the text')

        if (re.search(r'(?:\[bi\]fowl\[\/bi\]|fowl|"fowl") effect',
                      paragraph, flags=re.IGNORECASE) or
                '[b]fowl[/b] effect' in paragraph):
            errors.append('use [b]Fowl[/b] in the middle of the text')

        if (re.search(r'(?:\[bi\]shadow\[\/bi\]|\[b\]shadow\[\/b\]|"shadow") '
                      r'effect', paragraph, flags=re.IGNORECASE) or
                re.search(r'(?<!\.) Shadow effect\b', paragraph)):
            errors.append('use shadow (without tags and double quotes)')

        if (re.search(r'(?:\[bi\]when revealed\[\/bi\]|'
                      r'\[b\]when revealed\[\/b\]|when revealed) effect',
                      paragraph, flags=re.IGNORECASE) or
                '"When Revealed" effect' in paragraph or
                '"When revealed" effect' in paragraph):
            errors.append(
                'use "when revealed" (in double quotes and without tags)')

        if 'When revealed:' in paragraph:
            errors.append('use "When Revealed:"')

        if 'to a minimum of 0' in paragraph:
            errors.append('redundant "to a minimum of 0" statement')
        elif re.search(r'[^\(]to a minimum of ', paragraph,
                       flags=re.IGNORECASE):
            errors.append('"(to a minimum of ...)" must be in parenthesis')
        elif 'To a minimum of ' in paragraph:
            errors.append('"to a minimum of ..." must be in lower case')

        updated_paragraph = re.sub(
            r'\b(?:Valour )?(?:Resource |Planning |Quest |Travel |Encounter '
            r'|Combat |Refresh )?(?:Action):', '', paragraph)
        updated_paragraph = re.sub(r'\b(?:Valour Response|Response):', '',
                                   updated_paragraph)

        updated_paragraph = re.sub(
            r'\[b\](?:Valour )?(?:Resource |Planning |Quest |Travel '
            r'|Encounter |Combat |Refresh )?(?:Action)\[\/b\]:', '',
            updated_paragraph)
        updated_paragraph = re.sub(
            r'\[b\](?:Valour Response|Response)\[\/b\]:', '',
            updated_paragraph)

        if (re.search(r'(?:\[bi\]action\[\/bi\]|\[b\]action\[\/b\]|"action")',
                      updated_paragraph, flags=re.IGNORECASE) or
                re.search(r'(?<!\.) Action\b', updated_paragraph)):
            errors.append('use action (without tags and double quotes)')

        if (re.search(r'(?:\[bi\]response\[\/bi\]|\[b\]response\[\/b\]|'
                      r'"response")', updated_paragraph,
                      flags=re.IGNORECASE) or
                re.search(r'(?<!\.) Response\b', updated_paragraph)):
            errors.append('use response (without tags and double quotes)')

        if field == CARD_TEXT and card[CARD_TYPE] == T_QUEST:
            name_regex = (r'(?<!\[bi\])\b' + re.escape(card[CARD_NAME] or '') +
                          r'\b(?!\[\/bi\])')
            if re.search(name_regex, paragraph):
                errors.append('use "this stage" rather than card name')
            elif re.search(r'\bthis quest\b', paragraph, flags=re.IGNORECASE):
                errors.append('"this stage" not "this quest"')

        if (field == BACK_PREFIX + CARD_TEXT and
                card[BACK_PREFIX + CARD_TYPE] == T_QUEST):
            name_regex = (r'(?<!\[bi\])\b' +
                          re.escape(card[BACK_PREFIX + CARD_NAME] or '') +
                          r'\b(?!\[\/bi\])')
            if re.search(name_regex, paragraph):
                errors.append('use "this stage" rather than card name')
            elif re.search(r'\bthis quest\b', paragraph, flags=re.IGNORECASE):
                errors.append('"this stage" not "this quest"')

        if (field == CARD_TEXT and card[CARD_TYPE] in
                {T_ENCOUNTER_SIDE_QUEST, T_PLAYER_SIDE_QUEST}):
            name_regex = (r'(?<!\[bi\])\b' + re.escape(card[CARD_NAME] or '') +
                          r'\b(?!\[\/bi\]| (?:is )?in the victory display)')
            if re.search(name_regex, paragraph):
                errors.append('use "this quest" rather than card name')
            elif re.search(r'\bthis stage\b', paragraph, flags=re.IGNORECASE):
                errors.append('"this quest" not "this stage"')

        if (field == BACK_PREFIX + CARD_TEXT and
                card[BACK_PREFIX + CARD_TYPE] in
                {T_ENCOUNTER_SIDE_QUEST, T_PLAYER_SIDE_QUEST}):
            name_regex = (r'(?<!\[bi\])\b' +
                          re.escape(card[BACK_PREFIX + CARD_NAME] or '') +
                          r'\b(?!\[\/bi\]| (?:is )?in the victory display)')
            if re.search(name_regex, paragraph):
                errors.append('use "this quest" rather than card name')
            elif re.search(r'\bthis stage\b', paragraph, flags=re.IGNORECASE):
                errors.append('"this quest" not "this stage"')

    if (field == CARD_TEXT and card[CARD_TYPE] == T_QUEST
            and str(card[CARD_COST]) == '1'):
        if 'When Revealed' in text:
            errors.append('"Setup" not "When Revealed"')

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


def _remove_common_elements(list1, list2):
    """ Remove common elements from two lists.
    """
    for i in list1.copy():
        if i in list2:
            list1.remove(i)
            list2.remove(i)


def _split_combined_elements(input_list):
    """ Split combined elements in the list.
    """
    output_list = []
    for element in input_list:
        if re.match(r'^[0-9]+\[pp\]$', element):
            output_list.append(element[:-4])
            output_list.append(element[-4:])
        elif re.match(r'^[0-9]+ \[[^\]]+\]$', element):
            output_list.extend(element.split(' '))
        else:
            output_list.append(element)

    return output_list


def _clean_value_for_hash(value):
    """ Clean the value before generating its hash.
    """
    value = value.replace('[br]', '').replace('[nobr]', ' ')
    value = re.sub(r'\n{1}', ' ', value)
    return value


def _replace_numbers(value, lang=L_ENGLISH):
    """ Replace numbers as text.
    """
    for key, translations in NUMBER_TRANSLATIONS.items():
        translation = translations.get(lang, [])
        for word in translation:
            value = re.sub(_get_regex(word), key, value, flags=re.IGNORECASE)

    return value


def _add_automatic_tags(value, lang=L_ENGLISH):
    """ Add automatic tags.
    """
    if lang == L_ENGLISH:
        value = re.sub(
            r'\b(Valour )?(Resource |Planning |Quest |Travel |Encounter '
            r'|Combat |Refresh )?(Action):', '[b]\\1\\2\\3[/b]:', value)
        value = re.sub(
            r'\b(When Revealed|Forced|Valour Response|Response|Travel|Shadow'
            r'|Resolution):', '[b]\\1[/b]:', value)
        value = re.sub(
            r'\b(Setup)( \([^\)]+\))?:', '[b]\\1[/b]\\2:', value)
        value = re.sub(r'\b(Condition)\b', '[bi]\\1[/bi]', value)
    elif lang == L_FRENCH:
        value = re.sub(
            r'(\[Vaillance\] )?(\[Ressource\] |\[Organisation\] '
            r'|\[Qu\u00eate\] |\[Voyage\] |\[Rencontre\] |\[Combat\] '
            r'|\[Restauration\] )?\b(Action) ?:', '[b]\\1\\2\\3[/b] :', value)
        value = re.sub(
            r'\b(Une fois r\u00e9v\u00e9l\u00e9e|Forc\u00e9'
            r'|\[Vaillance\] R\u00e9ponse|R\u00e9ponse|Trajet|Ombre'
            r'|R\u00e9solution) ?:', '[b]\\1[/b] :', value)
        value = re.sub(
            r'\b(Mise en place)( \([^\)]+\))? ?:', '[b]\\1[/b]\\2 :', value)
        value = re.sub(r'\b(Condition)\b', '[bi]\\1[/bi]', value)
    elif lang == L_GERMAN:
        value = re.sub(
            r'\b(Ehrenvolle )?(Ressourcenaktion|Planungsaktion'
            r'|Abenteueraktion|Reiseaktion|Begegnungsaktion|Kampfaktion'
            r'|Auffrischungsaktion|Aktion):', '[b]\\1\\2[/b]:', value)
        value = re.sub(
            r'\b(Wenn aufgedeckt|Erzwungen|Ehrenvolle Reaktion|Reaktion|Reise'
            r'|Schatten|Aufl\u00f6sung):', '[b]\\1[/b]:', value)
        value = re.sub(
            r'\b(Vorbereitung)( \([^\)]+\))?:', '[b]\\1[/b]\\2:', value)
        value = re.sub(r'\b(Zustand)\b', '[bi]\\1[/bi]', value)
    elif lang == L_ITALIAN:
        value = re.sub(
            r'\b(Azione)( Valorosa)?( di Risorse| di Pianificazione'
            r'| di Ricerca| di Viaggio| di Incontri| di Combattimento'
            r'| di Riordino)?:', '[b]\\1\\2\\3[/b]:', value)
        value = re.sub(
            r'\b(Quando Rivelata|Obbligato|Risposta Valorosa|Risposta'
            r'|Viaggio|Ombra|Risoluzione):', '[b]\\1[/b]:', value)
        value = re.sub(
            r'\b(Preparazione)( \([^\)]+\))?:', '[b]\\1[/b]\\2:', value)
        value = re.sub(r'\b(Condizione)\b', '[bi]\\1[/bi]', value)
    elif lang == L_POLISH:
        value = re.sub(
            r'\b(Akcja)( Zasob\u00f3w| Planowania| Wyprawy| Podr\u00f3\u017cy'
            r'| Spotkania| Walki| Odpoczynku)?( M\u0119stwa)?:',
            '[b]\\1\\2\\3[/b]:', value)
        value = re.sub(
            r'\b(Po odkryciu|Wymuszony|Odpowied\u017a M\u0119stwa'
            r'|Odpowied\u017a|Podr\u00f3\u017c|Cie\u0144|Nast\u0119pstwa):',
            '[b]\\1[/b]:', value)
        value = re.sub(
            r'\b(Przygotowanie)( \([^\)]+\))?:', '[b]\\1[/b]\\2:', value)
        value = re.sub(r'\b(Stan)\b', '[bi]\\1[/bi]', value)
    elif lang == L_PORTUGUESE:
        value = re.sub(
            r'\b(A\u00e7\u00e3o)( Valorosa)?( de Recursos| de Planejamento'
            r'| de Miss\u00e3o| de Viagem| de Encontro| de Combate'
            r'| de Renova\u00e7\u00e3o)?:', '[b]\\1\\2\\3[/b]:', value)
        value = re.sub(
            r'\b(Efeito Revelado|Efeito For\u00e7ado|Resposta Valorosa'
            r'|Resposta|Viagem|Efeito Sombrio|Resolu\u00e7\u00e3o):',
            '[b]\\1[/b]:', value)
        value = re.sub(
            r'\b(Prepara\u00e7\u00e3o)( \([^\)]+\))?:', '[b]\\1[/b]\\2:',
            value)
        value = re.sub(r'\b(Condi\u00e7\u00e3o)\b', '[bi]\\1[/bi]', value)
    elif lang == L_SPANISH:
        value = re.sub(
            r'\b(Acci\u00f3n)( de Recursos| de Planificaci\u00f3n'
            r'| de Misi\u00f3n| de Viaje| de Encuentro| de Combate'
            r'| de Recuperaci\u00f3n)?( de Valor)?:', '[b]\\1\\2\\3[/b]:',
            value)
        value = re.sub(
            r'\b(Al ser revelada|Obligado|Respuesta de Valor|Respuesta|Viaje'
            r'|Sombra|Resoluci\u00f3n):', '[b]\\1[/b]:', value)
        value = re.sub(
            r'\b(Preparaci\u00f3n)( \([^\)]+\))?:', '[b]\\1[/b]\\2:', value)
        value = re.sub(r'\b(Estado)\b', '[bi]\\1[/bi]', value)

    value = value.replace('[bi][bi]', '[bi]')
    value = value.replace('[/bi][/bi]', '[/bi]')
    value = value.replace('[b][b]', '[b]')
    value = value.replace('[/b][/b]', '[/b]')
    return value


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
    quest_adventures = {}
    hash_by_key = {}
    keys_by_hash = {}
    card_data = DATA[:]
    card_data = sorted(card_data, key=lambda row: (row[CARD_SCRATCH] or 0,
                                                   row[ROW_COLUMN]))

    accents_regex = (
        r'\b(?:' + '|'.join([re.escape(a) for a in ACCENTS]) + r')\b')

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
        card_icons = row[CARD_ICONS]
        card_info = row[CARD_INFO]
        card_artist = row[CARD_ARTIST]
        card_panx = row[CARD_PANX]
        card_pany = row[CARD_PANY]
        card_scale = row[CARD_SCALE]
        card_portrait_shadow = row[CARD_PORTRAIT_SHADOW]

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
        card_icons_back = row[BACK_PREFIX + CARD_ICONS]
        card_info_back = row[BACK_PREFIX + CARD_INFO]
        card_artist_back = row[BACK_PREFIX + CARD_ARTIST]
        card_panx_back = row[BACK_PREFIX + CARD_PANX]
        card_pany_back = row[BACK_PREFIX + CARD_PANY]
        card_scale_back = row[BACK_PREFIX + CARD_SCALE]
        card_portrait_shadow_back = row[BACK_PREFIX + CARD_PORTRAIT_SHADOW]

        card_easy_mode = row[CARD_EASY_MODE]
        card_additional_encounter_sets = row[CARD_ADDITIONAL_ENCOUNTER_SETS]
        card_adventure = row[CARD_ADVENTURE]
        card_collection_icon = row[CARD_COLLECTION_ICON]
        card_copyright = row[CARD_COPYRIGHT]
        card_back = row[CARD_BACK]
        card_deck_rules = row[CARD_DECK_RULES]
        card_scratch = row[CARD_SCRATCH]
        card_selected = row[CARD_SELECTED]
        card_last_design_change_date = row[CARD_LAST_DESIGN_CHANGE_DATE]
        row_info = '{}{}{}{}'.format(
            ', {}'.format(card_name) if card_name else '',
            ' ({})'.format(row[CARD_SET_NAME]) if row[CARD_SET_NAME] else '',
            ' [Card GUID: {}]'.format(card_id) if card_id else '',
            ' (Scratch)' if card_scratch else '')

        if set_id is None:
            message = 'Missing set ID for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
        elif set_id == '[filtered set]':
            message = (
                'Reusing non-scratch set ID for row #{}{} (which is '
                'prohibited)'.format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
        elif set_id not in all_set_ids:
            message = 'Unknown set ID for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)

        if card_id is None:
            message = 'Missing card ID for row #{}{}'.format(i, row_info)
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

        for error in PRE_SANITY_CHECK['name'].get((i, card_scratch), []):
            message = ('{} for row #{}{} (use IgnoreName flag to ignore)'
                       .format(error, i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)

        for error in PRE_SANITY_CHECK['ref'].get(
                (i, card_scratch, L_ENGLISH), []):
            message = '{} for row #{}{}'.format(error, i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)

        for error in PRE_SANITY_CHECK['flavour'].get(
                (i, card_scratch, L_ENGLISH), []):
            message = '{} for row #{}{}'.format(error, i, row_info)
            if not [l for l in conf['languages'] if l != L_ENGLISH]:
                if message.startswith('Possibly '):
                    logging.warning(message)
                else:
                    logging.error(message)

        for error in PRE_SANITY_CHECK['shadow'].get(
                (i, card_scratch, L_ENGLISH), []):
            message = '{} for row #{}{}'.format(error, i, row_info)
            if not [l for l in conf['languages'] if l != L_ENGLISH]:
                logging.warning(message)

        if card_number is None:
            message = 'Missing card number for row #{}{}'.format(i, row_info)
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
            message = 'Missing card quantity for row #{}{}'.format(i, row_info)
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
                   F_ADDITIONALCOPIES in extract_flags(card_flags))):
            message = ('Incorrect card quantity according to its card type '
                       'for row #{}{}'.format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type in CARD_TYPES_THREE_COPIES and
              card_sphere not in CARD_SPHERES_BOON and
              card_quantity not in {1, 3} and
              not (card_flags and
                   F_ADDITIONALCOPIES in extract_flags(card_flags))):
            message = ('Incorrect card quantity according to its card type '
                       'for row #{}{}'.format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_encounter_set is None and
                ((card_type in CARD_TYPES_ENCOUNTER_SET and
                  card_sphere != S_BOON) or
                 (card_type_back in CARD_TYPES_ENCOUNTER_SET and
                  card_sphere_back != S_BOON))):
            message = 'Missing encounter set for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_encounter_set is not None and  # pylint: disable=R0916
              (card_type in CARD_TYPES_NO_ENCOUNTER_SET
               or card_sphere == S_BOON) and
              (card_type_back in CARD_TYPES_NO_ENCOUNTER_SET or
               card_type_back is None or card_sphere_back == S_BOON)):
            message = 'Redundant encounter set for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_encounter_set is not None and
              not (card_flags and F_IGNORENAME in extract_flags(
                  card_flags, conf['ignore_ignore_flags']))):
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
            message = 'Missing card name for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_name is not None and
              not (card_flags and F_IGNORENAME in extract_flags(
                  card_flags, conf['ignore_ignore_flags']))):
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
            message = 'Missing card name back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_name_back is not None and
              not (card_flags_back and
                   F_IGNORENAME in extract_flags(
                       card_flags_back, conf['ignore_ignore_flags']))):
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

        if card_unique is not None and card_unique not in {'1', 1}:
            message = 'Incorrect format for unique flag for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif ((card_unique is None and card_type in CARD_TYPES_UNIQUE) or
              (card_unique in {'1', 1} and
               card_type in CARD_TYPES_NO_UNIQUE)):
            message = (
                'Incorrect unique flag according to its card type for '
                'row #{}{}'.format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_unique_back is not None and card_type_back is None:
            message = 'Redundant unique flag back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_unique_back is not None and card_unique_back not in {'1', 1}:
            message = ('Incorrect format for unique flag back for row #{}{}'
                       .format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif ((card_unique_back is None and
               card_type_back in CARD_TYPES_UNIQUE) or
              (card_unique_back in {'1', 1} and
               card_type_back in CARD_TYPES_NO_UNIQUE)):
            message = ('Incorrect unique flag back according to its card type '
                       'for row #{}{}'.format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_type is None:
            message = 'Missing card type for row #{}{}'.format(i, row_info)
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
            message = 'Unknown card type back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type in CARD_TYPES_DOUBLESIDE_DEFAULT
              and card_type_back is not None and card_type_back != card_type):
            message = ('Incorrect card type back according to its card type '
                       'front for row #{}{}'.format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type not in CARD_TYPES_DOUBLESIDE_DEFAULT
              and card_type_back in CARD_TYPES_DOUBLESIDE_DEFAULT):
            message = ('Incorrect card type back according to its card type '
                       'front for row #{}{}'.format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_type == T_CAMPAIGN:
            spheres = SPHERES_CAMPAIGN.copy()
        elif card_type == T_OBJECTIVE:
            spheres = SPHERES_OBJECTIVE.copy()
        elif card_type == T_ENCOUNTER_SIDE_QUEST:
            spheres = SPHERES_SIDE_QUEST.copy()
        elif card_type == T_RULES:
            spheres = SPHERES_RULES.copy()
        elif card_type == T_PRESENTATION:
            spheres = SPHERES_PRESENTATION.copy()
        elif card_type == T_SHIP_OBJECTIVE:
            spheres = SPHERES_SHIP_OBJECTIVE.copy()
        elif card_type in CARD_TYPES_PLAYER_SPHERE:
            spheres = SPHERES_PLAYER.copy()
        else:
            spheres = SPHERES.copy()

        if card_type in CARD_TYPES_BOON:
            spheres.add(S_BOON)

        if card_type in CARD_TYPES_BOON_SPHERE:
            spheres.update([S_BOONLEADERSHIP, S_BOONLORE, S_BOONSPIRIT,
                            S_BOONTACTICS])

        if card_type in CARD_TYPES_BURDEN:
            spheres.add(S_BURDEN)

        if card_type in CARD_TYPES_NIGHTMARE:
            spheres.add(S_NIGHTMARE)

        if card_type in CARD_TYPES_NOSTAT:
            spheres.add(S_NOSTAT)

        if (card_sphere is None and
                (card_type in CARD_TYPES_PLAYER_SPHERE or
                 card_type == T_PRESENTATION)):
            message = 'Missing sphere for row #{}{}'.format(i, row_info)
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

        if not is_doubleside(card_type, card_type_back):
            if card_type_back == T_SHIP_OBJECTIVE:
                spheres_back = SPHERES_SHIP_OBJECTIVE.copy()
            elif card_type_back in CARD_TYPES_PLAYER_SPHERE:
                spheres_back = SPHERES_PLAYER.copy()
            else:
                spheres_back = SPHERES.copy()

            if card_type_back in CARD_TYPES_BOON:
                spheres_back.add(S_BOON)

            if card_type_back in CARD_TYPES_BOON_SPHERE:
                spheres_back.update([S_BOONLEADERSHIP, S_BOONLORE,
                                     S_BOONSPIRIT, S_BOONTACTICS])

            if card_type_back in CARD_TYPES_BURDEN:
                spheres_back.add(S_BURDEN)

            if card_type_back in CARD_TYPES_NIGHTMARE:
                spheres_back.add(S_NIGHTMARE)

            if card_type_back in CARD_TYPES_NOSTAT:
                spheres_back.add(S_NOSTAT)

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
                message = 'Missing sphere back for row #{}{}'.format(
                    i, row_info)
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
                not (card_flags and F_NOTRAITS in extract_flags(card_flags))):
            message = 'Missing traits for row #{}{}'.format(i, row_info)
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
              not (card_flags and F_NOTRAITS in extract_flags(card_flags))):
            message = 'Missing traits for row #{}{}'.format(i, row_info)
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
              not (card_flags and F_IGNORENAME in extract_flags(
                  card_flags, conf['ignore_ignore_flags']))):
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
                   F_NOTRAITS in extract_flags(card_flags_back))):
            message = 'Missing traits back for row #{}{}'.format(i, row_info)
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
                   F_NOTRAITS in extract_flags(card_flags_back))):
            message = 'Missing traits back for row #{}{}'.format(i, row_info)
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
                   F_IGNORENAME in extract_flags(
                       card_flags_back, conf['ignore_ignore_flags']))):
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
            message = 'Missing cost for row #{}{}'.format(i, row_info)
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
        elif (card_type == T_HERO and
              not re.match(r'^[1-9]?[0-9]$', str(card_cost))):
            message = 'Incorrect cost value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_type == T_QUEST and not re.match(r'^[1-9]$', str(card_cost)):
            message = 'Incorrect cost value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type not in {T_HERO, T_QUEST} and card_cost is not None and
              not re.match(r'^[1-9]?[0-9]$', str(card_cost)) and
              card_cost != '-' and card_cost != 'X'):
            message = 'Incorrect cost value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type not in {T_HERO, T_QUEST} and card_cost is not None and
              (B_ENCOUNTER in extract_keywords(card_keywords) or
               card_back == B_ENCOUNTER) and
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
            message = 'Missing cost back for row #{}{}'.format(i, row_info)
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
        elif (card_type_back == T_HERO and
              not re.match(r'^[1-9]?[0-9]$', str(card_cost_back))):
            message = 'Incorrect cost back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type_back == T_QUEST and
              not re.match(r'^[1-9]$', str(card_cost_back))):
            message = 'Incorrect cost back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type_back not in {T_HERO, T_QUEST} and
              card_cost_back is not None and
              not re.match(r'^[1-9]?[0-9]$', str(card_cost_back)) and
              card_cost_back != '-' and card_cost_back != 'X'):
            message = 'Incorrect cost back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type_back not in {T_HERO, T_QUEST} and
              card_cost_back is not None and
              B_ENCOUNTER in extract_keywords(card_keywords_back) and
              card_cost_back != '-'):
            message = 'Incorrect cost back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_engagement is None and card_type in CARD_TYPES_ENGAGEMENT:
            message = 'Missing engagement cost for row #{}{}'.format(
                i, row_info)
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
        elif (card_type == T_QUEST and
              not re.match(r'^[ACEG]$', str(card_engagement))):
            message = 'Incorrect engagement cost value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type != T_QUEST and card_engagement is not None and
              not re.match(r'^[1-9]?[0-9]$', str(card_engagement)) and
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
            message = 'Missing engagement cost back for row #{}{}'.format(
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
        elif (card_type_back == T_QUEST and
              not re.match(r'^[BDFH]$', str(card_engagement_back))):
            message = ('Incorrect engagement cost back value for row #{}{}'
                       .format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_type_back != T_QUEST and
              card_engagement_back is not None and
              not re.match(r'^[1-9]?[0-9]$', str(card_engagement_back)) and
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
            message = 'Missing threat for row #{}{}'.format(i, row_info)
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
              not re.match(r'^[1-9]?[0-9]$', str(card_threat)) and
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
            message = 'Missing threat back for row #{}{}'.format(i, row_info)
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
              not re.match(r'^[1-9]?[0-9]$', str(card_threat_back)) and
              card_threat_back != '-' and card_threat_back != 'X'):
            message = 'Incorrect threat back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_willpower is None and card_type in CARD_TYPES_WILLPOWER:
            message = 'Missing willpower for row #{}{}'.format(i, row_info)
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
              not re.match(r'^[1-9]?[0-9]$', str(card_willpower)) and
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
            message = 'Missing willpower back for row #{}{}'.format(
                i, row_info)
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
              not re.match(r'^[1-9]?[0-9]$', str(card_willpower_back)) and
              card_willpower_back != '-' and card_willpower_back != 'X'):
            message = 'Incorrect willpower back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_attack is None and card_type in CARD_TYPES_COMBAT:
            message = 'Missing attack for row #{}{}'.format(i, row_info)
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
              not re.match(r'^[1-9]?[0-9]$', str(card_attack)) and
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
            message = 'Missing attack back for row #{}{}'.format(i, row_info)
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
              not re.match(r'^[1-9]?[0-9]$', str(card_attack_back)) and
              card_attack_back != '-' and card_attack_back != 'X'):
            message = 'Incorrect attack back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_defense is None and card_type in CARD_TYPES_COMBAT:
            message = 'Missing defense for row #{}{}'.format(i, row_info)
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
              not re.match(r'^[1-9]?[0-9]$', str(card_defense)) and
              card_defense != '-' and card_defense != 'X'):
            message = 'Incorrect defense value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_defense_back is not None and card_type_back is None:
            message = 'Redundant defense back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_defense_back is None and
              card_type_back in CARD_TYPES_COMBAT):
            message = 'Missing defense back for row #{}{}'.format(i, row_info)
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
              not re.match(r'^[1-9]?[0-9]$', str(card_defense_back)) and
              card_defense_back != '-' and card_defense_back != 'X'):
            message = 'Incorrect defense back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_health is None and card_type in CARD_TYPES_COMBAT:
            message = 'Missing health for row #{}{}'.format(i, row_info)
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
              not re.match(r'^[1-9]?[0-9]$', str(card_health)) and
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
            message = 'Missing health back for row #{}{}'.format(i, row_info)
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
              not re.match(r'^[1-9]?[0-9]$', str(card_health_back)) and
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
            message = 'Missing quest points for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_quest is not None and
              (card_type not in CARD_TYPES_QUEST or
               card_sphere in CARD_SPHERES_NO_QUEST)):
            message = 'Redundant quest points for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_quest is not None and
              not re.match(r'^[1-9]?[0-9]$', str(card_quest)) and
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
            message = 'Missing quest points back for row #{}{}'.format(
                i, row_info)
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
              not re.match(r'^[1-9]?[0-9]$', str(card_quest_back)) and
              card_quest_back != '-' and card_quest_back != 'X'):
            message = 'Incorrect quest points back value for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_victory is not None and card_type in CARD_TYPES_PAGES:
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
        elif card_victory_back is not None and card_type_back == T_RULES:
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

        if card_text is not None and card_type in CARD_TYPES_NO_TEXT:
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
              card_type != T_PRESENTATION and card_sphere != S_BACK and
              not (card_flags and F_IGNORERULES in extract_flags(
                  card_flags, conf['ignore_ignore_flags']))):
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
              card_type_back != T_PRESENTATION and
              card_sphere != S_BACK and
              not (card_flags_back and
                   F_IGNORERULES in extract_flags(
                       card_flags_back, conf['ignore_ignore_flags']))):
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
                card_sphere != S_CAVE):
            message = 'Invalid [split] tag in text for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_text_back is not None and '[split]' in card_text_back and
                card_sphere_back != S_CAVE):
            message = 'Invalid [split] tag in text back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_shadow is not None and card_type not in CARD_TYPES_SHADOW and
                not (card_type in CARD_TYPES_SHADOW_ENCOUNTER and
                     (B_ENCOUNTER in extract_keywords(card_keywords) or
                      card_back == B_ENCOUNTER))):
            message = 'Redundant shadow for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_shadow is not None and
              not _verify_shadow_case(card_shadow, L_ENGLISH)):
            message = ('Shadow effect should start with a capital letter for '
                       'row #{}{}'.format(i, row_info))
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
              not (card_flags and F_IGNORERULES in extract_flags(
                  card_flags, conf['ignore_ignore_flags']))):
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
        elif (card_shadow_back is not None and
              not _verify_shadow_case(card_shadow_back, L_ENGLISH)):
            message = ('Shadow back effect should start with a capital letter '
                       'for row #{}{}'.format(i, row_info))
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
                   F_IGNORERULES in extract_flags(
                       card_flags_back, conf['ignore_ignore_flags']))):
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
            message = 'Redundant flavour back for row #{}{}'.format(
                i, row_info)
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
                 card_sphere in CARD_SPHERES_NO_ENCOUNTER_SET_NUMBER)):
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
               card_sphere_back in CARD_SPHERES_NO_ENCOUNTER_SET_NUMBER)):
            message = ('Redundant encounter set number back for row #{}{}'
                       .format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_encounter_set_icon is not None and
                (card_type not in CARD_TYPES_ENCOUNTER_SET_ICON or
                 card_sphere in CARD_SPHERES_NO_ENCOUNTER_SET_ICON)):
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
               card_sphere_back in CARD_SPHERES_NO_ENCOUNTER_SET_ICON)):
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
                message = 'Incorrect flags back for row #{}{}'.format(
                    i, row_info)
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            elif len(flags) != len(set(flags)):
                message = 'Duplicate flags back for row #{}{}'.format(
                    i, row_info)
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            elif [f for f in flags if f not in FLAGS]:
                message = 'Incorrect flags back for row #{}{}'.format(
                    i, row_info)
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

        if card_icons is not None and card_type not in CARD_TYPES_ICONS:
            message = 'Redundant icons for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_icons is not None and card_sphere in CARD_SPHERES_NO_ICONS:
            message = 'Redundant icons for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_icons_back is not None and card_type_back is None:
            message = 'Redundant icons back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_icons_back is not None and
              card_type_back not in CARD_TYPES_ICONS):
            message = 'Redundant icons back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_icons_back is not None and
              card_sphere_back in CARD_SPHERES_NO_ICONS):
            message = 'Redundant icons back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_info is not None and card_type in CARD_TYPES_NO_INFO:
            message = 'Redundant info for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if card_info_back is not None and card_type_back is None:
            message = 'Redundant info back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_info_back is not None and
              card_type_back in CARD_TYPES_NO_INFO_BACK):
            message = 'Redundant info back for row #{}{}'.format(i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

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
            message = 'Missing panx for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_panx is not None and not _is_float(card_panx):
            message = 'Incorrect format for panx value for row #{}{}'.format(
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
            message = 'Missing panx back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_panx_back is not None and not _is_float(card_panx_back):
            message = ('Incorrect format for panx back value for row #{}{}'
                       .format(i, row_info))
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
            message = 'Missing pany for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_pany is not None and not _is_float(card_pany):
            message = 'Incorrect format for pany value for row #{}{}'.format(
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
            message = 'Missing pany back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_pany_back is not None and not _is_float(card_pany_back):
            message = ('Incorrect format for pany back value for row #{}{}'
                       .format(i, row_info))
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
            message = 'Missing scale for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_scale is not None and not _is_positive_float(card_scale):
            message = 'Incorrect format for scale value for row #{}{}'.format(
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
            message = 'Missing scale back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_scale_back is not None and
              not _is_positive_float(card_scale_back)):
            message = ('Incorrect format for scale back value for row #{}{}'
                       .format(i, row_info))
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
        elif card_portrait_shadow not in {None, 'Black', 'PortraitTint'}:
            message = ('Incorrect value for portrait shadow for row #{}{}'
                       .format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_type != T_QUEST and card_portrait_shadow == 'PortraitTint':
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
        elif card_portrait_shadow_back not in {None, 'Black'}:
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

        if card_additional_encounter_sets is not None:
            all_sets = [
                s.strip() for s in card_additional_encounter_sets.split(';')
                if s.strip()]
            if card_type not in CARD_TYPES_ADDITIONAL_ENCOUNTER_SETS:
                message = ('Redundant additional encounter sets for row #{}{}'
                           .format(i, row_info))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            elif len(all_sets) > 6:
                message = ('Too many additional encounter sets for row #{}{}: '
                           '{} instead of the maximum 6'.format(i, row_info,
                                                                len(all_sets)))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            else:
                unknown_sets = [
                    s for s in all_sets if s not in ALL_ENCOUNTER_SET_NAMES]
                if (unknown_sets and
                        not (card_flags and
                             F_IGNORENAME in extract_flags(
                                 card_flags, conf['ignore_ignore_flags']))):
                    message = (
                        'Unknown additional encounter sets for row #{}{}: {} '
                        '(use IgnoreName flag to ignore)'.format(
                            i, row_info, '; '.join(unknown_sets)))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

        if (card_adventure is not None and  # pylint: disable=R0916
                (card_type not in CARD_TYPES_ADVENTURE or
                 card_sphere in CARD_SPHERES_NO_ADVENTURE) and
                (card_type_back not in CARD_TYPES_ADVENTURE or
                 card_sphere_back in CARD_SPHERES_NO_ADVENTURE or
                 card_type_back is None)):
            message = 'Redundant adventure for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_adventure is None and
              ((card_type in CARD_TYPES_SUBTITLE and
                card_sphere not in CARD_SPHERES_NO_ADVENTURE) or
               (card_type_back in CARD_TYPES_SUBTITLE and
                card_sphere_back not in CARD_SPHERES_NO_ADVENTURE))):
            message = 'Missing adventure for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif (card_adventure is not None and
              not (card_flags and F_IGNORENAME in extract_flags(
                  card_flags, conf['ignore_ignore_flags']))):
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

        if card_type == T_QUEST and card_adventure is not None:
            if (set_id, card_encounter_set) in quest_adventures:
                if (quest_adventures[(set_id, card_encounter_set)] !=
                        card_adventure):
                    message = (
                        'Different adventure values for the quest in row '
                        '#{}{}: "{}" and "{}"'.format(
                            i, row_info, card_adventure,
                            quest_adventures[(set_id, card_encounter_set)]))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)
            else:
                quest_adventures[(set_id, card_encounter_set)] = card_adventure

        if (card_collection_icon is not None and
                card_type in CARD_TYPES_NO_COLLECTION_ICON):
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
                (card_type in CARD_TYPES_DOUBLESIDE_DEFAULT or
                 card_type_back is not None)):
            message = 'Redundant custom card back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)
        elif card_back not in {None, B_ENCOUNTER, B_PLAYER}:
            message = 'Incorrect custom card back for row #{}{}'.format(
                i, row_info)
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        if (card_last_design_change_date is not None and
                not re.match(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$',
                             card_last_design_change_date)):
            message = ('Incorrect last design change date format for row '
                       '#{}{}: must be YYYY-MM-DD'.format(i, row_info))
            logging.error(message)
            if not card_scratch:
                errors.append(message)
            else:
                broken_set_ids.add(set_id)

        for key, value in row.items():
            if value == '#REF!':
                message = ('Reference error in {} column for row '
                           '#{}{}'.format(key.replace(BACK_PREFIX,
                                                      BACK_PREFIX_LOG), i,
                                          row_info))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)
            elif isinstance(value, str) and '[unmatched quot]' in value:
                message = (
                    'Unmatched quote character in {} column for row #{}{} '
                    '(use "[quot]" tag if needed)'.format(
                        key.replace(BACK_PREFIX, BACK_PREFIX_LOG), i,
                        row_info))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

            if (key in ONE_LINE_COLUMNS and isinstance(value, str) and
                    '\n' in value):
                message = ('Redundant line break in {} column for row #{}{}'
                           .format(key.replace(BACK_PREFIX, BACK_PREFIX_LOG),
                                   i, row_info))
                logging.error(message)
                if not card_scratch:
                    errors.append(message)
                else:
                    broken_set_ids.add(set_id)

            if key != CARD_DECK_RULES and isinstance(value, str):
                if key in TRANSLATED_COLUMNS:
                    value_key = (row[CARD_ID], key)
                    value_hash = hashlib.md5(_clean_value_for_hash(value)
                                             .encode()).hexdigest()
                    hash_by_key[(L_ENGLISH, value_key)] = value_hash
                    keys_by_hash[(L_ENGLISH, row[CARD_SET], value_hash)] = (
                        keys_by_hash.get((L_ENGLISH, row[CARD_SET],
                                          value_hash), []) + [value_key])

                match = re.search(r' ((?:\[[^\]]+\])+)(?:\n\n|$)', value)
                if match:
                    message = (
                        'Redundant space before "{}" in {} column for '
                        'row #{}{}'.format(
                            match.groups()[0],
                            key.replace(BACK_PREFIX, BACK_PREFIX_LOG), i,
                            row_info))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

                cleaned_value = _clean_tags(value)
                if key == CARD_SET:
                    cleaned_value = cleaned_value.replace('[filtered set]', '')
                elif key in {CARD_FLAVOUR, BACK_PREFIX + CARD_FLAVOUR}:
                    cleaned_value = cleaned_value.replace('[...]', '')

                unknown_tags = re.findall(r'\[[^\]\n]+\]', cleaned_value)
                if unknown_tags:
                    message = ('Unknown tag(s) in {} column for row #{}{}: {}'
                               .format(key.replace(BACK_PREFIX,
                                                   BACK_PREFIX_LOG), i,
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
                                   key.replace(BACK_PREFIX, BACK_PREFIX_LOG),
                                   i, row_info))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

                unmatched_tags = _detect_unmatched_tags(value)
                if unmatched_tags:
                    message = ('Unmatched tag(s) in {} column for row #{}{}: '
                               '{}'.format(key.replace(BACK_PREFIX,
                                                       BACK_PREFIX_LOG),
                                           i, row_info,
                                           ', '.join(unmatched_tags)))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

                match = re.search(
                    r'[0-9X]\[(attack|defense|willpower|threat)\]', value)
                if match:
                    message = (
                        'Missing space before [{}] in {} column for row #{}{}'
                        .format(match.groups()[0],
                                key.replace(BACK_PREFIX, BACK_PREFIX_LOG), i,
                                row_info))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

                if re.search(r'[0-9X ]pp[ .]', value):
                    message = (
                        '"[pp]" not "pp" in {} column for row #{}{}'
                        .format(key.replace(BACK_PREFIX, BACK_PREFIX_LOG), i,
                                row_info))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

                if re.search(r'[0-9X] \[pp\]', value):
                    message = (
                        'Redundant space before [pp] in {} column for row '
                        '#{}{}'.format(
                            key.replace(BACK_PREFIX, BACK_PREFIX_LOG), i,
                            row_info))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

                if 'Middle-Earth' in value:
                    message = (
                        '"Middle-earth" not "Middle-Earth" in {} column for '
                        'row #{}{}'.format(
                            key.replace(BACK_PREFIX, BACK_PREFIX_LOG), i,
                            row_info))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

                if ':[/b] ' in value:
                    message = (
                        '"[/b]:" not ":[/b]" in {} column for row #{}{}'
                        .format(key.replace(BACK_PREFIX, BACK_PREFIX_LOG), i,
                                row_info))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

                if ':[/bi] ' in value:
                    message = (
                        '"[/bi]:" not ":[/bi]" in {} column for row #{}{}'
                        .format(key.replace(BACK_PREFIX, BACK_PREFIX_LOG), i,
                                row_info))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

                if '“ ' in value:
                    message = (
                        'Redundant space after “ in {} column for row #{}{}'
                        .format(key.replace(BACK_PREFIX, BACK_PREFIX_LOG), i,
                                row_info))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

                if ' ”' in value:
                    message = (
                        'Redundant space before ” in {} column for row #{}{}'
                        .format(key.replace(BACK_PREFIX, BACK_PREFIX_LOG), i,
                                row_info))
                    logging.error(message)
                    if not card_scratch:
                        errors.append(message)
                    else:
                        broken_set_ids.add(set_id)

                ignore_accents = False
                if key.startswith(BACK_PREFIX):
                    if (card_flags_back and
                            F_IGNORENAME in extract_flags(
                                card_flags_back, conf['ignore_ignore_flags'])):
                        ignore_accents = True
                else:
                    if (card_flags and
                            F_IGNORENAME in extract_flags(
                                card_flags, conf['ignore_ignore_flags'])):
                        ignore_accents = True

                if not ignore_accents:
                    accents = set(re.findall(accents_regex, value))
                    if accents:
                        message = (
                            'Missing accents in {} column for row #{}{}: {} '
                            '(use IgnoreName flag to ignore)'
                            .format(key.replace(BACK_PREFIX, BACK_PREFIX_LOG),
                                    i, row_info, ', '.join(accents)))
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
        elif card_deck_rules is not None and set_id != card_selected:
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

            deck_rules_errors = _generate_octgn_o8d_quest(row)[2]
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
            if lang == L_ENGLISH or card_scratch:
                continue

            if not TRANSLATIONS[lang].get(card_id):
                logging.error(
                    'Missing card ID %s in %s translations', card_id, lang)
                continue

            for error in PRE_SANITY_CHECK['ref'].get(
                    (TRANSLATIONS[lang][card_id][ROW_COLUMN],
                     card_scratch, lang), []):
                logging.error(
                    '%s for card ID %s in %s translations, row #%s', error,
                    card_id, lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

            for error in PRE_SANITY_CHECK['flavour'].get(
                    (TRANSLATIONS[lang][card_id][ROW_COLUMN],
                     card_scratch, lang), []):
                message = (
                    '{} for card ID {} in {} translations, row #{}'
                    .format(error, card_id, lang,
                            TRANSLATIONS[lang][card_id][ROW_COLUMN]))
                if message.startswith('Possibly '):
                    logging.warning(message)
                else:
                    logging.error(message)

            for error in PRE_SANITY_CHECK['shadow'].get(
                    (TRANSLATIONS[lang][card_id][ROW_COLUMN],
                     card_scratch, lang), []):
                logging.warning(
                    '%s for card ID %s in %s translations, row #%s', error,
                    card_id, lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

            for key, value in TRANSLATIONS[lang][card_id].items():
                if key not in TRANSLATED_COLUMNS:
                    continue

                if value == '#REF!':
                    logging.error(
                        'Reference error in %s column for card ID %s in %s '
                        'translations, row #%s', key.replace(BACK_PREFIX,
                                                             BACK_PREFIX_LOG),
                        card_id, lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])
                elif isinstance(value, str) and '[unmatched quot]' in value:
                    logging.error(
                        'Unmatched quote character in %s column for card '
                        'ID %s in %s translations, row #%s (use "[quot]" tag '
                        'if needed)', key.replace(BACK_PREFIX,
                                                  BACK_PREFIX_LOG),
                        card_id, lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

                if (key in ONE_LINE_COLUMNS and isinstance(value, str) and
                        '\n' in value):
                    logging.error(
                        'Redundant line break in %s column for card ID %s in '
                        '%s translations, row #%s',
                        key.replace(BACK_PREFIX, BACK_PREFIX_LOG), card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

                if isinstance(value, str):
                    value_key = (row[CARD_ID], key)
                    value_hash = hashlib.md5(_clean_value_for_hash(value)
                                             .encode()).hexdigest()
                    hash_by_key[(lang, value_key)] = value_hash
                    keys_by_hash[(lang, row[CARD_SET], value_hash)] = (
                        keys_by_hash.get((lang, row[CARD_SET],
                                          value_hash), []) + [value_key])

                    match = re.search(r' ((?:\[[^\]]+\])+)(?:\n\n|$)', value)
                    if match:
                        logging.error(
                            'Redundant space before "%s" in %s column for '
                            'card ID %s in %s translations, row #%s',
                            match.groups()[0],
                            key.replace(BACK_PREFIX, BACK_PREFIX_LOG), card_id,
                            lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

                    cleaned_value = _clean_tags(value)
                    if key in {CARD_FLAVOUR, BACK_PREFIX + CARD_FLAVOUR}:
                        cleaned_value = cleaned_value.replace('[...]', '')

                    if lang == L_FRENCH:
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
                            key.replace(BACK_PREFIX, BACK_PREFIX_LOG), card_id,
                            lang, TRANSLATIONS[lang][card_id][ROW_COLUMN],
                            ', '.join(unknown_tags))
                    elif '[' in cleaned_value or ']' in cleaned_value:
                        logging.error(
                            'Unmatched square bracket(s) in %s '
                            'column for card ID %s in %s translations, '
                            'row #%s (use "[lsb]" and "[rsb]" tags if needed)',
                            key.replace(BACK_PREFIX, BACK_PREFIX_LOG), card_id,
                            lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])


                    unmatched_tags = _detect_unmatched_tags(value)
                    if unmatched_tags:
                        logging.error(
                            'Unmatched tag(s) in %s column for card ID %s in '
                            '%s translations, row #%s: %s',
                            key.replace(BACK_PREFIX, BACK_PREFIX_LOG), card_id,
                            lang, TRANSLATIONS[lang][card_id][ROW_COLUMN],
                            ', '.join(unmatched_tags))

                    match = re.search(
                        r'[0-9X]\[(attack|defense|willpower|threat)\]', value)
                    if match:
                        logging.error(
                            'Missing space before [%s] in %s column for card '
                            'ID %s in %s translations, row #%s',
                            match.groups()[0],
                            key.replace(BACK_PREFIX, BACK_PREFIX_LOG), card_id,
                            lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

                    if re.search(r'[0-9X ]pp[ .]', value):
                        logging.error(
                            '"[pp]" not "pp" in %s column for card'
                            ' ID %s in %s translations, row #%s',
                            key.replace(BACK_PREFIX, BACK_PREFIX_LOG), card_id,
                            lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

                    if re.search(r'[0-9X] \[pp\]', value):
                        logging.error(
                            'Redundant space before [pp] in %s column for card'
                            ' ID %s in %s translations, row #%s',
                            key.replace(BACK_PREFIX, BACK_PREFIX_LOG), card_id,
                            lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

                    if ':[/b] ' in value:
                        logging.error(
                            '"[/b]:" not ":[/b]" in %s column for card ID %s '
                            'in %s translations, row #%s',
                            key.replace(BACK_PREFIX, BACK_PREFIX_LOG), card_id,
                            lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

                    if ':[/bi] ' in value:
                        logging.error(
                            '"[/bi]:" not ":[/bi]" in %s column for card ID '
                            '%s in %s translations, row #%s',
                            key.replace(BACK_PREFIX, BACK_PREFIX_LOG), card_id,
                            lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

                    if lang != L_FRENCH and '“ ' in value:
                        logging.error(
                            'Redundant space after “ in %s column for card'
                            ' ID %s in %s translations, row #%s',
                            key.replace(BACK_PREFIX, BACK_PREFIX_LOG), card_id,
                            lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

                    if lang != L_FRENCH and ' ”' in value:
                        logging.error(
                            'Redundant space before ” in %s column for card'
                            ' ID %s in %s translations, row #%s',
                            key.replace(BACK_PREFIX, BACK_PREFIX_LOG), card_id,
                            lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

                    if (key in {CARD_TEXT, BACK_PREFIX + CARD_TEXT,
                                CARD_SHADOW, BACK_PREFIX + CARD_SHADOW} and
                            row.get(CARD_TYPE) != T_PRESENTATION and
                            isinstance(row.get(key), str)):
                        value_english = row[key]
                        if key in {CARD_TEXT, CARD_SHADOW}:
                            value_english = value_english.replace(
                                row.get(CARD_NAME) or '', '')
                        else:
                            value_english = value_english.replace(
                                row.get(BACK_PREFIX + CARD_NAME) or '', '')

                        value_translated = value
                        for term_english, lang_dict in TRANSLATION_MATCH:
                            regex_english = _get_regex(term_english)
                            regex_translated = lang_dict.get(lang)
                            if not regex_translated:
                                continue

                            if re.search(regex_english, value_english):
                                value_english = re.sub(regex_english, '',
                                                       value_english)
                                if re.search(regex_translated,
                                             value_translated):
                                    value_translated = re.sub(
                                        regex_translated, '', value_translated)
                                else:
                                    logging.error(
                                        'Missing translation for "%s" in %s '
                                        'column for card ID %s in %s '
                                        'translations, row #%s',
                                        term_english,
                                        key.replace(BACK_PREFIX,
                                                    BACK_PREFIX_LOG),
                                        card_id, lang,
                                        TRANSLATIONS[lang][card_id][ROW_COLUMN])

                        value_english = row[key]
                        value_translated = value
                        if key in {CARD_TEXT, CARD_SHADOW}:
                            value_translated = value_translated.replace(
                                TRANSLATIONS[lang][card_id].get(
                                    CARD_NAME) or '', '')
                        else:
                            value_translated = value_translated.replace(
                                TRANSLATIONS[lang][card_id].get(
                                    BACK_PREFIX + CARD_NAME) or '', '')

                        for term_english, lang_dict in TRANSLATION_MATCH:
                            regex_english = lang_dict.get(L_ENGLISH)
                            regex_translated = lang_dict.get(lang)
                            if not regex_english or not regex_translated:
                                continue

                            if re.search(regex_translated, value_translated):
                                value_translated = re.sub(
                                    regex_translated, '', value_translated)
                                if re.search(regex_english, value_english,
                                             flags=re.IGNORECASE):
                                    value_english = re.sub(
                                        regex_english, '', value_english,
                                        flags=re.IGNORECASE)
                                else:
                                    logging.error(
                                        'Redundant translation for "%s" in %s '
                                        'column for card ID %s in %s '
                                        'translations, row #%s',
                                        term_english,
                                        key.replace(BACK_PREFIX,
                                                    BACK_PREFIX_LOG),
                                        card_id, lang,
                                        TRANSLATIONS[lang][card_id][ROW_COLUMN])

                        value_english = re.sub(
                            r'\n +\n', '\n\n', _clean_tags(row[key])).strip()
                        value_translated = re.sub(
                            r'\n +\n', '\n\n', _clean_tags(value)).strip()

                        paragraphs_english = len(
                            re.split(r'\n{2,}', value_english))
                        paragraphs_translated = len(
                            re.split(r'\n{2,}', value_translated))
                        if paragraphs_english != paragraphs_translated:
                            if row.get(CARD_TYPE) == T_RULES:
                                # logging.warning(
                                #     'Different number of paragraphs in %s '
                                #     'column for card ID %s in %s '
                                #     'translations, row #%s: %s compared to %s '
                                #     'in the English source',
                                #     key.replace(BACK_PREFIX, BACK_PREFIX_LOG),
                                #     card_id, lang,
                                #     TRANSLATIONS[lang][card_id][ROW_COLUMN],
                                #     paragraphs_translated, paragraphs_english)
                                pass
                            else:
                                logging.warning(
                                    'Different number of paragraphs in %s '
                                    'column for card ID %s in %s '
                                    'translations, row #%s: %s compared to %s '
                                    'in the English source',
                                    key.replace(BACK_PREFIX, BACK_PREFIX_LOG),
                                    card_id, lang,
                                    TRANSLATIONS[lang][card_id][ROW_COLUMN],
                                    paragraphs_translated, paragraphs_english)

                        value_english = _add_automatic_tags(row[key],
                                                            lang=L_ENGLISH)
                        value_translated = _add_automatic_tags(value,
                                                               lang=lang)
                        for tag in ('[b]', '[i]', '[bi]'):
                            tags_english = value_english.count(tag)
                            tags_translated = value_translated.count(tag)
                            if tags_english != tags_translated:
                                if (row.get(CARD_TYPE) == T_RULES and
                                        tag != '[bi]'):
                                    # logging.warning(
                                    #     'Different number of %s tags in %s '
                                    #     'column for card ID %s in %s '
                                    #     'translations, row #%s: %s compared '
                                    #     'to %s in the English source', tag,
                                    #     key.replace(BACK_PREFIX,
                                    #                 BACK_PREFIX_LOG),
                                    #     card_id, lang,
                                    #     TRANSLATIONS[lang][card_id][ROW_COLUMN],
                                    #     tags_translated, tags_english)
                                    pass
                                else:
                                    logging.warning(
                                        'Different number of %s tags in %s '
                                        'column for card ID %s in %s '
                                        'translations, row #%s: %s compared '
                                        'to %s in the English source', tag,
                                        key.replace(BACK_PREFIX,
                                                    BACK_PREFIX_LOG),
                                        card_id, lang,
                                        TRANSLATIONS[lang][card_id][ROW_COLUMN],
                                        tags_translated, tags_english)

                    if (key in {CARD_TEXT, BACK_PREFIX + CARD_TEXT,
                                CARD_SHADOW, BACK_PREFIX + CARD_SHADOW,
                                CARD_KEYWORDS, BACK_PREFIX + CARD_KEYWORDS,
                                CARD_VICTORY, BACK_PREFIX + CARD_VICTORY} and
                            row.get(CARD_TYPE) != T_PRESENTATION and
                            isinstance(row.get(key), str)):
                        value_english = re.sub(TAGS_WITH_NUMBERS_REGEX, '',
                                               row[key])
                        if key in {CARD_TEXT, CARD_SHADOW}:
                            value_english = value_english.replace(
                                row.get(CARD_NAME) or '', '')
                        else:
                            value_english = value_english.replace(
                                row.get(BACK_PREFIX + CARD_NAME) or '', '')

                        value_translated = re.sub(TAGS_WITH_NUMBERS_REGEX, '',
                                                  value)
                        if key in {CARD_TEXT, CARD_SHADOW}:
                            value_translated = value_translated.replace(
                                TRANSLATIONS[lang][card_id].get(
                                    CARD_NAME) or '', '')
                        else:
                            value_translated = value_translated.replace(
                                TRANSLATIONS[lang][card_id].get(
                                    BACK_PREFIX + CARD_NAME) or '', '')

                        anchors_issue = False
                        anchors_english = re.findall(ANCHORS_REGEX,
                                                     value_english)
                        anchors_translated = re.findall(ANCHORS_REGEX,
                                                        value_translated)
                        if (sorted(anchors_english) !=
                                sorted(anchors_translated)):
                            _remove_common_elements(anchors_english,
                                                    anchors_translated)
                            anchors_issue = True

                        if (anchors_issue and
                                _split_combined_elements(anchors_english) ==
                                _split_combined_elements(anchors_translated)):
                            anchors_issue = False

                        if ((anchors_issue and not anchors_english and  # pylint: disable=R0916
                             not [a for a in anchors_translated
                                  if a not in {'2', '3'}]) or
                                (anchors_issue and not anchors_translated and
                                 not [a for a in anchors_english
                                      if a not in {'2', '3'}])):
                            if not anchors_english:
                                value_english = _replace_numbers(
                                    value_english, lang=L_ENGLISH)
                            else:
                                value_translated = _replace_numbers(
                                    value_translated, lang=lang)

                            anchors_english = re.findall(ANCHORS_REGEX,
                                                         value_english)
                            anchors_translated = re.findall(ANCHORS_REGEX,
                                                            value_translated)
                            if (sorted(anchors_english) ==
                                    sorted(anchors_translated)):
                                anchors_issue = False
                            else:
                                _remove_common_elements(anchors_english,
                                                        anchors_translated)

                            if (anchors_issue and
                                    _split_combined_elements(
                                        anchors_english) ==
                                    _split_combined_elements(
                                        anchors_translated)):
                                anchors_issue = False

                        if anchors_issue:
                            if (row.get(CARD_TYPE) == T_RULES and
                                    '[' not in ', '.join(anchors_english) and
                                    '[' not in ', '.join(anchors_translated)):
                                # logging.warning(
                                #     'Possibly different content in %s column '
                                #     'for card ID %s in %s translations, row '
                                #     '#%s: "%s" compared to "%s" in the '
                                #     'English source',
                                #     key.replace(BACK_PREFIX, BACK_PREFIX_LOG),
                                #     card_id, lang,
                                #     TRANSLATIONS[lang][card_id][ROW_COLUMN],
                                #     ', '.join(anchors_translated),
                                #     ', '.join(anchors_english))
                                pass
                            else:
                                logging.warning(
                                    'Possibly different content in %s column '
                                    'for card ID %s in %s translations, row '
                                    '#%s: "%s" compared to "%s" in the '
                                    'English source',
                                    key.replace(BACK_PREFIX, BACK_PREFIX_LOG),
                                    card_id, lang,
                                    TRANSLATIONS[lang][card_id][ROW_COLUMN],
                                    ', '.join(anchors_translated),
                                    ', '.join(anchors_english))

                if not value and row.get(key):
                    logging.error(
                        'Missing value for %s column for card ID %s in %s '
                        'translations, row #%s',
                        key.replace(BACK_PREFIX, BACK_PREFIX_LOG), card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])
                elif value and not row.get(key):
                    logging.error(
                        'Redundant value for %s column for card '
                        'ID %s in %s translations, row #%s',
                        key.replace(BACK_PREFIX, BACK_PREFIX_LOG), card_id,
                        lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

            for key, value in TRANSLATIONS[lang][card_id].items():
                if key not in TRANSLATED_COLUMNS:
                    continue

                if isinstance(value, str):
                    value_key = (row[CARD_ID], key)
                    translated_keys = [k for k in keys_by_hash[
                        (lang, row[CARD_SET], hash_by_key[(lang, value_key)])]
                                       if k != value_key]
                    english_keys = [k for k in keys_by_hash[
                        (L_ENGLISH, row[CARD_SET], hash_by_key[(L_ENGLISH,
                                                                value_key)])]
                                    if k != value_key]
                    if sorted(translated_keys) != sorted(english_keys):
                        if translated_keys:
                            translated_keys = ', '.join([
                                '{} for card ID {}'.format(
                                    k[1].replace(BACK_PREFIX, BACK_PREFIX_LOG),
                                    k[0])
                                for k in translated_keys])
                        else:
                            translated_keys = '[nothing]'

                        if english_keys:
                            english_keys = ', '.join([
                                '{} for card ID {}'.format(
                                    k[1].replace(BACK_PREFIX, BACK_PREFIX_LOG),
                                    k[0])
                                for k in english_keys])
                        else:
                            english_keys = '[nothing]'

                        logging.error(
                            'Suspicious value in %s column for card ID %s in '
                            '%s translations, row #%s: it\'s the same as %s, '
                            'but the English source is the same as %s',
                            key.replace(BACK_PREFIX, BACK_PREFIX_LOG), card_id,
                            lang, TRANSLATIONS[lang][card_id][ROW_COLUMN],
                            translated_keys, english_keys)

            if (card_traits is not None and
                    TRANSLATIONS[lang][card_id].get(CARD_TRAITS)):
                card_traits_tr = TRANSLATIONS[lang][card_id][CARD_TRAITS]
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

            if (card_traits_back is not None and
                    TRANSLATIONS[lang][card_id].get(
                        BACK_PREFIX + CARD_TRAITS)):
                card_traits_back_tr = (
                    TRANSLATIONS[lang][card_id][BACK_PREFIX + CARD_TRAITS])
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

            if (card_keywords is not None and
                    TRANSLATIONS[lang][card_id].get(CARD_KEYWORDS)):
                card_keywords_tr = TRANSLATIONS[lang][card_id][CARD_KEYWORDS]
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

            if (card_keywords_back is not None and
                    TRANSLATIONS[lang][card_id].get(
                        BACK_PREFIX + CARD_KEYWORDS)):
                card_keywords_back_tr = (
                    TRANSLATIONS[lang][card_id][BACK_PREFIX + CARD_KEYWORDS])
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
                    TRANSLATIONS[lang][card_id].get(CARD_VICTORY) and
                    (is_positive_or_zero_int(card_victory) or
                     card_type in CARD_TYPES_PAGES) and
                    card_victory !=
                    TRANSLATIONS[lang][card_id][CARD_VICTORY]):
                logging.error(
                    'Incorrect victory points for card '
                    'ID %s in %s translations, row #%s', card_id,
                    lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

            if (card_victory_back is not None and
                    TRANSLATIONS[lang][card_id].get(
                        BACK_PREFIX + CARD_VICTORY) and
                    (is_positive_or_zero_int(card_victory_back) or
                     card_type == T_RULES) and
                    card_victory_back !=
                    TRANSLATIONS[lang][card_id][BACK_PREFIX + CARD_VICTORY]):
                logging.error(
                    'Incorrect victory points back for card '
                    'ID %s in %s translations, row #%s', card_id,
                    lang, TRANSLATIONS[lang][card_id][ROW_COLUMN])

            if (card_text is not None and
                    TRANSLATIONS[lang][card_id].get(CARD_TEXT)):
                card_text_tr = TRANSLATIONS[lang][card_id][CARD_TEXT]
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

            if (card_text_back is not None and
                    TRANSLATIONS[lang][card_id].get(BACK_PREFIX + CARD_TEXT)):
                card_text_back_tr = (
                    TRANSLATIONS[lang][card_id][BACK_PREFIX + CARD_TEXT])
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

            if (card_shadow is not None and
                    TRANSLATIONS[lang][card_id].get(CARD_SHADOW)):
                card_shadow_tr = TRANSLATIONS[lang][card_id][CARD_SHADOW]
                if not _verify_shadow_case(card_shadow_tr, lang):
                    if lang == L_FRENCH:
                        logging.warning(
                            'Shadow effect should probably start with a '
                            'lowercase letter for card ID %s in %s '
                            'translations, row #%s', card_id, lang,
                            TRANSLATIONS[lang][card_id][ROW_COLUMN])
                    else:
                        logging.error(
                            'Shadow effect should start with a capital letter '
                            'for card ID %s in %s translations, row #%s',
                            card_id, lang,
                            TRANSLATIONS[lang][card_id][ROW_COLUMN])
                elif not _verify_period(card_shadow_tr):
                    logging.error(
                        'Missing period at the end of shadow for card ID %s '
                        'in %s translations, row #%s', card_id, lang,
                        TRANSLATIONS[lang][card_id][ROW_COLUMN])

            if (card_shadow_back is not None and
                    TRANSLATIONS[lang][card_id].get(
                        BACK_PREFIX + CARD_SHADOW)):
                card_shadow_back_tr = (
                    TRANSLATIONS[lang][card_id][BACK_PREFIX + CARD_SHADOW])
                if not _verify_shadow_case(card_shadow_back_tr, lang):
                    if lang == L_FRENCH:
                        logging.warning(
                            'Shadow back effect should probably start with a '
                            'lowercase letter for card ID %s in %s '
                            'translations, row #%s', card_id, lang,
                            TRANSLATIONS[lang][card_id][ROW_COLUMN])
                    else:
                        logging.error(
                            'Shadow back effect should start with a capital '
                            'letter for card ID %s in %s translations, row '
                            '#%s', card_id, lang,
                            TRANSLATIONS[lang][card_id][ROW_COLUMN])
                elif not _verify_period(card_shadow_back_tr):
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


def _verify_shadow_case(shadow_text, lang):  # pylint: disable=R0911
    """ Check whether a shadow effect has a correct case or not.
    """
    if (lang == L_ENGLISH and
            re.search(r'^(?:\[[^\]]+\])?Shadow(?:\[[^\]]+\])?: '
                      r'[a-zàáâãäąæçćĉèéêëęìíîïłñńòóôõöœśßùúûüźż]',
                      shadow_text)):
        return False

    if (lang == L_FRENCH and
            re.search(r'^(?:\[[^\]]+\])?Ombre(?:\[[^\]]+\])?: '
                      r'[A-ZÀÁÂÃÄĄÆÇĆĈÈÉÊËĘÌÍÎÏŁÑŃÒÓÔÕÖŒŚßÙÚÛÜŹŻ]',
                      shadow_text)):
        return False

    if (lang == L_GERMAN and
            re.search(r'^(?:\[[^\]]+\])?Schatten(?:\[[^\]]+\])?: '
                      r'[a-zàáâãäąæçćĉèéêëęìíîïłñńòóôõöœśßùúûüźż]',
                      shadow_text)):
        return False

    if (lang == L_ITALIAN and
            re.search(r'^(?:\[[^\]]+\])?Ombra(?:\[[^\]]+\])?: '
                      r'[a-zàáâãäąæçćĉèéêëęìíîïłñńòóôõöœśßùúûüźż]',
                      shadow_text)):
        return False

    if (lang == L_POLISH and
            re.search(r'^(?:\[[^\]]+\])?Cień(?:\[[^\]]+\])?: '
                      r'[a-zàáâãäąæçćĉèéêëęìíîïłñńòóôõöœśßùúûüźż]',
                      shadow_text)):
        return False

    if (lang == L_SPANISH and
            re.search(r'^(?:\[[^\]]+\])?Sombra(?:\[[^\]]+\])?: '
                      r'[a-zàáâãäąæçćĉèéêëęìíîïłñńòóôõöœśßùúûüźż]',
                      shadow_text)):
        return False

    return True


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

    if (CARD_PRINTED_NUMBER in old_card and
            old_card.get(CARD_PRINTED_NUMBER_AUTO)):
        del old_card[CARD_PRINTED_NUMBER]

    if (BACK_PREFIX + CARD_PRINTED_NUMBER in old_card and
            old_card.get(CARD_PRINTED_NUMBER_AUTO)):
        del old_card[BACK_PREFIX + CARD_PRINTED_NUMBER]

    if (CARD_PRINTED_NUMBER in new_card and
            new_card.get(CARD_PRINTED_NUMBER_AUTO)):
        del new_card[CARD_PRINTED_NUMBER]

    if (BACK_PREFIX + CARD_PRINTED_NUMBER in new_card and
            new_card.get(CARD_PRINTED_NUMBER_AUTO)):
        del new_card[BACK_PREFIX + CARD_PRINTED_NUMBER]

    for key in old_card:
        if (key in DISCORD_IGNORE_CHANGES_COLUMNS or
                key in DISCORD_IGNORE_COLUMNS):
            continue

        if key not in new_card:
            diffs.append((key, old_card[key], None))
        elif old_card[key] != new_card[key]:
            diffs.append((key, old_card[key], new_card[key]))

    for key in new_card:
        if (key in DISCORD_IGNORE_CHANGES_COLUMNS or
                key in DISCORD_IGNORE_COLUMNS):
            continue

        if key not in old_card:
            diffs.append((key, None, new_card[key]))

    diffs.sort(key=lambda d:
               CARD_COLUMNS.get(CARD_SIDE_B
                                if d[0] == BACK_PREFIX + CARD_NAME
                                else d[0], 0))
    return diffs


def _fix_flavour_for_discord(value):
    """ Remove redundant tags from the flavour text for the Discord bot.
    """
    parts = value.split('—')
    parts[-1] = parts[-1].replace('[nobr]', ' ')
    value = '—'.join(parts)
    return value


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
    data_raw = [
        {key: value for key, value in row.items() if value is not None}
        for row in DATA if row.get(CARD_ID) and row.get(CARD_SET) and
        row[CARD_SET] in SETS and
        not (SETS[row[CARD_SET]][SET_IGNORE] and
             SETS[row[CARD_SET]][SET_ID] in FOUND_SCRATCH_SETS)]
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
        if not category or row.get(CARD_TYPE) in CARD_TYPES_PLAYER:
            category = 'Player - {}{}'.format(discord_prefix, card_set)
        elif category != card_set:
            category = '{} ({}{})'.format(category, discord_prefix,
                                          card_set)
        else:
            category = '{}{}'.format(discord_prefix, category)

        category = _update_discord_category(category)
        row[CARD_DISCORD_CATEGORY] = category

        if row.get(CARD_FLAVOUR):
            row[CARD_FLAVOUR] = _fix_flavour_for_discord(row[CARD_FLAVOUR])

        if row.get(BACK_PREFIX + CARD_FLAVOUR):
            row[BACK_PREFIX + CARD_FLAVOUR] = _fix_flavour_for_discord(
                row[BACK_PREFIX + CARD_FLAVOUR])

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
            old_dict = json.load(obj)
            old_data = old_dict['data']
            old_sets_by_id = old_dict['sets_by_id']
    except Exception:
        old_data = None
        old_sets_by_id = None

    try:
        with open(DISCORD_CARD_DATA_RAW_PATH, 'r', encoding='utf-8') as obj:
            old_data_raw = json.load(obj)['data']
    except Exception:
        old_data_raw = None

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

    set_changes = {}
    if old_data_raw:
        old_dict = {row[CARD_ID]:row for row in old_data_raw}
        new_dict = {row[CARD_ID]:row for row in data_raw}
        for card_id in new_dict:
            if (card_id in old_dict and
                    old_dict[card_id][CARD_SET] !=
                    new_dict[card_id][CARD_SET]):
                set_changes.setdefault(
                    '{}|{}'.format(old_dict[card_id][CARD_SET],
                                   new_dict[card_id][CARD_SET]),
                    []).append(card_id)

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
                channel_changes.append(('move', diff[1], None))
        elif diff[0][1] == diff[1][1]:
            channel_changes.append(('rename', (diff[0][0], diff[1][0]), None))
        else:
            if ('rename', (diff[0][1], diff[1][1])) not in category_changes:
                channel_changes.append(
                    ('move', (diff[0][0], diff[1][1]), None))

            channel_changes.append(('rename', (diff[0][0], diff[1][0]), None))

    set_names = [s[SET_NAME] for s in SETS.values()
                 if not (s[SET_IGNORE] and s[SET_ID] in FOUND_SCRATCH_SETS)]
    sets_by_id = {s[SET_ID]:s[SET_NAME] for s in SETS.values()
                  if not (s[SET_IGNORE] and s[SET_ID] in FOUND_SCRATCH_SETS)}
    sets_by_code = {
        s[SET_HOB_CODE].lower():s[SET_NAME] for s in SETS.values()
        if s[SET_HOB_CODE] and not (s[SET_IGNORE] and
                                    s[SET_ID] in FOUND_SCRATCH_SETS)}
    playtesting_set_ids = [s[SET_ID] for s in SETS.values()
                           if not s[SET_IGNORE] or s[SET_LOCKED]]
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

    set_name_changes = []
    if old_sets_by_id:
        for set_id in sets_by_id:
            if (set_id in old_sets_by_id and
                    sets_by_id[set_id] != old_sets_by_id[set_id]):
                set_name_changes.append([old_sets_by_id[set_id],
                                         sets_by_id[set_id]])

    output = {'url': url,
              'set_names': set_names,
              'sets_by_id': sets_by_id,
              'sets_by_code': sets_by_code,
              'playtesting_set_ids': playtesting_set_ids,
              'set_and_quest_names': list(ALL_SET_AND_QUEST_NAMES),
              'encounter_set_names': list(ALL_ENCOUNTER_SET_NAMES),
              'card_names': list(ALL_CARD_NAMES[L_ENGLISH]),
              'traits': list(ALL_TRAITS),
              'artwork_ids': artwork_ids,
              'data': data}
    with open(DISCORD_CARD_DATA_PATH, 'w', encoding='utf-8') as obj:
        res = json.dumps(output, ensure_ascii=False)
        obj.write(res)

    output = {'data': data_raw}
    with open(DISCORD_CARD_DATA_RAW_PATH, 'w', encoding='utf-8') as obj:
        res = json.dumps(output, ensure_ascii=False)
        obj.write(res)

    utc_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    if (category_changes or channel_changes or card_changes or set_changes or  # pylint: disable=R0916
            modified_card_ids or set_name_changes):
        output = {'categories': category_changes,
                  'channels': channel_changes,
                  'cards': card_changes,
                  'set_names': set_name_changes,
                  'sets': set_changes,
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

    if name in {CARD_TYPE, BACK_PREFIX + CARD_TYPE}:
        if card_type in CARD_TYPES_DOUBLESIDE_DEFAULT:
            value = card_type
        elif value == T_ENCOUNTER_SIDE_QUEST:
            value = T_ALIAS_SIDE_QUEST
        elif value == T_OBJECTIVE_HERO:
            value = T_OBJECTIVE_ALLY
        elif value == T_OBJECTIVE_LOCATION:
            value = T_LOCATION

        return value

    if name in {CARD_SPHERE, BACK_PREFIX + CARD_SPHERE}:
        if card_type == T_TREASURE:
            value = S_NEUTRAL
        elif card_type in {T_PRESENTATION, T_RULES}:
            value = ''
        elif value in {S_CAVE, S_NOICON, S_NOPROGRESS, S_NOSTAT, S_REGION,
                       S_SMALLTEXTAREA, S_UPGRADED}:
            value = ''
        elif card_type == T_CAMPAIGN:
            value = str(value).upper() if value else 'CAMPAIGN'

        return value

    if name in {CARD_UNIQUE, BACK_PREFIX + CARD_UNIQUE}:
        if value:
            value = '‰'

        return value

    if name in {CARD_VICTORY, BACK_PREFIX + CARD_VICTORY}:
        if card_type in CARD_TYPES_PAGES:
            if value:
                value = 'Page {}'.format(value)
        elif is_positive_or_zero_int(value):
            value = 'VICTORY {}'.format(value)

        return value

    if name == CARD_ENCOUNTER_SET:
        if row[CARD_ADVENTURE]:
            value = row[CARD_ADVENTURE]

        return value

    if name == CARD_TEXT and card_type == T_PRESENTATION:
        value = ''
    elif name == BACK_PREFIX + CARD_TEXT and card_type == T_PRESENTATION:
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
    return (F_PROMO not in extract_flags(card[CARD_FLAGS]) and
            card[CARD_TYPE] not in {T_FULL_ART_LANDSCAPE,
                                    T_FULL_ART_PORTRAIT, T_PRESENTATION} and
            not (card[CARD_TYPE] == T_RULES and card[CARD_SPHERE] == S_BACK))


def _needed_for_dragncards(card):
    """ Check whether a card is needed for DragnCards or not.
    """
    return (card[CARD_TYPE] not in {T_FULL_ART_LANDSCAPE,
                                    T_FULL_ART_PORTRAIT, T_PRESENTATION} and
            not (card[CARD_TYPE] == T_RULES and card[CARD_SPHERE] == S_BACK))


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
        if card_type == T_PLAYER_SIDE_QUEST:
            card_size = 'PlayerQuestCard'
        elif card_type in {T_ENCOUNTER_SIDE_QUEST, T_QUEST}:
            card_size = 'QuestCard'
        elif ((card_type in CARD_TYPES_ENCOUNTER_SIZE or
               B_ENCOUNTER in extract_keywords(row[CARD_KEYWORDS]) or
               row[CARD_BACK] == B_ENCOUNTER) and
              row[CARD_BACK] != B_PLAYER):
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

        side_b = (card_type in CARD_TYPES_DOUBLESIDE_DEFAULT
                  or row[BACK_PREFIX + CARD_NAME])
        if card_type in {T_CAMPAIGN, T_NIGHTMARE}:
            properties.append((CARD_ENGAGEMENT, 'A'))
        elif card_type == row[BACK_PREFIX + CARD_TYPE] == T_CONTRACT:
            properties.append((CARD_ENGAGEMENT, 'A'))
        elif card_type == row[BACK_PREFIX + CARD_TYPE] == T_PLAYER_OBJECTIVE:
            properties.append((CARD_ENGAGEMENT, 'A'))

        fix_linebreaks = card_type not in {T_PRESENTATION, T_RULES}

        if properties:
            if side_b:
                properties.append(('', ''))

            _add_set_xml_properties(card, properties, fix_linebreaks, '    ')

        if side_b:
            if (card_type in CARD_TYPES_DOUBLESIDE_DEFAULT
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

            if card_type in {T_CAMPAIGN, T_NIGHTMARE}:
                properties.append((CARD_ENGAGEMENT, 'B'))
            elif card_type == row[BACK_PREFIX + CARD_TYPE] == T_CONTRACT:
                properties.append((CARD_ENGAGEMENT, 'B'))
            elif (card_type == row[BACK_PREFIX + CARD_TYPE] ==
                  T_PLAYER_OBJECTIVE):
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
        if card_type == T_ALIAS_SIDE_QUEST:
            if encounter_set:
                card_type = T_ENCOUNTER_SIDE_QUEST
            else:
                card_type = T_PLAYER_SIDE_QUEST
        elif card_type == T_ENEMY:
            if 'Ship' in [t.strip() for t in str(traits).split('.')]:
                card_type = T_SHIP_ENEMY
        elif card_type == T_OBJECTIVE:
            if 'Ship' in [t.strip() for t in str(traits).split('.')]:
                card_type = T_SHIP_OBJECTIVE

        sphere = _find_properties(card, 'Sphere')
        sphere = sphere[0].attrib['value'] if sphere else None

        if (not sphere and encounter_set
                and encounter_set.lower().endswith(' - nightmare')
                and card_type in {T_ENCOUNTER_SIDE_QUEST, T_ENEMY, T_LOCATION,
                                  T_OBJECTIVE, T_QUEST, T_SHIP_ENEMY,
                                  T_TREACHERY}):
            sphere = S_NIGHTMARE
        elif sphere == S_NEUTRAL and card_type == T_TREASURE:
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
            row[CARD_BACK] = B_PLAYER
        elif card.attrib.get('size') == 'EncounterCard':
            row[CARD_BACK] = B_ENCOUNTER
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


def _append_cards(res, cards, group_name):
    """ Append cards for the section.
    """
    cards = [c for c in cards if is_int(c[CARD_QUANTITY]) and
             c[CARD_QUANTITY] > 0]
    for card in cards:
        res.append({'databaseId': card[CARD_ID],
                    'quantity': int(card[CARD_QUANTITY]),
                    'loadGroupId': group_name,
                    '_name': card[CARD_ORIGINAL_NAME]
                    })


def _append_cards_octgn(parent, cards):
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


def _filter_section_cards(section):
    """ Group similar cards and remove cards with quantity=0.
    """
    cards = {}
    for card in section:
        if card[CARD_QUANTITY] is None or card[CARD_QUANTITY] <= 0:
            continue

        if card[CARD_ID] in cards:
            cards[card[CARD_ID]][CARD_QUANTITY] += card[CARD_QUANTITY]
            continue

        cards[card[CARD_ID]] = card

    section[:] = list(cards.values())


def _generate_octgn_o8d_player(conf, set_id, set_name):
    """ Generate O8D file with player cards for OCTGN.
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
    _append_cards_octgn(root.findall("./section[@name='Hero']")[0], cards)

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
        res = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
{}""".format(res)
        obj.write(res)


def _generate_octgn_o8d_quest(row):  # pylint: disable=R0912,R0914,R0915
    """ Generate O8D and JSON files for the quest(s).
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
    menus = {}
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
            if key.lower() not in {
                    'sets', 'encounter sets', 'prefix', 'external xml',
                    'remove', 'second quest deck', 'special',
                    'second special', 'setup', 'active setup',
                    'staging setup', 'player', 'main quest', 'extra1',
                    'extra2', 'extra3', 'extra4'}:
                errors.append('Unknown key "{}"'.format(key))
                continue

            if key.lower() not in key_count:
                key_count[key.lower()] = 0
            else:
                key_count[key.lower()] += 1

            if (key.lower() in {'sets', 'encounter sets', 'prefix',
                                'external xml'} and
                    key_count.get(key.lower(), 0) > 0):
                errors.append('Duplicate key "{}"'.format(key))

            rules[(key.lower(), key_count[key.lower()])] = value

        if rules.get(('prefix', 0)):
            quest['prefix'] = rules[('prefix', 0)][0]
            quest['prefix'] = quest['prefix'][:6].upper() + quest['prefix'][6:]

        if not quest['prefix']:
            errors.append('Missing scenario prefix')
            continue

        if not re.match(DECK_PREFIX_REGEX, quest['prefix']):
            errors.append('Incorrect scenario prefix "{}"'
                          .format(rules.get(('prefix', 0), [''])[0]))
            continue

        if quest['prefix'] in prefixes:
            errors.append('Duplicate scenario prefix "{}"'
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
                 and (r[CARD_TYPE] != T_RULES or
                      (r.get(CARD_TEXT) or '') not in {'', 'T.B.D.'} or
                      (r.get(BACK_PREFIX + CARD_TEXT) or '')
                      not in {'', 'T.B.D.'})]

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
            quest['modes'].insert(0, EASY_PREFIX)

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
            main_quest_cards = []
            extra1_cards = []
            extra2_cards = []
            extra3_cards = []
            extra4_cards = []
            for card in cards:
                if not card[CARD_ENCOUNTER_SET]:
                    other_cards.append(_update_card_for_rules(card.copy()))
                elif card[CARD_TYPE] in {T_CAMPAIGN, T_NIGHTMARE, T_QUEST}:
                    quest_cards.append(_update_card_for_rules(card.copy()))
                elif card[CARD_TYPE] == T_RULES:
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
                elif key == 'main quest':
                    mode_errors.extend(_apply_rules(
                        quest_cards, main_quest_cards, value, key))
                elif key == 'extra1':
                    mode_errors.extend(_apply_rules(
                        quest_cards + default_setup_cards + encounter_cards +
                        other_cards, extra1_cards, value, key))
                elif key == 'extra2':
                    mode_errors.extend(_apply_rules(
                        quest_cards + default_setup_cards + encounter_cards +
                        other_cards, extra2_cards, value, key))
                elif key == 'extra3':
                    mode_errors.extend(_apply_rules(
                        quest_cards + default_setup_cards + encounter_cards +
                        other_cards, extra3_cards, value, key))
                elif key == 'extra4':
                    mode_errors.extend(_apply_rules(
                        quest_cards + default_setup_cards + encounter_cards +
                        other_cards, extra4_cards, value, key))

            setup_cards.extend(default_setup_cards)

            if len(main_quest_cards) > 1:
                mode_errors.append('More than one card in Main Quest section')

            quest_cards_octgn = copy.deepcopy(quest_cards)
            quest_cards_octgn.extend(main_quest_cards)
            main_quest_cards = copy.deepcopy(main_quest_cards)

            setup_cards_octgn = copy.deepcopy(setup_cards)
            for card in (extra1_cards + extra2_cards + extra3_cards +
                         extra4_cards):
                if card[CARD_TYPE] == 'quest':
                    quest_cards_octgn.append(card)
                else:
                    setup_cards_octgn.append(card)

            extra1_cards = copy.deepcopy(extra1_cards)
            extra2_cards = copy.deepcopy(extra2_cards)
            extra3_cards = copy.deepcopy(extra3_cards)
            extra4_cards = copy.deepcopy(extra4_cards)

            for section in (
                    quest_cards, second_quest_cards, encounter_cards,
                    special_cards, second_special_cards, setup_cards,
                    staging_setup_cards, active_setup_cards, main_quest_cards,
                    extra1_cards, extra2_cards, extra3_cards, extra4_cards,
                    chosen_player_cards, quest_cards_octgn, setup_cards_octgn):
                _filter_section_cards(section)
                section.sort(key=lambda card: (
                    card[CARD_TYPE] != 'rules',
                    card[CARD_TYPE] not in {'campaign', 'nightmare'},
                    card[CARD_TYPE],
                    card[CARD_TYPE] == 'quest' and (card[CARD_COST] or 0) or 0,
                    card[CARD_SET_NAME],
                    is_positive_or_zero_int(card[CARD_NUMBER])
                    and int(card[CARD_NUMBER]) or 0,
                    card[CARD_NUMBER] or '',
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
                else:
                    mode_errors.append(
                        'Card "{}" with type "{}" can\'t be added to the deck'
                        .format(card[CARD_ORIGINAL_NAME],
                                card[CARD_TYPE].title()))

            root = ET.fromstring(O8D_TEMPLATE)
            for path, section in (
                    ("./section[@name='Hero']", hero_cards),
                    ("./section[@name='Ally']", ally_cards),
                    ("./section[@name='Attachment']", attachment_cards),
                    ("./section[@name='Event']", event_cards),
                    ("./section[@name='Side Quest']", side_quest_cards),
                    ("./section[@name='Quest']", quest_cards_octgn),
                    ("./section[@name='Second Quest Deck']",
                     second_quest_cards),
                    ("./section[@name='Encounter']", encounter_cards),
                    ("./section[@name='Special']", special_cards),
                    ("./section[@name='Second Special']",
                     second_special_cards),
                    ("./section[@name='Setup']", setup_cards_octgn),
                    ("./section[@name='Staging Setup']", staging_setup_cards),
                    ("./section[@name='Active Setup']", active_setup_cards)):
                _append_cards_octgn(root.findall(path)[0], section)

            if mode == EASY_PREFIX and quest['prefix'].startswith('Q'):
                prefix = '{}{}'.format('E', quest['prefix'][1:])
            else:
                prefix = '{}{}'.format(mode, quest['prefix'])

            parts = prefix.split('-', 1)
            prefix = parts[0]
            name_prefix = '{} '.format(parts[1]) if len(parts) == 2 else ''
            quest_name = '{}{}'.format(name_prefix, quest['name'])

            filename = escape_octgn_filename(escape_filename(
                '{} {}.o8d'.format(prefix, quest_name)))
            res = ET.tostring(root, encoding='utf-8').decode('utf-8')
            res = res.replace('<notes />', '<notes><![CDATA[]]></notes>')
            res = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
{}""".format(res)
            files.append((filename, res))

            filename = re.sub(r'\.o8d$', '.json', filename)
            res = []
            for section, group_name in (
                    (chosen_player_cards, 'player1Play1'),
                    (main_quest_cards, 'sharedMainQuest'),
                    (quest_cards, 'sharedQuestDeck'),
                    (second_quest_cards, 'sharedQuestDeck2'),
                    (encounter_cards, 'sharedEncounterDeck'),
                    (special_cards, 'sharedEncounterDeck2'),
                    (second_special_cards, 'sharedEncounterDeck3'),
                    (setup_cards, 'sharedSetAside'),
                    (extra1_cards, 'sharedExtra1'),
                    (extra2_cards, 'sharedExtra2'),
                    (extra3_cards, 'sharedExtra3'),
                    (extra4_cards, 'sharedExtra4'),
                    (staging_setup_cards, 'sharedStagingArea'),
                    (active_setup_cards, 'sharedActiveLocation')):
                _append_cards(res, section, group_name)

            if prefix[0] == 'E':
                name_suffix = ' (Easy)'
            elif prefix[0] == 'N':
                name_suffix = ' (Nightmare)'
            else:
                name_suffix = ''

            res = {'preBuiltDecks': {
                prefix: {'label': '{}{}'.format(quest_name, name_suffix),
                         'cards': res}}}
            res = json.dumps(res, ensure_ascii=True, indent=4)
            res = re.sub(r'(?<=,)\n                    ([^\n]+)', ' \\1', res)
            res = res.replace('{\n                    ', '{')
            res = res.replace('\n                }', '}')
            files.append((filename, res))

            if prefix[0] == 'E':
                label = 'id:easy'
            elif prefix[0] == 'N':
                label = 'id:nightmare'
            else:
                label = 'id:normal'

            if quest_name in menus:
                menus[quest_name]['deckLists'].append(
                    {'label': label, 'deckListId': prefix})
            else:
                menus[quest_name]= {
                    'label': quest_name,
                    'deckLists': [{'label': label, 'deckListId': prefix}]}

            if mode == EASY_PREFIX:
                mode_errors = ['{} in easy mode'.format(e)
                               for e in mode_errors]

            errors.extend(mode_errors)

    menus = list(menus.values())
    return (files, menus, errors)


def generate_octgn_o8d(conf, set_id, set_name):
    """ Generate O8D and JSON files for OCTGN and DragnCards.
    """
    logging.info('[%s] Generating O8D and JSON files for OCTGN and '
                 'DragnCards...', set_name)
    timestamp = time.time()

    files = []
    menus = []
    rows = [row for row in DATA
            if row[CARD_SET] == set_id
            and row[CARD_TYPE] in CARD_TYPES_DECK_RULES
            and row[CARD_DECK_RULES]
            and (not conf['selected_only'] or row[CARD_ID] in SELECTED_CARDS)]
    for row in rows:
        res = _generate_octgn_o8d_quest(row)
        files.extend(res[0])
        menus.extend(res[1])

    output_path = os.path.join(OUTPUT_OCTGN_DECKS_PATH,
                               escape_filename(set_name))
    clear_folder(output_path)
    if files or menus:
        create_folder(output_path)

    for filename, res in files:
        with open(
                os.path.join(output_path, filename),
                'w', encoding='utf-8') as obj:
            obj.write(res)

    if menus:
        json_data = {'deckMenu': {
            'subMenus': [{'label': DRAGNCARDS_MENU_LABEL, 'subMenus': menus}]}}
        with open(os.path.join(output_path, '{}.menu.json'.format(set_id)),
                  'w', encoding='utf-8') as obj:
            json.dump(json_data, obj, ensure_ascii=True, indent=4)

    _generate_octgn_o8d_player(conf, set_id, set_name)

    logging.info('[%s] ...Generating O8D and JSON files for OCTGN and '
                 'DragnCards (%ss)', set_name,
                 round(time.time() - timestamp, 3))


def _needed_for_ringsdb(card):
    """ Check whether a card is needed for RingsDB or not.
    """
    return (card.get(CARD_TYPE) in CARD_TYPES_PLAYER or
            card.get(CARD_SPHERE) in CARD_SPHERES_BOON or
            card.get(CARD_SPHERE) == S_BURDEN)


def _needed_for_frenchdb(card):
    """ Check whether a card is needed for the French database or not.
    """
    return (card[CARD_TYPE] not in
            {T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT, T_PRESENTATION,
             T_RULES} and
            F_PROMO not in extract_flags(card[CARD_FLAGS]))


def _needed_for_frenchdb_images(card):
    """ Check whether a card is needed for the French database images or not.
    """
    return (card[CARD_TYPE] not in
            {T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT, T_PRESENTATION} and
            not (card[CARD_TYPE] == T_RULES and
                 card[CARD_SPHERE] == S_BACK) and
            F_PROMO not in extract_flags(card[CARD_FLAGS]))


def _needed_for_spanishdb(card):
    """ Check whether a card is needed for the Spanish database or not.
    """
    return (card[CARD_TYPE] not in
            {T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT, T_PRESENTATION} and
            not (card[CARD_TYPE] == T_RULES and
                 card[CARD_SPHERE] == S_BACK) and
            F_PROMO not in extract_flags(card[CARD_FLAGS]))


def _ringsdb_code(row):
    """ Return the card's RingsDB code.
    """
    if is_positive_or_zero_int(row[CARD_NUMBER]):
        card_number = str(int(row[CARD_NUMBER])).zfill(3)
    elif re.match(r'^0\.[0-9a-f]$', str(row[CARD_NUMBER]),
                  flags=re.IGNORECASE):
        card_number = str(
            999 - 16 + int(str(row[CARD_NUMBER])[-1], 16)).zfill(3)
    else:
        card_number = '000'
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

            if row[CARD_TYPE] == T_HERO:
                cost = None
                threat = handle_int(row[CARD_COST])
            else:
                cost = handle_int(row[CARD_COST])
                threat = None

            if row[CARD_SPHERE] == S_BURDEN:
                willpower = handle_int(row[CARD_THREAT])
            else:
                willpower = handle_int(row[CARD_WILLPOWER])

            if (row[CARD_TYPE] in {T_CONTRACT, T_PLAYER_OBJECTIVE,
                                   T_TREASURE} or
                    row[CARD_SPHERE] in CARD_SPHERES_BOON or
                    row[CARD_SPHERE] == S_BURDEN):
                sphere = S_NEUTRAL
            else:
                sphere = row[CARD_SPHERE]

            if row[CARD_TYPE] == T_PLAYER_OBJECTIVE:
                card_type = T_CONTRACT
            elif (row[CARD_TYPE] == T_TREASURE or
                  row[CARD_SPHERE] in CARD_SPHERES_BOON or
                  row[CARD_SPHERE] == S_BURDEN):
                card_type = T_CAMPAIGN
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

            ringsdb_code = _ringsdb_code(row)
            csv_row = {
                'pack': set_name,
                'type': card_type,
                'sphere': sphere,
                'position': int(ringsdb_code[-3:]),
                'code': ringsdb_code,
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

            if (csv_row['type'] == T_ALLY and csv_row['isUnique'] == 1 and
                    csv_row['sphere'] != S_NEUTRAL):
                new_row = csv_row.copy()
                new_row['pack'] = 'ALeP - Messenger of the King Allies'
                new_row['type'] = T_HERO
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


def _generate_tsv_from_json(json_data, output_path, release):  # pylint: disable=R0912
    """ Generate DragnCards TSV from JSON.
    """
    with open(output_path, 'w', newline='', encoding='utf-8') as obj:
        fieldnames = ['databaseId', 'name', 'imageUrl', 'cardBack', 'type',
                      'packName', 'deckbuilderQuantity', 'setUuid',
                      'numberInPack', 'encounterSet', 'unique', 'sphere',
                      'traits', 'keywords', 'cost', 'engagementCost', 'threat',
                      'willpower', 'attack', 'defense', 'hitPoints',
                      'questPoints', 'victoryPoints', 'cornerText', 'text',
                      'shadow', 'side']

        if not release:
            fieldnames.append('modifiedTimeUtc')

        writer = csv.DictWriter(obj, delimiter='\t', fieldnames=fieldnames)
        writer.writeheader()
        for row in sorted(json_data.values(),
                          key=lambda r: str(r['cardnumber']).zfill(3)):
            if row['sides']['B']['name'] in {'player', 'encounter'}:
                card_back = row['sides']['B']['name']
            else:
                card_back = 'multi_sided'

            if row['sides']['A']['type'] == T_QUEST:
                engagement_cost = ''
                side = row['sides']['A']['engagementcost']
            else:
                engagement_cost = row['sides']['A']['engagementcost']
                side = ''

            if (row['sides']['A']['victorypoints'] and
                    not is_int(row['sides']['A']['victorypoints'])):
                victory_points = ''
                corner_text = row['sides']['A']['victorypoints']
            else:
                victory_points = row['sides']['A']['victorypoints']
                corner_text = ''

            tsv_row = {
                'databaseId': row['cardid'],
                'name': row['sides']['A']['printname'],
                'imageUrl': '{}.jpg'.format(row['cardid']),
                'cardBack': card_back,
                'type': row['sides']['A']['type'],
                'packName': row['cardpackname'],
                'deckbuilderQuantity': row['cardquantity'],
                'setUuid': row['cardsetid'],
                'numberInPack': row['cardnumber'],
                'encounterSet': row['cardencounterset'],
                'unique': row['sides']['A']['unique'],
                'sphere': row['sides']['A']['sphere'],
                'traits': row['sides']['A']['traits'],
                'keywords': row['sides']['A']['keywords'],
                'cost': row['sides']['A']['cost'],
                'engagementCost': engagement_cost,
                'threat': row['sides']['A']['threat'],
                'willpower': row['sides']['A']['willpower'],
                'attack': row['sides']['A']['attack'],
                'defense': row['sides']['A']['defense'],
                'hitPoints': row['sides']['A']['hitpoints'],
                'questPoints': row['sides']['A']['questpoints'],
                'victoryPoints': victory_points,
                'cornerText': corner_text,
                'text': row['sides']['A']['text'].replace('\n', ' '),
                'shadow': row['sides']['A']['shadow'].replace('\n', ' '),
                'side': side
            }
            if not release:
                if 'modifiedtimeutc' in row:
                    tsv_row['modifiedTimeUtc'] = row['modifiedtimeutc']
                else:
                    tsv_row['modifiedTimeUtc'] = ''

            writer.writerow(tsv_row)
            if card_back == 'multi_sided':
                if row['sides']['B']['type'] == T_QUEST:
                    engagement_cost = ''
                    side = row['sides']['B']['engagementcost']
                else:
                    engagement_cost = row['sides']['B']['engagementcost']
                    side = ''

                if (row['sides']['B']['victorypoints'] and
                        not is_int(row['sides']['B']['victorypoints'])):
                    victory_points = ''
                    corner_text = row['sides']['B']['victorypoints']
                else:
                    victory_points = row['sides']['B']['victorypoints']
                    corner_text = ''

                tsv_row = {
                    'databaseId': row['cardid'],
                    'name': row['sides']['B']['printname'],
                    'imageUrl': '{}.B.jpg'.format(row['cardid']),
                    'cardBack': card_back,
                    'type': row['sides']['B']['type'],
                    'packName': row['cardpackname'],
                    'deckbuilderQuantity': row['cardquantity'],
                    'setUuid': row['cardsetid'],
                    'numberInPack': row['cardnumber'],
                    'encounterSet': row['cardencounterset'],
                    'unique': row['sides']['B']['unique'],
                    'sphere': row['sides']['B']['sphere'],
                    'traits': row['sides']['B']['traits'],
                    'keywords': row['sides']['B']['keywords'],
                    'cost': row['sides']['B']['cost'],
                    'engagementCost': engagement_cost,
                    'threat': row['sides']['B']['threat'],
                    'willpower': row['sides']['B']['willpower'],
                    'attack': row['sides']['B']['attack'],
                    'defense': row['sides']['B']['defense'],
                    'hitPoints': row['sides']['B']['hitpoints'],
                    'questPoints': row['sides']['B']['questpoints'],
                    'victoryPoints': victory_points,
                    'cornerText': corner_text,
                    'text': row['sides']['B']['text'].replace('\n', ' '),
                    'shadow': row['sides']['B']['shadow'].replace('\n', ' '),
                    'side': side
                }
                if not release:
                    if 'modifiedtimeutc' in row:
                        tsv_row['modifiedTimeUtc'] = row['modifiedtimeutc']
                    else:
                        tsv_row['modifiedTimeUtc'] = ''

                writer.writerow(tsv_row)


def generate_dragncards_json(conf, set_id, set_name):  # pylint: disable=R0912,R0914,R0915
    """ Generate JSON and TSV files for DragnCards.
    """
    logging.info('[%s] Generating JSON and TSV files for DragnCards...',
                 set_name)
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

        if row[CARD_TYPE] in {T_ENCOUNTER_SIDE_QUEST, T_PLAYER_SIDE_QUEST}:
            card_type = T_ALIAS_SIDE_QUEST
        else:
            card_type = row[CARD_TYPE]

        if row[CARD_TYPE] == T_TREASURE:
            sphere = S_NEUTRAL
        elif row[CARD_SPHERE] in {S_CAVE, S_NOICON, S_NOPROGRESS, S_NOSTAT,
                                  S_REGION, S_SETUP, S_SMALLTEXTAREA,
                                  S_UPGRADED}:
            sphere = ''
        else:
            sphere = row[CARD_SPHERE]

        if row[CARD_TYPE] == T_RULES and row[CARD_VICTORY]:
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
            if row[BACK_PREFIX + CARD_TYPE] == T_ENCOUNTER_SIDE_QUEST:
                card_type = T_ALIAS_SIDE_QUEST
            else:
                card_type = row[BACK_PREFIX + CARD_TYPE]

            if row[BACK_PREFIX + CARD_TYPE] == T_TREASURE:
                sphere = S_NEUTRAL
            elif row[BACK_PREFIX + CARD_SPHERE] in {
                    S_CAVE, S_NOICON, S_NOPROGRESS, S_NOSTAT, S_REGION,
                    S_SETUP, S_SMALLTEXTAREA, S_UPGRADED}:
                sphere = ''
            else:
                sphere = row[BACK_PREFIX + CARD_SPHERE]

            if (row[BACK_PREFIX + CARD_TYPE] == T_RULES and
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
                 B_ENCOUNTER not in extract_keywords(row[CARD_KEYWORDS]) and
                 row[CARD_BACK] != B_ENCOUNTER) or
                    row[CARD_BACK] == B_PLAYER):
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

    tsv_path = re.sub(r'\.json$', '.tsv', output_path)
    _generate_tsv_from_json(json_data, tsv_path, release=False)

    for card in json_data.values():
        if 'playtest' in card:
            del card['playtest']

        if 'modifiedtimeutc' in card:
            del card['modifiedtimeutc']

    output_path = '{}.release'.format(output_path)
    with open(output_path, 'w', encoding='utf-8') as obj:
        res = json.dumps(json_data, ensure_ascii=True, indent=4)
        obj.write(res)

    tsv_path = '{}.release'.format(tsv_path)
    _generate_tsv_from_json(json_data, tsv_path, release=True)

    with open(DRAGNCARDS_TIMESTAMPS_JSON_PATH, 'w', encoding='utf-8') as fobj:
        json.dump(dragncards_timestamps, fobj)

    logging.info('[%s] ...Generating JSON and TSV files for DragnCards (%ss)',
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
                not is_doubleside(row[CARD_TYPE],
                                  row[BACK_PREFIX + CARD_TYPE])):
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

        if lang == L_ENGLISH:
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

        if card_type == T_HERO:
            cost = None
            threat = _handle_int_str(row[CARD_COST])
            quest_stage = None
            engagement_cost = None
            quest_points = None
            stage_letter = None
            opposite_stage_letter = None
        elif card_type == T_QUEST:
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

        if card_type in {T_CONTRACT, T_PLAYER_OBJECTIVE, T_TREASURE}:
            sphere = S_NEUTRAL
        elif card_type in {T_CAMPAIGN, T_PRESENTATION, T_RULES}:
            sphere = 'None'
        elif row[CARD_SPHERE] in {S_CAVE, S_NIGHTMARE, S_NOICON, S_NOPROGRESS,
                                  S_NOSTAT, S_REGION, S_SMALLTEXTAREA,
                                  S_UPGRADED}:
            sphere = 'None'
        elif row[CARD_SPHERE] is not None:
            sphere = row[CARD_SPHERE]
        else:
            sphere = 'None'

        if sphere in CARD_SPHERES_BOON:
            sphere = S_NEUTRAL
            subtype_name = S_BOON
        elif sphere == S_BURDEN:
            sphere = 'None'
            subtype_name = S_BURDEN
        else:
            subtype_name = None

        if row.get(CARD_DOUBLESIDE) is not None:
            card_side = row[CARD_DOUBLESIDE]
        elif (row[BACK_PREFIX + CARD_NAME] is not None and
              not is_doubleside(card_type, row[BACK_PREFIX + CARD_TYPE])):
            card_side = 'A'
        else:
            card_side = None

        if (translated_row.get(BACK_PREFIX + CARD_NAME) is not None and
                translated_row[BACK_PREFIX + CARD_NAME] !=
                translated_row.get(CARD_NAME, '') and
                is_doubleside(card_type, row[BACK_PREFIX + CARD_TYPE])):
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

        if card_type in {T_PRESENTATION, T_RULES}:
            type_name = S_SETUP
        elif card_type == T_NIGHTMARE:
            type_name = 'Nightmare Setup'
        elif card_type in {T_FULL_ART_LANDSCAPE, T_FULL_ART_PORTRAIT}:
            type_name = 'None'
        elif (card_type == T_ENCOUNTER_SIDE_QUEST and
              row[CARD_SPHERE] == S_CAVE):
            type_name = S_CAVE
        elif (card_type == T_ENCOUNTER_SIDE_QUEST and
              row[CARD_SPHERE] == S_REGION):
            type_name = S_REGION
        else:
            type_name = card_type or ''

        if card_type in CARD_TYPES_PAGES:
            victory_points = None
        elif is_doubleside(card_type, row[BACK_PREFIX + CARD_TYPE]):
            victory_points = (
                _handle_int_str(translated_row.get(CARD_VICTORY))
                or _handle_int_str(translated_row.get(
                    BACK_PREFIX + CARD_VICTORY)))
        else:
            victory_points = _handle_int_str(translated_row.get(CARD_VICTORY))

        tokens = []
        if row[CARD_ICONS] is not None:
            tokens.extend(re.split(r'(?<=\])(?=\[)', row[CARD_ICONS]))

        if victory_points is not None and not is_int(victory_points):
            tokens.append(victory_points)
            victory_points = None

        if not tokens:
            tokens = None

        additional_encounter_sets = [
            s.strip() for s in str(row[CARD_ADDITIONAL_ENCOUNTER_SETS] or ''
                                   ).split(';')
            if s.strip()] or None

        fix_linebreaks = card_type not in {T_PRESENTATION, T_RULES}

        text = _update_card_text('{}\n\n{}'.format(
            translated_row.get(CARD_KEYWORDS) or '',
            translated_row.get(CARD_TEXT) or ''
            ), fix_linebreaks=fix_linebreaks).replace('\n', '\r\n').strip()
        if (card_type in CARD_TYPES_PAGES and
                translated_row.get(CARD_VICTORY) is not None):
            text = '{}\r\n\r\nPage {}'.format(text,
                                              translated_row[CARD_VICTORY])

        if (translated_row.get(BACK_PREFIX + CARD_NAME) is not None and
                (translated_row.get(BACK_PREFIX + CARD_TEXT) is not None or
                 (card_type in CARD_TYPES_PAGES
                  and translated_row.get(BACK_PREFIX + CARD_VICTORY)
                  is not None)) and
                is_doubleside(card_type, row[BACK_PREFIX + CARD_TYPE])):
            text_back = _update_card_text(
                translated_row.get(BACK_PREFIX + CARD_TEXT) or '',
                fix_linebreaks=fix_linebreaks
                ).replace('\n', '\r\n').strip()
            if (card_type in CARD_TYPES_PAGES and
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
                is_doubleside(card_type, row[BACK_PREFIX + CARD_TYPE])):
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

            french_row = TRANSLATIONS[L_FRENCH].get(row[CARD_ID], {}).copy()

            if row[CARD_TYPE] in {T_CONTRACT, T_PLAYER_OBJECTIVE}:
                sphere = S_NEUTRAL
            elif row[CARD_SPHERE] in CARD_SPHERES_BOON:
                sphere = None
            elif row[CARD_SPHERE] == S_UPGRADED:
                sphere = None
            else:
                sphere = row[CARD_SPHERE]

            if row[CARD_TYPE] == T_HERO:
                cost = None
                threat = _update_french_non_int(handle_int(row[CARD_COST]))
            else:
                cost = _update_french_non_int(handle_int(row[CARD_COST]))
                threat = None

            text = _update_french_card_text('{}\n\n{}'.format(
                french_row.get(CARD_KEYWORDS) or '',
                french_row.get(CARD_TEXT) or '')).strip()

            if ((is_doubleside(row[CARD_TYPE], row[BACK_PREFIX + CARD_TYPE]) or
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
                    row[CARD_TYPE] == T_QUEST):
                continue

            french_row = TRANSLATIONS[L_FRENCH].get(row[CARD_ID], {}).copy()

            if row[CARD_SPHERE] == S_SETUP:
                card_type = T_NIGHTMARE
            else:
                card_type = row[CARD_TYPE]

            text = _update_french_card_text('{}\n\n{}'.format(
                french_row.get(CARD_KEYWORDS) or '',
                french_row.get(CARD_TEXT) or '')).strip()

            if ((is_doubleside(row[CARD_TYPE], row[BACK_PREFIX + CARD_TYPE])
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
            if row[CARD_TYPE] != T_QUEST:
                continue

            french_row = TRANSLATIONS[L_FRENCH].get(row[CARD_ID], {})

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
                     row[CARD_TYPE] == T_PRESENTATION]
    if presentations:
        spanish_name = TRANSLATIONS[L_SPANISH].get(
            presentations[0][CARD_ID], {}).get(CARD_NAME)
        if spanish_name:
            cycle = spanish_name

    data = DATA[:]
    for row in DATA:
        if (row[BACK_PREFIX + CARD_NAME] is not None and
                not is_doubleside(row[CARD_TYPE],
                                  row[BACK_PREFIX + CARD_TYPE])):
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
                    row[CARD_TYPE] == T_RULES):
                continue

            spanish_row = TRANSLATIONS[L_SPANISH].get(row[CARD_ID], {}).copy()
            if row.get(CARD_DOUBLESIDE):
                spanish_row[CARD_NAME] = spanish_row.get(
                    BACK_PREFIX + CARD_NAME, '')
                for key in spanish_row.keys():
                    if key.startswith(BACK_PREFIX):
                        spanish_row[key.replace(BACK_PREFIX, '')] = (
                            spanish_row[key])

            name = spanish_row.get(CARD_NAME)
            if (is_doubleside(row[CARD_TYPE], row[BACK_PREFIX + CARD_TYPE]) and
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
            if row[CARD_TYPE] == T_QUEST:
                quest_points = handle_int(row[BACK_PREFIX + CARD_QUEST])
                engagement = handle_int(row[CARD_COST])
                threat = '{}-{}'.format(
                    row[CARD_ENGAGEMENT] or '',
                    row[BACK_PREFIX + CARD_ENGAGEMENT] or '')
            else:
                quest_points = handle_int(row[CARD_QUEST])
                engagement = handle_int(row[CARD_ENGAGEMENT])
                threat = handle_int(row[CARD_THREAT])

            if is_doubleside(row[CARD_TYPE], row[BACK_PREFIX + CARD_TYPE]):
                victory_points = (
                    handle_int(spanish_row.get(BACK_PREFIX + CARD_VICTORY))
                    if spanish_row.get(BACK_PREFIX + CARD_VICTORY) is not None
                    else handle_int(spanish_row.get(CARD_VICTORY))
                    )
            else:
                victory_points = handle_int(spanish_row.get(CARD_VICTORY))

            text = _update_card_text('{}\n\n{}'.format(
                spanish_row.get(CARD_KEYWORDS) or '',
                spanish_row.get(CARD_TEXT) or ''), lang=L_SPANISH).strip()
            if text:
                text = '<p>{}</p>'.format(text.replace('\n', '</p><p>'))

            if spanish_row.get(CARD_SHADOW) is not None:
                shadow = _update_card_text(spanish_row.get(CARD_SHADOW),
                                           lang=L_SPANISH).strip()
            elif (is_doubleside(row[CARD_TYPE],
                                row[BACK_PREFIX + CARD_TYPE]) and
                  spanish_row.get(BACK_PREFIX + CARD_TEXT) is not None):
                shadow = _update_card_text('{}\n\n{}'.format(
                    spanish_row.get(BACK_PREFIX + CARD_KEYWORDS) or '',
                    spanish_row.get(BACK_PREFIX + CARD_TEXT)),
                                           lang=L_SPANISH).strip()
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
                    and row[CARD_TYPE] != T_RULES):
                continue

            spanish_row = TRANSLATIONS[L_SPANISH].get(row[CARD_ID], {}).copy()
            if row.get(CARD_DOUBLESIDE):
                spanish_row[CARD_NAME] = spanish_row.get(
                    BACK_PREFIX + CARD_NAME, '')
                for key in spanish_row.keys():
                    if key.startswith(BACK_PREFIX):
                        spanish_row[key.replace(BACK_PREFIX, '')] = (
                            spanish_row[key])

            if row[CARD_TYPE] in {T_CONTRACT, T_PLAYER_OBJECTIVE, T_TREASURE}:
                sphere = S_NEUTRAL
            else:
                sphere = row[CARD_SPHERE]

            if row[CARD_TYPE] == T_HERO:
                cost = None
                threat = handle_int(row[CARD_COST])
            else:
                cost = handle_int(row[CARD_COST])
                threat = None

            text = _update_card_text('{}\n\n{}'.format(
                spanish_row.get(CARD_KEYWORDS) or '',
                spanish_row.get(CARD_TEXT) or ''), lang=L_SPANISH).strip()
            if (row[CARD_TYPE] == T_RULES and
                    spanish_row.get(CARD_VICTORY) is not None):
                text = '{}\n\nPage {}'.format(text, spanish_row[CARD_VICTORY])

            if text:
                text = '<p>{}</p>'.format(text.replace('\n', '</p><p>'))

            if (is_doubleside(row[CARD_TYPE], row[BACK_PREFIX + CARD_TYPE]) and
                    spanish_row.get(BACK_PREFIX + CARD_TEXT)):
                text_back = _update_card_text('{}\n\n{}'.format(
                    spanish_row.get(BACK_PREFIX + CARD_KEYWORDS) or '',
                    spanish_row[BACK_PREFIX + CARD_TEXT]),
                                              lang=L_SPANISH).strip()
                if (row[CARD_TYPE] == T_RULES and
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
                                       lang=L_SPANISH,
                                       skip_rules=True,
                                       fix_linebreaks=False).strip()
            if flavor:
                flavor = '<p>{}</p>'.format(flavor.replace('\n', '</p><p>'))

            if (is_doubleside(row[CARD_TYPE], row[BACK_PREFIX + CARD_TYPE]) and
                    spanish_row.get(BACK_PREFIX + CARD_FLAVOUR)):
                flavor_back = _update_card_text(
                    spanish_row[BACK_PREFIX + CARD_FLAVOUR], lang=L_SPANISH,
                    skip_rules=True, fix_linebreaks=False).strip()
                if flavor_back:
                    flavor_back = '<p>{}</p>'.format(
                        flavor_back.replace('\n', '</p><p>'))

                flavor = (
                    '<p><b>Lado A.</b></p>\n{}\n<p><b>Lado B.</b></p>\n{}'
                    .format(flavor, flavor_back))

            if row[CARD_TYPE] == T_RULES:
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

    if name in {CARD_TYPE, BACK_PREFIX + CARD_TYPE}:
        if card_type in CARD_TYPES_DOUBLESIDE_DEFAULT:
            value = card_type

        return value

    if name in {CARD_SPHERE, BACK_PREFIX + CARD_SPHERE}:
        if card_type == T_RULES:
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
        if lang != L_ENGLISH and TRANSLATIONS[lang].get(row[CARD_ID]):
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
        if lang != L_ENGLISH and TRANSLATIONS[lang].get(row[CARD_ID]):
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
                                 CARD_QUEST, CARD_VICTORY, CARD_TEXT, CARD_SHADOW,
                                 CARD_ICONS, CARD_INFO, CARD_ADVENTURE}

        card_type = row[CARD_TYPE]
        properties = []
        for name in (CARD_NUMBER, CARD_QUANTITY, CARD_ENCOUNTER_SET,
                     CARD_UNIQUE, CARD_TYPE, CARD_SPHERE, CARD_TRAITS,
                     CARD_KEYWORDS, CARD_COST, CARD_ENGAGEMENT, CARD_THREAT,
                     CARD_WILLPOWER, CARD_ATTACK, CARD_DEFENSE, CARD_HEALTH,
                     CARD_QUEST, CARD_VICTORY, CARD_TEXT, CARD_SHADOW,
                     CARD_FLAVOUR, CARD_PRINTED_NUMBER,
                     CARD_ENCOUNTER_SET_NUMBER, CARD_ENCOUNTER_SET_ICON,
                     CARD_FLAGS, CARD_ICONS, CARD_INFO, CARD_ARTIST, CARD_PANX,
                     CARD_PANY, CARD_SCALE, CARD_PORTRAIT_SHADOW,
                     CARD_EASY_MODE, CARD_ADDITIONAL_ENCOUNTER_SETS,
                     CARD_ADVENTURE, CARD_COLLECTION_ICON, CARD_COPYRIGHT,
                     CARD_BACK, CARD_ENCOUNTER_SET_NUMBER_START,
                     CARD_ENCOUNTER_SET_TOTAL):
            value = _get_xml_property_value(row, name, card_type)
            if value != '':
                properties.append((name, value))

            if name in dragncards_properties:
                dragncards_values.append(str(value))

        properties.append(('Set Name', set_name))
        properties.append(('Set Icon',
                           SETS[set_id][SET_COLLECTION_ICON] or ''))
        properties.append(('Set Copyright', SETS[set_id][SET_COPYRIGHT] or ''))

        side_b = (card_type != T_PRESENTATION and (
            card_type in CARD_TYPES_DOUBLESIDE_DEFAULT or
            row[BACK_PREFIX + CARD_NAME]))
        if properties:
            if side_b:
                properties.append(('', ''))

            _add_xml_properties(card, properties, '    ')

        if side_b:
            if (card_type in CARD_TYPES_DOUBLESIDE_DEFAULT
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
                         CARD_TEXT, CARD_SHADOW, CARD_FLAVOUR,
                         CARD_PRINTED_NUMBER, CARD_ENCOUNTER_SET_NUMBER,
                         CARD_ENCOUNTER_SET_ICON, CARD_FLAGS, CARD_ICONS,
                         CARD_INFO, CARD_ARTIST, CARD_PANX, CARD_PANY,
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

                if filename.split('.')[-1] in {'jpg', 'png'}:
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

                if filename.split('.')[-1] in {'jpg', 'png'}:
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

    if (conf['nobleed_800'].get(lang)
            or 'makeplayingcards' in (conf['outputs'][lang] or [])
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
        elif card_type != T_RULES and conf['validate_missing_images']:
            logging.error('No image detected for card %s (%s)',
                          card.attrib['id'], card.attrib['name'])

        artist = _find_properties(card, 'Artist')
        if not artist and card.attrib['id'] in external_data:
            prop = _get_property(card, 'Artist')
            prop.set('value', external_data[card.attrib['id']])
            prop.tail = '\n      '

        if card_type == T_PRESENTATION:
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
            alternate_text = _find_properties(alternate,
                                              'Text')[0].attrib['value']
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

        if card_type in CARD_TYPES_NO_COLLECTION_ICON:
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

        if encounter_set and card_sphere != S_BOON:
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

    for card in root[0]:
        properties = [p for p in card]  # pylint: disable=R1721
        if properties:
            properties[-1].tail = re.sub(r'  $', '', properties[-1].tail)

    if conf['selected_only']:
        cards = list(root[0])
        for card in cards:
            if card.attrib['id'] not in SELECTED_CARDS:
                root[0].remove(card)

    tree.write(xml_path)

    for filename, is_used in images.values():
        if is_used:
            continue

        parts = filename.split('_')
        if len(parts) == 3 and parts[2] != lang:
            continue

        logging.error('Unused image detected: %s', filename)

    logging.info('[%s, %s] ...Updating the xml file with additional data '
                 '(%ss)', set_name, lang, round(time.time() - timestamp, 3))


def expire_dragncards_hashes():
    """ Expire DragnCards hashes requested by Discord bot.
    """
    logging.info('Expiring DragnCards hashes')
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

    logging.info(' ...Expiring DragnCards hashes (%ss)',
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

    if conf['verify_drive_timestamp']:
        _verify_drive_timestamp(conf['artwork_path'])

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


def run_cmd(cmd, log_prefix=''):
    """ Run bash command.
    """
    logging.info('%sRunning the command: %s', log_prefix, cmd)
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True, check=True)
        stdout = res.stdout.decode('unicode-escape', errors='ignore').strip()
        logging.info('%sCommand stdout: %s', log_prefix, stdout)
        stderr = res.stderr.decode('unicode-escape', errors='ignore').strip()
        logging.info('%sCommand stderr: %s', log_prefix, stderr)
        if 'Error' in stdout:
            raise RuntimeError(
                'Command "{}" contains error message(s) in stdout: {}'
                .format(cmd, stdout))

        if ('Error' in stderr and
                not 'Error renaming temporary file: Permission denied'
                in stderr):
            raise RuntimeError(
                'Command "{}" contains error message(s) in stderr: {}'
                .format(cmd, stderr))

        return stdout
    except subprocess.CalledProcessError as exc:
        raise RuntimeError('Command "{}" returned error with code {}: {}'
                           .format(cmd, exc.returncode, exc.output)) from exc


def generate_dragncards_proxies(sets):
    """ Generate DragnCards proxies.
    """
    logging.info('Generating DragnCards proxies...')
    timestamp = time.time()

    cmd = GENERATE_DRAGNCARDS_COMMAND.format(','.join(sets))
    run_cmd(cmd)

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
    run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < PNG_300_MIN_SIZE:
                raise GIMPError('Suspicious output file size for {}'.format(
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
    run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < PNG_480_MIN_SIZE:
                raise GIMPError('Suspicious output file size for {}'.format(
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
    run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < PNG_800_MIN_SIZE:
                raise GIMPError('Suspicious output file size for {}'.format(
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
        filenames = sorted(filenames, key=lambda f: f.rsplit('.', 1)[0])
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
    run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < PNG_300_MIN_SIZE:
                raise GIMPError('Suspicious output file size for {}'.format(
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
        filenames = sorted(filenames, key=lambda f: f.rsplit('.', 1)[0])
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
        filenames = sorted(filenames, key=lambda f: f.rsplit('.', 1)[0])
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


def generate_png800_rules_pdf(set_id, set_name, lang, skip_ids, card_data):  # pylint: disable=R0914
    """ Generate images for Rules PDF outputs.
    """
    logging.info('[%s, %s] Generating images for Rules PDF outputs...',
                 set_name, lang)
    timestamp = time.time()

    output_path = os.path.join(IMAGES_EONS_PATH, PNG800RULES,
                               '{}.{}'.format(set_id, lang))
    create_folder(output_path)
    _clear_modified_images(output_path, skip_ids)

    input_path = os.path.join(IMAGES_EONS_PATH, PNG800NOBLEED,
                              '{}.{}'.format(set_id, lang))
    known_keys = set()
    rules_cards = {c[CARD_ID]:c for c in card_data
                   if c[CARD_SET] == set_id and
                   c[CARD_TYPE] == T_RULES and c[CARD_SPHERE] != S_BACK}
    for _, _, filenames in os.walk(input_path):
        filenames = sorted(filenames, key=lambda f: f.rsplit('.', 1)[0])
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

    logging.info('[%s, %s] ...Generating images for Rules PDF outputs (%ss)',
                 set_name, lang, round(time.time() - timestamp, 3))


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
    run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < PNG_300_MIN_SIZE:
                raise GIMPError('Suspicious output file size for {}'.format(
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
    run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path3):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path3, filename)
                               ) < PNG_300_MIN_SIZE:
                raise GIMPError('Suspicious output file size for {}'.format(
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
    run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < PNG_800_MIN_SIZE:
                raise GIMPError('Suspicious output file size for {}'.format(
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
    run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path3):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path3, filename)
                               ) < PNG_800_MIN_SIZE:
                raise GIMPError('Suspicious output file size for {}'.format(
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
    run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < PNG_800_MIN_SIZE:
                raise GIMPError('Suspicious output file size for {}'.format(
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
    run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < JPG_300_MIN_SIZE:
                raise GIMPError('Suspicious output file size for {}'.format(
                    os.path.join(temp_path2, filename)))

        break

    if output_cnt != input_cnt:
        raise GIMPError('Wrong number of output files: {} instead of {}'
                        .format(output_cnt, input_cnt))

    _make_cmyk(conf, temp_path2, JPG_300CMYK_MIN_SIZE, set_name, lang)

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
    run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < JPG_800_MIN_SIZE:
                raise GIMPError('Suspicious output file size for {}'.format(
                    os.path.join(temp_path2, filename)))

        break

    if output_cnt != input_cnt:
        raise GIMPError('Wrong number of output files: {} instead of {}'
                        .format(output_cnt, input_cnt))

    _make_cmyk(conf, temp_path2, JPG_800CMYK_MIN_SIZE, set_name, lang)

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
    run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

    output_cnt = 0
    for _, _, filenames in os.walk(temp_path2):
        for filename in filenames:
            output_cnt += 1
            if os.path.getsize(os.path.join(temp_path2, filename)
                               ) < PNG_800_MIN_SIZE:
                raise GIMPError('Suspicious output file size for {}'.format(
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


def _make_low_quality(conf, input_path, set_name, lang):
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
        run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

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


def _make_jpg(conf, input_path, min_size, set_name, lang):
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
        run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

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
                   B_ENCOUNTER not in extract_keywords(
                    card_dict[card_id][CARD_KEYWORDS]) and
                   card_dict[card_id][CARD_BACK] != B_ENCOUNTER) or
                  card_dict[card_id][CARD_BACK] == B_PLAYER):
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
        run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

        output_cnt = 0
        for _, _, filenames in os.walk(output_path):
            for filename in filenames:
                if not filename.endswith('.jpg'):
                    continue

                output_cnt += 1
                if os.path.getsize(os.path.join(output_path, filename)
                                   ) < JPG_300_MIN_SIZE:
                    raise GIMPError(
                        'Suspicious output file size for {}'.format(
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
    flags = _find_properties(root, 'Flags')
    if (flags and F_PROMO in [
            f.strip() for f in flags[0].attrib['value'].split(';')]):
        flags = F_PROMO
    else:
        flags = ''

    data = {'path': artwork_path,
            'card_type': card_type,
            'card_sphere': card_sphere,
            'flags': flags,
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
            card_type_back = _find_properties(alternate, 'Type')
            card_type_back = (card_type_back[0].attrib['value']
                              if card_type_back
                              else '')
            data_back = _extract_image_properties(alternate)
            if data_back:
                images['{}.B'.format(card_id)] = data_back
            elif (data and
                  data['card_type'] in {T_CONTRACT, T_PLAYER_OBJECTIVE,
                                        T_QUEST}):
                images['{}.B'.format(card_id)] = data.copy()

            artist_back = _extract_artist_name(alternate)
            if artist_back:
                artists['{}.B'.format(card_id)] = artist_back
            elif (artist and data and
                  data['card_type'] in {T_CONTRACT, T_PLAYER_OBJECTIVE,
                                        T_QUEST}):
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
                card_type_back = _find_properties(alternate, 'Type')
                card_type_back = (card_type_back[0].attrib['value']
                                  if card_type_back
                                  else '')
                data_back = _extract_image_properties(alternate)
                if (not data_back and data and
                        data['card_type'] in {T_CONTRACT, T_PLAYER_OBJECTIVE,
                                              T_QUEST}):
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
        run_cmd(cmd, '[{}] '.format(set_name))

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
            run_cmd(cmd, '[{}] '.format(set_name))

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
        filenames = sorted(filenames, key=lambda f: f.rsplit('.', 1)[0])
        for filename in filenames:
            if not filename.endswith('.png'):
                continue

            output_filename = '{}-{}----{}{}{}'.format(
                filename[:3],
                re.sub(r'-+$', '', filename[8:50]),
                filename[50:86],
                re.sub(r'-1$', '', filename[86:88]),
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
        row[CARD_TYPE] == T_RULES and
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

        _make_low_quality(conf, temp_path, set_name, lang)

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
            filenames = sorted(filenames, key=lambda f: f.rsplit('.', 1)[0])
            for filename in filenames:
                if not filename.endswith('.png'):
                    continue

                if '----' not in filename:
                    continue

                card_id = filename.split('----')[1][:36]
                if filename.endswith('-2.png'):
                    card_type = card_dict[card_id][BACK_PREFIX + CARD_TYPE]
                    if is_doubleside(
                            card_dict[card_id][CARD_TYPE],
                            card_dict[card_id][BACK_PREFIX + CARD_TYPE]):
                        card_name = card_dict[card_id][CARD_NAME]
                        side = (
                            card_dict[card_id][BACK_PREFIX + CARD_ENGAGEMENT]
                            or '' if card_type == T_QUEST else 'B')
                    else:
                        card_name = card_dict[card_id][BACK_PREFIX + CARD_NAME]
                        side = ''
                elif (os.path.exists(os.path.join(
                        output_path, re.sub(r'\.png$', '-2.png', filename)))
                      and card_id not in empty_rules_backs):
                    card_type = card_dict[card_id][CARD_TYPE]
                    card_name = card_dict[card_id][CARD_NAME]
                    if is_doubleside(
                            card_dict[card_id][CARD_TYPE],
                            card_dict[card_id][BACK_PREFIX + CARD_TYPE]):
                        side = (card_dict[card_id][CARD_ENGAGEMENT] or ''
                                if card_type == T_QUEST else 'A')
                    else:
                        side = ''
                else:
                    card_type = card_dict[card_id][CARD_TYPE]
                    card_name = card_dict[card_id][CARD_NAME]
                    side = ''

                if side == 'B' and card_id in empty_rules_backs:
                    continue

                if card_type == T_QUEST:
                    if filename.endswith('-2.png'):
                        card_suffix = (
                            card_dict[card_id][BACK_PREFIX + CARD_COST] or '')
                    else:
                        card_suffix = card_dict[card_id][CARD_COST] or ''
                else:
                    card_suffix = CARD_TYPE_SUFFIX_HALLOFBEORN.get(card_type,
                                                                   '')

                if side and card_suffix:
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

    if lang == L_ENGLISH:  # pylint: disable=R1702
        cards = {}
        for row in card_data:
            if row[CARD_SET] == set_id and _needed_for_ringsdb(row):
                card_number = _to_str(handle_int(row[CARD_NUMBER])).zfill(3)
                code = _ringsdb_code(row)
                cards[card_number] = [code]
                if (row[CARD_TYPE] == T_ALLY and row[CARD_UNIQUE] and
                        row[CARD_SPHERE] != S_NEUTRAL):
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
                    run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

                break

    elif lang == L_FRENCH:  # pylint: disable=R1702
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
    elif lang == L_SPANISH:
        cards = {}
        for row in card_data:
            if (row[CARD_SET] == set_id and
                    (_needed_for_spanishdb(row) or
                     row[CARD_TYPE] == T_PRESENTATION)):
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
                and _needed_for_dragncards(row)}

    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            if not filename.endswith('.png'):
                continue

            if filename[50:86] not in card_ids:
                continue

            shutil.copyfile(os.path.join(input_path, filename),
                            os.path.join(temp_path, filename))

        break

    _make_jpg(conf, temp_path, JPG_480_MIN_SIZE, set_name, lang)

    known_filenames = set()
    for _, _, filenames in os.walk(temp_path):
        if not filenames:
            logging.error('[%s, %s] No cards found', set_name, lang)
            break

        create_folder(output_path)
        clear_folder(output_path)
        filenames = sorted(filenames, key=lambda f: f.rsplit('.', 1)[0])
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
                and (_needed_for_octgn(row) or _needed_for_dragncards(row))}

    for _, _, filenames in os.walk(input_path):
        for filename in filenames:
            if not filename.endswith('.png'):
                continue

            if filename[50:86] not in card_ids:
                continue

            shutil.copyfile(os.path.join(input_path, filename),
                            os.path.join(temp_path, filename))

        break

    _make_low_quality(conf, temp_path, set_name, lang)

    pack_path = os.path.join(output_path,
                             escape_octgn_filename('{}.{}.o8c'.format(
                                 escape_filename(set_name), lang)))

    known_filenames = set()
    for _, _, filenames in os.walk(temp_path):
        if not filenames:
            logging.error('[%s, %s] No cards found', set_name, lang)
            break

        create_folder(output_path)
        filenames = sorted(filenames, key=lambda f: f.rsplit('.', 1)[0])
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
    logging.info('[%s, %s] Generating Rules PDF outputs...', set_name, lang)
    timestamp = time.time()

    temp_path = os.path.join(
        TEMP_ROOT_PATH, 'generate_rules_pdf.{}.{}'.format(set_id, lang))
    input_path = os.path.join(IMAGES_EONS_PATH,
                              PNG800RULES,
                              '{}.{}'.format(set_id, lang))

    for _, _, filenames in os.walk(input_path):
        if not filenames:
            logging.error('[%s, %s] No cards found', set_name, lang)
            logging.info('[%s, %s] ...Generating Rules PDF outputs (%ss)',
                         set_name, lang, round(time.time() - timestamp, 3))
            return

        create_folder(temp_path)
        clear_folder(temp_path)
        for filename in filenames:
            if not filename.endswith('.png'):
                continue

            shutil.copyfile(os.path.join(input_path, filename),
                            os.path.join(temp_path, filename))

        break

    cmd = MAGICK_COMMAND_JPG.format(conf['magick_path'], temp_path, os.sep)
    run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

    output_path = os.path.join(OUTPUT_RULES_PDF_PATH, '{}.{}'.format(
        escape_filename(set_name), lang))
    create_folder(output_path)
    pdf_filename = 'Rules.{}.{}.pdf'.format(escape_filename(set_name),
                                            lang)
    pdf_path = os.path.join(output_path, pdf_filename)
    cmd = MAGICK_COMMAND_RULES_PDF.format(conf['magick_path'], temp_path,
                                          os.sep, pdf_path)
    run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

    delete_folder(temp_path)
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
            row[CARD_TYPE] == T_RULES and
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


def _make_cmyk(conf, input_path, min_size, set_name, lang):
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
        run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

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
                            re.sub(r'-+', '-',
                                   re.sub(r'.{36}-1(?=\.(?:png|jpg))', '-1o',
                                          '-'.join(parts)))))
                    shutil.copyfile(os.path.join(input_path, filename),
                                    front_output_path)
                    back_unofficial_output_path = os.path.join(
                        output_path, re.sub(
                            r'-(?:e|p)-', '-',
                            re.sub(r'-+', '-',
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
                                re.sub(r'-+', '-',
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
                        re.sub(r'-+', '-',
                               re.sub(r'.{36}-1(?=\.(?:png|jpg))', '-1o',
                                      '-'.join(parts)))))
                shutil.copyfile(os.path.join(input_path, filename),
                                front_output_path)
                back_unofficial_output_path = os.path.join(
                    output_path, re.sub(
                        r'-(?:e|p)-', '-',
                        re.sub(r'-+', '-',
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
                            re.sub(r'-+', '-',
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
        if (row[CARD_TYPE] == T_RULES and
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
        run_cmd(cmd, '[{}, {}] '.format(set_name, lang))

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
    """ Copy OCTGN O8D files to the destination folder.
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


def _get_ssh_client(conf, beta=False):
    """ Get SCP client.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    parts = conf.get('dragncards_hostname', '').split('@')
    if beta:
        parts[1] = 'beta.{}'.format(parts[1])

    client.connect(parts[1], username=parts[0],
                   key_filename=conf.get('dragncards_id_rsa_path', ''),
                   timeout=30)
    return client


def list_dragncards_files(conf):
    """ List playtesting JSON files on the DragnCards host.
    """
    logging.info('Running remote command: %s', DRAGNCARDS_FILES_COMMAND)
    client = _get_ssh_client(conf)
    try:
        _, res, _ = client.exec_command(DRAGNCARDS_FILES_COMMAND, timeout=30)
        res = res.read().decode('utf-8').strip()
        return res
    finally:
        try:
            client.close()
        except Exception:
            pass


def monitor_images_upload(conf):
    """ Monitor uploading images to S3 on the DragnCards host.
    """
    logging.info('Running remote command: %s',
                 DRAGNCARDS_MONITOR_IMAGES_UPLOAD_COMMAND)
    client = _get_ssh_client(conf)
    try:
        _, res, _ = client.exec_command(
            DRAGNCARDS_MONITOR_IMAGES_UPLOAD_COMMAND, timeout=30)
        res = res.read().decode('utf-8').strip()
        return res
    finally:
        try:
            client.close()
        except Exception:
            pass


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
    """ Get aggregated DragnCards statistics for all released quests.
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


def _scp_upload(client, scp_client, conf, source_path, destination_path,  # pylint: disable=R0913
                beta=False):
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
                client = _get_ssh_client(conf, beta=beta)
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
    client = None
    scp_client = None
    try:  # pylint: disable=R1702
        for set_id, set_name in sets:
            output_path = os.path.join(
                OUTPUT_OCTGN_IMAGES_PATH,
                '{}.English'.format(escape_filename(set_name)),
                '{}.English.o8c'.format(
                    escape_octgn_filename(escape_filename(set_name))))
            if (L_ENGLISH in conf['output_languages'] and
                    'octgn' in conf['outputs'][L_ENGLISH] and
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

                            if not client:
                                client = _get_ssh_client(conf)
                                scp_client = SCPClient(client.get_transport())

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
            if client:
                client.close()
        except Exception:
            pass

    logging.info('...Uploading pixel-perfect images to DragnCards (%ss)',
                 round(time.time() - timestamp, 3))


def _upload_dragncards_rendered_images(conf):
    """ Uploading rendered images to DragnCards.
    """
    images_uploaded = False
    client = None
    scp_client = None
    try:
        for _, _, filenames in os.walk(RENDERER_OUTPUT_PATH):
            filenames = [f for f in filenames if f.endswith('.jpg')]
            if filenames:
                images_uploaded = True

                if not client:
                    client = _get_ssh_client(conf)
                    scp_client = SCPClient(client.get_transport())

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
            if client:
                client.close()
        except Exception:
            pass

    return images_uploaded


def _upload_dragncards_decks_and_json(conf, sets):  # pylint: disable=R0912,R0914,R0915
    """ Uploading O8D, JSON and TSV files to DragnCards.
    """
    try:
        with open(DRAGNCARDS_FILES_CHECKSUM_PATH, 'r',
                  encoding='utf-8') as fobj:
            checksums = json.load(fobj)
    except Exception:
        checksums = {}

    changes = False
    client = None
    scp_client = None
    try:  # pylint: disable=R1702
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

                        if not client:
                            client = _get_ssh_client(conf)
                            scp_client = SCPClient(client.get_transport())

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

                if not client:
                    client = _get_ssh_client(conf)
                    scp_client = SCPClient(client.get_transport())

                client, scp_client = _scp_upload(
                    client,
                    scp_client,
                    conf,
                    output_path,
                    conf['dragncards_remote_json_path'])
    finally:
        try:
            if client:
                client.close()
        except Exception:
            pass

    client = None
    scp_client = None
    try:  # pylint: disable=R1702
        for _, set_name in sets:
            output_path = os.path.join(OUTPUT_OCTGN_DECKS_PATH,
                                       escape_filename(set_name))
            if (conf['dragncards_remote_deck_json_path'] and
                    conf['octgn_o8d'] and os.path.exists(output_path)):
                for _, _, filenames in os.walk(output_path):
                    for filename in filenames:
                        if not filename.endswith('.json'):
                            continue

                        if filename.endswith('.menu.json'):
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

                        if not client:
                            client = _get_ssh_client(conf, beta=True)
                            scp_client = SCPClient(client.get_transport())

                        client, scp_client = _scp_upload(
                            client,
                            scp_client,
                            conf,
                            file_path,
                            conf['dragncards_remote_deck_json_path'],
                            beta=True)

                    break

        menus = []
        for _, set_name in CHOSEN_SETS:
            output_path = os.path.join(OUTPUT_OCTGN_DECKS_PATH,
                                       escape_filename(set_name))
            if (conf['dragncards_remote_deck_json_path'] and
                    conf['octgn_o8d'] and os.path.exists(output_path)):
                for _, _, filenames in os.walk(output_path):
                    for filename in filenames:
                        if not filename.endswith('.menu.json'):
                            continue

                        file_path = os.path.join(output_path, filename)
                        with open(file_path, 'r', encoding='utf-8') as fobj:
                            content = json.load(fobj)
                            menus.extend(
                                content['deckMenu']['subMenus'][0]['subMenus'])

                    break

        menus.sort(key=lambda m:
            ([d for d in m['deckLists'] if d['label'] == 'id:normal'] or
             [{}])[0].get('deckListId', ''))
        if menus:
            temp_path = os.path.join(
                TEMP_ROOT_PATH, 'upload_dragncards_decks_and_json')
            create_folder(temp_path)
            clear_folder(temp_path)
            json_data = {'deckMenu': {
                'subMenus': [{'label': DRAGNCARDS_MENU_LABEL,
                              'subMenus': menus}]}}
            file_path = os.path.join(
                temp_path,
                escape_octgn_filename(
                    '{}.menu.json'.format(DRAGNCARDS_MENU_LABEL)))
            with open(file_path, 'w', encoding='utf-8') as fobj:
                json.dump(json_data, fobj)

            if not client:
                client = _get_ssh_client(conf, beta=True)
                scp_client = SCPClient(client.get_transport())

            client, scp_client = _scp_upload(
                client,
                scp_client,
                conf,
                file_path,
                conf['dragncards_remote_deck_json_path'],
                beta=True)

            delete_folder(temp_path)

        for set_id, set_name in sets:
            output_path = os.path.join(
                OUTPUT_DRAGNCARDS_PATH,
                escape_filename(set_name),
                '{}.tsv'.format(set_id))
            if (conf['dragncards_remote_tsv_path'] and
                    conf['dragncards_json'] and
                    os.path.exists(output_path)):
                with open(output_path, 'rb') as fobj:
                    content = fobj.read()

                checksum = hashlib.md5(content).hexdigest()
                if checksum == checksums.get(output_path):
                    continue

                changes = True
                checksums[output_path] = checksum

                if not client:
                    client = _get_ssh_client(conf, beta=True)
                    scp_client = SCPClient(client.get_transport())

                client, scp_client = _scp_upload(
                    client,
                    scp_client,
                    conf,
                    output_path,
                    conf['dragncards_remote_tsv_path'],
                    beta=True)
    finally:
        try:
            if client:
                client.close()
        except Exception:
            pass

    if changes:
        with open(DRAGNCARDS_FILES_CHECKSUM_PATH, 'w',
                  encoding='utf-8') as fobj:
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


def update_ringsdb(conf, sets):  # pylint: disable=R0914
    """ Update ringsdb.com.
    """
    logging.info('Updating ringsdb.com...')
    timestamp = time.time()

    try:
        with open(RINGSDB_JSON_PATH, 'r', encoding='utf-8') as fobj:
            data = json.load(fobj)
    except Exception:
        data = {}

    changes = False
    sets = [s for s in sets if s[0] in FOUND_SETS]
    for set_id, set_name in sets:
        code = SETS[set_id].get(SET_HOB_CODE)
        if not code:
            continue

        path = os.path.join(OUTPUT_RINGSDB_PATH, escape_filename(set_name),
                            '{}.csv'.format(escape_filename(set_name)))
        if not os.path.exists(path):
            continue

        with open(path, 'rb') as fobj:
            content = fobj.read()

        if (len([p for p in content.decode('utf-8').split('\n')
                if p.strip()]) <= 1):
            continue

        checksum = hashlib.md5(content).hexdigest()
        old_code, old_checksum = data.get(set_id, [None, None])
        if checksum == old_checksum and code == old_code:
            continue

        changes = True
        data[set_id] = [code, checksum]

        if not old_code:
            old_code = code

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
                data={'code': code, 'old_code': old_code, 'name': set_name})

        res = res.content.decode('utf-8').strip()
        if res != 'Done':
            raise RingsDBError('Error uploading {} to ringsdb.com: {}'
                               .format(set_name, res[:LOG_LIMIT]))

        cookies = session.cookies.get_dict()
        _write_ringsdb_cookies(cookies)

    if changes:
        with open(RINGSDB_JSON_PATH, 'w', encoding='utf-8') as fobj:
            json.dump(data, fobj)

    logging.info('...Updating ringsdb.com (%ss)',
                 round(time.time() - timestamp, 3))


def get_last_image_timestamp():
    """ Get timestamp of the last generated image output.

    NOT USED AT THE MOMENT
    """
    max_ts = 0
    for root, _, filenames in os.walk(OUTPUT_PATH):
        for filename in filenames:
            if filename.split('.')[-1] in {'png', 'jpg', 'pdf', 'o8c', '7z'}:
                file_ts = int(os.path.getmtime(os.path.join(root, filename)))
                if file_ts > max_ts:
                    max_ts = file_ts

    max_ts = datetime.fromtimestamp(max_ts).strftime('%Y-%m-%d %H:%M:%S')
    return max_ts
