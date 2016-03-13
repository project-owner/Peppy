[Rotary encoders](https://en.wikipedia.org/wiki/Rotary_encoder) (RE) look a bit awkward on the modern devices which we usually used to control from touchscreens. But I found it more convenient and intuitive to use RE for volume control than touchscreen. The latter is good for visual feedback of your RE actions. Also when the touchscreen is in screensaver mode and volume control UI component is not visible then RE is also the best way to change the volume.

[The Rotary Encoders](http://www.ebay.com/itm/New-10pcs-12mm-Rotary-Encoder-Push-Button-Switch-Keyswitch-Electronic-Components-/331262931119) which were used for Peppy player can be connected directly to the Raspberry Pi's GPIO pins. Each RE needs four GPIO pins. One of these pins is Ground and the rest are signal pins. There is no need to connect positive power voltage to the RE as GPIO pins in Raspberry Pi can be programmatically configured to use pull-up resistors which connect the pin to the positive voltage through resistor.

The following diagram shows which GPIO pins were used for this connection. The GPIO pins which are not in use by another components and which are close to each other were selected. It's easier to make [connection cable](https://github.com/project-owner/Peppy/wiki/Cabling) when the  pins/wires are grouped together.

<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/hardware/re-1.png|alt=re-1]]
</p>

The RE used for Peppy player have push-button functionality. One push-button serves for mute and the other for menu item selection functionality. Each push-button has two contacts - one for Ground and the other for Signal. Therefore to simplify the connection cable just one Ground signal from GPIO can be used and two Ground pins can be connected to each other on the RE itself. You can see that connection (copper wire) between Ground pins in the following image. [Two black aluminum knobs](http://www.ebay.com/itm/2PCS-25-18mm-Generic-Black-Solid-Aluminum-Knob-W-Black-Ring-FR-Potentiometer-Amp-/321039102439) attached to the REs provide nice inertia while adjusting the volume level or tuning radio station because of their heavy weight.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/hardware/re-2.jpg|alt=re-2]]
</p>

The usage of REs don't need any changes in the system configuration files. Peppy software handles all RE functionality.

[<<Previous](https://github.com/project-owner/Peppy/wiki/Infrared Sensor) | [Next>>](https://github.com/project-owner/Peppy/wiki/Other Control Devices)