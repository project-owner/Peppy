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
import {FormControl, FormGroup} from '@material-ui/core';
import Factory from "../Factory";
import Divider from '@material-ui/core/Divider';

export default class Gpio extends React.Component {
  render() {
    const { classes, params, updateState, labels } = this.props;
    const style = {width: "10rem", marginTop: "1.4rem"};
    const width = "12rem";

    return (
      <div style={{marginTop: "-2rem", display: "flex", flexDirection: "row"}}>
        <div style={{display: "flex", flexDirection: "column"}}>
          <h4>{labels["rotary.encoders"]}</h4>
          <Divider style={{marginBottom: "1rem"}} />
          {Factory.createCheckbox("use.rotary.encoders", params, updateState, labels)}
          <FormControl component="fieldset">
            <FormGroup column="true">              
              {Factory.createNumberTextField("rotary.encoder.jitter.filter", params, updateState, "", 
                {...style, marginBottom: "1rem"}, classes, labels, labels["jitter.filter"], width)}
              {Factory.createNumberTextField("rotary.encoder.volume.up", params, updateState, "", 
                style, classes, labels, labels["volume.up"], width)}
              {Factory.createNumberTextField("rotary.encoder.volume.down", params, updateState, "", 
                style, classes, labels, labels["volume.down"], width)}
              {Factory.createNumberTextField("rotary.encoder.volume.mute", params, updateState, "", 
                style, classes, labels, labels["mute"], width)}
              {Factory.createNumberTextField("rotary.encoder.navigation.left", params, updateState, "", 
                style, classes, labels, labels["left"], width)}
              {Factory.createNumberTextField("rotary.encoder.navigation.right", params, updateState, "", 
                style, classes, labels, labels["right"], width)}
              {Factory.createNumberTextField("rotary.encoder.navigation.select", params, updateState, "", 
                style, classes, labels, labels["select"], width)}
            </FormGroup>
          </FormControl>
        </div>
        <div style={{ borderRight: '0.1em solid lightgrey', marginTop: '1.4rem', marginLeft: "2rem" }}/>
        <div style={{display: "flex", flexDirection: "column", paddingLeft: "2rem"}}>
          <h4>{labels["buttons"]}</h4>
          <Divider style={{marginBottom: "1rem"}} />
          {Factory.createCheckbox("use.buttons", params, updateState, labels)}
          <div style={{display: "flex", flexDirection: "row"}}>
            <FormControl component="fieldset">
              <FormGroup column="true">
                {Factory.createNumberTextField("button.left", params, updateState, "", style, classes, 
                  labels, labels["left"], width)}
                {Factory.createNumberTextField("button.right", params, updateState, "", style, classes, 
                  labels, labels["right"], width)}
                {Factory.createNumberTextField("button.up", params, updateState, "", style, classes, 
                  labels, labels["up"], width)}
                {Factory.createNumberTextField("button.down", params, updateState, "", style, classes, 
                  labels, labels["down"], width)}
                {Factory.createNumberTextField("button.select", params, updateState, "", style, classes, 
                  labels, labels["select"], width)}
                {Factory.createNumberTextField("button.mute", params, updateState, "", style, classes, 
                  labels, labels["mute"], width)}
              </FormGroup>
            </FormControl>
            <FormControl component="fieldset" style={{marginLeft: "1.4rem"}}>
              <FormGroup column="true">
                {Factory.createNumberTextField("button.volume.up", params, updateState, "", style, classes, 
                  labels, labels["volume.up"], width)}
                {Factory.createNumberTextField("button.volume.down", params, updateState, "", style, classes, 
                  labels, labels["volume.down"], width)}
                {Factory.createNumberTextField("button.play.pause", params, updateState, "", style, classes, 
                  labels, labels["play.pause"], width)}
                {Factory.createNumberTextField("button.next", params, updateState, "", style, classes, 
                  labels, labels["next"], width)}
                {Factory.createNumberTextField("button.previous", params, updateState, "", style, classes, 
                  labels, labels["previous"], width)}
                {Factory.createNumberTextField("button.home", params, updateState, "", style, classes, 
                  labels, labels["home.menu"], width)}
              </FormGroup>
            </FormControl>
          </div>
        </div>
      </div>
    );
  }
}