/* Copyright 2020-2022 Peppy Player peppy.player@gmail.com
 
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
import Rgb from "../components/Rgb";
import Divider from '@material-ui/core/Divider';

export default class Background extends React.Component {
  handleChange = (event) => {
    this.props.updateState("bgr.type", event.target.value);
  }

  setColor = (name, index, value) => {
    this.props.params[name][index] = value;
    this.props.updateState(name, this.props.params[name])
  }

  getColor = (colorArray) => {
    if (!colorArray) {
      return "#000";
    }

    let r = colorArray[0];
    let g = colorArray[1];
    let b = colorArray[2];

    return "rgb(" + r + "," + g + "," + b + ")";
  }

  render() {
    const { params, labels, classes, updateState } = this.props;
    const style1 = { width: "30rem", marginTop: "1.4rem" };
    const style2 = { width: "22rem", marginTop: "1.4rem" };
    let screenBgrColor = this.getColor(params["screen.bgr.color"]);

    return (
        <FormControl>
          <FormControl style={{width: "20rem"}}>
            <InputLabel shrink>{labels["type"]}</InputLabel>
            <Select
              value={params["bgr.type"]}
              onChange={this.handleChange}
            >
              <MenuItem value="color">{labels["color"]}</MenuItem>
              <MenuItem value="image">{labels["image"]}</MenuItem>
              <MenuItem value="album.art">{labels["album.art"]}</MenuItem>
            </Select>
          </FormControl>
          {Factory.createTextField("screen.bgr.names", params, updateState, style1, classes, labels)}
          {Factory.createTextField("web.bgr.names", params, updateState, style1, classes, labels)}
          {Factory.createNumberTextField("header.bgr.opacity", params, updateState, "", style2, classes, labels)}
          {Factory.createNumberTextField("menu.bgr.opacity", params, updateState, "", style2, classes, labels)}
          {Factory.createNumberTextField("footer.bgr.opacity", params, updateState, "", style2, classes, labels)}
          {Factory.createNumberTextField("web.screen.bgr.opacity", params, updateState, "", style2, classes, labels)}
          <FormControl>
            <h4 className={classes.colorsHeader}>{labels["screen.bgr.color"]}</h4>
            <Divider className={classes.colorsDivider} />
            <div className={classes.colorsPaletteRow}>
              <div className={classes.slidersContainer}>
                <Rgb
                  colorId="screen.bgr.color"
                  labels={labels}
                  classes={classes}
                  red={params["screen.bgr.color"] ? params["screen.bgr.color"][0] : 0 }
                  green={params["screen.bgr.color"] ? params["screen.bgr.color"][1] : 0 }
                  blue={params["screen.bgr.color"] ? params["screen.bgr.color"][2] : 0 }
                  setColor={this.setColor}
                />                
              </div>
              <div style={{width: "3rem", height: "8rem", marginLeft: "1.4rem", borderRadius: "0.4rem", backgroundColor: screenBgrColor}}/>
            </div>
          </FormControl>
        </FormControl>
    );
  }
}
