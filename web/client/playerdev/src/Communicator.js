/**
* Creates new WebSocket
*
* @param messageCallback - callback method which will be called upon new message from server
* @param closeCallback = callback method which will be called when WebSocket channel closed
*/
export function getWebSocket(messageCallback, closeCallback) {
  let webSocket = null;

  try {
    webSocket = new WebSocket(`ws://${window.location.host}/ws?custom`);
  } catch (e) {
    webSocket = new WebSocket(`wss://${window.location.host}/ws?custom`);
  }

  if (webSocket == null) {
    return;
  }

  if (messageCallback) {
    webSocket.onmessage = messageCallback;
  }
  if (closeCallback) {
    webSocket.onclose = closeCallback;
  }

  return webSocket;
}

/**
* Closes and nullifies WebSocket object
*/
export function closeWebSocketInClient(webSocket) {
  if (webSocket !== null) {
    try {
      webSocket.close();
      webSocket = null;
    } catch (e) {
      console.log(e);
    }
  }
}

export function wsOpened() {
  console.log("webSocket opened");
}

export function setPoller(callback) {
  // Send ping command to server every 15 seconds to avoid idle websocket (20 sec)
  // termination if no message from server and client
  const period = 2000; // 1000 = 1 sec
  setInterval(function () {
    if (callback !== null && callback !== undefined) {
      // webSocket.send(JSON.stringify({ "command": "ping" }));
      // console.log("ping");
      callback();
    }
  }, period);
}