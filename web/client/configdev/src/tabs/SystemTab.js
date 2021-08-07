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

import React from "react";
import Timezone from "../config/Timezone";
import DiskManager from "../config/DiskManager";
import NasManager from "../config/NasManager";
import Default from "../config/Default";
import LogFile from "../config/LogFile";

export const systemSections = [
  "timezone", "disk.manager", "nas.manager", "defaults", "log.file"
];

export default class SystemTab extends React.Component {
  render() {
    const { params, classes, labels, topic, updateState, setDefaults, setTimezone, disks, mount, 
      unmount, poweroff, refresh, log, getLog, addNas, mountNas, unmountNas, delNas, nases, refreshNas } = this.props;

    if (topic === 3) {
      getLog();
    }

    return (
      <main className={classes.content}>
        {topic === 0 && <Timezone params={params.timezone} labels={labels} classes={classes} 
          updateState={updateState} setTimezone={setTimezone}/>}
        {topic === 1 && <DiskManager labels={labels} classes={classes} disks={disks}
          mount={mount} unmount={unmount} poweroff={poweroff} refresh={refresh}/>}
        {topic === 2 && <NasManager labels={labels} classes={classes} nases={nases} updateState={updateState}
          addNas={addNas} mount={mountNas} unmount={unmountNas} deleteNas={delNas} refreshNas={refreshNas}/>}
        {topic === 3 && <Default params={params.defaults} labels={labels} classes={classes} 
          updateState={updateState} setDefaults={setDefaults}/>}
        {topic === 4 && <LogFile log={log} labels={labels} classes={classes} getLog={getLog}/>}
      </main>
    );
  }
}
