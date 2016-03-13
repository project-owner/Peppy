[The HiFiBerry web site](https://www.hifiberry.com/guides/configuring-linux-3-18-x/) explains all steps required to install and configure the software for HiFiBerry Amp+ amplifier. I've got the driver for Amp+ with Raspbian Jessie which I downloaded from the Adafruit web site. There are still some steps required to complete the amplifier configuration.

Add the following line to file ```/boot/config.txt```:
```
dtoverlay=hifiberry-amp
```

Create file ```/etc/asound.conf``` with the following content:
```
pcm.!default  {
 type hw card 0
}
ctl.!default {
 type hw card 0
}
```

Either remove or comment out the line ```snd_bcm2835``` in file ```/etc/modules```. That will disable on-board [Raspberry Pi 2](https://github.com/project-owner/Peppy/wiki/Raspberry Pi 2) audio system. Reboot the system:
```
sudo reboot
```

Verify that AMP+ was configured properly by running the following program:
```
aplay -l
```
The output from that program should look like this:
```
**** List of PLAYBACK Hardware Devices ****
card 0: sndrpihifiberry [snd_rpi_hifiberry_amp], device 0: HifiBerry AMP HiFi tas5713-hifi-0 []
  Subdevices: 1/1
  Subdevice #0: subdevice #0
```

By default the volume level will be set to 100% which is very loud level. Use ```amixer``` to reduce the volume level:
```
amixer sset Master 70%
```
The volume range of the audio player (e.g. Mpd) will be restricted by this setting. Its maximum (100%) will not be louder than defined by ```amixer``` (70%).

<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/mpd.png|alt=mpd]]
</p>

To test amplifier and speakers run ```speaker-test``` program:
```
speaker-test -Dhw -c2 -tsine -f200
```

[<<Previous](https://github.com/project-owner/Peppy/wiki/Adafruit PiTFT) | [Next>>](https://github.com/project-owner/Peppy/wiki/Python)
