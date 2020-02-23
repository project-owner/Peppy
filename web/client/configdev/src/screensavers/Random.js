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

import React from "react";
import { FormControl } from '@material-ui/core';
import Factory from "../Factory";
import { screensaversSections } from "../tabs/ScreensaversTab"

export default class Random extends React.Component {
  render() {
    if (!this.props.values) {
      return null;
    }

    const style = { width: "10rem", marginBottom: "1rem" };
    const { classes, labels, values, updateState } = this.props;
    const savers = values.savers;

    return (
      <FormControl component="fieldset">
        {Factory.createNumberTextField("update.period", values, updateState, "sec", style, classes, labels)}
        {screensaversSections.map((section, index) => (
          section !== "random" && Factory.createCheckbox(section, {[section]: savers.includes(section)}, updateState, labels, index)
        ))}
      </FormControl>
    );
  }
}
