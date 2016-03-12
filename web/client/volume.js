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

var currentX = 0;
var mouseButtonDown = false;
var mouseMoving = false;
var volumeMute = false;
var volumeRectId = "volume.bgr";
var volumeSliderId = "volume.slider";
var volumeKnobId = "volume.knob";

/**
* Adds knob mouse listeners to provided knob object
*
* @param knob - the knob object
*/
function addKnobFunctionality(knob) {
	knob.setAttribute("style", "cursor: move;");
	knob.setAttribute("onmousedown", "knobDown(evt)");
	knob.setAttribute("onmouseup", "knobUp(evt)");
	knob.setAttribute("onmousemove", "knobMove(evt)");
	knob.setAttribute("onmouseout", "knobOut(evt)");
	knob.setAttribute("transform","translate(0, 0)");
}

/**
* Adds mouse up/down listeners to provided element
*
* @param element - the element
*/
function addSliderFunctionality(element) {
	element.setAttribute("onmousedown", "handleMouseDown(evt)");
	element.setAttribute("onmouseup", "handleMouseUp(evt)");
}

/**
* Event handler for knob mouse down event
*
* @param event - the event to handle
*/
function knobDown(event) {
	event.preventDefault();
	currentX = event.clientX;
	mouseButtonDown = true;
	handleMouseDown(event);
}

/**
* Event handler for knob mouse up event
*
* @param event - the event to handle
*/
function knobUp(event) {
	mouseButtonDown = false;
	if(mouseMoving) {
		mouseMoving = false;
	}
	handleMouseUp(event);
}

/**
* Event handler for knob move event
*
* @param event - the event to handle
*/       
function knobMove(event) {
	if(!mouseButtonDown) {
		return;
	}	 
	
	mouseMoving = true;
	var element = event.target;
	var width = element.getBBox()["width"];
	var dx = event.clientX - currentX;	
	var r = document.getElementById(volumeRectId);
	var rbb = r.getBoundingClientRect();
	var rectX = rbb["left"];
	var rectW = rbb["width"];
	var bb = element.getBoundingClientRect();
	var left = bb["left"];
	var right = bb["right"];
	if(((left + dx) < rectX) || ((right + dx)> (rectX + rectW))) {
		return;
	}
	var transform = element.transform.baseVal.getItem(0);
	var currentMatrix = transform.matrix.translate(dx, 0);  
	transform.setMatrix(currentMatrix);
	currentX = event.clientX;
	
	handleMouseMotion(event);
}

/**
* Event handler for mouse out knob event
*
* @param event - the event to handle
*/
function knobOut(event) {
	if(!mouseButtonDown) {
		return;
	}	
	mouseButtonDown = false;
	mouseMoving = false;
	handleMouseUp(event);
}
