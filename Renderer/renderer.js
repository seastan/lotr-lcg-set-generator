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

function iterateKeys(dict, name, res) {
    for (let key in dict) {
        if (dict.hasOwnProperty(key) && (key != '#text') && !key.match(/^@_/)) {
            let element = dict[key];
            if (key == name) {
                if (element instanceof Array) {
                    for (let i = 0; i < element.length; i++ ) {
                        res.push(new ElementAdapter(element[i]));
                    }
                }
                else {
                    res.push(new ElementAdapter(element));
                }
            }
            if (element instanceof Array) {
                for (let i = 0; i < element.length; i++ ) {
                    iterateKeys(element[i], name, res);
                }
            }
            else {
                iterateKeys(element, name, res);
            }
        }
    }
}

function ElementAdapter(dict) {
    this.json = dict;

    this.print = function() {
        return JSON.stringify(this.json, null, 2);
    };

    this.getAttribute = function(name) {
        return this.json['@_' + name] + '';
    };

    this.getElementsByTagName = function(name) {
        var res = [];
        iterateKeys(this.json, name, res);
        return new ElementListAdapter(res);
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
                return new ElementAdapter(this.json[key]);
            }
        }
    };

    this.getElementsByTagName = function(name) {
        var res = [];
        iterateKeys(this.json, name, res);
        return new ElementListAdapter(res);
    };
}

function getCardObjectsRenderer(_) {
    var settings = new RendererSettings();
    return [null, settings];
}

function saveResultRenderer(settings, setID, _1, _2, _3, _4, _5, _6, _7) {
    // T.B.D. save HTML file
    console.log(settings.settings);
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
