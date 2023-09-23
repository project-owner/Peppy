/* Copyright 2023 Peppy Player peppy.player@gmail.com
 
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
import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemButton from '@mui/material/ListItemButton';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import { COLOR_MEDIUM } from "../Style";
import DeleteOutlineIcon from '@material-ui/icons/DeleteOutline';

export default class Playlist extends React.Component {
  handleDelete = (index) => {
    this.props.deleteTrack(index);
  }
  
  render() {
    const { title, currentFilePlaylist, openDeletePlaylistDialog } = this.props;

    return (
      <div style={{ height: "30rem" }}>
        <Card>
          <CardHeader
            title={title}
            titleTypographyProps={{fontSize: 14, fontWeight: "bold"}}
            action={
              <IconButton onClick={() => { openDeletePlaylistDialog() }}>
                <DeleteOutlineIcon style={{ color: COLOR_MEDIUM, marginRight: "0.5rem" }}/>
              </IconButton>
            }
          />
          <Divider />
          <List
            sx={{
              width: '30rem',
              height: '30rem',
              overflow: 'auto',
            }}
            dense
            component="div"
            role="list"
          >
            {(currentFilePlaylist === null || currentFilePlaylist.length === 0)  && <div/>}
            {currentFilePlaylist && currentFilePlaylist.map((value, index) => {
              return (
                <ListItem 
                  disablePadding
                  id={index} 
                  key={index} 
                  role="listitem" 
                  secondaryAction={
                    <IconButton onClick={() => this.handleDelete(index)}>
                      <DeleteOutlineIcon style={{ color: COLOR_MEDIUM }}/>
                    </IconButton>
                  }
                >
                  <ListItemButton>
                    <ListItemText id={index} primary={value} style={{wordWrap: "break-word"}}/>
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
        </Card>
      </div>
    );
  }
}
