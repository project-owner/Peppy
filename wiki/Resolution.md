The default Peppy player resolution is 480*320 pixels. This is the resolution of the [touchscreen](https://github.com/project-owner/Peppy/wiki/Touchscreen) used for the project. It's defined in the [configuration file](https://github.com/project-owner/Peppy/wiki/Peppy#configuration-file) ```config.txt```:
```
[screen.info]
width = 480
height = 320
depth = 32
frame.rate = 30
```
The Peppy player software can support any resolution. There is no limit neither on the low end nor on the high end. The Pygame library doesn't support vector graphics. Therefore it's impossible to use images in SVG format for UI icons. Although the Pygame can scale bitmap images (e.g. in JPG and PNG formats) up and down. The result of scaling images down is acceptable but the images scaled up look blurry. To handle this drawback the Peppy player provides bitmap icons for different screen resolutions. They are placed in three folders:

1. **small**. This folder contains icons for screen width less than 350 pixels.
2. **medium**. This folder contains icons for screen width in range 350-700 pixels.
2. **large**. This folder contains icons for screen width greater than 700 pixels.

Depending on the screen resolution defined in the configuration file Peppy player will load icons from the corresponding folder. The following image shows Peppy player screen with resolution 320x240 pixels:
 
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/scr-1.png|alt=scr-1]]
</p>

And here is example of the screen with resolution 800*480:

<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/scr-4.jpg|alt=scr-4]]
</p>

[<<Previous](https://github.com/project-owner/Peppy/wiki/Web UI) | [Next>>](https://github.com/project-owner/Peppy/wiki/Woodware)