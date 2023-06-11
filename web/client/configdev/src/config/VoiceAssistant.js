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

import React from 'react';
import { FormControl, List, Paper } from '@material-ui/core';
import Factory from "../Factory";
import VoskModel from "../components/VoskModel";

export default class VoiceAssistant extends React.Component {
  render() {
    const { classes, params, updateState, labels, voskModels, downloadVoskModel, setCurrentVoskModel,
      handleDeleteVoskModelDialog, downloadVoskModelProgress, voskModelDownloading } = this.props;
    const style = {marginBottom: "1.4rem"};
    const style1 = {marginTop: "1.4rem", width: "24rem"};

    return (
      <FormControl>
        {Factory.createTextField("type", params.vaconfig, updateState, style, classes, labels, true)}
        {Factory.createCheckbox("translate.names", params.vaconfig, updateState, labels)}
        {Factory.createTextField("folder", params.vaconfig, updateState, style1, classes, labels)}

        <h4 className={classes.colorsHeader}>{labels["vosk.models"]}</h4>

        <div>
          {voskModels && <Paper>
            <div style={{ height: "24rem", width: "36rem", overflow: "auto" }} ref={element => (this.container = element)}>
              <List>
                {voskModels.length > 0 && voskModels.map(function (item, index) {
                  return <VoskModel
                    id={index}
                    key={index}
                    labels={labels}
                    name={item.name}
                    size={item.size}
                    size_bytes={item.size_bytes}
                    unit={item.unit}
                    current={item.current}
                    remote={item.remote}
                    url={item.url}
                    downloadModel={downloadVoskModel}
                    setCurrentModel={setCurrentVoskModel}
                    handleDeleteVoskModelDialog={handleDeleteVoskModelDialog}
                    downloadVoskModelProgress={downloadVoskModelProgress}
                    voskModelDownloading={voskModelDownloading}
                  />
                })}
              </List>
            </div>
          </Paper>}
        </div>
      </FormControl>
    );
  }
}
