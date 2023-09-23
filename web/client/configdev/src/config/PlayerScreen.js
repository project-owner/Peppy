/* Copyright 2020-2023 Peppy Player peppy.player@gmail.com
 
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
import Factory from "../Factory";

export default class PlayerScreen extends React.Component {
  handleChange = (event) => {
    this.props.updateState("image.location", event.target.value)
  }

  render() {
    const { classes, params, updateState, labels } = this.props;
    const style = {width: "16rem", marginTop: "1rem", marginBottom: "1rem"};

    return (
      <FormControl>
        {Factory.createNumberTextField("top.height", params, updateState, "percent", style, classes, labels)}
        {Factory.createNumberTextField("bottom.height", params, updateState, "percent", style, classes, labels)}
        {Factory.createNumberTextField("button.height", params, updateState, "percent", style, classes, labels)}
        {Factory.createNumberTextField("popup.width", params, updateState, "percent", style, classes, labels)}
        <FormControl style={{width: "12rem", marginTop: "0.4rem", marginBottom: "1.4rem"}}>
          <InputLabel shrink>{labels["image.location"]}</InputLabel>
          <Select
            value={params["image.location"]}
            onChange={this.handleChange}
          >
            <MenuItem value={"center"}>{labels["center"]}</MenuItem>
            <MenuItem value={"left"}>{labels["left"]}</MenuItem>
            <MenuItem value={"right"}>{labels["right"]}</MenuItem>
          </Select>
        </FormControl>
        {Factory.createCheckbox("enable.order.button", params, updateState, labels)}
        {Factory.createCheckbox("enable.info.button", params, updateState, labels)}
        {Factory.createCheckbox("show.time.slider", params, updateState, labels)}
      </FormControl>
    );
  }
}
