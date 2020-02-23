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

export default class Copyright extends React.Component {
  render() {
    const { classes, release } = this.props;
    const name = release["product.name"];
    const edition = release["edition.name"];
    const year = release["year"];

    return (
      <div className={classes.footerCopyright}>
        {name} &copy; {year} {edition}
      </div>
    );
  }
}
