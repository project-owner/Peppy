/* Copyright 2019-2023 Peppy Player peppy.player@gmail.com
 
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
import { Checkbox, FormControlLabel, TextField, TextareaAutosize, InputAdornment } from '@material-ui/core';
import NumberTextField from "./components/NumberTextField";
import { COLOR_DARK } from "./Style";
import PlaylistEditor from "./components/PlaylistEditor";

const FIELD_HEIGHT = "3.2rem";

export default class Factory {
  static setWidth(style, value, width) {
    let w;
    if (width) {
      w = width;
      style.width = w;
    } else {
      w = style.width;
    }
    
    if (!w) {
      style.width = "200px";
      if (value && value.length > 20) {
        style.width = value.length * 9 + "px";
      }
    }
  }

  static createTextField(id, props, onChange, style, classes, labels, disabled, index, type, required, unit=null) {
    if (!labels) {
      return null;
    }

    const value = props[id];
    this.setWidth(style, value);
    return <TextField
      id={id}
      label={labels[id]}
      variant="outlined"
      fullWidth
      type={type ? type : "text"}
      value={value}
      required={required}
      InputLabelProps={{
        style: { color: COLOR_DARK }
      }}
      InputProps={{
        style: {
          height: FIELD_HEIGHT
        },
        classes: {
          notchedOutline: classes.notchedOutline
        },
        endAdornment: unit !== null && <InputAdornment position="end">{unit}</InputAdornment>,
        readOnly: Boolean(disabled)
      }}
      onChange={event => { onChange(event.target.id, event.target.value, index) }}
      style={style}
    />;
  }

  static createPlaylistTextField(fieldName, label, item, items, updateItemState, classes) {
    let value = "";
    if (item[fieldName]) {
      value = item[fieldName];
    }

    return <TextField
      label={label}
      variant="outlined"
      fullWidth
      value={value}
      InputLabelProps={{
        style: { color: COLOR_DARK },
        shrink: true
      }}
      InputProps={{
        style: {
          height: FIELD_HEIGHT
        },
        classes: {
          notchedOutline: classes.notchedOutline
        }
      }}
      onChange={
        event => {
          updateItemState(item, fieldName, event.target.value, items);
        }
      }
    />;
  }

  static createTextArea(id, props, onChange, style, classes, labels, disabled, rows, txt, index) {
    if (!labels) {
      return null;
    }

    const value = props[id] || txt;
    return <TextField
      id={id}
      label={labels[id]}
      variant="outlined"
      multiline={true}
      minRows={ rows || 30 }
      maxRows={ rows || 30 }
      fullWidth
      value={value}
      InputLabelProps={{
        style: { color: COLOR_DARK }
      }}
      InputProps={{
        classes: {
          notchedOutline: classes.notchedOutline
        },
        readOnly: Boolean(disabled),
        spellCheck: false
      }}
      onChange={event => { onChange(event.target.id, event.target.value, index) }}
      style={style}
    />;
  }

  static createResizableTextArea(id, props, style) {
    const value = props[id];
    return <TextareaAutosize
      id={id}
      variant="outlined"
      minRows={40}
      maxRows={40}
      value={value}
      style={style}
    />;
  }

  static createPlaylist(id, playlist, text, play, pause, uploadPlaylist, playing, updateState, updateItemState, 
    updateText, classes, labels, addButtonLabel, defaultImage, basePath) {
    return <PlaylistEditor
      id={id}
      items={playlist}
      text={text}
      basePath={basePath}
      updateState={updateState}
      updateItemState={updateItemState}
      updateText={updateText}
      play={play}
      pause={pause}
      playing={playing}
      classes={classes}
      labels={labels}
      addButtonLabel={addButtonLabel}
      defaultImage={defaultImage}
      upload={uploadPlaylist}
    />
  }

  static createNumberTextField(id, props, onChange, unit, style, classes, labels, label, width) {
    if (!labels) {
      return null;
    }

    const value = props[id];
    this.setWidth(style, value, width);
    
    return <NumberTextField
      id={id}
      label={label ? label : labels[id]}
      value={value}
      onChange={onChange}
      unit={labels[unit]}
      style={style}
      classes={classes}
      fieldHeight={FIELD_HEIGHT}
    />;
  }

  static createCheckbox(id, value, onChange, labels, index) {
    if (!labels) {
      return null;
    }

    const checked = value[id];
    let label = labels[id];
    if (label === undefined) {
      label = id;
    }
    
    return <FormControlLabel
      key={index}
      control={
        <Checkbox
          id={id}
          color="primary"
          classes={this.checked}
          style={{
            color: "rgb(20, 90, 100)"
          }}
          checked={checked}
          onChange={event => { onChange(event.target.id, event.target.checked) }}
        />
      }
      label={label}
    />;
  }
}