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

export default class Disk extends React.Component {
  render() {
    const { disk, classes, labels, mount, unmount, poweroff } = this.props;
    let style = { "width": "30rem", "marginBottom": "1.4rem" };
    let last = { "width": "30rem", "marginBottom": "0rem" };

    return (
      <div style={{ width: "32rem", marginBottom: "0.5rem", marginLeft: "1rem", zIndex: "100" }}>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <div style={{ width: "100%", display: "flex", flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ fontWeight: "bold" }}>
                <div>{disk.name}</div>
              </div>
              <div style={{ fontWeight: "bold", color: disk.mounted ? "green" : "red" }}>
                <div>{disk.mounted ? labels.mounted : labels.unmounted}</div>
              </div>
            </div>
          </AccordionSummary>
          <AccordionDetails className={classes.details}>
            <div>
              {Factory.createTextField("name", disk, null, style, classes, labels, true)}
              {Factory.createTextField("mount.point", disk, null, style, classes, labels, true)}
              {Factory.createTextField("device", disk, null, style, classes, labels, true)}
              {Factory.createTextField("uuid", disk, null, style, classes, labels, true)}
              {Factory.createTextField("vendor", disk, null, style, classes, labels, true)}
              {Factory.createTextField("model", disk, null, style, classes, labels, true)}
              {Factory.createTextField("filesystem", disk, null, last, classes, labels, true)}
            </div>
          </AccordionDetails>
          <AccordionActions>
            <Button variant="contained" disabled={disk.mounted} className={classes.button}
              style={{ marginRight: "0.2rem", marginBottom: "1rem" }} onClick={() => { mount(disk.name, disk.device, disk["mount.point"]) }}>{labels["mount"]}
            </Button>
            <Button variant="contained" disabled={!disk.mounted} className={classes.button}
              style={{ marginRight: "0.2rem", marginBottom: "1rem" }} onClick={() => { unmount(disk.device) }}>{labels["unmount"]}
            </Button>
            <Button variant="contained" className={classes.button}
              style={{ marginRight: "0.5rem", marginBottom: "1rem" }} onClick={() => { poweroff(disk.device) }}>{labels["poweroff"]}
            </Button>
          </AccordionActions>
        </Accordion>
      </div>
    );
  }
}
