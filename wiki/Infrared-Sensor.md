[Infrared Sensor model 1838](http://www.ebay.com/itm/10pcs-Integrated-Infrared-Acceptor-Transducer-HX1838-/250888200539) was used for Peppy player. This sensor doesn't need any additional components (e.g. resistors or capacitors) for connecting to the Raspberry Pi. It can be directly connected to the GPIO pins. The sensor output signal can be connected to any spare GPIO pin. I connected sensor output to the GPIO pin #23 as it's not used neither by Amp+ nor by touchscreen. It was chosen because it's located close to the power pins (+3.3V and Ground). Therefore it's easier to make ribbon cable for this connection - all necessary wires in the cable will be located next to each other. The details of preparing such cable will be discussed in the [cabling](https://github.com/project-owner/Peppy/wiki/Cabling) chapter.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/hardware/ir-1.png|alt=ir-1]]
</p>

The sensor was mounted above the [touchscreen](https://github.com/project-owner/Peppy/wiki/Touchscreen) right in the middle of the front panel. The length of connecting cable/wires is not so critical just don't make it too long.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/hardware/ir-2.jpg|alt=ir-2]]
</p>

Any infrared remote could be used to control Peppy player. I had a spare remote from WD TV Live player so I configured the Peppy player to use that remote. The separate [chapter](https://github.com/project-owner/Peppy/wiki/LIRC) will explain how to configure a remote control for Raspberry Pi 2.

The front panel of the Peppy player is made of the black opaque acrylic glass which blocks infrared signal. That's why the small hole was drilled in the front panel and round window created from a transparent acrylic glass was inserted into that hole and glued to the panel.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/hardware/ir-3.jpg|alt=ir-3]]
</p>

[<<Previous](https://github.com/project-owner/Peppy/wiki/Power Supply) | [Next>>](https://github.com/project-owner/Peppy/wiki/Rotary Encoders)