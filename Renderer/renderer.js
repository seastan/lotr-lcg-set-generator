const fs = require('fs');
const he = require('he');
const {XMLParser} = require('fast-xml-parser');
eval(fs.readFileSync('../Frogmorton/common.js') + '');

const difficultyFolder = '../Difficulty/';
const generatedImagesFolderCheck = 'GeneratedImages/';
const generatedImagesFolder = '../GeneratedImages/';
const iconsFolder = '../Icons/';
const imagesFolder = '../Images/';
const xmlFolder = '../setEons/';

const containerFontSize = {
    'Adventure': 12,
    'AdventureBack': 12,
    'Artist': 11,
    'ArtistBack': 11,
    'Body': 14,
    'BodyBack': 14,
    'BodyRight': 14,
    'CollectionInfo': 11,
    'CollectionInfoBack': 11,
    'CollectionNumber': 11,
    'CollectionNumberBack': 11,
    'Copyright': 11,
    'CopyrightBack': 11,
    'Cycle': 14,
    'EncounterSetNumber': 11,
    'Name': 12,
    'NameBack': 12,
    'OptionLeft': 14,
    'OptionRight': 12,
    'OptionRightBack': 12,
    'PageIn': 11,
    'PageInBack': 11,
    'Side': 14,
    'SideBack': 14,
    'Star': 9,
    'StarBack': 9,
    'Subtype': 14,
    'TraitOut-Trait': 14,
    'Type': 12,
    'TypeBack': 12
};

var difficultyTypes = {};
difficultyTypes[ENEMY_NOSTAT] = ENEMY;
difficultyTypes[OBJECTIVE_HERO] = OBJECTIVE_ALLY;
difficultyTypes[OBJECTIVE_LOCATION] = OBJECTIVE;
difficultyTypes[SHIP_ENEMY] = ENEMY;
difficultyTypes[SHIP_OBJECTIVE] = OBJECTIVE_ALLY;

function RendererSettings() {
    this.settings = {};

    this.set = function(key, value) {
        this.settings[key] = value;
    };

    this.get = function(key) {
        return this.settings[key];
    };
}

function iterateKeys(root, name, res) {
    var json = root.json;
    for (let key in json) {
        if (json.hasOwnProperty(key) && (key != '#text') && !key.match(/^@_/)) {
            let child = json[key];
            if (child instanceof Array) {
                for (let i = 0; i < child.length; i++) {
                    let element = new ElementAdapter(child[i], root);
                    if (key == name) {
                        res.push(element);
                    }

                    iterateKeys(element, name, res);
                }
            }
            else {
                let element = new ElementAdapter(child, root);
                if (key == name) {
                    res.push(element);
                }

                iterateKeys(element, name, res);
            }
        }
    }
}

function ElementAdapter(json, parentElement) {
    this.json = json;
    this.parentElement = parentElement;

    this.print = function() {
        return JSON.stringify(this.json, null, 2);
    };

    this.getAttribute = function(name) {
        var value = this.json['@_' + name] + '';
        value = he.decode(value);
        return value;
    };

    this.getElementsByTagName = function(name) {
        var res = [];
        iterateKeys(this, name, res);
        return new ElementListAdapter(res);
    };

    this.getParentNode = function() {
        return this.parentElement;
    };

    this.isSameNode = function(element) {
        return this.json == element.json;
    };
}

function ElementListAdapter(list) {
    this.list = list;

    this.print = function() {
        return JSON.stringify(this.list, null, 2);
    };

    this.getLength = function() {
        return this.list.length;
    };

    this.item = function(number) {
        if ((number >= 0) && (number < this.list.length)) {
            return this.list[number];
        }
        else {
            return null;
        }
    };
}

function DocumentBuilderAdapter(path) {
    this.parser = new XMLParser({
        ignoreAttributes: false,
        processEntities: false
    });
    this.json = this.parser.parse(fs.readFileSync(path) + '');

    this.print = function() {
        return JSON.stringify(this.json, null, 2);
    };

    this.getDocumentElement = function() {
        for (let key in this.json) {
            if (this.json.hasOwnProperty(key)) {
                return new ElementAdapter(this.json[key], this);
            }
        }
    };

    this.getElementsByTagName = function(name) {
        var res = [];
        iterateKeys(this, name, res);
        return new ElementListAdapter(res);
    };
}

function getCardObjectsRenderer(_) {
    var settings = new RendererSettings();
    return [null, settings];
}

function round(value, digits) {
    return +value.toFixed(digits);
}

function updateRegion(key, value, card_type) {
    var regions = value.split(',');
    if (regions.length == 5) {
        regions = [regions[1], regions[2], regions[3], regions[4]];
    }
    else if (regions.length != 4) {
        return value;
    }

    for (let i = 0; i < regions.length; i++) {
        let bleed = 0;
        if (i < 2) {
            bleed = 38;
        }
        regions[i] = Math.round((regions[i] * 2 - bleed) / 1.75);
    }

    if ((key == 'Name-region') || (key == 'NameBack-region')) {
        regions[1] += 2;
    }

    var sizeKey = key.replace(/-region$/, '');
    if ((sizeKey in containerFontSize) &&
        (['Artist', 'ArtistBack', 'CollectionInfo', 'CollectionInfoBack',
          'CollectionNumber', 'CollectionNumberBack', 'Copyright', 'CopyrightBack'].indexOf(sizeKey) == -1)) {
        regions[0] -= 1;
        regions[2] += 2;
        regions[3] += 1;
    }

    if ((sizeKey == 'Type') && (card_type == HERO_PROMO)) {
        regions[2] += 10;
    }

    return regions;
}

function updateFontSize(value) {
    return round(value * 2 * 1.3333 / 14, 4);
}

function updateFontSizeReplacer(match, p1, offset, string) {
    return '<span style="font-size: ' + updateFontSize(p1) + 'em">';
}

function updateImageWidthReplacer(match, p1, p2, offset, string) {
    var width;
    if (p2.match(/pt$/)) {
        width = Math.round(p2.replace(/pt/g, '') * 2 * 1.3333 / 1.75);
    }
    else if (p2.match(/in$/)) {
        width = Math.round(p2.replace(/in/g, '') * 300 / 1.75);
    }
    else {
        width = Math.round(p2.replace(/cm/g, '') * 0.393701 * 300 / 1.75);
    }

    var res;
    if (width > 0) {
        res = '<img src="' + p1 + '" width="' + width + '">';
    }
    else {
        res = '<img src="' + imagesFolder + 'empty.png" width="1" height="1">';
    }

    return res;
}

function updateImageWidthHeightReplacer(match, p1, p2, p3, offset, string) {
    var width;
    if (p2.match(/pt$/)) {
        width = Math.round(p2.replace(/pt/g, '') * 2 * 1.3333 / 1.75);
    }
    else if (p2.match(/in$/)) {
        width = Math.round(p2.replace(/in/g, '') * 300 / 1.75);
    }
    else {
        width = Math.round(p2.replace(/cm/g, '') * 0.393701 * 300 / 1.75);
    }

    var height;
    if (p3.match(/pt$/)) {
        height = Math.round(p3.replace(/pt/g, '') * 2 * 1.3333 / 1.75);
    }
    else if (p3.match(/in$/)) {
        height = Math.round(p3.replace(/in/g, '') * 300 / 1.75);
    }
    else {
        height = Math.round(p3.replace(/cm/g, '') * 0.393701 * 300 / 1.75);
    }

    var res;
    if ((width > 0) && (height > 0)) {
        res = '<img src="' + p1 + '" width="' + width + '" height="' + height + '">';
    }
    else {
        res = '<img src="' + imagesFolder + 'empty.png" width="1" height="1">';
    }

    return res;
}

function convertTags(value) {
    value += '';
    value = value.replace(/&/g, '&amp;');
    value = value.replace(/\t/g, ' ');
    value = value.replace(/\n/g, '<br>');
    value = value.replace(/<uni>/g, '<lrs>u</lrs>');
    value = value.replace(/<thr>/g, '<lrs>t</lrs>');
    value = value.replace(/<att>/g, '<lrs>a</lrs>');
    value = value.replace(/<def>/g, '<lrs>d</lrs>');
    value = value.replace(/<wil>/g, '<lrs>w</lrs>');
    value = value.replace(/<lea>/g, '<lrs>e</lrs>');
    value = value.replace(/<lor>/g, '<lrs>o</lrs>');
    value = value.replace(/<spi>/g, '<lrs>s</lrs>');
    value = value.replace(/<tac>/g, '<lrs>c</lrs>');
    value = value.replace(/<bag>/g, '<lrs>b</lrs>');
    value = value.replace(/<fel>/g, '<lrs>f</lrs>');
    value = value.replace(/<hon>/g, '<lrs>1</lrs>');
    value = value.replace(/<hof>/g, '<lrs>2</lrs>');
    value = value.replace(/<hb>/g, '<lrs>3</lrs>');
    value = value.replace(/<hw>/g, '<lrs>4</lrs>');
    value = value.replace(/<sai>/g, '<lrs>0</lrs>');
    value = value.replace(/<eos>/g, '<lrs>5</lrs>');
    value = value.replace(/<pp>/g, '<lrs>8</lrs>');
    value = value.replace(/<lrs>/g, '<family "Symbols">');
    value = value.replace(/<\/lrs>/g, '</family>');
    value = value.replace(/<tracking -0.005><family "([^"]+)">/g, '<span style="letter-spacing: 0.2px; font-family: $1">');
    value = value.replace(/<family "([^"]+)">/g, '<span style="font-family: $1">');
    value = value.replace(/<\/family>/g, '</span>');
    value = value.replace(/<\/size><size 0\.01><\/i>(?:\u00a0| )<\/size><size [0-9.]+>/g, '</i>');
    value = value.replace(/<size ([0-9.]+)>/g, updateFontSizeReplacer);
    value = value.replace(/<\/size>/g, '</span>');
    value = value.replace(/<color ([^>]+)>/g, '<span style="color: $1">');
    value = value.replace(/<\/color>/g, '</span>');
    value = value.replace(/<width semicondensed>/g, '<span style="font-stretch: semi-condensed">');
    value = value.replace(/<\/width>/g, '</span>');
    value = value.replace(/<lt>/g, '&lt;');
    value = value.replace(/<gt>/g, '&gt;');
    value = value.replace(/res:\/\/TheLordOfTheRingsLCG\/image\/empty1x1\.png/g, imagesFolder + 'empty.png');
    value = value.replace(/res:\/\/TheLordOfTheRingsLCG\/image\/ShadowSeparator\.png/g, imagesFolder + 'shadow.png');
    value = value.replace(/project:imagesCustom\/[0-9a-f\-]+_Spacer\.png/g, imagesFolder + 'empty.png');
    value = value.replace(/project:imagesCustom\/[0-9a-f\-]+_Do-Not-Read-the-Following\.png/g, imagesFolder + 'donotread.png');
    value = value.replace(/project:imagesCustom\/[0-9a-f\-]+_Text-Divider-Black\.png/g, imagesFolder + 'textdividerblack.png');
    value = value.replace(/project:imagesCustom\/[0-9a-f\-]+_Text-Divider-Black-Official\.png/g, imagesFolder + 'textdividerblackofficial.png');
    value = value.replace(/project:imagesCustom\//g, generatedImagesFolder);
    value = value.replace(/project:imagesIcons\//g, iconsFolder);
    value = value.replace(/<image ([^ >]+)>/g, '<img src="$1">');
    value = value.replace(/<image ([^ >]+) ([^ >]+)>/g, updateImageWidthReplacer);
    value = value.replace(/<image ([^ >]+) ([^ >]+) ([^ >]+)>/g, updateImageWidthHeightReplacer);
    value = value.replace(/<img src="([^"]+?\/shadow\.png)"[^>]*>/g, '<img src="$1" width="266" height="21">');
    value = value.replace(/<img src="([^"]+?\/donotread\.png)"[^>]*>/g, '<img src="$1" width="249" height="64">');
    value = value.replace(/<img src="([^"]+?\/textdividerblack\.png)"[^>]*>/g, '<img src="$1" width="343" height="5">');
    value = value.replace(/<img src="([^"]+?\/textdividerblackofficial\.png)"[^>]*>/g, '<img src="$1" width="343" height="5">');
    value = value.replace(/<img src="([^"]+?\/empty\.png)"/g, '<emptyimg src="$1"');
    value = value.replace(/<img ([^>]+)>/g, '<img $1 style="display: block; margin-left: auto; margin-right: auto">');
    value = value.replace(/<emptyimg /g, '<img ');
    value = value.replace(/<left>/g, '');
    value = value.replace(/<center>/g, '');
    value = value.replace(/<right>/g, '');
    value = value.replace(/(style="display: block; margin-left: auto; margin-right: auto">)<br>/g, '$1');
    return value;
}

function saveResultRenderer(settings, _1, _2, _3, _4, _5, _6, _7, _8) {
    var containerRules = {
        'Adventure': function(data) {
            if (data.Adventure + '' == '') {
                return '';
            }

            return '<div style="text-align: center">' + data.Adventure + '</div>';
        },
        'Artist': function(data) {
            if (data.Artist + '' == '') {
                return '';
            }

            if (parseInt(data.NoArtist) == 1) {
                return '';
            }

            if (data.TypeRenderer == HERO_PROMO) {
                return '<div style="color: ' + data['Bottom-colour'] + '; line-height: ' + data['Artist-region'][3] + 'px">' +
                    data['Bottom-format'] + data['LRL-IllustratorShort'] + ' ' + data.Artist + data['Bottom-formatEnd'] + '</div>';
            }

            return '<div style="-webkit-text-stroke: 2px #000000; text-stroke: 2px #000000; color: ' + data['Bottom-colour'] + '; line-height: ' + data['Artist-region'][3] + 'px">' +
                data['Bottom-format'] + data['LRL-IllustratorShort'] + ' ' + data.Artist + data['Bottom-formatEnd'] + '</div>';
        },
        'Attack': function(data) {
            if (data.Attack + '' == '') {
                return '';
            }

            return '<div style="text-align: center; color: #000000; font-family: Vafthrudnir; font-size: 21px; width: ' + data['Attack-region'][2] + 'px">' + data.Attack + '</div>';
        },
        'Body': function(data) {
            var content = [];
            if (data.Story + '') {
                content.push(data['Story-format'] + data.Story + data['Story-formatEnd']);
            }

            if (data.Rules + '') {
                content.push(data['Rules-format'] + data.Rules + data['Rules-formatEnd']);
            }

            if (data.Shadow + '') {
                content.push(data['Shadow-format'] + data.Shadow + data['Shadow-formatEnd']);
            }

            if (data.Flavour + '') {
                content.push(data['Flavour-format'] + data.Flavour + data['Flavour-formatEnd']);
            }

            content = content.join('<br>' + data['VerticalSpacer-tag-replacement'] + '<br>');
            content = '<div style="color: ' + data['Body-colour'] + '; line-height: 0.96">' + content + '</div>';
            return content;
        },
        'BodyRight': function(data) {
            if (data.RulesRight + '' == '') {
                return '';
            }

            var content = data['RulesRight-format'] + data.RulesRight + data['RulesRight-formatEnd'];
            content = '<div style="color: ' + data['BodyRight-colour'] + '; line-height: 0.96">' + content + '</div>';
            return content;
        },
        'Collection-portrait-clip': function(data) {
            if (data['Collection-external-path'] + '' == '') {
                return '';
            }

            var content = '<img src="' + data['Collection-external-path'] + '" width="' + data['Collection-portrait-clip-region'][2] + '" height="' + data['Collection-portrait-clip-region'][3] + '">';
            return content;
        },
        'CollectionInfo': function(data) {
            if (data.CollectionInfo + '' == '') {
                return '';
            }

            if (data.TypeRenderer == HERO_PROMO) {
                return '<div style="color: ' + data['Bottom-colour'] + '; line-height: ' + data['CollectionInfo-region'][3] + 'px">' +
                    data['Bottom-format'] + data.CollectionInfo + data['Bottom-formatEnd'] + '</div>';
            }

            return '<div style="-webkit-text-stroke: 2px #000000; text-stroke: 2px #000000; color: ' + data['Bottom-colour'] + '; line-height: ' + data['CollectionInfo-region'][3] + 'px">' +
                data['Bottom-format'] + data.CollectionInfo + data['Bottom-formatEnd'] + '</div>';
        },
        'CollectionNumber': function(data) {
            if ((data.CollectionNumberCustom + '' == '') && (data.CollectionNumberCustomOverwrite + '' == '')) {
                return '';
            }

            if (data.TypeRenderer == HERO_PROMO) {
                return '<div style="color: ' + data['Bottom-colour'] + '; line-height: ' + data['CollectionNumber-region'][3] + 'px; padding-left: 2px">' +
                    data['Bottom-format'] + (data.CollectionNumberCustomOverwrite + '' || data.CollectionNumberCustom) + data['Bottom-formatEnd'] + '</div>';
            }

            return '<div style="-webkit-text-stroke: 2px #000000; text-stroke: 2px #000000; color: ' + data['Bottom-colour'] + '; line-height: ' + data['CollectionNumber-region'][3] + 'px">' +
                data['Bottom-format'] + (data.CollectionNumberCustomOverwrite + '' || data.CollectionNumberCustom) + data['Bottom-formatEnd'] + '</div>';
        },
        'Copyright': function(data) {
            if (data.Copyright + '' == '') {
                return '';
            }

            if (parseInt(data.NoCopyright) == 1) {
                return '';
            }

            if (data.TypeRenderer == HERO_PROMO) {
                return '<div style="color: ' + data['Bottom-colour'] + '; line-height: ' + data['Copyright-region'][3] + 'px">' +
                    data['Bottom-format'] + data.Copyright + data['Bottom-formatEnd'] + '</div>';
            }

            return '<div style="-webkit-text-stroke: 2px #000000; text-stroke: 2px #000000; color: ' + data['Bottom-colour'] + '; line-height: ' + data['Copyright-region'][3] + 'px">' +
                data['Bottom-format'] + data.Copyright + data['Bottom-formatEnd'] + '</div>';
        },
        'Cycle': function(data) {
            if (data.Cycle + '' == '') {
                return '';
            }

            return '<div style="text-align: center; padding-top: 4px">' + data.Cycle + '</div>';
        },
        'Defense': function(data) {
            if (data.Defense + '' == '') {
                return '';
            }

            return '<div style="text-align: center; color: #000000; font-family: Vafthrudnir; font-size: 21px; width: ' + data['Defense-region'][2] + 'px">' + data.Defense + '</div>';
        },
        'Difficulty': function(data) {
            if (data.Difficulty + '' == 'Standard') {
                return '';
            }

            var difficultyType = data.TypeRenderer;
            if (difficultyType in difficultyTypes) {
                difficultyType = difficultyTypes[difficultyType];
            }

            var content = '<img src="' + difficultyFolder + difficultyType.replace(/ /g, '') + '-' + data.Difficulty + '.png" style="margin-top: 22px; margin-left: 22px">';
            return content;
        },
        'EncounterSet-portrait-clip': function(data) {
            if (data['EncounterSet-external-path'] + '' == '') {
                return '';
            }

            var content = '<img src="' + data['EncounterSet-external-path'] + '" width="' + data['EncounterSet-portrait-clip-region'][2] + '" height="' + data['EncounterSet-portrait-clip-region'][3] + '">';
            return content;
        },
        'EncounterSet1-portrait-clip': function(data) {
            if (data['EncounterSet1-external-path'] + '' == '') {
                return '';
            }

            var content = '<img src="' + data['EncounterSet1-external-path'] + '" width="' + data['EncounterSet1-portrait-clip-region'][2] + '" height="' + data['EncounterSet1-portrait-clip-region'][3] + '">';
            return content;
        },
        'EncounterSet2-portrait-clip': function(data) {
            if (data['EncounterSet2-external-path'] + '' == '') {
                return '';
            }

            var content = '<img src="' + data['EncounterSet2-external-path'] + '" width="' + data['EncounterSet2-portrait-clip-region'][2] + '" height="' + data['EncounterSet2-portrait-clip-region'][3] + '">';
            return content;
        },
        'EncounterSet3-portrait-clip': function(data) {
            if (data['EncounterSet3-external-path'] + '' == '') {
                return '';
            }

            var content = '<img src="' + data['EncounterSet3-external-path'] + '" width="' + data['EncounterSet3-portrait-clip-region'][2] + '" height="' + data['EncounterSet3-portrait-clip-region'][3] + '">';
            return content;
        },
        'EncounterSet4-portrait-clip': function(data) {
            if (data['EncounterSet4-external-path'] + '' == '') {
                return '';
            }

            var content = '<img src="' + data['EncounterSet4-external-path'] + '" width="' + data['EncounterSet4-portrait-clip-region'][2] + '" height="' + data['EncounterSet4-portrait-clip-region'][3] + '">';
            return content;
        },
        'EncounterSet5-portrait-clip': function(data) {
            if (data['EncounterSet5-external-path'] + '' == '') {
                return '';
            }

            var content = '<img src="' + data['EncounterSet5-external-path'] + '" width="' + data['EncounterSet5-portrait-clip-region'][2] + '" height="' + data['EncounterSet5-portrait-clip-region'][3] + '">';
            return content;
        },
        'EncounterSet6-portrait-clip': function(data) {
            if (data['EncounterSet6-external-path'] + '' == '') {
                return '';
            }

            var content = '<img src="' + data['EncounterSet6-external-path'] + '" width="' + data['EncounterSet6-portrait-clip-region'][2] + '" height="' + data['EncounterSet6-portrait-clip-region'][3] + '">';
            return content;
        },
        'EncounterSetNumber': function(data) {
            if (data.EncounterSetNumberOverwrite + '' != '') {
                return '<div style="text-align: center; color: #FFFFFF">' + data['EncounterSetNumber-format'] + data.EncounterSetNumberOverwrite + data['EncounterSetNumber-formatEnd'] + '</div>';
            }

            if (parseInt(data.EncounterSetNumber) == 0) {
                return '';
            }

            return '<div style="text-align: center; color: #FFFFFF; line-height: ' + data['EncounterSetNumber-region'][3] + 'px; margin-left: auto; margin-right: auto">' +
                data['EncounterSetNumber-format'] + data.EncounterSetNumber + '/' + data.EncounterSetTotal + data['EncounterSetNumber-formatEnd'] + '</div>';
        },
        'Engagement': function(data) {
            if (data.Engagement + '' == '') {
                return '';
            }

            return '<div style="text-align: center; color: #C46900; font-family: Vafthrudnir; font-size: 29px; width: ' + data['Engagement-region'][2] + 'px">' + data.Engagement + '</div>';
        },
        'HitPoints': function(data) {
            if (data.HitPoints + '' == '') {
                return '';
            }

            return '<div style="-webkit-text-stroke: 2px #000000; text-stroke: 2px #000000; text-align: center; color: #DD4240; font-family: Vafthrudnir; font-size: 46px; width: ' +
                data['HitPoints-region'][2] + 'px">' + data.HitPoints + '</div>';
        },
        'Name': function(data) {
            if (data.Name + '' == '') {
                return '';
            }

            var rotate = '';
            if (data['Name-region'][3] > data['Name-region'][2] * 3) {
                rotate = '; width: 100%; line-height: ' + (data['Name-region'][2] - 2) + 'px; -webkit-transform: rotate(180deg); transform: rotate(180deg)';
            }

            var unique = '';
            if (data.Unique + '') {
                unique = '<span style="font-size: ' + updateFontSize(data['Name-pointsize']) + 'em"><span style="font-family: Symbols">u</span> </span>';
            }

            var content = '<div style="text-align: center' + rotate + '"><span style="color: ' + data['Name-colour'] + '">' + unique + data.Name + '</span></div>';
            return content;
        },
        'OptionLeft': function(data) {
            if (data.OptionLeft + '' == '') {
                return '';
            }

            return data['OptionLeft-format'] + data.OptionLeft + data['OptionLeft-formatEnd'];
        },
        'OptionRight': function(data) {
            if (data.OptionRight + '' == '') {
                return '';
            }

            return '<div style="text-align: center; padding-top: 4px">' + data['OptionRight-format'] + data.OptionRight + data['OptionRight-formatEnd'] + '</div>';
        },
        'PageIn': function(data) {
            if (parseInt(data.PageNumber) == 0) {
                return '';
            }

            return '<div style="text-align: right">' + data['PageIn-format'] + data['LRL-Page'] + ' ' + data.PageNumber + data['LRL-PageOf'] + data.PageTotal + data['PageIn-formatEnd'] + '</div>';
        },
        'Portrait-portrait-clip': function(data) {
            var suffix = '';
            if (data.SuffixRenderer == '-2') {
                suffix = '.B';
            }
            var content = '';
            if (fs.existsSync(generatedImagesFolderCheck + data.Id + suffix + '.jpg')) {
                content = '<img src="' + generatedImagesFolder + data.Id + suffix + '.jpg" width="100%" height="100%">';
            }
            return content;
        },
        'Progress': function(data) {
            if (data.Progress + '' == '') {
                return '';
            }

            return '<div style="text-align: center; color: #C46900; font-family: Vafthrudnir; font-size: 27px; width: ' + data['Progress-region'][2] + 'px">' + data.Progress + '</div>';
        },
        'ResourceCost': function(data) {
            if (data.ResourceCost + '' == '') {
                return '';
            }

            var size = 42;
            if (data.TypeRenderer == TREASURE) {
                size = 34;
            }

            return '<div style="-webkit-text-stroke: 2px #000000; text-stroke: 2px #000000; text-align: center; color: #DEDEDE; font-family: Vafthrudnir; font-size: ' + size + 'px; width: ' +
                data['ResourceCost-region'][2] + 'px">' + '<span style="vertical-align: middle; display: inline-block; padding-right: 2px">' + data.ResourceCost + '</span></div>';
        },
        'Side': function(data) {
            if ((data.Side + '' == '') && ((data.SideA + '' == '') || (data.Template == 'Neutral'))) {
                return '';
            }

            return '<div style="text-align: center; padding-top: 2px">' + (data.Side || data.SideA) + '</div>';
        },
        'Stage': function(data) {
            if ((data.Stage + '' == '') || (data.StageLetter + '' == '')) {
                return '';
            }

            return '<div style="text-align: center; color: #53B2C5; font-family: Vafthrudnir; width: ' + data['Stage-region'][2] + 'px"><span style="vertical-align: middle; display: inline-block; font-size: 48px">' +
                data.Stage + '</span><span style="vertical-align: middle; display: inline-block; font-size: 24px; padding-bottom: 4px; padding-right: 4px">' + data.StageLetter + '</span></div>';
        },
        'Star': function(data) {
            if (parseInt(data.Star) == 0) {
                return '';
            }

            return '<div style="color: ' + data['Star-colour'] + '; line-height: ' + data['Star-region'][3] + 'px">' +
                data['Star-format'] + '&#10038;' + data['Star-formatEnd'] + '</div>';
        },
        'Subtype': function(data) {
            if (data.Subtype + '' == '') {
                return '';
            }

            return '<div style="text-align: center; padding-top: 4px">' + data.Subtype + '</div>';
        },
        'Threat': function(data) {
            if (data.Threat + '' == '') {
                return '';
            }

            return '<div style="text-align: center; color: #000000; font-family: Vafthrudnir; font-size: 21px; width: ' + data['Threat-region'][2] + 'px">' + data.Threat + '</div>';
        },
        'ThreatCost': function(data) {
            if (data.ThreatCost + '' == '') {
                return '';
            }

            return '<div style="text-align: center; color: #2E7496; font-family: Vafthrudnir; font-size: 29px; width: ' + data['ThreatCost-region'][2] + 'px">' + data.ThreatCost + '</div>';
        },
        'TraitOut-Trait': function(data) {
            if (data.Trait + '' == '') {
                return '';
            }

            var content = data['Trait-format'] + data.Trait + data['Trait-formatEnd'];
            content = '<div style="text-align: center; color: ' + data['Body-colour'] + '; line-height: 0.96">' + content + '</div>';
            return content;
        },
        'Type': function(data) {
            if (data.Type + '' == '') {
                return '';
            }

            return '<div style="text-align: center">' + data.Type + '</div>';
        },
        'Willpower': function(data) {
            if (data.Willpower + '' == '') {
                return '';
            }

            return '<div style="text-align: center; color: #000000; font-family: Vafthrudnir; font-size: 21px; width: ' + data['Willpower-region'][2] + 'px">' + data.Willpower + '</div>';
        }
    };

    var containerRulesBack = {
        'AdventureBack': function(data) {
            if (data.Adventure + '' == '') {
                return '';
            }

            return '<div style="text-align: center">' + data.Adventure + '</div>';
        },
        'ArtistBack': function(data) {
            if ((data.ArtistBack + '' == '') && (data.Artist + '' == '')) {
                return '';
            }

            if (parseInt(data.NoArtistBack) == 1) {
                return '';
            }

            return '<div style="-webkit-text-stroke: 2px #000000; text-stroke: 2px #000000; color: ' + data['Bottom-colour'] + '; line-height: ' + data['ArtistBack-region'][3] + 'px">' +
                data['Bottom-format'] + data['LRL-IllustratorShort'] + ' ' + (data.ArtistBack + '' || data.Artist) + data['Bottom-formatEnd'] + '</div>';
        },
        'BodyBack': function(data) {
            var content = [];
            if (data.StoryBack + '') {
                content.push(data['StoryBack-format'] + data.StoryBack + data['StoryBack-formatEnd']);
            }

            if (data.RulesBack + '') {
                content.push(data['RulesBack-format'] + data.RulesBack + data['RulesBack-formatEnd']);
            }

            if (data.FlavourBack + '') {
                content.push(data['FlavourBack-format'] + data.FlavourBack + data['FlavourBack-formatEnd']);
            }

            content = content.join('<br>' + data['VerticalSpacer-tag-replacement'] + '<br>');
            content = '<div style="color: ' + data['Body-colour'] + '; line-height: 0.96">' + content + '</div>';
            return content;
        },
        'CollectionBack-portrait-clip': function(data) {
            if (data['Collection-external-path'] + '' == '') {
                return '';
            }

            var content = '<img src="' + data['Collection-external-path'] + '" width="' + data['CollectionBack-portrait-clip-region'][2] + '" height="' + data['CollectionBack-portrait-clip-region'][3] + '">';
            return content;
        },
        'CollectionInfoBack': function(data) {
            if (data.CollectionInfo + '' == '') {
                return '';
            }

            return '<div style="-webkit-text-stroke: 2px #000000; text-stroke: 2px #000000; color: ' + data['Bottom-colour'] + '; line-height: ' + data['CollectionInfoBack-region'][3] +
                'px">' + data['Bottom-format'] + data.CollectionInfoBack + data['Bottom-formatEnd'] + '</div>';
        },
        'CollectionNumberBack': function(data) {
            if ((data.CollectionNumberCustom + '' == '') && (data.CollectionNumberCustomOverwriteBack + '' == '')) {
                return '';
            }

            return '<div style="-webkit-text-stroke: 2px #000000; text-stroke: 2px #000000; color: ' + data['Bottom-colour'] + '; line-height: ' + data['CollectionNumberBack-region'][3] +
                'px">' + data['Bottom-format'] + (data.CollectionNumberCustomOverwriteBack + '' || data.CollectionNumberCustom) + data['Bottom-formatEnd'] + '</div>';
        },
        'CopyrightBack': function(data) {
            if (data.Copyright + '' == '') {
                return '';
            }

            if (parseInt(data.NoCopyrightBack) == 1) {
                return '';
            }

            return '<div style="-webkit-text-stroke: 2px #000000; text-stroke: 2px #000000; color: ' + data['Bottom-colour'] + '; line-height: ' + data['CopyrightBack-region'][3] + 'px">' +
                data['Bottom-format'] + data.Copyright + data['Bottom-formatEnd'] + '</div>';
        },
        'EncounterSetBack-portrait-clip': function(data) {
            if (data['EncounterSet-external-path'] + '' == '') {
                return '';
            }

            var content = '<img src="' + data['EncounterSet-external-path'] + '" width="' + data['EncounterSetBack-portrait-clip-region'][2] + '" height="' + data['EncounterSetBack-portrait-clip-region'][3] + '">';
            return content;
        },
        'NameBack': function(data) {
            if (data.NameBack + '' == '') {
                return '';
            }

            var rotate = '';
            if (data['NameBack-region'][3] > data['NameBack-region'][2] * 3) {
                rotate = '; width: 100%; line-height: ' + (data['NameBack-region'][2] - 2) + 'px; -webkit-transform: rotate(180deg); transform: rotate(180deg)';
            }

            var unique = '';
            if (data.UniqueBack + '') {
                unique = '<span style="font-size: ' + updateFontSize(data['Name-pointsize']) + 'em"><span style="font-family: Symbols">u</span> </span>';
            }

            var content = '<div style="text-align: center' + rotate + '"><span style="color: ' + data['Name-colour'] + '">' + unique + data.NameBack + '</span></div>';
            return content;
        },
        'OptionRightBack': function(data) {
            if (data.OptionRightBack + '' == '') {
                return '';
            }

            return '<div style="text-align: center; padding-top: 4px">' + data['OptionRight-format'] + data.OptionRightBack + data['OptionRight-formatEnd'] + '</div>';
        },
        'PageInBack': function(data) {
            if (parseInt(data.PageNumberBack) == 0) {
                return '';
            }

            return '<div style="text-align: right">' + data['PageIn-format'] + data['LRL-Page'] + ' ' + data.PageNumberBack + data['LRL-PageOf'] + data.PageTotalBack + data['PageIn-formatEnd'] + '</div>';
        },
        'PortraitBack-portrait-clip': function(data) {
            var content = '';
            if (fs.existsSync(generatedImagesFolderCheck + data.Id + '.B.jpg')) {
                content = '<img src="' + generatedImagesFolder + data.Id + '.B.jpg" width="100%" height="100%">';
            }
            return content;
        },
        'ProgressBack': function(data) {
            if (data.ProgressBack + '' == '') {
                return '';
            }

            return '<div style="text-align: center; color: #C46900; font-family: Vafthrudnir; font-size: 27px; width: ' + data['ProgressBack-region'][2] + 'px">' + data.ProgressBack + '</div>';
        },
        'SideBack': function(data) {
            if ((data.Side + '' == '') && (data.SideB + '' == '')) {
                return '';
            }

            return '<div style="text-align: center; padding-top: 2px">' + (data.Side || data.SideB) + '</div>';
        },
        'StageBack': function(data) {
            if ((data.Stage + '' == '') || (data.StageLetterBack + '' == '')) {
                return '';
            }

            return '<div style="text-align: center; color: #53B2C5; font-family: Vafthrudnir; width: ' + data['StageBack-region'][2] + 'px"><span style="vertical-align: middle; display: inline-block; font-size: 48px">' +
                data.Stage + '</span><span style="vertical-align: middle; display: inline-block; font-size: 24px; padding-bottom: 4px; padding-right: 4px">' + data.StageLetterBack + '</span></div>';
        },
        'StarBack': function(data) {
            if (parseInt(data.StarBack) == 0) {
                return '';
            }

            return '<div style="color: ' + data['Star-colour'] + '; line-height: ' + data['StarBack-region'][3] + 'px">' +
                data['Star-format'] + '&#10038;' + data['Star-formatEnd'] + '</div>';
        },
        'TypeBack': function(data) {
            if (data.Type + '' == '') {
                return '';
            }

            return '<div style="text-align: center">' + data.Type + '</div>';
        }
    };

    var data = settings.settings;
    for (let key in data) {
        if (data.hasOwnProperty(key)) {
            if ((data[key] == true) || (data[key] == false)) {
                continue;
            }

            if (key.match(/-region$/) || key.match(/-Body-shape$/)) {
                data[key] = updateRegion(key, data[key], data.TypeRenderer);
            }
            else {
                data[key] = convertTags(data[key]);
            }
        }
    }

    if (data['TraitOut-Body-region']) {
        data['Body-region'] = data['TraitOut-Body-region'];
    }

    if (data['TraitOut-Trait-region']) {
        data['Trait-region'] = data['TraitOut-Trait-region'];
    }

    if (data['Option-Body-shape']) {
        data['Sphere-Body-shape'] = data['Option-Body-shape'];
    }

    if (data['Adventure-region'] && (data.TypeRenderer == QUEST)) {
        data['AdventureBack-region'] = data['Adventure-region'];
    }

    if (data['Stage-region'] && (data.TypeRenderer == QUEST)) {
        data['StageBack-region'] = data['Stage-region'];
    }

    if (data['Progress-region'] && (data.TypeRenderer == QUEST)) {
        data['ProgressBack-region'] = data['Progress-region'];
    }

    if (data['OptionRight-region'] && (data.TypeRenderer == QUEST)) {
        data['OptionRightBack-region'] = data['OptionRight-region'];
    }

    if (data['OptionRightDecoration-region'] && (data.TypeRenderer == QUEST)) {
        data['OptionRightBackDecoration-region'] = data['OptionRightDecoration-region'];
    }

    if (data['EncounterSet-portrait-clip-region'] && (data.TypeRenderer == QUEST)) {
        data['EncounterSetBack-portrait-clip-region'] = data['EncounterSet-portrait-clip-region'];
    }

    if (data['Artist-region'] && data.DoubleSide && ([CONTRACT, QUEST].indexOf(data.TypeRenderer) > -1)) {
        data['ArtistBack-region'] = data['Artist-region'];
    }

    if (data['Copyright-region'] && data.DoubleSide && ([CONTRACT, QUEST].indexOf(data.TypeRenderer) > -1)) {
        data['CopyrightBack-region'] = data['Copyright-region'];
    }

    if (data['Collection-portrait-clip-region'] && data.DoubleSide && ([CONTRACT, QUEST].indexOf(data.TypeRenderer) > -1)) {
        data['CollectionBack-portrait-clip-region'] = data['Collection-portrait-clip-region'];
    }

    if (data['CollectionNumber-region'] && data.DoubleSide && ([CONTRACT, QUEST].indexOf(data.TypeRenderer) > -1)) {
        data['CollectionNumberBack-region'] = data['CollectionNumber-region'];
    }

    if (data['CollectionInfo-region'] && data.DoubleSide && ([CONTRACT, QUEST].indexOf(data.TypeRenderer) > -1)) {
        data['CollectionInfoBack-region'] = data['CollectionInfo-region'];
    }

    if (data['Star-region'] && data.DoubleSide && ([CONTRACT, QUEST].indexOf(data.TypeRenderer) > -1)) {
        data['StarBack-region'] = data['Star-region'];
    }

    if (data['PageIn-region'] && (data.TypeRenderer == RULES)) {
        data['PageInBack-region'] = data['PageIn-region'];
    }

    if (data['Side-region'] && data.DoubleSide && (data.TypeRenderer == CONTRACT)) {
        data['SideBack-region'] = data['Side-region'];
    }

    if (data['Type-region'] && data.DoubleSide && (data.TypeRenderer == CONTRACT)) {
        data['TypeBack-region'] = data['Type-region'];
    }
    else if (data['Type-region'] && (data.TypeRenderer == NIGHTMARE)) {
        data['TypeBack-region'] = data['Type-region'];
        data['Type-region'] = null;
    }

    if ((data.Progress + '' != '') && (data.TypeRenderer == QUEST)) {
        data.ProgressBack = data.Progress;
        data.Progress = '';
    }

    var template = data.Template;
    if ((data.TypeRenderer == CAMPAIGN) && (template == 'Standard')) {
        template = '';
    }

    var additionalEncounterSets = '';
    if ((data.TypeRenderer == QUEST) && (parseInt(data.AdditionalEncounterSetsLength) > 0)) {
        additionalEncounterSets = data.AdditionalEncounterSetsLength;
    }

    var htmlTemplate = fs.readFileSync('template.html') + '';

    var containerNames = [];
    for (let key in containerRules) {
        if (containerRules.hasOwnProperty(key) && (key in containerFontSize)) {
            containerNames.push(key);
        }
    }
    if (containerNames.length > 0) {
        containerNames = "'" + containerNames.join("', '") + "'";
    }
    else {
        containerNames = '';
    }

    var containers = [];
    for (let key in containerRules) {
        if (containerRules.hasOwnProperty(key)) {
            if (data[key + '-region'] && (containerRules[key](data))) {
                let shapeDiv = '';
                if ((key == 'Body') && data.BodyShapeNeededRenderer && data['Sphere-Body-shape']) {
                    shapeDiv = '<div id="BodyShape"><span></span></div>';
                }

                let content = '';
                if (key == 'Portrait-portrait-clip') {
                    content = '<div id="' + key + '" style="position: absolute; left: ' + data[key + '-region'][0] + 'px; top: ' + data[key + '-region'][1] + 'px; width: ' +
                        data[key + '-region'][2] + 'px; height: ' + data[key + '-region'][3] + 'px; overflow-x: hidden; overflow-y: hidden; z-index: -2">' + containerRules[key](data) + '</div>';
                }
                else if (['Attack', 'Collection-portrait-clip', 'Defense', 'Difficulty', 'EncounterSet-portrait-clip', 'EncounterSet1-portrait-clip',
                          'EncounterSet2-portrait-clip', 'EncounterSet3-portrait-clip', 'EncounterSet4-portrait-clip', 'EncounterSet5-portrait-clip',
                          'EncounterSet6-portrait-clip', 'Engagement', 'HitPoints', 'Progress', 'ResourceCost', 'Stage', 'Threat', 'ThreatCost', 'Willpower'].indexOf(key) > -1) {
                    content = '<div id="' + key + '" style="position: absolute; left: ' + data[key + '-region'][0] + 'px; top: ' + data[key + '-region'][1] + 'px; width: ' +
                        data[key + '-region'][2] + 'px; height: ' + data[key + '-region'][3] + 'px; overflow-x: visible; overflow-y: visible">' + containerRules[key](data) + '</div>';
                }
                else if (key == 'OptionLeft') {
                    content = '<div id="' + key + '" style="position: absolute; left: ' + data[key + '-region'][0] + 'px; top: ' + data[key + '-region'][1] + 'px; width: ' +
                        data[key + '-region'][2] + 'px; height: ' + data[key + '-region'][3] + 'px; overflow-x: visible; overflow-y: auto; font-size: ' + containerFontSize[key] + 'px; text-align: center">' +
                        shapeDiv + containerRules[key](data) + '</div>';
                }
                else if (key == 'OptionRight') {
                    content = '<div id="' + key + '" style="position: absolute; left: ' + data[key + '-region'][0] + 'px; top: ' + data[key + '-region'][1] + 'px; width: ' +
                        data[key + '-region'][2] + 'px; height: ' + data[key + '-region'][3] + 'px; overflow-x: visible; overflow-y: auto; z-index: 1; font-size: ' + containerFontSize[key] + 'px">' +
                        shapeDiv + containerRules[key](data) + '</div>';
                    content += '<div style="position: absolute; left: ' + data[key + 'Decoration-region'][0] + 'px; top: ' + data[key + 'Decoration-region'][1] + 'px; width: ' +
                        data[key + 'Decoration-region'][2] + 'px; height: ' + data[key + 'Decoration-region'][3] + 'px; overflow-x: visible; overflow-y: visible">' +
                        '<img src="' + imagesFolder + 'victorydecoration.png" width="82" height="20"></div>';
                }
                else if (data[key + '-region'][3] > data[key + '-region'][2] * 3) {
                    content = '<div id="' + key + '" style="position: absolute; left: ' + (parseInt(data[key + '-region'][0]) + parseInt(data[key + '-region'][2])) + 'px; top: ' + data[key + '-region'][1] + 'px; width: ' +
                        data[key + '-region'][3] + 'px; height: ' + data[key + '-region'][2] + 'px; overflow-x: visible; overflow-y: auto; font-size: ' + containerFontSize[key] + 'px; ' +
                        '-webkit-transform: rotate(90deg); transform: rotate(90deg); -webkit-transform-origin: 0 0 0; transform-origin: 0 0 0">' + shapeDiv + containerRules[key](data) + '</div>';
                }
                else {
                    content = '<div id="' + key + '" style="position: absolute; left: ' + data[key + '-region'][0] + 'px; top: ' + data[key + '-region'][1] + 'px; width: ' +
                        data[key + '-region'][2] + 'px; height: ' + data[key + '-region'][3] + 'px; overflow-x: visible; overflow-y: auto; font-size: ' + containerFontSize[key] + 'px">' +
                        shapeDiv + containerRules[key](data) + '</div>';
                }

                containers.push(content);
            }
        }
    }

    var shapeCSS = '';
    if (data.BodyShapeNeededRenderer && data['Sphere-Body-shape'] && data['Body-region']) {
        let shapeWidth = 0;
        let shapeAlignment = 'left';
        let shapeOppositeAlignment = 'right';
        if (data['Sphere-Body-shape'][2] > 0) {
            shapeWidth = data['Sphere-Body-shape'][2];
        }
        else if (data['Sphere-Body-shape'][3] > 0) {
            shapeWidth = data['Sphere-Body-shape'][3];
            shapeAlignment = 'right';
        }

        let shapeHeight = data['Body-region'][1] + data['Body-region'][3] - data['Sphere-Body-shape'][1] + 12;
        let shapeTop = data['Body-region'][3] - shapeHeight;
        shapeCSS = '#BodyShape:before {\n' +
            '    content: "";\n' +
            '    display: block;\n' +
            '    float: ' + shapeOppositeAlignment + ';\n' +
            '    height: ' + shapeTop + 'px;\n' +
            '}\n' +
            '#BodyShape span {\n' +
            '    float: ' + shapeAlignment + ';\n' +
            '    clear: both;\n' +
            '    width: ' + shapeWidth + 'px;\n' +
            '    height: ' + shapeHeight + 'px;\n' +
            '}';
    }

    var background = (data.TypeRenderer + template + additionalEncounterSets).replace(/ /g, '');
    var prefix = 'portrait.';
    var width = 429;
    var height = 600;
    if (landscapeTypes.indexOf(data.TypeRenderer) > -1) {
        prefix = 'landscape.';
        width = 600;
        height = 429;
    }

    var suffix = '';
    if (data.SuffixRenderer == '-2') {
        suffix = '.B';
    }

    var html = htmlTemplate.replace('{{ TEMPLATE_BACKGROUND }}', background);
    html = html.replace('{{ TEMPLATE_WIDTH }}', width);
    html = html.replace('{{ TEMPLATE_HEIGHT }}', height);
    html = html.replace('{{ SHAPE_CSS }}', shapeCSS);
    html = html.replace('{{ CONTAINER_NAMES }}', containerNames);
    html = html.replace('{{ CONTAINERS }}', containers.join('\n'));
    fs.writeFileSync('Output/' + prefix + data.Id + suffix + '.html', html);

    if (data.DoubleSide) {
        var containerNamesBack = [];
        for (let key in containerRulesBack) {
            if (containerRulesBack.hasOwnProperty(key) && (key in containerFontSize)) {
                containerNamesBack.push(key);
            }
        }
        if (containerNamesBack.length > 0) {
            containerNamesBack = "'" + containerNamesBack.join("', '") + "'";
        }
        else {
            containerNamesBack = '';
        }

        var containersBack = [];
        for (let key in containerRulesBack) {
            if (containerRulesBack.hasOwnProperty(key)) {
                if (data[key + '-region'] && (containerRulesBack[key](data))) {
                    let shapeDiv = '';
                    if ((key == 'BodyBack') && data.BodyShapeNeededBackRenderer && data['Sphere-Body-shape']) {
                        shapeDiv = '<div id="BodyShape"><span></span></div>';
                    }

                    let content = '';
                    if (key == 'PortraitBack-portrait-clip') {
                        content = '<div id="' + key + '" style="position: absolute; left: ' + data[key + '-region'][0] + 'px; top: ' + data[key + '-region'][1] + 'px; width: ' +
                            data[key + '-region'][2] + 'px; height: ' + data[key + '-region'][3] + 'px; overflow-x: hidden; overflow-y: hidden; z-index: -2">' + containerRulesBack[key](data) + '</div>';
                    }
                    else if (['CollectionBack-portrait-clip', 'EncounterSetBack-portrait-clip', 'ProgressBack', 'StageBack'].indexOf(key) > -1) {
                        content = '<div id="' + key + '" style="position: absolute; left: ' + data[key + '-region'][0] + 'px; top: ' + data[key + '-region'][1] + 'px; width: ' +
                            data[key + '-region'][2] + 'px; height: ' + data[key + '-region'][3] + 'px; overflow-x: visible; overflow-y: visible">' + containerRulesBack[key](data) + '</div>';
                    }
                    else if (key == 'OptionRightBack') {
                        content = '<div id="' + key + '" style="position: absolute; left: ' + data[key + '-region'][0] + 'px; top: ' + data[key + '-region'][1] + 'px; width: ' +
                            data[key + '-region'][2] + 'px; height: ' + data[key + '-region'][3] + 'px; overflow-x: visible; overflow-y: auto; z-index: 1; font-size: ' + containerFontSize[key] + 'px">' +
                            shapeDiv + containerRulesBack[key](data) + '</div>';
                        content += '<div style="position: absolute; left: ' + data[key + 'Decoration-region'][0] + 'px; top: ' + data[key + 'Decoration-region'][1] + 'px; width: ' +
                            data[key + 'Decoration-region'][2] + 'px; height: ' + data[key + 'Decoration-region'][3] + 'px; overflow-x: visible; overflow-y: visible">' +
                            '<img src="' + imagesFolder + 'victorydecoration.png" width="82" height="20"></div>';
                    }
                    else if (data[key + '-region'][3] > data[key + '-region'][2] * 3) {
                        content = '<div id="' + key + '" style="position: absolute; left: ' + (parseInt(data[key + '-region'][0]) + parseInt(data[key + '-region'][2])) + 'px; top: ' + data[key + '-region'][1] + 'px; width: ' +
                            data[key + '-region'][3] + 'px; height: ' + data[key + '-region'][2] + 'px; overflow-x: visible; overflow-y: auto; font-size: ' + containerFontSize[key] + 'px; ' +
                            '-webkit-transform: rotate(90deg); transform: rotate(90deg); -webkit-transform-origin: 0 0 0; transform-origin: 0 0 0">' + shapeDiv + containerRulesBack[key](data) + '</div>';
                    }
                    else {
                        content = '<div id="' + key + '" style="position: absolute; left: ' + data[key + '-region'][0] + 'px; top: ' + data[key + '-region'][1] + 'px; width: ' +
                            data[key + '-region'][2] + 'px; height: ' + data[key + '-region'][3] + 'px; overflow-x: visible; overflow-y: auto; font-size: ' + containerFontSize[key] + 'px">' +
                            shapeDiv + containerRulesBack[key](data) + '</div>';
                    }

                    containersBack.push(content);
                }
            }
        }

        shapeCSS = '';
        if (data.BodyShapeNeededBackRenderer && data['Sphere-Body-shape'] && data['BodyBack-region']) {
            let shapeWidth = 0;
            let shapeAlignment = 'left';
            let shapeOppositeAlignment = 'right';
            if (data['Sphere-Body-shape'][2] > 0) {
                shapeWidth = data['Sphere-Body-shape'][2];
            }
            else if (data['Sphere-Body-shape'][3] > 0) {
                shapeWidth = data['Sphere-Body-shape'][3];
                shapeAlignment = 'right';
            }

            let shapeHeight = data['BodyBack-region'][1] + data['BodyBack-region'][3] - data['Sphere-Body-shape'][1] + 12;
            let shapeTop = data['BodyBack-region'][3] - shapeHeight;
            shapeCSS = '#BodyShape:before {\n' +
                '    content: "";\n' +
                '    display: block;\n' +
                '    float: ' + shapeOppositeAlignment + ';\n' +
                '    height: ' + shapeTop + 'px;\n' +
                '}\n' +
                '#BodyShape span {\n' +
                '    float: ' + shapeAlignment + ';\n' +
                '    clear: both;\n' +
                '    width: ' + shapeWidth + 'px;\n' +
                '    height: ' + shapeHeight + 'px;\n' +
                '}';
        }

        background = (data.TypeRenderer + template + 'Back').replace(/ /g, '');
        prefix = 'portrait.';
        width = 429;
        height = 600;
        if (landscapeTypes.indexOf(data.TypeRenderer) > -1) {
            prefix = 'landscape.';
            width = 600;
            height = 429;
        }

        suffix = '.B';

        html = htmlTemplate.replace('{{ TEMPLATE_BACKGROUND }}', background);
        html = html.replace('{{ TEMPLATE_WIDTH }}', width);
        html = html.replace('{{ TEMPLATE_HEIGHT }}', height);
        html = html.replace('{{ SHAPE_CSS }}', shapeCSS);
        html = html.replace('{{ CONTAINER_NAMES }}', containerNamesBack);
        html = html.replace('{{ CONTAINERS }}', containersBack.join('\n'));
        fs.writeFileSync('Output/' + prefix + data.Id + suffix + '.html', html);
    }
}

function mainRenderer() {
    var sets = process.argv[2].split(',');
    var icons = [];
    var files = fs.readdirSync('Icons');
    files.forEach(function(file, _) {
        if (file.match(/\.png$/)) {
            icons.push(file.replace(/\.png$/, ''));
        }
    });

    for (let i = 0; i < sets.length; i++) {
        let setID = sets[i];
        if (!setID) {
            continue;
        }

        let path = xmlFolder + setID + '.English.xml';
        let doc = new DocumentBuilderAdapter(path);
        run('renderer', doc, setID, 'English', icons, getCardObjectsRenderer, saveResultRenderer, null);
    }
}

function main() {
    if (process.argv.length < 3) {
        console.error('Insufficient script arguments');
        return;
    }

    mainRenderer();
}

main();
