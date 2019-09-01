import React from 'react';
import {FormControl, FormGroup} from '@material-ui/core';
import Factory from "../Factory";

export default class Usage extends React.Component {
  render() {
    const { classes, params, updateState, labels } = this.props;

    return (
      <div>
        <FormControl component="fieldset">
          <FormGroup column="true">
            {Factory.createCheckbox("touchscreen", params, updateState, labels)}
            {Factory.createCheckbox("mouse", params, updateState, labels)}
            {Factory.createCheckbox("lirc", params, updateState, labels)}
            {Factory.createCheckbox("rotary.encoders", params, updateState, labels)}
            {Factory.createCheckbox("web", params, updateState, labels)}
            {Factory.createCheckbox("stream.server", params, updateState, labels)}
            {Factory.createCheckbox("browser.stream.player", params, updateState, labels)}
          </FormGroup>
          {Factory.createNumberTextField("long.press.time.ms", params, updateState, 
            "ms", {width: "10rem", marginTop: "1rem"}, classes, labels
          )}
        </FormControl>
        <FormControl component="fieldset">
          <FormGroup column="true">
            {Factory.createCheckbox("voice.assistant", params, updateState, labels)}
            {Factory.createCheckbox("headless", params, updateState, labels)}
            {Factory.createCheckbox("vu.meter", params, updateState, labels)}
            {Factory.createCheckbox("album.art", params, updateState, labels)}
            {Factory.createCheckbox("auto.play", params, updateState, labels)}
            {Factory.createCheckbox("poweroff", params, updateState, labels)}
          </FormGroup>
        </FormControl>
      </div>
    );
  }
}
