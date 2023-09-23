/* Copyright 2019-2023 Peppy Player peppy.player@gmail.com
 
This file is part of Peppy Player.
 
Peppy Player is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
Peppy Player is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with Peppy Player. If not, see <http://www.gnu.org/licenses/>.
*/

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
              <div className={classes.headerSubTabs}>
                {this.props.headerSubTabs}
              </div>
            </div>
            <div className={classes.content}>
              <div className={classes.contentMargin}>
                {this.props.content}
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
            <div>
              {this.props.setDefaultsAndRebootDialog}
            </div>
            <div>
              {this.props.deleteVoskModelDialog}
            </div>
            <div>
              {this.props.deletePlaylistDialog}
            </div>
            <div>
              {this.props.createPlaylistDialog}
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
