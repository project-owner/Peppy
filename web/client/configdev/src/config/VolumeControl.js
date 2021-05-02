/* Copyright 2020-2021 Peppy Player peppy.player@gmail.com
 
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

export default class VolumeControl extends React.Component {
  handleTypeChange = (event) => {
    this.props.updateState("type", event.target.value)
  }

  handleScaleChange = (event) => {
    this.props.updateState("amixer.scale", event.target.value)
  }

  render() {
    const { classes, params, updateState, labels } = this.props;
    const style = {width: "18rem", marginTop: "1.4rem"};

    return (
        <FormControl>
          <FormControl style={{width: "10rem"}}>
            <InputLabel shrink>{labels["type"]}</InputLabel>
            <Select
              value={params["type"]}
              onChange={this.handleTypeChange}
            >
                <MenuItem value={"amixer"}>{"amixer"}</MenuItem>
                <MenuItem value={"player"}>{labels["player"]}</MenuItem>
                <MenuItem value={"hardware"}>{labels["hardware"]}</MenuItem>
            </Select>
          </FormControl>
          <FormControl style={{width: "10rem", marginTop: "1.2rem"}}>
            <InputLabel shrink>{labels["scale"]}</InputLabel>
            <Select
              value={params["amixer.scale"]}
              onChange={this.handleScaleChange}
            >
                <MenuItem value={"linear"}>{labels["linear"]}</MenuItem>
                <MenuItem value={"logarithmic"}>{labels["logarithmic"]}</MenuItem>
            </Select>
          </FormControl>
          <FormControl>
            {Factory.createTextField("amixer.control", params, updateState, style, classes, labels)}
          </FormControl> 
          <FormControl>
            {Factory.createNumberTextField("initial.volume.level", params, updateState, "percent", style, classes, labels)}  
          </FormControl>   
        </FormControl>
    );
  }
}
