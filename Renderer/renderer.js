const fs = require('fs');
eval(fs.readFileSync('../Frogmorton/common.js') + '');

function RendererSettings() {
	this.settings = {};

	this.set = function(key, value) {
		this.settings[key] = value;
	};

	this.get = function(key) {
		return this.settings[key];
	};
}

/*
var docElement = doc.getDocumentElement();
var name = docElement.getAttribute('name');
var nList = doc.getElementsByTagName('card');
nList.getLength()
let nNode = nList.item(i);
nNode.getAttribute('skip')
let propList = nNode.getElementsByTagName('property');
propList.getLength()
let nProp = propList.item(j);
!nProp.getParentNode().isSameNode(nNode)
if (nProp)
nProp.getAttribute('name')
*/

function getCardObjectsRenderer(_1) {
	var settings = new RendererSettings();
	return [null, settings];
}

function saveResultRenderer(settings, setID, _1, _2, _3, _4, _5, _6, _7) {
	// T.B.D. save HTML file
}

function mainRenderer() {
	var setID = process.argv[2];
        var xmlPath = '../setEons/' + setID + '.English.xml';

	var icons = [];
	// T.B.D. initialize icons list

	var doc;
	// T.B.D. initialize javax.xml.parsers.DocumentBuilderFactory.newInstance().newDocumentBuilder().parse() object



//	run('renderer', doc, setID, 'English', icons, getCardObjectsRenderer, saveResultRenderer, null);
}

//const { XMLParser, XMLBuilder, XMLValidator} = require('fast-xml-parser');
//var parser = new XMLParser();
//console.log(parser);

function main() {
    if (process.argv.length < 3) {
        console.log('Insufficient script arguments');
        return;
    }

    mainRenderer();
}

main()
