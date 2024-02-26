/* Copyright 2016-2024 Peppy Player peppy.player@gmail.com
 
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
var SCROLL_TIME = "18s";

var currentTrackTimer = null;
var trackTime = 0;
var knobStep = 0;
var sliderWidth = 0;

var volumeKnobId = "volume.knob";
var timerRectId = "track.time.slider.bgr";
var timerSliderId = "track.time.slider.slider";
var timerKnobId = "track.time.slider.knob";
var timerId = "track.time.current.text";
var timerTotalId = "track.time.total.text";
var defs = null;
var templates = [
	{
		left: {
			channel: {
				red: 1.4,
				green: 1.2,
				blue: 2.2
			},
			bgr: {
				red: 0.6,
				green: 0.4,
				blue: 1.4
			}
		},
		right: {
			channel: {
				red: 2.4,
				green: 1.2,
				blue: 1.4
			},
			bgr: {
				red: 1.4,
				green: 0.4,
				blue: 0.6
			}
		}
	},
	{
		left: {
			channel: {
				red: 2.5,
				green: 1.4,
				blue: 1.8,
			},
			bgr: {
				red: 1.6,
				green: 0.7,
				blue: 1.0,
			}
		},
		right: {
			channel: {
				red: 2.5,
				green: 2.3,
				blue: 1.6
			},
			bgr: {
				red: 1.6,
				green: 1.5,
				blue: 0.7
			}
		}
	},
	{
		left: {
			channel: {
					red: 0.6,
					green: 1.8,
					blue: 1.4
			},
			bgr: {
					red: 0,
					green: 1.2,
					blue: 0.8
			}
		},
		right: {
			channel: {
					red: 2.5,
					green: 1.3,
					blue: 1.0
			},
			bgr: {
					red: 2.0,
					green: 0.8,
					blue: 0.5
			}
		}
	},
	{
		left: {
			channel: {
					red: 1.2,
					green: 0.2,
					blue: 2.5
			},
			bgr: {
					red: 0.7,
					green: 0,
					blue: 2.0
			}
		},
		right: {
			channel: {
					red: 2.5,
					green: 0.2,
					blue: 1.2
			},
			bgr: {
					red: 2.0,
					green: 0,
					blue: 0.7
			}
		}
	}
];

var leftColors = [];
var rightColors = [];
var bgrLeftColors = [];
var bgrRightColors = [];

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
		comp = createRectangle(d.name, d.x, d.y, d.w, d.h, d.fgr, d.bgr, d.t);
		if(d.name == timerRectId || d.name == timerSliderId) {
			comp.setAttribute("onmousedown", "handleMouseDown(evt)");
			comp.setAttribute("onmouseup", "handleMouseUp(evt)");			
			sliderWidth = d.w;
		}
	} else if(d.type == "image") {
		let data = Object.hasOwn(d, "data") ? d.data : null;
		comp = createImage(d.name, data, d.filename, d.x, d.y, d.w, d.h);
		if (comp != null) {
			if(d.name == volumeKnobId || d.name == timerKnobId) {
				comp.setAttribute("style", "cursor: move;");
			} else if(d.name == "pause.image" && d.filename.endsWith("play.png")) {
				stopCurrentTrackTimer();
			}
		}
	} else if(d.type == "text") {
		comp = createStaticText(d.name, d.x, d.y, d.text_color_current, d.text_size, d.text);
		if(d.name == timerId) {
			console.log('set timer');
			setCurrentTrackTime(comp);
			if(!d.pause) {
				currentTrackTimer = setInterval(updateCurrentTrackTimer, 1000);
			}
		} else if(d.name == timerTotalId) {
			trackTime = getSecondsFromString(d.text);
			knobStep = sliderWidth / trackTime;
		}
	} else if(d.type == "screen_title") {
		comp = createTitleGroup("screen_title", d.components);
	} else if(d.type == "screen_menu") {
		comp = createGroup(d.type, d.components);
	} else if(d.type == "stream_player") {
		comp = createStreamPlayer(d.name, d.port, d.volume, d.mute, d.pause);
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
	rect.style.fill = document.body.style.background;
	rect.setAttribute("fill-opacity", 0.4);
	rect.setAttribute("stroke-opacity", 0);
	rect.addEventListener('mouseup', handleMouseUp, false);
	return rect;
}

/**
 * Create arrays with gradient colors for VU Meter screensaver
 */
function createTemplates() {
	const i = Math.floor(Math.random() * templates.length);
	let t = templates[i];

	leftColors = [];
	rightColors = [];
	bgrLeftColors = [];
	bgrRightColors = [];

	for (n=0; n<101; n++) {
		leftColors.push("rgb(" + parseInt(n * t.left.channel.red) + "," + parseInt(n * t.left.channel.green) + "," + parseInt(n * t.left.channel.blue) + ")");
		bgrLeftColors.push("rgb(" + parseInt(n * t.left.bgr.red) + "," + parseInt(n * t.left.bgr.green) + "," + parseInt(n * t.left.bgr.blue) + ")");
		rightColors.push("rgb(" + parseInt(n * t.right.channel.red) + "," + parseInt(n * t.right.channel.green) + "," + parseInt(n * t.right.channel.blue) + ")");
		bgrRightColors.push("rgb(" + parseInt(n * t.right.bgr.red) + "," + parseInt(n * t.right.bgr.green) + "," + parseInt(n * t.right.bgr.blue) + ")");
	}
}

/**
 * Creates gradient overlay for VU Meter screensaver
 *
 * @returns - array with gradient start/stop elements
 */
function getGradientOverlay() {
	if (defs != null) {
		return {
			leftColor: defs.firstChild.firstChild,
			rightColor: defs.firstChild.lastChild,
		}
	}

	let overlay = document.getElementById('overlay');

	if (overlay == null) {
		return;
	}

	createTemplates();

	defs = document.createElementNS(SVG_URL, 'defs');
	defs.id = "defs";
	var gradient = document.createElementNS(SVG_URL, 'linearGradient');
	gradient.id = 'Gradient';
	let stopColor = document.createElementNS(SVG_URL, 'stop');
	stopColor.setAttribute('offset', '0%');
	stopColor.setAttribute('stop-color', 'rgb(0,0,0)');
	gradient.appendChild(stopColor);
	stopColor = document.createElementNS(SVG_URL, 'stop');
	stopColor.setAttribute('offset', '100%');
	stopColor.setAttribute('stop-color', 'rgb(0,0,0)');
	gradient.appendChild(stopColor);
	gradient.setAttribute('x1', '0');
	gradient.setAttribute('y1', '0');
	gradient.setAttribute('x2', '1');
	gradient.setAttribute('y2', '0');
	defs.appendChild(gradient);
	panel.appendChild(defs);
	overlay.style.fill = 'url(#Gradient)';
	overlay.setAttribute("fill-opacity", 0.75);

	return {
		leftColor: defs.firstChild.firstChild,
		rightColor: defs.firstChild.lastChild,
	};
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

	var config = document.getElementById("config.img");
	if(config) {
        w = config.getAttribute("width");
        h = config.getAttribute("height");
        newX = window.innerWidth - 60;
        newY = window.innerHeight - 60;
        config.setAttribute('x', newX);
        config.setAttribute('y', newY);
	}
}

/**
* Creates the page background
*
* @param image - link to the background image
* @param blur - blur value in pixels e.g. 10px
* @param opacity - opacity value 0-1 e.g. 0.4
*/
function createBackground(image, blur, opacity) {
	var div = document.createElement("div");
	div.setAttribute("id", "page.bgr.image");
	div.style.display = "block";
	div.style.zIndex = -1;
	div.style.background = "url('" + image + "')";
	div.style.position = "absolute";
	div.style.filter = "blur(" + blur + "px)";
	div.style.top = 0;
	div.style.left = 0;
	div.style.width = "100%";
	div.style.height = "100%";
	div.style.opacity = opacity;
	div.style.transform = "scale(1.1)";
	div.style.backgroundSize = "cover";
	document.body.appendChild(div);
}

/**
* Update the page background
*
* @param image - link to the background image
* @param blur - blur value in pixels e.g. 10px
* @param opacity - opacity value 0-1 e.g. 0.4
*/
function updateBackground(div, image, blur, opacity) {
	div.style.background = "url('" + image + "')";
	div.style.filter = "blur(" + blur + "px)";
	div.style.opacity = opacity;
	div.style.transform = "scale(1.1)";
	div.style.backgroundSize = "cover";
}

/**
* Creates the root SVG container
*
* @param id - the name of container
* 
* @return new SVG container
*/
function createScreen(id) {
	var screen = document.createElementNS(SVG_URL, 'svg');
	screen.setAttribute('id', id);
	screen.setAttribute('width', window.innerWidth - 30);
	screen.setAttribute('height', window.innerHeight - 30);
	screen.addEventListener('mousedown', handleMouseDown, false);
	screen.addEventListener('mouseup', handleMouseUp, false);
	screen.addEventListener('mousemove', handleMouseMotion, false);
	return screen;
}

/**
* Creates SVG container which contains all UI components
*
* @param id - the name of container
* @param width - container width
* @param height - container height
* @param fgr - foreground color
* @param bgr - background color
* 
* @return new SVG container
*/
function createPanel(id, width, height, fgr, bgr, bgrType) {
	var panel = document.createElementNS(SVG_URL, 'svg');
	panel.setAttribute('width', width);
	panel.setAttribute('height', height);
	panelX = (window.innerWidth - width)/2;
	panelY = (window.innerHeight - height)/2;
	panel.setAttribute('x', panelX);
	panel.setAttribute('y', panelY);
	panel.setAttribute('id', id);

	if((bgrType == "image" || bgrType == "album.art") && bgr) {
		console.log(bgrType);
		var img = createImage(bgr.filename, bgr.data, bgr.filename, bgr.x, bgr.y, bgr.w, bgr.h);
		panel.appendChild(img);
	} else {	
		var rect = createRectangle(id + ".rect", 0, 0, width, height, fgr, bgr, 0);
		panel.appendChild(rect);
	}

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
* @param lineColor - rectangle line color
* @param fillColor - rectangle fill color
* @param border - border thickness
* 
* @return new SVG rectangle
*/
function createRectangle(id, x, y, w, h, lineColor, fillColor, border) {
	console.log("rect id:" + id + " x:" + x + " y:" + y + " w:" + w + " h:" + h + " fgr:" + lineColor + " fill:" + fillColor + " border:" + border);

	var rect = document.createElementNS(SVG_URL,'rect');
	rect.setAttribute('id', id);
	rect.setAttribute('x', x);
	rect.setAttribute('y', y);
	rect.setAttribute('width', w + 0.5);
	rect.setAttribute('height', h + 0.5);
	rect.setAttribute("stroke-width", border);
	if (fillColor != null) {
		if (lineColor == null && border != 0) {
			rect.setAttribute("fill-opacity", 0);
			rect.setAttribute("stroke-opacity", 1.0);
			rect.style.stroke = fillColor;
		} else {
			rect.style.fill = fillColor;
			rect.setAttribute("fill-opacity", 1.0);
			rect.setAttribute("stroke-opacity", 0);
		}
	} else {
		rect.setAttribute("fill-opacity", 0);
		rect.setAttribute("stroke-opacity", 0);
	}
	if(lineColor != null) {
		rect.style.stroke = lineColor;
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
	if (filename.startsWith("http")) {
		img.setAttributeNS(XLINK_URL, 'href', decodeURIComponent(filename));
	} else {
		if (data == null) {
			return null;
		}

		if(filename.endsWith(".svg")) {
			img.setAttributeNS(XLINK_URL, 'href', "data:image/svg+xml;base64," + data);
		} else {
			console.log(data.length);
			img.setAttributeNS(XLINK_URL, 'href', "data:image/png;base64," + data);
		}
	}

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
	var a = document.createElementNS(SVG_URL, 'animate');
	a.setAttribute("begin", 0);
	a.setAttribute("attributeName", "x");
	a.setAttribute("from", from);
	a.setAttribute("to", to);
	a.setAttribute("dur", SCROLL_TIME);
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
	var color = t1.text_color_current;
	var size = t1.text_size;
	var text = t1.text;
	var textWidth = t1.text_width;
	var y = t1.y + 1;
	
	var text1 = createStaticText(t1.name, 0, y, color, size, text);
	var text2 = createStaticText(t1.name + ".2", textWidth + gap, y, color, size, text);	
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
* Creates screen title SVG group
*
* @param name - group name
* @param components - group components
* 
* @return new SVG group
*/
function createTitleGroup(name, components) {
	if(components == null) {
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
* Creates stream player
*
* @param name - component name
* @param port - streaming server port
* @param volume - current volume
* @param mute - mute flag
*/
function createStreamPlayer(name, port, volume, mute, pause) {
	console.log("audio id:" + name + " port:" + port + " volume:" + volume + " mute:" + mute + " pause:" + pause);

	var streamPlayer = new Audio();
	streamPlayer.id = name;
	streamPlayer.controls = false;
	streamPlayer.autoplay = true;
	streamPlayer.volume = volume/100;
	streamPlayer.muted = mute;
	streamPlayer.paused = false;
	
	streamPlayer.src = "http://" + window.location.hostname + ":" + port;
	streamPlayer.addEventListener("loadeddata", function () {		
		if(streamPlayer.readyState > 0) {
			streamPlayer.play();
			console.log('start playing stream');
		}
	});
	
	return streamPlayer;
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
	var sec = getSecondsFromString(comp.textContent);
	comp.setAttribute("seconds", sec);	
}

/**
* Update current track timer
*/
function updateCurrentTrackTimer() {
	var timer = document.getElementById(timerId);
	var timerKnob = document.getElementById(timerKnobId);

	if(timer == null || timerKnob == null) {
		stopCurrentTrackTimer();
		window.getSelection().removeAllRanges();
		return;
	}
	var s = parseInt(timer.getAttribute("seconds")) + 1;
	
	if(s > trackTime) {
		stopCurrentTrackTimer();
		window.getSelection().removeAllRanges();
		return;
	}

	timer.setAttribute("seconds", s);
	timer.textContent = getStringFromSeconds(s);
	timerKnob.setAttribute("x", parseFloat(timerKnob.getAttribute("x")) + knobStep);
	window.getSelection().removeAllRanges();
}

/**
* Set timerRunning flag to false
*/
function stopTimer() {
	stopCurrentTrackTimer();
	console.log('stopping timer');
}

/**
* Stop track timer
*/
function stopCurrentTrackTimer() {
	if(currentTrackTimer == null || currentTrackTimer == 'undefined') {
		console.log('currentTrackTimer is undefined');
		return;
	}
	clearInterval(currentTrackTimer);
	console.log('cleared timer');
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
	var nums = str.split(":");
	var result = 0;
	
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

    var s = parseInt(sec);
    var hours = parseInt(s / 3600);
    var minutes = parseInt(s / 60);
    var seconds = parseInt(s % 60);
    var label = "";
        
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
