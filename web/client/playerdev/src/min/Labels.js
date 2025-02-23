/* Copyright 2024 Peppy Player peppy.player@gmail.com
 
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
import Typography from '@mui/material/Typography';
import { TextContainer, Track, Album, Genre, Artist } from './mincss';

export default class Labels extends React.Component {
  render() {
    const { mode, label1, label2, label3, toggleTrack, toggleGenre } = this.props;

    return (
      <div>
        <div style={TextContainer}>
          <Typography noWrap style={Track} onClick={toggleTrack(true)}>{label1}</Typography>
        </div>
        <div style={TextContainer}>
            <Typography noWrap style={ mode === "radio" ? Genre : Album } onClick={toggleGenre && toggleGenre(true)}>{label2}</Typography>
        </div>
        <div style={TextContainer}>
          <Typography noWrap style={Artist}>{label3}</Typography>
        </div>
      </div>
    );
  }
}
