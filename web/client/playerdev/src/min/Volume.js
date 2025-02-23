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
import Drawer from '@mui/material/Drawer';
import Slider from '@mui/material/Slider';
import IconButton from '@mui/material/IconButton';
import { VolumeSliderStyle, VolumePanel, Mute } from './mincss';
import { setVolume, getIconUrl, getIconSelectedUrl } from "../Rest";

export default class Volume extends React.Component {

  render() {
    const { openVolume, toggleVolume, volume, setPosition, mute, setMute } = this.props;

    return (
      <Drawer open={openVolume} onClose={toggleVolume(false)}
        anchor='bottom'
        PaperProps={{
          style: {
            height: '86px',
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'center'
          }
        }}
      >
        <div style={VolumePanel}>
          <Slider
            disabled={mute}
            orientation="horizontal"
            aria-label="Volume"
            valueLabelDisplay="auto"
            value={volume}
            defaultValue={0}
            size='small'
            sx={VolumeSliderStyle}
            onChange={setPosition}
            onChangeCommitted={setVolume}
          />
          <IconButton aria-label="mute" style={{ marginLeft: '0.5rem' }} onClick={setMute}>
            <img src={mute ? getIconSelectedUrl('volume-mute') : getIconUrl('volume-mute')} key="mute" alt="mute" style={Mute} />
          </IconButton>
        </div>
      </Drawer>
    );
  }
}
