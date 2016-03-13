The following image shows all hardware ingredients which I used for the Peppy player. The directions for using each ingredient will be discussed in detail in separate chapters. I'll also provide the links to web sites where you can buy these components. Please don't consider it as advertisements as I don't work for those companies. Also be aware that availability of the component today doesn't mean that it will be available tomorrow. Though I'll try to keep these links up-to-date. You can definitely use another appropriate components but this document will describe installation and configuration of the particular hardware components shown below.

<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/hardware/hardware.jpg|alt=Hardware]]
</p>

1. [**Power Supply**](https://github.com/project-owner/Peppy/wiki/Power Supply). This is very important component in any project. Under-powering your system can cause many intermittent problems. Therefore I recommend to use good power supply which can provide more energy than your system requires. Over-powering doesn't hurt as your system will take only energy which it needs.

2. [**PiTFT Touchscreen**](https://github.com/project-owner/Peppy/wiki/Touchscreen). This is the main controlling and navigation tool in Peppy. The software can work with screen of any size/resolution. But I recommend to use the screen of size 3.5" and resolution 480*320 minimum. I've tried 2.8" screen and found it a bit small at least for my fingers. There is no limit on higher end just make sure that it will either fit into your existing enclosure or build new one accordingly.

3. [**Illuminated Power push-button**](https://github.com/project-owner/Peppy/wiki/Power Supply). Make sure that you buy button with diameter 19 mm. There is similar one with diameter 16 mm but it's suitable only for child's fingers.

4. [**Amplifier HiFiBerry Amp+**](https://github.com/project-owner/Peppy/wiki/Amplifier). This module converts I2S digital signal coming from Raspberry Pi into the analog signal appropriate for feeding speakers.

5. [**Raspberry Pi 2**](https://github.com/project-owner/Peppy/wiki/Raspberry Pi 2). There are several models of this single-board computer. The model 2 has much better performance over its previous models because of more powerful CPU. This document will discuss the usage of model 2 only.

6. [**Rotary Encoders**](https://github.com/project-owner/Peppy/wiki/Rotary Encoders). Even though the GUI on Touchscreen can provide a volume control I found using traditional rotary encoders more convenient for this task as those light clicks provide much better feedback during volume control. The rotary encoders used for Peppy project also have push-button functionality. That makes possible to mute sound using one rotary encoder and select station by pushing another rotary encoder.

7. [**Infrared Sensor**](https://github.com/project-owner/Peppy/wiki/Infrared Sensor). This sensor connected directly to the Raspberry Pi allows to control Peppy player using any remote control which you have in your disposal.

8. [**Speakers**](https://github.com/project-owner/Peppy/wiki/Speakers). Amplifier board provides 25 W output. Therefore your speakers should have wattage close to this number. The Sony speakers used for Peppy provide 30 W. Another factor which you have to consider while choosing speakers for your system is the size of the case/enclosure where you are going to install the speakers.

9. [**Passive Radiators**](https://github.com/project-owner/Peppy/wiki/Passive Radiators). There are several ways how you can handle the back side of your speaker system: do nothing and keep it open, use sound port or use passive radiators. I used the latter method as the former ones either look not so attractive (though probably provide better acoustics) or tend to collect dust and insects ;)

The following images shows the tools which were used while making Peppy player hardware. The images just give you the idea what you will need if you will decide to work on the similar project. You can definitely use any other tools which you have in your disposal.

### Mechanical Tools
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/hardware/h-tools.jpg|alt=h-tools]]
</p>

1. [**Pliers**](http://www.amazon.com/gp/product/B007HGNRQ4). This tools is handy either when you need much stronger fingers for example to tighten nuts or whenever you need much longer fingers - when you have to reach a place not reachable by your fingers.

2. [**Phillips Screwdriver**](http://www.amazon.com/gp/product/B000XDNSQ2). This tool is to handle large screws with phillips head. Such screws were used to attach speakers, passive radiators, front and back panels.

3. [**Tweezers**](http://www.amazon.com/Woodstock-D3288-Tweezer-Set-6-Piece/dp/B001N1FR3A). There are many situation when you need tweezers. The most common situation is when you need to hold very small screws, bolts and nuts. Another typical case is to protect your fingers when you hold the component which you are soldering.

4. [**Hobby Knife**](http://www.amazon.com/Xacto-X5282-Basic-Knife-Set/dp/B00004Z2UB). This tool is very helpful to remove cable plastic insulation.

5. [**Small Flat Head Screwdriver**](http://www.amazon.com/Stanley-66-039-Jewelers-Precision-Screwdriver/dp/B00002X29G). To tighten the screws on the Amp+ connector you need this tool.

6. [**Small Phillips Head Screwdriver**](http://www.amazon.com/Stanley-66-039-Jewelers-Precision-Screwdriver/dp/B00002X29G). Almost all hardware components in Peppy player were mounted using this screwdriver which can handle small (2-3 mm) screws with Phillips head.

7. **Hexagonal Spanner**. This tools is required to tighten screws in the aluminum knobs attached to the rotary encoders.

8. **Wire Cutters**. This is a must-have tool for any electronic project. It's used to cut wires and to shorten pins of the electronic components.

### Electrical tools.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/hardware/e-tools.jpg|alt=e-tools]]
</p>

There are two main electrical tools which I needed to assemble the hardware part of the Peppy player:

1. [**Soldering Iron**](http://www.amazon.com/gp/product/B000AS28UC). The iron is mostly necessary to prepare GPIO cable which connects infrared sensor and rotary encoders. 

2. [**Multimeter**](http://www.ebay.com/itm/LCD-Display-Digital-Ammeter-Voltmeter-Ohmmeter-Capacimeter-Multitester-w-Lead-/321883656749). This tool is used to define DC polarity, to make sure that voltage from power supply is correct and to find out the proper wires either in the cables or connectors.

[<<Previous](https://github.com/project-owner/Peppy/wiki/Home) | [Next>>](https://github.com/project-owner/Peppy/wiki/Raspberry Pi 2)