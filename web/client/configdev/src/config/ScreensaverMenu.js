import React from 'react';
import {FormControl} from '@material-ui/core';
import Factory from "../Factory";

export default class ScreensaverMenu extends React.Component {
  render() {
    const { params, updateState, labels } = this.props;

    return (
        <FormControl>
          {Factory.createCheckbox("clock", params, updateState, labels)}
          {Factory.createCheckbox("logo", params, updateState, labels)}
          {Factory.createCheckbox("slideshow", params, updateState, labels)}
          {Factory.createCheckbox("peppymeter", params, updateState, labels)}
          {Factory.createCheckbox("peppyweather", params, updateState, labels)}
          {Factory.createCheckbox("spectrum", params, updateState, labels)}
          {Factory.createCheckbox("lyrics", params, updateState, labels)}
          {Factory.createCheckbox("random", params, updateState, labels)}
        </FormControl>
    );
  }
}