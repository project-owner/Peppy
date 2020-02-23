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
import { withStyles } from "@material-ui/core/styles";
import styles from "../Style";
import { Snackbar } from "@material-ui/core";
import SnackbarContent from '@material-ui/core/SnackbarContent';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import ErrorIcon from '@material-ui/icons/Error';
import InfoIcon from '@material-ui/icons/Info';
import WarningIcon from '@material-ui/icons/Warning';

class Notification extends React.Component {
  render() {
    const { classes, message, variant } = this.props;

    const variants = {
      success: { icon: <CheckCircleIcon/>, bgr: classes.success },
      warning: { icon: <WarningIcon/>, bgr: classes.warning },
      error: { icon: <ErrorIcon/>, bgr: classes.error },
      info: { icon: <InfoIcon/>, bgr: classes.info }
    };

    return (
      <Snackbar
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right', }}
        open={this.props.openSnack}
        autoHideDuration={2000}
        onClose={this.props.handleSnackClose}
      >
        <SnackbarContent
          className={variants[variant].bgr}
          aria-describedby="client-snackbar"
          message={
            <span id="client-snackbar" className={classes.notificationMsg}>
              <span className={classes.notificationIcon}>{variants[variant].icon}</span>
              {message}
            </span>
          }
          action={[
            <IconButton
              key="close"
              aria-label="Close"
              color="inherit"
              className={classes.close}
              onClick={this.props.handleSnackClose}
            >
              <CloseIcon />
            </IconButton>
          ]}
        />
      </Snackbar>
    );
  }
}

export default withStyles(styles)(Notification);
