import React from "react";
import Clock from "../screensavers/Clock";
import Logo from "../screensavers/Logo";
import Lyrics from "../screensavers/Lyrics";
import Weather from "../screensavers/Weather";
import Random from "../screensavers/Random";
import Slideshow from "../screensavers/Slideshow";

export const screensaversSections = [
  "clock", "logo", "lyrics", "peppyweather", "random", "slideshow", "peppymeter", "spectrum"
];

export default class ScreensaversTab extends React.Component {
  render() {
    if (!this.props.screensavers) {
      return null;
    }

    const { classes, labels, topic, updateState, updateWeather, language, screensavers } = this.props;
    const p = screensavers[screensaversSections[topic]];

    return (
      <main className={classes.content}>
        {topic === 0 && <Clock labels={labels} classes={classes} values={p} updateState={updateState}/>}
        {topic === 1 && <Logo labels={labels} classes={classes} values={p} updateState={updateState}/>}
        {topic === 2 && <Lyrics labels={labels} classes={classes} values={p} updateState={updateState}/>}
        {topic === 3 && <Weather lang={language} labels={labels} classes={classes} values={p} updateState={updateWeather}/>}
        {topic === 4 && <Random labels={labels} classes={classes} values={p} updateState={updateState}/>}
        {topic === 5 && <Slideshow labels={labels} classes={classes} values={p} updateState={updateState}/>}
      </main>
    );
  }
}
