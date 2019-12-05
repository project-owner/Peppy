import React from 'react';
import {FormControl} from '@material-ui/core';
import Factory from "../Factory";

export default class LanguagesMenu extends React.Component {
  render() {
    const { params, updateState, labels } = this.props;

    return (
        <FormControl>
          {Factory.createCheckbox("English-USA", params, updateState, labels)}
          {Factory.createCheckbox("German", params, updateState, labels)}
          {Factory.createCheckbox("French", params, updateState, labels)}
          {Factory.createCheckbox("Italian", params, updateState, labels)}
          {Factory.createCheckbox("Spanish", params, updateState, labels)}
          {Factory.createCheckbox("Russian", params, updateState, labels)}
        </FormControl>
    );
  }
}
