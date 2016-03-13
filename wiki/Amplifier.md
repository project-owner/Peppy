[HiFiBerry Amp+](https://www.hifiberry.com/ampplus/) is the integrated amplifier module. That means that instead of using traditional components for a digital audio system: DAC - Pre-Amp - Power-Amp you can use just one - Amp+. It has Class-D amplifier on board which provides high quality powerful output: 25W on 4 Ohm speakers. As any other Class-D amplifier it's also very efficient meaning that there is no need to use heat sink or fan.

<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/hardware/amp.jpg|alt=amp]]
</p>

Raspberry Pi 2 feeds digital audio data to Amp+ via [I2S (Integrated Interchip Sound)](https://en.wikipedia.org/wiki/I%C2%B2S) signal. It comes from Raspberry Pi to Amp+ through GPIO connector. This is the same signal which you can find in traditional CD players between the transport and DAC.

Amp+ is ready-to-use right out of the box. You just have to install optional spacers (either your own or those which come with Amp+) on Raspberry Pi.

<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/hardware/pi-spacers.jpg|alt=pi-spacers]]
</p>

Amp+ has 40-pin connector with pins which protrude through the board and allow to connect any other devices which need GPIO signals. Peppy player leverages that connector on Amp+ to connect another external hardware components: [IR Sensor](https://github.com/project-owner/Peppy/wiki/Infrared Sensor), [Rotary Encoders](https://github.com/project-owner/Peppy/wiki/Rotary Encoders) and [Touchscreen](https://github.com/project-owner/Peppy/wiki/Touchscreen). Just remember that [pins used by Amp+](https://www.hifiberry.com/guides/gpio-usage-of-the-hifiberry-products/) should not be used by any other component.

<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/hardware/pi-amp.jpg|alt=pi-amp]]
</p>

After attaching Amp+ to GPIO connector on Raspberry Pi 2 some software configuration should be done to make Amp+ work properly. The details of that process will be covered in the separate [chapter](https://github.com/project-owner/Peppy/wiki/HiFiBerry Amp).

[<<Previous](https://github.com/project-owner/Peppy/wiki/Raspberry Pi 2) | [Next>>](https://github.com/project-owner/Peppy/wiki/Touchscreen)