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

import { fileBrowserSections } from "./config/FileBrowser";
import { logSections } from "./config/Logging";
import { configSections } from "./tabs/ConfigTab";

export const DEFAULT_STATION_IMAGE = "default/default-station.png";
export const DEFAULT_STREAM_IMAGE = "default/default-stream.png";
// let voskModelDownloader;

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
    prepareFolders(params);
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

export function deleteFilePlaylist(caller, playlistUrl) {
  return fetch("api/fileplaylists?name=" + playlistUrl, {
    method: "DELETE"
  }).then(function(json) {
    if (json && json.status === 500) {
      caller.setState({ 
        isDeleteFilePlaylistDialogOpen: false,
        openSnack: true,
        notificationMessage: json.statusText,
        notificationVariant: "error",
        showProgress: false
      })
    } else if (json && json.status === 200) {
      getFilePlaylists(caller, true);
      caller.setState({ 
        isDeleteFilePlaylistDialogOpen: false,
        openSnack: true,
        notificationMessage: caller.state.labels["deleted.playlist"],
        notificationVariant: "success",
        showProgress: false
      })
    } else {
      console.log(json);  
    }   
  }).catch(function (err) {
    console.log(err);
  });
}

export function createNewFilePlaylist(caller, playlistName) {
  let name = playlistName;

  if (!name.toLowerCase().endsWith(".m3u")) {
    name += ".m3u";
  }

  return fetch("api/fileplaylists?name=" + name, {
    method: "POST"
  }).then(function(json) {
    if (json && json.status === 500) {
      caller.setState({ 
        isCreatePlaylistDialogOpen: false,
        openSnack: true,
        notificationMessage: json.statusText,
        notificationVariant: "error",
        showProgress: false
      })
    } else if (json && json.status === 200) {
      caller.setState({
        openSnack: true,
        notificationMessage: caller.state.labels["created.playlist"],
        notificationVariant: "success",
        showProgress: false
      });
      getFilePlaylists(caller, true, name);
    } else {
      console.log(json);  
    }   
  }).catch(function (err) {
    console.log(err);
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

function prepareFolders(params) {
  const podcastsSection = {
    "music.folder": params["music.folder"],
    "podcasts.folder": params["podcasts.folder"],
    "file.playlists.folder": params["file.playlists.folder"]
  }
  params["folders"] = podcastsSection;
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
  for (let n = 0; n < currentItems.length; n++) {
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

  for (let n = 0; n < languages.length; n++) {
    const lang = languages[n];
    if (lang.name === caller.state.language) {
      folder = Object.keys(lang.stations)[0];
      break;
    }
  }

  return folder;
}

export function getRadioPlaylist(caller, index, refresh) {
  if (index === undefined) {
    index = 0;
  }
  const genre = caller.getRadioPlaylistMenu()[index];

  if (refresh === undefined || refresh === null) {
    if (caller.state.playlists[caller.state.language] !== undefined &&
      caller.state.playlists[caller.state.language][genre] !== undefined) {
      return;
    }
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

export function getYaStreams(caller) {
  if (caller.state.yastreams) {
    return;
  }

  fetch("/yastreams").then(function (response) {
    return response.json();
  }).then((json) => {
    caller.setState({ yastreams: json });
  }).catch(function (err) {
    console.log('Fetch problem: ' + err.message);
  });
}

export function getJukebox(caller) {
  if (caller.state.jukebox) {
    return;
  }

  fetch("/jukebox").then(function (response) {
    return response.json();
  }).then((json) => {
    caller.setState({ jukebox: json });
  }).catch(function (err) {
    console.log('Fetch problem: ' + err.message);
  });
}

export function getFilePlaylists(caller, force=false, selected=null) {
  if (!force && caller.state.filePlaylists) {
    return;
  }

  fetch("/api/fileplaylists").then(function (response) {
    return response.json();
  }).then((json) => {
    if (json && json["message"]) {
      caller.setState({ filePlaylists: null, currentFilePlaylist: null });  
    } else {
      let selectedItem = json[0];
      let menuIndex = 0;
      if (selected !== null) {
        for (let i = 0; i < json.length; i++) {
          if (json[i]["name"] === selected) {
            selectedItem = json[i];
            menuIndex = i;
            break;
          }
        }
      }
      caller.setState({
        isCreatePlaylistDialogOpen: false,
        currentMenuItem: menuIndex,
        filePlaylists: json,
        currentFilePlaylist: null,
        currentFilePlaylistName: selectedItem.name, 
        currentFilePlaylistUrl: selectedItem.url
      });
      getCurrentFilePlaylist(caller, selectedItem.url);
    }
  }).catch(function (err) {
    console.log('Fetch problem: ' + err.message);
  });
}

export function getCurrentFilePlaylist(caller, url, force=false) {
  if (!force && caller.state.currentFilePlaylist) {
    return;
  }
  fetch("/api/fileplaylists?name=" + url).then(function (response) {
    return response.json();
  }).then((json) => {
    if (json && json["message"]) {
      caller.setState({ currentFilePlaylist: null });  
    } else {
      caller.setState({ currentFilePlaylist: json });
      getFiles(caller, null);
    }
  }).catch(function (err) {
    console.log('Fetch problem: ' + err.message);
  });
}

export function getFiles(caller, folder) {
  let url = "/api/filebrowser?";
  if (folder) {
    url += "folder=" + folder + "&view=simple";
  } else {
    url += "view=simple";
  }
  fetch(url).then(function (response) {
    return response.json();
  }).then((json) => {
    if (json && json["message"]) {
      caller.setState({ files: null });  
    } else {
      if (json && json.content) {
        json.content.forEach((file) => {
          file.selected = false;
        });
      }
      caller.setState({ files: json });
    }
  }).catch(function (err) {
    console.log('Fetch problem: ' + err.message);
  });
}

export function goToRoot(caller) {
  if (!caller.state.files) {
    return;
  }

  let path = "";

  if (caller.state.files.start_from_separator) { // Linux
    path += caller.state.files.separator;
  } else { // Windows
    path += caller.state.files.breadcrumbs[0]["path"];  
  }

  getFiles(caller, path);
}

export function getFonts(caller, ignoreExistingFonts) {
  if (caller.state.fonts && ignoreExistingFonts === undefined) {
    return;
  }

  fetch("/fonts").then(function (response) {
    return response.json();
  }).then((json) => {
    caller.setState({ fonts: json });
  }).catch(function (err) {
    console.log('Fetch problem: ' + err.message);
  });
}

export function getVoskModels(caller) {
  fetch("/voiceassistant/voskmodels?language=" + caller.state.language, { method: "GET" }).then(function (response) {
    return response.json();
  }).then((json) => {
    caller.setState({ voskModels: json });
  }).catch(function (e) {
    console.log('Fetch Vosk models problem: ' + e.message);
  });
}

export function getDevices(caller) {
  fetch("/alsadevices", { method: "GET" }).then(function (response) {
    return response.json();
  }).then((json) => {
    caller.setState({ devices: json });
  }).catch(function (e) {
    console.log('Fetch ALSA devices problem: ' + e.message);
  });
}

export function getSystem(caller) {
  if (caller.state.system) {
    return;
  }

  fetch("/timezone").then(function (response) {
    return response.json();
  }).then((json) => {
    const newState = Object.assign({}, caller.state.system);
    newState.timezone = json;
    newState.defaults = [false, false, false];
    fetch("/diskmanager/disks", { method: "GET" }).then(function (response) {
      return response.json();
    }).then((json) => {
      newState.disks = json;
      caller.setState({ system: newState });
      fetch("/nasmanager/nases", { method: "GET" }).then(function (response) {
        return response.json();
      }).then((json) => {
        newState.nases = json;
        caller.setState({ system: newState });
        fetch("/sharefolder/shares", { method: "GET" }).then(function (response) {
          return response.json();
        }).then((json) => {
          newState.shares = json;
          caller.setState({ system: newState });
          fetch("/voiceassistant/config", { method: "GET" }).then(function (response) {
            return response.json();
          }).then((json) => {
            newState.vaconfig = json;
            caller.setState({ system: newState });
          }).catch(function (e) {
            console.log('Fetch VA config problem: ' + e.message);
          });
        }).catch(function (e) {
          console.log('Fetch shares problem: ' + e.message);
        });
      }).catch(function (e) {
        console.log('Fetch nases problem: ' + e.message);
      });
    }).catch(function (e) {
      console.log('Fetch disks problem: ' + e.message);
    });
  }).catch(function (err) {
    console.log('Fetch timezone problem: ' + err.message);
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
    } else if (caller.state.tabIndex === 4) {
      getVoskModels(caller);
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
    "podcastsDirty", "streamsDirty", "backgroundDirty", "nasDirty", "shareDirty", "yastreamsDirty", 
    "jukeboxDirty", "vaconfigDirty", "voskModelsDirty", "devicesDirty", "filePlaylistDirty"];

  let promises = [];
  if (caller.state[dirtyFlags[0]]) promises.push(saveConfiguration(caller));
  if (caller.state[dirtyFlags[1]]) promises.push(savePlayers(caller));
  if (caller.state[dirtyFlags[2]]) promises.push(saveScreensavers(caller));
  if (caller.state[dirtyFlags[3]]) promises = promises.concat(savePlaylists(caller));
  if (caller.state[dirtyFlags[4]]) promises.push(savePodcasts(caller));
  if (caller.state[dirtyFlags[5]]) promises.push(saveStreams(caller));
  if (caller.state[dirtyFlags[6]]) promises.push(saveBackground(caller));
  if (caller.state[dirtyFlags[7]]) promises.push(saveNases(caller));
  if (caller.state[dirtyFlags[8]]) promises.push(saveShares(caller));
  if (caller.state[dirtyFlags[9]]) promises.push(saveYaStreams(caller));
  if (caller.state[dirtyFlags[10]]) promises.push(saveJukebox(caller));
  if (caller.state[dirtyFlags[11]]) promises.push(saveVaconfig(caller));
  if (caller.state[dirtyFlags[12]]) promises.push(saveVoskModels(caller));
  if (caller.state[dirtyFlags[13]]) promises.push(saveDevices(caller));
  if (caller.state[dirtyFlags[14]]) promises.push(savePlaylist(caller));

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
      if (caller.state[flag]) {
        caller.setState({ [flag]: false });
      }
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
  configSections.push("home.menu");
  configSections.push("home.navigator");
  configSections.push("screensaver.menu");
  configSections.push("screensaver.delay");
  configSections.push("languages.menu");
  configSections.push("collection.menu");
  configSections.push("player.screen");
  configSections.push("file.browser");
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

export function saveNases(caller) {
  return saver("/nasmanager/save", caller.state.system.nases);
}

export function saveShares(caller) {
  return saver("/sharefolder/save", caller.state.system.shares);
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

export function saveYaStreams(caller) {
  return saver("/yastreams", caller.state.yastreams)
}

export function saveJukebox(caller) {
  return saver("/jukebox", caller.state.jukebox)
}

export function saveVaconfig(caller) {
  return saver("/voiceassistant/config", caller.state.system.vaconfig)
}

export function saveVoskModels(caller) {
  return saver("/voiceassistant/voskmodels", caller.state.system.voskmodels)
}

export function saveDevices(caller) {
  return saver("/alsadevices", caller.state.devices)
}

export function savePlaylist(caller) {
  let payload = {
    "name": caller.state.currentFilePlaylistUrl,
    "content": caller.state.currentFilePlaylist
  };
  return saver("/api/fileplaylists", payload);
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
  const body = { "imagePath": imagePath }
  return fetch("/upload", {
    method: "DELETE",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body)
  });
}

function saver(query, body) {
  console.log("saving");
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

export function reboot(caller, saveCurrentState) {
  intervalId = setInterval(function () { ping(caller); }, 4000);
  caller.setState({
    isRebootDialogOpen: false,
    isSaveAndRebootDialogOpen: false,
    isSetDefaultsAndRebootDialogOpen: false,
    hideUi: true,
    reboot: true
  });

  let query = "";
  if (saveCurrentState === false) {
    query = "/command/reboot?save=false";
  } else {
    query = "/command/reboot?save=true";
  }

  fetch(query, { method: "POST" }).then(function (response) {
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

export function setNewTimezone(caller) {
  let newTimezone = caller.state.system.timezone.currentArea;
  if (caller.state.system.timezone.currentCity) {
    newTimezone = newTimezone + "/" + caller.state.system.timezone.currentCity;
  }
  return fetch("/timezone", {
    method: 'PUT',
    body: JSON.stringify(newTimezone)
  }).then((response) => {
    return response.json();
  }).then((json) => {
    const msg = caller.state.labels["saved.successfully"];
    let timezone = caller.state.system.timezone;
    timezone.currentTimezone = json.currentTimezone;
    timezone.currentTime = json.currentTime;
    caller.setState({
      openSnack: true,
      notificationMessage: msg,
      notificationVariant: "success"
    });
  }).catch((errors) => {
    caller.setState({
      openSnack: true,
      notificationMessage: errors,
      notificationVariant: "error",
      showProgress: false
    })
  });
}

export function setDefaults(caller) {
  const defaults = caller.state.system.defaults;

  if (!defaults[0] && !defaults[1] && !defaults[2]) {
    const msg = caller.state.labels["nothing.save"];
    caller.setState({
      openSnack: true,
      notificationMessage: msg,
      notificationVariant: "warning"
    });
    return;
  }

  let promise = saver("/defaults", defaults);
  promise.then((response) => {
    if (response.status !== 200) {
      caller.setState({
        openSnack: true,
        notificationMessage: response.statusText,
        notificationVariant: "error",
        showProgress: false
      });
      return;
    } else {
      const msg = caller.state.labels["saved.successfully"];
      caller.setState({
        openSnack: true,
        notificationMessage: msg,
        notificationVariant: "success"
      });
    }
  }).catch((errors) => {
    caller.setState({
      openSnack: true,
      notificationMessage: errors,
      notificationVariant: "error",
      showProgress: false
    })
  });
}

export function mount(caller, name, device, mountPoint) {
  let query = encodeURI("/diskmanager/mount?name=" + name + "&device=" + device + "&mount.point=" + mountPoint);

  fetch(query, { method: "POST" }).then(function (response) {
    if (response.status !== 200) {
      console.log(response);
      caller.setState({
        openSnack: true,
        notificationMessage: caller.state.labels["cannot.mount"],
        notificationVariant: "error",
        showProgress: false
      });
    } else {
      caller.setState({
        openSnack: true,
        notificationMessage: caller.state.labels["mounted"],
        notificationVariant: "success"
      });
    }
  }).then(() => {
    refresh(caller);
  }).catch();
}

export function unmount(caller, device) {
  let query = encodeURI("/diskmanager/unmount?&device=" + device);

  fetch(query, { method: "POST" }).then(function (response) {
    if (response.status !== 200) {
      console.log(response);
      caller.setState({
        openSnack: true,
        notificationMessage: caller.state.labels["cannot.unmount"],
        notificationVariant: "error",
        showProgress: false
      });
    } else {
      caller.setState({
        openSnack: true,
        notificationMessage: caller.state.labels["unmounted"],
        notificationVariant: "success"
      });
    }
  }).then(() => {
    refresh(caller);
  }).catch();
}

export function poweroff(caller, device) {
  let query = encodeURI("/diskmanager/poweroff?&device=" + device);

  fetch(query, { method: "POST" }).then(function (response) {
    if (response.status !== 200) {
      console.log(response);
      caller.setState({
        openSnack: true,
        notificationMessage: caller.state.labels["cannot.poweroff"],
        notificationVariant: "error",
        showProgress: false
      });
    } else {
      caller.setState({
        openSnack: true,
        notificationMessage: caller.state.labels["poweroff"],
        notificationVariant: "success"
      });
    }
  }).then(() => {
    refresh(caller);
  }).catch();
}

export function refresh(caller) {
  fetch("/diskmanager/disks", { method: "GET" }).then(function (response) {
    return response.json();
  }).then((json) => {
    const newState = Object.assign({}, caller.state.system);
    newState.disks = json;
    caller.setState({ system: newState });
  }).catch(function (e) {
    console.log('Fetch disks problem: ' + e.message);
  });
}

export function addNewNas(caller) {
  const newState = Object.assign({}, caller.state.system);

  const nases = newState.nases;
  const emptyNas = {
    "name": "",
    "ip.address": "",
    "folder": "",
    "filesystem": "",
    "username": "",
    "password": "",
    "mount.options": ""
  };
  nases.push(emptyNas);
  saveNases(caller);
  
  caller.setState({
    system: newState
  });
}

export function mntNas(caller, index) {
  saveNases(caller);

  let nas = caller.state.system.nases[index];
  let query = encodeURI("/nasmanager/mount");

  fetch(query, { method: "POST", body: JSON.stringify(nas)}).then(function (response) {
    if (response.status !== 200) {
      caller.setState({
        openSnack: true,
        notificationMessage: caller.state.labels["cannot.mount"],
        notificationVariant: "error",
        showProgress: false
      });
    } else {
      caller.setState({
        openSnack: true,
        notificationMessage: caller.state.labels["mounted"],
        notificationVariant: "success"
      });
    }
  }).then(() => {
    refreshNases(caller);
  }).catch();
}

export function unmntNas(caller, index, delNas) {
  saveNases(caller);

  let nas = caller.state.system.nases[index];
  let query = encodeURI("/nasmanager/unmount");

  fetch(query, { method: "POST", body: JSON.stringify(nas) }).then(function (response) {
    if (response.status !== 200) {
      console.log(response);
      caller.setState({
        openSnack: true,
        notificationMessage: caller.state.labels["cannot.unmount"],
        notificationVariant: "error",
        showProgress: false
      });
    } else {
      caller.setState({
        openSnack: true,
        notificationMessage: caller.state.labels["unmounted"],
        notificationVariant: "success"
      });
    }
  }).then(() => {
    if (delNas) {
      const newState = Object.assign({}, caller.state.system);
      const nases = newState.nases;
      nases.splice(index, 1);
      caller.setState({
        system: newState
      });
    }
    saveNases(caller);
    refreshNases(caller);
  }).catch();
}

export function refreshNases(caller) {
  fetch("/nasmanager/nases", { method: "GET" }).then(function (response) {
    return response.json();
  }).then((json) => {
    const newState = Object.assign({}, caller.state.system);
    newState.nases = json;
    caller.setState({ system: newState });
  }).catch(function (e) {
    console.log('Fetch Nas problem: ' + e.message);
  });
}

export function deleteNas(caller, index) {
  let nas = caller.state.system.nases[index];
  if (nas.mounted) {
    unmntNas(caller, index, true);
  } else {
    const newState = Object.assign({}, caller.state.system);
    const nases = newState.nases;
    nases.splice(index, 1);

    caller.setState({
      system: newState
    });
    saveNases(caller);
    refreshNases(caller);
  }
}

export function addNewShare(caller) {
  const newState = Object.assign({}, caller.state.system);
  const shares = newState.shares;

  const emptyShare = {
    "name": "",
    "path": ""
  };
  shares.push(emptyShare);
  
  caller.setState({
    system: newState
  });
}

export function refreshShares(caller) {
  fetch("/sharefolder/shares", { method: "GET" }).then(function (response) {
    return response.json();
  }).then((json) => {
    const newState = Object.assign({}, caller.state.system);
    newState.shares = json;
    caller.setState({ system: newState });
  }).catch(function (e) {
    console.log('Fetch Shares problem: ' + e.message);
  });
}

export function deleteShare(caller, index) {
  const newState = Object.assign({}, caller.state.system);
  const shares = newState.shares;
  shares.splice(index, 1);

  caller.setState({
    system: newState,
    shareDirty: true
  });
}

export function deleteModel(caller) {
  caller.setState({
    isDeleteVoskModelDialogOpen: false
  })

  let modelName = caller.state.voskModelToDelete;

  fetch("/voiceassistant/deletemodel?name=" + modelName, { method: "DELETE"}).then(function (response) {
    if (response.ok) {
      caller.setState({
        voskModelDownloading: "",
        openSnack: true,
        notificationMessage: caller.state.labels["deleted.vosk.model"],
        notificationVariant: "success",
        voskModelToDelete: ""
      });
      getVoskModels(caller);
    } else {
      caller.setState({
        voskModelDownloading: "",
        openSnack: true,
        notificationMessage: response.statusText,
        notificationVariant: "error",
        voskModelToDelete: ""
      });
    }
  }).catch(function (err) {
    console.log("Vosk model deletion problem: " + err.message);
  });
}

export function downloadModel(caller, name, url, size) {
  let requestBody = {
    name: name,
    url: url,
    size: size
  };
  fetch("/voiceassistant/downloadmodel", { method: "PUT", body: JSON.stringify(requestBody) }).then(function (response) {
    if (response.ok) {
      caller.setState({
        voskModelDownloading: name
      });
      let voskModelDownloader = setInterval(() => {
        getDownloadProgress(caller, name, voskModelDownloader);
      }, 1000);
    } else {
      caller.setState({
        openSnack: true,
        notificationMessage: response.statusText,
        notificationVariant: "error"
      });
    }
  }).catch(function (err) {
    console.log("Vosk model download problem: " + err.message);
  });
}

export function setCurrentModel(caller, name, remote) {
  if (remote) {
    return;
  }
  let requestBody = {
    name: name,
    language: caller.state.language
  };
  fetch("/voiceassistant/setcurrentmodel", { method: "PUT", body: JSON.stringify(requestBody) }).then(function (response) {
    if (response.ok) {
      getVoskModels(caller);
    } else {
      caller.setState({
        openSnack: true,
        notificationMessage: response.statusText,
        notificationVariant: "error"
      });
    }
  }).catch(function (err) {
    console.log("Vosk set model problem: " + err.message);
  });
}

export function getDownloadProgress(caller, name, downloader) {
  fetch("/voiceassistant/downloadprogress", { method: "GET" }).then(function (response) {
    return response.json();
  }).then((json) => {
    if (caller.state.downloadVoskModelProgress >= 100) {
      clearInterval(downloader);
      caller.setState({
        openSnack: true,
        notificationMessage: caller.state.labels["downloaded.model"] + ": " + name,
        notificationVariant: "info",
        downloadVoskModelProgress: 0
      });
      fetch("/voiceassistant/resetprogress", { method: "PUT" }).then(function (_) {
        getVoskModels(caller);
      }).catch(function (err) {
        console.log("Reset progress problem: " + err.message);
      });
    } else {
      caller.setState({
        downloadVoskModelProgress: json.progress
      });
    }
  }).catch(function (e) {
    console.log('Fetch download progress problem: ' + e.message);
  });
}

export function getLog(caller, refreshLog) {
  if (caller.state.log && !refreshLog) {
    return;
  }

  fetch("/log").then(function (response) {
    return response.json();
  }).then((json) => {
    caller.setState({ log: json.log });
  }).catch(function (err) {
    console.log('Log fetch problem: ' + err.message);
  });
}

export function uploadPlaylist(caller, path, data, id) {
  let query = encodeURI("/playlist?path=" + path);

  let formData = new FormData();
  formData.append("data", data);
  const msg = caller.state.labels["saved.successfully"];

  fetch(query, {method: "POST", body: formData}).then(function (_) {
    caller.setState({
      openSnack: true,
      notificationMessage: msg,
      notificationVariant: "success",
      showProgress: false
    })
    let playlistIndex = caller.getRadioPlaylistMenu().indexOf(id);
    getRadioPlaylist(caller, playlistIndex, true);
  }).catch(function (err) {
    console.log('Upload problem: ' + err.message);
  });
}

export function uploadFont(caller, data) {
  let query = encodeURI("/fonts");
  let formData = new FormData();
  formData.append("data", data);
  const msg = caller.state.labels["saved.successfully"];

  fetch(query, {method: "POST", body: formData}).then(function (_) {
    caller.setState({
      openSnack: true,
      notificationMessage: msg,
      notificationVariant: "success",
      showProgress: false
    })
    getFonts(caller, true);
  }).catch(function (err) {
    console.log('Upload problem: ' + err.message);
  });
}

export function updateMpdDatabase(caller) {
  fetch("/command/updateMpdDatabase", { method: "POST" }).then(function (_) {
    caller.setState({
      openSnack: true,
      notificationMessage: caller.state.labels["update.database"],
      notificationVariant: "success",
      showProgress: false
    });
  }).then().catch(function (err) {
    console.log("Error while updating mpd database: " + err.message);
  });
}