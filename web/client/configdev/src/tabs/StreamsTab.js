import React from "react";
import Factory from "../Factory";
import { DEFAULT_STREAM_IMAGE } from "../Fetchers";

export default class StreamsTab extends React.Component {
  render() {
    if (!this.props.streams) {
      return null;
    }

    const { id, classes, labels, updateState, updateItemState, updateText, streams, text, play, pause, playing, basePath } = this.props;

    return Factory.createPlaylist(id, streams, text, play, pause, playing, updateState, updateItemState, updateText,
      classes, labels, labels["add.stream"], DEFAULT_STREAM_IMAGE, basePath);
  }
}
