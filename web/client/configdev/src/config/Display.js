import React from "react";
import { FormControl } from '@material-ui/core';
import Factory from "../Factory";

export default class Display extends React.Component {
  render() {
    const { classes, params, updateState, labels } = this.props;
    const style = {width: "10rem", marginBottom: "1rem"};

    return (
      <FormControl component="fieldset">
        {Factory.createNumberTextField("width", params, updateState, "pixels", style, classes, labels)}
        {Factory.createNumberTextField("height", params, updateState, "pixels", style, classes, labels)}
        {Factory.createNumberTextField("depth", params, updateState, "bits", style, classes, labels)}
        {Factory.createNumberTextField("frame.rate", params, updateState, "frames.sec", style, classes, labels)}
        {Factory.createCheckbox("hdmi", params, updateState, labels)}
        {Factory.createCheckbox("no.frame", params, updateState, labels)}
        {Factory.createCheckbox("flip.touch.xy", params, updateState, labels)}
        {Factory.createCheckbox("multi.touch", params, updateState, labels)}
      </FormControl>
    );
  }
}
