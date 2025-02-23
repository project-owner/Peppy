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
import IconButton from '@mui/material/IconButton';
import PauseRounded from '@material-ui/icons/PauseRounded';
import PlayArrowRounded from '@material-ui/icons/PlayArrowRounded';
import FastForwardRounded from '@material-ui/icons/FastForwardRounded';
import FastRewindRounded from '@material-ui/icons/FastRewindRounded';
import { ButtonPanel, ButtonCenterPanel, ButtonStyle, PlayButtonStyle, 
  NextPreviousButtonStyle, ModeIcon } from './mincss';
import { configIconUrl } from "../Rest";

export default class Buttons extends React.Component {
  render() {
    const { pause, toggleHome, toggleVolume, modeIconUrl, next, previous, playPause } = this.props;

    return (
      <div style={ButtonPanel}>
        <IconButton aria-label="volume" onClick={toggleHome(true)}>
          <img src={modeIconUrl} key="mode" alt="mode" style={ModeIcon} />
        </IconButton>

        <div style={ButtonCenterPanel}>
          <IconButton aria-label="previous song" style={ButtonStyle} onClick={previous}>
            <FastRewindRounded style={NextPreviousButtonStyle} />
          </IconButton>
          <IconButton
            aria-label={pause ? 'pause' : 'play'}
            onClick={playPause}
            style={ButtonStyle}
          >
            {pause ?
              (<PlayArrowRounded style={PlayButtonStyle} />) :
              (<PauseRounded style={PlayButtonStyle} />)
            }
          </IconButton>
          <IconButton aria-label="next song" style={ButtonStyle} onClick={next}>
            <FastForwardRounded style={NextPreviousButtonStyle}/>
          </IconButton>
        </div>

        <IconButton aria-label="volume" onClick={toggleVolume(true)}>
          <img src={configIconUrl} key="config" alt="config" style={ModeIcon} />
        </IconButton>
      </div>
    );
  }
}
