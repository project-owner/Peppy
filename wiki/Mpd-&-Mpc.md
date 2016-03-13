The following command installs Mpd player in folder /usr/bin/mpd
```
sudo apt-get install mpd
```
Then set Mpd mixer type to 'software' to control volume through Mpd. For that uncomment the line with mixer_type in file /etc/mpd.conf:
```
audio_output {
        type            "alsa"
        name            "My ALSA Device"
#       device          "hw:0,0"        # optional
        mixer_type      "software"      # optional
#       mixer_device    "default"       # optional
#       mixer_control   "PCM"           # optional
#       mixer_index     "0"             # optional
```
After installing Mpd it's automatically configured as a service and it will start every time the Raspberry Pi starts. In order to have full control on Mpd player it's better to stop Mpd service and disable it from starting upon system startup
```
sudo service mpd stop
sudo update-rc.d mpd disable
```
Peppy player can control Mpd audio player using Mpc client. To install Mpc run this command:
```
sudo apt-get install mpc
```

[<<Previous](https://github.com/project-owner/Peppy/wiki/Pygame) | [Next>>](https://github.com/project-owner/Peppy/wiki/LIRC)