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
import { Button } from "@material-ui/core";

export default class Buttons extends React.Component {
  render() {
    if(!this.props.lang) {
      return null;
    }

    const { classes, labels, buttonsDisabled, save, openRebootDialog, openShutdownDialog } = this.props;
    return (
      <>
        <Button disabled={buttonsDisabled} variant="contained" className={classes.button} onClick={save}>{labels.save}</Button>
        <Button disabled={buttonsDisabled} variant="contained" className={classes.button} onClick={openRebootDialog}>{labels.reboot}</Button>
        <Button disabled={buttonsDisabled} variant="contained" className={classes.button} onClick={openShutdownDialog}>{labels.shutdown}</Button>
      </>
    );
  }
}
