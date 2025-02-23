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

import { getSecondsFromString } from "./Util";
import { PaletteSlate, HomeIconType, HomeIconCategory } from "./min/mincss";

const host = window.location.host;
const baseUrl = `http://${host}`;
export const baseApiUrl = `${baseUrl}/api`;

export const configIconUrl = getIconUrl('config');
export const shutdownIconUrl = getIconUrl('shutdown');
export const rebootIconUrl = getIconUrl('reboot');
export const favoritesIconUrl = getIconUrl('favorites');
export const rootIconUrl = getColorIconUrl('root', PaletteSlate.colorTitle, PaletteSlate.colorTitle);
export const userHomeIconUrl = getColorIconUrl('user-home', PaletteSlate.colorTitle, PaletteSlate.colorTitle);
export const playlistIconUrl = getColorIconUrl('playlist', PaletteSlate.colorTitle, PaletteSlate.colorTitle);
export const countryIconUrl = getColorIconUrl('search-by-country', PaletteSlate.colorTitle, PaletteSlate.colorTitle);
export const languageIconUrl = getColorIconUrl('search-by-language', PaletteSlate.colorTitle, PaletteSlate.colorTitle);
export const genreIconUrl = getColorIconUrl('search-by-genre', PaletteSlate.colorTitle, PaletteSlate.colorTitle);
export const nameIconUrl = getColorIconUrl('search-by-name', PaletteSlate.colorTitle, PaletteSlate.colorTitle);
export const defaultStationImageUrl = `${baseUrl}/icon/default-station.png`;

function getUrl(resource, name, color1, color2) {
  return `${baseApiUrl}/${resource}?type=${HomeIconType}&category=${HomeIconCategory}&name=${name}` +
    `&color1=${color1}&color2=${color2}`;
};

export function getIconUrl(name) {
  return getUrl("icon", name, PaletteSlate.colorHomeIcon1, PaletteSlate.colorHomeIcon2);
};

export function getColorIconUrl(name, color1, color2) {
  return getUrl("icon", name, color1, color2);
};

export function getIconSelectedUrl(name) {
  return getUrl("icon", name, PaletteSlate.colorHomeIcon3, PaletteSlate.colorHomeIcon4);
};

export function getGenreIconUrl(name) {
  return getUrl("genreicon", name, PaletteSlate.colorTitle, PaletteSlate.colorTitle);
};

export function getGenreIconSelectedUrl(name) {
  return getUrl("genreicon", name, PaletteSlate.colorGenreSelected, PaletteSlate.colorGenreSelected);
};

export function getImageFileUrl(path) {
  return `${baseUrl}/image/${encodeURI(path)}`;
}

export function getConfig(caller) {
  fetch(`${baseUrl}/parameters`, { method: "GET" }).then(function (response) {
    return response.json();
  }).then((json) => {
    const currentLanguage = json.current.language;
    fetch(`${baseUrl}/labels?language=${currentLanguage}`, { method: "GET" }).then(function (response) {
      return response.json();
    }).then((labels) => {
      fetch(`${baseApiUrl}/modes`, { method: "GET" }).then(function (response) {
        return response.json();
      }).then((modeNames) => {
        fetch(`${baseApiUrl}/mode`, { method: "GET" }).then(function (response) {
          return response.json();
        }).then((modeJson) => {
          const mode = modeJson.mode;
          let modeIconUrl = null;
          let modeIcons = [];
          modeNames.forEach(function (element, index) {
            this[index] = getIconUrl(element);
            if (element === mode) {
              modeIconUrl = this[index];
            }
          }, modeIcons);
          let modeIconsSelected = [];
          modeNames.forEach(function (element, index) {
            this[index] = getIconSelectedUrl(element);
          }, modeIconsSelected);
          caller.setState({
            config: json,
            mode: mode,
            modeNames: modeNames,
            modeIcons: modeIcons,
            modeIconUrl: modeIconUrl,
            modeIconsSelected: modeIconsSelected,
            language: currentLanguage,
            labels: labels
          });
        }).catch(function (e) {
          console.log('Fetch modes problem', e.message);
        });
      })
    }).catch(function (e) {
      console.log('Fetch labels problem', e.message);
    });
  }).catch(function (e) {
    console.log('Fetch config problem', e.message);
  });
};

export function getInfo(caller) {
  fetch(`${baseApiUrl}/info`, { method: "GET" }).then(function (response) {
    return response.json();
  }).then((json) => {
    caller.setState({
      info: json
    });
  }).catch(function (e) {
    console.log('Fetch info problem', e.message);
  });
};

export function getLyrics(caller) {
  fetch(`${baseApiUrl}/lyrics`, { method: "GET" }).then(function (response) {
    return response.text();
  }).then((text) => {
    caller.setState({
      lyrics: text
    });
  }).catch(function (e) {
    console.log('Fetch lyrics problem', e.message);
  });
};

export function getGenre(caller) {
  fetch(`${baseApiUrl}/genre`, { method: "GET" }).then(function (response) {
    return response.text();
  }).then((genre) => {
    caller.setState({
      genre: genre
    });
  }).catch(function (e) {
    console.log('Fetch genre problem', e.message);
  });
};

export function getRadioPlaylist(caller) {
  fetch(`${baseApiUrl}/playlist`, { method: "GET" }).then(function (response) {
    return response.json();
  }).then((json) => {
    caller.setState({
      radioPlaylist: json.playlist
    });
  }).catch(function (e) {
    console.log('Fetch radio playlist problem', e.message);
  });
};

export function getFilePlaylists(caller) {
  fetch(`${baseApiUrl}/fileplaylists`, { method: "GET" }).then(function (response) {
    return response.json();
  }).then((json) => {
    caller.setState({
      filePlaylists: json,
      fileBrowserMode: 'playlists'
    });
  }).catch(function (e) {
    console.log('Fetch file playlists problem', e.message);
  });
};

export function getFilePlaylist(caller, url) {
  fetch(`${baseApiUrl}/fileplaylists?name=${url}`, { method: "GET" }).then(function (response) {
    return response.json();
  }).then((json) => {
    caller.setState({
      filePlaylist: json,
      fileBrowserMode: 'playlists'
    });
  }).catch(function (e) {
    console.log('Fetch file playlist problem', e.message);
  });
};

export function getState(caller, setTimer) {
  const modes = caller.state.modeNames;
  fetch(`${baseApiUrl}/state`, { method: "GET" }).then(function (response) {
    return response.json();
  }).then((state) => {
    let position = 0;
    let timeStep = 0;
    let totalTime = 0;
    let currentTime = 0;

    let modeIconUrl = null;
    if (modes) {
      modes.forEach(function (name) {
        const url = getIconUrl(name);
        if (name === state.mode) {
          modeIconUrl = url;
        }
      });
    }

    if (state.time && state.time.total) {
      totalTime = getSecondsFromString(state.time.total);
      timeStep = totalTime / 100;
      currentTime = getSecondsFromString(state.time.current);
      position = currentTime / timeStep;
    }

    if (caller.state.mode === "audio-files" && caller.state.currentFolder && caller.state.currentFile !== state.currentFile) {
      getFiles(caller, caller.state.currentFolder);
    }

    caller.setState({
      mode: state.mode,
      modeIconUrl: modeIconUrl,
      metadata: state.metadata,
      title: state.title,
      volume: state.volume,
      pause: state.pause,
      mute: state.mute,
      time: state.time,
      timeSliderPosition: position,
      timeStep: timeStep,
      totalTime: totalTime,
      currentTime: currentTime,
      currentFolder: state.currentFolder ? state.currentFolder : null,
      currentFile: state.currentFile ? state.currentFile : null,
    });

    if (state.mode === "radio") {
      getRadioGenres(caller);
      getGenre(caller);
      getRadioPlaylist(caller);
      getInfo(caller);
    } else if (state.mode === "audio-files") {
      getInfo(caller);
      getLyrics(caller);
    }

    if (setTimer) {
      setTimer();
    }

  })
    .catch(function (e) {
      console.log('Fetch state problem', e.message);
    });
};

export function command(url, caller) {
  fetch(url, { method: "PUT" })
    .then(() => {
      getState(caller);
    })
    .catch(function (e) {
      console.log(`Command ${url} problem`, e.message);
    });
};

export function setTime(time, position) {
  let requestBody = {
    time: '' + time,
    position: position
  };
  fetch(`${baseApiUrl}/time`, { method: "PUT", body: JSON.stringify(requestBody) })
    .catch(function (e) {
      console.log("Set time problem", e.message);
    });
}

export function setVolume(_, volume) {
  let requestBody = {
    volume: '' + volume
  };
  fetch(`${baseApiUrl}/volume`, { method: "PUT", body: JSON.stringify(requestBody) })
    .catch(function (e) {
      console.log("Set volume problem", e.message);
    });
}

export function setRadioStation(caller, index, genre, url) {
  let requestBody = {
    index: index,
    genre: genre,
    url: url
  };
  fetch(`${baseApiUrl}/radioplayer`, { method: "PUT", body: JSON.stringify(requestBody) })
    .then(() => {
      caller.setState({
        openBrowser: false
      });
    })
    .catch(function (e) {
      console.log("Set radio station problem", e.message);
    });
}

export function setMode(event, caller) {
  const mode = event.target.alt;
  let requestBody = {
    mode: mode
  };
  fetch(`${baseApiUrl}/mode`, { method: "PUT", body: JSON.stringify(requestBody) })
    .then(() => {

      let properties = {
        openHome: false,
        mode: mode
      }

      if (mode === "radio") {
        getRadioGenres(caller);
        getGenre(caller);
        getRadioPlaylist(caller);
      } else if (mode === "audio-files") {
        getFiles(caller);
      } else if (mode === "radio-browser") {
        properties.image = defaultStationImageUrl;
      }

      caller.setState(properties);
    })
    .catch(function (e) {
      console.log("Set mode problem", e.message);
    });
}

export function setGenre(event, caller) {
  const genre = event.target.alt;
  let requestBody = {
    genre: genre
  };
  fetch(`${baseApiUrl}/genre`, { method: "PUT", body: JSON.stringify(requestBody) })
    .then(() => {
      caller.setState({
        openGenre: false
      });
      getGenre(caller);
      getRadioPlaylist(caller);
    })
    .catch(function (e) {
      console.log("Set genre problem", e.message);
    });
}

export function getRadioGenres(caller) {
  fetch(`${baseApiUrl}/genres`, { method: "GET" }).then((response) => {
    return response.json();
  }).then((genres) => {
    let radioGenreIcons = [];
    genres.forEach(function (element, index) {
      this[index] = getGenreIconUrl(element);
    }, radioGenreIcons);
    let radioGenreIconsSelected = [];
    genres.forEach(function (element, index) {
      this[index] = getGenreIconSelectedUrl(element);
    }, radioGenreIconsSelected);
    caller.setState({
      genres: genres,
      genreIcons: radioGenreIcons,
      genreIconsSelected: radioGenreIconsSelected
    });
  }).catch(function (e) {
    console.log('Fetch radio genres problem', e.message);
  });
};

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
    if (json) {
      let index = null;
      if (json.content && caller.state.currentFolder && caller.state.currentFile && caller.state.currentFolder === json.folder) {
        json.content.forEach ((item, i) => {
          if (item.type === "file" && item.name === caller.state.currentFile) {
            index = i;
          }
        });
      }

      caller.setState({ 
        files: json,
        currentFileIndex: index,
        fileBrowserMode: 'files'
      });
    }
  }).catch(function (e) {
    console.log('Fetch files problem: ' + e.message);
  });
};

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
};

export function setFile(folder, file) {
  let requestBody = {
    folder: folder,
    file: file
  };
  fetch(`${baseApiUrl}/fileplayer`, { method: "PUT", body: JSON.stringify(requestBody) })
    .catch(function (e) {
      console.log("Set file problem", e.message);
    });
};

export function setPlaylistFile(file) {
  let requestBody = {
    file: file
  };
  fetch(`${baseApiUrl}/playlistfileplayer`, { method: "PUT", body: JSON.stringify(requestBody) })
    .catch(function (e) {
      console.log("Set playlist file problem", e.message);
    });
};

export function getRadioBrowserCountries(caller) {
  if (caller.state.radioBrowserCountries !== null) {
    return caller.state.radioBrowserCountries;
  }

  fetch(`${baseApiUrl}/radiobrowser?category=countries`, { method: "GET" }).then((response) => {
    return response.json();
  }).then((countries) => {
    caller.setState({ 
      radioBrowserCountries: countries,
      radioBrowserCategory: "countries"
    });
  }).catch(function (e) {
    console.log('Fetch radio browser countries problem', e.message);
  });
};

export function getStationsByCountry(caller, country) {
  fetch(`${baseApiUrl}/radiobrowser?country=${country}`, { method: "GET" }).then((response) => {
    return response.json();
  }).then((stations) => {
    caller.setState({ 
      radioBrowserStations: stations
    });
  }).catch(function (e) {
    console.log('Fetch radio browser stations by country problem', e.message);
  });
};
