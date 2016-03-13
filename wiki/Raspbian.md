The Raspbian OS can be installed on SD flash card from several different places:

1. [**Official Raspbian Web Site**](https://www.raspbian.org/).
2. [**HiFiBerry installer**](https://www.hifiberry.com/guides/hifiberry-installer/). It can install many different distributions including Raspbian.
3. [**Adafruit Web Site**](https://learn.adafruit.com/adafruit-pitft-3-dot-5-touch-screen-for-raspberry-pi/easy-install).

I used the Raspbian from the Adafruit Web Site as it has all required configuration settings for the [PiTFT touchscreen](https://github.com/project-owner/Peppy/wiki/Touchscreen) which I bought from the same web site. If I would use the distribution from another place I would need to make all these changes for the touchscreen myself. I used Raspbian Jessie version from September 24 2015. Free software [Win32 Disk Imager](https://sourceforge.net/projects/win32diskimager/) can be used to install Raspbian image on SD flash card. I used 8GB SD flash card.

After inserting SD card and switching power on I connected to the [Raspberry Pi 2](https://github.com/project-owner/Peppy/wiki/Raspberry Pi 2) using Putty and started configuration utility:
```
sudo raspi-config
```
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/rc-1.png|alt=rc-1]]
</p>
I used the following menu items from the raspi-config program:
* Expanded Filesystem (1) so that the whole space on the SD flash card would be available.
* Changed Boot options (3) for booting to console with autologin rather than to the desktop which is default option.
* Changed timezone settings (5)

[<<Previous](https://github.com/project-owner/Peppy/wiki/Software) | [Next>>](https://github.com/project-owner/Peppy/wiki/Adafruit PiTFT)