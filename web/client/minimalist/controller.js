/* Copyright 2023 Peppy Player peppy.player@gmail.com
 
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

DEBUG = true; // global

if(!DEBUG || typeof(console.log) == 'undefined') {
   console.log = function() {};
}

function handleMouseUp(e) {
	for (const child of e.target.children) {
		child.setAttribute("transform", "scale(1.0)");
	}
	if (e.target.id === "play-icon" || e.target.id === "pause-icon") {
		play();
	} else if (e.target.id === "right-icon") {
		next();
	} else if (e.target.id === "left-icon") {
		previous();
	}
}

function play() {
	fetch("/api/playpause", { method: "PUT" }).then(function (_) {}).then().catch(function (err) {
	  console.log("Error: " + err.message);
	});
}

function next() {
	fetch("/api/next", { method: "PUT" }).then(function (_) {}).then().catch(function (err) {
	  console.log("Error: " + err.message);
	});
}

function previous() {
	fetch("/api/previous", { method: "PUT" }).then(function (_) {}).then().catch(function (err) {
	  console.log("Error: " + err.message);
	});
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
* Handle mouse event
*
* @param e - mouse event
* @param upDownMotion - number defining mouse up/down/motion event
*/
function handleMouseEvent(e, upDownMotion) {
	// var x = e.clientX - panelX - 9;
	// var y = e.clientY - panelY - 9;
	// d = {};
	// d["command"] = "mouse";
	// d["x"] = x;
	// d["y"] = y;
	// d["b"] = e.which; // 1-left, 2-middle, 3-right button
	// d["d"] = upDownMotion; // 0-down, 1-up, 2-motion

	console.log(e);

	// sendDataToServer(d);
	// e.stopPropagation();
	
	// if (e.stopPropagation) {
	// 	e.stopPropagation();
	// }
	// else if(window.event){
	// 	window.event.cancelBubble=true;
	// }
}

function getClickableSvg(parent, id, path, container, elementDiv) {
	let div = document.createElement("div");
	if (container) {
		div = container;
	}
	let svg = document.createElementNS('http://www.w3.org/2000/svg', 'image');
	svg.setAttribute('src', path);
	

	if (elementDiv) {
		elementDiv.setAttribute('id', id);
		elementDiv.appendChild(svg);
		div.appendChild(elementDiv);
    	parent.appendChild(div);
	} else {
		div.setAttribute('id', id);
		div.appendChild(svg);
	}
	
    parent.appendChild(div);
	SVGInject(svg, {
        onAllFinish: function() {
			if (elementDiv) {
				elementDiv.addEventListener('mousedown', handleMouseDown, false);
				elementDiv.addEventListener('mouseup', handleMouseUp, false);
			} else {
				div.addEventListener('mousedown', handleMouseDown, false);
				div.addEventListener('mouseup', handleMouseUp, false);
			}
        }
    });
	return div;
}

var seconds;
var playPauseDiv = document.createElement("div");
var playDiv = document.createElement("div");
var pauseDiv = document.createElement("div");
var span = document.createElement("span");

function timer() {
	fetch("/api/playpause", { method: "GET" }).then(function (response) {
		return response.json();
	  }).then((json) => {
		if (json.pause === false && playDiv.style.display !== 'block') {
			playDiv.style.display = 'block';
			pauseDiv.style.display = 'none';	
		} else if (json.pause === true && playDiv.style.display !== 'none') {
			playDiv.style.display = 'none';
			pauseDiv.style.display = 'block';
		}
	  }).catch(function (e) {
		console.log('Play/pause error: ' + e.message);
	  });
}

/**
* This method called upon page loading
*/
async function init() {
	let root = document.getElementById("screen");
	span.setAttribute('class', 'arrow');
	root.appendChild(span);	

	getClickableSvg(span, "left-icon", "icons/left.svg");
	getClickableSvg(span, "play-icon", "icons/play.svg", playPauseDiv, playDiv);
	playDiv.style.display = 'none';
	getClickableSvg(span, "pause-icon", "icons/pause.svg", playPauseDiv, pauseDiv);
	getClickableSvg(span, "right-icon", "icons/right.svg");

	let svg = document.createElementNS("http://www.w3.org/2000/svg", 'svg');
	svg.setAttribute("height",55);
	svg.setAttribute("width",55);
	let div = document.createElement("div");
	// div.setAttributeNS(null, 'style', 'display:flex;align-items: center;' );

	let circle = document.createElementNS("http://www.w3.org/2000/svg", 'circle');
	circle.setAttributeNS(null, 'cx', 25);
    circle.setAttributeNS(null, 'cy', 25);
    circle.setAttributeNS(null, 'r', 20);
	circle.setAttributeNS(null, 'style', 'fill: white; stroke: blue; stroke-width: 3px;' );
	svg.appendChild(circle);
	svg.setAttribute('class', 'right');
	div.setAttribute('class', 'arrow');
	div.appendChild(svg);
	span.appendChild(div);	

	seconds = setInterval(timer, 1000);
}
