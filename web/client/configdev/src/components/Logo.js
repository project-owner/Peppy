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

export default class Logo extends React.Component {
  render() {
    const { classes, release } = this.props;
    const imagePath = "/icon/peppy-logo.svg";
    const name = release["product.name"].toUpperCase();
    const edition = release["edition.name"].toUpperCase();

    return (
      <>
        <div className={classes.logoIcon}>
          <a href="/">
            <img src={imagePath} alt="Logo"/>
          </a>
        </div>
        <div className={classes.logoText}>
          <a href="/" className={classes.logoLink}>
            <div className={classes.logoNameText}>{name}</div>
            <div className={classes.logoEditionText}>{edition}</div>
          </a>
        </div>
      </>
    );
  }
}
