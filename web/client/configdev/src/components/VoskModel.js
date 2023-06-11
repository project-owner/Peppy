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

import React from "react";
import { ListItem, ListItemText } from '@material-ui/core';
import RadioButtonCheckedIcon from '@material-ui/icons/RadioButtonChecked';
import RadioButtonUncheckedIcon from '@material-ui/icons/RadioButtonUnchecked';
import DeleteIcon from '@material-ui/icons/Delete';
import GetAppIcon from '@material-ui/icons/GetApp';
import { COLOR_MEDIUM } from "../Style";
import IconButton from '@material-ui/core/IconButton';
import Progress from "./Progress";

export default class VoskModel extends React.Component {
  render() {
    const { name, size, size_bytes, current, remote, url, downloadModel, setCurrentModel, handleDeleteVoskModelDialog, 
      downloadVoskModelProgress, voskModelDownloading, labels, unit } = this.props;

    return <>
      <ListItem button>
        {current === true && <RadioButtonCheckedIcon style={{ color: COLOR_MEDIUM, paddingRight: "1rem", verticalAlign: "top"}}/>}
        {current === false && <RadioButtonUncheckedIcon style={{ color: COLOR_MEDIUM, paddingRight: "1rem" }} 
          onClick={() => setCurrentModel(name, remote)}/>}
        <ListItemText primary={labels["model.name"] + ": " + name} secondary={labels["model.size"] + ": " + size + " " + labels[unit]} />
        {remote === true && downloadVoskModelProgress !== 0 && voskModelDownloading === name &&
          <Progress value={downloadVoskModelProgress} />
        }
        {remote === true && voskModelDownloading !== name &&
          <IconButton style={{ color: COLOR_MEDIUM }} onClick={() => downloadModel(name, url, size_bytes)} disabled={downloadVoskModelProgress !== 0}>
            <GetAppIcon />
          </IconButton>
        }
        {remote === false && 
          <IconButton style={{ color: COLOR_MEDIUM }} onClick={() => handleDeleteVoskModelDialog(name)}>
            <DeleteIcon />
          </IconButton>
        }
      </ListItem>
    </>
  }
}
