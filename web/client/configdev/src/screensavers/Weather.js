/* Copyright 2019-2021 Peppy Player peppy.player@gmail.com
 
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

export default class Weather extends React.Component {
  render() {
    if (!this.props.values) {
      return null;
    }

    const { classes, labels, values, updateState } = this.props;
    const params = values;
    const style1 = {marginBottom: "1rem"};
    const style2 = {width: "22rem", marginBottom: "1rem"};

    return (
      <FormControl component="fieldset">
        {Factory.createTextField("city", params, updateState, style1, classes, labels)}
        {Factory.createNumberTextField("latitude", params, updateState, null, style1, classes, labels)}
        {Factory.createNumberTextField("longitude", params, updateState, null, style1, classes, labels)}
        {Factory.createTextField("unit", params, updateState, style1, classes, labels)}
        {Factory.createNumberTextField("update.period", params, updateState, "sec", style1, classes, labels)}
        {Factory.createTextField("api.key", params, updateState, style2, classes, labels)}
        {Factory.createNumberTextField("weather.update.period", params, updateState, "sec", style2, classes, labels)}
      </FormControl>
    );
  }
}
