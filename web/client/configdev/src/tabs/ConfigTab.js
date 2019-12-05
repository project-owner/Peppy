import React from "react";
import Display from "../config/Display";
import Usage from "../config/Usage";
import Logging from "../config/Logging";
import FileBrowser from "../config/FileBrowser";
import WebServer from "../config/WebServer";
import StreamServer from "../config/StreamServer";
import Podcasts from "../config/Podcasts";
import HomeMenu from "../config/HomeMenu";
import HomeNavigator from "../config/HomeNavigator";
import ScreensaverMenu from "../config/ScreensaverMenu";
import LanguagesMenu from "../config/LanguagesMenu";
import VoiceAssistant from "../config/VoiceAssistant";
import Colors from "../config/Colors";
import Font from "../config/Font";
import Scripts from "../config/Scripts";
import Rotary from "../config/Rotary";

export const configSections = [
  "screen.info", "usage", "logging", "file.browser", "web.server", "stream.server", "podcasts", "home.menu",
  "home.navigator", "screensaver.menu", "languages.menu", "voice.assistant", "colors", "font", "scripts", "rotary.encoders"
];

export default class ConfigTab extends React.Component {
  render() {
    const { params, classes, topic, updateState, labels } = this.props;
    let p = params[configSections[topic]];

    return (
      <main className={classes.content}>
        <div className={classes.toolbar} />
        {topic === 0 && <Display params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 1 && <Usage params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 2 && <Logging params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 3 && <FileBrowser params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 4 && <WebServer params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 5 && <StreamServer params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 6 && <Podcasts params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 7 && <HomeMenu params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 8 && <HomeNavigator params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 9 && <ScreensaverMenu params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 10 && <LanguagesMenu params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 11 && <VoiceAssistant params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 12 && <Colors params={p} labels={labels} reset={this.props.reset} classes={classes}
          updateState={updateState} setPalette={this.props.setPalette} setColor={this.props.setColor} />}
        {topic === 13 && <Font params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 14 && <Scripts params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 15 && <Rotary params={p} labels={labels} classes={classes} updateState={updateState} />}
      </main>
    );
  }
}
