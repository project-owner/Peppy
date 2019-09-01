import { configSections } from "./tabs/ConfigTab";
import { playersSections } from "./tabs/PlayersTab";
import { screensaversSections } from "./tabs/ScreensaversTab";

export function updateConfiguration(caller, name, value, index) {
  const newState = Object.assign({}, caller.state.parameters);
  const section = configSections[caller.state.currentMenuItem];
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
  } else {
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
  caller.setState({
    playlists: newState,
    playlistsDirty: true
  });
}

export function updatePodcasts(caller, value) {
  caller.setState({
    podcasts: value,
    podcastsDirty: true
  });
}

export function updateStreams(caller, value) {
  caller.setState({
    streams: value,
    streamsDirty: true
  });
}
