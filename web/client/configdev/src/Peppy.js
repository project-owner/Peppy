import React from "react";
import { withStyles } from "@material-ui/core/styles";
import Template from "./Template";
import styles from "./Style";
import SelectLanguage from "./components/SelectLanguage";
import TabContainer from "./components/TabContainer";
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
import Logo from "./components/Logo";
import ConfirmationDialog from "./components/ConfirmationDialog";
import LinearProgress from '@material-ui/core/LinearProgress';
import {
  getParameters, getPlayers, getScreensavers, getRadioPlaylist, getPodcasts, getStreams, changeLanguage,
  save, reboot, shutdown
} from "./Fetchers";
import {
  updateConfiguration, updatePlayers, updateScreensavers, updatePlaylists, updatePodcasts,
  updateStreams
} from "./Updater"
import { State } from "./State"

class Peppy extends React.Component {
  constructor(props) {
    super(props);
    this.state = State;
    this.colorBackup = {};
  }

  handleTabChange = (_, value) => {
    this.setState({
      tabIndex: value,
      currentMenuItem: 0
    }, this.refreshTab(value));
  }

  refreshTab = (tabIndex) => {
    const tabFunctions = [getParameters, getPlayers, getScreensavers, getRadioPlaylist, getPodcasts, getStreams];
    tabFunctions[tabIndex](this);
  }

  handleListItemClick = (_, index) => {
    this.setState({ currentMenuItem: index }, () => {
      if (this.state.tabIndex === 3) {
        const lang = this.state.playlists[this.state.language];
        const genre = this.getRadioPlaylistMenu()[this.state.currentMenuItem];
        if (!(lang && lang[genre])) {
          getRadioPlaylist(this);
        }
      }
    });
  }

  getConfigMenu() {
    const labels = this.state.labels;

    return [
      labels.display, labels.usage, labels.logging, labels["file.browser"],
      labels["web.server"], labels["stream.server"], labels.podcasts, labels["home.menu"],
      labels["home.navigator"], labels["screensaver.menu"], labels["voice.assistant"],
      labels.colors, labels.font, labels.scripts
    ];
  }

  getScreensaversMenu() {
    const labels = this.state.labels;
    return [labels.clock, labels.logo, labels.lyrics, labels.weather, labels.random, labels.slideshow]
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

  getMenu() {
    if (!this.state.parameters || !this.state.labels) {
      return null;
    }

    const tab = this.state.tabIndex;
    if (tab === 0) {
      return this.getConfigMenu();
    } else if (tab === 1) {
      return PlayersMenu;
    } else if (tab === 2) {
      return this.getScreensaversMenu();
    } else if (tab === 3) {
      return this.getRadioPlaylistMenu();
    } else if (tab === 4 || tab === 5) {
      return null;
    }
  }

  resetColors = () => {
    const newState = Object.assign({}, this.state);
    const clone = JSON.parse(JSON.stringify(this.colorBackup));
    newState.parameters.colors = clone;
    newState.parametersDirty = true;
    this.setState(newState);
  }

  setPalette = (palette) => {
    const newState = Object.assign({}, this.state);
    const clone = JSON.parse(JSON.stringify(palette));
    newState.parameters.colors = clone;
    newState.parametersDirty = true;
    this.setState(newState);
  }

  updateState = (name, value, index) => {
    if (this.state.tabIndex === 0) {
      updateConfiguration(this, name, value, index);
    } else if (this.state.tabIndex === 1) {
      updatePlayers(this, name, value);
    } else if (this.state.tabIndex === 2) {
      updateScreensavers(this, name, value);
    } else if (this.state.tabIndex === 3) {
      updatePlaylists(this, value);
    } else if (this.state.tabIndex === 4) {
      updatePodcasts(this, value);
    } else if (this.state.tabIndex === 5) {
      updateStreams(this, value);
    }
  }

  updateWeather = (name, value) => {
    const newState = Object.assign({}, this.state.screensavers);
    newState.peppyweather[this.state.language][name] = value;
    newState.screensaversDirty = true
    this.setState(newState);
  }

  handleSnackClose = () => {
    this.setState({ openSnack: false });
  }

  setColor = (name, value, index) => {
    this.updateState(name, value, index);
  }

  rebootPlayer = () => {
    reboot(this);
  }

  saveAndReboot = () => {
    save(this, () => { reboot(this) });
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

  isDirty = () => {
    return this.state.parametersDirty || this.state.playersDirty || this.state.screensaversDirty ||
      this.state.playlistsDirty || this.state.podcastsDirty || this.state.streamsDirty ? true : false;
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

  render() {
    const { classes } = this.props;
    const { tabIndex, currentMenuItem, parameters, labels } = this.state;

    if (!this.state.parameters || !this.state.labels || this.state.playerWasRebooted) {
      getParameters(this);
      return null;
    }

    if (tabIndex === 1 && this.state.players == null) {
      getPlayers(this);
      return null;
    } else if (tabIndex === 2 && this.state.screensavers == null) {
      getScreensavers(this);
      return null;
    } else if (tabIndex === 3 && this.state.playlists == null) {
      getRadioPlaylist(this);
      return null;
    } else if (tabIndex === 4 && this.state.podcasts == null) {
      getPodcasts(this);
      return null;
    } else if (tabIndex === 5 && this.state.streams == null) {
      getStreams(this);
      return null;
    }

    return (
      <Template
        labels={this.state.labels}
        hide={this.state.hideUi}
        reboot={this.state.reboot}
        shutdown={this.state.shutdown}
        logo={<Logo classes={classes} />}
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
        footerCopyright={<Copyright classes={classes} />}
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
            title={labels["confirm.reboot.title"]}
            message={labels["confirm.reboot.message"]}
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
            title={labels["confirm.save.reboot.title"]}
            message={labels["confirm.save.reboot.message"]}
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
            title={labels["confirm.shutdown.title"]}
            message={labels["confirm.shutdown.message"]}
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
            title={labels["confirm.save.shutdown.title"]}
            message={labels["confirm.save.shutdown.message"]}
            yes={labels.yes}
            no={labels.no}
            isDialogOpen={this.state.isSaveAndShutdownDialogOpen}
            yesAction={this.saveAndShutdown}
            noAction={this.shutdownPlayer}
            cancelAction={() => { this.setState({ isSaveAndShutdownDialogOpen: false }) }}
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
                updateWeather={this.updateWeather}
              />
            }
            {tabIndex === 3 &&
              <RadioPlaylistsTab
                labels={labels}
                language={this.state.language}
                classes={classes}
                playlists={this.state.playlists}
                genre={this.getRadioPlaylistMenu()[this.state.currentMenuItem]}
                updateState={this.updateState}
                title={this.getRadioPlaylistMenu()[this.state.currentMenuItem]}
              />
            }
            {tabIndex === 4 &&
              <PodcastsTab
                topic={currentMenuItem}
                labels={labels}
                classes={classes}
                podcasts={this.state.podcasts}
                updateState={this.updateState}
              />
            }
            {tabIndex === 5 &&
              <StreamsTab
                topic={currentMenuItem}
                labels={labels}
                classes={classes}
                streams={this.state.streams}
                updateState={this.updateState}
              />
            }
          </div>
        }
      />
    );
  }
}

export default withStyles(styles)(Peppy);
