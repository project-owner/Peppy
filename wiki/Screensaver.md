The Screensaver screen has two menus to change such screensaver settings as Screensaver Type and Screensaver delay. 
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/screensaver.png|alt=screensaver]]
</p>
The Screensaver type can be chosen from the following items:

1. **Clock**.
2. **Logo**.
3. **Slideshow**.

The Screensaver delay is the time of inactivity (no user actions) after which screensaver starts. The delay can be one of the following:

1. **1 minute**.
2. **3 minutes**.
3. **Off**.

###Clock Screensaver###
The Clock screensaver displays the current time using format HH:MM. The clock changes its position every 4 seconds. New time will be displayed when it changes position.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/saver-3.jpg|alt=saver-3]]
</p>

###Logo Screensaver###
The Logo Screensaver displays the current radio station logo. It changes logo position on screen every 4 seconds.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/saver-2.jpg|alt=saver-2]]
</p>

###Slideshow Screensaver###
This screensaver shows images from the folder ```Peppy/screensaver/slideshow/slides```. It shows images in the loop. The delay between images is 6 seconds. If image doesn't fit to the screen it will be scaled so that the whole image is visible on screen.

Each release of the Peppy player will have new set of images for slideshow. Peppy releases will be dedicated to the famous artists. The release will be named after that artist. The paintings of that artist will be placed in the slides folder. For example the first release 'Leonardo' is dedicated to Leonardo Da Vinci and there are three his paintings in the slides folder.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/saver-1.jpg|alt=saver-1]]
</p>
The file names of the images in the slides folder are not hard coded. The program reads all images from that folder. Therefore it's possible to place there your own images. The expected image resolution is 480*320 pixels. The images in this resolution will be displayed on screen without any border. Images in different resolution will be scaled to fit the screen therefore they will have some black borders on some of the sides. The images should be in PNG or JPG formats.

[<<Previous](https://github.com/project-owner/Peppy/wiki/Language) | [Next>>](https://github.com/project-owner/Peppy/wiki/Web UI)
