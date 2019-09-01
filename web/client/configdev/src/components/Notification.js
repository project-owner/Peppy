import React from "react";
import { withStyles } from "@material-ui/core/styles";
import styles from "../Style";
import { Snackbar } from "@material-ui/core";
import SnackbarContent from '@material-ui/core/SnackbarContent';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import ErrorIcon from '@material-ui/icons/Error';
import InfoIcon from '@material-ui/icons/Info';
import WarningIcon from '@material-ui/icons/Warning';

class Notification extends React.Component {
  render() {
    const { classes, message, variant } = this.props;

    const variants = {
      success: { icon: <CheckCircleIcon/>, bgr: classes.success },
      warning: { icon: <WarningIcon/>, bgr: classes.warning },
      error: { icon: <ErrorIcon/>, bgr: classes.error },
      info: { icon: <InfoIcon/>, bgr: classes.info }
    };

    return (
      <Snackbar
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right', }}
        open={this.props.openSnack}
        autoHideDuration={2000}
        onClose={this.props.handleSnackClose}
      >
        <SnackbarContent
          className={variants[variant].bgr}
          aria-describedby="client-snackbar"
          message={
            <span id="client-snackbar" className={classes.notificationMsg}>
              <span className={classes.notificationIcon}>{variants[variant].icon}</span>
              {message}
            </span>
          }
          action={[
            <IconButton
              key="close"
              aria-label="Close"
              color="inherit"
              className={classes.close}
              onClick={this.props.handleSnackClose}
            >
              <CloseIcon />
            </IconButton>
          ]}
        />
      </Snackbar>
    );
  }
}

export default withStyles(styles)(Notification);
