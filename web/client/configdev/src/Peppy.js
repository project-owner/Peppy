/* Copyright 2019-2022 Peppy Player peppy.player@gmail.com
 
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
import { withStyles } from "@material-ui/core/styles";
import Template from "./Template";
import styles from "./Style";
import SelectLanguage from "./components/SelectLanguage";
import TabContainer from "./components/TabContainer";
import TabContainerPlaylist from "./components/TabContainerPlaylist";
import Navigator from "./components/Navigator";
import Copyright from "./components/Copyright";
import Buttons from "./components/Buttons";
import Notification from "./components/Notification";
import ConfigTab from "./tabs/ConfigTab";
import PlayersTab, { PlayersMenu } from "./tabs/PlayersTab";
import ScreensaversTab from "./tabs/ScreensaversTab";
import RadioPlaylistsTab from "./tabs/RadioPlaylistsTab";
import PodcastsTab from "./tabs/PodcastsTab";
import StreamsTab from "./tabs/StreamsTab";
import YaStreamsTab from "./tabs/YaStreamsTab";
import SystemTab from "./tabs/SystemTab";
import Logo from "./components/Logo";
import ConfirmationDialog from "./components/ConfirmationDialog";
import LinearProgress from '@material-ui/core/LinearProgress';
import {
  getParameters, getPlayers, getScreensavers, getRadioPlaylist, getPodcasts, getStreams, getYaStreams, changeLanguage,
  save, reboot, shutdown, getBackground, getFonts, getSystem, setDefaults, setNewTimezone, addNewNas, getPlaylists,
  mount, unmount, poweroff, refresh, getLog, uploadPlaylist, refreshNases, mntNas, unmntNas, deleteNas, addNewShare, 
  deleteShare, uploadFont
} from "./Fetchers";
import {
  updateConfiguration, updatePlayers, updateScreensavers, updatePlaylists, updatePodcasts, updateStreams, updateYaStreams,
  updateStreamsText, updatePlaylistText, updateBackground, updateDefaults, updateTimezone, updateNas, updateShare
} from "./Updater"
import { State } from "./State"

let player = new Audio();
let bgrParameters = [
  "bgr.type", "screen.bgr.color", "screen.bgr.names", "web.bgr.names", "header.bgr.opacity",
  "menu.bgr.opacity", "footer.bgr.opacity", "web.screen.bgr.opacity"
];

class Peppy extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      ...State,
      playing: false
    };
    this.colorBackup = {};
  }

  play = (src) => {
    try {
      player.src = src;
      const p = player.play();
      p.then(() => {
        this.setState({ playing: true });
      }).catch(e => {
        console.log(e.message);
        this.setState({ playing: false });
        player.pause();
      })
    }
    catch (err) {
      this.setState({ playing: false });
      player.pause();
      console.log(err.message);
    }
  }

  pause = () => {
    try {
      if (player && this.state.playing) {
        player.pause();
        this.setState({ playing: false });
        return;
      }
    }
    catch (err) {
      console.log(err.message);
    }
  }

  handleTabChange = (_, value) => {
    this.setState({
      tabIndex: value,
      currentMenuItem: 0
    }, this.refreshTab(value));
  }

  handlePlaylistsTabChange = (_, value) => {
    this.setState({
      playlistTabIndex: value,
      currentMenuItem: 0
    }, this.refreshPlaylistsTab(value));
  }

  refreshTab = (tabIndex) => {
    const tabFunctions = [getParameters, getPlayers, getScreensavers, getPlaylists, getSystem];
    tabFunctions[tabIndex](this);
    if (tabIndex === 0) {
      getBackground(this);
    }
    if (tabIndex === 3) { // playlists
      this.refreshPlaylistsTab(0);
    }
  }

  refreshPlaylistsTab = (playlistTabIndex) => {
    const tabFunctions = [getRadioPlaylist, getPodcasts, getStreams, getYaStreams];
    tabFunctions[playlistTabIndex](this);
    if (playlistTabIndex === 0) {
      getBackground(this);
    }
  }

  updatePlaylist = (index) => {
    if (this.state.tabIndex === 3 || this.state.playlistTabIndex === 0) {
      const lang = this.state.playlists[this.state.language];
      const genre = this.getRadioPlaylistMenu()[index];
      if (!(lang && lang[genre])) {
        getRadioPlaylist(this, index);
      }
    }
  }

  handleListItemClick = (_, index) => {
    this.setState({ currentMenuItem: index }, this.updatePlaylist(index));
  }

  getConfigMenu() {
    const labels = this.state.labels;

    return [
      labels.display, labels.usage, labels.logging, labels["file.browser"],
      labels["web.server"], labels["stream.server"], labels.podcasts, labels["home.menu"],
      labels["home.navigator"], labels["screensaver.menu"], labels["delay"], labels["languages.menu"], 
      labels["collection"], labels["collection.menu"], labels["disk.mount"], 
      labels["voice.assistant"], labels.colors, labels["icons"], labels["background"], 
      labels.font, labels["volume.control"], labels["player.screen"], labels["display.backlight"], 
      labels.scripts, labels["gpio"], labels["i2c"]
    ];
  }

  getScreensaversMenu() {
    const labels = this.state.labels;
    return [labels.clock, labels.logo, labels.slideshow, labels.weather, labels.lyrics,
      labels.pexels, labels.monitor, labels.horoscope, labels.stock, labels.random]
  }

  getRadioPlaylistMenu() {
    const language = this.state.language;
    const languages = this.state.parameters.languages
    let menu = undefined;

    languages.forEach((lang) => {
      if (lang.name === language) {
        const key = Object.keys(lang.stations)[0]
        menu = lang.stations[key];
      }
    })
    return menu;
  }

  getSystemMenu() {
    const labels = this.state.labels;
    return [labels.timezone, labels["disk.manager"], labels["nas.manager"], labels["share.manager"], labels.defaults, labels["log.file"]]
  }

  getMenu() {
    if (!this.state.parameters || !this.state.labels) {
      return null;
    }

    const tab = this.state.tabIndex;
    const playlistTabIndex = this.state.playlistTabIndex;

    if (tab === 0) {
      return this.getConfigMenu();
    } else if (tab === 1) {
      return PlayersMenu;
    } else if (tab === 2) {
      return this.getScreensaversMenu();
    } else if (tab === 3) {
      if (playlistTabIndex === 0) {
        return this.getRadioPlaylistMenu();
      } else {
        return null;
      }
    } else if (tab === 4) {
      return this.getSystemMenu();
    }
  }

  resetColors = () => {
    const newState = Object.assign({}, this.state);
    try {
      const clone = JSON.parse(JSON.stringify(this.colorBackup));
      newState.parameters.colors = clone;
      newState.parametersDirty = true;
      this.setState(newState);
    } catch (err) {
      console.log(err.message);
    }
  }

  setPalette = (palette) => {
    const newState = Object.assign({}, this.state);
    try {
      const clone = JSON.parse(JSON.stringify(palette));
      newState.parameters.colors = clone;
      newState.parametersDirty = true;
      this.setState(newState);
    } catch (err) {
      console.log(err.message);
    }
  }

  updateState = (name, value, index) => {
    if (this.state.tabIndex === 0) {
      if (bgrParameters.includes(name)) {
        updateBackground(this, name, value);
      } else {
        updateConfiguration(this, name, value, index);
      }
    } else if (this.state.tabIndex === 1) {
      updatePlayers(this, name, value);
    } else if (this.state.tabIndex === 2) {
      updateScreensavers(this, name, value);
    } else if (this.state.tabIndex === 3) {
      const playlistTabIndex = this.state.playlistTabIndex;
      if (playlistTabIndex === 0) {
        updatePlaylists(this, value);
      } else if (playlistTabIndex === 1) {
        updatePodcasts(this, value);
      } else if (playlistTabIndex === 2) {
        updateStreams(this, value);
      } else if (playlistTabIndex === 3) {
        updateYaStreams(this, value);
      }
    }else if (this.state.tabIndex === 4) {
      if (this.state.currentMenuItem === 0) {
        updateTimezone(this, name, value);
      } else if (this.state.currentMenuItem === 2) {
        updateNas(this, name, value, index);
      } else if (this.state.currentMenuItem === 3) {
        updateShare(this, name, value, index);
      } else if (this.state.currentMenuItem === 4) {
        updateDefaults(this, name, value);
      }
    }
  }

  updateItemState = (item, fieldName, value, items) => {
    item[fieldName] = value;
    const playlistTabIndex = this.state.playlistTabIndex;

    if (this.state.tabIndex === 3 && playlistTabIndex === 0) {
      updatePlaylists(this, items);
    } else if (this.state.tabIndex === 3 && playlistTabIndex === 2) {
      updateStreams(this, items);
    }
  }

  updateStreamsTextFn = (text) => {
    updateStreamsText(this, text);
  }

  updatePlaylistTextFn = (text) => {
    updatePlaylistText(this, text);
  }

  handleSnackClose = () => {
    this.setState({ openSnack: false });
  }

  setColor = (name, value, index) => {
    this.updateState(name, value, index);
  }

  rebootPlayer = () => {
    reboot(this, true);
  }

  saveAndReboot = () => {
    save(this, () => { reboot(this, true) });
  }

  shutdownPlayer = () => {
    shutdown(this);
  }

  saveAndShutdown = () => {
    save(this, () => { shutdown(this) });
  }

  changeCurrentLanguage = (event) => {
    changeLanguage(event, this);
  }

  setDefaultsAndReboot = () => {
    setDefaults(this);
    reboot(this, false);
  }

  setTimezone = () => {
    setNewTimezone(this);
  }

  mountDisk = (name, device, mountPoint) => {
    mount(this, name, device, mountPoint);
  }

  unmountDisk = (device) => {
    unmount(this, device);
  }

  poweroffDisk = (device) => {
    poweroff(this, device);
  }

  refreshDisks = () => {
    refresh(this);
  }

  addNas = () => {
    addNewNas(this);
  }

  delNas = (index) => {
    deleteNas(this, index);
  }

  mountNas = (index) => {
    mntNas(this, index);
  }

  unmountNas = (index) => {
    unmntNas(this, index);
  }

  refreshNas = () => {
    refreshNases(this);
  }

  addShare = () => {
    addNewShare(this);
  }

  delShare = (index) => {
    deleteShare(this, index);
  }

  getLogFile = (refreshLog) => {
    getLog(this, refreshLog);
  }

  upload = (path, data, id) => {
    uploadPlaylist(this, path, data, id);
  }

  uploadFontFile = (data) => {
    uploadFont(this, data);
  }

  isDirty = () => {
    return this.state.parametersDirty || this.state.playersDirty || this.state.screensaversDirty ||
      this.state.playlistsDirty || this.state.podcastsDirty || this.state.streamsDirty || this.state.yaStreamsDirty ||
      this.state.backgroundDirty || this.state.nasDirty || this.state.shareDirty || this.state.yastreamsDirty ? true : false;
  }

  handleRebootDialog = () => {
    if (this.isDirty()) {
      this.setState({ isSaveAndRebootDialogOpen: true });
    } else {
      this.setState({ isRebootDialogOpen: true });
    }
  }

  handleShutdownDialog = () => {
    if (this.isDirty()) {
      this.setState({ isSaveAndShutdownDialogOpen: true });
    } else {
      this.setState({ isShutdownDialogOpen: true });
    }
  }

  handleSetDefaultsAndRebootDialog = () => {
    if (this.state.system === null || this.state.system.defaults == null ||
      (!this.state.system.defaults[0] && !this.state.system.defaults[1] && !this.state.system.defaults[2])) {
      const msg = this.state.labels["nothing.save"];
      this.setState({
        openSnack: true,
        notificationMessage: msg,
        notificationVariant: "warning"
      });
      return;
    }

    this.setState({ isSetDefaultsAndRebootDialogOpen: true });
  }

  render() {
    const { classes } = this.props;
    const { tabIndex, currentMenuItem, parameters, labels, background } = this.state;
    const playlistTabIndex = this.state.playlistTabIndex;

    if (!parameters || !labels || this.state.playerWasRebooted) {
      getParameters(this);
      getBackground(this);
      getFonts(this);
      return null;
    }

    if (tabIndex === 1 && this.state.players == null) {
      getPlayers(this);
      return null;
    } else if (tabIndex === 2 && this.state.screensavers == null) {
      getScreensavers(this);
      return null;
    } else if (tabIndex === 3) {
      if (playlistTabIndex === 0 && this.state.playlists == null) {
        getRadioPlaylist(this, 0);
        return null;
      } else if (playlistTabIndex === 1 && this.state.podcasts == null) {
        getPodcasts(this);
        return null;
      } else if (playlistTabIndex === 2 && this.state.streams == null) {
        getStreams(this);
        return null;
      } else if (playlistTabIndex === 3 && this.state.yastreams == null) {
        getYaStreams(this);
        return null;
      }
    } else if (tabIndex === 4 && this.state.system == null) {
      return null;
    }

    return (
      <Template
        labels={this.state.labels}
        hide={this.state.hideUi}
        reboot={this.state.reboot}
        shutdown={this.state.shutdown}
        logo={<Logo classes={classes} release={this.state.parameters.release} />}
        headerLanguage={
          <SelectLanguage
            classes={classes}
            flags={this.state.flags}
            languages={parameters.languages}
            language={this.state.language}
            onChange={this.changeCurrentLanguage}
            labels={labels} />
        }
        headerTabs={
          <TabContainer
            classes={classes}
            labels={labels}
            tabIndex={tabIndex}
            handleTabChange={this.handleTabChange} />
        }
        headerSubTabs={
          tabIndex === 3 && <TabContainerPlaylist
            classes={classes}
            tabIndex={this.state.playlistTabIndex}
            labels={labels}
            yastreams={this.state.yastreams}
            updateState={this.updateState}
            handleTabChange={this.handlePlaylistsTabChange} />
        }
        navigator={
          <Navigator
            classes={classes}
            menu={this.getMenu()}
            currentMenuItem={currentMenuItem}
            handleListItemClick={this.handleListItemClick} />
        }
        footerProgress={this.state.showProgress && <LinearProgress color="secondary" />}
        footerButtons={
          <Buttons
            classes={classes}
            lang={this.state.language}
            save={() => { save(this) }}
            labels={labels}
            buttonsDisabled={this.state.buttonsDisabled}
            openRebootDialog={this.handleRebootDialog}
            openShutdownDialog={this.handleShutdownDialog} />
        }
        footerCopyright={<Copyright classes={classes} release={this.state.parameters.release} />}
        notification={
          this.state.notificationMessage && <Notification
            variant={this.state.notificationVariant}
            openSnack={this.state.openSnack}
            message={this.state.notificationMessage}
            handleSnackClose={this.handleSnackClose} />
        }
        rebootDialog={
          <ConfirmationDialog
            classes={classes}
            title={labels["reboot"]}
            message={labels["confirm.reboot.title"] + " " + labels["confirm.reboot.message"]}
            yes={labels.yes}
            no={labels.no}
            isDialogOpen={this.state.isRebootDialogOpen}
            yesAction={this.rebootPlayer}
            noAction={() => { this.setState({ isRebootDialogOpen: false }) }}
            cancelAction={() => { this.setState({ isRebootDialogOpen: false }) }}
          />
        }
        saveAndRebootDialog={
          <ConfirmationDialog
            classes={classes}
            style={{whiteSpace: "pre-line"}}
            title={labels["reboot"]}
            message={labels["confirm.save.reboot.title"] + " " + labels["confirm.save.reboot.message"]}
            yes={labels.yes}
            no={labels.no}
            isDialogOpen={this.state.isSaveAndRebootDialogOpen}
            yesAction={this.saveAndReboot}
            noAction={this.rebootPlayer}
            cancelAction={() => { this.setState({ isSaveAndRebootDialogOpen: false }) }}
          />
        }
        shutdownDialog={
          <ConfirmationDialog
            classes={classes}
            title={labels["shutdown"]}
            message={labels["confirm.shutdown.title"] + " " + labels["confirm.shutdown.message"]}
            yes={labels.yes}
            no={labels.no}
            isDialogOpen={this.state.isShutdownDialogOpen}
            yesAction={() => { shutdown(this) }}
            noAction={() => { this.setState({ isShutdownDialogOpen: false }) }}
            cancelAction={() => { this.setState({ isShutdownDialogOpen: false }) }}
          />
        }
        saveAndShutdownDialog={
          <ConfirmationDialog
            classes={classes}
            title={labels["shutdown"]}
            message={labels["confirm.save.shutdown.title"] + " " + labels["confirm.save.shutdown.message"]}
            yes={labels.yes}
            no={labels.no}
            isDialogOpen={this.state.isSaveAndShutdownDialogOpen}
            yesAction={this.saveAndShutdown}
            noAction={this.shutdownPlayer}
            cancelAction={() => { this.setState({ isSaveAndShutdownDialogOpen: false }) }}
          />
        }
        setDefaultsAndRebootDialog={
          <ConfirmationDialog
            classes={classes}
            style={{whiteSpace: "pre-line"}}
            title={labels["set.default"]}
            message={labels["confirm.set.defaults"]}
            yes={labels.yes}
            no={labels.no}
            isDialogOpen={this.state.isSetDefaultsAndRebootDialogOpen}
            yesAction={this.setDefaultsAndReboot}
            noAction={() => { this.setState({ isSetDefaultsAndRebootDialogOpen: false }) }}
            cancelAction={() => { this.setState({ isSetDefaultsAndRebootDialogOpen: false }) }}
          />
        }
        content={
          <div>
            {tabIndex === 0 &&
              <ConfigTab
                params={parameters}
                labels={this.state.labels}
                topic={currentMenuItem}
                classes={classes}
                setPalette={this.setPalette}
                setColor={this.setColor}
                reset={this.resetColors}
                updateState={this.updateState}
                background={background}
                fonts={this.state.fonts}
                uploadFont={this.uploadFontFile}
                languages={parameters.languages}
                language={this.state.language}
              />
            }
            {tabIndex === 1 &&
              <PlayersTab
                players={this.state.players}
                topic={currentMenuItem}
                labels={labels}
                classes={classes}
                updateState={this.updateState}
              />
            }
            {tabIndex === 2 &&
              <ScreensaversTab
                language={this.state.language}
                topic={currentMenuItem}
                labels={labels}
                classes={classes}
                screensavers={this.state.screensavers}
                updateState={this.updateState}
                fonts={this.state.fonts}
                clockImageFolders={this.state.clockImageFolders}
              />
            }
            {tabIndex === 3  && playlistTabIndex === 0 &&
              <RadioPlaylistsTab
                labels={labels}
                language={this.state.language}
                classes={classes}
                playlists={this.state.playlists}
                texts={this.state.playlistsTexts}
                basePath={this.state.playlistBasePath}
                genre={this.getRadioPlaylistMenu()[this.state.currentMenuItem]}
                updateState={this.updateState}
                updateItemState={this.updateItemState}
                updateText={this.updatePlaylistTextFn}
                play={this.play}
                pause={this.pause}
                playing={this.state.playing}
                uploadPlaylist={this.upload}
              />
            }
            {tabIndex === 3 && playlistTabIndex === 1 &&
              <PodcastsTab
                topic={currentMenuItem}
                labels={labels}
                classes={classes}
                podcasts={this.state.podcasts}
                updateState={this.updateState}
              />
            }
            {tabIndex === 3 && playlistTabIndex === 2 &&
              <StreamsTab
                id={"streams"}
                topic={currentMenuItem}
                labels={labels}
                classes={classes}
                streams={this.state.streams}
                text={this.state.streamsText}
                basePath={this.state.streamsBasePath}
                updateState={this.updateState}
                updateItemState={this.updateItemState}
                updateText={this.updateStreamsTextFn}
                play={this.play}
                pause={this.pause}
                playing={this.state.playing}
                uploadPlaylist={null}
              />
            }
            {tabIndex === 3 && playlistTabIndex === 3 &&
              <YaStreamsTab
                topic={currentMenuItem}
                labels={labels}
                classes={classes}
                playlistTabIndex={playlistTabIndex}
                yastreams={this.state.yastreams}
                updateState={this.updateState}
              />
            }
            {tabIndex === 4 &&
              <SystemTab
                params={this.state.system}
                topic={currentMenuItem}
                labels={labels}
                classes={classes}
                updateState={this.updateState}
                setDefaults={this.handleSetDefaultsAndRebootDialog}
                setTimezone={this.setTimezone}
                disks={this.state.system.disks}
                addNas={this.addNas}
                delNas={this.delNas}
                mount={this.mountDisk}
                unmount={this.unmountDisk}
                poweroff={this.poweroffDisk}
                refresh={this.refreshDisks}
                nases={this.state.system.nases}
                mountNas={this.mountNas}
                unmountNas={this.unmountNas}
                refreshNas={this.refreshNas}
                shares={this.state.system.shares}
                addShare={this.addShare}
                delShare={this.delShare}
                log={this.state.log}
                getLog={this.getLogFile}
              />
            }
          </div>
        }
      />
    );
  }
}

export default withStyles(styles)(Peppy);
