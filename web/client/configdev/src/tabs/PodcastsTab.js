import React from "react";
import Factory from "../Factory";

export default class PodcastsTab extends React.Component {
  render() {
    if (!this.props.podcasts) {
      return null;
    }

    const { classes, labels, updateState, podcasts } = this.props;
    const style = {width: "40rem"};
    const linksObj = {"podcasts": podcasts}

    return (
      <main className={classes.content}>
        <div className={classes.toolbar} />
        {Factory.createTextArea("podcasts", linksObj, updateState, style, classes, labels)}
      </main>
    );
  }
}
