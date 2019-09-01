import React from "react";
import { withStyles } from "@material-ui/core/styles";
import styles from "./Style";
import styled, { keyframes } from 'styled-components'

const zoomer = keyframes`
  0%   { opacity: 0; transform: scale(1, 1)}
  75%  { opacity: 1; transform: scale(1, 1)}
  100% { opacity: 0; transform: scale(0, 0) rotateZ(-15deg);}
`;

const Shutdown = styled.div`
  opacity:0;  
  animation: ${zoomer} 2s ease-out;
`;

const waiver = keyframes`
  0%   { opacity: 0.2; }
  50%  { opacity: 1.0; }
  100% { opacity: 0.2; }
`;

const Reboot = styled.div`
  opacity:0;  
  animation: ${waiver} 2s infinite linear;
`;

class Template extends React.Component {
  render() {
    const { classes, hide, labels, reboot, shutdown } = this.props;
    const displayValue = hide ? { display: "none" } : null;

    return (
      <>
        <div className={classes.topContainer} style={displayValue}>
          <div className={classes.leftContainer}>
            <div className={classes.logoContainer}>
              {this.props.logo}
            </div>
            <div>
              {this.props.navigator}
            </div>
          </div>
          <div className={classes.rightContainer}>
            <div className={classes.headerContainer}>
              <div className={classes.headerLanguage}>
                {this.props.headerLanguage}
              </div>
              <div className={classes.headerTabs}>
                {this.props.headerTabs}
              </div>
            </div>
            <div className={classes.content}>
              <div className={classes.contentMargin}>
                {this.props.content}
              </div>
            </div>
            <div className={classes.footerContainer}>
              <div className={classes.footerProgress}>
                {this.props.footerProgress}
              </div>
              <div className={classes.footerButtons}>
                {this.props.footerButtons}
              </div>
              <div className={classes.footerCopyright}>
                {this.props.footerCopyright}
              </div>
            </div>
            <div>
              {this.props.notification}
            </div>
            <div>
              {this.props.rebootDialog}
            </div>
            <div>
              {this.props.saveAndRebootDialog}
            </div>
            <div>
              {this.props.shutdownDialog}
            </div>
            <div>
              {this.props.saveAndShutdownDialog}
            </div>
          </div>
        </div>
        {hide && reboot && <Reboot className={classes.actionText}>{labels["rebooting"]}</Reboot>}
        {hide && shutdown && <Shutdown className={classes.actionText}>{labels["see.you.later"]}</Shutdown>}
      </>
    );
  }
}

export default withStyles(styles)(Template);
