/* Copyright 2019-2020 Peppy Player peppy.player@gmail.com
 
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

import { fileBrowserSections } from "./config/FileBrowser";
import { logSections } from "./config/Logging";
import { configSections } from "./tabs/ConfigTab";

export const DEFAULT_STATION_IMAGE = "default/default-station.png";
export const DEFAULT_STREAM_IMAGE = "default/default-stream.png";

export function getParameters(caller) {
  if (caller.state.parameters) {
    return;
  }

  fetch("/parameters").then(function (response) {
    return response.json();
  }).then((json) => {
    let params = { ...json };
    prepareLogging(params);
    prepareFileBrowser(params);
    preparePodcasts(params);
    prepareFont(params);
    caller.setState({
      parameters: params,
      language: json.current.language,
      labels: json.labels,
      playerWasRebooted: false
    });
    changeLanguage({ target: { value: json.current.language } }, caller);
    setFlags(params.languages, caller);
    caller.colorBackup = JSON.parse(JSON.stringify(json.colors));
  }).catch(function (err) {
    console.log('Fetch problem: ' + err.message);
  });
}

export function getBackground(caller) {
  if (caller.state.background) {
    return;
  }

  fetch("/bgr").then(function (response) {
    return response.json();
  }).then((json) => caller.setState({ background: { ...json } })).catch(function (err) {
    console.log('Fetch problem: ' + err.message);
  });
}

function prepareLogging(params) {
  const logSection = {};

  logSections.forEach((section) => {
    logSection[section] = params["usage"][section];
    delete params["usage"][section];
  });
  params["logging"] = logSection;
}

function prepareFileBrowser(params) {
  const fileBrowserSection = {};
  fileBrowserSections.forEach((section) => {
    fileBrowserSection[section] = params[section];
    delete params[section];
  });
  params["file.browser"] = fileBrowserSection;
}

function preparePodcasts(params) {
  const podcastsSection = {
    "podcasts.folder": params["podcasts.folder"]
  }
  params["podcasts"] = podcastsSection;
}

function prepareFont(params) {
  const fontSection = {
    "font.name": params["font.name"]
  }
  params["font"] = fontSection;
}

export function getPlayers(caller) {
  if (caller.state.players) {
    return;
  }
  fetch("/players").then(function (response) {
    return response.json();
  }).then((json) => caller.setState({ players: { ...json } })).catch(function (err) {
    console.log('Fetch problem: ' + err.message);
  });
}

export function getScreensavers(caller) {
  if (caller.state.screensavers) {
    return;
  }
  fetch("/savers").then(function (response) {
    return response.json();
  }).then((json) => caller.setState({ screensavers: { ...json } })).catch(function (err) {
    console.log('Fetch problem: ' + err.message);
  });
}

function findImage(basePath, item) {
  const imagePathPng = basePath + item.name + ".png";
  const imagePathJpg = basePath + item.name + ".jpg";

  return fetch(imagePathPng, { method: 'HEAD' }).then(res => {
    if (res.ok) {
      item.imagePath = imagePathPng;
    } else {
      return fetch(imagePathJpg, { method: 'HEAD' }).then(res => {
        if (res.ok) {
          item.imagePath = imagePathJpg;
        }
      });
    }
  }).catch(err => console.log('Error:', err));
}

function getCurrentItem(currentItems, name) {
  for (let n=0; n<currentItems.length; n++) {
    if (currentItems[n].name === name) {
      return currentItems[n];
    }
  }
  return undefined;
}

export function createPlaylist(lines, defaultImage, basePath, currentItems) {
  if (!lines) {
    return null;
  }
  let linesArray = lines.split("\n");
  let items = [];
  let item = {};

  for (let i = 0; i < linesArray.length; i++) {
    if (linesArray[i].trim().length === 0) {
      continue;
    }
    if (linesArray[i].trim().startsWith("#")) {
      item = {};
      const name = linesArray[i].substr(1).trim();
      if (name.length > 0) {
        item.name = name;
      }
    } else {
      if (item) {
        let currentItem = undefined;
        if (currentItems) {
          currentItem = getCurrentItem(currentItems, item.name);
        }

        item.link = linesArray[i].trim();
        item.play = false;
        item.edit = false;

        if (currentItem) {
          item.image = currentItem.image;
          item.imagePath = currentItem.imagePath;
        } else {
          item.image = undefined;
          item.imagePath = defaultImage;
        }

        item.basePath = basePath;
        items.push(item);
      }
    }
  }
  return items;
}

export function createText(items) {
  let text = "";
  for (let n = 0; n < items.length; n++) {
    const item = items[n];
    text += "#" + item.name + "\n";
    text += item.link + "\n";
  }
  return text;
}

function getFolder(caller) {
  let folder = "";
  const languages = caller.state.parameters.languages;

  for (let n=0; n<languages.length; n++) {
    const lang = languages[n];
    if (lang.name === caller.state.language) {
      folder = Object.keys(lang.stations)[0];
      break;
    }
  }

  return folder;
}

export function getRadioPlaylist(caller, index) {
  if (index === undefined) {
    index = 0;
  }

  const genre = caller.getRadioPlaylistMenu()[index];

  if (caller.state.playlists[caller.state.language] !== undefined &&
    caller.state.playlists[caller.state.language][genre] !== undefined) {
    return;
  }

  const folder = getFolder(caller);
  fetch("/playlists?language=" + caller.state.language + "&genre=" + genre + "&folder=" + folder).then(function (response) {
    return response.json();
  }).then((json) => {
    const newState = Object.assign({}, caller.state.playlists);
    const texts = Object.assign({}, caller.state.playlistsTexts);
    const basePath = "flag/" + caller.state.language + "/radio-stations/" + folder + "/" + genre + "/";
    const iconPath = "icon/" + caller.state.language + "/radio-stations/" + folder + "/" + genre + "/";
    const items = createPlaylist(json, DEFAULT_STATION_IMAGE, basePath, caller.state.playlists);
    let promises = [];
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      promises.push(findImage(iconPath, item));
    }
    Promise.all(promises).then(() => {
      if (newState[caller.state.language] === undefined) {
        newState[caller.state.language] = {};
        texts[caller.state.language] = {};
      }
      newState[caller.state.language][genre] = items;
      texts[caller.state.language][genre] = json;
      caller.setState({
        playlists: newState,
        playlistsTexts: texts,
        playlistBasePath: basePath
      });
    });
  }).catch(function (err) {
    console.log('Fetch problem: ' + err.message);
  });
}

export function getPodcasts(caller) {
  if (caller.state.podcasts) {
    return;
  }

  fetch("/podcasts").then(function (response) {
    return response.json();
  }).then((json) => {
    caller.setState({ podcasts: json });
  }).catch(function (err) {
    console.log('Fetch problem: ' + err.message);
  });
}

export function getStreams(caller) {
  if (caller.state.streams) {
    return;
  }

  fetch("/streams").then(function (response) {
    return response.json();
  }).then((json) => {
    const basePath = "streamimage/";
    if (!json) {
      caller.setState({
        streams: {},
        streamsBasePath: basePath
      });
      return;
    }

    const items = createPlaylist(json, DEFAULT_STREAM_IMAGE, basePath, caller.state.streams);
    let promises = [];
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      promises.push(findImage(basePath, item));
    }
    Promise.all(promises).then(() => {

      caller.setState({
        streams: items,
        streamsText: json,
        streamsBasePath: basePath
      });
    });
  }).catch(function (err) {
    console.log('Fetch problem: ' + err.message);
  });
}

export function changeLanguage(event, caller) {
  const newLanguage = event.target.value;

  fetch("/labels?language=" + newLanguage).then(function (response) {
    return response.json();
  }).then((json) => {
    caller.setState({
      labels: { ...json },
      language: newLanguage
    });
    if (caller.state.tabIndex === 3) {
      caller.setState({ currentMenuItem: 0 }, getRadioPlaylist(caller, 0));
    }
  }).catch(function (err) {
    console.log('Fetch problem: ' + err.message);
  });
}

export function save(caller, callback) {
  if (!caller.isDirty()) {
    const msg = caller.state.labels["nothing.save"];
    caller.setState({
      openSnack: true,
      notificationMessage: msg,
      notificationVariant: "warning"
    });
    return;
  }

  const dirtyFlags = ["parametersDirty", "playersDirty", "screensaversDirty", "playlistsDirty",
    "podcastsDirty", "streamsDirty", "backgroundDirty"];

  let promises = [];
  if (caller.state[dirtyFlags[0]]) promises.push(saveConfiguration(caller));
  if (caller.state[dirtyFlags[1]]) promises.push(savePlayers(caller));
  if (caller.state[dirtyFlags[2]]) promises.push(saveScreensavers(caller));
  if (caller.state[dirtyFlags[3]]) promises = promises.concat(savePlaylists(caller));
  if (caller.state[dirtyFlags[4]]) promises.push(savePodcasts(caller));
  if (caller.state[dirtyFlags[5]]) promises.push(saveStreams(caller));
  if (caller.state[dirtyFlags[6]]) promises.push(saveBackground(caller));

  caller.setState({ showProgress: true });
  const msg = caller.state.labels["saved.successfully"];

  Promise.all(promises).then((responses) => {
    for (let n = 0; n < responses.length; n++) {
      const response = responses[n];
      if (response.status === 500) {
        response.json().then(data => {
          caller.setState({
            openSnack: true,
            notificationMessage: data.message,
            notificationVariant: "error",
            showProgress: false
          })
        });
        dirtyFlags.forEach((flag) => {
          caller.setState({ [flag]: false });
        });
        if (callback) callback();
        return;
      }
    }
    caller.setState({
      openSnack: true,
      notificationMessage: msg,
      notificationVariant: "success",
      showProgress: false
    });
    dirtyFlags.forEach((flag) => {
      caller.setState({ [flag]: false });
    });
    if (callback) callback();
  }).catch((errors) => {
    caller.setState({
      openSnack: true,
      notificationMessage: errors,
      notificationVariant: "error",
      showProgress: false
    })
  });
}

export function saveConfiguration(caller) {
  let objectToSave = {}
  configSections.forEach((section) => {
    objectToSave[section] = caller.state.parameters[section];
  })
  return saver("/parameters", objectToSave)
}

export function savePlayers(caller) {
  return saver("/players", caller.state.players)
}

export function saveScreensavers(caller) {
  return saver("/savers", caller.state.screensavers)
}

export function saveBackground(caller) {
  return saver("/bgr", caller.state.background)
}

export function savePlaylists(caller) {
  const languages = Object.keys(caller.state.playlists);
  let images = [];
  let promises = [];
  let playlists = {};

  for (let n = 0; n < languages.length; n++) {
    const language = languages[n];
    playlists[language] = {};
    const genres = Object.keys(caller.state.playlists[language]);
    for (let m = 0; m < genres.length; m++) {
      const genre = genres[m];
      playlists[language][genre] = {};
      const playlist = caller.state.playlists[language][genre];
      let textPlaylist = "";
      for (let k = 0; k < playlist.length; k++) {
        const playlistItem = playlist[k];
        if (!playlistItem.name || playlistItem.name.trim().length === 0 || playlistItem.link.trim().length === 0) {
          continue;
        }
        textPlaylist += "#" + playlistItem.name + "\n";
        textPlaylist += playlistItem.link + "\n";
        if (playlistItem.image) {
          let formData = new FormData();
          formData.append("language", language);
          formData.append("genre", genre);
          const tokens = playlistItem.image.name.toLowerCase().split(".");
          const extension = tokens[tokens.length - 1];
          formData.append("filename", playlistItem.name + "." + extension);
          formData.append("image", playlistItem.image);
          images.push(formData);
        }
      }
      if (textPlaylist.length > 0) {
        playlists[language][genre] = textPlaylist;
      }
    }
  }

  if (images.length > 0) {
    for (let n = 0; n < images.length; n++) {
      promises.push(upload("/upload", images[n]));
    }
  }

  promises.push(saver("/playlists", playlists));

  return promises;
}

export function savePodcasts(caller) {
  return saver("/podcasts", caller.state.podcasts)
}

export function saveStreams(caller) {
  let textPlaylist = "";
  let playlist = caller.state.streams;
  let images = [];
  let promises = [];

  for (let k = 0; k < playlist.length; k++) {
    const playlistItem = playlist[k];
    if (!playlistItem.name || playlistItem.name.trim().length === 0 || playlistItem.link.trim().length === 0) {
      continue;
    }
    textPlaylist += "#" + playlistItem.name + "\n";
    textPlaylist += playlistItem.link + "\n";
    if (playlistItem.image) {
      let formData = new FormData();
      const tokens = playlistItem.image.name.toLowerCase().split(".");
      const extension = tokens[tokens.length - 1];
      formData.append("filename", playlistItem.name + "." + extension);
      formData.append("image", playlistItem.image);
      images.push(formData);
    }
  }

  if (images.length > 0) {
    for (let n = 0; n < images.length; n++) {
      promises.push(upload("/upload", images[n]));
    }
  }

  promises.push(saver("/streams", textPlaylist));

  return promises;
}

export function deleteImage(imagePath) {
  const body = {"imagePath": imagePath}
  return fetch("/upload", {
    method: 'DELETE',
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body)
  });
}

function saver(query, body) {
  return fetch(query, {
    method: 'PUT',
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body)
  });
}

function upload(query, imageFormData) {
  return fetch(query, {
    method: 'POST',
    body: imageFormData
  });
}

var intervalId = null;

export function reboot(caller) {
  intervalId = setInterval(function () { ping(caller); }, 4000);
  caller.setState({
    isRebootDialogOpen: false,
    isSaveAndRebootDialogOpen: false,
    hideUi: true,
    reboot: true
  });
  fetch("/command/reboot", { method: "POST" }).then(function (response) {
    return response.json();
  }).then().catch(function () {
    console.log("reboot started");
  });
}

function ping(caller) {
  fetch("/command/ping", { method: "GET" }).then(function (response) {
    return response.json();
  }).then(() => {
    clearInterval(intervalId);
    caller.setState({
      isRebootDialogOpen: false,
      hideUi: false,
      reboot: false,
      playerWasRebooted: true,
      parameters: null,
      players: null,
      screensavers: null,
      playlists: {},
      podcasts: null,
      streams: null
    }, caller.refreshTab(caller.state.tabIndex));
  }).catch(() => { });
}

export function shutdown(caller) {
  caller.setState({
    isShutdownDialogOpen: false,
    isSaveAndShutdownDialogOpen: false,
    hideUi: true,
    shutdown: true
  });
  fetch("/command/shutdown", { method: "POST" }).then(function (response) {
    return response.json();
  }).then().catch(function () {
    console.log("shutdown initiated");
  });
}

function setFlags(languages, caller) {
  let urls = {};
  languages.forEach((lang) => {
    urls[lang.name] = "/flag/" + lang.name + "/flag.png";
  });
  caller.setState({ flags: urls });
}

