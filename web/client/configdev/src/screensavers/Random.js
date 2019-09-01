import React from "react";
import { FormControl } from '@material-ui/core';
import Factory from "../Factory";
import { screensaversSections } from "../tabs/ScreensaversTab"

export default class Random extends React.Component {
  render() {
    if (!this.props.values) {
      return null;
    }

    const style = { width: "10rem", marginBottom: "1rem" };
    const { classes, labels, values, updateState } = this.props;
    const savers = values.savers;

    return (
      <FormControl component="fieldset">
        {Factory.createNumberTextField("update.period", values, updateState, "sec", style, classes, labels)}
        {screensaversSections.map((section) => (
          section !== "random" && Factory.createCheckbox(section, {[section]: savers.includes(section)}, updateState, labels)
        ))}
      </FormControl>
    );
  }
}
