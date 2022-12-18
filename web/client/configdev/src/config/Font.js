/* Copyright 2019-2022 Peppy Player peppy.player@gmail.com
 
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
import { FormControl, InputLabel, Select, MenuItem, Button } from '@material-ui/core';
import PublishIcon from '@material-ui/icons/Publish';

export default class Font extends React.Component {
  handleChange = (event) => {
    this.props.updateState("font.name", event.target.value)
  }

  uploadFontFile = (event, uploadFunction) => {
    if (!event.target.files || !event.target.files[0]) {
      return;
    }

    let file = event.target.files[0];
    let reader = new FileReader();

    reader.onloadend = () => {
      if (file) {
        uploadFunction(file);
      }
    }
    reader.readAsArrayBuffer(file);
  }

  render() {
    const { params, labels, fonts, classes } = this.props;
    const items = fonts;

    return (
        <FormControl>
          <FormControl style={{width: "20rem", marginTop: "1.2rem"}}>
            <InputLabel shrink>{labels["font.name"]}</InputLabel>
            <Select
              value={params["font.name"]}
              onChange={this.handleChange}
            >
              {items.map( (item,keyIndex) => <MenuItem  key={keyIndex} value={item}>{item}</MenuItem>)}
            </Select>
          </FormControl>
          <input
            id="upload"
            type="file"
            accept=".ttf, .otf"
            style={{ display: "none" }}
            onChange={(e) => { this.uploadFontFile(e, this.props.uploadFont) }}
          />
          <Button
            variant="contained"
            className={classes.addButton}
            style={{ width: "10rem", marginTop: "2rem" }}
            onClick={() => { document.getElementById("upload").click() }}
          >
            {labels.upload}
            <PublishIcon style={{ marginLeft: "1rem" }} />
          </Button>
        </FormControl>
    );
  }
}
