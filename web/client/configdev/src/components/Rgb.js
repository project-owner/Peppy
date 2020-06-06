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
import ColorSlider from "./ColorSlider";

export default class Rgb extends React.Component {
  setRed = (_, value) => {
    const v = Math.trunc(value);
    this.props.setColor(this.props.colorId, 0, v);
  };

  setGreen = (_, value) => {
    const v = Math.trunc(value);
    this.props.setColor(this.props.colorId, 1, v);
  };

  setBlue = (_, value) => {
    const v = Math.trunc(value);
    this.props.setColor(this.props.colorId, 2, v);
  };

  render() {
    const { classes, red, green, blue, labels, disabled } = this.props;
    const LABEL_WIDTH = Math.max(labels.red.length, labels.green.length, labels.blue.length) * 20 + "px";
    const SLIDER_WIDTH = "320px";
    const SLIDER_HEIGHT = "30px";

    return (
      <div className={classes.slidersContainer} style={{height: "8rem"}}>
        <ColorSlider
          classes={classes}
          width={SLIDER_WIDTH}
          height={SLIDER_HEIGHT}
          thumbColor={classes.red}
          value={red}
          label={labels.red}
          labelWidth={LABEL_WIDTH}
          onChange={this.setRed}
          sliderContainerClass={classes.sliderContainer}
          sliderTextClass={classes.sliderText}
          notchedOutline={classes.notchedOutline}
          disabled={disabled}
        />
        <ColorSlider
          classes={classes}
          width={SLIDER_WIDTH}
          height={SLIDER_HEIGHT}
          thumbColor={classes.green}
          value={green}
          label={labels.green}
          labelWidth={LABEL_WIDTH}
          onChange={this.setGreen}
          sliderContainerClass={classes.sliderContainer}
          sliderTextClass={classes.sliderText}
          notchedOutline={classes.notchedOutline}
          disabled={disabled}
        />
        <ColorSlider
          classes={classes}
          width={SLIDER_WIDTH}
          height={SLIDER_HEIGHT}
          thumbColor={classes.blue}
          label={labels.blue}
          value={blue}
          labelWidth={LABEL_WIDTH}
          onChange={this.setBlue}
          sliderContainerClass={classes.sliderContainer}
          sliderTextClass={classes.sliderText}
          notchedOutline={classes.notchedOutline}
          disabled={disabled}
        />
      </div>
    );
  }
}
