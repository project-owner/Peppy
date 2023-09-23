/* Copyright 2022-2023 Peppy Player peppy.player@gmail.com
 
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
import { Tabs, Tab } from "@material-ui/core";

export default class TabContainerPlaylist extends React.Component {
  render() {
    const { classes, labels, tabIndex, handleTabChange } = this.props;

    if (!labels) {
      return null;
    }

    const titles = [labels["radio.playlists"], labels["file.playlists"], labels.podcasts, labels.streams, labels["ya-streams"], labels.jukebox];
    return (
      <Tabs
        value={tabIndex}
        onChange={handleTabChange}
        TabIndicatorProps={{className: classes.playlistTabSelection}}
        variant="scrollable"
        scrollButtons="auto"
      >
        {titles.map((text, index) => (<Tab key={index} label={text} />))}
      </Tabs>
    );
  }
}
