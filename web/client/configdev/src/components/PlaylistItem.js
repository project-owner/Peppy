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
import { ListItem, ListItemText, ListItemAvatar, Avatar, Divider, IconButton } from '@material-ui/core';
import EditIcon from '@material-ui/icons/Edit';
import PlaylistAddCheckIcon from '@material-ui/icons/PlaylistAddCheck';
import DeleteIcon from '@material-ui/icons/Delete';
import PlayCircleFilledIcon from '@material-ui/icons/PlayCircleFilled';
import VolumeUpIcon from '@material-ui/icons/VolumeUp';
import ArrowUpwardIcon from '@material-ui/icons/ArrowUpward';
import ArrowDownwardIcon from '@material-ui/icons/ArrowDownward';
import CloseIcon from '@material-ui/icons/Close';
import Factory from "../Factory";
import { COLOR_PANEL, COLOR_WEB_BGR, COLOR_MEDIUM } from "../Style";
import { deleteImage } from "../Fetchers";
import ConfirmationDialog from "./ConfirmationDialog";

export default class PlaylistItem extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectItem: props.selectItem,
      itemIndex: undefined,
      isDeleteImageDialogOpen: false
    }
    this.selectIndex = this.selectIndex.bind(this);
  }

  selectIndex(index) {
    this.state.selectItem(index);
  }

  edit(id, item, items, updateState) {
    if (item.name && !item.nameBak) {
      item.nameBak = item.name;
    }
    if (item.link && !item.linkBak) {
      item.linkBak = item.link;
    }
    if (item.imagePath && !item.imagePathBak) {
      item.imagePathBak = item.imagePath;
    }
    if (item.image && !item.imageBak) {
      item.imageBak = item.image;
    }
    item.edit = !item.edit;
    updateState(id, items);
  }

  getItemView(props) {
    const { id, item, items, index, updateState, play, pause, playing, selectedIndex } = props;
    const itemSelected = selectedIndex === index ? true : false;

    return <>
      <ListItem
        button
        alignItems="flex-start"
        id={index}
        key={index}
        onClick={() => this.selectIndex(index)}
        selected={itemSelected}>
        <ListItemAvatar>
          <Avatar
            src={item.imagePath}
            style={{ borderRadius: 0, border: "1px solid " + COLOR_WEB_BGR, background: COLOR_PANEL }}
          />
        </ListItemAvatar>
        <ListItemText primary={item.name} secondary={item.link} />
        <div style={{ marginLeft: "1rem" }} />
        <IconButton style={{ color: COLOR_MEDIUM, padding: "0.4rem" }}
          onClick={() => this.edit(id, item, items, updateState)}
        >
          <EditIcon />
        </IconButton>
        <IconButton style={{ color: COLOR_MEDIUM, padding: "0.4rem" }}
          onClick={() => {
            items.map(function (i) { return i.name !== item.name ? i.play = false : ""; });
            item.play = !item.play;
            item.play ? play(item.link) : pause();
            updateState(id, items);
          }}>
          {item.play && playing ? <VolumeUpIcon style={{ color: "red" }} /> : <PlayCircleFilledIcon />}
        </IconButton>
        <IconButton style={{ color: COLOR_MEDIUM, padding: "0.4rem" }}
          onClick={() => {
            if (item.name === items[index].name) {
              pause();
            }
            this.deleteItemImage(id, item, items, updateState);
            items.splice(index, 1);
            updateState(id, items);
          }}>
          <DeleteIcon />
        </IconButton>
      </ListItem>
      {index !== (items.length - 1) ? <Divider /> : <></>}
    </>
  }

  loadImage = (id, e, items, updateState) => {
    if (!e.target.files) {
      return;
    }
    const item = items[this.props.selectedIndex];
    if (!item) {
      return;
    }
    let file = e.target.files[0];
    let reader = new FileReader();
    reader.onloadend = () => {
      item.imagePath = reader.result;
      item.image = file;
      if (file) {
        const tokens = file.name.toLowerCase().split(".");
        const extension = tokens[tokens.length - 1];
        item.filename = item.basePath + item.name + "." + extension;
      }
      updateState(id, items);
    }
    reader.readAsDataURL(file);
  }

  handleDeleteImage = () => {
    this.setState({ isDeleteImageDialogOpen: true });
  }

  deleteItemImage = () => {
    const { id, item, items, updateState } = this.props;
    let path = item.imagePath;
    if (item.filename) {
      path = item.filename;
    }

    if (this.props.defaultImage === path) {
      return;
    }

    deleteImage(path).then(() => {
      item.image = undefined;
      item.imageBak = undefined;
      item.imagePath = this.props.defaultImage;
      item.imagePathBak = this.props.defaultImage;
      updateState(id, items);
      this.setState({ isDeleteImageDialogOpen: false });
    }).catch((e) => {
      console.log(e);
    });
  }

  submitChanges = (id, index, item, items, updateState) => {
    item.edit = !item.edit;
    if (item.name === undefined || (item.name.trim().length === 0 && item.nameBak)) {
      item.name = item.nameBak;
    }
    if (item.link === undefined || (item.link.trim().length === 0 && item.linkBak)) {
      item.link = item.linkBak;
    }
    if (!(item.name && item.name.trim().length > 0 && item.link && item.link.trim().length > 0)) {
      items.splice(index, 1);
    }
    updateState(id, items);
  }

  moveItem = (id, items, from, to, updateState) => {
    if (to === -1) {
      to = items.length - 1;
    } else if (to === items.length) {
      to = 0;
    }
    items.splice(to, 0, items.splice(from, 1)[0]);
    updateState(id, items);
  }

  cancelChanges = (id, index, item, items, updateState) => {
    item.name = item.nameBak;
    item.link = item.linkBak;
    item.imagePath = item.imagePathBak;
    item.edit = !item.edit;
    if (item.imageBak) {
      item.image = item.imageBak;
    }
    if (item.name === undefined || (item.name.trim().length === 0 && item.nameBak)) {
      item.name = item.nameBak;
    }
    if (item.link === undefined || (item.link.trim().length === 0 && item.linkBak)) {
      item.link = item.linkBak;
    }
    if (!(item.name && item.name.trim().length > 0 && item.link && item.link.trim().length > 0)) {
      items.splice(index, 1);
    }
    updateState(id, items);
  }

  getItemEdit(props) {
    const { id, item, items, index, updateState, updateItemState, classes, labels } = props;
    let deleteImage = false;
    if (item.imagePath && item.imagePath !== this.props.defaultImage) {
      deleteImage = true;
    }

    return <>
      <ListItem
        button
        alignItems="flex-start"
        key={index}
        disableRipple={true}
        onClick={() => this.selectIndex(index)}
      >
        <ListItemAvatar>
          <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", marginRight: "1.6rem" }}>
            {this.props.selectedIndex === index && <input
              id="upload"
              type="file"
              accept="image/png, image/jpeg"
              style={{ display: "none" }}
              onChange={(e) => { this.loadImage(id, e, items, updateState) }}
            />}
            <label htmlFor="upload">
              <Avatar
                src={item.imagePath}
                style={{ borderRadius: 0, border: "1px solid " + COLOR_WEB_BGR, background: COLOR_PANEL, cursor: "pointer" }}
              />
            </label>
            {deleteImage && <IconButton style={{ color: COLOR_MEDIUM }}
              onClick={() => { this.handleDeleteImage() }}
            // onClick={() => { this.deleteItemImage(id, item, items, updateState) }}
            >
              <DeleteIcon />
            </IconButton>}
          </div>
        </ListItemAvatar>
        <div style={{ display: "flex", flexDirection: "column", width: "100%" }}>
          {Factory.createPlaylistTextField("name", labels.name, item, items, updateItemState, classes)}
          <div style={{ marginTop: "1rem" }} />
          {Factory.createPlaylistTextField("link", labels.link, item, items, updateItemState, classes)}
          <div style={{ display: "flex", flexDirection: "row", justifyContent: "flex-end" }}>
            <IconButton style={{ color: COLOR_MEDIUM }}
              onClick={() => { this.submitChanges(id, index, item, items, updateState) }}
            >
              <PlaylistAddCheckIcon />
            </IconButton>
            <IconButton style={{ color: COLOR_MEDIUM }}
              onClick={() => { this.moveItem(id, items, index, index - 1, updateState) }}
            >
              <ArrowUpwardIcon />
            </IconButton>
            <IconButton style={{ color: COLOR_MEDIUM }}
              onClick={() => { this.moveItem(id, items, index, index + 1, updateState) }}
            >
              <ArrowDownwardIcon />
            </IconButton>
            <IconButton style={{ color: COLOR_MEDIUM }}
              onClick={() => { this.cancelChanges(id, index, item, items, updateState) }}
            >
              <CloseIcon />
            </IconButton>
          </div>
        </div>
      </ListItem>
      <Divider />
      <ConfirmationDialog
        classes={classes}
        title={labels["delete.image"]}
        message={labels["confirm.delete.image"]}
        yes={labels.yes}
        no={labels.no}
        isDialogOpen={this.state.isDeleteImageDialogOpen}
        yesAction={this.deleteItemImage}
        noAction={() => { this.setState({ isDeleteImageDialogOpen: false }) }}
        cancelAction={() => { this.setState({ isDeleteImageDialogOpen: false }) }}
      />
    </>
  }

  render() {
    const item = this.props.item;
    return item.edit ? this.getItemEdit(this.props) : this.getItemView(this.props);
  }
}
