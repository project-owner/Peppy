/* Copyright 2016 Peppy Player peppy.player@gmail.com
 
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
		console.log("WebSocket closed");
		return;
	}
	d = JSON.stringify(data);
	console.log("Sent to server: " + d);
	webSocket.send(d);
}

/**
* Dispatch the message from web server to corresponding handler
*
* @param msg - the message received from web server
*/
function dispatchMessageFromServer(msg) {
	d = JSON.parse(msg.data);
	
	if(d["command"] == "update_screen") {
		updateScreen(d["components"]);
	}
	else if(d["command"] == "update_element") {
		updateComponents(d["components"]);
	}
	else if(d["command"] == "update_station_title") {
		updateTitleGroup("station_title", d["components"]);
	}
	else if(d["command"] == "update_station_menu") {
		updateGroup("station_menu", d["components"]);
	}
	else if(d["command"] == "update_menu") {
		updateScreen(d["components"]);
	}
	else if(d["command"] == "remove_element") {
		removeComponents(d["components"]);
	}
	else if(d["command"] == "start_screensaver") {
		startScreensaver();
	}
	else if(d["command"] == "stop_screensaver") {
		stopScreensaver();
	}
}

/**
* Start screensaver mode by adding dark overlay
*/
function startScreensaver() {
	console.log("starting screensaver");
	var panel = document.getElementById('panel');
	var w = panel.getAttribute("width");
	var h = panel.getAttribute("height");
	overlay = createOverlay(0, 0, w, h);
	panel.appendChild(overlay);
	console.log("screensaver started");
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
}

/**
* Remove components specified by their IDs
* 
* @param ids - the list of component ids to remove
*/
function removeComponents(ids) {
	var panel = document.getElementById('panel');
	
	console.log("removing component");
	
	for (var i=0; i < ids.length; i++) {
		var id = ids[i];
		var element = document.getElementById(id);
		if(element != null) {
			panel.removeChild(element);
		}
	}
	
	console.log("component removed");
}

/**
* Update screen by new components
*
* @param components -  the list of new components
*/
function updateScreen(components) {
	var screen = document.getElementById('screen');
	var panel = document.getElementById('panel');
	var isNewScreen = false;
	
	console.log("updating screen");
	
	for (var i=0; i < components.length; i++) {
		var d = components[i];
		var type = d.type;
		
		if(type == "screen") {
			if(screen == null) {
				screen = createScreen(d.name, d.bgr);
				isNewScreen = true;
			}
		} else if(type == "panel") {
			if(panel != null) {
				screen.removeChild(panel);
			}
			panel = createPanel(d.name, d.w, d.h);
			screen.appendChild(panel);
		} else {
			var comp = createComponent(d);
			panel.appendChild(comp);
		}
	}
	
	if(isNewScreen) {
		document.body.appendChild(screen);
	}
	
	console.log("screen updated");
}

/**
* Update components
*
* @param components - the list of new components
*/
function updateComponents(components) {
	var panel = document.getElementById('panel');
	
	console.log("updating components");
	
	for (var i=0; i < components.length; i++) {
		var d = components[i];
		if(d == null) {
			continue;
		}
		var element = document.getElementById(d.name);
		comp = createComponent(d);
		if(element != null) {
			panel.replaceChild(comp, element);
		}
		else {
			clickableRect = document.getElementById("clickable_rect");
			panel.removeChild(clickableRect);
			panel.appendChild(comp);
			panel.appendChild(clickableRect);
		}
	}
	
	console.log("components updated");
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
	console.log("updating group");
	var newGroup = createGroup(name, components);
	panel.replaceChild(newGroup, oldGroup);	
	console.log("group updated");
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
	
	if(oldGroup == null) {
		return;
	}
	
	console.log("updating title group");
	var newGroup = createTitleGroup(name, components);
	panel.removeChild(oldGroup);
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
	handleMouseEvent(e, 2);
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
}

/**
* Handler for initial WebSocket event. Called upon WebSocket opened.
*/
function wsOpened() {
	console.log("WebSocket opened");
	d = {};
	d["command"] = "init";
	sendDataToServer(d);
}

/**
* Handler for WebSocket close event
*/
function webSocketClosedInServer() {
	console.log("WebSocket closed in server");
	closeWebSocketInClient();
	console.log("WebSocket closed in client");
	var panel = document.getElementById("panel");
	panel.parentElement.removeChild(panel);
}

/**
* This method called upon page loading. Calls wsOpened if WebSocket channel established.
*/
function init() {
	if(webSocket == null) {
		openWebSocket(wsOpened, dispatchMessageFromServer, webSocketClosedInServer);	
	}
	else {
		wsOpened();
	}
}