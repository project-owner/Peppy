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
import {FormControl, FormGroup} from '@material-ui/core';
import Factory from "../Factory";
import Divider from '@material-ui/core/Divider';

export const homeMenuItems = ["radio", "audio-files", "audiobooks", "podcasts", "stream", "cd-player", 
    "airplay", "spotify-connect", "collection", "bluetooth-sink", "ya-streams", "jukebox", "archive"];
export const homeNavigatorItems = ["back", "screensaver", "equalizer", "language", "timer", "network", "player", "about"];

export default class HomeScreen extends React.Component {
  render() {
    const { menuParams, navigatorParams, updateState, labels, classes } = this.props;
    
    return (
        <div>
            <FormControl component="fieldset">
                <FormGroup column="true" style={{paddingLeft: "2rem"}}>
                    <h4 className={classes.colorsHeader}>{labels["home.menu"]}</h4>
                    <Divider className={classes.colorsDivider} />
                    {homeMenuItems.map((v, i) => {return Factory.createCheckbox(v, menuParams, updateState, labels, i)})}
                </FormGroup>
            </FormControl>
            <FormControl>
                <FormGroup column="true" style={{paddingLeft: "3rem"}}>
                    <h4 className={classes.colorsHeader}>{labels["home.navigator"]}</h4>
                    <Divider className={classes.colorsDivider} />
                    {homeNavigatorItems.map((v, i) => {return Factory.createCheckbox(v, navigatorParams, updateState, labels, i)})}
                </FormGroup>
            </FormControl>
        </div>
    );
  }
}
