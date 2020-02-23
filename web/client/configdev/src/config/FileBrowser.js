/* Copyright 2019 Peppy Player peppy.player@gmail.com
 
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
import { FormControl, InputLabel, Select, MenuItem } from '@material-ui/core';
import Factory from "../Factory";

export const fileBrowserSections = [
  "audio.file.extensions", "playlist.file.extensions", "folder.images", "cover.art.folders",
  "show.embedded.images", "folder.image.scale.ratio", "label.text.height.ratio", "hide.folder.name", 
  "rows", "columns", "alignment"
];

export default class FileBrowser extends React.Component {
  handleChange = (event) => {
    this.props.updateState("alignment", event.target.value)
  }

  render() {
    const { classes, params, updateState, labels } = this.props;
    const style1 = { width: "30rem", marginBottom: "1.4rem" };
    const style2 = { width: "14rem", marginBottom: "1rem" };
    const style3 = { width: "5rem", marginTop: "1.2rem" };

    return (
      <FormControl>
        {Factory.createTextField(fileBrowserSections[0], params, updateState, style1, classes, labels)}
        {Factory.createTextField(fileBrowserSections[1], params, updateState, style1, classes, labels)}
        {Factory.createTextField(fileBrowserSections[2], params, updateState, style1, classes, labels)}
        {Factory.createTextField(fileBrowserSections[3], params, updateState, style1, classes, labels)}
        {Factory.createTextField(fileBrowserSections[4], params, updateState, style2, classes, labels)}
        {Factory.createNumberTextField(fileBrowserSections[5], params, updateState, "", style2, classes, labels)}
        {Factory.createNumberTextField(fileBrowserSections[6], params, updateState, "", style2, classes, labels)}
        {Factory.createCheckbox(fileBrowserSections[7], params, updateState, labels)}
        {Factory.createNumberTextField(fileBrowserSections[10], params, updateState, "", style3, classes, labels)}
        {Factory.createNumberTextField(fileBrowserSections[11], params, updateState, "", style3, classes, labels)}
        <FormControl style={{width: "10rem", marginTop: "1.2rem"}}>
          <InputLabel shrink>{labels["alignment"]}</InputLabel>
          <Select
            value={params["alignment"]}
            onChange={this.handleChange}
          >
            <MenuItem value={"center"}>{labels["center"]}</MenuItem>
            <MenuItem value={"left"}>{labels["left"]}</MenuItem>
            <MenuItem value={"right"}>{labels["right"]}</MenuItem>
          </Select>
        </FormControl>
      </FormControl>
    );
  }
}
