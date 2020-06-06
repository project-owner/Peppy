/* Copyright 2019-2020 Peppy Player peppy.player@gmail.com
 
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
import { Select, MenuItem, FormControl, InputLabel } from "@material-ui/core";
import Factory from "../Factory";

export const PlayersMenu = ["Audio", "VLC Linux", "VLC Windows", "MPD Linux", "MPD Windows",
  "MPV Linux", "MPV Windows"];

export const playersSections = [
  "audio", "vlc.linux", "vlc.windows", "mpd.linux", "mpd.windows", "mpv.linux", "mpv.windows"
];

function getStyle() {
  return {marginBottom: "1.4rem"};
}

class Audio extends React.Component {
  handleChange = (event) => {
    this.props.updateState("player.name", event.target.value)
  }
  render() {
    const {classes, labels, params, updateState} = this.props;
    const style = getStyle();
    style.marginTop = "2rem";

    if (!params) {
      return null;
    }

    return (
      <div className={classes.playersAudioContainer}>
        <FormControl>
          <InputLabel shrink>{labels["player.name"]}</InputLabel>
          <Select
            value={params["player.name"]}
            onChange={this.handleChange}
          >
            <MenuItem value={"vlc"}>VLC</MenuItem>
            <MenuItem value={"mpd"}>MPD</MenuItem>
            <MenuItem value={"mpv"}>MPV</MenuItem>
          </Select>
        </FormControl>
        <div className={classes.playersAudioTextContainer}>
          {Factory.createTextField("music.folder.linux", params, updateState, style, classes, labels)}
          {Factory.createTextField("music.folder.windows", params, updateState, getStyle(), classes, labels)}
        </div>
      </div>
    );
  }
}

class PlayerSettings extends React.Component {
  render() {
    const {classes, params, updateState, labels} = this.props;
    return (
      <div className={classes.playersAudioTextContainer}>
        {this.props.playerType !== "vlc" && this.props.playerType !== "mpv" && 
           Factory.createTextField("server.folder", params, updateState, getStyle(), classes, labels)
        }
        {Factory.createTextField("server.start.command", params, updateState, getStyle(), classes, labels)}
        {Factory.createTextField("client.name", params, updateState, getStyle(), classes, labels)}
        {this.props.playerType === "vlc" &&
          Factory.createTextField("stream.server.parameters", params, updateState, getStyle(), classes, labels)
        }
      </div>
    );
  }
}

export default class PlayersTab extends React.Component {
  render() {
    if (!this.props.players) {
      return null;
    }

    const { classes, topic, updateState, labels, players } = this.props;
    const p = players[playersSections[topic]];

    return (
      <main className={classes.content}>
        <div className={classes.toolbar} />
        {topic === 0 && <Audio labels={labels} classes={classes} params={players.audio} updateState={updateState}/>}
        {topic === 1 && <PlayerSettings labels={labels} classes={classes} playerType="vlc" params={p} updateState={updateState}/>}
        {topic === 2 && <PlayerSettings labels={labels} classes={classes} playerType="vlc" params={p} updateState={updateState}/>}
        {topic === 3 && <PlayerSettings labels={labels} classes={classes} playerType="mpd" params={p} updateState={updateState}/>}
        {topic === 4 && <PlayerSettings labels={labels} classes={classes} playerType="mpd" params={p} updateState={updateState}/>}
        {topic === 5 && <PlayerSettings labels={labels} classes={classes} playerType="mpv" params={p} updateState={updateState}/>}
        {topic === 6 && <PlayerSettings labels={labels} classes={classes} playerType="mpv" params={p} updateState={updateState}/>}
      </main>
    );
  }
}
