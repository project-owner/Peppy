/* Copyright 2023 Peppy Player peppy.player@gmail.com
 
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
import {FormControl, FormGroup, FormControlLabel, Radio, RadioGroup} from '@material-ui/core';
import Factory from "../Factory";
import Divider from '@material-ui/core/Divider';

export default class ScreensaverScreen extends React.Component {
  handleTypeChange = (event) => {
    this.props.updateState("screensaver.delay", event.target.value);
  }

  render() {
    const { menuParams, delayParams, updateState, labels, classes } = this.props;
    const menuItems = ["clock", "logo", "slideshow", "peppymeter", "peppyweather", "spectrum", "lyrics", "pexels",
      "monitor", "horoscope", "stock", "random"];
    const ctl = <Radio color="primary" style={{color: "rgb(20, 90, 100)"}}/>;
    const d1 = "delay.1";
    const d2 = "delay.3";
    const d3 = "delay.off";

    if(menuParams === undefined || delayParams === undefined) {
        return null;
    }

    return (
        <div>
            <FormControl component="fieldset">
                <FormGroup column="true" style={{paddingLeft: "2rem"}}>
                    <h4 className={classes.colorsHeader}>{labels["screensaver.menu"]}</h4>
                    <Divider className={classes.colorsDivider} />
                    {menuItems.map((v, i) => {return Factory.createCheckbox(v, menuParams, updateState, labels, i)})}
                </FormGroup>
            </FormControl>
            <FormControl>
                <FormGroup column="true" style={{paddingLeft: "3rem"}}>
                    <h4 className={classes.colorsHeader}>{labels["delay"]}</h4>
                    <Divider className={classes.colorsDivider} />
                    <RadioGroup value={delayParams} onChange={this.handleTypeChange}>
                        <FormControlLabel value={d1} control={ctl} label={labels[d1]} />
                        <FormControlLabel value={d2} control={ctl} label={labels[d2]} />
                        <FormControlLabel value={d3} control={ctl} label={labels[d3]} />
                    </RadioGroup>
                </FormGroup>
            </FormControl>
        </div>
    );
  }
}