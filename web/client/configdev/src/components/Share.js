/* Copyright 2022 Peppy Player peppy.player@gmail.com
 
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

export default class Share extends React.Component {
  render() {
    const { index, share, classes, labels, deleteShare, updateState } = this.props;
    let style = { "width": "30rem", "marginBottom": "1.4rem" };
    let last = { "width": "28rem", "marginBottom": "0rem" };
    const TYPE_DEFAULT = "text";
    const rows = 5;

    return (
      <div style={{ width: "32rem", marginBottom: "0.5rem" }}>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <div style={{ width: "100%", display: "flex", flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ fontWeight: "bold" }}>
                <div>{share.name}</div>
              </div>
            </div>
          </AccordionSummary>
          <AccordionDetails className={classes.details}>
            <div>
              {Factory.createTextField("name", share, updateState, style, classes, labels, false, index, TYPE_DEFAULT, true)}
              {Factory.createTextField("path", share, updateState, style, classes, labels, false, index, TYPE_DEFAULT, true)}

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <div style={{ width: "100%", display: "flex", flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
                    <div style={{ fontWeight: "bold" }}>
                      <div>{labels["options"]}</div>
                    </div>
                  </div>
                </AccordionSummary>
                <AccordionDetails className={classes.details}>
                  <div style={{ width: "28rem"}}>
                    {Factory.createTextArea("", share, updateState, last, classes, labels, false, rows, share["options"], index)}
                  </div>
                </AccordionDetails>
              </Accordion>

            </div>
          </AccordionDetails>
          <AccordionActions>
            <Button variant="contained" className={classes.button}
              style={{ marginRight: "0.5rem", marginBottom: "1rem" }} onClick={() => { deleteShare(index) }}>{labels["delete"]}
            </Button>
          </AccordionActions>
        </Accordion>
      </div>
    );
  }
}
