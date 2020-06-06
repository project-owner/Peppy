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
import { FormControl, InputLabel, Select, MenuItem } from '@material-ui/core';
import Rgb from "../components/Rgb";
import Divider from '@material-ui/core/Divider';

export default class Icons extends React.Component {
  getColors = (colorGroup) => {
    if (!colorGroup) {
      return "rbg(0,0,0)";
    }

    let r = colorGroup[0];
    let g = colorGroup[1];
    let b = colorGroup[2];

    return "rgb(" + r + "," + g + "," + b + ")";
  }

  setColor = (name, index, value) => {
    this.props.params[name][index] = value;
    this.props.updateState(name, this.props.params[name])
  }

  getSvg = (id, iconType, colors) => {
    let c0 = colors[0];
    let g0 = c0;
    let c1 = colors[1];
    let g1 = c1;
    const gradientId = "gradient." + id;

    if(iconType === "monochrome") {
      c1 = c0;
    } else if(iconType === "gradient") {
      c0 = "url(#" + gradientId + ")";
      c1 = c0;
    }

    let rectId = id + ".rect";

    return <svg id={id} width="7rem" height="6rem" viewBox="5 -3 25 32">
      <linearGradient id={gradientId} gradientUnits="userSpaceOnUse" x1="17.1387" y1="28.3467" x2="17.1387" y2="4.882813e-004">
        <stop offset="0" style={{ stopColor: g1 }} />
        <stop offset="1" style={{ stopColor: g0 }} />
      </linearGradient>
      <path id="path" fill={c0} d="M17.14,6.742L5.463,18.419v7.914c0,1.112,0.901,2.014,2.013,2.014h4.698V16.603h9.933v11.744h4.697
                c1.111,0,2.014-0.901,2.014-2.014v-7.914L17.14,6.742z"/>
      <polygon id="polygon" fill={c1} points="17.14,0 0,17.14 3.986,17.14 17.14,3.988 30.292,17.14 34.278,17.14 " />
      <rect id={rectId} x="14.188" y="18.616" fill={c1} width="5.905" height="9.73" />
    </svg>
  }

  handleTypeChange = (event) => {
    this.props.updateState("type", event.target.value);
  }

  selectColor = (e) => {
    console.log(e);
  }

  render() {
    const { classes, params, labels } = this.props;

    let mainColor1 = this.getColors(params["color.1.main"]);
    let mainColor2 = this.getColors(params["color.2.main"]);
    let mainColors = [mainColor1, mainColor2]

    let selectedColor1 = this.getColors(params["color.1.on"]);
    let selectedColor2 = this.getColors(params["color.2.on"]);
    let selectedColors = [selectedColor1, selectedColor2];

    return (
      <FormControl>
        <FormControl style={{width: "10rem", marginBottom: "1rem"}}>
            <InputLabel shrink>{labels["type"]}</InputLabel>
            <Select
              value={params["type"]}
              onChange={this.handleTypeChange}
            >
                <MenuItem value={"monochrome"}>{labels["monochrome"]}</MenuItem>
                <MenuItem value={"bi-color"}>{labels["bi.color"]}</MenuItem>
                <MenuItem value={"gradient"}>{labels["gradient"]}</MenuItem>
            </Select>
          </FormControl>
        <FormControl>
          <h4 className={classes.colorsHeader}>{labels["base.icon"]}</h4>
          <Divider className={classes.colorsDivider} />
          <div className={classes.colorsPaletteRow}>
            <div>
              {this.getSvg("main.svg", params.type, mainColors)}
            </div>
            <div className={classes.slidersContainer}>
              <Rgb 
                labels={labels}
                classes={classes}
                colorId="color.1.main"
                red={params["color.1.main"][0]}
                green={params["color.1.main"][1]}
                blue={params["color.1.main"][2]}
                setColor={this.setColor}
              />
            </div>
            <div className={classes.slidersContainer}>
              <Rgb 
                labels={labels}
                classes={classes}
                colorId="color.2.main"
                red={params["color.2.main"] ? params["color.2.main"][0] : 0 }
                green={params["color.2.main"] ? params["color.2.main"][1] : 0 }
                blue={params["color.2.main"] ? params["color.2.main"][2] : 0 }
                setColor={this.setColor}
                disabled={params.type === "monochrome" ? true : false}
              />
            </div>
          </div>
        </FormControl>
        <FormControl>
          <h4 className={classes.colorsHeader}>{labels["selected.icon"]}</h4>
          <Divider className={classes.colorsDivider} />
          <div className={classes.colorsPaletteRow}>
            {this.getSvg("selected.svg", params.type, selectedColors)}
            <div className={classes.slidersContainer}>
              <Rgb 
                labels={labels}
                classes={classes}
                colorId="color.1.on"
                red={params["color.1.on"][0]}
                green={params["color.1.on"][1]}
                blue={params["color.1.on"][2]}
                setColor={this.setColor}
              />
            </div>
            <div className={classes.slidersContainer}>
              <Rgb 
                labels={labels}
                classes={classes}
                colorId="color.2.on"
                red={params["color.2.on"] ? params["color.2.on"][0] : 0}
                green={params["color.2.on"] ? params["color.2.on"][1] : 0}
                blue={params["color.2.on"] ? params["color.2.on"][2] : 0}
                setColor={this.setColor}
                disabled={params.type === "monochrome" ? true : false}             
              />
            </div>
          </div>
        </FormControl>
      </FormControl>
    );
  }
}
