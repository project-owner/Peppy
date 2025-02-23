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

import React from 'react';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemButton from '@mui/material/ListItemButton';
import { Drawer } from '@mui/material';
import ListItemIcon from '@mui/material/ListItemIcon';
import { Avatar } from '@mui/material';
import { getImageFileUrl } from '../Rest';

export default class RadioPlaylist extends React.Component {
  render() {
    const { openBrowser, toggleBrowser, playlist, callback, currentStation } = this.props;

    return (
      <Drawer open={openBrowser} onClose={toggleBrowser(false)}
        anchor='left'
        PaperProps={{
          style: {
            width: '300px',
            backgroundColor: 'rgb(255,255,255)'
          }
        }}
      >
        <div style={{ height: "100%" }}>
          <List
            sx={{
              width: '34rem',
              overflow: 'auto',
            }}
            dense
            component="div"
            role="list"
          >
            {(playlist === null || playlist.length === 0) && <div />}
            {playlist && playlist.map((value, index) => {
              return (
                <ListItem
                  disablePadding
                  key={index}
                  role="listitem"
                  onClick={() => { callback(index, value.genre, value.url) }}
                >
                  <ListItemButton
                    selected={currentStation === value.l_name}
                    autoFocus={currentStation === value.l_name}
                    disablePadding
                    dense
                    id={index}
                    key={index}
                    alt={index}
                    role="listitem"
                  >
                    <ListItemIcon >
                      <Avatar src={getImageFileUrl(value.image_path)} style={{ borderRadius: 0 }} />
                    </ListItemIcon >
                    <ListItemText id={index} primary={value.l_name} style={{ wordWrap: "break-word" }} />
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
        </div>
      </Drawer>
    );
  }
}
