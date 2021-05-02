/* Copyright 2019-2021 Peppy Player peppy.player@gmail.com
 
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
import Factory from "../Factory";
import { DEFAULT_STREAM_IMAGE } from "../Fetchers";

export default class StreamsTab extends React.Component {
  render() {
    if (!this.props.streams) {
      return null;
    }

    const { id, classes, labels, updateState, updateItemState, updateText, streams, text, play, pause, playing, basePath } = this.props;

    return Factory.createPlaylist(id, streams, text, play, pause, null, playing, updateState, updateItemState, updateText,
      classes, labels, labels["add.stream"], DEFAULT_STREAM_IMAGE, basePath);
  }
}
