/* Copyright 2019-2020 Peppy Player peppy.player@gmail.com
 
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
import { FormControl, InputLabel, Select, MenuItem } from '@material-ui/core';

export default class Font extends React.Component {
  handleChange = (event) => {
    this.props.updateState("font.name", event.target.value)
  }

  render() {
    const { params, labels } = this.props;
    const items = ["FiraSans.ttf", "FiraSansCondensed-Regular.ttf", "FiraSansExtraCondensed-Regular.ttf"];

    return (
        <FormControl>
          <FormControl style={{width: "20rem", marginTop: "1.2rem"}}>
            <InputLabel shrink>{labels["font.name"]}</InputLabel>
            <Select
              value={params["font.name"]}
              onChange={this.handleChange}
            >
              <MenuItem value={items[0]}>{items[0]}</MenuItem>
              <MenuItem value={items[1]}>{items[1]}</MenuItem>
              <MenuItem value={items[2]}>{items[2]}</MenuItem>
            </Select>
          </FormControl>
        </FormControl>
    );
  }
}
