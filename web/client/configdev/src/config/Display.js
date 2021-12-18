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

import React from "react";
import { FormControl } from '@material-ui/core';
import Factory from "../Factory";

export default class Display extends React.Component {
  render() {
    const { classes, params, updateState, labels } = this.props;
    const style = {width: "13rem", marginBottom: "1rem"};

    return (
      <FormControl component="fieldset">
        {Factory.createNumberTextField("width", params, updateState, "pixels", style, classes, labels)}
        {Factory.createNumberTextField("height", params, updateState, "pixels", style, classes, labels)}
        {Factory.createNumberTextField("depth", params, updateState, "bits", style, classes, labels)}
        {Factory.createNumberTextField("frame.rate", params, updateState, "frames.sec", style, classes, labels)}
        {Factory.createCheckbox("hdmi", params, updateState, labels)}
        {Factory.createCheckbox("no.frame", params, updateState, labels)}
        {Factory.createCheckbox("flip.touch.xy", params, updateState, labels)}
        {Factory.createCheckbox("multi.touch", params, updateState, labels)}
      </FormControl>
    );
  }
}
