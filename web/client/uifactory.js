/* Copyright 2016-2017 Peppy Player peppy.player@gmail.com
 
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

window.onload = window.onresize = function() {
    resize();
}

var SVG_URL = 'http://www.w3.org/2000/svg';
var XLINK_URL = 'http://www.w3.org/1999/xlink';
var NS_URL = "http://www.w3.org/XML/1998/namespace";

var currentTrackTimer = null;
var trackTime = 0;
var knobStep = 0;
var sliderWidth = 0;

/**
* Dispatches component creation to component specific methods
*
* @param d - dictionary containing component information
*/
function createComponent(d) {
	var comp = null;

	if(d == null) {
		return null;
	}
	
	if(d.type == "rectangle") {
		comp = createRectangle(d.name, d.x, d.y, d.w, d.h, 1, d.fgr, d.bgr, 1);
		if(d.name == volumeRectId || d.name == volumeSliderId || d.name == timerRectId || d.name == timerSliderId) {
			addSliderFunctionality(comp);
			sliderWidth = d.w;
		}
	} else if(d.type == "image") {
		comp = createImage(d.name, d.data, d.filename, d.x, d.y, d.w, d.h);
		if(d.name == volumeKnobId || d.name == timerKnobId) {
			addKnobFunctionality(comp);
		} else if(d.name == "pause.image" && d.filename.endsWith("play.png")) {			
			stopCurrentTrackTimer();
		}
	} else if(d.type == "text") {
		comp = createStaticText(d.name, d.x, d.y, d.text_color_current, d.text_size, d.text);
		if(d.name == timerId) {
			setCurrentTrackTime(comp);
			currentTrackTimer = setInterval(updateCurrentTrackTimer, 1000);
		} else if(d.name == timerTotalId) {
			trackTime = getSecondsFromString(d.text);
			knobStep = sliderWidth / trackTime;
		}
	} else if(d.type == "screen_title") {
		comp = createTitleGroup("screen_title", d.components);
	} else if(d.type == "screen_menu") {
		comp = createGroup(d.type, d.components);
	} else if(d.type == "clickable_rect") {
		comp = createRectangle(d.name, d.x, d.y, d.w, d.h, 0, null, null, 0);
		comp.addEventListener('mousedown', handleMouseDown, false);
		comp.addEventListener('mouseup', handleMouseUp, false);
	}
	return comp;
}

/**
* Creates screen overlay which receives and handles all mouse events
*
* @param x - overlay X coordinate
* @param y - overlay Y coordinate
* @param w - overlay width
* @param h - overlay height
*/
function createOverlay(x, y, w, h) {
	rect = document.createElementNS(SVG_URL,'rect');
	rect.setAttribute('id', 'overlay');
	rect.setAttribute('x', x);
	rect.setAttribute('y', y);
	rect.setAttribute('width', w);
	rect.setAttribute('height', h);
	rect.setAttribute("stroke-width", 0);
	rect.setAttribute("shape-rendering","optimizeQuality");
	rect.style.fill = document.body.style.background;
	rect.setAttribute("fill-opacity", 0.4);
	rect.setAttribute("stroke-opacity", 0);
	rect.addEventListener('mouseup', handleMouseUp, false);
	return rect;
}

/**
* Handles browser window resizing - moves panel to center of new browser window
*/
function resize() {
	var screen = document.getElementById('screen');
	
	if(screen == null) {
		return;
	}
	
	screen.setAttribute('width', window.innerWidth - 30);
	screen.setAttribute('height', window.innerHeight - 30);
	
	var panel = document.getElementById('panel');
	
	if(panel == null) {
		return;
	}
	
	var w = panel.getAttribute("width");
	var h = panel.getAttribute("height");
	panelX = (window.innerWidth - w)/2;
	panelY = (window.innerHeight - h)/2;
	panel.setAttribute('x', panelX);
	panel.setAttribute('y', panelY);
}

/**
* Creates the root SVG container
*
* @param id - the name of container
* @param bgr - background color
* 
* @return new SVG container
*/
function createScreen(id, bgr) {
	var screen = document.createElementNS(SVG_URL, 'svg');
	screen.setAttribute('width', window.innerWidth - 30);
	screen.setAttribute('height', window.innerHeight - 30);
	screen.setAttribute('id', id);
	document.body.style.background = bgr;
	return screen;
}

/**
* Creates SVG container which contains all UI components
*
* @param id - the name of container
* @param width - container width
* @param height - container height
* 
* @return new SVG container
*/
function createPanel(id, width, height) {	
	var panel = document.createElementNS(SVG_URL, 'svg');
	panel.setAttribute('width', width);
	panel.setAttribute('height', height + 1);
	panelX = (window.innerWidth - width)/2;
	panelY = (window.innerHeight - height)/2;
	panel.setAttribute('x', panelX);
	panel.setAttribute('y', panelY);
	panel.setAttribute('id', id);
	panel.setAttribute("shape-rendering", "crispEdges");
	var rect = createRectangle(id + ".rect", 0, 0, width + 1, height + 1, 1, "black", "black", 1);
	panel.appendChild(rect);
	return panel;
}

/**
* Creates SVG rectangle component
*
* @param id - the name of component
* @param x - rectangle X coordinate
* @param y - rectangle Y coordinate
* @param w - rectangle width
* @param h - rectangle height
* @param t - rectangle outline thickness
* @param lineColor - rectangle line color
* @param fillColor - rectangle fill color
* @param opacity - rectangle opacity
* 
* @return new SVG rectangle
*/
function createRectangle(id, x, y, w, h, t, lineColor, fillColor, opacity) {
	console.log("rect id:" + id + " x:" + x + " y:" + y + " w:" + w + " h:" + h + " fgr: " + lineColor + " fill:" + fillColor);

	rect = document.createElementNS(SVG_URL,'rect');
	rect.setAttribute('id', id);
	rect.setAttribute('x', x + 1);
	rect.setAttribute('y', y + 1);
	rect.setAttribute('width', w - 1);
	if(h < 3) {
		h = 3
	}
	rect.setAttribute('height', h - 1);
	rect.setAttribute("stroke-width", t);
	rect.setAttribute("shape-rendering","optimizeQuality");
	if(fillColor != null) {
		rect.style.fill = fillColor;
		rect.setAttribute("fill-opacity", 1.0);
	} else {
		rect.setAttribute("fill-opacity", 0);
	}
	if(lineColor != null) {
		rect.style.stroke = lineColor;
		rect.setAttribute("stroke-opacity", 0);
	} else {
		rect.setAttribute("stroke-opacity", 0);
	}	
	return rect;
}

/**
* Creates SVG image component
*
* @param id - the name of component
* @param data image data
* @param filename - image filename
* @param x - image X coordinate
* @param y - image Y coordinate
* @param w - image width
* @param h - image height
* 
* @return new SVG image
*/
function createImage(id, data, filename, x, y, w, h) {
	console.log("image id:" + id + " filename:" + filename + " x:" + x + " y:" + y + " w:" + w + " h:" + h);

	var img = document.createElementNS(SVG_URL, 'image');
	img.setAttributeNS(XLINK_URL, 'href', "data:image/png;base64," + data);
	img.setAttribute('width', w);
	img.setAttribute('height', h);
	img.setAttribute('id', id);
	img.setAttribute('x', x);
	img.setAttribute('y', y);
	return img;
}

/**
* Creates SVG text component
*
* @param id - the name of component
* @param x - text X coordinate
* @param y - text Y coordinate
* @param color - text color
* @param size - text height
* @param txt - text
* 
* @return new SVG text
*/
function createStaticText(id, x, y, color, size, txt) {
	console.log("text id:" + id + " text:" + txt + " x:" + x + " y:" + y + " color:" + color + " size:" + size);

	var text = document.createElementNS(SVG_URL, 'text');
	text.setAttribute('x', x);
	text.setAttribute('y', y + size + 1);
	text.setAttribute('fill', color);
	text.textContent = txt;
	text.setAttribute('id', id);
	text.setAttribute("font-size", size);
	text.setAttributeNS(NS_URL, "xml:space", "preserve");
	return text;
}

/**
* Creates SVG animation
*
* @param from - animation start position in pixels
* @param to - animation stop position in pixels
* 
* @return new SVG animation
*/
function getAnimation(from, to) {
	var scrollTime = "30s";
	var a = document.createElementNS(SVG_URL, 'animate');
	a.setAttribute("begin", 0);
	a.setAttribute("attributeName", "x");
	a.setAttribute("from", from);
	a.setAttribute("to", to);
	a.setAttribute("dur", scrollTime);
	a.setAttribute("repeatCount", "indefinite");
	return a;
}

/**
* Appends animated text to the provided group component
*
* @param group - the group component to which animation will be added
* @param comp - text component to animate
* 
* @return new SVG animation
*/
function createAnimatedText(group, comp) {
	var gap = 20;	
	var t1 = comp[1];
	var id = t1.name;
	var color = t1.text_color_current;
	var size = t1.text_size;
	var text = t1.text;
	var textWidth = t1.text_width;
	
	var text1 = createStaticText(t1.name, 0, 0, color, size, text);
	var text2 = createStaticText(t1.name + ".2", textWidth + gap, 0, color, size, text);	
	var a1 = getAnimation(0, -textWidth - gap);
	var a2 = getAnimation(textWidth + gap, 0);	
	text1.appendChild(a1);
	text2.appendChild(a2);
	
	group.appendChild(text1);
	group.appendChild(text2);
}

/**
* Creates SVG group
*
* @param name - group name
* @param components - group components
* 
* @return new SVG group
*/
function createGroup(name, components) {
	var group = document.createElementNS(SVG_URL, 'g');
	group.setAttribute("id", name);
	
	for (var i=0; i < components.length; i++) {
		var d = components[i];
		comp = createComponent(d);
		group.appendChild(comp);
	}
	return group;
}

/**
* Creates station screen title SVG group
*
* @param name - group name
* @param components - group components
* 
* @return new SVG group
*/
function createTitleGroup(name, components) {
	if(components == null || components.length == 0) {
		return;
	}

	var group = document.createElementNS(SVG_URL, 'g');
	group.setAttribute("id", name);
	
	if(components[0] != null) {
		comp = createComponent(components[0]);
		group.appendChild(comp);
	}
			
	for (var i=1; i < components.length; i++) {
		var d = components[i];
		if(d.label_type == 0) {
			comp = createComponent(d);
			group.appendChild(comp);
		} else {
			comp = createAnimatedText(group, components);
			break;
		}
	}
	
	return group;
}

/**
* Set current track time
*
* @param comp - time slider component
*/
function setCurrentTrackTime(comp) {
	if(currentTrackTimer != null) {
		stopCurrentTrackTimer();
	}
	sec = getSecondsFromString(comp.textContent);
	comp.setAttribute("seconds", sec);
}

/**
* Update current track timer
*/
function updateCurrentTrackTimer() {
	timer = document.getElementById(timerId);
	timerKnob = document.getElementById(timerKnobId);
	
	if(timer == null || timerKnob == null) {
		stopCurrentTrackTimer();
		return;
	}
	
	s = parseInt(timer.getAttribute("seconds")) + 1;
	
	if(s > trackTime) {
		stopCurrentTrackTimer();
		return;
	}
	
	timer.setAttribute("seconds", s);
	timer.textContent = getStringFromSeconds(s);
	
	timerKnob.setAttribute("x", parseFloat(timerKnob.getAttribute("x")) + knobStep);
}

/**
* Stop track timer
*/
function stopCurrentTrackTimer() {
	if(currentTrackTimer == null || currentTrackTimer == 'undefined') {
		return;
	}
	clearInterval(currentTrackTimer);
}

/**
* Converts string to seconds
*
* @param str - string representing time
* 
* @return seconds
*/
function getSecondsFromString(str) {
	if(str == null) {
		return 0;
	}
	nums = str.split(":");
	result = 0;
	
	if(nums.length == 3) {
		result = (parseInt(nums[0]) * 3600) + (parseInt(nums[1]) * 60) + (parseInt(nums[2]));
	} else if(nums.length == 2) {
		result = (parseInt(nums[0]) * 60) + (parseInt(nums[1]));
	}
	
	return result;
}

/**
* Creates string from seconds
*
* @param sec - seconds
* 
* @return string representation of time
*/
function getStringFromSeconds(sec) {
	if(sec == null || sec == 'undefined') {
		return "";
	}

    s = parseInt(sec);
    hours = parseInt(s / 3600);
    minutes = parseInt(s / 60);
    seconds = parseInt(s % 60);
    label = "";
        
    if(hours != 0) {
        label += hours.toString();
		if(label.length == 1) {
			label = "0" + label;
		}
		label += ":";
        minutes = parseInt((s - hours * 3600) / 60);
    }
	
    min = minutes.toString();
	if(min.length == 1) {
		label += "0";
	}
	label += min + ":";

	secs = seconds.toString();
	if(secs.length == 1) {
		label += "0";
	}
	label += secs;
	
    return label;
}
