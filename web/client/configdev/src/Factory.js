import React from "react";
import { Checkbox, FormControlLabel, TextField } from '@material-ui/core';
import NumberTextField from "./components/NumberTextField";
import { COLOR_DARK } from "./Style";
import PlaylistEditor from "./components/PlaylistEditor";

const FIELD_HEIGHT = "3.2rem";

export default class Factory {
  static setWidth(style, value) {
    let w = style.width;
    if (!w) {
      style.width = "200px";
      if (value && value.length > 20) {
        style.width = value.length * 9 + "px";
      }
    }
  }

  static createTextField(id, props, onChange, style, classes, labels) {
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
      value={value}
      InputLabelProps={{
        style: { color: COLOR_DARK }
      }}
      InputProps={{
        style: {
          height: FIELD_HEIGHT
        },
        classes: {
          notchedOutline: classes.notchedOutline,
        }
      }}
      onChange={event => { onChange(event.target.id, event.target.value) }}
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
        style: { color: COLOR_DARK }
      }}
      InputProps={{
        style: {
          height: FIELD_HEIGHT
        },
        classes: {
          notchedOutline: classes.notchedOutline,
        }
      }}
      onChange={
        event => {
          updateItemState(item, fieldName, event.target.value, items);
        }
      }
    />;
  }

  static createTextArea(id, props, onChange, style, classes, labels) {
    if (!labels) {
      return null;
    }

    const value = props[id];
    return <TextField
      id={id}
      label={labels[id]}
      variant="outlined"
      multiline={true}
      rows={30}
      rowsMax={30}
      fullWidth
      value={value}
      InputLabelProps={{
        style: { color: COLOR_DARK }
      }}
      InputProps={{
        classes: {
          notchedOutline: classes.notchedOutline,
        }
      }}
      onChange={event => { onChange(event.target.id, event.target.value) }}
      style={style}
    />;
  }

  static createPlaylist(id, playlist, text, play, pause, playing, updateState, updateItemState, updateText,
    classes, labels, addButtonLabel, defaultImage, basePath) {
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
    />
  }

  static createNumberTextField(id, props, onChange, unit, style, classes, labels) {
    if (!labels) {
      return null;
    }

    const value = props[id];
    this.setWidth(style, value);
    return <NumberTextField
      id={id}
      label={labels[id]}
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
      label={labels[id]}
    />;
  }
}