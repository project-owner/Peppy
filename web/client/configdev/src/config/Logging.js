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
import {FormControl} from '@material-ui/core';
import Factory from "../Factory";

export const logSections = [
  "file.logging", "log.filename", "console.logging", "enable.stdout", "show.mouse.events"
];

export default class Logging extends React.Component {
  render() {
    const { classes, params, updateState, labels } = this.props;
    const s = {width: "16rem", marginTop: "0.8rem", marginBottom: "0.6rem"};

    return (
      <FormControl>
        {Factory.createCheckbox(logSections[0], params, updateState, labels)}
        {Factory.createTextField(logSections[1], params, updateState, s, classes, labels)}
        {Factory.createCheckbox(logSections[2], params, updateState, labels)}
        {Factory.createCheckbox(logSections[3], params, updateState, labels)}
        {Factory.createCheckbox(logSections[4], params, updateState, labels)}        
      </FormControl>
    );
  }
}
