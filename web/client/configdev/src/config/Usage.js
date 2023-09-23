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

import React from 'react';
import {FormControl, FormGroup} from '@material-ui/core';
import Factory from "../Factory";

export default class Usage extends React.Component {
  render() {
    const { classes, params, updateState, labels } = this.props;

    return (
      <div>
        <FormControl component="fieldset">
          <FormGroup column="true">
            {Factory.createCheckbox("touchscreen", params, updateState, labels)}
            {Factory.createCheckbox("mouse", params, updateState, labels)}
            {Factory.createCheckbox("lirc", params, updateState, labels)}
            {Factory.createCheckbox("web", params, updateState, labels)}
            {Factory.createCheckbox("stream.server", params, updateState, labels)}
            {Factory.createCheckbox("browser.stream.player", params, updateState, labels)}
            {Factory.createCheckbox("voice.assistant", params, updateState, labels)}
          </FormGroup>
          {Factory.createNumberTextField("long.press.time.ms", params, updateState, 
            "ms", {width: "10rem", marginTop: "1rem"}, classes, labels
          )}
          {Factory.createNumberTextField("dns.ip", params, updateState,
            "", {width: "10rem", marginTop: "1rem"}, classes, labels
          )}
        </FormControl>
        <FormControl component="fieldset">
          <FormGroup column="true">
            {Factory.createCheckbox("headless", params, updateState, labels)}
            {Factory.createCheckbox("vu.meter", params, updateState, labels)}
            {Factory.createCheckbox("album.art", params, updateState, labels)}
            {Factory.createCheckbox("auto.play", params, updateState, labels)}
            {Factory.createCheckbox("desktop", params, updateState, labels)}
            {Factory.createCheckbox("check.for.updates", params, updateState, labels)}
            {Factory.createCheckbox("bluetooth", params, updateState, labels)}
            {Factory.createCheckbox("samba", params, updateState, labels)}
            {Factory.createCheckbox("use.clock.screensaver.in.timer", params, updateState, labels)}
          </FormGroup>
        </FormControl>
      </div>
    );
  }
}
