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
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';

export default class ConfirmationDialog extends React.Component {
  render() {
    const { classes, title, message, yes, no, isDialogOpen, yesAction, noAction, cancelAction } = this.props;
    return (
      <Dialog
        fullWidth={false}
        open={isDialogOpen}>
        <DialogTitle disableTypography className={classes.dialogTitle}>
          <h3>{title}</h3>
          <IconButton className={classes.dialogIcon} aria-label="Close" onClick={cancelAction}><CloseIcon /></IconButton>
        </DialogTitle>
        <DialogContent className={classes.dialogContent} dividers>{message}</DialogContent>
        <DialogActions>
          <Button onClick={yesAction} color="primary">{yes}</Button>
          <Button onClick={noAction} color="primary" autoFocus>{no}</Button>
        </DialogActions>
      </Dialog>
    );
  }
}
