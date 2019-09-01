import React from 'react';
import { FormControl } from '@material-ui/core';
import Factory from "../Factory";

export default class Font extends React.Component {
  render() {
    const { classes, params, updateState, labels } = this.props;
    const style = { width: "12rem" };
    
    return (
      <FormControl>
        {Factory.createTextField("font.name", params, updateState, style, classes, labels)}
      </FormControl>
    );
  }
}
