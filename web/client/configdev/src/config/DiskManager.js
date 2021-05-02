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
import Disk from "../components/Disk";
import RefreshIcon from '@material-ui/icons/Refresh';

export default class DiskManager extends React.Component {
  render() {
    const { classes, labels, disks, mount, unmount, poweroff, refresh } = this.props;

    if (disks === null || disks === undefined) {
      return labels["supported.for.Linux"];
    }

    return (
      <div style={{ width: "30rem", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
        <span style={{ width: "33rem", display: "flex", flexDirection: "row", justifyContent: "space-between" }}>
          { disks.length === 0 && <div>{labels["no.disks.found"]}</div>}
          <div style={{ marginLeft: "auto" }}>
            <Button variant="contained" className={classes.addButton} onClick={() => { refresh() }}>
              {labels.refresh}
              <RefreshIcon style={{ marginLeft: "1rem" }} />
            </Button>
          </div>
        </span>
        {disks && disks.length > 0 && disks.map(function (disk, index) {
          return <Disk key={index} classes={classes} labels={labels} disk={disk} mount={mount} 
            unmount={unmount} poweroff={poweroff}/>
        })}
      </div>
    );
  }
}
