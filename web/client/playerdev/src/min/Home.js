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
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import { Mode, ModeText, HomeIcon, HomeButtonsPanel, HomeButtonsCenterPanel } from './mincss';
import { shutdownIconUrl, rebootIconUrl } from "../Rest";

export default class Home extends React.Component {
  render() {
    const { openHome, toggleHome, mode, modeIcons, modeIconsSelected, modeNames, labels, 
      shutdown, reboot, changeMode } = this.props;

    return (
      <Drawer open={openHome} onClose={toggleHome(false)} anchor='top'>
        <div style={HomeButtonsPanel}>
          <IconButton aria-label='shutdown' style={HomeIcon} onClick={shutdown}>
            <img src={shutdownIconUrl} key='shutdown' alt='shutdown' style={Mode} />
            <Typography noWrap style={ModeText}>{labels && labels['shutdown']}</Typography>
          </IconButton>
          <div style={HomeButtonsCenterPanel}>
            {modeNames && modeNames.map((name, i) =>
              (name === "radio" || name === "audio-files") &&
              <IconButton aria-label={i} style={HomeIcon} onClick={changeMode}>
                <img src={name === mode ? modeIconsSelected[i] : modeIcons[i]} key={name} alt={name} style={Mode} />
                <Typography noWrap style={ModeText}>{labels[modeNames[i]]}</Typography>
              </IconButton>
            )}
          </div>
          <IconButton aria-label='reboot' style={HomeIcon} onClick={reboot}>
            <img src={rebootIconUrl} key='reboot' alt='reboot' style={Mode} />
            <Typography noWrap style={ModeText}>{labels && labels['reboot']}</Typography>
          </IconButton>
        </div>
      </Drawer>
    );
  }
}
