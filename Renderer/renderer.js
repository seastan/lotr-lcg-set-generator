const fs = require('fs');
const {XMLParser} = require('fast-xml-parser');
eval(fs.readFileSync('../Frogmorton/common.js') + '');

const iconsFolder = 'Icons/';
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
        return this.json['@_' + name] + '';
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
        ignoreAttributes: false
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
    if (regions.length != 4) {
        return value;
    }

    for (let i = 0; i < regions.length; i++) {
        regions[i] = Math.round(regions[i] * 2 / 1.75);
    }

    return regions;
}

function updateFontSize(match, p1, offset, string) {
    return '<span style="font-size: ' + round((p1 * 1.3333 / 1.75) / 14, 4) + 'em">';
}

function updateImageWidth(match, p1, p2, offset, string) {
    var width;
    if (p2.match(/pt$/)) {
        width = Math.round(p2.replace(/pt/g, '') * 1.3333 / 1.75);
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
        res = '<img src="Images/empty.png" width="1" height="1">';
    }

    return res;
}

function updateImageWidthHeight(match, p1, p2, p3, offset, string) {
    var width;
    if (p2.match(/pt$/)) {
        width = Math.round(p2.replace(/pt/g, '') * 1.3333 / 1.75);
    }
    else if (p2.match(/in$/)) {
        width = Math.round(p2.replace(/in/g, '') * 300 / 1.75);
    }
    else {
        width = Math.round(p2.replace(/cm/g, '') * 0.393701 * 300 / 1.75);
    }

    var height;
    if (p3.match(/pt$/)) {
        height = Math.round(p3.replace(/pt/g, '') * 1.3333 / 1.75);
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
        res = '<img src="Images/empty.png" width="1" height="1">';
    }

    return res;
}

function convertTags(value) {
    value += '';
    value.replace(/\t/g, ' ');
    value.replace(/\n/g, '<br>');
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
    value = value.replace(/<tracking -0.005>/g, '');
    value = value.replace(/<family "([^"]+)">/g, '<span style="font-family: $1">');
    value = value.replace(/<\/family>/g, '</span>');
    value = value.replace(/<\/size><size 0\.01><\/i>(?:\u00a0| )<\/size><size [0-9.]+>/g, '</i>');
    value = value.replace(/<size ([0-9.]+)>/g, updateFontSize);
    value = value.replace(/<\/size>/g, '</span>');
    value = value.replace(/<color ([^>]+)>/g, '<span style="color: $1">');
    value = value.replace(/<\/color>/g, '</span>');
    value = value.replace(/<lt>/g, '&lt;');
    value = value.replace(/<gt>/g, '&gt;');
    value = value.replace(/res:\/\/TheLordOfTheRingsLCG\/image\/empty1x1\.png/g, 'Images/empty.png');
    value = value.replace(/res:\/\/TheLordOfTheRingsLCG\/image\/ShadowSeparator\.png/g, 'Images/shadow.png');
    value = value.replace(/project:imagesCustom\/[0-9a-f\-]+_Do-Not-Read-the-Following\.png/g, 'Images/donotread.png');
    value = value.replace(/project:imagesCustom/g, 'Images');
    value = value.replace(/project:imagesIcons/g, 'Icons');
    value = value.replace(/<image ([^ >]+)>/g, '<img src="$1">');
    value = value.replace(/<image ([^ >]+) ([^ >]+)>/g, updateImageWidth);
    value = value.replace(/<image ([^ >]+) ([^ >]+) ([^ >]+)>/g, updateImageWidthHeight);
    value = value.replace(/<left>/g, '<div style="text-align: left">');
    value = value.replace(/<center>/g, '<div style="text-align: center">');
    value = value.replace(/<right>/g, '<div style="text-align: right">');
    return value;
}

function saveResultRenderer(settings, _1, _2, _3, _4, _5, _6, _7, _8) {
    var containerRules = {
        'body': function(data) {
            return '';
        },
        'name': function(data) {
            return '';
        },
        'type': function(data) {
            return '';
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
            if (key.match(/-region$/)) {
                data[key] = updateRegion(data[key]);
            }
            else {
                data[key] = convertTags(data[key]);
            }
        }
    }
//    console.log(res);

    var template = data.Template;
    if ((data.TypeRenderer == 'Campaign') && (template == 'Standard')) {
        template = '';
    }

    var additionalEncounterSets = '';
    if ((data.TypeRenderer == 'Quest') && (data.AdditionalEncounterSetsLength + 0 > 0)) {
        additionalEncounterSets = data.AdditionalEncounterSetsLength;
    }

    var background = (data.TypeRenderer + template + additionalEncounterSets).replace(/ /g, '');
    var html = fs.readFileSync('template.html') + '';
    html = html.replace('{{ BACKGROUND }}', background);
    html = html.replace('{{ CONTAINER_NAMES }}', containerNames);

    fs.writeFileSync('Output/' + data.IdRenderer + '.html', html);

    if ((doubleSideTypes.indexOf(data.TypeRenderer) > -1) &&
        ((data.TypeRenderer != 'Contract') || (template == 'DoubleSided'))) {
        background = background.replace(/[1-9]?$/, 'Back');
        html = fs.readFileSync('template.html') + '';
        html = html.replace('{{ BACKGROUND }}', background);
        html = html.replace('{{ CONTAINER_NAMES }}', containerNames);

        fs.writeFileSync('Output/' + data.IdRenderer + '.B.html', html);
    }
}

function mainRenderer() {
    var sets = process.argv[2].split(',');
    var icons = [];
    var files = fs.readdirSync(iconsFolder);
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
