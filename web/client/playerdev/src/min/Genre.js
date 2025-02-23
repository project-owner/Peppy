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
import { TopDrawerIcon, TopDrawerText, HomeIcon, TopDrawerPanel, TopDrawerCenterPanel } from './mincss';
import { favoritesIconUrl } from "../Rest";

export default class Genre extends React.Component {
  render() {
    const { openGenre, toggleGenre, genre, genreIcons, genreIconsSelected, genres, changeGenre } = this.props;

    return (
      <Drawer open={openGenre} onClose={toggleGenre(false)} anchor='top'>
        <div style={TopDrawerPanel}>
          <div style={{width:'1px'}}/>
          <div style={TopDrawerCenterPanel}>
            {genres && genres.map((name, i) =>
              <IconButton aria-label={i} style={HomeIcon} onClick={changeGenre}>
                <img src={name === genre ? genreIconsSelected[i] : genreIcons[i]} key={name} alt={name} style={TopDrawerIcon} />
                <Typography noWrap style={TopDrawerText}>{name}</Typography>
              </IconButton>
            )}
          </div>
          <IconButton aria-label='favorites' style={HomeIcon} onClick={changeGenre}>
            <img src={favoritesIconUrl} key='favorites' alt='favorites' style={TopDrawerIcon} />
            <Typography noWrap style={TopDrawerText}>Favorites</Typography>
          </IconButton>
        </div>
      </Drawer>
    );
  }
}
