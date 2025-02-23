/* Copyright 2024 Peppy Player peppy.player@gmail.com
 
This file is part of Peppy Player.
 
Peppy Player is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
Peppy Player is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with Peppy Player. If not, see <http://www.gnu.org/licenses/>.
*/

export let State = {
    webSocket: null,
    mode: null,
    modeIconUrl: null,
    modeIcons: null,
    modeNames: null,
    image: null,
    track: null,
    album: null,
    artist: null,
    station: null,
    pause: null,
    volume: null,
    openHome: false,
    openRadioPlaylist: false,
    openRadioBrowser: false,
    openFileBrowser: false,
    openTrack: false,
    openVolume: false,
    openGenre: false,
    config: null,
    info: null,
    metadata: null,
    mute: false,
    title: null,
    time: null,
    timeSliderPosition: null,
    timeStep: null,
    running: true,
    totalTime: null,
    currentTime: null,
    language: null,
    labels: null,
    genre: null,
    genres: null,
    genreIcons: null,
    genreIconsSelected: null,
    radioPlaylist: null,
    lyrics: null,
    files: null,
    currentFolder: null,
    currentFile: null,
    currentFileIndex: null,
    fileBrowserMode: 'file',
    filePlaylists: null,
    filePlaylist: null,
    currentPlaylistFile: null,
    currentPlaylistFileIndex: null,
    radioBrowserCountries: null,
    radioBrowserCategory: null,
    currentRadioBrowserStationIndex: null,
    radioBrowserStations: null
};