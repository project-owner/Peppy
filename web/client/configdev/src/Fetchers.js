import { fileBrowserSections } from "./config/FileBrowser";
import { logSections } from "./config/Logging";
import { configSections } from "./tabs/ConfigTab";

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
    caller.colorBackup = JSON.parse(JSON.stringify(json.colors))
  }).catch(function (err) {
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

export function getRadioPlaylist(caller) {
  const genre = caller.getRadioPlaylistMenu()[caller.state.currentMenuItem];
  let folder = "";
  caller.state.parameters.languages.forEach((lang) => {
    if (lang.name === caller.state.language) {
      folder = Object.keys(lang.stations)[0];
    }
  });

  fetch("/playlists?language=" + caller.state.language + "&genre=" + genre + "&folder=" + folder).then(function (response) {
    return response.json();
  }).then((json) => {
    const newState = Object.assign({}, caller.state.playlists);
    if (newState && newState[caller.state.language]) {
      if (!newState[caller.state.language][genre]) {
        newState[caller.state.language][genre] = json;
        caller.setState({ playlists: newState });
      }
    } else {
      newState[caller.state.language] = { [genre]: json };
      caller.setState({ playlists: newState });
    }
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
    caller.setState({ streams: json });
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
      getRadioPlaylist(caller);
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
    "podcastsDirty", "streamsDirty"];

  let promises = [];
  if (caller.state[dirtyFlags[0]]) promises.push(saveConfiguration(caller));
  if (caller.state[dirtyFlags[1]]) promises.push(savePlayers(caller));
  if (caller.state[dirtyFlags[2]]) promises.push(saveScreensavers(caller));
  if (caller.state[dirtyFlags[3]]) promises.push(savePlaylists(caller));
  if (caller.state[dirtyFlags[4]]) promises.push(savePodcasts(caller));
  if (caller.state[dirtyFlags[5]]) promises.push(saveStreams(caller));

  caller.setState({ showProgress: true });
  const msg = caller.state.labels["saved.successfully"];

  Promise.all(promises)
    .then(() => {
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
    })
    .catch((errors) => {
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

export function savePlaylists(caller) {
  return saver("/playlists", caller.state.playlists)
}

export function savePodcasts(caller) {
  return saver("/podcasts", caller.state.podcasts)
}

export function saveStreams(caller) {
  return saver("/streams", caller.state.streams)
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

