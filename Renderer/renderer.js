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
                for (let i = 0; i < child.length; i++ ) {
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
        res = '';
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
        res = '';
    }

    return res;
}

function convertTags(value) {
    value += '';
    value = value.replace(/<tracking -0.005/g, '');
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

//    value = value.replace(//g, '');
    return value;
}

function saveResultRenderer(settings, setID, _1, _2, _3, _4, _5, _6, _7) {
    var data = settings.settings;
    for (let key in data) {
        if (data.hasOwnProperty(key)) {
            data[key] = convertTags(data[key]);
        }
    }
    console.log(data);
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

    for (let i = 0; i < sets.length; i++ ) {
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
