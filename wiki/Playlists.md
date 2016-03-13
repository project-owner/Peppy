There is separate playlist for each genre and for each language. The playlists contain the direct links to free radio station streams. Here is the example path to English/USA playlist with radio stations for kids:
```
/home/pi/Peppy/stations/en_us/children/children.m3u
```

Each radio station should be defined by three lines in the playlist:

1. **Station index**.
2. **Station name**.
3. **The URL to station stream**.

Here is the example of the playlist content:
```
#0
#Kids Public Radio. Lullaby
http://kidspublicradio2.got.net:8000/lullaby
#1
#Kids Public Radio. Pipsqueaks
http://kidspublicradio2.got.net:8000/pipsqueaks
```

###Station Index##
The number after the comment character defines the order of the radio station in the station menu. The station logo image which is located in the same folder as playlist file should be named after this number. For example for the playlist shown above there are two images for the station logos:
```
/home/pi/Peppy/stations/en_us/children/0.png
/home/pi/Peppy/stations/en_us/children/1.png
```
The station logo image can be of any size. The images for the default stations have resolution 200*200 pixels.

###Station Name###
This name will be displayed in the title bar on the Station Screen. If the name needs character set other than ASCII then the playlist file should be saved in UTF-8 encoding.

###The URL to station stream###
The Peppy player will send this URL to audio player (e.g. Mpd) for playback when corresponding station will be selected in the Station Menu.

[<<Previous](https://github.com/project-owner/Peppy/wiki/Peppy) | [Next>>](https://github.com/project-owner/Peppy/wiki/Peppy Player UI)