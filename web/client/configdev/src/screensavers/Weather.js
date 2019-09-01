import React from "react";
import { FormControl } from '@material-ui/core';
import Factory from "../Factory";

function getStyle() {
  return {marginBottom: "1rem"};
}

export default class Weather extends React.Component {
  render() {
    if (!this.props.values || !this.props.lang) {
      return null;
    }

    const { classes, labels, values, updateState, lang } = this.props;
    const params = values[lang]

    return (
      <FormControl component="fieldset">
        {Factory.createTextField("city", params, updateState, getStyle(), classes, labels)}
        {Factory.createTextField("city.label", params, updateState, getStyle(), classes, labels)}
        {Factory.createTextField("country", params, updateState, getStyle(), classes, labels)}
        {Factory.createTextField("region", params, updateState, getStyle(), classes, labels)}
        {Factory.createNumberTextField("update.period", params, updateState, "sec", getStyle(), classes, labels)}
        {Factory.createTextField("unit", params, updateState, getStyle(), classes, labels)}
        {Factory.createCheckbox("military.time.format", params, updateState, labels)}
        {Factory.createCheckbox("use.logging", params, updateState, labels)}
      </FormControl>
    );
  }
}
