var doubleSideTypes = ['Campaign', 'Contract', 'Nightmare', 'Presentation', 'Quest', 'Rules'];
var playerTypes = ['Ally', 'Attachment', 'Contract', 'Event', 'Full Art Landscape', 'Full Art Portrait', 'Hero', 'Hero Promo', 'Player Objective', 'Player Side Quest', 'Treasure'];
var playerCopyTypes = ['Ally', 'Attachment', 'Event', 'Player Objective', 'Player Side Quest'];
var landscapeTypes = ['Cave', 'Encounter Side Quest', 'Encounter Side Quest SmallTextArea', 'Full Art Landscape', 'Player Side Quest', 'Region', 'Quest'];

var optionalTraitTypes = ['Cave', 'Encounter Side Quest', 'Encounter Side Quest SmallTextArea', 'Player Side Quest'];

/*
var Region = {};
Region['Ally'] = '';
Region['Attachment'] = '';
Region['Campaign'] = '';
Region['Cave'] = '';
Region['Contract'] = '';
Region['Encounter Side Quest'] = '';
Region['Encounter Side Quest SmallTextArea'] = '';
Region['Enemy'] = '';
Region['Event'] = '';
Region['Full Art Landscape'] = '';
Region['Full Art Portrait'] = '';
Region['Hero'] = '';
Region['Hero Promo'] = '';
Region['Location'] = '';
Region['Nightmare'] = '';
Region['Objective'] = '';
Region['Objective Ally'] = '';
Region['Objective Hero'] = '';
Region['Objective Location'] = '';
Region['Player Objective'] = '';
Region['Player Side Quest'] = '';
Region['Presentation'] = '';
Region['Quest'] = '';
Region['Rules'] = '';
Region['Ship Enemy'] = '';
Region['Ship Objective'] = '';
Region['Treachery'] = '';
Region['Treasure'] = '';
*/

var gameNamePortraitRegion = {};
gameNamePortraitRegion['Presentation'] = '50,33,313,140';

var namePortraitRegion = {};
namePortraitRegion['Presentation'] = '50,420,313,113';

var pageInRegion = {};
pageInRegion['Presentation'] = '48,488,317,15';
pageInRegion['Rules'] = '48,488,317,15';

var sideRegion = {};
sideRegion['Contract'] = '0,279,413,17';

var encounterSet1PortraitRegion = {};
encounterSet1PortraitRegion['Quest'] = '450,213,20,20';

var encounterSet2PortraitRegion = {};
encounterSet2PortraitRegion['Quest'] = '426,213,20,20';

var encounterSet3PortraitRegion = {};
encounterSet3PortraitRegion['Quest'] = '402,213,20,20';

var encounterSet4PortraitRegion = {};
encounterSet4PortraitRegion['Quest'] = '378,213,20,20';

var encounterSet5PortraitRegion = {};
encounterSet5PortraitRegion['Quest'] = '354,213,20,20';

var asteriskRegion = {};
asteriskRegion['Ally'] = '372,526,8,8';
asteriskRegion['Attachment'] = '374,526,8,8';
asteriskRegion['Campaign'] = '374,526,8,8';
asteriskRegion['Cave'] = '530,376,8,8';
asteriskRegion['Contract'] = '374,526,8,8';
asteriskRegion['Encounter Side Quest'] = '532,376,8,8';
asteriskRegion['Encounter Side Quest SmallTextArea'] = '532,376,8,8';
asteriskRegion['Enemy'] = '374,526,8,8';
asteriskRegion['Event'] = '374,526,8,8';
asteriskRegion['Hero'] = '374,526,8,8';
asteriskRegion['Hero Promo'] = '352,526,8,8';
asteriskRegion['Location'] = '374,526,8,8';
asteriskRegion['Nightmare'] = '380,526,8,8';
asteriskRegion['Objective'] = '364,526,8,8';
asteriskRegion['Objective Ally'] = '364,526,8,8';
asteriskRegion['Objective Hero'] = '364,526,8,8';
asteriskRegion['Objective Location'] = '364,526,8,8';
asteriskRegion['Player Objective'] = '364,526,8,8';
asteriskRegion['Player Side Quest'] = '530,376,8,8';
asteriskRegion['Quest'] = '530,376,8,8';
asteriskRegion['Region'] = '530,376,8,8';
asteriskRegion['Ship Enemy'] = '374,526,8,8';
asteriskRegion['Ship Objective'] = '364,526,8,8';
asteriskRegion['Treachery'] = '374,526,8,8';
asteriskRegion['Treasure'] = '378,526,8,8';

var collectionInfoRegion = {};
collectionInfoRegion['Ally'] = '350,527,20,15';
collectionInfoRegion['Attachment'] = '350,527,20,15';
collectionInfoRegion['Campaign'] = '350,527,20,15';
collectionInfoRegion['Cave'] = '504,375,20,15';
collectionInfoRegion['Contract'] = '350,527,20,15';
collectionInfoRegion['Encounter Side Quest'] = '419,375,20,15';
collectionInfoRegion['Encounter Side Quest SmallTextArea'] = '419,375,20,15';
collectionInfoRegion['Enemy'] = '350,527,20,15';
collectionInfoRegion['Event'] = '350,527,20,15';
collectionInfoRegion['Hero'] = '350,527,20,15';
collectionInfoRegion['Hero Promo'] = '326,510,20,12';
collectionInfoRegion['Location'] = '350,527,20,15';
collectionInfoRegion['Nightmare'] = '350,527,20,15';
collectionInfoRegion['Objective'] = '350,527,20,15';
collectionInfoRegion['Objective Ally'] = '350,527,20,15';
collectionInfoRegion['Objective Hero'] = '350,527,20,15';
collectionInfoRegion['Objective Location'] = '350,527,20,15';
collectionInfoRegion['Player Objective'] = '350,527,20,15';
collectionInfoRegion['Player Side Quest'] = '419,375,20,15';
collectionInfoRegion['Presentation'] = '350,527,20,15';
collectionInfoRegion['Quest'] = '419,375,20,15';
collectionInfoRegion['Region'] = '504,375,20,15';
collectionInfoRegion['Rules'] = '350,527,20,15';
collectionInfoRegion['Ship Enemy'] = '350,527,20,15';
collectionInfoRegion['Ship Objective'] = '350,527,20,15';
collectionInfoRegion['Treachery'] = '350,527,20,15';
collectionInfoRegion['Treasure'] = '350,527,20,15';

var collectionNumberRegion = {};
collectionNumberRegion['Ally'] = '334,527,18,15';
collectionNumberRegion['Attachment'] = '334,527,18,15';
collectionNumberRegion['Campaign'] = '334,527,18,15';
collectionNumberRegion['Cave'] = '488,375,18,15';
collectionNumberRegion['Contract'] = '334,527,18,15';
collectionNumberRegion['Encounter Side Quest'] = '403,375,18,15';
collectionNumberRegion['Encounter Side Quest SmallTextArea'] = '403,375,18,15';
collectionNumberRegion['Enemy'] = '334,527,18,15';
collectionNumberRegion['Event'] = '334,527,18,15';
collectionNumberRegion['Full Art Landscape'] = '334,527,18,15';
collectionNumberRegion['Full Art Portrait'] = '334,527,18,15';
collectionNumberRegion['Hero'] = '334,527,18,15';
collectionNumberRegion['Hero Promo'] = '314,510,18,12';
collectionNumberRegion['Location'] = '334,527,18,15';
collectionNumberRegion['Nightmare'] = '334,527,18,15';
collectionNumberRegion['Objective'] = '334,527,18,15';
collectionNumberRegion['Objective Ally'] = '334,527,18,15';
collectionNumberRegion['Objective Hero'] = '334,527,18,15';
collectionNumberRegion['Objective Location'] = '334,527,18,15';
collectionNumberRegion['Player Objective'] = '334,527,18,15';
collectionNumberRegion['Player Side Quest'] = '403,375,18,15';
collectionNumberRegion['Quest'] = '403,375,18,15';
collectionNumberRegion['Region'] = '488,375,18,15';
collectionNumberRegion['Ship Enemy'] = '334,527,18,15';
collectionNumberRegion['Ship Objective'] = '334,527,18,15';
collectionNumberRegion['Treachery'] = '334,527,18,15';
collectionNumberRegion['Treasure'] = '334,527,18,15';

var collectionPortraitRegion = {};
collectionPortraitRegion['Ally'] = '322,528,12,12';
collectionPortraitRegion['Attachment'] = '322,528,12,12';
collectionPortraitRegion['Campaign'] = '322,528,12,12';
collectionPortraitRegion['Cave'] = '476,376,12,12';
collectionPortraitRegion['Contract'] = '322,528,12,12';
collectionPortraitRegion['Encounter Side Quest'] = '391,376,12,12';
collectionPortraitRegion['Encounter Side Quest SmallTextArea'] = '391,376,12,12';
collectionPortraitRegion['Enemy'] = '322,528,12,12';
collectionPortraitRegion['Event'] = '322,528,12,12';
collectionPortraitRegion['Hero'] = '322,528,12,12';
collectionPortraitRegion['Hero Promo'] = '305,511,9,9';
collectionPortraitRegion['Location'] = '322,528,12,12';
collectionPortraitRegion['Nightmare'] = '322,528,12,12';
collectionPortraitRegion['Objective'] = '322,528,12,12';
collectionPortraitRegion['Objective Ally'] = '322,528,12,12';
collectionPortraitRegion['Objective Hero'] = '322,528,12,12';
collectionPortraitRegion['Objective Location'] = '322,528,12,12';
collectionPortraitRegion['Player Objective'] = '322,528,12,12';
collectionPortraitRegion['Player Side Quest'] = '391,376,12,12';
collectionPortraitRegion['Presentation'] = '185,383,43,43';
collectionPortraitRegion['Quest'] = '391,376,12,12';
collectionPortraitRegion['Region'] = '476,376,12,12';
collectionPortraitRegion['Ship Enemy'] = '322,528,12,12';
collectionPortraitRegion['Ship Objective'] = '322,528,12,12';
collectionPortraitRegion['Treachery'] = '322,528,12,12';
collectionPortraitRegion['Treasure'] = '322,528,12,12';

var typeRegion = {};
typeRegion['Ally'] = '136,504,141,20';
typeRegion['Attachment'] = '136,504,141,20';
typeRegion['Campaign'] = '136,504,141,20';
typeRegion['Contract'] = '136,504,141,20';
typeRegion['Enemy'] = '136,504,141,20';
typeRegion['Event'] = '136,504,141,20';
typeRegion['Hero'] = '136,504,141,20';
typeRegion['Hero Promo'] = '285,448,32,15';
typeRegion['Location'] = '136,504,141,20';
typeRegion['Nightmare'] = '136,504,141,20';
typeRegion['Objective'] = '136,504,141,20';
typeRegion['Objective Ally'] = '136,504,141,20';
typeRegion['Objective Hero'] = '136,504,141,20';
typeRegion['Objective Location'] = '136,504,141,20';
typeRegion['Player Objective'] = '136,504,141,20';
typeRegion['Ship Enemy'] = '136,504,141,20';
typeRegion['Ship Objective'] = '136,504,141,20';
typeRegion['Treachery'] = '136,504,141,20';
typeRegion['Treasure'] = '136,504,141,20';

var copyrightRegion = {};
copyrightRegion['Ally'] = '158,527,124,15';
copyrightRegion['Attachment'] = '158,527,124,15';
copyrightRegion['Campaign'] = '158,527,124,15';
copyrightRegion['Cave'] = '345,375,124,15';
copyrightRegion['Contract'] = '158,527,124,15';
copyrightRegion['Encounter Side Quest'] = '225,375,124,15';
copyrightRegion['Encounter Side Quest SmallTextArea'] = '225,375,124,15';
copyrightRegion['Enemy'] = '158,527,124,15';
copyrightRegion['Event'] = '158,527,124,15';
copyrightRegion['Full Art Landscape'] = '34,364,124,15';
copyrightRegion['Full Art Portrait'] = '34,514,124,15';
copyrightRegion['Hero'] = '158,527,124,15';
copyrightRegion['Hero Promo'] = '161,510,124,12';
copyrightRegion['Location'] = '158,527,124,15';
copyrightRegion['Nightmare'] = '158,527,124,15';
copyrightRegion['Objective'] = '158,527,124,15';
copyrightRegion['Objective Ally'] = '158,527,124,15';
copyrightRegion['Objective Hero'] = '158,527,124,15';
copyrightRegion['Objective Location'] = '158,527,124,15';
copyrightRegion['Player Objective'] = '158,527,124,15';
copyrightRegion['Player Side Quest'] = '225,375,124,15';
copyrightRegion['Quest'] = '225,375,124,15';
copyrightRegion['Region'] = '276,375,124,15';
copyrightRegion['Ship Enemy'] = '158,527,124,15';
copyrightRegion['Ship Objective'] = '158,527,124,15';
copyrightRegion['Treachery'] = '158,527,124,15';
copyrightRegion['Treasure'] = '158,527,124,15';

var artistRegion = {};
artistRegion['Ally'] = '63,527,100,15';
artistRegion['Attachment'] = '63,527,100,15';
artistRegion['Campaign'] = '63,527,100,15';
artistRegion['Cave'] = '48,375,100,15';
artistRegion['Contract'] = '63,527,100,15';
artistRegion['Encounter Side Quest'] = '130,375,100,15';
artistRegion['Encounter Side Quest SmallTextArea'] = '130,375,100,15';
artistRegion['Enemy'] = '63,527,100,15';
artistRegion['Event'] = '63,527,100,15';
artistRegion['Full Art Landscape'] = '390,364,140,15';
artistRegion['Full Art Portrait'] = '240,514,140,15';
artistRegion['Hero'] = '63,527,100,15';
artistRegion['Hero Promo'] = '79,510,88,12';
artistRegion['Location'] = '63,527,100,15';
artistRegion['Nightmare'] = '63,527,100,15';
artistRegion['Objective'] = '63,527,100,15';
artistRegion['Objective Ally'] = '63,527,100,15';
artistRegion['Objective Hero'] = '63,527,100,15';
artistRegion['Objective Location'] = '63,527,100,15';
artistRegion['Player Objective'] = '63,527,100,15';
artistRegion['Player Side Quest'] = '130,375,100,15';
artistRegion['Quest'] = '130,375,100,15';
artistRegion['Region'] = '68,375,100,15';
artistRegion['Ship Enemy'] = '63,527,100,15';
artistRegion['Ship Objective'] = '63,527,100,15';
artistRegion['Treachery'] = '63,527,100,15';
artistRegion['Treasure'] = '63,527,100,15';

var portraitRegion = {};
portraitRegion['Ally'] = '87,0,326,330';
portraitRegion['Attachment'] = '40,50,333,280';
portraitRegion['Campaign'] = '0,0,413,245';
portraitRegion['Cave'] = '0,0,563,413';
portraitRegion['Contract'] = '0,0,413,315';
portraitRegion['Encounter Side Quest'] = '0,0,563,413';
portraitRegion['Encounter Side Quest SmallTextArea'] = '0,0,563,413';
portraitRegion['Enemy'] = '87,0,326,330';
portraitRegion['Event'] = '60,0,353,330';
portraitRegion['Full Art Landscape'] = '0,0,563,413';
portraitRegion['Full Art Portrait'] = '0,0,413,563';
portraitRegion['Hero'] = '87,0,326,330';
portraitRegion['Hero Promo'] = '0,0,413,563';
portraitRegion['Location'] = '0,60,413,268';
portraitRegion['Nightmare'] = '0,77,413,245';
portraitRegion['Objective'] = '0,69,413,300';
portraitRegion['Objective Ally'] = '78,81,335,268';
portraitRegion['Objective Hero'] = '78,81,335,268';
portraitRegion['Objective Location'] = '0,69,413,300';
portraitRegion['Player Objective'] = '0,69,413,300';
portraitRegion['Player Side Quest'] = '0,0,563,413';
portraitRegion['Presentation'] = '0,140,413,285';
portraitRegion['Quest'] = '0,0,563,413';
portraitRegion['Region'] = '0,0,563,413';
portraitRegion['Ship Enemy'] = '87,0,326,330';
portraitRegion['Ship Objective'] = '78,81,335,268';
portraitRegion['Treachery'] = '60,0,353,330';
portraitRegion['Treasure'] = '0,61,413,265';

var portraitBackRegion = {};
portraitBackRegion['Contract'] = '0,0,413,315';
portraitBackRegion['Quest'] = '0,0,563,413';

var bodyRegion = {};
bodyRegion['Ally'] = '57,378,299,114';
bodyRegion['Attachment'] = '57,347,299,144';
bodyRegion['Enemy'] = '57,377,299,114';
bodyRegion['Event'] = '65,351,283,140';
bodyRegion['Hero'] = '57,377,299,114';
bodyRegion['Hero Promo'] = '78,467,259,45';
bodyRegion['Location'] = '56,346,301,142';
bodyRegion['Objective'] = '65,355,283,137';
bodyRegion['Objective Ally'] = '65,355,283,137';
bodyRegion['Objective Hero'] = '65,355,283,137';
bodyRegion['Objective Location'] = '65,355,283,137';
bodyRegion['Player Objective'] = '65,355,283,137';
bodyRegion['Ship Enemy'] = '57,377,299,114';
bodyRegion['Ship Objective'] = '65,355,283,137';
bodyRegion['Treachery'] = '65,356,283,135';
bodyRegion['Treasure'] = '57,347,299,144';

bodyRegion['Cave'] = '50,303,171,60';
bodyRegion['Encounter Side Quest'] = '51,269,461,94';
bodyRegion['Encounter Side Quest SmallTextArea'] = '51,324,461,38';
bodyRegion['Player Side Quest'] = '51,271,461,94';

var traitRegion = {};
traitRegion['Ally'] = '57,358,299,20';
traitRegion['Attachment'] = '85,327,243,20';
traitRegion['Enemy'] = '57,357,299,20';
traitRegion['Event'] = '78,331,257,20';
traitRegion['Hero'] = '57,357,299,20';
traitRegion['Hero Promo'] = '93,449,160,14';
traitRegion['Location'] = '56,326,301,20';
traitRegion['Objective'] = '65,335,283,20';
traitRegion['Objective Ally'] = '65,335,283,20';
traitRegion['Objective Hero'] = '65,335,283,20';
traitRegion['Objective Location'] = '65,335,283,20';
traitRegion['Player Objective'] = '65,335,283,20';
traitRegion['Ship Enemy'] = '57,357,299,20';
traitRegion['Ship Objective'] = '65,335,283,20';
traitRegion['Treachery'] = '65,336,283,20';
traitRegion['Treasure'] = '85,327,243,20';

traitRegion['Cave'] = '50,283,171,20';
traitRegion['Encounter Side Quest'] = '51,249,461,20';
traitRegion['Encounter Side Quest SmallTextArea'] = '51,304,461,20';
traitRegion['Player Side Quest'] = '51,251,461,20';
traitRegion['Region'] = '279,350,237,25';

var bodyNoTraitRegion = {};
bodyNoTraitRegion['Campaign'] = '56,277,301,211';
bodyNoTraitRegion['Contract'] = '65,313,283,176';
bodyNoTraitRegion['Nightmare'] = '54,325,305,192';
bodyNoTraitRegion['Presentation'] = '48,73,317,418';
bodyNoTraitRegion['Rules'] = '48,73,317,418';
bodyNoTraitRegion['Quest'] = '51,249,461,114';

bodyNoTraitRegion['Cave'] = '50,283,171,80';
bodyNoTraitRegion['Encounter Side Quest'] = '51,249,461,114';
bodyNoTraitRegion['Encounter Side Quest SmallTextArea'] = '51,304,461,58';
bodyNoTraitRegion['Player Side Quest'] = '51,251,461,114';

var bodyRightNoTraitRegion = {};
bodyRightNoTraitRegion['Cave'] = '347,283,171,80';

var bodyBackRegion = {};
bodyBackRegion['Campaign'] = '64,60,285,443';
bodyBackRegion['Contract'] = '65,313,283,176';
bodyBackRegion['Nightmare'] = '54,55,305,439';
bodyBackRegion['Quest'] = '51,249,461,114';
bodyBackRegion['Rules'] = '48,73,317,418';

var nameRegion = {};
nameRegion['Ally'] = '100,329,213,25';
nameRegion['Attachment'] = '132,38,183,25';
nameRegion['Campaign'] = '108,43,197,25';
nameRegion['Cave'] = '80,43,160,25';
nameRegion['Contract'] = '84,245,245,29';
nameRegion['Encounter Side Quest'] = '100,42,363,29';
nameRegion['Encounter Side Quest SmallTextArea'] = '100,42,363,29';
nameRegion['Enemy'] = '94,327,225,25';
nameRegion['Event'] = '57,86,26,178';
nameRegion['Hero'] = '100,327,213,25';
nameRegion['Hero Promo'] = '103,418,206,25';
nameRegion['Location'] = '108,43,197,25';
nameRegion['Nightmare'] = '95,40,225,34';
nameRegion['Objective'] = '75,48,263,29';
nameRegion['Objective Ally'] = '75,48,263,29';
nameRegion['Objective Hero'] = '75,48,263,29';
nameRegion['Objective Location'] = '75,48,263,29';
nameRegion['Player Objective'] = '127,48,211,29';
nameRegion['Player Side Quest'] = '144,44,368,29';
nameRegion['Quest'] = '144,44,368,29';
nameRegion['Region'] = '80,349,160,25';
nameRegion['Ship Enemy'] = '94,327,225,25';
nameRegion['Ship Objective'] = '75,48,263,29';
nameRegion['Treachery'] = '55,108,26,164';
nameRegion['Treasure'] = '132,45,183,25';

var nameUniqueRegion = {};
nameUniqueRegion['Ally'] = '100,326,213,25';
nameUniqueRegion['Attachment'] = '132,36,183,25';
nameUniqueRegion['Cave'] = '80,40,160,25';
nameUniqueRegion['Encounter Side Quest'] = '100,39,363,29';
nameUniqueRegion['Encounter Side Quest SmallTextArea'] = '100,39,363,29';
nameUniqueRegion['Enemy'] = '94,325,225,25';
nameUniqueRegion['Hero'] = '100,325,213,25';
nameUniqueRegion['Hero Promo'] = '103,416,206,25';
nameUniqueRegion['Location'] = '108,40,197,25';
nameUniqueRegion['Objective'] = '75,45,263,29';
nameUniqueRegion['Objective Ally'] = '75,45,263,29';
nameUniqueRegion['Objective Hero'] = '75,45,263,29';
nameUniqueRegion['Objective Location'] = '75,45,263,29';
nameUniqueRegion['Player Objective'] = '127,45,211,29';
nameUniqueRegion['Region'] = '80,346,160,25';
nameUniqueRegion['Ship Enemy'] = '94,325,225,25';
nameUniqueRegion['Ship Objective'] = '75,45,263,29';
nameUniqueRegion['Treachery'] = '55,108,26,164';
nameUniqueRegion['Treasure'] = '132,43,183,25';

var subtypeRegion = {};
subtypeRegion['Attachment'] = '146,301,124,20';
subtypeRegion['Enemy'] = '146,302,124,20';
subtypeRegion['Event'] = '146,301,124,20';
subtypeRegion['Objective'] = '146,309,124,20';
subtypeRegion['Objective Ally'] = '146,309,124,20';
subtypeRegion['Objective Hero'] = '146,309,124,20';
subtypeRegion['Objective Location'] = '146,309,124,20';
subtypeRegion['Ship Enemy'] = '146,302,124,20';
subtypeRegion['Ship Objective'] = '146,309,124,20';
subtypeRegion['Treachery'] = '146,305,124,20';

var hitPointsRegion = {};
hitPointsRegion['Ally'] = '66,269,58,40';
hitPointsRegion['Enemy'] = '64,269,58,40';
hitPointsRegion['Hero'] = '64,269,58,40';
hitPointsRegion['Hero Promo'] = '46,408,58,40';
hitPointsRegion['Objective Ally'] = '61,272,58,40';
hitPointsRegion['Objective Hero'] = '61,272,58,40';
hitPointsRegion['Ship Enemy'] = '64,269,58,40';
hitPointsRegion['Ship Objective'] = '61,272,58,40';

var engagementRegion = {};
engagementRegion['Enemy'] = '76,48,36,25';
engagementRegion['Ship Enemy'] = '76,48,36,25';

var attackRegion = {};
attackRegion['Ally'] = '70,157,26,16';
attackRegion['Enemy'] = '68,156,26,16';
attackRegion['Hero'] = '68,157,26,16';
attackRegion['Hero Promo'] = '42,128,26,16';
attackRegion['Objective Ally'] = '65,159,26,16';
attackRegion['Objective Hero'] = '65,159,26,16';
attackRegion['Ship Enemy'] = '68,156,26,16';
attackRegion['Ship Objective'] = '65,159,26,16';

var defenseRegion = {};
defenseRegion['Ally'] = '70,200,26,16';
defenseRegion['Enemy'] = '68,199,26,16';
defenseRegion['Hero'] = '68,200,26,16';
defenseRegion['Hero Promo'] = '42,166,26,16';
defenseRegion['Objective Ally'] = '65,203,26,16';
defenseRegion['Objective Hero'] = '65,203,26,16';
defenseRegion['Ship Enemy'] = '68,199,26,16';
defenseRegion['Ship Objective'] = '65,203,26,16';

var willpowerRegion = {};
willpowerRegion['Ally'] = '70,117,26,16';
willpowerRegion['Hero'] = '68,117,26,16';
willpowerRegion['Hero Promo'] = '42,94,26,16';
willpowerRegion['Objective Ally'] = '65,113,26,16';
willpowerRegion['Objective Hero'] = '65,113,26,16';
willpowerRegion['Ship Objective'] = '65,113,26,16';

var threatRegion = {};
threatRegion['Enemy'] = '68,115,26,16';
threatRegion['Location'] = '54,92,26,16';
threatRegion['Ship Enemy'] = '68,115,26,16';

var threatCostRegion = {};
threatCostRegion['Hero'] = '75,50,36,25';
threatCostRegion['Hero Promo'] = '50,48,33,23';

var progressRegion = {};
progressRegion['Encounter Side Quest'] = '52,202,35,24';
progressRegion['Encounter Side Quest SmallTextArea'] = '52,257,35,24';
progressRegion['Location'] = '56,283,35,24';
progressRegion['Objective Location'] = '56,291,35,24';
progressRegion['Quest'] = '55,202,35,24';
progressRegion['Player Side Quest'] = '55,202,35,24';

var adventureRegion = {};
adventureRegion['Objective'] = '67,83,276,15';
adventureRegion['Objective Ally'] = '67,83,276,15';
adventureRegion['Objective Hero'] = '67,83,276,15';
adventureRegion['Objective Location'] = '67,83,276,15';
adventureRegion['Quest'] = '190,78,275,15';
adventureRegion['Ship Objective'] = '67,83,276,15';

var cycleRegion = {};
cycleRegion['Campaign'] = '68,243,274,32';

var resourceCostRegion = {};
resourceCostRegion['Ally'] = '67,41,56,37';
resourceCostRegion['Attachment'] = '37,44,56,37';
resourceCostRegion['Event'] = '37,38,56,37';
resourceCostRegion['Player Objective'] = '38,43,56,37';
resourceCostRegion['Player Side Quest'] = '43,44,56,37';
resourceCostRegion['Treasure'] = '45,61,44,30';

var difficultyRegion = {};
difficultyRegion['Encounter Side Quest'] = '0,0,563,413';
difficultyRegion['Encounter Side Quest SmallTextArea'] = '0,55,563,413';
difficultyRegion['Enemy'] = '0,0,413,563';
difficultyRegion['Location'] = '0,0,413,563';
difficultyRegion['Objective'] = '0,0,413,563';
difficultyRegion['Objective Ally'] = '0,0,413,563';
difficultyRegion['Objective Hero'] = '0,0,413,563';
difficultyRegion['Objective Location'] = '0,0,413,563';
difficultyRegion['Ship Enemy'] = '0,0,413,563';
difficultyRegion['Ship Objective'] = '0,0,413,563';
difficultyRegion['Treachery'] = '0,0,413,563';

var encounterPortraitRegion = {};
encounterPortraitRegion['Campaign'] = '319,190,43,43';
encounterPortraitRegion['Cave'] = '37,35,35,35';
encounterPortraitRegion['Encounter Side Quest'] = '478,186,43,43';
encounterPortraitRegion['Encounter Side Quest SmallTextArea'] = '478,241,43,43';
encounterPortraitRegion['Enemy'] = '321,266,43,43';
encounterPortraitRegion['Location'] = '319,265,43,43';
encounterPortraitRegion['Nightmare'] = '322,263,43,43';
encounterPortraitRegion['Objective'] = '315,269,43,43';
encounterPortraitRegion['Objective Ally'] = '315,269,43,43';
encounterPortraitRegion['Objective Hero'] = '315,269,43,43';
encounterPortraitRegion['Objective Location'] = '315,269,43,43';
encounterPortraitRegion['Quest'] = '474,185,43,43';
encounterPortraitRegion['Region'] = '37,341,35,35';
encounterPortraitRegion['Ship Enemy'] = '321,266,43,43';
encounterPortraitRegion['Ship Objective'] = '315,269,43,43';
encounterPortraitRegion['Treachery'] = '320,269,43,43';
encounterPortraitRegion['Treasure'] = '327,478,43,43';

var encounterNumberRegion = {};
encounterNumberRegion['Cave'] = '41,70,26,10';
encounterNumberRegion['Encounter Side Quest'] = '486,230,26,10';
encounterNumberRegion['Encounter Side Quest SmallTextArea'] = '486,285,26,10';
encounterNumberRegion['Enemy'] = '328,313,26,10';
encounterNumberRegion['Location'] = '327,314,26,10';
encounterNumberRegion['Objective'] = '322,316,26,10';
encounterNumberRegion['Objective Ally'] = '322,316,26,10';
encounterNumberRegion['Objective Hero'] = '322,316,26,10';
encounterNumberRegion['Objective Location'] = '322,316,26,10';
encounterNumberRegion['Region'] = '41,332,26,10';
encounterNumberRegion['Ship Enemy'] = '328,313,26,10';
encounterNumberRegion['Ship Objective'] = '322,316,26,10';
encounterNumberRegion['Treachery'] = '328,317,26,10';

var optionRightDecorationRegion = {};
optionRightDecorationRegion['Ally'] = '298,503,72,18';
optionRightDecorationRegion['Attachment'] = '300,503,72,18';
optionRightDecorationRegion['Campaign'] = '301,503,72,18';
optionRightDecorationRegion['Encounter Side Quest'] = '452,347,72,18';
optionRightDecorationRegion['Encounter Side Quest SmallTextArea'] = '452,347,72,18';
optionRightDecorationRegion['Enemy'] = '301,503,72,18';
optionRightDecorationRegion['Event'] = '298,503,72,18';
optionRightDecorationRegion['Hero'] = '298,502,72,18';
optionRightDecorationRegion['Hero Promo'] = '282,495,72,18';
optionRightDecorationRegion['Location'] = '301,503,72,18';
optionRightDecorationRegion['Nightmare'] = '299,503,72,18';
optionRightDecorationRegion['Objective'] = '290,502,72,18';
optionRightDecorationRegion['Objective Ally'] = '290,502,72,18';
optionRightDecorationRegion['Objective Hero'] = '290,502,72,18';
optionRightDecorationRegion['Objective Location'] = '290,502,72,18';
optionRightDecorationRegion['Player Objective'] = '290,502,72,18';
optionRightDecorationRegion['Player Side Quest'] = '451,349,72,18';
optionRightDecorationRegion['Quest'] = '450,350,72,18';
optionRightDecorationRegion['Ship Enemy'] = '301,503,72,18';
optionRightDecorationRegion['Ship Objective'] = '290,502,72,18';
optionRightDecorationRegion['Treachery'] = '301,503,72,18';
optionRightDecorationRegion['Treasure'] = '253,477,72,18';

var optionRightRegion = {};
optionRightRegion['Ally'] = '305,504,59,20';
optionRightRegion['Attachment'] = '307,504,59,20';
optionRightRegion['Campaign'] = '308,504,59,20';
optionRightRegion['Encounter Side Quest'] = '459,348,59,20';
optionRightRegion['Encounter Side Quest SmallTextArea'] = '459,348,59,20';
optionRightRegion['Enemy'] = '308,504,59,20';
optionRightRegion['Event'] = '305,504,59,20';
optionRightRegion['Hero'] = '305,503,59,20';
optionRightRegion['Hero Promo'] = '289,496,59,20';
optionRightRegion['Location'] = '308,504,59,20';
optionRightRegion['Nightmare'] = '306,507,59,20';
optionRightRegion['Objective'] = '297,503,59,20';
optionRightRegion['Objective Ally'] = '297,503,59,20';
optionRightRegion['Objective Hero'] = '297,503,59,20';
optionRightRegion['Objective Location'] = '297,503,59,20';
optionRightRegion['Player Objective'] = '297,503,59,20';
optionRightRegion['Player Side Quest'] = '458,350,59,20';
optionRightRegion['Quest'] = '457,351,59,20';
optionRightRegion['Ship Enemy'] = '308,504,59,20';
optionRightRegion['Ship Objective'] = '297,503,59,20';
optionRightRegion['Treachery'] = '308,504,59,20';
optionRightRegion['Treasure'] = '260,478,59,20';

var optionSpecialRegion = {};
optionSpecialRegion['Enemy'] = '55,494,24,24';
optionSpecialRegion['Location'] = '55,494,24,24';
optionSpecialRegion['Objective'] = '75,494,24,24';
optionSpecialRegion['Objective Ally'] = '75,494,24,24';
optionSpecialRegion['Objective Location'] = '75,494,24,24';
optionSpecialRegion['Ship Enemy'] = '55,494,24,24';
optionSpecialRegion['Ship Objective'] = '75,494,24,24';
optionSpecialRegion['Treachery'] = '55,494,24,24';

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

var bodyPointSize = {};
bodyPointSize['Ally'] = 7.5;
bodyPointSize['Attachment'] = 7.5;
bodyPointSize['Campaign'] = 7.5;
bodyPointSize['Cave'] = 7;
bodyPointSize['Contract'] = 7.5;
bodyPointSize['Encounter Side Quest'] = 7;
bodyPointSize['Encounter Side Quest SmallTextArea'] = 7;
bodyPointSize['Enemy'] = 7.5;
bodyPointSize['Event'] = 7.5;
bodyPointSize['Hero'] = 7.5;
bodyPointSize['Hero Promo'] = 5.9;
bodyPointSize['Location'] = 7.5;
bodyPointSize['Nightmare'] = 7.5;
bodyPointSize['Objective'] = 7.5;
bodyPointSize['Objective Ally'] = 7.5;
bodyPointSize['Objective Hero'] = 7.5;
bodyPointSize['Objective Location'] = 7.5;
bodyPointSize['Player Objective'] = 7.5;
bodyPointSize['Player Side Quest'] = 7;
bodyPointSize['Presentation'] = 7.5;
bodyPointSize['Quest'] = 7;
bodyPointSize['Rules'] = 7.5;
bodyPointSize['Ship Enemy'] = 7.5;
bodyPointSize['Ship Objective'] = 7.5;
bodyPointSize['Treachery'] = 7.5;
bodyPointSize['Treasure'] = 7.5;

var flavourPointSize = {};
flavourPointSize['Ally'] = 6.25;
flavourPointSize['Attachment'] = 6.25;
flavourPointSize['Campaign'] = 6.25;
flavourPointSize['Cave'] = 7;
flavourPointSize['Contract'] = 6.25;
flavourPointSize['Encounter Side Quest'] = 7;
flavourPointSize['Encounter Side Quest SmallTextArea'] = 7;
flavourPointSize['Enemy'] = 6.25;
flavourPointSize['Event'] = 6.25;
flavourPointSize['Hero'] = 6.25;
flavourPointSize['Hero Promo'] = 4.9;
flavourPointSize['Location'] = 6.25;
flavourPointSize['Nightmare'] = 6.25;
flavourPointSize['Objective'] = 6.25;
flavourPointSize['Objective Ally'] = 6.25;
flavourPointSize['Objective Hero'] = 6.25;
flavourPointSize['Objective Location'] = 6.25;
flavourPointSize['Player Objective'] = 6.25;
flavourPointSize['Player Side Quest'] = 7;
flavourPointSize['Quest'] = 7;
flavourPointSize['Ship Enemy'] = 6.25;
flavourPointSize['Ship Objective'] = 6.25;
flavourPointSize['Treachery'] = 6.25;
flavourPointSize['Treasure'] = 6.25;

var traitPointSize = {};
traitPointSize['Ally'] = 8.25;
traitPointSize['Attachment'] = 8.25;
traitPointSize['Cave'] = 7.75;
traitPointSize['Encounter Side Quest'] = 7.75;
traitPointSize['Encounter Side Quest SmallTextArea'] = 7.75;
traitPointSize['Enemy'] = 8.25;
traitPointSize['Event'] = 8.25;
traitPointSize['Hero'] = 8.25;
traitPointSize['Hero Promo'] = 6.5;
traitPointSize['Location'] = 8.25;
traitPointSize['Objective'] = 8.25;
traitPointSize['Objective Ally'] = 8.25;
traitPointSize['Objective Hero'] = 8.25;
traitPointSize['Objective Location'] = 8.25;
traitPointSize['Player Objective'] = 8.25;
traitPointSize['Player Side Quest'] = 7.75;
traitPointSize['Region'] = 7.75;
traitPointSize['Ship Enemy'] = 8.25;
traitPointSize['Ship Objective'] = 8.25;
traitPointSize['Treachery'] = 8.25;
traitPointSize['Treasure'] = 8.25;

var namePointSize = {};
namePointSize['Ally'] = 6.5;
namePointSize['Attachment'] = 6.5;
namePointSize['Campaign'] = 6.5;
namePointSize['Cave'] = 6.5;
namePointSize['Contract'] = 7.5;
namePointSize['Encounter Side Quest'] = 7.5;
namePointSize['Encounter Side Quest SmallTextArea'] = 7.5;
namePointSize['Enemy'] = 6.5;
namePointSize['Event'] = 6.5;
namePointSize['Hero'] = 6.5;
namePointSize['Hero Promo'] = 6.5;
namePointSize['Location'] = 6.5;
namePointSize['Nightmare'] = 6.5;
namePointSize['Objective'] = 7.5;
namePointSize['Objective Ally'] = 7.5;
namePointSize['Objective Hero'] = 7.5;
namePointSize['Objective Location'] = 7.5;
namePointSize['Player Objective'] = 7.5;
namePointSize['Player Side Quest'] = 7.5;
namePointSize['Quest'] = 7.5;
namePointSize['Region'] = 6.5;
namePointSize['Ship Enemy'] = 6.5;
namePointSize['Ship Objective'] = 7.5;
namePointSize['Treachery'] = 6.5;
namePointSize['Treasure'] = 6.5;

var bottomPointSize = {};
bottomPointSize['Hero Promo'] = 3.5;

var threatCostTint = {};
threatCostTint['Hero'] = '200.0,0.7,0.7';
threatCostTint['Hero Promo'] = '0.0,0.0,0.95';

var sphereBodyShape = {};
sphereBodyShape['Hero'] = '0,0,472,40,0';
sphereBodyShape['Hero Promo'] = '0,0,0,0,0';
sphereBodyShape['Treasure'] = '0,0,472,0,34';

var sphereOptionBodyShape = {};
sphereOptionBodyShape['Treasure'] = '0,0,472,0,104';

var optionBodyShape = {};
optionBodyShape['Encounter Side Quest'] = '0,0,348,0,62';
optionBodyShape['Encounter Side Quest SmallTextArea'] = '0,0,348,0,62';
optionBodyShape['Player Side Quest'] = '0,0,350,0,62';
optionBodyShape['Quest'] = '0,0,351,0,62';

var translate = {};
translate['Ally'] = {'English': 'Ally', 'French': 'Alli\u00e9', 'German': 'Verb\u00fcndeter', 'Spanish': 'Aliado', 'Polish': 'Sprzymierzeniec', 'Italian': 'Alleato',
	'Portuguese': 'Aliado'};
translate['Attachment'] = {'English': 'Attachment', 'French': 'Attachement', 'German': 'Verst\u00e4rkung', 'Spanish': 'Vinculada', 'Polish': 'Dodatek',
	'Italian': 'Aggregato', 'Portuguese': 'Acess\u00f3rio'};
translate['Boon'] = {'English': 'Boon', 'French': 'Avantage', 'German': 'Gunst', 'Spanish': 'Ayuda', 'Polish': '\u0141aska', 'Italian': 'Vantaggio',
	'Portuguese': 'D\u00e1diva'};
translate['Burden'] = {'English': 'Burden', 'French': 'Fardeau', 'German': 'B\u00fcrde', 'Spanish': 'Carga', 'Polish': 'Brzemi\u0119', 'Italian': 'Svantaggio',
	'Portuguese': 'Fardo'};
translate['Campaign'] = {'English': 'Campaign', 'French': 'Campagne', 'German': 'Kampagne', 'Spanish': 'Campa\u00f1a', 'Polish': 'Kampania', 'Italian': 'Campagna',
	'Portuguese': 'Campanha'};
translate['Cave'] = {'English': 'Side Quest', 'French': 'Qu\u00eate Annexe', 'German': 'Nebenabenteuer', 'Spanish': 'Misi\u00f3n Secundaria',
	'Polish': 'Poboczna wyprawa', 'Italian': 'Ricerca Secondaria', 'Portuguese': 'Miss\u00e3o Secund\u00e1ria'};
translate['Contract'] = {'English': 'Contract', 'French': 'Contrat', 'German': 'Abkommen', 'Spanish': 'Contrato', 'Polish': 'Kontrakt', 'Italian': 'Contratto',
	'Portuguese': 'Contrato'};
translate['Encounter Side Quest'] = {'English': 'Side Quest', 'French': 'Qu\u00eate Annexe', 'German': 'Nebenabenteuer', 'Spanish': 'Misi\u00f3n Secundaria',
	'Polish': 'Poboczna wyprawa', 'Italian': 'Ricerca Secondaria', 'Portuguese': 'Miss\u00e3o Secund\u00e1ria'};
translate['Encounter Side Quest SmallTextArea'] = {'English': 'Side Quest', 'French': 'Qu\u00eate Annexe', 'German': 'Nebenabenteuer', 'Spanish': 'Misi\u00f3n Secundaria',
	'Polish': 'Poboczna wyprawa', 'Italian': 'Ricerca Secondaria', 'Portuguese': 'Miss\u00e3o Secund\u00e1ria'};
translate['Enemy'] = {'English': 'Enemy', 'French': 'Ennemi', 'German': 'Gegner', 'Spanish': 'Enemigo', 'Polish': 'Wr\u00f3g', 'Italian': 'Nemico', 'Portuguese': 'Inimigo'};
translate['Event'] = {'English': 'Event', 'French': '\u00c9v\u00e9nement', 'German': 'Ereignis', 'Spanish': 'Evento', 'Polish': 'Wydarzenie', 'Italian': 'Evento',
	'Portuguese': 'Evento'};
translate['Hero'] = {'English': 'Hero', 'French': 'H\u00e9ros', 'German': 'Held', 'Spanish': 'H\u00e9roe', 'Polish': 'Bohater', 'Italian': 'Eroe',
	'Portuguese': 'Her\u00f3i'};
translate['Hero Promo'] = {'English': 'Hero', 'French': 'H\u00e9ros', 'German': 'Held', 'Spanish': 'H\u00e9roe', 'Polish': 'Bohater', 'Italian': 'Eroe',
	'Portuguese': 'Her\u00f3i'};
translate['Location'] = {'English': 'Location', 'French': 'Lieu', 'German': 'Ort', 'Spanish': 'Lugar', 'Polish': 'Obszar', 'Italian': 'Luogo',
	'Portuguese': 'Localiza\u00e7\u00e3o'};
translate['Nightmare'] = {'English': 'Setup', 'French': 'Pr\u00e9paration', 'German': 'Vorbereitung', 'Spanish': 'Preparaci\u00f3n', 'Polish': 'Przygotowanie',
	'Italian': 'Preparazione', 'Portuguese': 'Prepara\u00e7\u00e3o'};
translate['Objective'] = {'English': 'Objective', 'French': 'Objectif', 'German': 'Ziel', 'Spanish': 'Objetivo', 'Polish': 'Cel', 'Italian': 'Obiettivo',
	'Portuguese': 'Objetivo'};
translate['Objective Ally'] = {'English': 'Objective-Ally', 'French': 'Objectif-Alli\u00e9', 'German': 'Ziel-Verb\u00fcndeter', 'Spanish': 'Objetivo-Aliado',
	'Polish': 'Cel-Sprzymierzeniec', 'Italian': 'Obiettivo-Alleato', 'Portuguese': 'Objetivo-Aliado'};
translate['Objective Hero'] = {'English': 'Objective-Hero', 'French': 'Objectif-H\u00e9ros', 'German': 'Ziel-Held', 'Spanish': 'H\u00e9roe-Objetivo',
	'Polish': 'Cel-Bohater', 'Italian': 'Eroe-Obiettivo', 'Portuguese': 'Objetivo-Her\u00f3i'};
translate['Objective Location'] = {'English': 'Objective-Location', 'French': 'Objectif-Lieu', 'German': 'Ziel-Ort', 'Spanish': 'Lugar-Objetivo', 'Polish': 'Cel-Obszar',
	'Italian': 'Luogo-Obiettivo', 'Portuguese': 'Objetivo-Localiza\u00e7\u00e3o'};
translate['Player Objective'] = {'English': 'Objective', 'French': 'Objectif', 'German': 'Ziel', 'Spanish': 'Objetivo', 'Polish': 'Cel', 'Italian': 'Obiettivo',
	'Portuguese': 'Objetivo'};
translate['Player Side Quest'] = {'English': 'Side Quest', 'French': 'Qu\u00eate Annexe', 'German': 'Nebenabenteuer', 'Spanish': 'Misi\u00f3n Secundaria',
	'Polish': 'Poboczna wyprawa', 'Italian': 'Ricerca Secondaria', 'Portuguese': 'Miss\u00e3o Secund\u00e1ria'};
translate['Quest'] = {'English': 'Quest', 'French': 'Qu\u00eate', 'German': 'Abenteuer', 'Spanish': 'Misi\u00f3n', 'Polish': 'Wyprawa', 'Italian': 'Ricerca',
	'Portuguese': 'Miss\u00e3o'};
translate['Region'] = {'English': 'Side Quest', 'French': 'Qu\u00eate Annexe', 'German': 'Nebenabenteuer', 'Spanish': 'Misi\u00f3n Secundaria',
	'Polish': 'Poboczna wyprawa', 'Italian': 'Ricerca Secondaria', 'Portuguese': 'Miss\u00e3o Secund\u00e1ria'};
translate['Setup'] = {'English': 'Setup', 'French': 'Pr\u00e9paration', 'German': 'Vorbereitung', 'Spanish': 'Preparaci\u00f3n', 'Polish': 'Przygotowanie',
	'Italian': 'Preparazione', 'Portuguese': 'Prepara\u00e7\u00e3o'};
translate['Ship Enemy'] = {'English': 'Ship-Enemy', 'French': 'Navire-Ennemi', 'German': 'Schiff-Gegner', 'Spanish': 'Barco-Enemigo', 'Polish': 'Statek-Wr\u00f3g',
	'Italian': 'Nave-Nemico', 'Portuguese': 'Navio-Inimigo'};
translate['Ship Objective'] = {'English': 'Ship-Objective', 'French': 'Navire-Objectif', 'German': 'Schiff-Ziel', 'Spanish': 'Barco-Objetivo', 'Polish': 'Statek-Cel',
	'Italian': 'Nave-Obiettivo', 'Portuguese': 'Navio-Objetivo'};
translate['Treachery'] = {'English': 'Treachery', 'French': 'Tra\u00eetrise', 'German': 'Verrat', 'Spanish': 'Traici\u00f3n', 'Polish': 'Podst\u0119p',
	'Italian': 'Perfidia', 'Portuguese': 'Infort\u00fanio'};
translate['Treasure'] = {'English': 'Treasure', 'French': 'Tr\u00e9sor', 'German': 'Schatz', 'Spanish': 'Tesoro', 'Polish': 'Skarb', 'Italian': 'Tesoro',
	'Portuguese': 'Tesouro'};
translate['Encounter Keyword'] = {'English': 'Encounter', 'French': 'Rencontre', 'German': 'Begegnung', 'Spanish': 'Encuentro', 'Polish': 'Spotkanie',
	'Italian': 'Incontro', 'Portuguese': 'Encontro'};
translate['Illustrator'] = {'English': 'Illus.', 'French': 'Illus.', 'German': 'Illus.', 'Spanish': 'Ilus.', 'Polish': 'Illus.', 'Italian': 'Illus.',
	'Portuguese': 'Ilust.'};
translate['Unknown Artist'] = {'English': 'Unknown Artist', 'French': 'Artiste inconnu', 'German': 'Unbekannter K\u00fcnstler', 'Spanish': 'Artista desconocido',
	'Polish': 'Artysta nieznany', 'Italian': 'Artista sconosciuto', 'Portuguese': 'Artista Desconhecido'};
translate['Victory'] = {'English': 'Victory', 'French': 'Victoire', 'German': 'Sieg', 'Spanish': 'Victoria', 'Polish': 'Zwyci\u0119stwo', 'Italian': 'Vittoria',
	'Portuguese': 'Vit\u00f3ria'};
translate['Page'] = {'English': 'Page', 'French': 'Page', 'German': 'Seite', 'Spanish': 'P\u00e1gina', 'Polish': 'Strona', 'Italian': 'Pagina',
	'Portuguese': 'P\u00e1gina'};
translate['Side'] = {'English': 'Side', 'French': 'Face', 'German': 'Seite', 'Spanish': 'Lado', 'Polish': 'Strona', 'Italian': 'Lato', 'Portuguese': 'Lado'};
translate['Full Art Landscape'] = {'English': 'Full Art Landscape', 'French': 'Full Art Landscape', 'German': 'Full Art Landscape', 'Spanish': 'Full Art Landscape',
	'Polish': 'Full Art Landscape', 'Italian': 'Full Art Landscape', 'Portuguese': 'Full Art Landscape'};
translate['Full Art Portrait'] = {'English': 'Full Art Portrait', 'French': 'Full Art Portrait', 'German': 'Full Art Portrait', 'Spanish': 'Full Art Portrait',
	'Polish': 'Full Art Portrait', 'Italian': 'Full Art Portrait', 'Portuguese': 'Full Art Portrait'};
translate['Presentation'] = {'English': 'Presentation', 'French': 'Presentation', 'German': 'Presentation', 'Spanish': 'Presentation', 'Polish': 'Presentation',
	'Italian': 'Presentation', 'Portuguese': 'Presentation'};
translate['Rules'] = {'English': 'Rules', 'French': 'Rules', 'German': 'Rules', 'Spanish': 'Rules', 'Polish': 'Rules', 'Italian': 'Rules', 'Portuguese': 'Rules'};

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

		if (card['Type'] == 'Quest' && card['BQuest Points']) {
			card['Quest Points'] = card['BQuest Points'];
		}

		if (!card['Text']) {
			card['Text'] = ' ';
		}

		if ((doubleSideTypes.indexOf(card['Type'] + '') == -1) && card['BName'] && !card['BText']) {
			card['BText'] = ' ';
		}

		if (!card['Artist']) {
			card['Artist'] = 'Unknown Artist';
		}

		if ((doubleSideTypes.indexOf(card['Type'] + '') == -1) && card['BName'] && !card['BArtist']) {
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
			if ((doubleSideTypes.indexOf(card['Type'] + '') == -1) && card['BName']) {
				sides.push('back');
			}
			for (let idx = 0; idx < sides.length; idx++) {
				let side = sides[idx];
				let cardName, cardType, cardSphere, keywords, suffix, mapping, flags;
				if (side == 'front') {
					cardName = card['Name'];
					cardType = card['Type'] + '';
					cardSphere = card['Sphere'] + '';
					cardTrait = card['Traits'];

					flags = [];
					for (let idx_f = 0; idx_f < card['Flags'].length; idx_f++) {
						flags.push(card['Flags'][idx_f]);
					}

					if ((cardType == 'Hero') && (flags.indexOf('Promo') > -1)) {
						cardType = 'Hero Promo';
						cardSphere = 'Promo' + card['Sphere'];
						card['Sphere'] = cardSphere;
					}
					else if ((cardType == 'Encounter Side Quest') && (card['Sphere'] + '' == 'SmallTextArea')) {
						cardType = 'Encounter Side Quest SmallTextArea';
					}
					else if ((cardType == 'Encounter Side Quest') && (card['Sphere'] + '' == 'Cave')) {
						cardType = 'Cave';
					}
					else if ((cardType == 'Encounter Side Quest') && (card['Sphere'] + '' == 'Region')) {
						cardType = 'Region';
					}
					else if (cardType == 'Objective Hero') {
						cardSphere = 'Hero';
						card['Sphere'] = cardSphere;
					}
					else if (cardType == 'Objective Location') {
						cardSphere = 'Location';
						card['Sphere'] = cardSphere;
					}
					else if ((cardType == 'Ship Enemy') && (card['Sphere'] + '' == 'Nightmare')) {
						cardSphere = 'ShipNightmare';
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
						['OptionSpecial', 'Special Icon'],
						['Rules', 'Text'],
						['Shadow', 'Shadow'],
						['Flavour', 'Flavour'],
						['Story', 'Flavour'],
						['Artist', 'Artist'],
						['Adventure', 'Adventure'],
						['Cycle', 'Adventure'],
						['CollectionNumberCustom', 'Card Number'],
						['CollectionNumberCustomOverwrite', 'Printed Card Number'],
						['CollectionInfo', 'Version'],
						['EncounterSetNumberOverwrite', 'Encounter Set Number']
					];
					if (doubleSideTypes.indexOf(cardType) > -1) {
						mapping = mapping.concat([
							['NameBack', 'BName'],
							['StageLetterBack', 'BEngagement Cost'],
							['RulesBack', 'BText'],
							['FlavourBack', 'BFlavour'],
							['StoryBack', 'BFlavour'],
							['OptionRightBack', 'BVictory Points'],
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

					if ((cardType == 'Hero') && (flags.indexOf('Promo') > -1)) {
						cardType = 'Hero Promo';
						cardSphere = 'Promo' + card['BSphere'];
						card['BSphere'] = cardSphere;
					}
					else if ((cardType == 'Encounter Side Quest') && (card['BSphere'] + '' == 'SmallTextArea')) {
						cardType = 'Encounter Side Quest SmallTextArea';
					}
					else if ((cardType == 'Encounter Side Quest') && (card['BSphere'] + '' == 'Cave')) {
						cardType = 'Cave';
					}
					else if ((cardType == 'Encounter Side Quest') && (card['BSphere'] + '' == 'Region')) {
						cardType = 'Region';
					}
					else if (cardType == 'Objective Hero') {
						cardSphere = 'Hero';
						card['BSphere'] = cardSphere;
					}
					else if (cardType == 'Objective Location') {
						cardSphere = 'Location';
						card['BSphere'] = cardSphere;
					}
					else if ((cardType == 'Ship Enemy') && (card['BSphere'] + '' == 'Nightmare')) {
						cardSphere = 'ShipNightmare';
						card['BSphere'] = cardSphere;
					}

					keywords = card['BKeywords'];
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
						['OptionSpecial', 'BSpecial Icon'],
						['Rules', 'BText'],
						['Shadow', 'BShadow'],
						['Flavour', 'BFlavour'],
						['Story', 'BFlavour'],
						['Artist', 'BArtist'],
						['Adventure', 'Adventure'],
						['Cycle', 'Adventure'],
						['CollectionNumberCustom', 'Card Number'],
						['CollectionNumberCustomOverwrite', 'BPrinted Card Number'],
						['CollectionInfo', 'Version'],
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
						else if (['Special Icon', 'BSpecial Icon'].indexOf(nXml + '') > -1) {
							s.set(nEon, 'Empty');
						}
						else {
							s.set(nEon, '');
						}
						continue;
					}

					if (['Victory Points', 'BVictory Points'].indexOf(nXml + '') > -1) {
						if ((cardType != 'Presentation') && (cardType != 'Rules') && vXml.match(/^[0-9]+$/)) {
							vXml = translate['Victory'][lang].toUpperCase() + ' ' + vXml;
						}
					}
					else if (['Special Icon', 'BSpecial Icon'].indexOf(nXml + '') > -1) {
						vXml = convertIconName(vXml);
					}
					else if (['Artist', 'BArtist'].indexOf(nXml + '') > -1) {
						if (vXml == 'Unknown Artist') {
							vXml = translate['Unknown Artist'][lang];
						}
					}
					else if (['Text', 'BText'].indexOf(nXml + '') > -1) {
						if (keywords) {
							vXml = keywords + '\n\n' + vXml;
						}
					}
					else if (nXml == 'Card Number') {
						if ((sides.length > 1) && (side == 'front')) {
							vXml = vXml + 'a';
						}
						else if ((sides.length > 1) && (side == 'back')) {
							vXml = vXml + 'b';
						}
					}
					else if ((nXml == 'Adventure') && (cardType != 'Campaign')) {
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
				if (flags.indexOf('Asterisk') > -1) {
					s.set('Asterisk', 1);
				}
				else {
					s.set('Asterisk', 0);
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
				if (flags.indexOf('AsteriskBack') > -1) {
					s.set('AsteriskBack', 1);
				}
				else {
					s.set('AsteriskBack', 0);
				}

				if (context == 'renderer') {
					let bodyShapeNeeded = false;
					if (((cardType == 'Hero') && (cardSphere != 'Neutral')) || (cardType == 'Treasure') ||
						((['Encounter Side Quest', 'Encounter Side Quest SmallTextArea', 'Player Side Quest', 'Quest'].indexOf(cardType) > -1) &&
						(s.get('OptionRight') && (s.get('OptionRight') + '').length))) {
						bodyShapeNeeded = true;
					}
					s.set('BodyShapeNeededRenderer', bodyShapeNeeded);

					let bodyShapeNeededBack = false;
					if ((cardType == 'Quest') && s.get('OptionRightBack') && (s.get('OptionRightBack') + '').length) {
						bodyShapeNeededBack = true;
					}
					s.set('BodyShapeNeededBackRenderer', bodyShapeNeededBack);
				}

				if (cardType == 'Cave') {
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

				if ((cardType == 'Presentation') || (cardType == 'Rules')) {
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

				if (cardType == 'Contract') {
					s.set('SideA', markUp(translate['Side'][lang].toUpperCase() + ' A', 'Side', cardType, lang, setID));
					s.set('SideB', markUp(translate['Side'][lang].toUpperCase() + ' B', 'Side', cardType, lang, setID));

					if (card['BName']) {
						s.set('Template', 'DoubleSided');
					}
					else {
						s.set('Template', 'Neutral');
					}
				}

				if (['Boon', 'Burden'].indexOf(cardSphere) > -1) {
					s.set('Subtype', markUp(translate[cardSphere][lang].toUpperCase(), 'Subtype', cardType, lang, setID));
				}
				else {
					s.set('Subtype', '');
				}

				if ((cardType == 'Campaign') && (cardSphere == 'Setup')) {
					s.set('Type', markUp(translate['Setup'][lang].toUpperCase(), 'Type', cardType, lang, setID));
					s.set('Template', 'Standard');
				}
				else {
					s.set('Type', markUp(translate[cardType][lang].toUpperCase(), 'Type', cardType, lang, setID));
				}

				if (side == 'front') {
					if (card['Portrait Shadow']) {
						s.set('PortraitShadow', card['Portrait Shadow']);
						if ((cardType == 'Quest') && (!card['BArtwork'] || (card['BArtwork'] == card['Artwork']))) {
							s.set('PortraitBackShadow', card['Portrait Shadow']);
						}
					}
					if ((cardType == 'Quest') && card['BPortrait Shadow'] && card['BArtwork'] && (card['BArtwork'] != card['Artwork'])) {
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
						s.set('Portrait-external-path', 'project:imagesOther/white.jpg');
					}
					if ((cardType == 'Quest') || (cardType == 'Contract')) {
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
							s.set('PortraitBack-external-path', 'project:imagesOther/white.jpg');
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
					else {
						s.set('Portrait-external-path', 'project:imagesOther/white.jpg');
					}
				}

				let encounterSet = card['Encounter Set'];
				if (card['Encounter Set Back'] && (side == 'back')) {
					encounterSet = card['Encounter Set Back'];
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

				if (cardType == 'Quest') {
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
					while (encounterSets.length < 5) {
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

				if (card['Encounter Set Number Start']) {
					s.set('EncounterSetNumber', parseInt(card['Encounter Set Number Start']) + j);
				}
				else {
					s.set('EncounterSetNumber', 0);
				}

				if (card['Encounter Set Total']) {
					s.set('EncounterSetTotal', card['Encounter Set Total']);
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

				if (((cardType == 'Presentation') && (['BlueNightmare', 'GreenNightmare', 'PurpleNightmare', 'RedNightmare', 'BrownNightmare', 'YellowNightmare'].indexOf(cardSphere) == -1)) || (cardType == 'Rules')) {
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
					if (flags.indexOf('Promo') > -1) {
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

				if ((cardType == 'Full Art Landscape') || (cardType == 'Full Art Portrait')) {
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
				s.set('Name-style', 'FAMILY: {"Vafthrudnir"}');
				s.set('Subtype-style', 'FAMILY: {"Vafthrudnir"}');
				s.set('Type-style', 'FAMILY: {"Vafthrudnir"}');
				s.set('Adventure-style', 'FAMILY: {"Vafthrudnir"}');
				s.set('Cycle-style', 'FAMILY: {"Vafthrudnir"}');
				s.set('Option-style', 'WIDTH: SEMICONDENSED; FAMILY: {"Vafthrudnir"}');
				s.set('EncounterSetNumber-style', 'WEIGHT: BOLD; FAMILY: {"Times New Roman"}');
				s.set('Bottom-style', 'WIDTH: SEMICONDENSED; WEIGHT: BOLD; FAMILY: {"Times New Roman"}');
				s.set('Side-style', 'FAMILY: {"Vafthrudnir"}');
				s.set('Name-pointsize', Math.round(defaultNamePointSize * 1.734 * 100) / 100);
				s.set('Bottom-pointsize', defaultBottomPointSize);
				s.set('EncounterSetNumber-pointsize', defaultEncounterSetNumberPointSize);
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

				if ((cardType == 'Presentation') || (cardType == 'Rules')) {
					s.set('VerticalSpacer-tag-replacement', '<image res://TheLordOfTheRingsLCG/image/empty1x1.png 0.1 0.1>');
					s.set('Body-lineTightness', 0.8);
					s.set('BodyRight-lineTightness', 0.8);
				}
				else {
					s.set('VerticalSpacer-tag-replacement', '<image res://TheLordOfTheRingsLCG/image/empty1x1.png 0.075 0.075>');
					s.set('Body-lineTightness', 0.2);
					s.set('BodyRight-lineTightness', 0.2);
				}

				if (cardType == 'Hero Promo') {
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

				if ((cardType == 'Cave') || (cardType == 'Region')) {
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
					if (cardType in bodyRegion) {
						s.set('TraitOut-Body-region', bodyRegion[cardType]);
					}

					if (cardType in traitRegion) {
						s.set('TraitOut-Trait-region', traitRegion[cardType]);
					}
				}
				else if (cardType in bodyNoTraitRegion) {
					s.set('TraitOut', 'false');
					s.set('Body-region', bodyNoTraitRegion[cardType]);
				}
				else {
					s.set('TraitOut', 'true');
					if ((cardType == 'Hero Promo') && (lang == 'German')) {
						s.set('TraitOut-Body-region', '73,467,269,45');
					}
					else if (cardType in bodyRegion) {
						s.set('TraitOut-Body-region', bodyRegion[cardType]);
					}

					if (cardType in traitRegion) {
						s.set('TraitOut-Trait-region', traitRegion[cardType]);
					}
				}

				if (s.get('Unique') + '') {
					if (cardType in nameUniqueRegion) {
						s.set('Name-region', nameUniqueRegion[cardType]);
					}
				}
				else {
					if (cardType in nameRegion) {
						s.set('Name-region', nameRegion[cardType]);
					}
				}

				if ((cardType == 'Hero Promo') && (translate[cardType][lang].length > 4)) {
					s.set('Type-region', '279,448,39,15');
				}
				else {
					if (cardType in typeRegion) {
						s.set('Type-region', typeRegion[cardType]);
					}
				}

				if (cardType == 'Quest') {
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
					['OptionRightDecoration-region', optionRightDecorationRegion],
					['OptionRight-region', optionRightRegion],
					['OptionSpecial-portrait-clip-region', optionSpecialRegion],
					['Artist-region', artistRegion],
					['Copyright-region', copyrightRegion],
					['Collection-portrait-clip-region', collectionPortraitRegion],
					['CollectionNumber-region', collectionNumberRegion],
					['CollectionInfo-region', collectionInfoRegion],
					['PageIn-region', pageInRegion],
					['Side-region', sideRegion],
					['Asterisk-region', asteriskRegion],
					['GameName-portrait-clip-region', gameNamePortraitRegion],
					['Name-portrait-clip-region', namePortraitRegion],
					['EncounterSet1-portrait-clip-region', encounterSet1PortraitRegion],
					['EncounterSet2-portrait-clip-region', encounterSet2PortraitRegion],
					['EncounterSet3-portrait-clip-region', encounterSet3PortraitRegion],
					['EncounterSet4-portrait-clip-region', encounterSet4PortraitRegion],
					['EncounterSet5-portrait-clip-region', encounterSet5PortraitRegion],
					['Sphere-Body-shape', sphereBodyShape],
					['Option-Body-shape', optionBodyShape]
				];
				for (let k = 0; k < relations.length; k++) {
					if (cardType in relations[k][1]) {
						s.set(relations[k][0], relations[k][1][cardType]);
					}
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
				else if (cardType == 'Contract') {
					if (card['BName']) {
						back = '-';
						simple_back = false;
					}
					else {
						back = 'p';
						simple_back = true;
					}
				}
				else if (doubleSideTypes.indexOf(cardType) > -1) {
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

				if (context == 'renderer') {
					s.set('Bottom-format', '<width semicondensed><family "Times New Roman"><size ' + defaultBottomPointSize + '><b>');
					s.set('Bottom-formatEnd', '</b></size></family></width>');
					s.set('EncounterSetNumber-format', '<family "Times New Roman"><size ' + defaultEncounterSetNumberPointSize + '><b>');
					s.set('EncounterSetNumber-formatEnd', '</b></size></family>');
					s.set('OptionRight-format', '<width semicondensed>');
					s.set('OptionRight-formatEnd', '</width>');
					s.set('TypeRenderer', cardType);
					s.set('CardNumberRenderer', card['Card Number']);
					s.set('IdRenderer', card['octgn']);
					s.set('CopyRenderer', copy);
					s.set('BackRenderer', back);
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
	value = value.replace(/\u00c2/g, 'A');
	value = value.replace(/\u00e2/g, 'a');
	value = value.replace(/[\u00da\u00db]/g, 'U');
	value = value.replace(/[\u00fa\u00fb]/g, 'u');
	value = value.replace(/[,\(\)'"\u2013\u2014\u2026\u2019\u201c\u201d\u201e\u00ab\u00bb]/g, '');
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
	value = value.trim();
	value = value.replace(/ /g, '-');
	return value;
}

function updatePunctuation(value, lang) {
	if (lang == 'Polish') {
		value = value.replace(/\u201c/g, '\u201e');
	}
	else if (lang == 'German') {
		value = value.replace(/\u201c/g, '\u201e');
		value = value.replace(/\u201d/g, '\u201c');
	}
	else if (lang == 'French') {
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
	var res = '';
	var tag = false;
	value = value.replace(/\[space\]/g, ' ');
	value = value.replace(/\[SPACE\]/g, ' ');
	value = updatePunctuation(value, lang);
	for (let i = 0; i < value.length; i++) {
		let ch = value[i];
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
	value = value.replace(/\[NOBR\]/g, '\u00a0');
	value = value.replace(/\[inline\]\n\n/g, ' ');
	value = value.replace(/\[inline\]/g, '');
	value = value.replace(/\[INLINE\]\n\n/g, ' ');
	value = value.replace(/\[INLINE\]/g, '');

	if (['Side', 'Subtype'].indexOf(key + '') > -1) {
		return updateVafthrudnir(value, 3.515, lang);
	}
	else if (key == 'Type') {
		return updateVafthrudnir(value, 5.095, lang);
	}
	else if (['Name', 'BName'].indexOf(key + '') > -1) {
		let fixHeight = false;
		let lowerSize = 6.5;
		if (cardType in namePointSize) {
			lowerSize = namePointSize[cardType];
		}

		if ((['Ally', 'Hero', 'Hero Promo'].indexOf(cardType) > -1) && (value.length > 10) &&
			value.match(/^[\u00c0\u00c1\u00c2\u00c3\u00c4\u00c8\u00c9\u00ca\u00cb\u00cc\u00cd\u00ce\u00cf\u00d1\u00d2\u00d3\u00d4\u00d5\u00d6\u00d9\u00da\u00db\u00dc\u0106\u0108\u0143\u015a\u0179\u017b]/)) {
			lowerSize = lowerSize * 0.8;
			fixHeight = true;
		}
		res = updateVafthrudnir(value, lowerSize, lang);
		if (fixHeight) {
			res += '<family "Vafthrudnir"><size ' + Math.round(lowerSize / 0.8 * 1.423 * 100) / 100 + '> </size></family>';
		}
		return res;
	}
	else if ((['Victory Points', 'BVictory Points'].indexOf(key + '') > -1) && (['Presentation', 'Rules'].indexOf(cardType) == -1)) {
		return updateVafthrudnir(value, 3.69, lang);
	}
	else if (key == 'Adventure') {
		if (cardType == 'Campaign') {
			return updateVafthrudnir(value, 5.6, lang);
		}
		else {
			return updateVafthrudnir(value, 3.69, lang);
		}
	}

	if (['Text', 'BText', 'Shadow', 'BShadow'].indexOf(key + '') > -1) {
		if (lang == 'English') {
			value = value.replace(/\b(Quest Resolution)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(Valour )?(Resource |Planning |Quest |Travel |Encounter |Combat |Refresh )?(Action):/g, '[b]$1$2$3[/b]:');
			value = value.replace(/\b(When Revealed|Forced|Valour Response|Response|Travel|Shadow|Resolution):/g, '[b]$1[/b]:');
			value = value.replace(/\b(Setup)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(Condition)\b/g, '[bi]$1[/bi]');
		}
		else if (lang == 'French') {
			value = value.replace(/\b(R\u00e9solution de la qu\u00eate)( \([^\)]+\))? ?:/g, '[b]$1[/b]$2 :');
			value = value.replace(/(\[Vaillance\] )?(\[Ressource\] |\[Organisation\] |\[Qu\u00eate\] |\[Voyage\] |\[Rencontre\] |\[Combat\] |\[Restauration\] )?\b(Action) ?:/g, '[b]$1$2$3[/b] :');
			value = value.replace(/\b(Une fois r\u00e9v\u00e9l\u00e9e|Forc\u00e9|\[Vaillance\] R\u00e9ponse|R\u00e9ponse|Trajet|Ombre|R\u00e9solution) ?:/g, '[b]$1[/b] :');
			value = value.replace(/\b(Mise en place)( \([^\)]+\))? ?:/g, '[b]$1[/b]$2 :');
			value = value.replace(/\b(Condition)\b/g, '[bi]$1[/bi]');
		}
		else if (lang == 'German') {
			value = value.replace(/\b(Abenteuer bestehen)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(Ehrenvolle )?(Ressourcenaktion|Planungsaktion|Abenteueraktion|Reiseaktion|Begegnungsaktion|Kampfaktion|Auffrischungsaktion|Aktion):/g, '[b]$1$2[/b]:');
			value = value.replace(/\b(Wenn aufgedeckt|Erzwungen|Ehrenvolle Reaktion|Reaktion|Reise|Schatten|Aufl\u00f6sung):/g, '[b]$1[/b]:');
			value = value.replace(/\b(Vorbereitung)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(Zustand)\b/g, '[bi]$1[/bi]');
		}
		else if (lang == 'Spanish') {
			value = value.replace(/\b(Resoluci\u00f3n de la misi\u00f3n)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(Acci\u00f3n)( de Recursos| de Planificaci\u00f3n| de Misi\u00f3n| de Viaje| de Encuentro| de Combate| de Recuperaci\u00f3n)?( de Valor)?:/g, '[b]$1$2$3[/b]:');
			value = value.replace(/\b(Al ser revelada|Obligado|Respuesta de Valor|Respuesta|Viaje|Sombra|Resoluci\u00f3n):/g, '[b]$1[/b]:');
			value = value.replace(/\b(Preparaci\u00f3n)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(Condici\u00f3n)\b/g, '[bi]$1[/bi]');
		}
		else if (lang == 'Polish') {
			value = value.replace(/\b(Rozpatrzenie wyprawy)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(Akcja)( Zasob\u00f3w| Planowania| Wyprawy| Podr\u00f3\u017cy| Spotka\u0144| Walki| Odpoczynku)?( M\u0119stwa)?:/g, '[b]$1$2$3[/b]:');
			value = value.replace(/\b(Po odkryciu|Wymuszony|Odpowied\u017a M\u0119stwa|Odpowied\u017a|Podr\u00f3\u017c|Cie\u0144|Nast\u0119pstwa):/g, '[b]$1[/b]:');
			value = value.replace(/\b(Przygotowanie)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(Stan)\b/g, '[bi]$1[/bi]');
		}
		else if (lang == 'Italian') {
			value = value.replace(/\b(Risoluzione della Ricerca)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(Azione)( Valorosa)?( di Risorse| di Pianificazione| di Ricerca| di Viaggio| di Incontri| di Combattimento| di Riordino)?:/g, '[b]$1$2$3[/b]:');
			value = value.replace(/\b(Quando Rivelata|Obbligato|Risposta Valorosa|Risposta|Viaggio|Ombra|Risoluzione):/g, '[b]$1[/b]:');
			value = value.replace(/\b(Preparazione)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(Condizione)\b/g, '[bi]$1[/bi]');
		}
		else if (lang == 'Portuguese') {
			value = value.replace(/\b(Resolu\u00e7\u00e3o da Miss\u00e3o)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(A\u00e7\u00e3o)( Valorosa)?( de Recursos| de Planejamento| de Miss\u00e3o| de Viagem| de Encontro| de Combate| de Renova\u00e7\u00e3o)?:/g, '[b]$1$2$3[/b]:');
			value = value.replace(/\b(Efeito Revelado|Efeito For\u00e7ado|Resposta Valorosa|Resposta|Viagem|Efeito Sombrio|Resolu\u00e7\u00e3o):/g, '[b]$1[/b]:');
			value = value.replace(/\b(Prepara\u00e7\u00e3o)( \([^\)]+\))?:/g, '[b]$1[/b]$2:');
			value = value.replace(/\b(Condi\u00e7\u00e3o)\b/g, '[bi]$1[/bi]');
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
		value = value.replace(/\[bi\](.*?)\[\/bi\]/g, '$1');
		value = value.replace(/\[b\](.*?)\[\/b\]/g, '$1');
		value = value.replace(/\[i\](.*?)\[\/i\]/g, '$1');
		tagPrefix = '</b></i></size></family><size ' + iconPointSize + '>';
		tagSuffix = '</size><family "Times New Roman"><size ' + defaultPointSize + '><i><b>';
	}
	else if (['Shadow', 'BShadow', 'Flavour', 'BFlavour'].indexOf(key + '') > -1) {
		value = value.replace(/\[bi\](.*?)\[\/bi\]/g, '[b]$1[/b]');
		value = value.replace(/\[i\](.*?)\[\/i\]/g, '$1');
		tagPrefix = '</i></size></family><size ' + iconPointSize + '>';
		tagSuffix = '</size><family "Times New Roman"><size ' + defaultPointSize + '><i>';
	}
	else {
		tagPrefix = '</size></family><size ' + iconPointSize + '>';
		tagSuffix = '</size><family "Times New Roman"><size ' + defaultPointSize + '>';
	}

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

	value = value.replace(/([^:;,.?!\u2026]) ((?:<\/b>)?(?:<\/i>)?(?:<\/size>)?(?:<\/family>)?(?:<size [^>]+>)?)(<uni>|<thr>|<att>|<def>|<wil>|<lea>|<lor>|<spi>|<tac>|<bag>|<fel>|<mas>|<hon>|<hof>|<hb>|<hw>|<sai>|<eos>|<per>|<pp>)/g, '$1\u00a0$2$3');
	value = value.replace(/([0-9]+) /g, '$1\u00a0');
	value = value.replace(/ ([0-9]+)([:;,.?!\)\u2026])/g, '\u00a0$1$2');
	value = value.replace(/(^|[ \n"\u201c\u201d\(])([\-\u2013\u2014'\u2019A-Za-z\u00c0-\u017e]{1,4})([:;,.?!"\u2026\u201c\u201d\)]*) (["\u201c\u201d\(]*)([\-\u2013\u2014'\u2019A-Za-z\u00c0-\u017e]{1,4})([:;,.?!"\u2026\u201c\u201d\)]+)(\n|$)/g, '$1$2$3\u00a0$4$5$6$7');
	value = value.replace(/ (["\u201c\u201d\(]*)([\-\u2013\u2014'\u2019A-Za-z\u00c0-\u017e]{1,2})([:;,.?!"\u2026\u201c\u201d\)]+)(\n|$)/g, '\u00a0$1$2$3$4');
	value = value.replace(/ ([;:?!])/g, '\u00a0$1');

	var valueOld;
	do {
		valueOld = value;
		value = value.replace(/\u00a0([^<]+)>/g, ' $1>');
	}
	while (value != valueOld);

	value = value.replace(/<\/i>(?! )/g, '</size><size 0.01></i>\u00a0</size><size ' + defaultPointSize + '>');
	value = value.replace(/<\/i>(?= )/g, '</size><size 0.01></i> </size><size ' + defaultPointSize + '>');
	value = value.replace(/\n+$/g, '');
	value = value.replace(/\n(<left>|<right>|<center>)?(?=\n)/g, '\n$1<vs>');

	function updateVafthrudnirReplacer(match, p1, p2, offset, string) {
		var res = '</size></family>' + updateVafthrudnir(p2, p1, lang) + '<family "Times New Roman"><size ' + defaultPointSize + '>';
		return res;
	}

	function updateLotrHeaderReplacer(match, p1, p2, offset, string) {
		var res = '</size></family><family "Lord of the Headers"><size ' + p1 + '>' + p2 + '</size></family><family "Times New Roman"><size ' + defaultPointSize + '>';
		return res;
	}

	value = value.replace(/<lotr ([0-9\.]+)>(.*?)<\/lotr>/g, updateVafthrudnirReplacer);
	value = value.replace(/<lotrheader ([0-9\.]+)>(.*?)<\/lotrheader>/g, updateLotrHeaderReplacer);
	value = value.replace(/<size [^>]+><\/size>/g, '');
	value = value.replace(/<family [^>]+><\/family>/g, '');

	value = value.replace(/<hs>/g, '<image res://TheLordOfTheRingsLCG/image/empty1x1.png 0.3 0.1>');

	if ((cardType == 'Presentation') || (cardType == 'Rules')) {
		value = value.replace(/<vs>/g, '<image res://TheLordOfTheRingsLCG/image/empty1x1.png 0.1 0.1>');
	}
	else {
		value = value.replace(/<vs>/g, '<image res://TheLordOfTheRingsLCG/image/empty1x1.png 0.075 0.075>');
	}

	value = updatePunctuation(value, lang);
	if ((['Traits', 'BTraits'].indexOf(key + '') > -1) && (lang == 'Spanish')) {
		value = value.replace(/\. /g, ' \u2022 ');
		value = value.replace(/\.$/g, '');
	}

	return value;
}
