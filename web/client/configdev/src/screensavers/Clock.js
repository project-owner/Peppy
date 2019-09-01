import React from "react";
import { FormControl } from '@material-ui/core';
import Factory from "../Factory";

export default class Clock extends React.Component {
  render() {
    if (!this.props.values) {
      return null;
    }

    const style = {width: "10rem", marginBottom: "1rem"};
    const { classes, labels, values, updateState } = this.props;
    return (
      <FormControl component="fieldset">
        {Factory.createNumberTextField("update.period", values, updateState, "sec", style, classes, labels)}
        {Factory.createCheckbox("military.time.format", values, updateState, labels)}
        {Factory.createCheckbox("animated", values, updateState, labels)}
      </FormControl>
    );
  }
}
