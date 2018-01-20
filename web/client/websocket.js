/* Copyright 2016-2018 Peppy Player peppy.player@gmail.com
 
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

webSocket = null // global

/**
* Creates new WebSocket channel
*
* @param openCallback - callback method which will be called upon successful WebSocket channel
* @param messageCallback - callback method which will be called upon new message from server
* @param closeCallback = callback method which will be called when WebSocket channel closed
*/
function openWebSocket(openCallback, messageCallback, closeCallback) {
	webSocket = new WebSocket("ws://" + location.host + "/ws");

	if(openCallback != null) {
		webSocket.onopen = openCallback;
	}
	if(messageCallback != null) {
		webSocket.onmessage = messageCallback;
	}
	if(closeCallback != null) {
		webSocket.onclose = closeCallback;
	}		
}

/**
* Closes and nullifies WebSocket object
*/
function closeWebSocketInClient() {
	if(webSocket == null) {
		return;
	}
	webSocket.close();
    webSocket = null;
}