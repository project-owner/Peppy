import React from 'react';
import {FormControl} from '@material-ui/core';
import Factory from "../Factory";

export default class WebServer extends React.Component {
  render() {
    const { classes, params, updateState, labels } = this.props;
    const s = {width: "10rem", marginBottom: "0.6rem"};

    return (
        <FormControl component="fieldset" className={classes.formControl}>
          {Factory.createNumberTextField("http.port", params, updateState, "", s, classes, labels)}
          {Factory.createCheckbox("https", params, updateState, labels)}
        </FormControl>
    );
  }
}
