import React from 'react';
import { FormControl } from '@material-ui/core';
import Factory from "../Factory";

export default class VoiceAssistant extends React.Component {
  
  render() {
    const { classes, params, updateState, labels } = this.props;
    const style = {marginBottom: "1.4rem"};
    
    return (
      <FormControl>
        {Factory.createTextField("type", params, updateState, style, classes, labels)}
        {Factory.createTextField("credentials", params, updateState, style, classes, labels)}
        {Factory.createTextField("device.model.id", params, updateState, style, classes, labels)}
        {Factory.createTextField("device.id", params, updateState, style, classes, labels)}
        {Factory.createNumberTextField("command.display.time", params, updateState, "sec", style, classes, labels)}
      </FormControl>
    );
  }
}
