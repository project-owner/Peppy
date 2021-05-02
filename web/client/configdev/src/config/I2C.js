/* Copyright 2021 Peppy Player peppy.player@gmail.com
 
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
import {FormControl, FormGroup} from '@material-ui/core';
import Factory from "../Factory";

export default class I2C extends React.Component {
  render() {
    const { classes, params, updateState, labels } = this.props;
    const style = {width: "10rem", marginTop: "1.4rem"};
    const width = "12rem";

    return (
      <div style={{marginTop: "-2rem", display: "flex", flexDirection: "row"}}>
        <div style={{display: "flex", flexDirection: "column"}}>
          <FormControl component="fieldset">
              <FormGroup column="true">
                {Factory.createNumberTextField("i2c.input.address", params, updateState, "", {...style, marginTop: "2rem"}, classes,
                        labels, labels["i2c.input.address"], width)}
                {Factory.createNumberTextField("i2c.output.address", params, updateState, "", style, classes,
                        labels, labels["i2c.output.address"], width)}
                {Factory.createNumberTextField("i2c.gpio.interrupt", params, updateState, "", style, classes,
                        labels, labels["i2c.gpio.interrupt"], width)}
              </FormGroup>
            </FormControl>
        </div>
      </div>
    );
  }
}