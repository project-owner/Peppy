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

webSocket = null; // global

/**
* Creates new WebSocket channel
*
* @param openCallback - callback method which will be called upon successful WebSocket channel
* @param messageCallback - callback method which will be called upon new message from server
* @param closeCallback = callback method which will be called when WebSocket channel closed
*/
function openWebSocket(openCallback, messageCallback, closeCallback) {
    webSocket = null;

    try {
        webSocket = new WebSocket(`ws://${location.host}/ws`);
    } catch(e) {
        webSocket = new WebSocket(`wss://${location.host}/ws`);
    }

    if (webSocket == null) {
        return;
    }

    if (openCallback) {
        webSocket.onopen = openCallback;
    }
    if (messageCallback) {
        webSocket.onmessage = messageCallback;
    }
    if (closeCallback) {
        webSocket.onclose = closeCallback;
    }

    // Send ping command to server every 15 seconds to avoid idle websocket (20 sec)
    // termination if no message from server and client
    setInterval(function() {
        if (webSocket !== null && webSocket.readyState == 1) {
            webSocket.send(JSON.stringify({"command": "ping"}));
            console.log("ping");
        }
    }, 15000);
}

/**
* Closes and nullifies WebSocket object
*/
function closeWebSocketInClient() {
    if (webSocket !== null) {
        webSocket.close();
        webSocket = null;
    }
}
