import React from "react";
import { Button } from "@material-ui/core";

export default class Buttons extends React.Component {
  render() {
    if(!this.props.lang) {
      return null;
    }

    const { classes, labels, buttonsDisabled, save, openRebootDialog, openShutdownDialog } = this.props;
    return (
      <>
        <Button disabled={buttonsDisabled} variant="contained" className={classes.button} onClick={save}>{labels.save}</Button>
        <Button disabled={buttonsDisabled} variant="contained" className={classes.button} onClick={openRebootDialog}>{labels.reboot}</Button>
        <Button disabled={buttonsDisabled} variant="contained" className={classes.button} onClick={openShutdownDialog}>{labels.shutdown}</Button>
      </>
    );
  }
}
