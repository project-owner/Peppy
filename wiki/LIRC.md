The LIRC is required if you are going to control Peppy player using Infrared Remote Control. To check that LIRC is installed on your system run the program 'irw' which comes with LIRC (this is the program for testing IR remote):
```
pi@raspberrypi ~ $ irw
-bash: irw: command not found
```
I installed Raspbian from Adafruit web site and in my case LIRC was not included into the Raspbian distro. To install LIRC run the following command:
```
sudo apt-get install lirc
``` 
This command will install LIRC libraries and it will create folder ```/etc/lirc``` with default files in it:
```
pi@raspberrypi ~ $ ls /etc/lirc
hardware.conf  lircrc  lircd.conf
```
You should prepare your own files and replace the default files. There are many [tutorials](http://alexba.in/blog/2013/01/06/setting-up-lirc-on-the-raspberrypi/) in the Internet explaining how to create these files. You can use my files created for WD TV Live remote for reference:

* [**hardware.conf**](https://github.com/project-owner/Peppy/blob/master/files/hardware.conf)
* [**lircd.conf**](https://github.com/project-owner/Peppy/blob/master/files/lircd.conf)
* [**lircrc**](https://github.com/project-owner/Peppy/blob/master/files/lircrc)

To test LIRC run the program 'irw' again and press buttons on your remote. You should see the output in the console:
```
pi@raspberrypi ~ $ irw
00000000219e10ef 00 KEY_OK WD_TVLIVE
00000000219ea05f 00 KEY_UP WD_TVLIVE
00000000219e00ff 00 KEY_DOWN WD_TVLIVE
```
Finally you have to modify file ```/boot/config.txt```. Remove comments from line with ```dtoverlay=lirc-rpi``` and add GPIO pin number which will receive signal from IR sensor. In my case it's GPIO pin #23:
```
dtoverlay=lirc-rpi,gpio_in_pin=23
```
If you don't provide pin number the [Amp+](https://github.com/project-owner/Peppy/wiki/Amplifier) will not work because it's using GPIO pin #18. LIRC is using the same pin by default. 

[<<Previous](https://github.com/project-owner/Peppy/wiki/Mpd & Mpc) | [Next>>](https://github.com/project-owner/Peppy/wiki/Pylirc)