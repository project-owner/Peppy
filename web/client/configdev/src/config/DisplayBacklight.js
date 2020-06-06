/* Copyright 2020 Peppy Player peppy.player@gmail.com
 
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
import {FormControl} from '@material-ui/core';
import Factory from "../Factory";

export default class DisplayBacklight extends React.Component {
  render() {
    const { classes, params, updateState, labels } = this.props;
    const style = {width: "18rem", marginTop: "1rem", marginBottom: "1rem"};

    return (
      <FormControl>
        {Factory.createCheckbox("use.display.backlight", params, updateState, labels)}
        {Factory.createNumberTextField("screen.brightness", params, updateState, "percent", style, classes, labels)}
        {Factory.createNumberTextField("screensaver.brightness", params, updateState, "percent", style, classes, labels)}
        {Factory.createCheckbox("screensaver.display.power.off", params, updateState, labels)}
        {Factory.createCheckbox("sleep.now.display.power.off", params, updateState, labels)}        
      </FormControl>
    );
  }
}
