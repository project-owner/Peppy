import React from 'react';
import {FormControl} from '@material-ui/core';
import Factory from "../Factory";

export default class Rotary extends React.Component {
  render() {
    const { classes, params, updateState, labels } = this.props;
    const style = {width: "10rem", marginTop: "1.4rem"};

    return (
        <FormControl component="fieldset" className={classes.formControl}>
          {Factory.createNumberTextField("jitter.filter", params, updateState, "", {...style, marginTop: "0", marginBottom: "1rem"}, classes, labels)}
          {Factory.createNumberTextField("gpio.volume.up", params, updateState, "", style, classes, labels)}
          {Factory.createNumberTextField("gpio.volume.down", params, updateState, "", style, classes, labels)}
          {Factory.createNumberTextField("gpio.mute", params, updateState, "", style, classes, labels)}
          {Factory.createNumberTextField("gpio.move.left", params, updateState, "", style, classes, labels)}
          {Factory.createNumberTextField("gpio.move.right", params, updateState, "", style, classes, labels)}
          {Factory.createNumberTextField("gpio.select", params, updateState, "", style, classes, labels)}          
        </FormControl>
    );
  }
}