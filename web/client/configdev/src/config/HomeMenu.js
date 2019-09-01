import React from 'react';
import {FormControl} from '@material-ui/core';
import Factory from "../Factory";

export default class HomeMenu extends React.Component {
  render() {
    const { params, updateState, labels } = this.props;
    
    return (
        <FormControl>
          {Factory.createCheckbox("radio", params, updateState, labels)}
          {Factory.createCheckbox("audio-files", params, updateState, labels)}
          {Factory.createCheckbox("audiobooks", params, updateState, labels)}
          {Factory.createCheckbox("podcasts", params, updateState, labels)}
          {Factory.createCheckbox("stream", params, updateState, labels)}
          {Factory.createCheckbox("cd-player", params, updateState, labels)}
        </FormControl>
    );
  }
}
