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
import { FormControl } from '@material-ui/core';
import { Button } from "@material-ui/core";
import Factory from "../Factory";

const CURRENT = "current.player.state.file";
const CONFIG = "configuration.file";
const PLAYERS = "players.file";

export const defaultsSections = [
  CURRENT, CONFIG, PLAYERS
];

export default class Default extends React.Component {
  
  render() {
    const { params, updateState, labels, classes, setDefaults } = this.props;
    const items = {};
    items[CURRENT] = params[0];
    items[CONFIG] = params[1];
    items[PLAYERS] = params[2];

    return (
      <FormControl component="fieldset">
        {Factory.createCheckbox(CURRENT, items, updateState, labels)}
        {Factory.createCheckbox(CONFIG, items, updateState, labels)}
        {Factory.createCheckbox(PLAYERS, items, updateState, labels)}
        <Button variant="contained" className={classes.button} style={{marginTop: "1rem"}} onClick={setDefaults}>{labels["set.default"]}</Button>
      </FormControl>
    );
  }
}
