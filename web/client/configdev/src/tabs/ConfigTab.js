/* Copyright 2019-2023 Peppy Player peppy.player@gmail.com
 
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
import Display from "../config/Display";
import Usage from "../config/Usage";
import Logging from "../config/Logging";
import WebServer from "../config/WebServer";
import StreamServer from "../config/StreamServer";
import Folders from "../config/Folders";
import Collection from "../config/Collection";
import DiskMount from "../config/DiskMount";
import Colors from "../config/Colors";
import Icons from "../config/Icons";
import Background from "../config/Background";
import Font from "../config/Font";
import VolumeControl from "../config/VolumeControl";
import DisplayBacklight from "../config/DisplayBacklight";
import Scripts from "../config/Scripts";
import Gpio from "../config/Gpio";
import I2C from "../config/I2C";

export const configSections = [
  "screen.info", "usage", "logging", "web.server", "stream.server", "folders", "collection", "disk.mount", 
  "colors", "icons", "background", "font", "volume.control", "display.backlight", "scripts", "gpio", "i2c"
];

export default class ConfigTab extends React.Component {
  render() {
    const { params, classes, topic, updateState, labels, background, fonts, uploadFont } = this.props;
    let p = params[configSections[topic]];
    
    return (
      <main className={classes.content}>
        <div className={classes.toolbar} />
        {topic === 0 && <Display params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 1 && <Usage params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 2 && <Logging params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 3 && <WebServer params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 4 && <StreamServer params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 5 && <Folders params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 6 && <Collection params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 7 && <DiskMount params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 8 && <Colors params={p} labels={labels} reset={this.props.reset} classes={classes}
          updateState={updateState} setPalette={this.props.setPalette} setColor={this.props.setColor} />}
        {topic === 9 && <Icons params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 10 && <Background params={background} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 11 && <Font params={p} labels={labels} classes={classes} updateState={updateState} fonts={fonts} uploadFont={uploadFont} />}
        {topic === 12 && <VolumeControl params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 13 && <DisplayBacklight params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 14 && <Scripts params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 15 && <Gpio params={p} labels={labels} classes={classes} updateState={updateState} />}
        {topic === 16 && <I2C params={p} labels={labels} classes={classes} updateState={updateState} />}
      </main>
    );
  }
}
