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
import { Button, List, Paper, IconButton, TextField } from '@material-ui/core';
import PlaylistItem from "./PlaylistItem";
import { flexbox } from "@material-ui/system";
import PlaylistAddIcon from '@material-ui/icons/PlaylistAdd';
import ViewListIcon from '@material-ui/icons/ViewList';
import ViewHeadlineIcon from '@material-ui/icons/ViewHeadline';
import { COLOR_MEDIUM } from "../Style";

const EDITOR_LIST = "list";
const EDITOR_TEXT = "text";

export default class PlaylistEditor extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      id: props.id,
      selectedIndex: undefined,
      items: props.items,
      updateState: props.updateState,
      updateItemState: props.updateItemState,
      play: props.play,
      pause: props.pause,
      playing: props.playing,
      editorMode: EDITOR_LIST
    }
    this.addNewItem = this.addNewItem.bind(this);
    this.setSelectedIndex = this.setSelectedIndex.bind(this);
  }

  setSelectedIndex = (index) => {
    this.setState({ selectedIndex: index });
  }

  addNewItem(id, items, updateState) {
    let item = {
      name: undefined,
      imagePath: this.props.defaultImage,
      link: undefined,
      play: false,
      edit: true,
      image: undefined,
      basePath: this.props.basePath
    };
    if (this.state.selectedIndex) {
      items.splice(this.state.selectedIndex, 0, item);
      updateState(id, items);      
    } else {
      if (items.length > 0) {
        items.unshift(item);
        updateState(id, items);
        this.container.scrollTop = this.container.style.scrollHeight;
      } else {
        items = [item];
        updateState(id, items);
      }
    }
  }

  setMode(mode) {
    this.setState({ editorMode: mode });
  }

  render() {
    const id = this.state.id;
    const items = this.props.items;
    const updateState = this.state.updateState;
    const updateItemState = this.state.updateItemState;
    const updateText = this.props.updateText;
    const play = this.state.play;
    const pause = this.state.pause;
    const playing = this.props.playing;
    const selected = this.state.selectedIndex;
    const setSelected = this.setSelectedIndex;
    const classes = this.props.classes;
    const labels = this.props.labels;
    const addButtonLabel = this.props.addButtonLabel;
    const defaultImage = this.props.defaultImage;
    let text = this.props.text;
    if (!text) {
      text = "";
    }

    return (
      <div style={{ display: flexbox, flexDirection: "column" }}>
        <span style={{ width: "100%", display: "flex", flexDirection: "row", justifyContent: "space-between" }}>
          <div>
            {
              this.state.editorMode === EDITOR_LIST && <Button
                variant="contained"
                className={classes.addButton}
                style={{ justifyContent: "flex-start" }}
                onClick={() => { this.addNewItem(id, items, updateState) }}
              >
                {addButtonLabel}
                <PlaylistAddIcon style={{ marginLeft: "1rem" }} />
              </Button>
            }
          </div>
          <div style={{ display: "flex", justifyContent: "flex-end", alignItems: "center" }}>
            <IconButton style={{ color: COLOR_MEDIUM }}
              onClick={() => { this.setMode(EDITOR_LIST) }}
            >
              <ViewListIcon />
            </IconButton>
            <IconButton style={{ color: COLOR_MEDIUM }}
              onClick={() => { this.setMode(EDITOR_TEXT) }}
            >
              <ViewHeadlineIcon />
            </IconButton>
          </div>
        </span>
        {this.state.editorMode === EDITOR_LIST && <Paper>
          <div style={{ height: "35rem", width: "34rem", overflow: "auto" }} ref={element => (this.container = element)}>
            <List>
              {items.length > 0 && items.map(function (item, index) {
                return <PlaylistItem
                  id={id}
                  key={index}
                  item={item}
                  items={items}
                  index={index}
                  updateState={updateState}
                  updateItemState={updateItemState}
                  play={play}
                  pause={pause}
                  playing={playing}
                  selectedIndex={selected}
                  selectItem={setSelected}
                  classes={classes}
                  labels={labels}
                  defaultImage={defaultImage}
                />
              })}
            </List>
          </div>
        </Paper>}
        {this.state.editorMode === EDITOR_TEXT &&
          <TextField
            id={id}
            variant="outlined"
            rows={28}
            rowsMax={28}
            multiline={true}
            fullWidth={true}
            value={text}
            style={{ width: "34rem", overflow: "auto", overflowWrap: "normal" }}
            InputProps={{
              classes: {
                notchedOutline: classes.notchedOutline,
              }
            }}
            onChange={event => { updateText(event.target.value) }}
          />
        }
      </div>
    );
  }
}
