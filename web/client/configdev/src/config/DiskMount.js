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
import {FormControl} from '@material-ui/core';
import Factory from "../Factory";

export const diskMountSections = [
  "mount.at.startup", "mount.at.plug", "mount.read.only", "mount.point", "mount.options"
];

export default class DiskMount extends React.Component {
  render() {
    const { classes, params, updateState, labels } = this.props;
    const s = {width: "28rem", marginTop: "0.8rem", marginBottom: "0.6rem"};

    return (
      <FormControl>
        {Factory.createCheckbox(diskMountSections[0], params, updateState, labels)}
        {Factory.createCheckbox(diskMountSections[1], params, updateState, labels)}
        {Factory.createCheckbox(diskMountSections[2], params, updateState, labels)}
        {Factory.createTextField(diskMountSections[3], params, updateState, s, classes, labels)}
        {Factory.createTextField(diskMountSections[4], params, updateState, s, classes, labels)}
      </FormControl>
    );
  }
}
