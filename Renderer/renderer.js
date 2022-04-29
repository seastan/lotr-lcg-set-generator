const fs = require('fs');
const he = require('he');
const {XMLParser} = require('fast-xml-parser');
eval(fs.readFileSync('../Frogmorton/common.js') + '');

const iconsFolder = '../Icons/';
const imagesFolder = '../Images/';
const xmlFolder = '../setEons/';

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

function updateRegion(value) {
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
    value = value.replace(/project:imagesCustom\/[0-9a-f\-]+_Do-Not-Read-the-Following\.png/g, imagesFolder + 'donotread.png');
    value = value.replace(/project:imagesCustom\/[0-9a-f\-]+_Text-Divider-Black\.png/g, imagesFolder + 'textdividerblack.png');
    value = value.replace(/project:imagesCustom\//g, imagesFolder);
    value = value.replace(/project:imagesIcons\//g, iconsFolder);
    value = value.replace(/<image ([^ >]+)>/g, '<img src="$1">');
    value = value.replace(/<image ([^ >]+) ([^ >]+)>/g, updateImageWidthReplacer);
    value = value.replace(/<image ([^ >]+) ([^ >]+) ([^ >]+)>/g, updateImageWidthHeightReplacer);
    value = value.replace(/<img src="([^"]+?\/shadow\.png)"[^>]*>/g, '<img src="$1" width="266" height="21">');
    value = value.replace(/<img src="([^"]+?\/donotread\.png)"[^>]*>/g, '<img src="$1" width="249" height="64">');
    value = value.replace(/<img src="([^"]+?\/textdividerblack\.png)"[^>]*>/g, '<img src="$1" width="343" height="5">');
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
    var containerFontSize = {
        'Body': 14,
        'Name': 12,
        'Type': 12
    };
    var containerRules = {
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
        'Type': function(data) {
            if (data.Type + '' == '') {
                return '';
            }

            return '<div style="text-align: center">' + data.Type + '</div>';
        }};

    var containerNames = [];
    for (let key in containerRules) {
        if (containerRules.hasOwnProperty(key)) {
            containerNames.push(key);
        }
    }
    if (containerNames.length > 0) {
        containerNames = "'" + containerNames.join("', '") + "'";
    }
    else {
        containerNames = '';
    }

    var data = settings.settings;
    for (let key in data) {
        if (data.hasOwnProperty(key)) {
            if (key.match(/-region$/) || key.match(/-Body-shape$/)) {
                data[key] = updateRegion(data[key]);
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

    // console.log(data);
    var template = data.Template;
    if ((data.TypeRenderer == 'Campaign') && (template == 'Standard')) {
        template = '';
    }

    var additionalEncounterSets = '';
    if ((data.TypeRenderer == 'Quest') && (parseInt(data.AdditionalEncounterSetsLength) > 0)) {
        additionalEncounterSets = data.AdditionalEncounterSetsLength;
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
                if (data[key + '-region'][3] > data[key + '-region'][2] * 3) {
                    content = '<div id="' + key + '" style="position: absolute; left: ' + (parseInt(data[key + '-region'][0]) + parseInt(data[key + '-region'][2])) + 'px; top: ' + data[key + '-region'][1] + 'px; width: ' +
                        data[key + '-region'][3] + 'px; height: ' + data[key + '-region'][2] + 'px; overflow-x: visible; overflow-y: auto; font-size: ' + containerFontSize[key] + 'px; ' +
                        '-webkit-transform: rotate(90deg); transform: rotate(90deg); -webkit-transform-origin: 0 0 0; transform-origin: 0 0 0">' + shapeDiv + containerRules[key](data) + '</div>';
                }
                else {
                    content = '<div id="' + key + '" style="position: absolute; left: ' + data[key + '-region'][0] + 'px; top: ' + data[key + '-region'][1] + 'px; width: ' +
                    data[key + '-region'][2] + 'px; height: ' + data[key + '-region'][3] + 'px; overflow-x: visible; overflow-y: auto; font-size: ' + containerFontSize[key] + 'px">' + shapeDiv + containerRules[key](data) + '</div>';
                }

                containers.push(content);
            }
        }
    }

    var shapeCSS = '';
    if (data.BodyShapeNeededRenderer && data['Sphere-Body-shape'] && data['Body-region']) {
        var shapeWidth = 0;
        var shapeAlignment = 'left';
        var shapeOppositeAlignment = 'right';
        if (data['Sphere-Body-shape'][2] > 0) {
            shapeWidth = data['Sphere-Body-shape'][2];
        }
        else if (data['Sphere-Body-shape'][3] > 0) {
            shapeWidth = data['Sphere-Body-shape'][3];
            shapeAlignment = 'right';
        }

        var shapeHeight = data['Body-region'][1] + data['Body-region'][3] - data['Sphere-Body-shape'][1] + 12;
        var shapeTop = data['Body-region'][3] - shapeHeight;
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
    var html = fs.readFileSync('template.html') + '';
    var prefix = 'portrait.';
    if (landscapeTypes.indexOf(data.TypeRenderer) > -1) {
        prefix = 'landscape.';
    }

    var suffix = '';
    if (data.SuffixRenderer == '-2') {
        suffix = '.B';
    }

    html = html.replace('{{ BACKGROUND }}', background);
    html = html.replace('{{ CONTAINER_NAMES }}', containerNames);
    html = html.replace('{{ SHAPE_CSS }}', shapeCSS);
    html = html.replace('{{ CONTAINERS }}', containers.join('\n'));
    fs.writeFileSync('Output/' + prefix + data.IdRenderer + suffix + '.html', html);

    if ((doubleSideTypes.indexOf(data.TypeRenderer) > -1) &&
        ((data.TypeRenderer != 'Contract') || (template == 'DoubleSided'))) {
        background = background.replace(/[1-9]?$/, 'Back');
        html = fs.readFileSync('template.html') + '';
        html = html.replace('{{ BACKGROUND }}', background);
        html = html.replace('{{ CONTAINER_NAMES }}', containerNames);
        // T.B.D.
        fs.writeFileSync('Output/' + prefix + data.IdRenderer + '.B.html', html);
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
