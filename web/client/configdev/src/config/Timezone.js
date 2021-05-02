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
import { flexbox } from "@material-ui/system";
import { Button, List, Paper, ListItem, ListItemText, Grid, FormControl } from '@material-ui/core';
import Factory from "../Factory";

export default class Timezone extends React.Component {
  handleChange = (src, item) => {
    this.props.updateState(src, item)
  }

  render() {
    const { params, labels, classes, setTimezone } = this.props;

    if (params === null) {
      return labels["supported.for.Linux"];
    }

    const areas = Object.keys(params.areaCities);
    const cities = params.areaCities[params.currentArea];
    const style = {width: "26rem", marginBottom: "1rem"};
    const timezoneLabel = {currentTimezone: labels["timezone"]};
    const timeLabel = {currentTime: labels["local.time"]}

    return (
      <div style={{ display: flexbox, flexDirection: "column" }}>
        <FormControl component="fieldset">
          {Factory.createTextField("currentTimezone", params, null, style, classes, timezoneLabel, true)}
          {Factory.createTextField("currentTime", params, null, style, classes, timeLabel, true)}
        </FormControl>
        <Grid container spacing={2}>
          <Grid item>
            <h4 className={classes.colorsHeader} style={{ marginTop: "0rem" }}>{labels["geographic.area"]}</h4>
            <Paper>
              <div style={{ height: "26rem", width: "16rem", overflow: "auto" }} ref={element => (this.container = element)}>
                <List>
                  {areas.map(function (item, index) {
                    return <ListItem
                      button
                      alignItems="flex-start"
                      id={index}
                      key={index}
                      dense={true}
                      selected={params.currentArea === item}>
                      <ListItemText primary={item} onClick={() => this.handleChange("area", item)}/>
                    </ListItem>
                  }, this)}
                </List>
              </div>
            </Paper>
          </Grid>
          <Grid item>
            <h4 className={classes.colorsHeader} style={{ marginTop: "0rem" }}>{labels["city"]}</h4>
            <Paper>
              <div style={{ height: "26rem", width: "16rem", overflow: "auto" }} ref={element => (this.container = element)}>
                <List>
                  {cities.map(function (item, index) {
                    return <ListItem
                      button
                      alignItems="flex-start"
                      id={index}
                      key={index}
                      dense={true}
                      selected={params.currentCity === item}>
                      <ListItemText primary={item} onClick={() => this.handleChange("city", item)}/>
                    </ListItem>
                  }, this)}
                </List>
              </div>
            </Paper>
          </Grid>
        </Grid>
        <Button variant="contained" className={classes.button} style={{ marginTop: "1.2rem" }}
          onClick={setTimezone}>{labels["set.timezone"]}</Button>
      </div>
    );
  }
}
