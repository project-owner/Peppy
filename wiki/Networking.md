There are two main methods to connect Raspberry Pi 2 to the network:
* [**Wired Ethernet connection**](#wired)
* [**Wireless WiFi connection**](#wifi)

### Wired Ethernet connection <a id="wired"></a>
In my home network this is the most reliable connection method. The Peppy player is not completely portable system as it still needs to be connected to the main power outlet. Therefore to have one more cable for the network connection doesn't hurt especially when you use [Ethernet over powerline adapters](http://www.amazon.com/gp/product/B00CUD1M66) which you can connect at any location in your house. I even wanted to embed that adapter into the Peppy player itself but decided that such system could be over-heated. Though I still keep this idea in my mind.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/hardware/net.jpg|alt=net]]
</p>

### Wireless WiFi connection <a id="wifi"></a>
This is more convenient method as it doesn't need any network cable but less reliable method (at least in my home network) than the wired connection. I have tried a couple of different USB WiFi dongles but had the best results with the following [one](http://www.amazon.com/CanaKit-Raspberry-Wireless-Adapter-Dongle/dp/B00GFAN498).
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/hardware/wifi.jpg|alt=wifi]]
</p>

[This web page](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md) explains how to configure WiFi for Raspberry Pi.

There is currently the bug in Peppy player. That bug prevents the usage of infrared remote control when WiFi connection is in use.

[<<Previous](https://github.com/project-owner/Peppy/wiki/Cabling) | [Next>>](https://github.com/project-owner/Peppy/wiki/Assembling)