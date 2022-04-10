function RendererSettings() {
	this.settings = {};

	this.set = function(key, value) {
		this.settings[key] = value;
	};

	this.get = function(key) {
		return this.settings[key];
	};
}

function getCardObjectsRenderer(cardType) {
	var settings = new RendererSettings();
	return [null, settings];
}

function saveResultRenderer(settings, setID, _1, _2, _3, _4, _5, _6, _7) {
	// T.B.D. save HTML file
}

function mainRenderer() {
	var setID;
	// T.B.D. initialize set ID

	var doc;
	// T.B.D. initialize javax.xml.parsers.DocumentBuilderFactory.newInstance().newDocumentBuilder().parse() object

	var icons = [];
	// T.B.D. initialize icons list

	run('renderer', doc, setID, 'English', icons, getCardObjectsRenderer, saveResultRenderer, null);
}