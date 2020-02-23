/* Copyright 2019 Peppy Player peppy.player@gmail.com
 
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
import { TextField,
  InputAdornment
} from '@material-ui/core';
import {COLOR_DARK} from "../Style";

export default class NumberTextField extends React.Component {
  render() {
    return (
      <div>
        <TextField
          id={this.props.id}
          label={this.props.label}
          variant="outlined"
          style={this.props.style}
          value={this.props.value}
          onChange={event => {this.props.onChange(event.target.id, event.target.value)}}
          InputLabelProps={{
            style: { color: COLOR_DARK }
          }}
          InputProps={{
            style: {
              height: this.props.fieldHeight
            },
            endAdornment: this.props.unit && <InputAdornment position="end">{this.props.unit}</InputAdornment>,
            classes: {
              notchedOutline: this.props.classes.notchedOutline
            }
          }}
        />
      </div>
    );
  }
}
