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
import { Button } from '@material-ui/core';
import Nas from "../components/Nas";
import AddIcon from '@material-ui/icons/Add';
import RefreshIcon from '@material-ui/icons/Refresh';

export default class NasManager extends React.Component {
  render() {
    const { classes, labels, nases, mount, unmount, addNas, deleteNas, refreshNas, updateState } = this.props;

    if (nases === null || nases === undefined) {
      return labels["supported.for.Linux"];
    }

    return (
      <div style={{ width: "32rem", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
        <span style={{ width: "100%", display: "flex", flexDirection: "row", justifyContent: "space-between" }}>
          <div>
            <Button variant="contained" className={classes.addButton} style={{ justifyContent: "flex-start" }}
              onClick={() => { addNas() }}
            >
              {labels["add.nas"]}
              <AddIcon style={{ marginLeft: "1rem" }} />
            </Button>
          </div>
          <div style={{ display: "flex", justifyContent: "flex-end", alignItems: "center" }}>
            <Button variant="contained" className={classes.addButton} onClick={() => { refreshNas() }}>
              {labels.refresh}
              <RefreshIcon style={{ marginLeft: "1rem" }} />
            </Button>
          </div>
        </span>
        {nases && nases.length > 0 && nases.map(function (nas, index) {
          return <Nas key={index} index={index} classes={classes} labels={labels} nas={nas} mount={mount} 
            unmount={unmount} deleteNas={deleteNas} updateState={updateState}/>
        })}
      </div>
    );
  }
}
