import React from "react";
import { FormControl } from '@material-ui/core';
import Factory from "../Factory";

export default class Logo extends React.Component {
  render() {
    if (!this.props.values) {
      return null;
    }

    const style = {width: "10rem", marginBottom: "1.4rem"};
    const { classes, labels, values, updateState } = this.props;
    return (
      <FormControl component="fieldset">
        {Factory.createNumberTextField("update.period", values, updateState, "sec", style, classes, labels)}
        {Factory.createNumberTextField("vertical.size.percent", values, updateState, "percent", style, classes, labels)}
      </FormControl>
    );
  }
}
