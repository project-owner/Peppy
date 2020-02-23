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
import Slider from '@material-ui/lab/Slider';
import { TextField } from "@material-ui/core";

export default class ColorSlider extends React.Component {
  handleNumberChange = event => {
    if (isNaN(event.target.value)) {
      return;
    }

    if (Math.trunc(event.target.value) > 255 || Math.trunc(event.target.value) < 0) {
      return;
    }
    this.props.onChange("", event.target.value)
  };

  render() {
    const { label, value, thumbColor, sliderContainerClass, sliderTextClass, notchedOutline } = this.props;

    return (
      <div className={sliderContainerClass} style={{ width: this.props.width }}>
        <div style={{ width: this.props.labelWidth }}>{label}</div>
        <Slider
          classes={{ thumb: thumbColor }}
          value={value}
          aria-labelledby="label"
          style={{color: thumbColor}}
          onChange={this.props.onChange}
          min={0}
          max={255}
        />
        <TextField
          id="outlined-dense"
          value={value}
          onChange={this.handleNumberChange}
          variant="outlined"
          className={sliderTextClass}
          InputProps={{
            style: {
              height: "2.4rem"
            },
            maxLength: 3,
            min: 0,
            max: 255,
            classes: {
              notchedOutline: notchedOutline
            }
          }}
        />
      </div>
    );
  }
}
