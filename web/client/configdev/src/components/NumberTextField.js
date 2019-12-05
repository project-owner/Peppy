import React from 'react';
import { TextField,
  InputAdornment
} from '@material-ui/core';
import {COLOR_DARK} from "../Style";

export default class NumberTextField extends React.Component {
  render() {
    return (
      <div>
        <TextField
          id={this.props.id}
          label={this.props.label}
          variant="outlined"
          style={this.props.style}
          value={this.props.value}
          onChange={event => {this.props.onChange(event.target.id, event.target.value)}}
          InputLabelProps={{
            style: { color: COLOR_DARK }
          }}
          InputProps={{
            style: {
              height: this.props.fieldHeight
            },
            endAdornment: this.props.unit && <InputAdornment position="end">{this.props.unit}</InputAdornment>,
            classes: {
              notchedOutline: this.props.classes.notchedOutline
            }
          }}
        />
      </div>
    );
  }
}
