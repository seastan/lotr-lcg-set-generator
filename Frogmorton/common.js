const ALLY = 'Ally';
const ATTACHMENT = 'Attachment';
const BOON = 'Boon';
const BURDEN = 'Burden';
const CAMPAIGN = 'Campaign';
const CAVE = 'Cave';
const CONTRACT = 'Contract';
const ENCOUNTER_SIDE_QUEST = 'Encounter Side Quest';
const ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA = 'Encounter Side Quest SmallTextArea';
const ENEMY = 'Enemy';
const ENEMY_NOSTAT = 'Enemy NoStat';
const EVENT = 'Event';
const FULL_ART_LANDSCAPE = 'Full Art Landscape';
const FULL_ART_PORTRAIT = 'Full Art Portrait';
const HERO = 'Hero';
const HERO_PROMO = 'Hero Promo';
const LOCATION = 'Location';
const NIGHTMARE = 'Nightmare';
const OBJECTIVE = 'Objective';
const OBJECTIVE_ALLY = 'Objective Ally';
const OBJECTIVE_HERO = 'Objective Hero';
const OBJECTIVE_LOCATION = 'Objective Location';
const PLAYER_OBJECTIVE = 'Player Objective';
const PLAYER_SIDE_QUEST = 'Player Side Quest';
const PRESENTATION = 'Presentation';
const PROMO = 'Promo';
const QUEST = 'Quest';
const REGION = 'Region';
const RING = 'Ring';
const RING_ATTACHMENT = 'RingAttachment';
const RULES = 'Rules';
const SETUP = 'Setup';
const SHIP_ENEMY = 'Ship Enemy';
const SHIP_OBJECTIVE = 'Ship Objective';
const TREACHERY = 'Treachery';
const TREASURE = 'Treasure';

const ENGLISH = 'English';
const FRENCH = 'French';
const GERMAN = 'German';
const ITALIAN = 'Italian';
const POLISH = 'Polish';
const PORTUGUESE = 'Portuguese';
const SPANISH = 'Spanish';

var doubleSideTypes = [CAMPAIGN, NIGHTMARE, PRESENTATION, QUEST, RULES];
var playerTypes = [ALLY, ATTACHMENT, CONTRACT, EVENT, FULL_ART_LANDSCAPE, FULL_ART_PORTRAIT, HERO, HERO_PROMO, PLAYER_OBJECTIVE, PLAYER_SIDE_QUEST, TREASURE];
var playerCopyTypes = [ALLY, ATTACHMENT, EVENT, PLAYER_SIDE_QUEST];
var landscapeTypes = [CAVE, ENCOUNTER_SIDE_QUEST, ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA, FULL_ART_LANDSCAPE, PLAYER_SIDE_QUEST, REGION, QUEST];

var optionalTraitTypes = [CAVE, ENCOUNTER_SIDE_QUEST, ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA, PLAYER_SIDE_QUEST];

/*
var Region = {};
Region[ALLY] = '';
Region[ATTACHMENT] = '';
Region[CAMPAIGN] = '';
Region[CAVE] = '';
Region[CONTRACT] = '';
Region[ENCOUNTER_SIDE_QUEST] = '';
Region[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '';
Region[ENEMY] = '';
Region[ENEMY_NOSTAT] = '';
Region[EVENT] = '';
Region[FULL_ART_LANDSCAPE] = '';
Region[FULL_ART_PORTRAIT] = '';
Region[HERO] = '';
Region[HERO_PROMO] = '';
Region[LOCATION] = '';
Region[NIGHTMARE] = '';
Region[OBJECTIVE] = '';
Region[OBJECTIVE_ALLY] = '';
Region[OBJECTIVE_HERO] = '';
Region[OBJECTIVE_LOCATION] = '';
Region[PLAYER_OBJECTIVE] = '';
Region[PLAYER_SIDE_QUEST] = '';
Region[PRESENTATION] = '';
Region[QUEST] = '';
Region[REGION] = '';
Region[RULES] = '';
Region[SHIP_ENEMY] = '';
Region[SHIP_OBJECTIVE] = '';
Region[TREACHERY] = '';
Region[TREASURE] = '';
*/

var gameNamePortraitRegion = {};
gameNamePortraitRegion[PRESENTATION] = '50,33,313,140';

var namePortraitRegion = {};
namePortraitRegion[PRESENTATION] = '50,420,313,113';

var pageInRegion = {};
pageInRegion[PRESENTATION] = '48,488,317,15';
pageInRegion[RULES] = '48,488,317,15';

var sideRegion = {};
sideRegion[CONTRACT] = '0,279,413,17';
sideRegion[PLAYER_OBJECTIVE] = '144,308,129,20';

var encounterSet1PortraitRegion = {};
encounterSet1PortraitRegion[QUEST] = '450,213,20,20';

var encounterSet2PortraitRegion = {};
encounterSet2PortraitRegion[QUEST] = '426,213,20,20';

var encounterSet3PortraitRegion = {};
encounterSet3PortraitRegion[QUEST] = '402,213,20,20';

var encounterSet4PortraitRegion = {};
encounterSet4PortraitRegion[QUEST] = '378,213,20,20';

var encounterSet5PortraitRegion = {};
encounterSet5PortraitRegion[QUEST] = '354,213,20,20';

var encounterSet6PortraitRegion = {};
encounterSet6PortraitRegion[QUEST] = '330,213,20,20';

var starRegion = {};
starRegion[ALLY] = '373,524,11,11';
starRegion[ATTACHMENT] = '373,524,11,11';
starRegion[CAMPAIGN] = '373,524,11,11';
starRegion[CAVE] = '529,374,11,11';
starRegion[CONTRACT] = '373,524,11,11';
starRegion[ENCOUNTER_SIDE_QUEST] = '531,374,11,11';
starRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '531,374,11,11';
starRegion[ENEMY] = '373,524,11,11';
starRegion[ENEMY_NOSTAT] = '373,524,11,11';
starRegion[EVENT] = '373,524,11,11';
starRegion[HERO] = '373,524,11,11';
starRegion[HERO_PROMO] = '351,524,11,11';
starRegion[LOCATION] = '373,524,11,11';
starRegion[NIGHTMARE] = '379,524,11,11';
starRegion[OBJECTIVE] = '363,524,11,11';
starRegion[OBJECTIVE_ALLY] = '363,524,11,11';
starRegion[OBJECTIVE_HERO] = '363,524,11,11';
starRegion[OBJECTIVE_LOCATION] = '363,524,11,11';
starRegion[PLAYER_OBJECTIVE] = '363,524,11,11';
starRegion[PLAYER_SIDE_QUEST] = '529,374,11,11';
starRegion[QUEST] = '529,374,11,11';
starRegion[REGION] = '529,374,11,11';
starRegion[SHIP_ENEMY] = '373,524,11,11';
starRegion[SHIP_OBJECTIVE] = '363,524,11,11';
starRegion[TREACHERY] = '373,524,11,11';
starRegion[TREASURE] = '377,524,11,11';

var collectionInfoRegion = {};
collectionInfoRegion[ALLY] = '358,526,26,15';
collectionInfoRegion[ATTACHMENT] = '358,526,26,15';
collectionInfoRegion[CAMPAIGN] = '358,526,26,15';
collectionInfoRegion[CAVE] = '516,374,26,15';
collectionInfoRegion[CONTRACT] = '358,526,26,15';
collectionInfoRegion[ENCOUNTER_SIDE_QUEST] = '518,374,26,15';
collectionInfoRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '518,374,26,15';
collectionInfoRegion[ENEMY] = '358,526,26,15';
collectionInfoRegion[ENEMY_NOSTAT] = '358,526,26,15';
collectionInfoRegion[EVENT] = '358,526,26,15';
collectionInfoRegion[HERO] = '358,526,26,15';
collectionInfoRegion[HERO_PROMO] = '321,510,20,12';
collectionInfoRegion[LOCATION] = '358,526,26,15';
collectionInfoRegion[NIGHTMARE] = '364,526,26,15';
collectionInfoRegion[OBJECTIVE] = '348,526,26,15';
collectionInfoRegion[OBJECTIVE_ALLY] = '348,526,26,15';
collectionInfoRegion[OBJECTIVE_HERO] = '348,526,26,15';
collectionInfoRegion[OBJECTIVE_LOCATION] = '348,526,26,15';
collectionInfoRegion[PLAYER_OBJECTIVE] = '348,526,26,15';
collectionInfoRegion[PLAYER_SIDE_QUEST] = '516,374,26,15';
collectionInfoRegion[QUEST] = '516,374,26,15';
collectionInfoRegion[REGION] = '516,374,26,15';
collectionInfoRegion[SHIP_ENEMY] = '358,526,26,15';
collectionInfoRegion[SHIP_OBJECTIVE] = '348,526,26,15';
collectionInfoRegion[TREACHERY] = '358,526,26,15';
collectionInfoRegion[TREASURE] = '362,526,26,15';

var collectionNumberRegion = {};
collectionNumberRegion[ALLY] = '334,527,24,15';
collectionNumberRegion[ATTACHMENT] = '334,527,24,15';
collectionNumberRegion[CAMPAIGN] = '334,527,24,15';
collectionNumberRegion[CAVE] = '488,375,24,15';
collectionNumberRegion[CONTRACT] = '334,527,24,15';
collectionNumberRegion[ENCOUNTER_SIDE_QUEST] = '403,375,24,15';
collectionNumberRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '403,375,24,15';
collectionNumberRegion[ENEMY] = '334,527,24,15';
collectionNumberRegion[ENEMY_NOSTAT] = '334,527,24,15';
collectionNumberRegion[EVENT] = '334,527,24,15';
collectionNumberRegion[FULL_ART_LANDSCAPE] = '403,375,24,15';
collectionNumberRegion[FULL_ART_PORTRAIT] = '334,527,24,15';
collectionNumberRegion[HERO] = '334,527,24,15';
collectionNumberRegion[HERO_PROMO] = '314,510,24,12';
collectionNumberRegion[LOCATION] = '334,527,24,15';
collectionNumberRegion[NIGHTMARE] = '334,527,24,15';
collectionNumberRegion[OBJECTIVE] = '334,527,24,15';
collectionNumberRegion[OBJECTIVE_ALLY] = '334,527,24,15';
collectionNumberRegion[OBJECTIVE_HERO] = '334,527,24,15';
collectionNumberRegion[OBJECTIVE_LOCATION] = '334,527,24,15';
collectionNumberRegion[PLAYER_OBJECTIVE] = '334,527,24,15';
collectionNumberRegion[PLAYER_SIDE_QUEST] = '403,375,24,15';
collectionNumberRegion[QUEST] = '403,375,24,15';
collectionNumberRegion[REGION] = '488,375,24,15';
collectionNumberRegion[SHIP_ENEMY] = '334,527,24,15';
collectionNumberRegion[SHIP_OBJECTIVE] = '334,527,24,15';
collectionNumberRegion[TREACHERY] = '334,527,24,15';
collectionNumberRegion[TREASURE] = '334,527,24,15';

var collectionPortraitRegion = {};
collectionPortraitRegion[ALLY] = '322,528,12,12';
collectionPortraitRegion[ATTACHMENT] = '322,528,12,12';
collectionPortraitRegion[CAMPAIGN] = '322,528,12,12';
collectionPortraitRegion[CAVE] = '476,376,12,12';
collectionPortraitRegion[CONTRACT] = '322,528,12,12';
collectionPortraitRegion[ENCOUNTER_SIDE_QUEST] = '391,376,12,12';
collectionPortraitRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '391,376,12,12';
collectionPortraitRegion[ENEMY] = '322,528,12,12';
collectionPortraitRegion[ENEMY_NOSTAT] = '322,528,12,12';
collectionPortraitRegion[EVENT] = '322,528,12,12';
collectionPortraitRegion[HERO] = '322,528,12,12';
collectionPortraitRegion[HERO_PROMO] = '305,511,10,10';
collectionPortraitRegion[LOCATION] = '322,528,12,12';
collectionPortraitRegion[NIGHTMARE] = '322,528,12,12';
collectionPortraitRegion[OBJECTIVE] = '322,528,12,12';
collectionPortraitRegion[OBJECTIVE_ALLY] = '322,528,12,12';
collectionPortraitRegion[OBJECTIVE_HERO] = '322,528,12,12';
collectionPortraitRegion[OBJECTIVE_LOCATION] = '322,528,12,12';
collectionPortraitRegion[PLAYER_OBJECTIVE] = '322,528,12,12';
collectionPortraitRegion[PLAYER_SIDE_QUEST] = '391,376,12,12';
collectionPortraitRegion[PRESENTATION] = '185,383,43,43';
collectionPortraitRegion[QUEST] = '391,376,12,12';
collectionPortraitRegion[REGION] = '476,376,12,12';
collectionPortraitRegion[SHIP_ENEMY] = '322,528,12,12';
collectionPortraitRegion[SHIP_OBJECTIVE] = '322,528,12,12';
collectionPortraitRegion[TREACHERY] = '322,528,12,12';
collectionPortraitRegion[TREASURE] = '322,528,12,12';

var typeRegion = {};
typeRegion[ALLY] = '135,507,143,20';
typeRegion[ATTACHMENT] = '136,504,142,20';
typeRegion[CAMPAIGN] = '135,504,142,20';
typeRegion[CONTRACT] = '136,504,141,20';
typeRegion[ENEMY] = '136,504,141,20';
typeRegion[EVENT] = '136,504,141,20';
typeRegion[HERO] = '135,507,143,20';
typeRegion[HERO_PROMO] = '285,448,32,15';
typeRegion[LOCATION] = '135,504,142,20';
typeRegion[NIGHTMARE] = '136,504,141,20';
typeRegion[OBJECTIVE] = '138,502,141,20';
typeRegion[OBJECTIVE_ALLY] = '138,502,141,20';
typeRegion[OBJECTIVE_HERO] = '136,508,141,20';
typeRegion[OBJECTIVE_LOCATION] = '136,504,141,20';
typeRegion[PLAYER_OBJECTIVE] = '138,502,141,20';
typeRegion[SHIP_ENEMY] = '136,504,141,20';
typeRegion[SHIP_OBJECTIVE] = '136,504,141,20';
typeRegion[TREACHERY] = '136,504,141,20';
typeRegion[TREASURE] = '136,504,141,20';

var copyrightRegion = {};
copyrightRegion[ALLY] = '158,527,124,15';
copyrightRegion[ATTACHMENT] = '158,527,124,15';
copyrightRegion[CAMPAIGN] = '158,527,124,15';
copyrightRegion[CAVE] = '345,375,124,15';
copyrightRegion[CONTRACT] = '158,527,124,15';
copyrightRegion[ENCOUNTER_SIDE_QUEST] = '225,375,124,15';
copyrightRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '225,375,124,15';
copyrightRegion[ENEMY] = '158,527,124,15';
copyrightRegion[ENEMY_NOSTAT] = '158,527,124,15';
copyrightRegion[EVENT] = '158,527,124,15';
copyrightRegion[FULL_ART_LANDSCAPE] = '34,364,124,15';
copyrightRegion[FULL_ART_PORTRAIT] = '34,514,124,15';
copyrightRegion[HERO] = '158,527,124,15';
copyrightRegion[HERO_PROMO] = '161,510,124,12';
copyrightRegion[LOCATION] = '158,527,124,15';
copyrightRegion[NIGHTMARE] = '158,527,124,15';
copyrightRegion[OBJECTIVE] = '158,527,124,15';
copyrightRegion[OBJECTIVE_ALLY] = '158,527,124,15';
copyrightRegion[OBJECTIVE_HERO] = '158,527,124,15';
copyrightRegion[OBJECTIVE_LOCATION] = '158,527,124,15';
copyrightRegion[PLAYER_OBJECTIVE] = '158,527,124,15';
copyrightRegion[PLAYER_SIDE_QUEST] = '225,375,124,15';
copyrightRegion[QUEST] = '225,375,124,15';
copyrightRegion[REGION] = '276,375,124,15';
copyrightRegion[SHIP_ENEMY] = '158,527,124,15';
copyrightRegion[SHIP_OBJECTIVE] = '158,527,124,15';
copyrightRegion[TREACHERY] = '158,527,124,15';
copyrightRegion[TREASURE] = '158,527,124,15';

var artistRegion = {};
artistRegion[ALLY] = '63,527,100,15';
artistRegion[ATTACHMENT] = '63,527,100,15';
artistRegion[CAMPAIGN] = '63,527,100,15';
artistRegion[CAVE] = '48,375,100,15';
artistRegion[CONTRACT] = '63,527,100,15';
artistRegion[ENCOUNTER_SIDE_QUEST] = '130,375,100,15';
artistRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '130,375,100,15';
artistRegion[ENEMY] = '63,527,100,15';
artistRegion[ENEMY_NOSTAT] = '63,527,100,15';
artistRegion[EVENT] = '63,527,100,15';
artistRegion[FULL_ART_LANDSCAPE] = '390,364,140,15';
artistRegion[FULL_ART_PORTRAIT] = '240,514,140,15';
artistRegion[HERO] = '63,527,100,15';
artistRegion[HERO_PROMO] = '79,510,88,12';
artistRegion[LOCATION] = '63,527,100,15';
artistRegion[NIGHTMARE] = '63,527,100,15';
artistRegion[OBJECTIVE] = '63,527,100,15';
artistRegion[OBJECTIVE_ALLY] = '63,527,100,15';
artistRegion[OBJECTIVE_HERO] = '63,527,100,15';
artistRegion[OBJECTIVE_LOCATION] = '63,527,100,15';
artistRegion[PLAYER_OBJECTIVE] = '63,527,100,15';
artistRegion[PLAYER_SIDE_QUEST] = '130,375,100,15';
artistRegion[QUEST] = '130,375,100,15';
artistRegion[REGION] = '68,375,100,15';
artistRegion[SHIP_ENEMY] = '63,527,100,15';
artistRegion[SHIP_OBJECTIVE] = '63,527,100,15';
artistRegion[TREACHERY] = '63,527,100,15';
artistRegion[TREASURE] = '63,527,100,15';

// UPDATE discord_bot.py and scripts.py
var portraitRegion = {};
portraitRegion[ALLY] = '87,0,326,330';
portraitRegion[ATTACHMENT] = '40,50,333,280';
portraitRegion[CAMPAIGN] = '0,0,413,245';
portraitRegion[CAVE] = '0,0,563,413';
portraitRegion[CONTRACT] = '0,0,413,315';
portraitRegion[ENCOUNTER_SIDE_QUEST] = '0,0,563,413';
portraitRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '0,0,563,413';
portraitRegion[ENEMY] = '87,0,326,330';
portraitRegion[ENEMY_NOSTAT] = '0,0,413,563';
portraitRegion[EVENT] = '60,0,353,330';
portraitRegion[FULL_ART_LANDSCAPE] = '0,0,563,413';
portraitRegion[FULL_ART_PORTRAIT] = '0,0,413,563';
portraitRegion[HERO] = '87,0,326,330';
portraitRegion[HERO_PROMO] = '0,0,413,563';
portraitRegion[LOCATION] = '0,60,413,268';
portraitRegion[NIGHTMARE] = '0,77,413,245';
portraitRegion[OBJECTIVE] = '0,69,413,300';
portraitRegion[OBJECTIVE + RING] = '0,0,413,563';
portraitRegion[OBJECTIVE + RING_ATTACHMENT] = '0,0,413,563';
portraitRegion[OBJECTIVE_ALLY] = '78,81,335,268';
portraitRegion[OBJECTIVE_HERO] = '78,81,335,268';
portraitRegion[OBJECTIVE_LOCATION] = '0,69,413,300';
portraitRegion[PLAYER_OBJECTIVE] = '0,69,413,300';
portraitRegion[PLAYER_SIDE_QUEST] = '0,0,563,413';
portraitRegion[PRESENTATION] = '0,140,413,285';
portraitRegion[QUEST] = '0,0,563,413';
portraitRegion[REGION] = '0,0,563,413';
portraitRegion[SHIP_ENEMY] = '87,0,326,330';
portraitRegion[SHIP_OBJECTIVE] = '78,81,335,268';
portraitRegion[TREACHERY] = '60,0,353,330';
portraitRegion[TREASURE] = '0,61,413,265';

var portraitBackRegion = {};
portraitBackRegion[CONTRACT] = '0,0,413,315';
portraitBackRegion[QUEST] = '0,0,563,413';

var bodyRegionHeroPromo = {};
bodyRegionHeroPromo[GERMAN] = '73,467,269,45';

var bodyRegion = {};
bodyRegion[ALLY] = '55,380,303,115';
bodyRegion[ATTACHMENT] = '57,347,299,144';
bodyRegion[ENEMY] = '57,377,299,114';
bodyRegion[ENEMY_NOSTAT] = '57,484,299,32';
bodyRegion[EVENT] = '65,351,283,140';
bodyRegion[HERO] = '55,380,303,115';
bodyRegion[HERO_PROMO] = '78,467,259,45';
bodyRegion[LOCATION] = '56,346,301,142';
bodyRegion[OBJECTIVE] = '65,355,283,137';
bodyRegion[OBJECTIVE_ALLY] = '65,355,283,137';
bodyRegion[OBJECTIVE_HERO] = '55,351,302,145';
bodyRegion[OBJECTIVE_LOCATION] = '65,355,283,137';
bodyRegion[PLAYER_OBJECTIVE] = '65,355,283,137';
bodyRegion[SHIP_ENEMY] = '57,377,299,114';
bodyRegion[SHIP_OBJECTIVE] = '65,355,283,137';
bodyRegion[TREACHERY] = '65,356,283,135';
bodyRegion[TREASURE] = '57,347,299,144';

bodyRegion[CAVE] = '50,303,171,60';
bodyRegion[ENCOUNTER_SIDE_QUEST] = '51,269,461,94';
bodyRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '51,324,461,38';
bodyRegion[PLAYER_SIDE_QUEST] = '51,271,461,94';

var traitRegion = {};
traitRegion[ALLY] = '55,360,303,20';
traitRegion[ATTACHMENT] = '85,327,243,20';
traitRegion[ENEMY] = '57,357,299,20';
traitRegion[ENEMY_NOSTAT] = '57,470,299,14';
traitRegion[EVENT] = '78,331,257,20';
traitRegion[HERO] = '55,360,303,20';
traitRegion[HERO_PROMO] = '93,449,160,14';
traitRegion[LOCATION] = '56,326,301,20';
traitRegion[OBJECTIVE] = '65,335,283,20';
traitRegion[OBJECTIVE_ALLY] = '65,335,283,20';
traitRegion[OBJECTIVE_HERO] = '55,331,302,20';
traitRegion[OBJECTIVE_LOCATION] = '65,335,283,20';
traitRegion[PLAYER_OBJECTIVE] = '65,335,283,20';
traitRegion[SHIP_ENEMY] = '57,357,299,20';
traitRegion[SHIP_OBJECTIVE] = '65,335,283,20';
traitRegion[TREACHERY] = '65,336,283,20';
traitRegion[TREASURE] = '85,327,243,20';

traitRegion[CAVE] = '50,283,171,20';
traitRegion[ENCOUNTER_SIDE_QUEST] = '51,249,461,20';
traitRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '51,304,461,20';
traitRegion[PLAYER_SIDE_QUEST] = '51,251,461,20';
traitRegion[REGION] = '279,350,237,25';

var bodyNoTraitRegion = {};
bodyNoTraitRegion[CAMPAIGN] = '56,277,301,211';
bodyNoTraitRegion[CONTRACT] = '65,313,283,176';
bodyNoTraitRegion[NIGHTMARE] = '54,325,305,192';
bodyNoTraitRegion[PRESENTATION] = '48,73,317,418';
bodyNoTraitRegion[QUEST] = '51,249,461,114';
bodyNoTraitRegion[RULES] = '48,73,317,418';

bodyNoTraitRegion[CAVE] = '50,283,171,80';
bodyNoTraitRegion[ENCOUNTER_SIDE_QUEST] = '51,249,461,114';
bodyNoTraitRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '51,304,461,58';
bodyNoTraitRegion[PLAYER_SIDE_QUEST] = '51,251,461,114';

var bodyRightNoTraitRegion = {};
bodyRightNoTraitRegion[CAVE] = '347,283,171,80';

var bodyBackRegion = {};
bodyBackRegion[CAMPAIGN] = '64,60,285,443';
bodyBackRegion[CONTRACT] = '65,313,283,176';
bodyBackRegion[NIGHTMARE] = '54,55,305,439';
bodyBackRegion[QUEST] = '51,249,461,114';
bodyBackRegion[RULES] = '48,73,317,418';

var nameRegion = {};
nameRegion[ALLY] = '97,328,219,30';
nameRegion[ATTACHMENT] = '131,36,185,30';
nameRegion[CAMPAIGN] = '107,41,199,30';
nameRegion[CAVE] = '79,41,162,30';
nameRegion[CONTRACT] = '83,243,247,33';
nameRegion[ENCOUNTER_SIDE_QUEST] = '99,40,365,33';
nameRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '99,40,365,33';
nameRegion[ENEMY] = '93,325,227,30';
nameRegion[ENEMY_NOSTAT] = '93,438,227,30';
nameRegion[EVENT] = '57,86,26,178';
nameRegion[HERO] = '97,328,219,30';
nameRegion[HERO_PROMO] = '102,414,208,30';
nameRegion[LOCATION] = '107,40,199,30';
nameRegion[NIGHTMARE] = '94,45,227,33';
nameRegion[OBJECTIVE] = '66,47,281,34';
nameRegion[OBJECTIVE_ALLY] = '66,47,281,34';
nameRegion[OBJECTIVE_HERO] = '74,46,265,33';
nameRegion[OBJECTIVE_LOCATION] = '74,46,265,33';
nameRegion[PLAYER_OBJECTIVE] = '66,47,281,34';
nameRegion[PLAYER_SIDE_QUEST] = '143,42,370,33';
nameRegion[QUEST] = '143,42,370,33';
nameRegion[REGION] = '79,347,162,30';
nameRegion[SHIP_ENEMY] = '93,325,227,30';
nameRegion[SHIP_OBJECTIVE] = '74,46,265,33';
nameRegion[TREACHERY] = '55,108,26,164';
nameRegion[TREASURE] = '131,42,185,30';

var nameBackRegion = {};
nameBackRegion[CONTRACT] = '83,243,247,33';
nameBackRegion[QUEST] = '143,42,370,33';

var nameUniqueRegion = {};
nameUniqueRegion[ALLY] = '97,326,219,31';
nameUniqueRegion[ATTACHMENT] = '131,34,185,31';
nameUniqueRegion[CAVE] = '79,39,162,31';
nameUniqueRegion[CONTRACT] = '83,241,247,34';
nameUniqueRegion[ENCOUNTER_SIDE_QUEST] = '99,38,365,34';
nameUniqueRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '99,38,365,34';
nameUniqueRegion[ENEMY] = '93,323,227,31';
nameUniqueRegion[ENEMY_NOSTAT] = '93,436,227,31';
nameUniqueRegion[HERO] = '97,326,219,31';
nameUniqueRegion[HERO_PROMO] = '102,414,208,31';
nameUniqueRegion[LOCATION] = '107,38,199,31';
nameUniqueRegion[OBJECTIVE] = '66,45,281,34';
nameUniqueRegion[OBJECTIVE_ALLY] = '66,45,281,34';
nameUniqueRegion[OBJECTIVE_HERO] = '74,44,265,34';
nameUniqueRegion[OBJECTIVE_LOCATION] = '74,44,265,34';
nameUniqueRegion[PLAYER_OBJECTIVE] = '66,45,281,34';
nameUniqueRegion[PLAYER_SIDE_QUEST] = '143,40,370,34';
nameUniqueRegion[REGION] = '79,345,162,31';
nameUniqueRegion[SHIP_ENEMY] = '93,323,227,31';
nameUniqueRegion[SHIP_OBJECTIVE] = '74,44,265,34';
nameUniqueRegion[TREACHERY] = '52,108,29,164';
nameUniqueRegion[TREASURE] = '131,40,185,31';

var nameUniqueBackRegion = {};
nameUniqueBackRegion[CONTRACT] = '83,241,247,34';

var subtypeRegion = {};
subtypeRegion[ALLY] = '146,305,124,20';
subtypeRegion[ATTACHMENT] = '146,301,124,20';
subtypeRegion[ENEMY] = '146,302,124,20';
subtypeRegion[EVENT] = '146,303,124,20';
subtypeRegion[OBJECTIVE] = '144,308,129,20';
subtypeRegion[OBJECTIVE + BURDEN] = '163,309,95,20';
subtypeRegion[OBJECTIVE_ALLY] = '144,308,129,20';
subtypeRegion[OBJECTIVE_HERO] = '146,309,124,20';
subtypeRegion[OBJECTIVE_LOCATION] = '146,309,124,20';
subtypeRegion[SHIP_ENEMY] = '146,302,124,20';
subtypeRegion[SHIP_OBJECTIVE] = '146,309,124,20';
subtypeRegion[TREACHERY] = '161,304,97,20';

var hitPointsRegion = {};
hitPointsRegion[ALLY] = '63,270,58,40';
hitPointsRegion[ENEMY] = '64,269,58,40';
hitPointsRegion[HERO] = '63,270,58,40';
hitPointsRegion[HERO_PROMO] = '46,408,58,40';
hitPointsRegion[OBJECTIVE_ALLY] = '62,272,58,40';
hitPointsRegion[OBJECTIVE_HERO] = '61,272,58,40';
hitPointsRegion[SHIP_ENEMY] = '64,269,58,40';
hitPointsRegion[SHIP_OBJECTIVE] = '61,272,58,40';

var engagementRegion = {};
engagementRegion[ENEMY] = '76,48,36,25';
engagementRegion[SHIP_ENEMY] = '76,48,36,25';

var attackRegion = {};
attackRegion[ALLY] = '66,159,26,16';
attackRegion[ENEMY] = '68,156,26,16';
attackRegion[HERO] = '66,159,26,16';
attackRegion[HERO_PROMO] = '42,128,26,16';
attackRegion[OBJECTIVE_ALLY] = '66,159,26,16';
attackRegion[OBJECTIVE_HERO] = '65,159,26,16';
attackRegion[SHIP_ENEMY] = '68,156,26,16';
attackRegion[SHIP_OBJECTIVE] = '65,159,26,16';

var defenseRegion = {};
defenseRegion[ALLY] = '66,203,26,16';
defenseRegion[ENEMY] = '68,199,26,16';
defenseRegion[HERO] = '66,203,26,16';
defenseRegion[HERO_PROMO] = '42,166,26,16';
defenseRegion[OBJECTIVE_ALLY] = '66,203,26,16';
defenseRegion[OBJECTIVE_HERO] = '65,203,26,16';
defenseRegion[SHIP_ENEMY] = '68,199,26,16';
defenseRegion[SHIP_OBJECTIVE] = '65,203,26,16';

var willpowerRegion = {};
willpowerRegion[ALLY] = '66,119,26,16';
willpowerRegion[HERO] = '66,119,26,16';
willpowerRegion[HERO_PROMO] = '42,94,26,16';
willpowerRegion[OBJECTIVE_ALLY] = '66,113,26,16';
willpowerRegion[OBJECTIVE_HERO] = '65,113,26,16';
willpowerRegion[SHIP_OBJECTIVE] = '65,113,26,16';

var threatRegion = {};
threatRegion[ENEMY] = '68,115,26,16';
threatRegion[LOCATION] = '54,92,26,16';
threatRegion[SHIP_ENEMY] = '68,115,26,16';

var threatCostRegion = {};
threatCostRegion[HERO] = '73,51,36,25';
threatCostRegion[HERO_PROMO] = '50,48,33,23';

var progressRegion = {};
progressRegion[ENCOUNTER_SIDE_QUEST] = '52,202,35,24';
progressRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '52,257,35,24';
progressRegion[LOCATION] = '56,283,35,24';
progressRegion[OBJECTIVE_LOCATION] = '56,291,35,24';
progressRegion[QUEST] = '55,202,35,24';
progressRegion[PLAYER_SIDE_QUEST] = '55,202,35,24';

var adventureRegion = {};
adventureRegion[OBJECTIVE] = '66,84,281,15';
adventureRegion[OBJECTIVE_ALLY] = '66,84,281,15';
adventureRegion[OBJECTIVE_HERO] = '67,83,276,15';
adventureRegion[OBJECTIVE_LOCATION] = '67,83,276,15';
adventureRegion[QUEST] = '190,78,275,15';
adventureRegion[SHIP_OBJECTIVE] = '67,83,276,15';

var cycleRegion = {};
cycleRegion[CAMPAIGN] = '68,243,274,32';

var resourceCostRegion = {};
resourceCostRegion[ALLY] = '64,44,56,37';
resourceCostRegion[ATTACHMENT] = '37,44,56,37';
resourceCostRegion[EVENT] = '37,38,56,37';
resourceCostRegion[PLAYER_SIDE_QUEST] = '43,44,56,37';
resourceCostRegion[TREASURE] = '45,61,44,30';

var difficultyRegion = {};
difficultyRegion[ENCOUNTER_SIDE_QUEST] = '0,0,563,413';
difficultyRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '0,55,563,413';
difficultyRegion[ENEMY] = '0,0,413,563';
difficultyRegion[ENEMY_NOSTAT] = '0,0,413,563';
difficultyRegion[LOCATION] = '0,0,413,563';
difficultyRegion[OBJECTIVE] = '0,0,413,563';
difficultyRegion[OBJECTIVE_ALLY] = '0,0,413,563';
difficultyRegion[OBJECTIVE_HERO] = '0,0,413,563';
difficultyRegion[OBJECTIVE_LOCATION] = '0,0,413,563';
difficultyRegion[SHIP_ENEMY] = '0,0,413,563';
difficultyRegion[SHIP_OBJECTIVE] = '0,0,413,563';
difficultyRegion[TREACHERY] = '0,0,413,563';

var encounterPortraitRegion = {};
encounterPortraitRegion[CAMPAIGN] = '319,189,43,43';
encounterPortraitRegion[CAVE] = '37,34,35,35';
encounterPortraitRegion[ENCOUNTER_SIDE_QUEST] = '478,186,43,43';
encounterPortraitRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '478,241,43,43';
encounterPortraitRegion[ENEMY] = '321,265,43,43';
encounterPortraitRegion[ENEMY_NOSTAT] = '321,379,43,43';
encounterPortraitRegion[LOCATION] = '319,265,43,43';
encounterPortraitRegion[NIGHTMARE] = '322,263,43,43';
encounterPortraitRegion[OBJECTIVE] = '314,269,43,43';
encounterPortraitRegion[OBJECTIVE_ALLY] = '314,269,43,43';
encounterPortraitRegion[OBJECTIVE_HERO] = '314,269,43,43';
encounterPortraitRegion[OBJECTIVE_LOCATION] = '314,269,43,43';
encounterPortraitRegion[QUEST] = '474,185,43,43';
encounterPortraitRegion[REGION] = '37,341,35,35';
encounterPortraitRegion[SHIP_ENEMY] = '321,265,43,43';
encounterPortraitRegion[SHIP_OBJECTIVE] = '315,268,43,43';
encounterPortraitRegion[TREACHERY] = '321,266,43,43';
encounterPortraitRegion[TREASURE] = '327,478,43,43';

var encounterNumberRegion = {};
encounterNumberRegion[CAVE] = '41,70,26,10';
encounterNumberRegion[ENCOUNTER_SIDE_QUEST] = '486,229,26,10';
encounterNumberRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '486,284,26,10';
encounterNumberRegion[ENEMY] = '329,313,26,10';
encounterNumberRegion[ENEMY_NOSTAT] = '330,427,26,10';
encounterNumberRegion[LOCATION] = '328,314,26,10';
encounterNumberRegion[OBJECTIVE] = '323,317,26,10';
encounterNumberRegion[OBJECTIVE_ALLY] = '323,317,26,10';
encounterNumberRegion[OBJECTIVE_HERO] = '323,317,26,10';
encounterNumberRegion[OBJECTIVE_LOCATION] = '323,317,26,10';
encounterNumberRegion[REGION] = '41,332,26,10';
encounterNumberRegion[SHIP_ENEMY] = '329,313,26,10';
encounterNumberRegion[SHIP_OBJECTIVE] = '323,316,26,10';
encounterNumberRegion[TREACHERY] = '330,314,26,10';

var optionLeftRegion = {};
optionLeftRegion[ENEMY] = '43,490,48,24';
optionLeftRegion[LOCATION] = '43,490,48,24';
optionLeftRegion[OBJECTIVE] = '60,490,48,24';
optionLeftRegion[OBJECTIVE_ALLY] = '60,490,48,24';
optionLeftRegion[OBJECTIVE_HERO] = '60,490,48,24';
optionLeftRegion[OBJECTIVE_LOCATION] = '60,490,48,24';
optionLeftRegion[SHIP_ENEMY] = '43,490,48,24';
optionLeftRegion[SHIP_OBJECTIVE] = '43,490,48,24';
optionLeftRegion[TREACHERY] = '43,490,48,24';

var optionRightDecorationRegion = {};
optionRightDecorationRegion[ALLY] = '300,506,72,18';
optionRightDecorationRegion[ATTACHMENT] = '300,503,72,18';
optionRightDecorationRegion[ENCOUNTER_SIDE_QUEST] = '452,347,72,18';
optionRightDecorationRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '452,347,72,18';
optionRightDecorationRegion[ENEMY] = '301,503,72,18';
optionRightDecorationRegion[EVENT] = '298,503,72,18';
optionRightDecorationRegion[HERO] = '300,506,72,18';
optionRightDecorationRegion[HERO_PROMO] = '282,495,72,18';
optionRightDecorationRegion[LOCATION] = '301,503,72,18';
optionRightDecorationRegion[OBJECTIVE] = '290,500,72,18';
optionRightDecorationRegion[OBJECTIVE_ALLY] = '290,500,72,18';
optionRightDecorationRegion[OBJECTIVE_HERO] = '298,506,72,18';
optionRightDecorationRegion[OBJECTIVE_LOCATION] = '290,502,72,18';
optionRightDecorationRegion[PLAYER_OBJECTIVE] = '290,500,72,18';
optionRightDecorationRegion[PLAYER_SIDE_QUEST] = '451,349,72,18';
optionRightDecorationRegion[QUEST] = '450,350,72,18';
optionRightDecorationRegion[SHIP_ENEMY] = '301,503,72,18';
optionRightDecorationRegion[SHIP_OBJECTIVE] = '290,502,72,18';
optionRightDecorationRegion[TREACHERY] = '301,503,72,18';
optionRightDecorationRegion[TREASURE] = '253,477,72,18';

var optionRightRegion = {};
optionRightRegion[ALLY] = '307,507,59,20';
optionRightRegion[ATTACHMENT] = '307,504,59,20';
optionRightRegion[ENCOUNTER_SIDE_QUEST] = '459,348,59,20';
optionRightRegion[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '459,348,59,20';
optionRightRegion[ENEMY] = '308,504,59,20';
optionRightRegion[EVENT] = '305,504,59,20';
optionRightRegion[HERO] = '307,507,59,20';
optionRightRegion[HERO_PROMO] = '289,496,59,20';
optionRightRegion[LOCATION] = '308,504,59,20';
optionRightRegion[OBJECTIVE] = '297,501,59,20';
optionRightRegion[OBJECTIVE_ALLY] = '297,501,59,20';
optionRightRegion[OBJECTIVE_HERO] = '305,507,59,20';
optionRightRegion[OBJECTIVE_LOCATION] = '297,503,59,20';
optionRightRegion[PLAYER_OBJECTIVE] = '297,501,59,20';
optionRightRegion[PLAYER_SIDE_QUEST] = '458,350,59,20';
optionRightRegion[QUEST] = '457,351,59,20';
optionRightRegion[SHIP_ENEMY] = '308,504,59,20';
optionRightRegion[SHIP_OBJECTIVE] = '297,503,59,20';
optionRightRegion[TREACHERY] = '308,504,59,20';
optionRightRegion[TREASURE] = '260,478,59,20';

var bodyPointSize = {};
bodyPointSize[ALLY] = 7.5;
bodyPointSize[ATTACHMENT] = 7.5;
bodyPointSize[CAMPAIGN] = 7.5;
bodyPointSize[CAVE] = 7;
bodyPointSize[CONTRACT] = 7.5;
bodyPointSize[ENCOUNTER_SIDE_QUEST] = 7;
bodyPointSize[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = 7;
bodyPointSize[ENEMY] = 7.5;
bodyPointSize[ENEMY_NOSTAT] = 5.9;
bodyPointSize[EVENT] = 7.5;
bodyPointSize[HERO] = 7.5;
bodyPointSize[HERO_PROMO] = 5.9;
bodyPointSize[LOCATION] = 7.5;
bodyPointSize[NIGHTMARE] = 7.5;
bodyPointSize[OBJECTIVE] = 7.5;
bodyPointSize[OBJECTIVE_ALLY] = 7.5;
bodyPointSize[OBJECTIVE_HERO] = 7.5;
bodyPointSize[OBJECTIVE_LOCATION] = 7.5;
bodyPointSize[PLAYER_OBJECTIVE] = 7.5;
bodyPointSize[PLAYER_SIDE_QUEST] = 7;
bodyPointSize[PRESENTATION] = 7.5;
bodyPointSize[QUEST] = 7;
bodyPointSize[RULES] = 7.5;
bodyPointSize[SHIP_ENEMY] = 7.5;
bodyPointSize[SHIP_OBJECTIVE] = 7.5;
bodyPointSize[TREACHERY] = 7.5;
bodyPointSize[TREASURE] = 7.5;

var flavourPointSize = {};
flavourPointSize[ALLY] = 6.25;
flavourPointSize[ATTACHMENT] = 6.25;
flavourPointSize[CAMPAIGN] = 6.25;
flavourPointSize[CAVE] = 7;
flavourPointSize[CONTRACT] = 6.25;
flavourPointSize[ENCOUNTER_SIDE_QUEST] = 7;
flavourPointSize[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = 7;
flavourPointSize[ENEMY] = 6.25;
flavourPointSize[ENEMY_NOSTAT] = 4.9;
flavourPointSize[EVENT] = 6.25;
flavourPointSize[HERO] = 6.25;
flavourPointSize[HERO_PROMO] = 4.9;
flavourPointSize[LOCATION] = 6.25;
flavourPointSize[NIGHTMARE] = 6.25;
flavourPointSize[OBJECTIVE] = 6.25;
flavourPointSize[OBJECTIVE_ALLY] = 6.25;
flavourPointSize[OBJECTIVE_HERO] = 6.25;
flavourPointSize[OBJECTIVE_LOCATION] = 6.25;
flavourPointSize[PLAYER_OBJECTIVE] = 6.25;
flavourPointSize[PLAYER_SIDE_QUEST] = 7;
flavourPointSize[QUEST] = 7;
flavourPointSize[SHIP_ENEMY] = 6.25;
flavourPointSize[SHIP_OBJECTIVE] = 6.25;
flavourPointSize[TREACHERY] = 6.25;
flavourPointSize[TREASURE] = 6.25;

var traitPointSize = {};
traitPointSize[ALLY] = 8.25;
traitPointSize[ATTACHMENT] = 8.25;
traitPointSize[CAVE] = 7.75;
traitPointSize[ENCOUNTER_SIDE_QUEST] = 7.75;
traitPointSize[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = 7.75;
traitPointSize[ENEMY] = 8.25;
traitPointSize[ENEMY_NOSTAT] = 6.5;
traitPointSize[EVENT] = 8.25;
traitPointSize[HERO] = 8.25;
traitPointSize[HERO_PROMO] = 6.5;
traitPointSize[LOCATION] = 8.25;
traitPointSize[OBJECTIVE] = 8.25;
traitPointSize[OBJECTIVE_ALLY] = 8.25;
traitPointSize[OBJECTIVE_HERO] = 8.25;
traitPointSize[OBJECTIVE_LOCATION] = 8.25;
traitPointSize[PLAYER_OBJECTIVE] = 8.25;
traitPointSize[PLAYER_SIDE_QUEST] = 7.75;
traitPointSize[REGION] = 7.75;
traitPointSize[SHIP_ENEMY] = 8.25;
traitPointSize[SHIP_OBJECTIVE] = 8.25;
traitPointSize[TREACHERY] = 8.25;
traitPointSize[TREASURE] = 8.25;

var namePointSize = {};
namePointSize[ALLY] = 6.5;
namePointSize[ATTACHMENT] = 6.5;
namePointSize[CAMPAIGN] = 6.5;
namePointSize[CAVE] = 6.5;
namePointSize[CONTRACT] = 7.5;
namePointSize[ENCOUNTER_SIDE_QUEST] = 7.5;
namePointSize[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = 7.5;
namePointSize[ENEMY] = 6.5;
namePointSize[ENEMY_NOSTAT] = 6.5;
namePointSize[EVENT] = 6.5;
namePointSize[HERO] = 6.5;
namePointSize[HERO_PROMO] = 6.5;
namePointSize[LOCATION] = 6.5;
namePointSize[NIGHTMARE] = 7.5;
namePointSize[OBJECTIVE] = 7.5;
namePointSize[OBJECTIVE_ALLY] = 7.5;
namePointSize[OBJECTIVE_HERO] = 7.5;
namePointSize[OBJECTIVE_LOCATION] = 7.5;
namePointSize[PLAYER_OBJECTIVE] = 7.5;
namePointSize[PLAYER_SIDE_QUEST] = 7.5;
namePointSize[QUEST] = 7.5;
namePointSize[REGION] = 6.5;
namePointSize[SHIP_ENEMY] = 6.5;
namePointSize[SHIP_OBJECTIVE] = 7.5;
namePointSize[TREACHERY] = 6.5;
namePointSize[TREASURE] = 6.5;

var bottomPointSize = {};
bottomPointSize[HERO_PROMO] = 3.5;

var threatCostTint = {};
threatCostTint[HERO] = '200.0,0.7,0.7';
threatCostTint[HERO_PROMO] = '0.0,0.0,0.95';

var sphereBodyShape = {};
sphereBodyShape[HERO] = '0,0,472,40,0';
sphereBodyShape[HERO_PROMO] = '0,0,0,0,0';
sphereBodyShape[TREASURE] = '0,0,472,0,34';

var sphereOptionBodyShape = {};
sphereOptionBodyShape[TREASURE] = '0,0,472,0,104';

var optionBodyShape = {};
optionBodyShape[ENCOUNTER_SIDE_QUEST] = '0,0,348,0,62';
optionBodyShape[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = '0,0,348,0,62';
optionBodyShape[PLAYER_SIDE_QUEST] = '0,0,350,0,62';
optionBodyShape[QUEST] = '0,0,351,0,62';

var questStageRegion = {};
questStageRegion['1'] = '44,43,62,42';
questStageRegion['2'] = '46,44,62,42';
questStageRegion['3'] = '45,44,62,42';
questStageRegion['4'] = '44,43,62,42';
questStageRegion['5'] = '44,43,62,42';
questStageRegion['6'] = '45,43,62,42';
questStageRegion['7'] = '45,43,62,42';
questStageRegion['8'] = '45,43,62,42';
questStageRegion['9'] = '45,43,62,42';

var translate = {};
translate[ALLY] = {'English': 'Ally', 'French': 'Alli\u00e9', 'German': 'Verb\u00fcndeter', 'Spanish': 'Aliado', 'Polish': 'Sprzymierzeniec', 'Italian': 'Alleato',
	'Portuguese': 'Aliado'};
translate[ATTACHMENT] = {'English': 'Attachment', 'French': 'Attachement', 'German': 'Verst\u00e4rkung', 'Spanish': 'Vinculada', 'Polish': 'Dodatek',
	'Italian': 'Aggregato', 'Portuguese': 'Acess\u00f3rio'};
translate[BOON] = {'English': 'Boon', 'French': 'Avantage', 'German': 'Gunst', 'Spanish': 'Ayuda', 'Polish': '\u0141aska', 'Italian': 'Vantaggio',
	'Portuguese': 'D\u00e1diva'};
translate[BURDEN] = {'English': 'Burden', 'French': 'Fardeau', 'German': 'B\u00fcrde', 'Spanish': 'Carga', 'Polish': 'Brzemi\u0119', 'Italian': 'Svantaggio',
	'Portuguese': 'Fardo'};
translate[CAMPAIGN] = {'English': 'Campaign', 'French': 'Campagne', 'German': 'Kampagne', 'Spanish': 'Campa\u00f1a', 'Polish': 'Kampania', 'Italian': 'Campagna',
	'Portuguese': 'Campanha'};
translate[CAVE] = {'English': 'Side Quest', 'French': 'Qu\u00eate Annexe', 'German': 'Nebenabenteuer', 'Spanish': 'Misi\u00f3n Secundaria',
	'Polish': 'Poboczna wyprawa', 'Italian': 'Ricerca Secondaria', 'Portuguese': 'Miss\u00e3o Secund\u00e1ria'};
translate[CONTRACT] = {'English': 'Contract', 'French': 'Contrat', 'German': 'Abkommen', 'Spanish': 'Contrato', 'Polish': 'Kontrakt', 'Italian': 'Contratto',
	'Portuguese': 'Contrato'};
translate[ENCOUNTER_SIDE_QUEST] = {'English': 'Side Quest', 'French': 'Qu\u00eate Annexe', 'German': 'Nebenabenteuer', 'Spanish': 'Misi\u00f3n Secundaria',
	'Polish': 'Poboczna wyprawa', 'Italian': 'Ricerca Secondaria', 'Portuguese': 'Miss\u00e3o Secund\u00e1ria'};
translate[ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA] = {'English': 'Side Quest', 'French': 'Qu\u00eate Annexe', 'German': 'Nebenabenteuer', 'Spanish': 'Misi\u00f3n Secundaria',
	'Polish': 'Poboczna wyprawa', 'Italian': 'Ricerca Secondaria', 'Portuguese': 'Miss\u00e3o Secund\u00e1ria'};
translate[ENEMY] = {'English': 'Enemy', 'French': 'Ennemi', 'German': 'Gegner', 'Spanish': 'Enemigo', 'Polish': 'Wr\u00f3g', 'Italian': 'Nemico', 'Portuguese': 'Inimigo'};
translate[ENEMY_NOSTAT] = {'English': 'Enemy', 'French': 'Ennemi', 'German': 'Gegner', 'Spanish': 'Enemigo', 'Polish': 'Wr\u00f3g', 'Italian': 'Nemico',
	'Portuguese': 'Inimigo'};
translate[EVENT] = {'English': 'Event', 'French': '\u00c9v\u00e9nement', 'German': 'Ereignis', 'Spanish': 'Evento', 'Polish': 'Wydarzenie', 'Italian': 'Evento',
	'Portuguese': 'Evento'};
translate[FULL_ART_LANDSCAPE] = {'English': 'Full Art Landscape', 'French': 'Full Art Landscape', 'German': 'Full Art Landscape', 'Spanish': 'Full Art Landscape',
	'Polish': 'Full Art Landscape', 'Italian': 'Full Art Landscape', 'Portuguese': 'Full Art Landscape'};
translate[FULL_ART_PORTRAIT] = {'English': 'Full Art Portrait', 'French': 'Full Art Portrait', 'German': 'Full Art Portrait', 'Spanish': 'Full Art Portrait',
	'Polish': 'Full Art Portrait', 'Italian': 'Full Art Portrait', 'Portuguese': 'Full Art Portrait'};
translate[HERO] = {'English': 'Hero', 'French': 'H\u00e9ros', 'German': 'Held', 'Spanish': 'H\u00e9roe', 'Polish': 'Bohater', 'Italian': 'Eroe',
	'Portuguese': 'Her\u00f3i'};
translate[HERO_PROMO] = {'English': 'Hero', 'French': 'H\u00e9ros', 'German': 'Held', 'Spanish': 'H\u00e9roe', 'Polish': 'Bohater', 'Italian': 'Eroe',
	'Portuguese': 'Her\u00f3i'};
translate[LOCATION] = {'English': 'Location', 'French': 'Lieu', 'German': 'Ort', 'Spanish': 'Lugar', 'Polish': 'Obszar', 'Italian': 'Luogo',
	'Portuguese': 'Localiza\u00e7\u00e3o'};
translate[NIGHTMARE] = {'English': 'Setup', 'French': 'Pr\u00e9paration', 'German': 'Vorbereitung', 'Spanish': 'Preparaci\u00f3n', 'Polish': 'Przygotowanie',
	'Italian': 'Preparazione', 'Portuguese': 'Prepara\u00e7\u00e3o'};
translate[OBJECTIVE] = {'English': 'Objective', 'French': 'Objectif', 'German': 'Ziel', 'Spanish': 'Objetivo', 'Polish': 'Cel', 'Italian': 'Obiettivo',
	'Portuguese': 'Objetivo'};
translate[OBJECTIVE_ALLY] = {'English': 'Objective-Ally', 'French': 'Objectif-Alli\u00e9', 'German': 'Ziel-Verb\u00fcndeter', 'Spanish': 'Objetivo-Aliado',
	'Polish': 'Cel-Sprzymierzeniec', 'Italian': 'Obiettivo-Alleato', 'Portuguese': 'Objetivo-Aliado'};
translate[OBJECTIVE_HERO] = {'English': 'Objective-Hero', 'French': 'Objectif-H\u00e9ros', 'German': 'Ziel-Held', 'Spanish': 'H\u00e9roe-Objetivo',
	'Polish': 'Cel-Bohater', 'Italian': 'Eroe-Obiettivo', 'Portuguese': 'Objetivo-Her\u00f3i'};
translate[OBJECTIVE_LOCATION] = {'English': 'Objective-Location', 'French': 'Objectif-Lieu', 'German': 'Ziel-Ort', 'Spanish': 'Lugar-Objetivo', 'Polish': 'Cel-Obszar',
	'Italian': 'Luogo-Obiettivo', 'Portuguese': 'Objetivo-Localiza\u00e7\u00e3o'};
translate[PLAYER_OBJECTIVE] = {'English': 'Player Objective', 'French': 'Objectif Joueur', 'German': 'Spieler-Ziel', 'Spanish': 'Objetivo de Jugador',
	'Polish': 'Cel Gracza', 'Italian': 'Obiettivo dei Giocatori', 'Portuguese': 'T.B.D.'};
translate[PLAYER_SIDE_QUEST] = {'English': 'Side Quest', 'French': 'Qu\u00eate Annexe', 'German': 'Nebenabenteuer', 'Spanish': 'Misi\u00f3n Secundaria',
	'Polish': 'Poboczna wyprawa', 'Italian': 'Ricerca Secondaria', 'Portuguese': 'Miss\u00e3o Secund\u00e1ria'};
translate[PRESENTATION] = {'English': 'Presentation', 'French': 'Presentation', 'German': 'Presentation', 'Spanish': 'Presentation', 'Polish': 'Presentation',
	'Italian': 'Presentation', 'Portuguese': 'Presentation'};
translate[QUEST] = {'English': 'Quest', 'French': 'Qu\u00eate', 'German': 'Abenteuer', 'Spanish': 'Misi\u00f3n', 'Polish': 'Wyprawa', 'Italian': 'Ricerca',
	'Portuguese': 'Miss\u00e3o'};
translate[REGION] = {'English': 'Side Quest', 'French': 'Qu\u00eate Annexe', 'German': 'Nebenabenteuer', 'Spanish': 'Misi\u00f3n Secundaria',
	'Polish': 'Poboczna wyprawa', 'Italian': 'Ricerca Secondaria', 'Portuguese': 'Miss\u00e3o Secund\u00e1ria'};
translate[RULES] = {'English': 'Rules', 'French': 'Rules', 'German': 'Rules', 'Spanish': 'Rules', 'Polish': 'Rules', 'Italian': 'Rules', 'Portuguese': 'Rules'};
translate[SETUP] = {'English': 'Setup', 'French': 'Pr\u00e9paration', 'German': 'Vorbereitung', 'Spanish': 'Preparaci\u00f3n', 'Polish': 'Przygotowanie',
	'Italian': 'Preparazione', 'Portuguese': 'Prepara\u00e7\u00e3o'};
translate[SHIP_ENEMY] = {'English': 'Ship-Enemy', 'French': 'Navire-Ennemi', 'German': 'Schiff-Gegner', 'Spanish': 'Barco-Enemigo', 'Polish': 'Statek-Wr\u00f3g',
	'Italian': 'Nave-Nemico', 'Portuguese': 'Navio-Inimigo'};
translate[SHIP_OBJECTIVE] = {'English': 'Ship-Objective', 'French': 'Navire-Objectif', 'German': 'Schiff-Ziel', 'Spanish': 'Barco-Objetivo', 'Polish': 'Statek-Cel',
	'Italian': 'Nave-Obiettivo', 'Portuguese': 'Navio-Objetivo'};
translate[TREACHERY] = {'English': 'Treachery', 'French': 'Tra\u00eetrise', 'German': 'Verrat', 'Spanish': 'Traici\u00f3n', 'Polish': 'Podst\u0119p',
	'Italian': 'Perfidia', 'Portuguese': 'Infort\u00fanio'};
translate[TREASURE] = {'English': 'Treasure', 'French': 'Tr\u00e9sor', 'German': 'Schatz', 'Spanish': 'Tesoro', 'Polish': 'Skarb', 'Italian': 'Tesoro',
	'Portuguese': 'Tesouro'};

translate['BoonLeadership'] = {'English': 'Boon', 'French': 'Avantage', 'German': 'Gunst', 'Spanish': 'Ayuda', 'Polish': '\u0141aska', 'Italian': 'Vantaggio',
	'Portuguese': 'D\u00e1diva'};
translate['BoonLore'] = {'English': 'Boon', 'French': 'Avantage', 'German': 'Gunst', 'Spanish': 'Ayuda', 'Polish': '\u0141aska', 'Italian': 'Vantaggio',
	'Portuguese': 'D\u00e1diva'};
translate['BoonSpirit'] = {'English': 'Boon', 'French': 'Avantage', 'German': 'Gunst', 'Spanish': 'Ayuda', 'Polish': '\u0141aska', 'Italian': 'Vantaggio',
	'Portuguese': 'D\u00e1diva'};
translate['BoonTactics'] = {'English': 'Boon', 'French': 'Avantage', 'German': 'Gunst', 'Spanish': 'Ayuda', 'Polish': '\u0141aska', 'Italian': 'Vantaggio',
	'Portuguese': 'D\u00e1diva'};
translate['Encounter Keyword'] = {'English': 'Encounter', 'French': 'Rencontre', 'German': 'Begegnung', 'Spanish': 'Encuentro', 'Polish': 'Spotkanie',
	'Italian': 'Incontro', 'Portuguese': 'Encontro'};
translate['Illustrator'] = {'English': 'Illus.', 'French': 'Illus.', 'German': 'Illus.', 'Spanish': 'Ilus.', 'Polish': 'Illus.', 'Italian': 'Illus.',
	'Portuguese': 'Ilust.'};
translate['Page'] = {'English': 'Page', 'French': 'Page', 'German': 'Seite', 'Spanish': 'P\u00e1gina', 'Polish': 'Strona', 'Italian': 'Pagina',
	'Portuguese': 'P\u00e1gina'};
translate['Side'] = {'English': 'Side', 'French': 'Face', 'German': 'Seite', 'Spanish': 'Lado', 'Polish': 'Strona', 'Italian': 'Lato', 'Portuguese': 'Lado'};
translate['Unknown Artist'] = {'English': 'Unknown Artist', 'French': 'Artiste inconnu', 'German': 'Unbekannter K\u00fcnstler', 'Spanish': 'Artista desconocido',
	'Polish': 'Artysta nieznany', 'Italian': 'Artista sconosciuto', 'Portuguese': 'Artista Desconhecido'};
translate['Victory'] = {'English': 'Victory', 'French': 'Victoire', 'German': 'Sieg', 'Spanish': 'Victoria', 'Polish': 'Zwyci\u0119stwo', 'Italian': 'Vittoria',
	'Portuguese': 'Vit\u00f3ria'};

try {
	if (project.findChild('custom.js')) {
		useLibrary('project:custom.js');
	}
}
catch (err) {
	// ignore
}

function run(context, doc, setID, lang, icons, getCardObjects, saveResult, progress) {
	var docElement = doc.getDocumentElement();
	var setName = docElement.getAttribute('name');
	var setIcon = docElement.getAttribute('icon');
	var setCopyright = docElement.getAttribute('copyright');
	var png300Bleed = docElement.getAttribute('png300Bleed') + '' == '1';
	var png480Bleed = docElement.getAttribute('png480Bleed') + '' == '1';
	var png800Bleed = docElement.getAttribute('png800Bleed') + '' == '1';

	var nList = doc.getElementsByTagName('card');
	for (let i = 0; i < nList.getLength(); i++) {
		let nNode = nList.item(i);
		if (nNode.getAttribute('skip') == '1') {
			continue;
		}

		if ((context == 'renderer') && ((nNode.getAttribute('noDragncards') == '1') || (nNode.getAttribute('skipDragncards') == '1'))) {
			continue;
		}

		let card = {};
		card['Set'] = setName;
		card['octgn'] = nNode.getAttribute('id');
		card['Name'] = nNode.getAttribute('name');
		let propList = nNode.getElementsByTagName('property');
		for (let j = 0; j < propList.getLength(); j++) {
			let nProp = propList.item(j);
			if (nProp && nProp.getParentNode().isSameNode(nNode)) {
				card[nProp.getAttribute('name')] = nProp.getAttribute('value');
			}
		}
		let altList = nNode.getElementsByTagName('alternate');
		for (let k = 0; k < altList.getLength(); k++) {
			let nAlternate = altList.item(k);
			if (nAlternate) {
				card['BName'] = nAlternate.getAttribute('name');
				let altPropList = nAlternate.getElementsByTagName('property');
				for (let l = 0; l < altPropList.getLength(); l++) {
					let nAltProp = altPropList.item(l);
					if (nAltProp) {
						card['B' + nAltProp.getAttribute('name')] = nAltProp.getAttribute('value');
					}
				}
			}
		}

		let doubleSide = isDoubleSide(card['Type'], card['BType']);

		if ((card['Type'] + '' == QUEST) && card['BQuest Points']) {
			card['Quest Points'] = card['BQuest Points'];
		}

		if ((card['Type'] + '' == QUEST) && !card['Sphere'] && (card['BSphere'] == 'Nightmare')) {
			card['Sphere'] = 'HalfNightmare';
		}

		if (!card['Text']) {
			card['Text'] = ' ';
		}

		if (!doubleSide && card['BName'] && !card['BText']) {
			card['BText'] = ' ';
		}

		if (!card['Artist']) {
			card['Artist'] = 'Unknown Artist';
		}

		if (((card['Type'] + '' == CONTRACT) || (card['Type'] + '' == PLAYER_OBJECTIVE)) && !card['BArtist']) {
			card['BArtist'] = card['Artist'];
		}

		if (!doubleSide && card['BName'] && !card['BArtist']) {
			card['BArtist'] = 'Unknown Artist';
		}

		if (card['Flags']) {
			card['Flags'] = (card['Flags'] + '').replace(/;/g, '\n').split('\n');
			for (let idx_f = 0; idx_f < card['Flags'].length; idx_f++) {
				card['Flags'][idx_f] = card['Flags'][idx_f].trim();
			}
		}
		else {
			card['Flags'] = [];
		}

		if (card['BFlags']) {
			card['BFlags'] = (card['BFlags'] + '').replace(/;/g, '\n').split('\n');
			for (let idx_f = 0; idx_f < card['BFlags'].length; idx_f++) {
				card['BFlags'][idx_f] = card['BFlags'][idx_f].trim();
			}
		}
		else {
			card['BFlags'] = [];
		}

		let playerCopies = false;
		if (playerCopyTypes.indexOf(card['Type'] + '') > -1 && card['Quantity'] == 3) {
			playerCopies = true;
			card['Quantity'] = 1;
		}

		for (let j = 0; j < card['Quantity']; j++) {
			if ((context == 'renderer') && (j > 0)) {
				break;
			}

			let sides = ['front'];
			if (!doubleSide && card['BName']) {
				sides.push('back');
			}
			for (let idx = 0; idx < sides.length; idx++) {
				let side = sides[idx];
				let keywords = '';
				let keywordsBack = '';
				let cardNameBack = '';
				let cardName, cardType, cardSphere, suffix, mapping, flags;
				if (side == 'front') {
					cardName = card['Name'];
					cardType = card['Type'] + '';
					cardSphere = card['Sphere'] + '';
					cardTrait = card['Traits'];

					flags = [];
					for (let idx_f = 0; idx_f < card['Flags'].length; idx_f++) {
						flags.push(card['Flags'][idx_f]);
					}

					if ((cardType == HERO) && (flags.indexOf(PROMO) > -1)) {
						cardType = HERO_PROMO;
						cardSphere = PROMO + card['Sphere'];
						card['Sphere'] = cardSphere;
					}
					else if ((cardType == ENEMY) && (card['Sphere'] + '' == 'NoStat')) {
						cardType = ENEMY_NOSTAT;
					}
					else if ((cardType == ENCOUNTER_SIDE_QUEST) && (card['Sphere'] + '' == 'SmallTextArea')) {
						cardType = ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA;
					}
					else if ((cardType == ENCOUNTER_SIDE_QUEST) && (card['Sphere'] + '' == CAVE)) {
						cardType = CAVE;
					}
					else if ((cardType == ENCOUNTER_SIDE_QUEST) && (card['Sphere'] + '' == REGION)) {
						cardType = REGION;
					}
					else if (cardType == OBJECTIVE_HERO) {
						cardSphere = HERO;
						card['Sphere'] = cardSphere;
					}
					else if (cardType == OBJECTIVE_LOCATION) {
						cardSphere = LOCATION;
						card['Sphere'] = cardSphere;
					}
					else if ((cardType == SHIP_ENEMY) && (card['Sphere'] + '' == NIGHTMARE)) {
						cardSphere = 'ShipNightmare';
						card['Sphere'] = cardSphere;
					}
					else if ((cardType == SHIP_ENEMY) && (card['Sphere'] + '' == BURDEN)) {
						cardSphere = 'ShipBurden';
						card['Sphere'] = cardSphere;
					}

					keywords = card['Keywords'];
					suffix = '';
					mapping = [
						// Convert from member name in xml file to member name in eon file
						// [eon, xml]
						['Name', 'Name'],
						['Unique', 'Unique'],
						['Template', 'Sphere'],
						['Trait', 'Traits'],
						['ResourceCost', 'Cost'],
						['ThreatCost', 'Cost'],
						['Stage', 'Cost'],
						['Engagement', 'Engagement Cost'],
						['StageLetter', 'Engagement Cost'],
						['Threat', 'Threat'],
						['Willpower', 'Willpower'],
						['Attack', 'Attack'],
						['Defense', 'Defense'],
						['HitPoints', 'Health'],
						['Progress', 'Quest Points'],
						['OptionRight', 'Victory Points'],
						['Rules', 'Text'],
						['Shadow', 'Shadow'],
						['Flavour', 'Flavour'],
						['Story', 'Flavour'],
						['OptionLeft', 'Icons'],
						['CollectionInfo', 'Info'],
						['Artist', 'Artist'],
						['Adventure', 'Adventure'],
						['Cycle', 'Adventure'],
						['CollectionNumberCustom', 'Card Number'],
						['CollectionNumberCustomOverwrite', 'Printed Card Number'],
						['EncounterSetNumberOverwrite', 'Encounter Set Number']
					];
					if (doubleSide) {
						keywordsBack = card['BKeywords'];
						cardNameBack = card['BName'];
						mapping = mapping.concat([
							['NameBack', 'BName'],
							['UniqueBack', 'BUnique'],
							['StageLetterBack', 'BEngagement Cost'],
							['OptionRightBack', 'BVictory Points'],
							['RulesBack', 'BText'],
							['FlavourBack', 'BFlavour'],
							['StoryBack', 'BFlavour'],
							['CollectionInfoBack', 'BInfo'],
							['CollectionNumberCustomOverwriteBack', 'BPrinted Card Number'],
							['ArtistBack', 'BArtist']
						]);
						for (let idx_f = 0; idx_f < card['BFlags'].length; idx_f++) {
							flags.push(card['BFlags'][idx_f] + 'Back');
						}
					}
				}
				else {
					cardName = card['BName'];
					cardType = card['BType'] + '';
					cardSphere = card['BSphere'] + '';
					cardTrait = card['BTraits'];

					flags = [];
					for (let idx_f = 0; idx_f < card['BFlags'].length; idx_f++) {
						flags.push(card['BFlags'][idx_f]);
					}

					if ((cardType == HERO) && (flags.indexOf(PROMO) > -1)) {
						cardType = HERO_PROMO;
						cardSphere = PROMO + card['BSphere'];
						card['BSphere'] = cardSphere;
					}
					else if ((cardType == ENEMY) && (card['BSphere'] + '' == 'NoStat')) {
						cardType = ENEMY_NOSTAT;
					}
					else if ((cardType == ENCOUNTER_SIDE_QUEST) && (card['BSphere'] + '' == 'SmallTextArea')) {
						cardType = ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA;
					}
					else if ((cardType == ENCOUNTER_SIDE_QUEST) && (card['BSphere'] + '' == CAVE)) {
						cardType = CAVE;
					}
					else if ((cardType == ENCOUNTER_SIDE_QUEST) && (card['BSphere'] + '' == REGION)) {
						cardType = REGION;
					}
					else if (cardType == OBJECTIVE_HERO) {
						cardSphere = HERO;
						card['BSphere'] = cardSphere;
					}
					else if (cardType == OBJECTIVE_LOCATION) {
						cardSphere = LOCATION;
						card['BSphere'] = cardSphere;
					}
					else if ((cardType == SHIP_ENEMY) && (card['BSphere'] + '' == NIGHTMARE)) {
						cardSphere = 'ShipNightmare';
						card['BSphere'] = cardSphere;
					}
					else if ((cardType == SHIP_ENEMY) && (card['BSphere'] + '' == BURDEN)) {
						cardSphere = 'ShipBurden';
						card['BSphere'] = cardSphere;
					}

					keywordsBack = card['BKeywords'];
					suffix = '-2';
					mapping = [
						// Convert from member name in xml file to member name in eon file
						// [eon, xml]
						['Name', 'BName'],
						['Unique', 'BUnique'],
						['Template', 'BSphere'],
						['Trait', 'BTraits'],
						['ResourceCost', 'BCost'],
						['ThreatCost', 'BCost'],
						['Engagement', 'BEngagement Cost'],
						['Threat', 'BThreat'],
						['Willpower', 'BWillpower'],
						['Attack', 'BAttack'],
						['Defense', 'BDefense'],
						['HitPoints', 'BHealth'],
						['Progress', 'BQuest Points'],
						['OptionRight', 'BVictory Points'],
						['Rules', 'BText'],
						['Shadow', 'BShadow'],
						['Flavour', 'BFlavour'],
						['Story', 'BFlavour'],
						['CollectionInfo', 'BInfo'],
						['OptionLeft', 'BIcons'],
						['Artist', 'BArtist'],
						['Adventure', 'Adventure'],
						['Cycle', 'Adventure'],
						['CollectionNumberCustom', 'Card Number'],
						['CollectionNumberCustomOverwrite', 'BPrinted Card Number'],
						['EncounterSetNumberOverwrite', 'BEncounter Set Number']
					];
				}

				if (progress) {
					progress.status = cardName;
				}

				let cardObjects = getCardObjects(cardType);
				let newCard = cardObjects[0];
				let s = cardObjects[1];

				for (let k = 0; k < mapping.length; k++) {
					let nEon = mapping[k][0];
					let nXml = mapping[k][1];
					let vXml = card[nXml];

					if (!vXml) {
						if (['Sphere', 'BSphere'].indexOf(nXml + '') > -1) {
							if (context == 'renderer') {
								s.set(nEon, '');
							}
						}
						else {
							s.set(nEon, '');
						}
						continue;
					}

					if (['Victory Points', 'BVictory Points'].indexOf(nXml + '') > -1) {
						if ((cardType != PRESENTATION) && (cardType != RULES) && vXml.match(/^-?[0-9]+$/)) {
							vXml = translate['Victory'][lang].toUpperCase() + ' ' + vXml;
							if (lang == GERMAN) {
								vXml += '.';
							}
						}
					}
					else if (['Artist', 'BArtist'].indexOf(nXml + '') > -1) {
						if (vXml == 'Unknown Artist') {
							vXml = translate['Unknown Artist'][lang];
						}
					}
					else if (['Icons', 'BIcons'].indexOf(nXml + '') > -1) {
						vXml = (vXml + '').replace(/\]\[/g, '][size 4]\u00a0[/size][');
					}
					else if (nXml == 'Text') {
						if (keywords) {
							vXml = keywords + '\n\n' + vXml;
						}
					}
					else if (nXml == 'BText') {
						if (keywordsBack) {
							vXml = keywordsBack + '\n\n' + vXml;
						}
					}
					else if ((nXml == 'Adventure') && (cardType != CAMPAIGN)) {
						vXml = vXml.toUpperCase();
					}

					vXml = markUp(vXml, nXml, cardType, lang, setID);
					s.set(nEon, vXml);
				}

				if (landscapeTypes.indexOf(cardType) > -1) {
					s.set('Flavour', '');
					s.set('FlavourBack', '');
				}
				else {
					s.set('Story', '');
					s.set('StoryBack', '');
				}

				if (flags.indexOf('NoArtist') > -1) {
					s.set('NoArtist', 1);
				}
				else {
					s.set('NoArtist', 0);
				}
				if (flags.indexOf('Star') > -1) {
					s.set('Star', 1);
				}
				else {
					s.set('Star', 0);
				}

				if (flags.indexOf('NoArtistBack') > -1) {
					s.set('NoArtistBack', 1);
				}
				else {
					s.set('NoArtistBack', 0);
				}
				if (flags.indexOf('NoCopyright') > -1) {
					s.set('NoCopyright', 1);
				}
				else {
					s.set('NoCopyright', 0);
				}
				if (flags.indexOf('NoCopyrightBack') > -1) {
					s.set('NoCopyrightBack', 1);
				}
				else {
					s.set('NoCopyrightBack', 0);
				}
				if (flags.indexOf('StarBack') > -1) {
					s.set('StarBack', 1);
				}
				else {
					s.set('StarBack', 0);
				}

				if (context == 'renderer') {
					let bodyShapeNeeded = false;
					if (((cardType == HERO) && (cardSphere != 'Neutral')) || (cardType == TREASURE) ||
						(([ENCOUNTER_SIDE_QUEST, ENCOUNTER_SIDE_QUEST_SMALLTEXTAREA, PLAYER_SIDE_QUEST, QUEST].indexOf(cardType) > -1) &&
						(s.get('OptionRight') && (s.get('OptionRight') + '').length))) {
						bodyShapeNeeded = true;
					}
					s.set('BodyShapeNeededRenderer', bodyShapeNeeded);

					let bodyShapeNeededBack = false;
					if ((cardType == QUEST) && s.get('OptionRightBack') && (s.get('OptionRightBack') + '').length) {
						bodyShapeNeededBack = true;
					}
					s.set('BodyShapeNeededBackRenderer', bodyShapeNeededBack);
				}

				if (cardType == CAVE) {
					if (s.get('Rules').search('\\[split\\]') > -1) {
						if (context == 'renderer') {
							s.set('RulesRight', s.get('Rules').split('[split]')[1].trim());
							s.set('Rules', s.get('Rules').split('[split]')[0].trim());
						}
						else {
							s.set('RulesRight', s.get('Rules').split('\\[split\\]')[1].trim());
							s.set('Rules', s.get('Rules').split('\\[split\\]')[0].trim());
						}
					}
					else {
						s.set('RulesRight', '');
					}
				}

				if ((cardType == PRESENTATION) || (cardType == RULES)) {
					if (s.get('OptionRight').search('/') > -1) {
						s.set('PageFrontShow', 'true');
						s.set('PageNumber', s.get('OptionRight').split('/')[0]);
						s.set('PageTotal', s.get('OptionRight').split('/')[1]);
					}
					else {
						s.set('PageFrontShow', 'false');
						s.set('PageNumber', 0);
						s.set('PageTotal', 0);
					}

					if (s.get('OptionRightBack').search('/') > -1) {
						s.set('PageBackShow', 'true');
						s.set('PageNumberBack', s.get('OptionRightBack').split('/')[0]);
						s.set('PageTotalBack', s.get('OptionRightBack').split('/')[1]);
					}
					else {
						s.set('PageBackShow', 'false');
						s.set('PageNumberBack', 0);
						s.set('PageTotalBack', 0);
					}

					s.set('Background-external-path', 'project:Templates/Rules-Background.png');
					s.set('BackgroundBack-external-path', 'project:Templates/Rules-Background.png');
					s.set('GameName-external-path', 'project:imagesRaw/' + card['ArtworkTop']);
					s.set('Name-external-path', 'project:imagesRaw/' + card['ArtworkBottom']);
				}

				if (cardType == CONTRACT) {
					s.set('Side', '');
					s.set('SideA', markUp(translate['Side'][lang].toUpperCase() + ' A', 'Side', cardType, lang, setID));
					s.set('SideB', markUp(translate['Side'][lang].toUpperCase() + ' B', 'Side', cardType, lang, setID));

					if (card['BType'] + '' == CONTRACT) {
						s.set('Template', 'DoubleSided');
					}
					else {
						s.set('Template', 'Neutral');
					}
				}
				else if (cardType == PLAYER_OBJECTIVE) {
					let playerObjectiveSide;
					if (side == 'front') {
						playerObjectiveSide = 'A';
					}
					else {
						playerObjectiveSide = 'B';
					}
					s.set('Side', markUp(translate['Side'][lang].toUpperCase() + ' ' + playerObjectiveSide, 'Side', cardType, lang, setID));
				}

				if ([BOON, BURDEN].indexOf(cardSphere) > -1) {
					s.set('Subtype', markUp(translate[cardSphere][lang].toUpperCase(), 'Subtype', cardType, lang, setID));
				}
				else {
					s.set('Subtype', '');
				}

				if ((cardType == CAMPAIGN) && (cardSphere == SETUP)) {
					s.set('Type', markUp(translate[SETUP][lang].toUpperCase(), 'Type', cardType, lang, setID));
					s.set('Template', 'Standard');
				}
				else if ((cardType == OBJECTIVE) && (cardSphere == RING_ATTACHMENT)) {
					s.set('Type', markUp(translate[ATTACHMENT][lang].toUpperCase(), 'Type', cardType, lang, setID));
					s.set('Template', RING);
				}
				else {
					s.set('Type', markUp(translate[cardType][lang].toUpperCase(), 'Type', cardType, lang, setID));
				}

				if (side == 'front') {
					if (card['Portrait Shadow']) {
						s.set('PortraitShadow', card['Portrait Shadow']);
						if ((cardType == QUEST) && (!card['BArtwork'] || (card['BArtwork'] == card['Artwork']))) {
							s.set('PortraitBackShadow', card['Portrait Shadow']);
						}
					}
					if ((cardType == QUEST) && card['BPortrait Shadow'] && card['BArtwork'] && (card['BArtwork'] != card['Artwork'])) {
						s.set('PortraitBackShadow', card['BPortrait Shadow']);
					}
					if (card['Artwork']) {
						s.set('Portrait-external-path', 'project:imagesRaw/' + card['Artwork']);
						if (card['PanX'] && card['PanY'] && card['Scale']) {
							s.set('Portrait-external-panx', card['PanX']);
							s.set('Portrait-external-pany', card['PanY']);
							s.set('Portrait-external-scale', card['Scale'] / 100);
						}
					}
					else {
						s.set('Portrait-external-path', 'project:imagesDefault/white.jpg');
					}
					if ((cardType == QUEST) || ((cardType == CONTRACT) && (card['BType'] + '' == CONTRACT))) {
						if (card['BArtwork'] && (card['BArtwork'] != card['Artwork'])) {
							s.set('PortraitBack-external-path', 'project:imagesRaw/' + card['BArtwork']);
							s.set('PortraitShare', 0);
							if (card['BPanX'] && card['BPanY'] && card['BScale']) {
								s.set('PortraitBack-external-panx', card['BPanX']);
								s.set('PortraitBack-external-pany', card['BPanY']);
								s.set('PortraitBack-external-scale', card['BScale'] / 100);
							}
						}
						else if (card['Artwork']) {
							s.set('PortraitBack-external-path', 'project:imagesRaw/' + card['Artwork']);
							s.set('PortraitShare', 1);
							if (card['PanX'] && card['PanY'] && card['Scale']) {
								s.set('PortraitBack-external-panx', card['PanX']);
								s.set('PortraitBack-external-pany', card['PanY']);
								s.set('PortraitBack-external-scale', card['Scale'] / 100);
							}
						}
						else {
							s.set('PortraitBack-external-path', 'project:imagesDefault/white.jpg');
						}
					}
				}
				else {
					if (card['BPortrait Shadow']) {
						s.set('PortraitShadow', card['BPortrait Shadow']);
					}
					if (card['BArtwork']) {
						s.set('Portrait-external-path', 'project:imagesRaw/' + card['BArtwork']);
						if (card['BPanX'] && card['BPanY'] && card['BScale']) {
							s.set('Portrait-external-panx', card['BPanX']);
							s.set('Portrait-external-pany', card['BPanY']);
							s.set('Portrait-external-scale', card['BScale'] / 100);
						}
					}
					else if (((card['Type'] + '' == CONTRACT) || (card['Type'] + '' == PLAYER_OBJECTIVE)) && card['Artwork']) {
						s.set('Portrait-external-path', 'project:imagesRaw/' + card['Artwork']);
						if (card['PanX'] && card['PanY'] && card['Scale']) {
							s.set('Portrait-external-panx', card['PanX']);
							s.set('Portrait-external-pany', card['PanY']);
							s.set('Portrait-external-scale', card['Scale'] / 100);
						}
					}
					else {
						s.set('Portrait-external-path', 'project:imagesDefault/white.jpg');
					}
				}

				let encounterSet = card['Encounter Set'];
				if (card['Encounter Set Icon'] && (side == 'front')) {
					encounterSet = card['Encounter Set Icon'];
				}
				else if (card['BEncounter Set Icon'] && (side == 'back')) {
					encounterSet = card['BEncounter Set Icon'];
				}

				if (encounterSet) {
					let iconName = escapeIconFileName(encounterSet);
					if (icons.indexOf(iconName) > -1) {
						s.set('EncounterSet', 'Custom');
						s.set('EncounterSet-external-path', 'project:imagesIcons/' + iconName + '.png');
					}
					else {
						s.set('EncounterSet', convertIconName(encounterSet));
						s.set('EncounterSet-external-path', '');
					}
				}
				else {
					s.set('EncounterSet', 'Empty');
					s.set('EncounterSet-external-path', '');
				}

				if (cardType == QUEST) {
					let encounterSets = [];
					if (card['Additional Encounter Sets']) {
						let encounterSetsRaw = card['Additional Encounter Sets'].split(';');
						for (let k = 0; k < encounterSetsRaw.length; k++) {
							if (encounterSetsRaw[k].trim()) {
								encounterSets.push(encounterSetsRaw[k].trim());
							}
						}
					}
					if (context == 'renderer') {
						s.set('AdditionalEncounterSetsLength', encounterSets.length);
					}
					while (encounterSets.length < 6) {
						encounterSets.push('');
					}
					for (let k = 0; k < encounterSets.length; k++) {
						let iconName = escapeIconFileName(encounterSets[k]);
						if (iconName == '') {
							s.set('EncounterSet' + (k + 1), 'Empty');
							s.set('EncounterSet' + (k + 1) + '-external-path', '');
						}
						else if (icons.indexOf(iconName) > -1) {
							s.set('EncounterSet' + (k + 1), 'Custom');
							s.set('EncounterSet' + (k + 1) + '-external-path', 'project:imagesIcons/' + iconName + '.png');
						}
						else {
							s.set('EncounterSet' + (k + 1), convertIconName(encounterSets[k].trim()));
							s.set('EncounterSet' + (k + 1) + '-external-path', '');
						}
					}
				}

				if (card['_Encounter Set Number Start']) {
					s.set('EncounterSetNumber', parseInt(card['_Encounter Set Number Start']) + j);
				}
				else {
					s.set('EncounterSetNumber', 0);
				}

				if (card['_Encounter Set Total']) {
					s.set('EncounterSetTotal', card['_Encounter Set Total']);
				}
				else {
					s.set('EncounterSetTotal', 0);
				}

				if (flags.indexOf('BlueRing') > -1) {
					s.set('Difficulty', 'Blue');
				}
				else if (flags.indexOf('GreenRing') > -1) {
					s.set('Difficulty', 'Green');
				}
				else if (flags.indexOf('RedRing') > -1) {
					s.set('Difficulty', 'Red');
				}
				else if (card['Removed for Easy Mode'] && j >= parseInt(card['Quantity']) - parseInt(card['Removed for Easy Mode'])) {
					s.set('Difficulty', 'Gold');
				}
				else {
					s.set('Difficulty', 'Standard');
				}

				if (((cardType == PRESENTATION) && (['BlueNightmare', 'GreenNightmare', 'PurpleNightmare', 'RedNightmare', 'BrownNightmare', 'YellowNightmare'].indexOf(cardSphere) == -1)) || (cardType == RULES)) {
					s.set('Collection', 'Empty');
					s.set('Collection-external-path', '');
				}
				else {
					let selectedIcon;
					if (card['Collection Icon']) {
						selectedIcon = card['Collection Icon'];
					}
					else if (setIcon + '') {
						selectedIcon = setIcon;
					}
					else {
						selectedIcon = card['Set'];
					}

					let iconName;
					if (flags.indexOf(PROMO) > -1) {
						iconName = escapeIconFileName(selectedIcon) + '_black';
					}
					else {
						iconName = escapeIconFileName(selectedIcon) + '_stroke';
					}
					if (icons.indexOf(iconName) > -1) {
						s.set('Collection', 'Custom');
						s.set('Collection-external-path', 'project:imagesIcons/' + iconName + '.png');
					}
					else {
						let iconName = escapeIconFileName(selectedIcon);
						if (icons.indexOf(iconName) > -1) {
							s.set('Collection', 'Custom');
							s.set('Collection-external-path', 'project:imagesIcons/' + iconName + '.png');
						}
						else {
							s.set('Collection', convertIconName(selectedIcon));
							s.set('Collection-external-path', '');
						}
					}
				}

				if (card['Copyright']) {
					s.set('Copyright', card['Copyright']);
				}
				else {
					s.set('Copyright', setCopyright);
				}

				if ((cardType == FULL_ART_LANDSCAPE) || (cardType == FULL_ART_PORTRAIT)) {
					s.set('Artist', '<right>' + s.get('Artist'));
				}

				let defaultBodyPointSize = 7.5;
				if (cardType in bodyPointSize) {
					defaultBodyPointSize = bodyPointSize[cardType];
				}

				let defaultFlavourPointSize = 6.25;
				if (cardType in flavourPointSize) {
					defaultFlavourPointSize = flavourPointSize[cardType];
				}

				let defaultTraitPointSize = 8.25;
				if (cardType in traitPointSize) {
					defaultTraitPointSize = traitPointSize[cardType];
				}

				let defaultNamePointSize = 6.5;
				if (cardType in namePointSize) {
					defaultNamePointSize = namePointSize[cardType];
				}

				let defaultBottomPointSize = 4;
				if (cardType in bottomPointSize) {
					defaultBottomPointSize = bottomPointSize[cardType];
				}

				let defaultStarPointSize = 6.5;
				let defaultOptionLeftPointSize = 12;
				let defaultPagePointSize = 7;
				let defaultEncounterSetNumberPointSize = 4;

				s.set('Rules-format', '<left><tracking -0.005><family "Times New Roman"><size ' + defaultBodyPointSize + '>');
				s.set('Rules-formatEnd', '</size></family>');
				s.set('RulesBack-format', '<left><tracking -0.005><family "Times New Roman"><size ' + defaultBodyPointSize + '>');
				s.set('RulesBack-formatEnd', '</size></family>');
				s.set('RulesRight-format', '<left><tracking -0.005><family "Times New Roman"><size ' + defaultBodyPointSize + '>');
				s.set('RulesRight-formatEnd', '</size></family>');
				s.set('Shadow-format', '<image res://TheLordOfTheRingsLCG/image/empty1x1.png 0.1 0.005>' +
					'<br><center><image res://TheLordOfTheRingsLCG/image/ShadowSeparator.png 1.55in>' +
					'<br><image res://TheLordOfTheRingsLCG/image/empty1x1.png 0.1 0.005>' +
					'<br><left><tracking -0.005><family "Times New Roman"><size ' + defaultBodyPointSize + '><i>');
				s.set('Shadow-formatEnd', '</i></size></family>');
				s.set('Flavour-format', '<left><tracking -0.005><family "Times New Roman"><size ' + defaultFlavourPointSize + '><i>');
				s.set('Flavour-formatEnd', '</i></size></family>');
				s.set('FlavourBack-format', '<left><tracking -0.005><family "Times New Roman"><size ' + defaultFlavourPointSize + '><i>');
				s.set('FlavourBack-formatEnd', '</i></size></family>');
				s.set('Story-format', '<left><tracking -0.005><family "Times New Roman"><size ' + defaultFlavourPointSize + '><i>');
				s.set('Story-formatEnd', '</i></size></family>');
				s.set('StoryBack-format', '<left><tracking -0.005><family "Times New Roman"><size ' + defaultFlavourPointSize + '><i>');
				s.set('StoryBack-formatEnd', '</i></size></family>');
				s.set('Trait-format', '<center><tracking -0.005><family "Times New Roman"><size ' + defaultTraitPointSize + '><i><b>');
				s.set('Trait-formatEnd', '</b></i></size></family>');
				s.set('PageIn-format', '<right><tracking -0.005><family "Times New Roman"><size ' + defaultPagePointSize + '><b>');
				s.set('PageIn-formatEnd', '</b></size></family>');

				s.set('Body-style', 'FAMILY: {"Times New Roman"}');
				s.set('BodyRight-style', 'FAMILY: {"Times New Roman"}');
				s.set('Trait-style', 'FAMILY: {"Times New Roman"}');
				s.set('Name-style', 'FAMILY: {"Vafthaurdir"}');
				s.set('Subtype-style', 'FAMILY: {"Vafthrudnir"}');
				s.set('Type-style', 'FAMILY: {"Vafthrudnir"}');
				s.set('Adventure-style', 'FAMILY: {"Vafthrudnir"}');
				s.set('Cycle-style', 'FAMILY: {"Vafthrudnir"}');
				s.set('Option-style', 'WIDTH: SEMICONDENSED; FAMILY: {"Vafthrudnir"}');
				s.set('EncounterSetNumber-style', 'WEIGHT: BOLD; FAMILY: {"Times New Roman"}');
				s.set('Bottom-style', 'WIDTH: SEMICONDENSED; WEIGHT: BOLD; FAMILY: {"Times New Roman"}');
				s.set('Star-style', 'FAMILY: {"Times New Roman"}');
				s.set('OptionLeft-style', 'FAMILY: {"Times New Roman"}');
				s.set('Side-style', 'FAMILY: {"Vafthrudnir"}');
				s.set('Star-colour', '#FFFFFF');
				s.set('OptionLeft-colour', '#000000');
				s.set('Name-pointsize', Math.round(defaultNamePointSize * 1.734 * 100) / 100);
				s.set('Bottom-pointsize', defaultBottomPointSize);
				s.set('Star-pointsize', defaultStarPointSize);
				s.set('OptionLeft-pointsize', defaultOptionLeftPointSize);
				s.set('EncounterSetNumber-pointsize', defaultEncounterSetNumberPointSize);
				s.set('OptionLeft-alignment', 'bottom,center');
				s.set('Engagement-tint', '32.0,1.0,0.9');
				s.set('Progress-tint', '32.0,1.0,0.9');
				s.set('HitPoints-tint', '0.0,0.8,1.0');
				s.set('ResourceCost-tint', '180.0,0.0,1.0');
				s.set('Stage-tint', '190.0,0.6,0.9');
				s.set('Difficulty-tint', '0.0,0.2,1.0');
				s.set('LRL-IllustratorShort', translate['Illustrator'][lang]);
				s.set('LRL-IllustratorUnknown', translate['Illustrator'][lang] + ' ' + translate['Unknown Artist'][lang]);
				s.set('LRL-Page', translate['Page'][lang]);
				s.set('LRL-PageOf', '</size><size 3> </size><size 7>/</size><size 3> </size><size 7>');
				s.set('HorizontalSpacer-tag-replacement', '<image res://TheLordOfTheRingsLCG/image/empty1x1.png 0.3 0.1>');

				if ((cardType == PRESENTATION) || (cardType == RULES)) {
					s.set('VerticalSpacer-tag-replacement', '<image res://TheLordOfTheRingsLCG/image/empty1x1.png 0.1 0.1>');
					s.set('Body-lineTightness', 0.8);
					s.set('BodyRight-lineTightness', 0.8);
				}
				else {
					s.set('VerticalSpacer-tag-replacement', '<image res://TheLordOfTheRingsLCG/image/empty1x1.png 0.075 0.075>');
					s.set('Body-lineTightness', 0.2);
					s.set('BodyRight-lineTightness', 0.2);
				}

				if (cardType == HERO_PROMO) {
					s.set('Bottom-colour', '#000000');
					s.set('Bottom-stroke', 'Custom');
					s.set('Bottom-stroke-colour', '#00000000');
					s.set('Bottom-stroke-width', 1);
				}
				else {
					s.set('Bottom-colour', '#FFFFFF');
					s.set('Bottom-stroke', 'Medium');
					s.set('Bottom-stroke-colour', '#F0000000');
					s.set('Bottom-stroke-width', 2);
				}

				if ((cardType == CAVE) || (cardType == REGION)) {
					s.set('Body-colour', '#FFFFFF');
					s.set('BodyRight-colour', '#FFFFFF');
					s.set('Name-colour', '#FFFFFF');
				}
				else {
					s.set('Body-colour', '#000000');
					s.set('BodyRight-colour', '#000000');
					s.set('Name-colour', '#000000');
				}

				if ((optionalTraitTypes.indexOf(cardType) > -1) && cardTrait) {
					s.set('TraitOut', 'true');
					if (cardType + cardSphere in bodyRegion) {
						s.set('TraitOut-Body-region', bodyRegion[cardType + cardSphere]);
					}
					else if (cardType in bodyRegion) {
						s.set('TraitOut-Body-region', bodyRegion[cardType]);
					}

					if (cardType + cardSphere in traitRegion) {
						s.set('TraitOut-Trait-region', traitRegion[cardType + cardSphere]);
					}
					else if (cardType in traitRegion) {
						s.set('TraitOut-Trait-region', traitRegion[cardType]);
					}
				}
				else if (cardType + cardSphere in bodyNoTraitRegion) {
					s.set('TraitOut', 'false');
					s.set('Body-region', bodyNoTraitRegion[cardType + cardSphere]);
				}
				else if (cardType in bodyNoTraitRegion) {
					s.set('TraitOut', 'false');
					s.set('Body-region', bodyNoTraitRegion[cardType]);
				}
				else {
					s.set('TraitOut', 'true');
					if ((cardType == HERO_PROMO) && (lang in bodyRegionHeroPromo)) {
						s.set('TraitOut-Body-region', bodyRegionHeroPromo[lang]);
					}
					else if ((cardType == ENEMY) && (cardName == 'Touque Rapporteuse')) { // workaround for the French card
						s.set('TraitOut-Body-region', '57,377,299,123');
					}
					else if (cardType + cardSphere in bodyRegion) {
						s.set('TraitOut-Body-region', bodyRegion[cardType + cardSphere]);
					}
					else if (cardType in bodyRegion) {
						s.set('TraitOut-Body-region', bodyRegion[cardType]);
					}

					if (cardType + cardSphere in traitRegion) {
						s.set('TraitOut-Trait-region', traitRegion[cardType + cardSphere]);
					}
					else if (cardType in traitRegion) {
						s.set('TraitOut-Trait-region', traitRegion[cardType]);
					}
				}

				if ((s.get('Unique') + '' == '1') || (cardName.indexOf('[ringa]') != -1) || (cardName.indexOf('[ringb]') != -1)) {
					if (cardType + cardSphere in nameUniqueRegion) {
						s.set('Name-region', nameUniqueRegion[cardType + cardSphere]);
					}
					else if (cardType in nameUniqueRegion) {
						s.set('Name-region', nameUniqueRegion[cardType]);
					}
				}
				else if ((cardType == TREACHERY) && (cardName == 'Dziewi\u0119ciu Kr\u0105\u017cy po \u015awiecie')) { // workaround for the Polish card
					s.set('Name-region', '54,101,26,178');
				}
				else if ((cardType == TREACHERY) && (cardName == 'Zagubiony w mie\u015bcie goblin\u00f3w')) { // workaround for the Polish card
					s.set('Name-region', '55,100,26,180');
				}
				else {
					if (cardType + cardSphere in nameRegion) {
						s.set('Name-region', nameRegion[cardType + cardSphere]);
					}
					else if (cardType in nameRegion) {
						s.set('Name-region', nameRegion[cardType]);
					}
				}

				if ((s.get('UniqueBack') + '' == '1') || (cardNameBack && ((cardNameBack.indexOf('[ringa]') != -1) || (cardNameBack.indexOf('[ringb]') != -1)))) {
					if (cardType + cardSphere in nameUniqueBackRegion) {
						s.set('NameBack-region', nameUniqueBackRegion[cardType + cardSphere]);
					}
					else if (cardType in nameUniqueBackRegion) {
						s.set('NameBack-region', nameUniqueBackRegion[cardType]);
					}
				}
				else {
					if (cardType + cardSphere in nameBackRegion) {
						s.set('NameBack-region', nameBackRegion[cardType + cardSphere]);
					}
					else if (cardType in nameBackRegion) {
						s.set('NameBack-region', nameBackRegion[cardType]);
					}
				}

				if ((cardType == HERO_PROMO) && (translate[cardType][lang].length > 4)) {
					s.set('Type-region', '279,448,39,15');
				}
				else {
					if (cardType + cardSphere in typeRegion) {
						s.set('Type-region', typeRegion[cardType + cardSphere]);
					}
					else if (cardType in typeRegion) {
						s.set('Type-region', typeRegion[cardType]);
					}
				}

				if (cardType == QUEST) {
					s.set('Stage-region', questStageRegion[s.get('Stage') + '']);
				}

				let relations = [
					['Portrait-portrait-clip-region', portraitRegion],
					['PortraitBack-portrait-clip-region', portraitBackRegion],
					['BodyBack-region', bodyBackRegion],
					['BodyRight-region', bodyRightNoTraitRegion],
					['Subtype-region', subtypeRegion],
					['HitPoints-region', hitPointsRegion],
					['Engagement-region', engagementRegion],
					['Attack-region', attackRegion],
					['Defense-region', defenseRegion],
					['Willpower-region', willpowerRegion],
					['Threat-region', threatRegion],
					['ThreatCost-region', threatCostRegion],
					['Progress-region', progressRegion],
					['Adventure-region', adventureRegion],
					['Cycle-region', cycleRegion],
					['ResourceCost-region', resourceCostRegion],
					['Difficulty-region', difficultyRegion],
					['EncounterSet-portrait-clip-region', encounterPortraitRegion],
					['EncounterSetNumber-region', encounterNumberRegion],
					['OptionLeft-region', optionLeftRegion],
					['OptionRightDecoration-region', optionRightDecorationRegion],
					['OptionRight-region', optionRightRegion],
					['Artist-region', artistRegion],
					['Copyright-region', copyrightRegion],
					['Collection-portrait-clip-region', collectionPortraitRegion],
					['CollectionNumber-region', collectionNumberRegion],
					['CollectionInfo-region', collectionInfoRegion],
					['PageIn-region', pageInRegion],
					['Side-region', sideRegion],
					['Star-region', starRegion],
					['GameName-portrait-clip-region', gameNamePortraitRegion],
					['Name-portrait-clip-region', namePortraitRegion],
					['EncounterSet1-portrait-clip-region', encounterSet1PortraitRegion],
					['EncounterSet2-portrait-clip-region', encounterSet2PortraitRegion],
					['EncounterSet3-portrait-clip-region', encounterSet3PortraitRegion],
					['EncounterSet4-portrait-clip-region', encounterSet4PortraitRegion],
					['EncounterSet5-portrait-clip-region', encounterSet5PortraitRegion],
					['EncounterSet6-portrait-clip-region', encounterSet6PortraitRegion],
					['Sphere-Body-shape', sphereBodyShape],
					['Option-Body-shape', optionBodyShape]
				];
				for (let k = 0; k < relations.length; k++) {
					if (cardType + cardSphere in relations[k][1]) {
						s.set(relations[k][0], relations[k][1][cardType + cardSphere]);
					}
					else if (cardType in relations[k][1]) {
						s.set(relations[k][0], relations[k][1][cardType]);
					}
				}

				if (s.get('Name-region') && cardName && cardName.match(/[\u00c0\u00c1\u00c2\u00c3\u00c4\u00c8\u00c9\u00ca\u00cb\u00cc\u00cd\u00ce\u00cf\u00d1\u00d2\u00d3\u00d4\u00d5\u00d6\u00d9\u00da\u00db\u00dc\u0106\u0108\u0143\u015a\u0179\u017b]/)) {
					let parts = s.get('Name-region').split(',');
					if ([EVENT, TREACHERY].indexOf(cardType) > -1) {
						parts[0] = (parseInt(parts[0]) + 1).toString();
					}
					else {
						parts[1] = (parseInt(parts[1]) + 2).toString();
					}
					s.set('Name-region', parts.join(','));
				}

				if (s.get('NameBack-region') && cardNameBack && cardNameBack.match(/[\u00c0\u00c1\u00c2\u00c3\u00c4\u00c8\u00c9\u00ca\u00cb\u00cc\u00cd\u00ce\u00cf\u00d1\u00d2\u00d3\u00d4\u00d5\u00d6\u00d9\u00da\u00db\u00dc\u0106\u0108\u0143\u015a\u0179\u017b]/)) {
					let parts = s.get('NameBack-region').split(',');
					parts[1] = (parseInt(parts[1]) + 2).toString();
					s.set('NameBack-region', parts.join(','));
				}

				if ((cardType in sphereOptionBodyShape) && s.get('OptionRight') && (s.get('OptionRight') + '').length) {
					s.set('Sphere-Body-shape', sphereOptionBodyShape[cardType]);
				}

				if (cardType in threatCostTint) {
					s.set('ThreatCost-tint', threatCostTint[cardType]);
				}
				else {
					s.set('ThreatCost-tint', '200.0,0.7,0.7');
				}

				let copy;
				if (playerCopies) {
					copy = 'p';
				}
				else {
					copy = j + 1;
				}

				let back;
				let simple_back;
				if (side == 'back') {
					back = '-';
					simple_back = true;
				}
				else if (doubleSide) {
					back = '-';
					simple_back = false;
				}
				else if (card['BName']) {
					back = '-';
					simple_back = true;
				}
				else if ((playerTypes.indexOf(cardType) > -1 &&
						(keywords + '').replace(/\. /g, '.').split('.').indexOf(translate['Encounter Keyword'][lang]) == -1 &&
						(card['Card Back'] + '') != 'Encounter') ||
						(card['Card Back'] + '') == 'Player') {
					back = 'p';
					simple_back = true;
				}
				else {
					back = 'e';
					simple_back = true;
				}

				let fname = (Array(Math.max(0, 4 - (card['Card Number'] + '').length)).join('0') + card['Card Number'] + '-' + copy + '-' +
					back + '-' + escapeFileName(card['Name']) + Array(50).join('-')).substring(0, 50) + card['octgn'] + suffix;

				s.set('Id', card['octgn']);
				if (context == 'renderer') {
					s.set('Star-format', '<family "Times New Roman"><size ' + defaultStarPointSize + '>');
					s.set('Star-formatEnd', '</size></family>');
					s.set('Bottom-format', '<width semicondensed><family "Times New Roman"><size ' + defaultBottomPointSize + '><b>');
					s.set('Bottom-formatEnd', '</b></size></family></width>');
					s.set('EncounterSetNumber-format', '<family "Times New Roman"><size ' + defaultEncounterSetNumberPointSize + '><b>');
					s.set('EncounterSetNumber-formatEnd', '</b></size></family>');
					s.set('OptionLeft-format', '<family "Times New Roman"><size ' + defaultOptionLeftPointSize + '>');
					s.set('OptionLeft-formatEnd', '</size></family>');
					s.set('OptionRight-format', '<width semicondensed>');
					s.set('OptionRight-formatEnd', '</width>');
					s.set('TypeRenderer', cardType);
					s.set('DoubleSide', doubleSide);
					s.set('SuffixRenderer', suffix);
				}

				if (progress) {
					progress.status = fname;
				}

				saveResult(s, setID, lang, newCard, fname, simple_back, png300Bleed, png480Bleed, png800Bleed);
			}
		}
	}
	return;
}

function isDoubleSide(cardType, cardTypeBack) {
	if (doubleSideTypes.indexOf(cardType + '') > -1) {
		return true;
	}
	else if ((cardType + '' == CONTRACT) && (cardTypeBack + '' == CONTRACT)) {
		return true;
	}
	else {
		return false;
	}
}

function capitalizeWord(value) {
	return value.charAt(0).toUpperCase() + value.slice(1);
}

function capitalizeText(value) {
	value = value + '';
	value = value.split(' ').map(capitalizeWord).join(' ');
	value = value.split('-').map(capitalizeWord).join('-');
	return value;
}

function convertIconName(value) {
	value = value + '';
	value = value.replace(/[,\(\)'"\u2013\u2014\u2026\u2019\u201c\u201d\u201e\u00ab\u00bb]/g, '');
	value = value.replace(/\u00c2/g, 'A');
	value = value.replace(/\u00e2/g, 'a');
	value = value.replace(/\u00ce/g, 'I');
	value = value.replace(/\u00ee/g, 'i');
	value = value.replace(/\u00d3/g, 'O');
	value = value.replace(/\u00f3/g, 'o');
	value = value.replace(/[\u00da\u00db]/g, 'U');
	value = value.replace(/[\u00fa\u00fb]/g, 'u');
	value = capitalizeText(value);
	value = value.replace(/[\-\u2013\u2014 ]/g, '');
	return value;
}

function escapeFileName(value) {
	value += '';
	value = value.replace(/[<>:\/\\|?*'"\u2013\u2014\u2026\u2019\u201c\u201d\u201e\u00ab\u00bb\u00bf\u00a1]/g, ' ');
	value = value.trim();
	return value;
}

function escapeIconFileName(value) {
	value += '';
	value = value.replace(/[<>:\/\\|?*'"\u2013\u2014\u2026\u2019\u201c\u201d\u201e\u00ab\u00bb\u00bf\u00a1]/g, '');
	value = value.replace(/\u00c2/g, 'A');
	value = value.replace(/\u00e2/g, 'a');
	value = value.replace(/\u00ce/g, 'I');
	value = value.replace(/\u00ee/g, 'i');
	value = value.replace(/\u00d3/g, 'O');
	value = value.replace(/\u00f3/g, 'o');
	value = value.replace(/[\u00da\u00db]/g, 'U');
	value = value.replace(/[\u00fa\u00fb]/g, 'u');
	value = value.replace(/ /g, '-');
	return value;
}

function updatePunctuation(value, lang) {
	if (lang == POLISH) {
		value = value.replace(/\u201c/g, '\u201e');
	}
	else if (lang == GERMAN) {
		value = value.replace(/\u201c/g, '\u201e');
		value = value.replace(/\u201d/g, '\u201c');
	}
	else if (lang == FRENCH) {
		value = value.replace(/\u201c[ \u00a0]?/g, '\u00ab\u00a0');
		value = value.replace(/[ \u00a0]?\u201d/g, '\u00a0\u00bb');
		value = value.replace(/[ \u00a0]?([:;?!])/g, '\u00a0$1');

		var valueOld;
		do {
			valueOld = value;
			value = value.replace(/\u00a0([:;?!][^<]+)>/g, '$1>');
		}
		while (value != valueOld);
	}

	return value;
}

function updateVafthrudnir(value, lowerSize, lang) {
	var upperSize = Math.round(lowerSize * 1.423 * 100) / 100;
	var ringSize = Math.round(lowerSize * 1.692 * 100) / 100;
	var res = '';
	var tag = false;
	value = value.replace(/\[space\]/g, ' ');
	value = value.replace(/\[SPACE\]/g, ' ');
	value = value.replace(/\[ringa\]/g, '<ringa>');
	value = value.replace(/\[ringb\]/g, '<ringb>');
	value = updatePunctuation(value, lang);
	for (let i = 0; i < value.length; i++) {
		let ch = value[i];
		if (ch == '\u00df') {
			ch = 'ss';
		}
		if (ch == '<') {
			res += ch;
			tag = true;
		}
		else if (ch == '>') {
			res += ch;
			tag = false;
		}
		else if (tag) {
			res += ch;
		}
		else if ((ch == ch.toLowerCase()) && !ch.match(/[&0-9;:,.!\u1d31\u00a1?\u00bf\-\u2013\(\)'\u2019"\u201c\u201d\u201e\u00ab\u00bb \u00a0\u00df]/)) {
			if (ch.match(/[a-z&0-9;:,.!? ]/i)) {
				res += ch.toUpperCase();
			}
			else {
				res += '</size></family><family "Vafthaurdir"><size ' + lowerSize + '>' + ch.toUpperCase() + '</size></family><family "Vafthrudnir"><size ' + lowerSize + '>';
			}
		}
		else {
			if (ch.match(/[a-z&0-9;:,.!? ]/i)) {
				res += '</size><size ' + upperSize + '>' + ch + '</size><size ' + lowerSize + '>';
			}
			else {
				res += '</size></family><family "Vafthaurdir"><size ' + upperSize + '>' + ch + '</size></family><family "Vafthrudnir"><size ' + lowerSize + '>';
			}
		}
	}
	res = res.replace(/<ringa>/g, '</size></family><lrs><size ' + ringSize + '>A</size></lrs><family "Vafthrudnir"><size ' + lowerSize + '>');
	res = res.replace(/<ringb>/g, '</size></family><lrs><size ' + ringSize + '>B</size></lrs><family "Vafthrudnir"><size ' + lowerSize + '>');
	res = res.replace(/<size [^>]+> <\/size>(?:<size [^>]+><\/size>)*<\/family><lrs>/g, '<size ' + lowerSize + '> </size></family><lrs>')
	res = '<family "Vafthrudnir"><size ' + lowerSize + '>' + res + '</size></family>';
	res = res.replace(/<size [^>]+><\/size>/g, '');
	res = res.replace(/<family [^>]+><\/family>/g, '');
	return res;
}

function markUp(value, key, cardType, lang, setID) {
	value += '';
	value = value.replace(/ +(?=\n|$)/g, '');
	value = value.replace(/\n+$/g, '');
	value = value.replace(/\[nobr\]/g, '\u00a0');
	value = value.replace(/\[br\]/g, '');
	value = value.replace(/\[inline\]\n\n/g, ' ');
	value = value.replace(/\[inline\]/g, '');

	if (['Side', 'Subtype'].indexOf(key + '') > -1) {
		return updateVafthrudnir(value, 3.515, lang);
	}
	else if (key == 'Type') {
		return updateVafthrudnir(value, 5.095, lang);
	}
	else if (['Name', 'BName'].indexOf(key + '') > -1) {
		let lowerSize = 6.5;
		if (cardType in namePointSize) {
			lowerSize = namePointSize[cardType];
		}

		if (lang == FRENCH) {
			value = value.replace(/ /g, '\u00a0');
			let valueOld;
			do {
				valueOld = value;
				value = value.replace(/\u00a0([^<]+)>/g, ' $1>');
			}
			while (value != valueOld);
		}
		return updateVafthrudnir(value, lowerSize, lang);
	}
	else if ((['Victory Points', 'BVictory Points'].indexOf(key + '') > -1) && ([PRESENTATION, RULES].indexOf(cardType) == -1)) {
		return updateVafthrudnir(value, 3.69, lang);
	}
	else if (key == 'Adventure') {
		if (cardType == CAMPAIGN) {
			return updateVafthrudnir(value, 5.6, lang);
		}
		else {
			return updateVafthrudnir(value, 3.69, lang);
		}
	}

	if (['Text', 'BText', 'Shadow', 'BShadow'].indexOf(key + '') > -1) {
		if (lang == ENGLISH) {
			value = value.replace(/\b(Valour )?(Resource |Planning |Quest |Travel |Encounter |Combat |Refresh )?(Action):/g, '[b]$1$2$3[/b]:');
			value = value.replace(/\b(When Revealed|Forced|Valour Response|Response|Travel|Shadow|Resolution):/g, '[b]$1[/b]:');
			value = value.replace(/\b(Setup)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(Condition)\b/g, '[bi]$1[/bi]');
		}
		else if (lang == FRENCH) {
			value = value.replace(/(\[Vaillance\] )?(\[Ressource\] |\[Organisation\] |\[Qu\u00eate\] |\[Voyage\] |\[Rencontre\] |\[Combat\] |\[Restauration\] )?\b(Action) ?:/g, '[b]$1$2$3[/b] :');
			value = value.replace(/\b(Une fois r\u00e9v\u00e9l\u00e9e|Forc\u00e9|\[Vaillance\] R\u00e9ponse|R\u00e9ponse|Trajet|Ombre|R\u00e9solution) ?:/g, '[b]$1[/b] :');
			value = value.replace(/\b(Mise en place)( \([^\)]+\))? ?:/g, '[b]$1[/b]$2 :');
			value = value.replace(/\b(Condition)\b/g, '[bi]$1[/bi]');
		}
		else if (lang == GERMAN) {
			value = value.replace(/\b(Ehrenvolle )?(Ressourcenaktion|Planungsaktion|Abenteueraktion|Reiseaktion|Begegnungsaktion|Kampfaktion|Auffrischungsaktion|Aktion):/g, '[b]$1$2[/b]:');
			value = value.replace(/\b(Wenn aufgedeckt|Erzwungen|Ehrenvolle Reaktion|Reaktion|Reise|Schatten|Aufl\u00f6sung):/g, '[b]$1[/b]:');
			value = value.replace(/\b(Vorbereitung)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(Zustand)\b/g, '[bi]$1[/bi]');
		}
		else if (lang == ITALIAN) {
			value = value.replace(/\b(Azione)( Valorosa)?( di Risorse| di Pianificazione| di Ricerca| di Viaggio| di Incontri| di Combattimento| di Riordino)?:/g, '[b]$1$2$3[/b]:');
			value = value.replace(/\b(Quando Rivelata|Obbligato|Risposta Valorosa|Risposta|Viaggio|Ombra|Risoluzione):/g, '[b]$1[/b]:');
			value = value.replace(/\b(Preparazione)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(Condizione)\b/g, '[bi]$1[/bi]');
		}
		else if (lang == POLISH) {
			value = value.replace(/\b(Akcja)( Zasob\u00f3w| Planowania| Wyprawy| Podr\u00f3\u017cy| Spotkania| Walki| Odpoczynku)?( M\u0119stwa)?:/g, '[b]$1$2$3[/b]:');
			value = value.replace(/\b(Po odkryciu|Wymuszony|Odpowied\u017a M\u0119stwa|Odpowied\u017a|Podr\u00f3\u017c|Cie\u0144|Nast\u0119pstwa):/g, '[b]$1[/b]:');
			value = value.replace(/\b(Przygotowanie)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(Stan)\b/g, '[bi]$1[/bi]');
		}
		else if (lang == PORTUGUESE) {
			value = value.replace(/\b(A\u00e7\u00e3o)( Valorosa)?( de Recursos| de Planejamento| de Miss\u00e3o| de Viagem| de Encontro| de Combate| de Renova\u00e7\u00e3o)?:/g, '[b]$1$2$3[/b]:');
			value = value.replace(/\b(Efeito Revelado|Efeito For\u00e7ado|Resposta Valorosa|Resposta|Viagem|Efeito Sombrio|Resolu\u00e7\u00e3o):/g, '[b]$1[/b]:');
			value = value.replace(/\b(Prepara\u00e7\u00e3o)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(Condi\u00e7\u00e3o)\b/g, '[bi]$1[/bi]');
		}
		else if (lang == SPANISH) {
			value = value.replace(/\b(Acci\u00f3n)( de Recursos| de Planificaci\u00f3n| de Misi\u00f3n| de Viaje| de Encuentro| de Combate| de Recuperaci\u00f3n)?( de Valor)?:/g, '[b]$1$2$3[/b]:');
			value = value.replace(/\b(Al ser revelada|Obligado|Respuesta de Valor|Respuesta|Viaje|Sombra|Resoluci\u00f3n):/g, '[b]$1[/b]:');
			value = value.replace(/\b(Preparaci\u00f3n)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(Estado)\b/g, '[bi]$1[/bi]');
		}
	}

	var defaultPointSize;
	if (['Traits', 'BTraits'].indexOf(key + '') > -1) {
		if (cardType in traitPointSize) {
			defaultPointSize = traitPointSize[cardType];
		}
		else {
			defaultPointSize = 8.25;
		}
	}
	else if (['Flavour', 'BFlavour'].indexOf(key + '') > -1) {
		if (cardType in flavourPointSize) {
			defaultPointSize = flavourPointSize[cardType];
		}
		else {
			defaultPointSize = 6.25;
		}
	}
	else if (['Icons', 'BIcons'].indexOf(key + '') > -1) {
		defaultPointSize = 12;
	}
	else {
		if (cardType in bodyPointSize) {
			defaultPointSize = bodyPointSize[cardType];
		}
		else {
			defaultPointSize = 7.5;
		}
	}

	var matchRegExp = /^\[defaultsize ([0-9\.]+)\]/g;
	var match = matchRegExp.exec(value);
	if (match) {
		defaultPointSize = match[1];
	}
	var iconPointSize = defaultPointSize * 1.2;

	var tagPrefix;
	var tagSuffix;
	if (['Traits', 'BTraits'].indexOf(key + '') > -1) {
		value = value.replace(/\[bi\]((?:.|\n)*?)\[\/bi\]/g, '$1');
		value = value.replace(/\[b\]((?:.|\n)*?)\[\/b\]/g, '$1');
		value = value.replace(/\[i\]((?:.|\n)*?)\[\/i\]/g, '$1');
		tagPrefix = '</b></i></size></family><size ' + iconPointSize + '>';
		tagSuffix = '</size><family "Times New Roman"><size ' + defaultPointSize + '><i><b>';
	}
	else if (['Shadow', 'BShadow', 'Flavour', 'BFlavour'].indexOf(key + '') > -1) {
		value = value.replace(/\[bi\]((?:.|\n)*?)\[\/bi\]/g, '[b]$1[/b]');
		value = value.replace(/\[i\]((?:.|\n)*?)\[\/i\]/g, '$1');
		tagPrefix = '</i></size></family><size ' + iconPointSize + '>';
		tagSuffix = '</size><family "Times New Roman"><size ' + defaultPointSize + '><i>';
	}
	else {
		tagPrefix = '</size></family><size ' + iconPointSize + '>';
		tagSuffix = '</size><family "Times New Roman"><size ' + defaultPointSize + '>';
	}

	function updateItalicIconsReplacer(match, offset, string) {
		var res = match.replace(/(\[unique\]|\[threat\]|\[attack\]|\[defense\]|\[willpower\]|\[leadership\]|\[lore\]|\[spirit\]|\[tactics\]|\[baggins\]|\[fellowship\]|\[sunny\]|\[cloudy\]|\[rainy\]|\[stormy\]|\[sailing\]|\[eos\]|\[pp\]|\[ringa\]|\[ringb\])/g, '[/i]$1[i]');
		return res;
	}
	value = value.replace(/\[i\](?:.|\n)+?\[\/i\]/g, updateItalicIconsReplacer);

	value = value.replace(/\[bi\]\[bi\]/g, '[bi]');
	value = value.replace(/\[\/bi\]\[\/bi\]/g, '[/bi]');
	value = value.replace(/\[b\]\[b\]/g, '[b]');
	value = value.replace(/\[\/b\]\[\/b\]/g, '[/b]');
	value = value.replace(/\[i\]\[i\]/g, '[i]');
	value = value.replace(/\[\/i\]\[\/i\]/g, '[/i]');
	value = value.replace(/</g, '[lt]');
	value = value.replace(/>/g, '[gt]');
	value = value.replace(/\[lt\]/g, '<lt>');
	value = value.replace(/\[gt\]/g, '<gt>');
	value = value.replace(/\[unique\]/g, tagPrefix + '<uni>' + tagSuffix);
	value = value.replace(/\[threat\]/g, tagPrefix + '<thr>' + tagSuffix);
	value = value.replace(/\[attack\]/g, tagPrefix + '<att>' + tagSuffix);
	value = value.replace(/\[defense\]/g, tagPrefix + '<def>' + tagSuffix);
	value = value.replace(/\[willpower\]/g, tagPrefix + '<wil>' + tagSuffix);
	value = value.replace(/\[leadership\]/g, tagPrefix + '<lea>' + tagSuffix);
	value = value.replace(/\[lore\]/g, tagPrefix + '<lor>' + tagSuffix);
	value = value.replace(/\[spirit\]/g, tagPrefix + '<spi>' + tagSuffix);
	value = value.replace(/\[tactics\]/g, tagPrefix + '<tac>' + tagSuffix);
	value = value.replace(/\[baggins\]/g, tagPrefix + '<bag>' + tagSuffix);
	value = value.replace(/\[fellowship\]/g, tagPrefix + '<fel>' + tagSuffix);
	value = value.replace(/\[sunny\]/g, tagPrefix + '<hon>' + tagSuffix);
	value = value.replace(/\[cloudy\]/g, tagPrefix + '<hof>' + tagSuffix);
	value = value.replace(/\[rainy\]/g, tagPrefix + '<hb>' + tagSuffix);
	value = value.replace(/\[stormy\]/g, tagPrefix + '<hw>' + tagSuffix);
	value = value.replace(/\[sailing\]/g, tagPrefix + '<sai>' + tagSuffix);
	value = value.replace(/\[eos\]/g, tagPrefix + '<eos>' + tagSuffix);
	value = value.replace(/\[pp\]/g, tagPrefix + '<pp>' + tagSuffix);
	value = value.replace(/\[ringa\]/g, tagPrefix + '<lrs>A</lrs>' + tagSuffix);
	value = value.replace(/\[ringb\]/g, tagPrefix + '<lrs>B</lrs>' + tagSuffix);
	value = value.replace(/\[center\]/g, '<center>');
	value = value.replace(/([^\n])\<center\>/g, '$1\n<center>');
	value = value.replace(/\[\/center\]\n?/g, '\n<left>');
	value = value.replace(/\[right\]/g, '<right>');
	value = value.replace(/([^\n])\<right\>/g, '$1\n<right>');
	value = value.replace(/\[\/right\]\n?/g, '\n<left>');
	value = value.replace(/\<left\>(\n*)\<center\>/g, '$1<center>');
	value = value.replace(/\<left\>(\n*)\<right\>/g, '$1<right>');
	value = value.replace(/\n*\<left\>$/g, '');
	value = value.replace(/\[bi\]/g, '<i><b>');
	value = value.replace(/\[\/bi\]/g, '</b></i>');
	value = value.replace(/\[b\]/g, '<b>');
	value = value.replace(/\[\/b\]/g, '</b>');
	value = value.replace(/\[i\]/g, '<i>');
	value = value.replace(/\[\/i\]/g, '</i>');
	value = value.replace(/\[u\]/g, '<u>');
	value = value.replace(/\[\/u\]/g, '</u>');
	value = value.replace(/\[strike\]/g, '<del>');
	value = value.replace(/\[\/strike\]/g, '</del>');
	value = value.replace(/\[red\]/g, '<color #8b1c23>');
	value = value.replace(/\[\/red\]/g, '</color>');
	value = value.replace(/\[space\]/g, '<hs>');
	value = value.replace(/\[vspace\]/g, '<image res://TheLordOfTheRingsLCG/image/empty1x1.png 0.025 0.025>');
	value = value.replace(/\[tab\]/g, '\t');
	value = value.replace(/\[lotr ([0-9\.]+)\]/g, '<lotr $1>');
	value = value.replace(/\[\/lotr\]/g, '</lotr>');
	value = value.replace(/\[lotrheader ([0-9\.]+)\]/g, '<lotrheader $1>');
	value = value.replace(/\[\/lotrheader\]/g, '</lotrheader>');
	value = value.replace(/\[size ([0-9\.]+)\]/g, '</size><size $1>');
	value = value.replace(/\[\/size\]/g, '</size><size ' + defaultPointSize + '>');
	value = value.replace(/^\[defaultsize ([0-9\.]+)\]\n*/g, '</size><size $1>');
	value = value.replace(/\[img ("?)([^\]]+)\]/g, '<image $1project:$2>');
	value = value.replace(/\<image ("?)project:icons\//g, '<image $1project:imagesIcons/');
	value = value.replace(/\<image ("?)project:custom\//g, '<image $1project:imagesCustom/' + setID + '_');
	value = value.replace(/\[lsb\]/g, '<lsb>');
	value = value.replace(/\[rsb\]/g, '<rsb>');
	value = value.replace(/<lsb>/g, '[');
	value = value.replace(/<rsb>/g, ']');

	value = value.replace(/([^:;,.?!\u2026]) ((?:<\/b>)?(?:<\/i>)?(?:<\/size>)?(?:<\/family>)?(?:<size [^>]+>)?)(<uni>|<thr>|<att>|<def>|<wil>|<lea>|<lor>|<spi>|<tac>|<bag>|<fel>|<mas>|<hon>|<hof>|<hb>|<hw>|<sai>|<eos>|<per>|<pp>|<lrs>)/g, '$1\u00a0$2$3');
	value = value.replace(/([0-9]+) /g, '$1\u00a0');
	value = value.replace(/ ([0-9]+)([:;,.?!\)\u2026])/g, '\u00a0$1$2');
	value = value.replace(/(^|[ \n"\u201c\u201d\(])([\-\u2013\u2014'\u2019A-Za-z\u00c0-\u017e]{1,4})([:;,.?!"\u2026\u201c\u201d\)]*) (["\u201c\u201d\(]*)([\-\u2013\u2014'\u2019A-Za-z\u00c0-\u017e]{1,4})([:;,.?!"\u2026\u201c\u201d\)]+(?:<\/[^>]+>)*)(\n|$)/g, '$1$2$3\u00a0$4$5$6$7');
	value = value.replace(/ (["\u201c\u201d\(]*)([\-\u2013\u2014'\u2019A-Za-z\u00c0-\u017e]{1,2})([:;,.?!"\u2026\u201c\u201d\)]+(?:<\/[^>]+>)*)(\n|$)/g, '\u00a0$1$2$3$4');
	value = value.replace(/ ([;:?!])/g, '\u00a0$1');

	var valueOld;
	do {
		valueOld = value;
		value = value.replace(/\u00a0([^<]+)>/g, ' $1>');
	}
	while (value != valueOld);

	value = value.replace(/\u2014/g, '\u2014</size><size 0.01>\u00a0</size><size ' + defaultPointSize + '>');
	value = value.replace(/<\/i>(?! )/g, '</size><size 0.01></i>\u00a0</size><size ' + defaultPointSize + '>');
	value = value.replace(/<\/i>(?= )/g, '</size><size 0.01></i> </size><size ' + defaultPointSize + '>');
	value = value.replace(/\n+$/g, '');
	value = value.replace(/\n(<left>|<right>|<center>)?(?=\n)/g, '\n$1<vs>');

	function updateVafthrudnirReplacer(match, p1, p2, offset, string) {
		var res = '</size></family>' + updateVafthrudnir(p2, p1, lang) + '<family "Times New Roman"><size ' + defaultPointSize + '>';
		return res;
	}
	value = value.replace(/<lotr ([0-9\.]+)>((?:.|\n)*?)<\/lotr>/g, updateVafthrudnirReplacer);

	function updateLotrHeaderReplacer(match, p1, p2, offset, string) {
		var res = '</size></family><family "Lord of the Headers"><size ' + p1 + '>' + p2 + '</size></family><family "Times New Roman"><size ' + defaultPointSize + '>';
		return res;
	}
	value = value.replace(/<lotrheader ([0-9\.]+)>((?:.|\n)*?)<\/lotrheader>/g, updateLotrHeaderReplacer);

	value = value.replace(/<size [^>]+><\/size>/g, '');
	value = value.replace(/<family [^>]+><\/family>/g, '');

	value = value.replace(/<hs>/g, '<image res://TheLordOfTheRingsLCG/image/empty1x1.png 0.3 0.1>');

	if ((cardType == PRESENTATION) || (cardType == RULES)) {
		value = value.replace(/<vs>/g, '<image res://TheLordOfTheRingsLCG/image/empty1x1.png 0.1 0.1>');
	}
	else {
		value = value.replace(/<vs>/g, '<image res://TheLordOfTheRingsLCG/image/empty1x1.png 0.075 0.075>');
	}

	value = updatePunctuation(value, lang);
	if ((['Traits', 'BTraits'].indexOf(key + '') > -1) && (lang == SPANISH)) {
		value = value.replace(/\. /g, ' \u2022 ');
		value = value.replace(/\.$/g, '');
	}

	return value;
}
