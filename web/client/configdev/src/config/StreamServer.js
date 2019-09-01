import React from 'react';
import {FormControl} from '@material-ui/core';
import Factory from "../Factory";

export default class StreamServer extends React.Component {
  render() {
    const { classes, params, updateState, labels } = this.props;

    return (
        <FormControl component="fieldset" className={classes.formControl}>
          {Factory.createNumberTextField("stream.server.port", params, updateState, "", {width: "10rem"}, classes, labels)}
        </FormControl>
    );
  }
}
