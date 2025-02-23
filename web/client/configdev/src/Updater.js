/* Copyright 2019-2023 Peppy Player peppy.player@gmail.com
 
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

import { configSections } from "./tabs/ConfigTab";
import { playersSections } from "./tabs/PlayersTab";
import { screensaversSections } from "./tabs/ScreensaversTab";
import { defaultsSections } from "./config/Default"
import { createPlaylist, DEFAULT_STATION_IMAGE, DEFAULT_STREAM_IMAGE, createText } from "./Fetchers";
import { homeMenuItems } from "./config/HomeScreen";

export function updateConfiguration(caller, name, value, index) {
  const newState = Object.assign({}, caller.state.parameters);
  let section = configSections[caller.state.currentMenuItem];

  if (caller.state.tabIndex === 1) { // Screens
    if (caller.state.currentMenuItem === 0) { // Home
      if (homeMenuItems.includes(name)) {
        section = "home.menu";
      } else {
        section = "home.navigator";
      }
    } else if (caller.state.currentMenuItem === 1) { // Screensaver
      if (name === "screensaver.delay") {
        section = "screensaver.delay";
        name = "delay";
      } else {
        section = "screensaver.menu";
      }
    } else if (caller.state.currentMenuItem === 2) { // Languages Menu
      section = "languages.menu";
    } else if (caller.state.currentMenuItem === 3) { // Collection Menu
      section = "collection.menu";
    } else if (caller.state.currentMenuItem === 4) { // Player
      section = "player.screen";
    } else if (caller.state.currentMenuItem === 5) { // File Browser
      section = "file.browser";
    }
  }

  if (section.length === 0) {
    newState[name] = value;
  } else {
    if (index === undefined) {
      newState[section][name] = value;
    } else {
      newState[section][name][index] = value;
    }
  }
  newState.parametersDirty = true;
  caller.setState({
    parameters: newState,
    parametersDirty: true
  });
}

export function updatePlayers(caller, name, value) {
  const newState = Object.assign({}, caller.state.players);
  const section = playersSections[caller.state.currentMenuItem];
  newState[section][name] = value;
  caller.setState({ 
    players: newState,
    playersDirty: true
  });
}

export function updateBackground(caller, name, value) {
  const newState = Object.assign({}, caller.state.background);
  newState[name] = value;
  caller.setState({ 
    background: newState,
    backgroundDirty: true
  });
}

export function updateScreensavers(caller, name, value) {
  const newState = Object.assign({}, caller.state.screensavers);
  const section = screensaversSections[caller.state.currentMenuItem];

  if (section === "random" && name !== "update.period") {
    let newArray = [];
    let newString = "";
    const currentString = caller.state.screensavers.random.savers;

    screensaversSections.forEach((saver) => {
      if (currentString.includes(saver)) {
        if (!(saver === name && value === false)) {
          newArray.push(saver);
        }
      } else {
        if (saver === name && value === true) {
          newArray.push(saver);
        }
      }
    })

    for (let i = 0; i < newArray.length; i++) {
      newString += newArray[i];
      if (i < (newArray.length - 1)) {
        newString += ",";
      }
    }
    newState[section]["savers"] = newString;
  } else if (section === "horoscope") {
    newState["horoscope"]["zodiac"][name] = value;
  }  else {
    newState[section][name] = value;
  }
  caller.setState({
    screensavers: newState,
    screensaversDirty: true
  });

}

export function updatePlaylists(caller, value) {
  const newState = Object.assign({}, caller.state.playlists);
  newState[caller.state.language][caller.getRadioPlaylistMenu()[caller.state.currentMenuItem]] = value;

  const text = createText(value);
  const newText = Object.assign({}, caller.state.playlistsTexts);
  newText[caller.state.language][caller.getRadioPlaylistMenu()[caller.state.currentMenuItem]] = text;

  caller.setState({
    playlists: newState,
    playlistsTexts: newText,
    playlistsDirty: true
  });
}

export function updateFilePlaylists(caller, value) {
  caller.setState({
    currentFilePlaylistName: value,
    currentFilePlaylist: null
  });
}

export function updatePodcasts(caller, value) {
  caller.setState({
    podcasts: value,
    podcastsDirty: true
  });
}

export function updateStreams(caller, value) {
  const text = createText(value);
  caller.setState({
    streams: value,
    streamsText: text,
    streamsDirty: true
  });
}

export function updateYaStreams(caller, value) {
  caller.setState({
    yastreams: value,
    yastreamsDirty: true
  });
}

export function updateJukebox(caller, value) {
  caller.setState({
    jukebox: value,
    jukeboxDirty: true
  });
}

export function updatePlaylistText(caller, text) {
  const playlist = caller.state.playlists[caller.state.language][caller.getRadioPlaylistMenu()[caller.state.currentMenuItem]];
  const items = createPlaylist(text, DEFAULT_STATION_IMAGE, caller.state.playlistBasePath, playlist);
  const newState = Object.assign({}, caller.state.playlists);
  newState[caller.state.language][caller.getRadioPlaylistMenu()[caller.state.currentMenuItem]] = items;

  const newText = Object.assign({}, caller.state.playlistsTexts);
  newText[caller.state.language][caller.getRadioPlaylistMenu()[caller.state.currentMenuItem]] = text;

  caller.setState({
    playlistsTexts: newText,
    playlists: newState,
    playlistsDirty: true,
  });
}

export function updateStreamsText(caller, text) {
  const items = createPlaylist(text, DEFAULT_STREAM_IMAGE, caller.state.streamsBasePath, caller.state.streams);
  caller.setState({
    streamsText: text,
    streams: items,
    streamsDirty: true
  });
}

export function updateDefaults(caller, name, value) {
  const index = defaultsSections.indexOf(name);
  const newState = Object.assign({}, caller.state.system);
  const defaults = newState.defaults;
  defaults[index] = value;

  caller.setState({
    defaults: newState
  });
}

export function updateTimezone(caller, name, value) {
  const newState = Object.assign({}, caller.state.system);

  const timezone = newState.timezone;
  if (name === "area") {
    timezone.currentArea = value;
    timezone.currentCity = timezone.areaCities[value][0];
  } else if (name === "city") {
    timezone.currentCity = value;
  }
  
  caller.setState({
    system: newState
  });
}

export function updateNas(caller, name, value, index) {
  const newState = Object.assign({}, caller.state.system);

  const nases = newState.nases;
  let nas = nases[index];
  nas[name] = value;

  caller.setState({
    system: newState,
    nasDirty: true
  });
}

export function updateShare(caller, name, value, index) {
  const newState = Object.assign({}, caller.state.system);
  const shares = newState.shares;
  let share = shares[index];
  if(name === "") {
    name = "options";
  }
  share[name] = value;

  caller.setState({
    system: newState,
    shareDirty: true
  });
}

export function updateVaconfig(caller, name, value) {
  const newState = Object.assign({}, caller.state.system);

  const config = newState.vaconfig;
  config[name] = value;

  caller.setState({
    system: newState,
    vaconfigDirty: true
  });
}

export function updateVoskModels(caller, name, value) {
  const newState = Object.assign({}, caller.state.system);

  const config = newState.voskModels;
  config[name] = value;

  caller.setState({
    system: newState,
    voskModelsDirty: true
  });
}

export function updateDevices(caller, name) {
  const newState = Object.assign({}, caller.state.devices);

  Object.keys(newState).forEach((key) => {
    newState[key][0] === name ? newState[key][2] = true : newState[key][2] = false;
  })

  caller.setState({
    system: newState,
    devicesDirty: true
  });
}
