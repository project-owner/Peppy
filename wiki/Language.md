The Language screen provides menu for switching to new language. Currently Peppy player supports four languages and has radio station playlists for each language/country.

1. **English/USA**
2. **German**
3. **French**
4. **Russian**

<p align="center">
[[https://github.com/project-owner/Peppy/blob/master/wiki/images/software/language.png|alt=language]]
</p>

After switching to new language all UI labels will be displayed using that new language and playlists for new language will be loaded. All labels are placed in the single resource bundle file in UTF-8 format. The Peppy player doesn't check the current locale. It will save current language to the configuration file. When it starts next time the language from the configuration file will define which resource bundle to load.

There is just one font in the player which is used to display text - [FiraSans.ttf](https://github.com/mozilla/Fira/tree/master/ttf). This font supports all four languages used in player - English, German, French and Russian.

[<<Previous](https://github.com/project-owner/Peppy/wiki/Genre) | [Next>>](https://github.com/project-owner/Peppy/wiki/Screensaver)