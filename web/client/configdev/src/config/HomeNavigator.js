import React from 'react';
import {FormControl} from '@material-ui/core';
import Factory from "../Factory";

export default class HomeNavigator extends React.Component {
  render() {
    const { params, updateState, labels } = this.props;

    return (
        <FormControl>
          {Factory.createCheckbox("back", params, updateState, labels)}
          {Factory.createCheckbox("screensaver", params, updateState, labels)}
          {Factory.createCheckbox("equalizer", params, updateState, labels)}
          {Factory.createCheckbox("language", params, updateState, labels)}
          {Factory.createCheckbox("timer", params, updateState, labels)}
          {Factory.createCheckbox("network", params, updateState, labels)}
          {Factory.createCheckbox("player", params, updateState, labels)}
          {Factory.createCheckbox("about", params, updateState, labels)}
        </FormControl>
    );
  }
}
