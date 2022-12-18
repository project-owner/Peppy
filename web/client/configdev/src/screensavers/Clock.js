/* Copyright 2019-2022 Peppy Player peppy.player@gmail.com
 
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
import { FormControl, InputLabel, Select, MenuItem } from '@material-ui/core';
import Factory from "../Factory";
import Rgb from "../components/Rgb";
import Divider from '@material-ui/core/Divider';
import ClockPalette from "./ClockPalette";

export default class Clock extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedClockDigit: "0"
    };
  }

  changeType = (event) => {
    this.props.updateState("type", event.target.value);
  }

  changeFont = (event) => {
    this.props.updateState("font.name", event.target.value)
  }

  changeImageFolder = (event) => {
    this.props.updateState("image.folder", event.target.value)
  }

  setColor = (name, index, value) => {
    this.props.values[name][index] = value;
    this.props.updateState(name, this.props.values[name])
  }

  setMultiColor = (name, index, value) => {
    this.props.values.colors[this.state.selectedClockDigit][index] = value;
    this.props.updateState(name, this.props.values.colors)
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

  selectDigit = (index) => {
    this.setState({ selectedClockDigit: index });
  };

  setRed = (_, value) => {
    const v = Math.trunc(value);
    this.props.setMultiColor(0, v);
  };

  setGreen = (_, value) => {
    const v = Math.trunc(value);
    this.props.setMultiColor(1, v);
  };

  setBlue = (_, value) => {
    const v = Math.trunc(value);
    this.props.setMultiColor(2, v);
  };

  render() {
    if (!this.props.values) {
      return null;
    }

    const style = {width: "12rem", marginBottom: "1rem"};
    const style1 = {width: "12rem", marginTop: "1rem"};
    const { classes, labels, values, updateState, fonts } = this.props;
    let color = this.getColor(values["color"]);

    return (
      <FormControl component="fieldset">
        {Factory.createNumberTextField("update.period", values, updateState, "sec", style, classes, labels)}
        {Factory.createCheckbox("military.time.format", values, updateState, labels)}
        {Factory.createCheckbox("animated", values, updateState, labels)}
        {Factory.createCheckbox("show.seconds", values, updateState, labels)}
        {Factory.createNumberTextField("clock.size", values, updateState, "percent", style1, classes, labels)}
        <div style={{ display: "flex", flexDirection: "row" }}>
          <FormControl style={{width: "12rem", marginTop: "1rem"}}>
            <InputLabel shrink>{labels["type"]}</InputLabel>
            <Select
              value={values["type"]}
              onChange={this.changeType}
            >
              <MenuItem value="font">{labels["font"]}</MenuItem>
              <MenuItem value="image">{labels["image"]}</MenuItem>
            </Select>
          </FormControl>
          <FormControl style={{width: "20rem", marginTop: "1rem", marginLeft: "2rem", display: values["type"] !== "font" ? "none" : "" }}>
            <InputLabel shrink>{labels["font.name"]}</InputLabel>
            <Select
              value={values["font.name"]}
              onChange={this.changeFont}
            >
              {fonts.map( (item,keyIndex) => <MenuItem  key={keyIndex} value={item}>{item}</MenuItem>)}
            </Select>
          </FormControl>
          <FormControl style={{width: "20rem", marginTop: "1rem", marginLeft: "2rem", display: values["type"] !== "image" ? "none" : "" }}>
            <InputLabel shrink>{labels["image.folder"]}</InputLabel>
            <Select
              value={values["image.folder"]}
              onChange={this.changeImageFolder}
            >
              {values["image.folders"].map( (item,keyIndex) => <MenuItem  key={keyIndex} value={item}>{item}</MenuItem>)}
            </Select>
          </FormControl>
          <div style={{ marginTop: "2rem", marginLeft: "2rem", display: values["type"] !== "font" ? "none" : ""  }}>
            {Factory.createCheckbox("multi.color", values, updateState, labels)}
          </div>
        </div>
        <FormControl style={{marginTop: "1rem", display: values["type"] === "image" || (values["type"] === "font" && values["multi.color"] === true) ? "none" : "" }}>
          <h4 className={classes.colorsHeader}>{labels["color"]}</h4>
          <Divider className={classes.colorsDivider} />
          <div className={classes.colorsPaletteRow}>
            <div className={classes.slidersContainer}>
              <Rgb
                colorId="color"
                labels={labels}
                classes={classes}
                red={values["color"] ? values["color"][0] : 0 }
                green={values["color"] ? values["color"][1] : 0 }
                blue={values["color"] ? values["color"][2] : 0 }
                setColor={this.setColor}
              />
            </div>
            <div style={{width: "3rem", height: "8rem", marginLeft: "1.4rem", borderRadius: "0.4rem", backgroundColor: color}}/>
          </div>
        </FormControl>
        <FormControl style={{marginTop: "1rem", display: values["type"] === "image" || (values["type"] === "font" && values["multi.color"] === false) ? "none" : "" }}>
          <h4 className={classes.colorsHeader}>{labels["multi.color"]}</h4>
          <Divider className={classes.colorsDivider} />
          <div className={classes.colorsPaletteRow}>
            <ClockPalette
              classes={classes}
              width={320}
              height={110}
              showSeconds={values["show.seconds"]}
              colorSchema={values["colors"]}
              selectDigit={this.selectDigit}
              selected={this.state.selectedClockDigit}
            />
            <Rgb
              colorId="colors"
              labels={labels}
              classes={classes}
              red={values["colors"] ? values["colors"][parseInt(this.state.selectedClockDigit)][0] : 0 }
              green={values["colors"] ? values["colors"][parseInt(this.state.selectedClockDigit)][1] : 0 }
              blue={values["colors"] ? values["colors"][parseInt(this.state.selectedClockDigit)][2] : 0 }
              setColor={this.setMultiColor}
            />
          </div>
        </FormControl>
      </FormControl>
    );
  }
}
