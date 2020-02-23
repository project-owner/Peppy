## Hogarth Edition 2020.02.23

New features:
* Implemented Audio Files Collection functionality.
* Automated the connection process of Bluetooth devices.
* Added Playback Order and Information popup menus.
* The majority of screensavers are available in Web UI now.
* Added support for 'mpv' media player.
* Implemented support for GPIO buttons.

## Cranach Edition 2019.12.04

New features:
* Implemented Advanced Playlist Editor in the Configuration Web UI.
* Show images embedded into MP3 and FLAC files.
* Support AirPlay.
* Support Spotify Connect.
* Added two new languages: Italian and Spanish.
* Check for updates.
* Added ability to configure rotary encoders from the Configuration Web UI.

## Holbein Edition 2019.09.01

New features:
* Implemented Web UI for Peppy player configuration.
* Added new functionality for connecting to a Wi-Fi network.
* Made Home Navigator configurable.
* Added 'Start Now' option to the Screensaver navigator.
* Provided new disk image for the Official 7" Touchscreen.
* Fixed the issues in the mpd playback and audiobooks.

## Dürer Edition 2019.03.08

New features:
* Implemented support for Podcasts.
* Added PWM output to VU Meter.
* Added support for user-defined statrup and shutdown scripts.
* Fixed the issue with Weather Screensaver.

Known issues:

* There is noticeable slowness when VLC player is in use with VU Meter ALSA plugin. To prevent the issue VU Meter Screensaver was configured to use the 'noise' data source instead of 'pipe'.


## El Greco Edition 2019.01.01

New features:
* Added new resolution (800*480) to the VU Meter screensaver.
* Implemented Radio Favorites.
* Added timer functionality.
* Implemented song lyrics screensaver.
* Implemented random screensaver.
* Provided new disk image for Waveshare 2.8" touchscreen.

## Goya Edition 2018.10.31

New features:
* Refactored VU Meter screensaver.
* Added Spectrum Analyzer screensaver.
* Modified Weather screensaver.
* Added Recursive Playback mode.
* Introduced the flag disabling automatic playback upon startup.
* Improved support for SVG icons.
* Fixed issues in Logo screensaver and Audiobooks playback.

## Velázquez Edition 2018.08.26

New features:
* Replaced all icons by SVG images.
* Added functionality which will display album art for all radio stations which provide information about current artist and song.
* Implemented Equalizer UI.
* Added pagination for radio groups.
* Provided new disk image for Waveshare 5" touchscreen.
* Added support for m3u playlists with absolute filenames.

## Rubens Edition 2018.07.22

New features:
* Streamlined the process of adding new languages.
* Added CD album art functionality.
* Made Screensaver and Language menus customizable.
* Implemented Weather forecast screensaver.
* Added information about connecting Bluetooth devices.
* Provided disk images.

## Vermeer Edition 2018.06.02

New features:
* Replaced HiFiBerry Amp+ by HiFiBerry Amp2. That solved audiobooks playback issues.
* Added CD Player mode.
* Made Home menu customizable.
* Added configuration files for screensavers.
* Refactored VU Meter screensaver.
* Improved logging functionality.
* Provided disk images to simplify player installation and configuration.

## Rembrandt Edition 2018.01.21

New features:
* Switched from custom WebSocket implementation to the Tornado Web Server.
* Implemented Voice Assistant which allows to navigate through menus using voice commands.
* Made a major update of the radio playlists. The number of radio stations increased in two times for all genres and languages.
* Added headless mode. In this mode Peppy Player can work without display/TV connected to Raspberry Pi.
* Created user Gallery where other people can demo their projects based on Peppy Player.

## Bosch Edition 2017.11.05

New features:
* Modified hardware. Now **&#181;Peppy** leverages HiFiBerry MiniAmp for Raspberry Pi Zero.
* Added ability to listen to audiobooks. Books can be selected by genre and author.
* Redesigned screens to simplify navigation.
* Added more information to the wiki pages.

Known issues:

* HiFiBerry Amp+ amplifier used in Peppy Player doesn't support sample rate 22050 Hz. Therefore the audiobooks with this sample rate will sound like white noise. HiFiBerry MiniAmp amplifier used in µPeppy can handle such audiobooks without any issues.

## Caravaggio Edition 2017.05.08

New features:
* Implemented playback of playlists (m3u and cue).
* Added support for 'vlc' player. Now Peppy supports three popular players 'mpd', 'mplayer' and 'vlc'.
* Redesigned communication with audio players.
* Added support for Streaming server and client.
* Updated web radio playlists.

## Raphael Edition 2017.03.12

New features:
* Added File Playback functionality. Both supported players 'mpd' and 'mplayer' provide file playback on Linux and Windows platforms.
* Updated Logo screensaver. In the File Playback mode it will display current album art.
* Updated Slideshow screensaver. In the File Playback mode it will display images from art folder.
* Removed 'mpc' pipe client.

## Michelangelo Edition 2016.09.05

New features:
* Added support for 'mplayer'. Now Peppy UI supports two players 'mpd' and 'mplayer'.
* Added VU Meter screensaver. This screensaver has two native resolutions: 480x320 and 320x240.
* Updated playlists for all languages - removed obsolete links and added new ones.
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
