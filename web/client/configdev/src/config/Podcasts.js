import React from 'react';
import { FormControl } from '@material-ui/core';
import Factory from "../Factory";

export default class Podcasts extends React.Component {
  render() {
    const { classes, params, updateState, labels } = this.props;
    
    return (
      <FormControl>
        {Factory.createTextField("podcasts.folder", params, updateState, { width: "20rem" }, classes, labels)}
      </FormControl>
    );
  }
}
