import React from 'react';
import {FormControl} from '@material-ui/core';
import Factory from "../Factory";

export const logSections = [
  "file.logging", "log.filename", "console.logging", "enable.stdout", "show.mouse.events"
];

export default class Logging extends React.Component {
  render() {
    const { classes, params, updateState, labels } = this.props;
    const s = {width: "16rem", marginTop: "0.8rem", marginBottom: "0.6rem"};

    return (
      <FormControl>
        {Factory.createCheckbox(logSections[0], params, updateState, labels)}
        {Factory.createTextField(logSections[1], params, updateState, s, classes, labels)}
        {Factory.createCheckbox(logSections[2], params, updateState, labels)}
        {Factory.createCheckbox(logSections[3], params, updateState, labels)}
        {Factory.createCheckbox(logSections[4], params, updateState, labels)}        
      </FormControl>
    );
  }
}
