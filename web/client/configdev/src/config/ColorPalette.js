import React from 'react';
import Box from '@material-ui/core/Box';
import {COLOR_DARK, COLOR_DARK_LIGHT, COLOR_MEDIUM, COLOR_BRIGHT, COLOR_CONTRAST, 
  COLOR_LOGO, COLOR_MUTE, COLOR_WEB_BGR} from "./Colors";

export default class ColorPalette extends React.Component {
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

  selectTile = (evt) => {
    if (this.props.disableSelection && this.props.disableSelection === true) {
      return;
    }
    this.props.selectTile(evt.target.id)
  }

  getBorder = (name) => {
    let borderColor = "white";
    if (this.props.selected === name) {
      const c = this.props.colorSchema[name];
      if (c && c[0] > 200 && c[1] > 200 && c[2] > 200) {
        borderColor = "black";
      }
    }
    return this.props.selected === name ? "4px double " + borderColor : undefined;
  }

  render() {
    const { classes, name } = this.props;
    const colorSchema = { ...this.props.colorSchema };
    const color_web_bgr = colorSchema[COLOR_WEB_BGR];
    const color_dark = colorSchema[COLOR_DARK];
    const color_dark_light = colorSchema[COLOR_DARK_LIGHT];
    const color_medium = colorSchema[COLOR_MEDIUM];
    const color_bright = colorSchema[COLOR_BRIGHT];
    const color_contrast = colorSchema[COLOR_CONTRAST];
    const color_logo = colorSchema[COLOR_LOGO];
    const color_mute = colorSchema[COLOR_MUTE];
    const borderColor = "white";
    const TILE_WIDTH = this.props.width / 4 + "px";
    const TILE_HEIGHT = this.props.height / 2 + "px";
    const boxStyle={width: TILE_WIDTH, height: TILE_HEIGHT, boxSizing: "border-box"};
    
    return (
      <div className={classes.paletteContainer}>
        <div className={classes.paletteRow}>
          <Box
            id={COLOR_DARK}
            bgcolor={this.getColors(color_dark)}
            borderColor={borderColor}
            m={this.props.margin}
            border={this.getBorder(COLOR_DARK)}
            style={boxStyle}
            onClick={this.selectTile}
          />
          <Box
            id={COLOR_DARK_LIGHT}
            bgcolor={this.getColors(color_dark_light)}
            borderColor={borderColor}
            m={this.props.margin}
            border={this.getBorder(COLOR_DARK_LIGHT)}
            style={boxStyle}
            onClick={this.selectTile}
          />
          <Box
            id={COLOR_MEDIUM}
            bgcolor={this.getColors(color_medium)}
            borderColor={borderColor}
            m={this.props.margin}
            border={this.getBorder(COLOR_MEDIUM)}
            style={boxStyle}
            onClick={this.selectTile}
          />
           <Box
            id={COLOR_BRIGHT}
            bgcolor={this.getColors(color_bright)}
            borderColor={borderColor}
            m={this.props.margin}
            border={this.getBorder(COLOR_BRIGHT)}
            style={boxStyle}
            onClick={this.selectTile}
          />
        </div>
        <div className={classes.paletteRow}>
          <Box
            id={COLOR_CONTRAST}
            bgcolor={this.getColors(color_contrast)}
            borderColor={borderColor}
            m={this.props.margin}
            border={this.getBorder(COLOR_CONTRAST)}
            style={boxStyle}
            onClick={this.selectTile}
          />
          <Box
            id={COLOR_LOGO}
            bgcolor={this.getColors(color_logo)}
            borderColor={borderColor}
            m={this.props.margin}
            border={this.getBorder(COLOR_LOGO)}
            style={boxStyle}
            onClick={this.selectTile}
          />
          <Box
            id={COLOR_MUTE}
            bgcolor={this.getColors(color_mute)}
            borderColor={borderColor}
            m={this.props.margin}
            border={this.getBorder(COLOR_MUTE)}
            style={boxStyle}
            onClick={this.selectTile}
          />
          <Box
            id={COLOR_WEB_BGR}
            bgcolor={this.getColors(color_web_bgr)}
            borderColor={borderColor}
            m={this.props.margin}
            border={this.getBorder(COLOR_WEB_BGR)}
            style={boxStyle}
            onClick={this.selectTile}
          />
        </div>
        {name && <span>{name}</span>}
      </div>
    );
  }
}

