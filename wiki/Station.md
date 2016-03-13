The Station Screen has two modes:

1. **Station Mode**. In this mode current station logo displayed in the center of the screen.
2. **Page Mode**. In this mode the Station menu displayed on screen.

###Station Mode###
Peppy player will display this screen upon startup.

<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/stations.png|alt=stations]]
</p>

###Page Mode###
Player switches to the Page Mode after clicking on the current station logo. In this mode Station menu will be displayed and the selection frame will be displayed on top of the current station. Another difference between Station Mode and Page Mode is navigation buttons. 

<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/page.png|alt=page]]
</p>

###Common Buttons###
Both modes Station and Page have the following common buttons:

* **Shutdown Button**. This toggle button should be clicked twice in order to shutdown the player. This is done to exclude accidental shutdown. If between these two clicks any other button will be clicked the shutdown action will be canceled. Upon the second click of the Shutdown Button Peppy player issues the following command (Linux platform):
_**sudo poweroff**_. This is the recommended way to switch off the player because only during this process the player saves the current settings which include: current language, current genre and current station.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/shutdown.png|alt=shutdown]]
</p>

* **Genre Button**. The icon of the Genre Button shows the current genre. Genre Screen will be displayed in place of Station Screen after clicking on Genre Button.

* **Home Button**. The Home Screen will be displayed after clicking on this button.

* **Play/Pause Button**. This button provides functionality to control audio playback. Clicking on this button switches playback mode from Play to Pause and back.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/play-pause.png|alt=play-pause]]
</p>

###Navigation Buttons###
Navigation buttons have different functionality in different modes.
* **Navigation Left**. This button serves two purposes: to switch to the station located on the left side from the current station and to display the number of stations on the left side from the current station.

* **Navigation Right**. This button serves the same purposes as the previous button but for the right side.

* **Navigation Page Left**. This button switches to the next page of stations on the left side.

* **Navigation Page Right**. This button switches to the next page of stations on the right side.

###Title Bar###
After switching from one station to another this component shows the name of newly selected station. If radio station doesn't provide the artist and song names the station name will be displayed all the time. The station name comes from the playlist file.

The Title Bar dynamically adjusts the way of displaying information depending on the size of the displayed string. There are four modes of displaying information in the title bar:

1. The string will be displayed using the default font size if it fits to the screen width.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/title-1.png|alt=title-1]]
</p>

2. If the string displayed with default font size doesn't fit into the screen width the font size will be reduced. The string with reduced font size will be displayed if it fits into the screen width.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/title-2.png|alt=title-2]]
</p>

3. If the string with reduced font size doesn't fit into the screen width then the string will be broken into two parts: artist name which will be displayed as the first string and song name which will be displayed under the first string. 
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/title-3.png|alt=title-3]]
</p>

4. If the strings in the previous approach don't fit into the screen width then the string will displayed using the default font and the string will be animated.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/title-4.png|alt=title-4]]
</p>

###Volume Bar###
The Volume control component serves two purposes: to adjust volume level and to mute sound. There are two ways to adjust volume level. One way is to click on the volume knob and holding the mouse button down drag the knob to the desired position. Another way is just to click on the Volume Bar in the desired position. The knob will jump to that position and the volume level will be changed accordingly.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/volume-1.png|alt=volume-1]]
</p>

The single click on the volume knob will mute the sound.
<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/volume-2.png|alt=volume-2]]
</p>

[<<Previous](https://github.com/project-owner/Peppy/wiki/Home Screen) | [Next>>](https://github.com/project-owner/Peppy/wiki/Genre)

