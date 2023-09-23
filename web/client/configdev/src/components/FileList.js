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
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import ListItemIcon from '@mui/material/ListItemIcon';
import Checkbox from '@mui/material/Checkbox';
import Divider from '@mui/material/Divider';
import FolderOutlinedIcon from '@material-ui/icons/FolderOutlined';
import AudiotrackOutlinedIcon from '@material-ui/icons/AudiotrackOutlined';
import { COLOR_MEDIUM, COLOR_DARK_LIGHT } from "../Style";

export default class FileList extends React.Component {
  render() {
    const { title, files, selectAllFiles, handleFileClick, selectAllFilesState } = this.props;

    return (
      <div style={{ height: "30rem" }}>
        <Card>
          <CardHeader
            title={title}
            titleTypographyProps={{fontSize: 14, fontWeight: "bold"}}
            action={
              <Checkbox
                style={{"color": COLOR_DARK_LIGHT, "marginRight": "1.5rem"}}
                onClick={() => { selectAllFiles() }}
                checked={selectAllFilesState}
                disableRipple
              />
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
            {files && files.content && files.content.map((value, index) => {
              return (
                <ListItem
                  disablePadding
                  key={index}
                  role="listitem"
                  onClick={() => {handleFileClick(index)}}
                  secondaryAction={
                    <ListItemIcon>
                      { value.type === "file" && <Checkbox
                          checked={value.selected}
                          disableRipple
                          style={{"color": COLOR_DARK_LIGHT}}
                        />
                      }
                    </ListItemIcon>
                  }
                >
                  <ListItemButton role={undefined} dense>
                    <ListItemIcon>
                      { value.type === "folder" && <FolderOutlinedIcon style={{ color: COLOR_MEDIUM }}/> }
                      { value.type === "file" && <AudiotrackOutlinedIcon style={{ color: COLOR_MEDIUM }}/> }
                    </ListItemIcon>
                    <ListItemText id={index} primary={value.name} style={{wordWrap: "break-word"}}/>
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
