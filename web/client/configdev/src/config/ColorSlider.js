import React from 'react';
import Slider from '@material-ui/lab/Slider';
import { TextField } from "@material-ui/core";
import NumberFormat from 'react-number-format';
import { withStyles } from "@material-ui/core/styles";

const styles = () => ({
  red: {
    backgroundColor: "red"
  },
  green: {
    backgroundColor: "green"
  },
  blue: {
    backgroundColor: "blue"
  }
});

class ColorSlider extends React.Component {
  handleNumberChange = event => {
    if (Math.trunc(event.target.value) > 255 || Math.trunc(event.target.value) < 0) {
      return;
    }
    this.props.onChange("", event.target.value)
  };

  render() {
    const { classes, label, value, thumbColor } = this.props;

    return (
      <div className={classes.sliderContainer} style={{ width: this.props.width }}>
        <div style={{ width: this.props.labelWidth }}>{label}</div>
        <Slider
          classes={{ thumb: classes[thumbColor] }}
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
          className={classes.sliderText}
          inputProps={{
            style: {
              height: "0.2rem"
            },
            inputComponent: NumberFormat,
            maxLength: 3,
            min: 0,
            max: 255
          }}
        />
      </div>
    );
  }
}
export default withStyles(styles)(ColorSlider);
