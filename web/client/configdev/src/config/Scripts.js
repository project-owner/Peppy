import React from 'react';
import { FormControl } from '@material-ui/core';
import Factory from "../Factory";

export default class Scripts extends React.Component {  
  render() {
    const { classes, params, updateState, labels } = this.props;
    const style = {width: "14rem", marginBottom: "1.4rem"};

    return (
      <FormControl>
        {Factory.createTextField("startup.script.name", params, updateState, style, classes, labels)}
        {Factory.createTextField("shutdown.script.name", params, updateState, style, classes, labels)}
      </FormControl>
    );
  }
}


