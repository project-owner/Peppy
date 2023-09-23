/* Copyright 2023 Peppy Player peppy.player@gmail.com
 
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
import Factory from "../Factory";

let playlistName = "";

export default class CreatePlaylistDialog extends React.Component {
  setName = (name, value) => {
    playlistName = value;
  }

  createPlaylist() {
    this.props.yesAction(playlistName);
    playlistName = "";
  }

  render() {
    const { classes, labels, isDialogOpen, noAction, cancelAction } = this.props;
    let style = { "width": "30rem", "marginBottom": "1.4rem" };
    let value = {};

    return (
      <Dialog
        fullWidth={false}
        open={isDialogOpen}>
        <DialogTitle disableTypography className={classes.dialogTitle}>
          <h3>{labels["create.playlist"]}</h3>
          <IconButton className={classes.dialogIcon} aria-label="Close" onClick={cancelAction}><CloseIcon /></IconButton>
        </DialogTitle>
        <DialogContent className={classes.dialogContent} dividers>
          {Factory.createTextField("playlist.name", value, this.setName, style, classes, labels, false, 0, "text", false, ".m3u")}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {this.createPlaylist()}} color="primary">{labels.yes}</Button>
          <Button onClick={noAction} color="primary" autoFocus>{labels.no}</Button>
        </DialogActions>
      </Dialog>
    );
  }
}
