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
