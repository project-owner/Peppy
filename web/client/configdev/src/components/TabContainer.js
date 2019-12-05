import React from "react";
import { Tabs, Tab } from "@material-ui/core";

export default class TabContainer extends React.Component {
  render() {
    const { classes, labels } = this.props;

    if (!labels) {
      return null;
    }

    const titles = [
      labels.configuration, labels.players, labels.screensavers, labels["radio.playlists"], labels.podcasts, 
      labels.streams
    ]
    return (
      <Tabs
        value={this.props.tabIndex}
        onChange={this.props.handleTabChange}
        TabIndicatorProps={{className: classes.tabSelection}}
      >
        {titles.map((text, index) => (<Tab key={index} label={text} />))}
      </Tabs>
    );
  }
}
