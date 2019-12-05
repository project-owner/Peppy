import React from "react";
import Factory from "../Factory";
import { DEFAULT_STATION_IMAGE } from "../Fetchers";

export default class RadioPlaylistsTab extends React.Component {
  render() {
    if (!this.props.playlists || !this.props.playlists[this.props.language]) {
      return null;
    }
    const {classes, language, playlists, genre, updateState, updateItemState, updateText, texts, labels, play, pause,
      playing, basePath} = this.props;
    const playlist = playlists[language][genre];
    const text = texts[language][genre];

    if (playlist === undefined) {
      return <div>{labels["loading"]}</div>;
    }
    
    return Factory.createPlaylist(genre, playlist, text, play, pause, playing, updateState, updateItemState, updateText,
      classes, labels, labels["add.station"], DEFAULT_STATION_IMAGE, basePath);
  }
}
