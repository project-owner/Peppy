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

import React from "react";
import Factory from "../Factory";

export default class YaStreamsTab extends React.Component {
  render() {
    if (!this.props.yastreams) {
      return null;
    }

    const { classes, labels, updateState, yastreams } = this.props;
    const style = {width: "40rem", paddingTop: "3rem"};
    const linksObj = {"yastreams": yastreams}

    return (
      <main className={classes.content}>
        {Factory.createTextArea("yastreams", linksObj, updateState, style, classes, labels, false, 32)}
      </main>
    );
  }
}
