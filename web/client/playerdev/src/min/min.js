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

import React from "react";
import { Window, EmptyWindow, PlayerFrame, MainPanel, ImageLabelsSlider, LabelsSlider, AlbumArt, WindowBackground } from './mincss';
import TimeSlider from './TimeSlider';
import Buttons from './Buttons';
import Labels from './Labels';
import { State } from "./State"
import { getWebSocket } from "../Communicator";
import {
  getConfig, getInfo, getState, command, setTime, baseApiUrl, setMode, setGenre, setRadioStation, getLyrics, getFiles, 
  goToRoot, setFile, getFilePlaylists, getFilePlaylist, setPlaylistFile, getRadioBrowserCountries, getStationsByCountry
} from "../Rest";
import Home from "./Home";
import Track from "./Track";
import Volume from "./Volume";
import Genre from "./Genre";
import RadioPlaylist from "./RadioPlaylist";
import RadioBrowser from "./RadioBrowser";
import FileBrowser from "./FileBrowser";
import { getStringFromSeconds } from "../Util";

export default class PeppyPlayer extends React.Component {
  constructor(props) {
    super(props);
    this.state = { ...State };
    let webSocket = getWebSocket(this.dispatchCommand, this.webSocketClosedInServer);
    this.state.webSocket = webSocket;
    this.state.image = `${baseApiUrl}/image?${Date.now()}`;
    getConfig(this);
    getState(this, this.setTimer);
  }

  webSocketClosedInServer = (socket) => {
    clearInterval(this.timer);
    console.log("webSocket closed on server side");
    if (socket.target !== null) {
      try {
        socket.target.close();
        this.webSocket = null;
      } catch (e) {
        console.log(e);
      }
    }
    console.log("webSocket closed in client");
    this.setState({
      running: false,
      openHome: false,
      openBrowser: false,
      openGenre: false,
      openVolume: false,
      openTrack: false
    });
  }

  dispatchCommand = (msg) => {
    var d = {}
    try {
      d = JSON.parse(msg.data);
    } catch (e) {
      console.log("error parsing message from server");
      return;
    }

    var c = d["command"];

    if (c === "update_screen") {
      if (this.state.mode !== "radio-browser") {
        this.setState({
          "image": `${baseApiUrl}/image?${Date.now()}`
        });
      }
      getState(this);
    } else if (c === "start_timer") {
      getState(this);

      if (this.state && this.state.pause !== null && !this.state.pause) {
        this.setTimer();
      }
    } else if (c === "stop_timer") {
      clearInterval(this.timer);
      setTimeout(() => {
        getState(this);
      }, 300);
    } else if (c === "mode_changed") {
      clearInterval(this.timer);
      if (this.state.mode !== "radio-browser") {
        this.setState({
          "image": `${baseApiUrl}/image?${Date.now()}`
        });
      }
      getState(this);
    }
  }

  toggleHome = (flag) => () => {
    this.setState({ openHome: flag });
  };

  toggleRadioPlaylist = (flag) => () => {
    this.setState({ openRadioPlaylist: flag });
  };

  toggleRadioBrowser = (flag) => () => {
    this.setState({ openRadioBrowser: flag });
  };

  toggleFiles = (flag) => () => {
    if (this.state.files === null) {
      getFiles(this, this.state.currentFolder);
    }
    this.setState({ openFileBrowser: flag });
  };

  toggleTrack = (flag) => () => {
    getInfo(this);
    getLyrics(this)
    this.setState({ openTrack: flag });
  };

  toggleGenre = (flag) => () => {
    this.setState({ openGenre: flag });
  };

  next = () => {
    command(`${baseApiUrl}/next`, this);
  }

  previous = () => {
    command(`${baseApiUrl}/previous`, this);
  }

  playPause = () => {
    command(`${baseApiUrl}/playpause`, this);
  }

  toggleVolume = (flag) => () => {
    this.setState({ openVolume: flag });
  };

  mute = () => {
    command(`${baseApiUrl}/mute`, this);
  }

  changeMode = (event) => {
    setMode(event, this);
  }

  changeGenre = (event) => {
    setGenre(event, this);
  }

  changeRadioStation = (index, genre, url) => {
    setRadioStation(this, index, genre, url);
  }

  handleFileClick = (index) => {
    let file = this.state.files.content[index];

    if (file && file.type === "folder") {
      getFiles(this, file.url);
    } else if (file && file.type === "file") {
      setFile(this.state.files.folder, file.name);
      this.setState({
        openFileBrowser: false,
        currentFileIndex: index,
        currentFile: file.name
      });
    }
  }

  handlePlaylistFileClick = (value, index) => {
    if (this.state.filePlaylist === null) {
      return;
    }

    if (value) {
      setPlaylistFile(value);
      this.setState({
        openFileBrowser: false,
        currentPlaylistFileIndex: index,
        currentPlaylistFile: value
      });
    }
  }

  goToDefaultMusicFolder = () => {
    getFiles(this);
  }

  selectBreadcrumb = (path) => {
    getFiles(this, path);
  }

  goToFileSystemRoot = () => {
    goToRoot(this);
  }

  getFilePlaylists = () => {
    getFilePlaylists(this);
  }

  getFilePlaylist = (index) => {
    if(this.state.filePlaylists) { 
      this.state.filePlaylists.forEach((e, i) => {
        if (i === index) {
          getFilePlaylist(this, e.url);
        }
      });
    }
  }

  getRadioBrowserCountries = () => {
    getRadioBrowserCountries(this);
  }

  setRadioBrowserCountry = (index) => {
    this.setState({
      currentRadioBrowserCountryIndex: index
    });
    getStationsByCountry(this, this.state.countries[index].name);
  }

  shutdown = () => {
    command(`${baseApiUrl}/shutdown`, this);
    this.setState({
      openHome: false,
      openBrowser: false,
      openTrack: false,
      openVolume: false
    });
  }

  reboot = () => {
    command(`${baseApiUrl}/reboot`, this);
    this.setState({
      openHome: false,
      openBrowser: false,
      openTrack: false,
      openVolume: false
    });
  }

  setTimeSliderPosition = (_, value) => {
    if (this.state.time && this.state.time.total) {
      const timeTotalStr = this.state.time.total;
      const currentTime = value * this.state.timeStep;
      this.setState(
        {
          timeSliderPosition: value,
          currentTime: currentTime,
          time: {
            total: timeTotalStr,
            current: getStringFromSeconds(currentTime)
          }
        }
      );
      if (this.state && this.state.pause !== null && !this.state.pause) {
        this.setTimer();
      }
    }
  };

  setVolumePosition = (_, value) => {
    this.setState(
      {
        volume: value,
      }
    );
  };

  setTimer = () => {
    if (this.timer) {
      clearInterval(this.timer);
    }
    if (this.state === null || (this.state !== null && this.state.pause === null) ||
      (this.state !== null && this.state.pause !== null && this.state.pause)) {
      return;
    }
    this.timer = setInterval(() => {
      let currentTime = this.state.currentTime;
      if (currentTime + 1 < this.state.totalTime) {
        ++currentTime;
        let currentPosition = currentTime / this.state.timeStep;
        const timeTotalStr = this.state.time.total;
        const current = getStringFromSeconds(currentTime);
        this.setState(
          {
            time: {
              total: timeTotalStr,
              current: current
            },
            timeSliderPosition: currentPosition,
            currentTime: currentTime
          }
        );
      }
    }, 1000);
  };

  setPlayTime = (_, time) => {
    const playTime = Math.ceil(time * this.state.timeStep);
    setTime(playTime, this.state.timeSliderPosition);
  }

  render() {
    let label1 = null;
    let label2 = null;
    let label3 = null;
    let toggle = null;

    if (this.state.mode === "audio-files") {
      label1 = this.state.title;
      label2 = this.state.metadata.album;
      label3 = this.state.metadata.artist;
      toggle = this.toggleFiles;
    } else if (this.state.mode === "radio") {
      label1 = this.state.title;
      label2 = this.state.metadata.playlist_genre_translated;
      label3 = label1 !== this.state.metadata.playlist_name ? label3 = this.state.metadata.playlist_name : null;
      toggle = this.toggleRadioPlaylist;
    } else if (this.state.mode === "radio-browser") {
      toggle = this.toggleRadioBrowser;
    }

    return (
      <div style={this.state.running ? Window : EmptyWindow}>
        <div style={WindowBackground} />
        <Home
          openHome={this.state.openHome}
          toggleHome={this.toggleHome}
          modeIcons={this.state.modeIcons}
          mode={this.state.mode}
          modeIconsSelected={this.state.modeIconsSelected}
          modeNames={this.state.modeNames}
          labels={this.state.labels}
          shutdown={this.shutdown}
          reboot={this.reboot}
          changeMode={this.changeMode}
        />
        <Genre
          openGenre={this.state.openGenre}
          toggleGenre={this.toggleGenre}
          genre={this.state.genre}
          genreIcons={this.state.genreIcons}
          genreIconsSelected={this.state.genreIconsSelected}
          genres={this.state.genres}
          changeGenre={this.changeGenre}
        />
        {/* --------------------- Browsers --------------------- */}
        {this.state.mode === "radio" && <RadioPlaylist
          openBrowser={this.state.openRadioPlaylist}
          toggleBrowser={this.toggleRadioPlaylist}
          currentStation={label3 !== null ? label3 : label1}
          playlist={this.state.radioPlaylist}
          callback={this.changeRadioStation}
        />}
        {this.state.mode === "radio-browser" && <RadioBrowser
          openBrowser={this.state.openRadioBrowser}
          toggleBrowser={this.toggleRadioBrowser}
          labels={this.state.labels}
          getRadioBrowserCountries={this.getRadioBrowserCountries}
          countries={this.state.radioBrowserCountries}
          radioBrowserCategory={this.state.radioBrowserCategory}
          currentRadioBrowserStationIndex={this.state.currentRadioBrowserStationIndex}
          setRadioBrowserCountry={this.setRadioBrowserCountry}
          radioBrowserStations={this.state.radioBrowserStations}
        />}
        {this.state.mode === "audio-files" && <FileBrowser
          openBrowser={this.state.openFileBrowser}
          toggleBrowser={this.toggleFiles}
          files={this.state.files}
          handleFileClick={this.handleFileClick}
          selectAllFiles={this.selectAllFiles}
          goToDefaultMusicFolder={this.goToDefaultMusicFolder}
          goToFileSystemRoot={this.goToFileSystemRoot}
          selectBreadcrumb={this.selectBreadcrumb}
          currentFileIndex={this.state.currentFileIndex}
          getFilePlaylists={this.getFilePlaylists}
          fileBrowserMode={this.state.fileBrowserMode}
          playlists={this.state.filePlaylists}
          getFilePlaylist={this.getFilePlaylist}
          playlist={this.state.filePlaylist}
          handlePlaylistFileClick={this.handlePlaylistFileClick}
          currentPlaylistFileIndex={this.state.currentPlaylistFileIndex}
        />}

        {/* --------------------- Info/Lyrics --------------------- */}
        <Track
          openTrack={this.state.openTrack}
          toggleTrack={this.toggleTrack}
          info={this.state.info}
          lyrics={this.state.lyrics}
          labels={this.state.labels}
        />
        <Volume
          openVolume={this.state.openVolume}
          toggleVolume={this.toggleVolume}
          volume={this.state.volume}
          setPosition={this.setVolumePosition}
          mute={this.state.mute}
          setMute={this.mute}
        />
        <div style={PlayerFrame}>
          <div style={MainPanel}>
            <div style={ImageLabelsSlider}>
              <div style={AlbumArt} onClick={toggle !== null && toggle(true)}>
                <img component="img" style={AlbumArt} alt='album' src={`${this.state.image}`} />
              </div>
              <div style={LabelsSlider}>
                {<Labels
                  mode={this.state.mode}
                  label1={label1}
                  label2={label2}
                  label3={label3}
                  toggleTrack={this.toggleTrack}
                  toggleGenre={this.state.mode === "radio" ? this.toggleGenre : null}
                  changeGenre={this.changeGenre}
                />}
                {this.state.mode === 'audio-files' && this.state.time !== null &&
                  <TimeSlider
                    mode={this.state.mode}
                    timeCurrent={this.state.time.current}
                    timeTotal={this.state.time.total}
                    position={this.state.timeSliderPosition}
                    setTimeSliderPosition={this.setTimeSliderPosition}
                    setTime={this.setPlayTime}
                  />
                }
              </div>
            </div>
          </div>
          <Buttons
            pause={this.state.pause}
            toggleHome={this.toggleHome}
            toggleVolume={this.toggleVolume}
            modeIconUrl={this.state.modeIconUrl}
            next={this.next}
            previous={this.previous}
            playPause={this.playPause}
            mute={this.state.mute}
          />
        </div>
        <div style={{ marginTop: 'auto' }} />
      </div>
    );
  }
}