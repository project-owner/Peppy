Peppy player has embedded Web Server which can be activated by setting corresponding flag in the [configuration file](https://github.com/project-owner/Peppy/wiki/Peppy#configuration-file). The Web Server allows to control the player using Web Browser from any device in your home network. The IP Address of the Peppy player should be specified as URL in Web Browser. Here is the example URL (you should provide you own IP Address):
```
http://192.168.1.75:8000
```
The default port number specified in the [configuration file](https://github.com/project-owner/Peppy/wiki/Peppy#configuration-file) is 8000. It can be changed to any other port.

Web UI which appears in Web Browser is absolutely the same as UI in the [touchscreen](https://github.com/project-owner/Peppy/wiki/Touchscreen). The only current limitation is that only one Web UI can be active at the time. All UI actions which you are making on the touchscreen will be automatically repeated in Web UI and vice verse. For example if you are moving the volume control knob on the touchscreen it will be also moving in the Web UI.

The Web UI was written using technologies (HTML5, Json, SVG, WebSocket) which should be supported by all modern Web Browsers. Here are the screenshots taken from the Windows machine running Peppy Web UI in Firefox 44.0.2 and Internet Explorer 11.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/browsers.png|alt=browsers]]
</p>
The following pictures where taken from the Samsung smartphone running Chrome browser and from iPhone running Safari browser.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/web-ui.jpg|alt=web-ui]]
</p>

[<<Previous](https://github.com/project-owner/Peppy/wiki/Screensaver) | [Next>>](https://github.com/project-owner/Peppy/wiki/Resolution)