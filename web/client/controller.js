/* Copyright 2016-2023 Peppy Player peppy.player@gmail.com
 
This file is part of Peppy Player.
 
Peppy Player is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
Peppy Player is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with Peppy Player. If not, see <http://www.gnu.org/licenses/>.
*/

DEBUG = false; // global

if(!DEBUG || typeof(console.log) == 'undefined') {
   console.log = function() {};
}

/**
* Send data to web server via WebSocket
*
* @param data - command in Json format
*/
function sendDataToServer(data) {
	if(webSocket == null) {
		console.log("webSocket closed");
		return;
	}
	d = JSON.stringify(data);
	console.log("sending to server: " + d);
	webSocket.send(d);
	console.log("sent");
}

/**
* Dispatch the message from web server to corresponding handler
*
* @param msg - the message received from web server
*/
function dispatchMessageFromServer(msg) {
	console.log("received message from server");
	
	var d = {}
	try {
		d = JSON.parse(msg.data);
	} catch(e) {
		console.log("error parsing message from server");
		console.log(msg.data);
		return;
	}
	
	var c = d["command"];
	var comps = d["components"];
	
	if(isScreensaverRunning() && c != "stop_screensaver" && c !== "vumeter") {
		return;
	}

	console.log("command: " + c);
	
	if(c == "update_screen" || c== "update_screensaver") {
		updateScreen(comps);
	}
	else if(c == "update_element") {
		updateComponents(comps);
	}
	else if(c == "update_station_title" || c == "update_file_player_title") {
		updateTitleGroup("screen_title", comps); 
	}
	else if(c == "update_station_menu") {
		updateGroup("screen_menu", comps);
	}
	else if(c == "update_menu") {
		updateScreen(comps);
	}
	else if(c == "remove_element") {
		removeComponents(comps);
	}
	else if(c == "start_screensaver") {
		stopCurrentTrackTimer();
		startScreensaver();
	}
	else if(c == "stop_screensaver") {
		stopScreensaver();
	}
	else if(c == "stop_timer") {		
		stopTimer();
	}
	else if(c == "vumeter") {
		updateGradient(d);
	}
}

/**
 * Update VU Meter screensaver gradient
 *
 * @param data
 */
function updateGradient(data) {
	let gradientOverlay = getGradientOverlay();
	if (gradientOverlay === undefined) {
		return;
	}
	gradientOverlay.leftColor.setAttribute('stop-color', leftColors[parseInt(data["left"])]);
	gradientOverlay.rightColor.setAttribute('stop-color', rightColors[parseInt(data["right"])]);
	document.body.style.background = "linear-gradient(to right," + bgrLeftColors[parseInt(data["left"])] + "," + bgrRightColors[parseInt(data["right"])] + ")";
}

/**
* Start screensaver mode by adding dark overlay
*/
function startScreensaver() {
	console.log("starting screensaver");
	var panel = document.getElementById('panel');
	var w = panel.getAttribute("width");
	var h = panel.getAttribute("height");
	var overlay = createOverlay(0, 0, w, h);
	panel.appendChild(overlay);
	console.log("screensaver started");
}

/**
 * Check that screensaver is running
 * 
 * @returns {Boolean} true - running, false - not running
 */
function isScreensaverRunning() {
	var overlay = document.getElementById('overlay');
	return overlay != null;
}

/**
* Stop screensaver mode by removing dark overlay
*/
function stopScreensaver() {
	console.log("stopping screensaver");
	var panel = document.getElementById('panel');
	var overlay = document.getElementById('overlay');
	if(overlay != null) {
		panel.removeChild(overlay);
	}
	console.log("screensaver stopped");
	defs = null;
	initializeWebUi();
}

/**
* Remove components specified by their IDs
* 
* @param ids - the list of component ids to remove
*/
function removeComponents(ids) {
	var panel = document.getElementById('panel');
	
	console.log("removing components");
	
	for (var i=0; i < ids.length; i++) {
		var id = ids[i];
		var element = document.getElementById(id);
		if(element != null) {
			panel.removeChild(element);
			console.log("removed component: " + id);
		}
	}
	
	console.log("components removed");
}

/**
* Update screen by new components
*
* @param components - the list of new components
* @param options - additional options
*/
function updateScreen(components) {
	console.log("start updating screen");
	
	var screen = document.getElementById('screen');
	var panel = document.getElementById('panel');
	var isNewScreen = false;
	
	for (var i=0; i < components.length; i++) {
		var d = components[i];
		var type = d.type;
		
		if(d == null) {
			continue;
		}
		
		if(type == "screen") {
			handleBackground(d);
			if(screen == null) {
				screen = createScreen(d.name);
				isNewScreen = true;
			}
		} else if(type == "panel") {
			if(panel != null) {
				screen.removeChild(panel);
			}
			panel = createPanel(d.name, d.w, d.h, d.fgr, d.bgr, d.bgr_type);
			screen.appendChild(panel);			
		} else if(type == "stream_player") {
			var p = document.getElementById("stream_player");
			if(p == null) {
				p = createComponent(d);
				document.body.appendChild(p);
			}
		} else {
			var comp = createComponent(d);
			if(comp) {
				panel.appendChild(comp);
			}
		}
	}
	
	if(isNewScreen) {
		document.body.appendChild(screen);
	}

	console.log("screen updated");
}

/**
 * Create/Update background image/color
 * 
 * @param d - screen component 
 */
function handleBackground(d) {
	var image = d.original_image_filename;
	if (image) {
		document.body.style.background = d.bgr_base_color;
		var blur = d.bgr_blur;
		var opacity = d.bgr_opacity;
		var bgrImageDiv = document.getElementById("page.bgr.image");
		if(bgrImageDiv) {
			currentImage = bgrImageDiv.style.backgroundImage;
			newImage = "url(\"" + image + "\")";
			if(currentImage !== newImage) {
				updateBackground(bgrImageDiv, image, blur, opacity);
			}
		} else {
			createBackground(image, blur, opacity);
		}
	} else {
		document.body.style.background = d.bgr;
	}
}

/**
* Update components
*
* @param components - the list of new components
*/
function updateComponents(components) {
	console.log("updating components");
	
	for (var i=0; i < components.length; i++) {
		var d = components[i];
		if(d == null) {
			continue;
		}
		
		if(d.name === "stream_player") {
			update_stream_player(d);
			continue;
		}
		
		var element = document.getElementById(d.name);
		var comp = createComponent(d);
		
		if(element != null) {
			element.parentElement.replaceChild(comp, element);
		}
		else {
			var panel = document.getElementById('panel');
			panel.appendChild(comp);
		}
	}
	
	console.log("components updated");
}

/**
* Update stream player
*
* @param d - stream player parameters
*/
function update_stream_player(d) {
	p = document.getElementById(d.name);
	if(p == null) {
		return;
	}		
	v = d.volume/100;
	if(p.volume != v) {
		p.volume = v;
	}
	if(p.muted != d.mute) {
		p.muted = d.mute;
	}
	if(p.paused != d.paused) {
		p.paused = d.paused;
	}
}

/**
* Update SVG group of components
*
* @param name - the group name
* @param components -  the list of new components
*/
function updateGroup(name, components) {
	var panel = document.getElementById('panel');
	var oldGroup = document.getElementById(name);
	if(oldGroup) {
		console.log("updating group");
		var newGroup = createGroup(name, components);
		panel.replaceChild(newGroup, oldGroup);	
		console.log("group updated");
	}
}

/**
* Update title SVG group
*
* @param name - the group name
* @param components - the list of new components
*/
function updateTitleGroup(name, components) {
	var panel = document.getElementById('panel');
	var oldGroup = document.getElementById(name);

	console.log("updating title group");
	var newGroup = createTitleGroup(name, components);
	if(oldGroup != null) {
		panel.removeChild(oldGroup);
	}
	var overlay = document.getElementById('overlay');
	if(overlay != null) {
		panel.removeChild(overlay);
		panel.appendChild(newGroup);
		var w = panel.getAttribute("width");
		var h = panel.getAttribute("height");
		overlay = createOverlay(0, 0, w, h);
		panel.appendChild(overlay);
	}
	else {
		panel.appendChild(newGroup);
	}
	
	console.log("title group updated");
}

/**
* Handle mouse down event
*
* @param e - mouse event
*/
function handleMouseDown(e) {
	handleMouseEvent(e, 0);
}

/**
* Handle mouse up event
*
* @param e - mouse event
*/
function handleMouseUp(e) {
	handleMouseEvent(e, 1);
}

/**
* Handle mouse motion event
*
* @param e - mouse event
*/
function handleMouseMotion(e) {
	if(e.buttons == 1) { // left mouse button
		handleMouseEvent(e, 2);
	}
}

/**
* Go to the Configuration page
*/
function goConfig() {
    window.open(location.href + 'config/', '_self');
}

/**
* Handle mouse event
*
* @param e - mouse event
* @param upDownMotion - number defining mouse up/down/motion event
*/
function handleMouseEvent(e, upDownMotion) {
	var x = e.clientX - panelX - 9;
	var y = e.clientY - panelY - 9;
	d = {};
	d["command"] = "mouse";
	d["x"] = x;
	d["y"] = y;
	d["b"] = e.which; // 1-left, 2-middle, 3-right button
	d["d"] = upDownMotion; // 0-down, 1-up, 2-motion
	sendDataToServer(d);
	e.stopPropagation();
	
	if (e.stopPropagation) {
		e.stopPropagation();
	}
	else if(window.event){
		window.event.cancelBubble=true;
	}
}

/**
 * Send command to the server to initialize Web UI
 */
function initializeWebUi() {
	d = {};
	d["command"] = "init";
	sendDataToServer(d);
}

/**
* Handler for initial WebSocket event. Called upon WebSocket opened.
*/
function wsOpened() {
	console.log("webSocket opened");
	initializeWebUi();
}

/**
* Handler for WebSocket close event
*/
function webSocketClosedInServer() {
	console.log("webSocket closed in server");
	closeWebSocketInClient();
	console.log("webSocket closed in client");
	var panel = document.getElementById("panel");
	if(panel != null) {
		panel.parentElement.removeChild(panel);
	}
	var bgr = document.getElementById("page.bgr.image");
	if(bgr) {
		bgr.parentElement.removeChild(bgr);
	}
	var config = document.getElementById("config.img");
	if(config != null) {
		config.parentElement.removeChild(config);
	}
	document.body.style.background = "#ffffff";
}

/**
* This method called upon page loading
*/
async function init() {
	// Get the current font name
	var response = await fetch('/fonts?current');
	var currentFontName = response.ok ? await response.text() : null;
	if(currentFontName == null) {
		console.log("Cannot get the current font name from the server");
		return;
	}

	// Load the current font
	const font = new FontFace('newfont', 'url(../../font/' + currentFontName + ')');
	await font.load();
	document.fonts.add(font);
	document.body.style.fontFamily = '"newfont", Arial';

	// Open WebSocket
	if(webSocket == null) {
		openWebSocket(wsOpened, dispatchMessageFromServer, webSocketClosedInServer);	
	}
	else {
		wsOpened();
	}
}