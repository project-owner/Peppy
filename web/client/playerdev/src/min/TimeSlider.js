/* Copyright 2024 Peppy Player peppy.player@gmail.com
 
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
import Slider from '@mui/material/Slider';
import Typography from '@mui/material/Typography';
import { TimeSliderPanel, TimeStyle, TimeSliderStyle, SliderPanel, TimeLeftPanel, TimeRightPanel } from './mincss';

export default class TimeSlider extends React.Component {
  render() {
    const { timeCurrent, timeTotal, position, setTimeSliderPosition, setTime } = this.props;

    return (
      <div style={TimeSliderPanel}>
        <div style={TimeLeftPanel}>
          <Typography noWrap style={TimeStyle}>{timeCurrent}</Typography>
        </div>
        <div style={SliderPanel}>
          <Slider
            orientation="horizontal"
            aria-label="time"
            size='small'
            value={position}
            min={0}
            step={1}
            defaultValue={0}
            max={100}
            onChange={setTimeSliderPosition}
            onChangeCommitted={setTime}
            sx={TimeSliderStyle}
          />
        </div>
        <div style={TimeRightPanel}>
          <Typography noWrap style={TimeStyle}>{timeTotal}</Typography>
        </div>
      </div>
    );
  }
}
