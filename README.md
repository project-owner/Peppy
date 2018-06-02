## Vermeer Edition 2018.06.02

New features:
* Replaced HiFiBerry Amp+ by HiFiBerry Amp2. That solved audiobooks issues.
* Added CD Player mode.
* Made Home menu customizable.
* Added configuration files for screensavers.
* Refactored VU Meter screensaver.
* Improved logging functionality.
* Bug fixing

## Rembrandt Edition 2018.01.21

New features:
* Switched from custom WebSocket implementation to the Tornado Web Server.
* Implemented Voice Assistant which allows to navigate through menus using voice commands.
* Made a major update of the radio playlists. The number of radio stations increased in two times for all genres and languages.
* Added headless mode. In this mode Peppy Player can work without display/TV connected to Raspberry Pi.
* Created user Gallery where other people can demo their projects based on Peppy Player.
* Bug fixing.

## Bosch Edition 2017.11.05

New features:
* Modified hardware. Now **&#181;Peppy** leverages HiFiBerry MiniAmp for Raspberry Pi Zero.
* Added ability to listen to audiobooks. Books can be selected by genre and author.
* Redesigned screens to simplify navigation.
* Added more information to the wiki pages.
* Bug fixing.

Known issues:

* HiFiBerry Amp+ amplifier used in Peppy Player doesn't support sample rate 22050 Hz. Therefore the audiobooks with this sample rate will sound like white noise. HiFiBerry MiniAmp amplifier used in µPeppy can handle such audiobooks without any issues.

## Caravaggio Edition 2017.05.08

New features:
* Implemented playback of playlists (m3u and cue).
* Added support for 'vlc' player. Now Peppy supports three popular players 'mpd', 'mplayer' and 'vlc'.
* Redesigned communication with audio players.
* Added support for Streaming server and client.
* Updated web radio playlists.
* Bug fixing.

## Raphael Edition 2017.03.12

New features:
* Added File Playback functionality. Both supported players 'mpd' and 'mplayer' provide file playback on Linux and Windows platforms.
* Updated Logo screensaver. In the File Playback mode it will display current album art.
* Updated Slideshow screensaver. In the File Playback mode it will display images from art folder.
* Removed 'mpc' pipe client.
* Bug fixing and code cleanup.

## Michelangelo Edition 2016.09.05

New features:
* Added support for 'mplayer'. Now Peppy UI supports two players 'mpd' and 'mplayer'.
* Added VU Meter screensaver. This screensaver has two native resolutions: 480x320 and 320x240.
* Updated playlists for all languages - removed obsolete links and added new ones.
* Bug fixing and code cleanup.
* The IR issues existed in Leonardo Edition were fixed in hardware.

## Leonardo Edition 2016.03.12

Key features:
* Written in Python. Multi-platform - can run on Linux and Windows.
* Provides Internet radio functionality.
* Supports 'mpd' audio player.
* Can be controlled using mouse, keyboard, touchscreen, rotary encoders, IR remote control and from Web browser.
* Provides playlists for 4 languages and 9 genres.

Known issues:
* IR remote control doesn't work with WiFi network.
* IR remote control doesn't work with animated titles.
* Some radio stations don't work on Linux plarform because of old version of the 'mpd' player.
