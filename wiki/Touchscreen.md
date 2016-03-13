[Adafruit PiTFT Touchscreen](https://www.adafruit.com/products/2097) is the main control component in the Peppy player. Even if you are using another controlling devices such as mouse, keyboard or IR remote control you still have to validate the correctness of issued commands on touchscreen. The screen size of PiTFT is 3.5" and screen resolution is 480*320 pixels. This is probably the minimum touchscreen size/resolution for UI of average complexity like in Peppy player. The touch areas of smaller size screens become hard to use for fingertips.

<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/hardware/tft-1.jpg|alt=tft-1]]
</p>

There are two small pads on the back of the PiTFT. The PiTFT comes with those pads connected. This allows to switch on/off the PiTFT back-light by changing level on GPIO pin #18. This is a good feature which could be used for example to switch off PiTFT when player enters the screensaver mode. But unfortunately Amp+ module is also using GPIO pin#18 for its own purposes. Therefore if you don't cut that trace which connects those two small pads Amp+ will be nonfunctional. You can do that by hobby knife. The image below shows the pads and trace before cut and after.

<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/hardware/tft-2.jpg|alt=tft-2]]
</p>

PiTFT can be connected to 40-pin GPIO connector of the Raspberry Pi 2 using the first 26 pins. PiTFT doesn't use all those pins but I found that it's much easier to create 26-pin ribbon cable rather than to connect individual pins between Raspberry Pi's GPIO and PiTFT connector. The details of preparing such cable will be discussed in the chapter about [cabling](https://github.com/project-owner/Peppy/wiki/Cabling).

<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/hardware/tft-3.jpg|alt=tft-3]]
</p>
[<<Previous](https://github.com/project-owner/Peppy/wiki/Amplifier) | [Next>>](https://github.com/project-owner/Peppy/wiki/Speakers)