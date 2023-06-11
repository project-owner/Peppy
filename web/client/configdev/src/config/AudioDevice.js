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
import { FormControl, List, ListItem, ListItemText, Paper } from '@material-ui/core';
import RadioButtonCheckedIcon from '@material-ui/icons/RadioButtonChecked';
import RadioButtonUncheckedIcon from '@material-ui/icons/RadioButtonUnchecked';
import { COLOR_MEDIUM } from "../Style";

export default class AudioDevice extends React.Component {
  render() {
    const { classes, labels, devices, updateState } = this.props;
    return (
      <FormControl>
        <h4 className={classes.colorsHeader} style={{paddingTop: "-2rem"}}>{labels["audio.device"]}</h4>
        <div>
          {devices && <Paper>
            <div style={{ height: "20rem", width: "30rem", overflow: "auto" }} ref={element => (this.container = element)}>
              <List>
                {devices.length > 0 && devices.map(function (item, index) {
                  return <ListItem button key={index}>
                    {item[2] === true && <RadioButtonCheckedIcon style={{ color: COLOR_MEDIUM, paddingRight: "1rem", verticalAlign: "top"}}/>}
                    {item[2] === false && <RadioButtonUncheckedIcon style={{ color: COLOR_MEDIUM, paddingRight: "1rem" }} 
                        onClick={() => updateState(item[0])}/>}
                    <ListItemText primary={item[1]}/>
                  </ListItem>
                })}
              </List>
            </div>
          </Paper>}
        </div>
      </FormControl>
    );
  }
}
