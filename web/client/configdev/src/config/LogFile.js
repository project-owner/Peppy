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
import { FormControl, Button } from '@material-ui/core';
import Factory from "../Factory";
import RefreshIcon from '@material-ui/icons/Refresh';

export default class LogFile extends React.Component {
  render() {
    const { log, classes, labels, getLog } = this.props;
    let logData = log || "";
    let data = { "log": logData };

    return (
      <FormControl>
        <main className={classes.content}>
          <div style={{ display: "flex", flexDirection: "column" }} autoComplete="off" 
            autoCorrect="off" autoCapitalize="off" spellCheck="false">
            <div style={{ marginLeft: "auto" }}>
              <Button variant="contained" className={classes.addButton} onClick={() => { getLog(true) }}>
                {labels.refresh}
                <RefreshIcon style={{ marginLeft: "1rem" }} />
              </Button>
            </div>
            {Factory.createResizableTextArea("log", data, { width: "50rem" })}
          </div>
        </main>
      </FormControl>
    );
  }
}
