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
import Accordion from '@material-ui/core/Accordion';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionActions from '@material-ui/core/AccordionActions';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import Button from '@material-ui/core/Button';
import Factory from "../Factory";

export default class Nas extends React.Component {
  setOptions = (name, value, index) => {
    if (value === "cifs") {
      this.props.updateState("mount.options", "uid=1000,gid=1000,dir_mode=0700,file_mode=0700", index);
    }
    this.props.updateState(name, value, index);
  }

  render() {
    const { index, nas, classes, labels, mount, unmount, deleteNas, updateState } = this.props;
    let style = { "width": "30rem", "marginBottom": "1.4rem" };
    let last = { "width": "30rem", "marginBottom": "0rem" };
    const TYPE_DEFAULT = "text";
    const TYPE_PASSWORD = "password";

    return (
      <div style={{ width: "32rem", marginBottom: "0.5rem" }}>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <div style={{ width: "100%", display: "flex", flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ fontWeight: "bold" }}>
                <div>{nas.name}</div>
              </div>
              <div style={{ fontWeight: "bold", color: nas.mounted ? "green" : "red" }}>
                <div>{nas.mounted ? labels.mounted : labels.unmounted}</div>
              </div>
            </div>
          </AccordionSummary>
          <AccordionDetails className={classes.details}>
            <div>
              {Factory.createTextField("name", nas, updateState, style, classes, labels, false, index, TYPE_DEFAULT, true)}
              {Factory.createTextField("ip.address", nas, updateState, style, classes, labels, false, index, TYPE_DEFAULT, true)}
              {Factory.createTextField("folder", nas, updateState, style, classes, labels, false, index, TYPE_DEFAULT, true)}
              {Factory.createTextField("filesystem", nas, this.setOptions, style, classes, labels, false, index, TYPE_DEFAULT, true)}
              {Factory.createTextField("username", nas, updateState, style, classes, labels, false, index, TYPE_DEFAULT, true)}
              {Factory.createTextField("password", nas, updateState, style, classes, labels, false, index, TYPE_PASSWORD, true)}
              {Factory.createTextField("mount.options", nas, updateState, last, classes, labels, false, index, TYPE_DEFAULT)}
            </div>
          </AccordionDetails>
          <AccordionActions>
            <Button variant="contained" disabled={nas.mounted} className={classes.button}
              style={{ marginRight: "0.2rem", marginBottom: "1rem" }} onClick={() => { mount(index) }}>{labels["mount"]}
            </Button>
            <Button variant="contained" disabled={!nas.mounted} className={classes.button}
              style={{ marginRight: "0.2rem", marginBottom: "1rem" }} onClick={() => { unmount(index) }}>{labels["unmount"]}
            </Button>
            <Button variant="contained" className={classes.button}
              style={{ marginRight: "0.5rem", marginBottom: "1rem" }} onClick={() => { deleteNas(index) }}>{labels["delete"]}
            </Button>
          </AccordionActions>
        </Accordion>
      </div>
    );
  }
}
