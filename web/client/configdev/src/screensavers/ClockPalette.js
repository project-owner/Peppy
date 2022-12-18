/* Copyright 2022 Peppy Player peppy.player@gmail.com
 
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
import Typography from '@material-ui/core/Typography';

export default class ClockPalette extends React.Component {
  getColors = (colorGroup) => {
    if (!colorGroup) {
      return "#000";
    }
    let r = colorGroup[0];
    let g = colorGroup[1];
    let b = colorGroup[2];
    const c = "rgb(" + r + "," + g + "," + b + ")";
    return c;
  }

  selectDigit = (evt) => {
    this.props.selectDigit(evt.target.id)
  }

  getBorder = (name) => {
    let borderColor = "white";
    return this.props.selected === name ? "4px double " + borderColor : undefined;
  }

  render() {
    const { classes } = this.props;
    const colorSchema = this.props.colorSchema;
    const TILE_WIDTH = this.props.width / 8 + "px";
    
    return (
      <div className={classes.paletteContainer} style={{marginTop: "2.4rem"}}>
        <div className={classes.paletteRow}>
          <Typography 
            id="0" 
            variant="h3" 
            align="center" 
            style={{
                width: TILE_WIDTH, 
                border: this.getBorder("0"), 
                backgroundColor: "black", 
                color:this.getColors(colorSchema[0]),
                marginTop: this.props.selected === "0" ? "-4px" : ""
            }}
            onClick={this.selectDigit}>
            1
          </Typography>
          <Typography 
            id="1" 
            variant="h3" 
            align="center" 
            style={{
                width: TILE_WIDTH, 
                border: this.getBorder("1"), 
                backgroundColor: "black", 
                color:this.getColors(colorSchema[1]),
                marginTop: this.props.selected === "1" ? "-4px" : ""
            }}
            onClick={this.selectDigit}>
            2
          </Typography>
          <Typography
            id="2" 
            variant="h3" 
            align="center" 
            style={{
                width: TILE_WIDTH, 
                border: this.getBorder("2"), 
                backgroundColor: "black", 
                color:this.getColors(colorSchema[2]),
                marginTop: this.props.selected === "2" ? "-4px" : ""
            }}
            onClick={this.selectDigit}>
              :
          </Typography>
          <Typography 
            id="3" 
            variant="h3" 
            align="center" 
            style={{
                width: TILE_WIDTH, 
                border: this.getBorder("3"), 
                backgroundColor: "black", 
                color:this.getColors(colorSchema[3]),
                marginTop: this.props.selected === "3" ? "-4px" : ""
            }}
            onClick={this.selectDigit}>
            3
          </Typography>
          <Typography 
            id="4" 
            variant="h3" 
            align="center" 
            style={{
                width: TILE_WIDTH, 
                border: this.getBorder("4"), 
                backgroundColor: "black", 
                color:this.getColors(colorSchema[4]),
                marginTop: this.props.selected === "4" ? "-4px" : ""
            }}
            onClick={this.selectDigit}>
            4
          </Typography>
          <Typography 
            id="5" 
            variant="h3" 
            align="center" 
            style={{
                width: TILE_WIDTH, 
                border: this.getBorder("5"), 
                backgroundColor: "black", 
                color:this.getColors(colorSchema[5]), 
                display: !this.props.showSeconds ? "none" : "",
                marginTop: this.props.selected === "5" ? "-4px" : ""
            }}
            onClick={this.selectDigit}>
            :
          </Typography>
          <Typography 
            id="6" 
            variant="h3" 
            align="center" 
            style={{
                width: TILE_WIDTH, 
                border: this.getBorder("6"), 
                backgroundColor: "black", 
                color:this.getColors(colorSchema[6]),
                display: !this.props.showSeconds ? "none" : "",
                marginTop: this.props.selected === "6" ? "-4px" : ""
            }}
            onClick={this.selectDigit}>
            5
          </Typography>
          <Typography 
            id="7" 
            variant="h3" 
            align="center" 
            style={{
                width: TILE_WIDTH, 
                border: this.getBorder("7"), 
                backgroundColor: "black", 
                color:this.getColors(colorSchema[7]),
                display: !this.props.showSeconds ? "none" : "",
                marginTop: this.props.selected === "7" ? "-4px" : ""
            }}
            onClick={this.selectDigit}>
            6
          </Typography>
        </div>
      </div>
    );
  }
}

