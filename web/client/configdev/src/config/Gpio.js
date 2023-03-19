/* Copyright 2020-2023 Peppy Player peppy.player@gmail.com
 
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
import Factory from "../Factory";
import Accordion from '@material-ui/core/Accordion';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import { FormControl, FormGroup, InputLabel, Select, MenuItem } from '@material-ui/core';

export default class Gpio extends React.Component {
  handleChange = (event) => {
    this.props.updateState("button.type", event.target.value)
  }

  render() {
    const { classes, params, updateState, labels } = this.props;
    const style = { width: "10rem", marginTop: "1.4rem" };
    const width = "12rem";

    return (
      <div style={{ width: "28rem", marginBottom: "0.5rem" }}>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <div style={{ width: "100%", display: "flex", flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ fontWeight: "bold" }}>
                <div>{labels["rotary.encoders"]}</div>
              </div>
            </div>
          </AccordionSummary>
          <AccordionDetails className={classes.details}>
            <div style={{ display: "flex", flexDirection: "column", marginBottom: "1rem" }}>
              {Factory.createCheckbox("use.rotary.encoders", params, updateState, labels)}
              <FormControl component="fieldset">
                <FormGroup column="true">
                  {Factory.createNumberTextField("rotary.encoder.jitter.filter", params, updateState, "",
                    { ...style, marginBottom: "1rem" }, classes, labels, labels["jitter.filter"], width)}
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
          </AccordionDetails>
        </Accordion>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <div style={{ width: "100%", display: "flex", flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ fontWeight: "bold" }}>
                <div>{labels["buttons.player"]}</div>
              </div>
            </div>
          </AccordionSummary>
          <AccordionDetails className={classes.details}>
            <div style={{ display: "flex", flexDirection: "row", marginBottom: "1rem" }}>
              <div style={{ display: "flex", flexDirection: "column" }}>
                <div style={{ display: "flex", flexDirection: "row" }}>
                  {Factory.createCheckbox("use.player.buttons", params, updateState, labels)}
                  <FormControl style={{ width: "12rem", marginTop: "0.4rem", marginLeft: "5rem" }}>
                    <FormGroup column="true">
                      <InputLabel shrink>{labels["type"]}</InputLabel>
                      <Select
                        value={params["button.type"] || "GPIO"}
                        onChange={this.handleChange}
                      >
                        <MenuItem value={"GPIO"}>{labels["gpio"]}</MenuItem>
                        <MenuItem value={"I2C"}>{labels["i2c"]}</MenuItem>
                      </Select>
                    </FormGroup>
                  </FormControl>
                </div>
                <div style={{ display: "flex", flexDirection: "row" }}>
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
                      {Factory.createNumberTextField("button.poweroff", params, updateState, "", style, classes,
                        labels, labels["poweroff"], width)}
                    </FormGroup>
                  </FormControl>
                  <FormControl component="fieldset" style={{ marginLeft: "1.4rem" }}>
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
          </AccordionDetails>
        </Accordion>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <div style={{ width: "100%", display: "flex", flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ fontWeight: "bold" }}>
                <div>{labels["buttons.menu"]}</div>
              </div>
            </div>
          </AccordionSummary>
          <AccordionDetails className={classes.details}>
            <div style={{ display: "flex", flexDirection: "row", marginBottom: "1rem" }}>
              <div style={{ display: "flex", flexDirection: "column" }}>
                <div style={{ display: "flex", flexDirection: "row" }}>
                  {Factory.createCheckbox("use.menu.buttons", params, updateState, labels)}
                </div>
                <div style={{ display: "flex", flexDirection: "row" }}>
                  <FormControl component="fieldset">
                    <FormGroup column="true">
                      {Factory.createNumberTextField("button.menu.1", params, updateState, "", style, classes,
                        labels, labels["menu.item"] + " 1", width)}
                      {Factory.createNumberTextField("button.menu.2", params, updateState, "", style, classes,
                        labels, labels["menu.item"] + " 2", width)}
                      {Factory.createNumberTextField("button.menu.3", params, updateState, "", style, classes,
                        labels, labels["menu.item"] + " 3", width)}
                      {Factory.createNumberTextField("button.menu.4", params, updateState, "", style, classes,
                        labels, labels["menu.item"] + " 4", width)}
                      {Factory.createNumberTextField("button.menu.5", params, updateState, "", style, classes,
                        labels, labels["menu.item"] + " 5", width)}
                    </FormGroup>
                  </FormControl>
                  <FormControl component="fieldset" style={{ marginLeft: "1.4rem" }}>
                    <FormGroup column="true">
                      {Factory.createNumberTextField("button.menu.6", params, updateState, "", style, classes,
                        labels, labels["menu.item"] + " 6", width)}
                      {Factory.createNumberTextField("button.menu.7", params, updateState, "", style, classes,
                        labels, labels["menu.item"] + " 7", width)}
                      {Factory.createNumberTextField("button.menu.8", params, updateState, "", style, classes,
                        labels, labels["menu.item"] + " 8", width)}
                      {Factory.createNumberTextField("button.menu.9", params, updateState, "", style, classes,
                        labels, labels["menu.item"] + " 9", width)}
                      {Factory.createNumberTextField("button.menu.10", params, updateState, "", style, classes,
                        labels, labels["menu.item"] + " 10", width)}
                    </FormGroup>
                  </FormControl>
                </div>
              </div>
            </div>
          </AccordionDetails>
        </Accordion>
      </div>
    );
  }
}