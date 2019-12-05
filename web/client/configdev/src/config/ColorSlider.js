import React from 'react';
import Slider from '@material-ui/lab/Slider';
import { TextField } from "@material-ui/core";

export default class ColorSlider extends React.Component {
  handleNumberChange = event => {
    if (isNaN(event.target.value)) {
      return;
    }

    if (Math.trunc(event.target.value) > 255 || Math.trunc(event.target.value) < 0) {
      return;
    }
    this.props.onChange("", event.target.value)
  };

  render() {
    const { label, value, thumbColor, sliderContainerClass, sliderTextClass, notchedOutline } = this.props;

    return (
      <div className={sliderContainerClass} style={{ width: this.props.width }}>
        <div style={{ width: this.props.labelWidth }}>{label}</div>
        <Slider
          classes={{ thumb: thumbColor }}
          value={value}
          aria-labelledby="label"
          style={{color: thumbColor}}
          onChange={this.props.onChange}
          min={0}
          max={255}
        />
        <TextField
          id="outlined-dense"
          value={value}
          onChange={this.handleNumberChange}
          variant="outlined"
          className={sliderTextClass}
          InputProps={{
            style: {
              height: "2.4rem"
            },
            maxLength: 3,
            min: 0,
            max: 255,
            classes: {
              notchedOutline: notchedOutline
            }
          }}
        />
      </div>
    );
  }
}
