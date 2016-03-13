Download Peppy from ```github```:
```
cd /home/pi
mkdir Peppy
cd Peppy
git init
git pull https://github.com/project-owner/Peppy.git
```
Make sure that Peppy player is working:
```
cd Peppy
sudo python peppy.py
```
When Peppy player starts in invokes Mpc client which in turn launches Mpd player. It should start playing the current radio station defined in Peppy's [configuration file](https://github.com/project-owner/Peppy/wiki/Peppy#configuration-file) ```config.txt```.

To start Peppy player automatically during the system startup add the following commands to the file ```/etc/rc.local```:
```
sleep 10
cd /home/pi/Peppy/
sudo python peppy.py
```
The line ```sleep 10``` is required to let the system load network libraries before starting Peppy player. Without this delay Peppy player will not be able to start Web Server. If you don't use Web UI to control Peppy player you can delete or comment out this line. That will reduce the player startup time.

After all these changes reboot the system:
```
sudo reboot
```
The Peppy player will start playing current radio stream automatically.

To disable all booting messages during startup remove properties ```fbcon=map:10 fbcon=font:VGA8x8``` from the end of line in file ```/boot/cmdline.txt```. The edited line should look like this one:
```
dwc_otg.lpm_enable=0 console=ttyAMA0,115200 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait
```

###Configuration File###
The Peppy player configuration file is located in the root folder ```Peppy/config.txt```. This file contains properties which can control different areas of the player functionality. Some properties in this file are updated by the player during the shutdown operation. Therefore any manual settings for these properties can be overwritten by the player. The following paragraphs will explain the meaning of the properties and their default values.

####screen.info####
The properties in this section allow to define screen information.
```
[screen.info]
width = 480
height = 320
depth = 32
frame.rate = 30
```
The property ```frame.rate``` defines the screen frame rate. 30 frames per second is the default value. This property affects the animation speed of the scrolling title.

####usage####
This section contains properties which can switch on/off different functionality in Peppy player.
```
[usage]
use.lirc = True
use.rotary.encoders = True
use.mpc.player = True
use.mpd.player = False
use.web = True
use.logging = False
```
The property ```use.mpc.player``` activates ```mpc``` client. All ```mpd``` commands in this case will be issued through ```mpc```. The property ```use.mpd.player``` activates the code which sends ```mpd``` commands directly to the TCP/IP socket of the ```mpd``` server. Only one of these properties should be True at the given time either ```use.mpc.player``` or ```use.mpd.player```.

####current####
The properties in this section define which playlist will be loaded and which radio station will start playing upon system startup. This section will be updated by the Peppy player during system shutdown.
```
[current]
mode = radio
language = en_us
playlist = news
station = 0
screensaver = slideshow
screensaver.delay = delay.1
```

####music.server####
This section defines the location of the audio player (e.g. Mpd) and command used to start this player. This information is required only if Peppy player is running on Windows platform. The host and port properties are required only if you defined ```use.mpd.player``` property in the ```usage``` section.
```
[music.server]
folder = C:\\mpd-0.17.4-win32\\bin
command = mpd mpd.conf
host = localhost
port = 6600
```

####web.server####
The only property necessary to configure web server is the port number. The host IP address will be detected by the Peppy player automatically.
```
[web.server]
http.port = 8000
```

####colors####
The colors in this section define the color scheme of the whole UI.
```
[colors]
color.web.bgr = 0,38,40
color.dark = 0,70,75
color.medium = 70,110,120
color.bright = 160,190,210
color.contrast = 255,190,120
color.logo = 20,190,160
```

####font####
The font for Peppy player is located in folder ```Peppy/font/```. It can be changed for any other font and its name should be defined here. This allows to switch between fonts placed in that folder.
```
[font]
font.name = FiraSans.ttf
```

####previous####
This section contains properties which define station numbers for each genre. It is updated upon system shutdown. If you switch to new genre the last played station from that genre will start playing.
```
[previous]
news = 0
culture = 0
retro = 0
children = 0
classical = 0
pop = 0
jazz = 0
rock = 0
contemporary = 0
```

####order sections####
The properties in these sections define the order of menu items in different screens.
```
[order.home.menu]
radio = 1
screensaver = 2
language = 3
about = 4
hard.drive = 5
stream = 6
```
```
[order.language.menu]
en_us = 1
de = 2
fr = 3
ru = 4
```
```
[order.genre.menu]
news = 1
culture = 2
retro = 3
children = 4
classical = 5
pop = 6
jazz = 7
rock = 8
contemporary = 9
```
```
[order.screensaver.menu]
clock = 1
logo = 2
slideshow = 3
```
```
[order.screensaver.delay.menu]
delay.1 = 1
delay.3 = 2
delay.off = 3
```

[<<Previous](https://github.com/project-owner/Peppy/wiki/Pylirc) | [Next>>](https://github.com/project-owner/Peppy/wiki/Playlists)