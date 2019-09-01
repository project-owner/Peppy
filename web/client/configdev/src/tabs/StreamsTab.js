import React from "react";
import Factory from "../Factory";

export default class StreamsTab extends React.Component {
  render() {
    if (!this.props.streams) {
      return null;
    }

    const { classes, labels, updateState, streams } = this.props;
    const style = {width: "40rem"};
    const linksObj = {"streams": streams}

    return (
      <main className={classes.content}>
        <div className={classes.toolbar} />
        {Factory.createTextArea("streams", linksObj, updateState, style, classes, labels)}
      </main>
    );
  }
}
