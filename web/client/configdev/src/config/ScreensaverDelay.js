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

import React from 'react';
import {FormControl, RadioGroup, FormControlLabel, Radio} from '@material-ui/core';

export default class ScreensaverDelay extends React.Component {
  handleTypeChange = (event) => {
    this.props.updateState("delay", event.target.value);
  }

  render() {
    const { params, labels } = this.props;
    const ctl = <Radio color="primary" style={{color: "rgb(20, 90, 100)"}}/>;
    const d1 = "delay.1";
    const d2 = "delay.3";
    const d3 = "delay.off";

    return (
      <div style={{ display: "flex", flexDirection: "column" }}>
        <FormControl component="fieldset">
          <RadioGroup value={params["delay"]} onChange={this.handleTypeChange}>
            <FormControlLabel value={d1} control={ctl} label={labels[d1]} />
            <FormControlLabel value={d2} control={ctl} label={labels[d2]} />
            <FormControlLabel value={d3} control={ctl} label={labels[d3]} />
          </RadioGroup>
        </FormControl>
      </div>
    );
  }
}
