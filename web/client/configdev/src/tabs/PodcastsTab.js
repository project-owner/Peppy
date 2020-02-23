/* Copyright 2019 Peppy Player peppy.player@gmail.com
 
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

export default class PodcastsTab extends React.Component {
  render() {
    if (!this.props.podcasts) {
      return null;
    }

    const { classes, labels, updateState, podcasts } = this.props;
    const style = {width: "40rem"};
    const linksObj = {"podcasts": podcasts}

    return (
      <main className={classes.content}>
        <div className={classes.toolbar} />
        {Factory.createTextArea("podcasts", linksObj, updateState, style, classes, labels)}
      </main>
    );
  }
}
