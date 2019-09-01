import React from "react";
import Factory from "../Factory";

export default class RadioPlaylistsTab extends React.Component {
  render() {
    if (!this.props.playlists || !this.props.playlists[this.props.language]) {
      return null;
    }

    const style = { width: "40rem" };
    const {classes, language, playlists, genre, updateState, labels, title} = this.props;
    labels[title] = title;
    const playlist = playlists[language][genre];
    const params = {[title]: playlist}
    
    return (
      <main className={classes.content}>
        {Factory.createTextArea(title, params, updateState, style, classes, labels)}
      </main>
    );
  }
}
