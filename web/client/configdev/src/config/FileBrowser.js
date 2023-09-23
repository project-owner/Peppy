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
import { FormControl, InputLabel, Select, MenuItem } from '@material-ui/core';
import Factory from "../Factory";

export const fileBrowserSections = [
  "audio.file.extensions", "playlist.file.extensions", "folder.images", "cover.art.folders", "image.file.extensions", "show.embedded.images",
  "image.area", "image.size", "image.size.without.label", "icon.size", "hide.folder.name", "list.view.rows", "list.view.columns", "alignment", "sort.by.type",
  "wrap.lines", "horizontal.layout", "font.height", "padding", "enable.folder.images", "enable.embedded.images", "enable.image.file.icon",
  "ascending", "file.types", "icon.view.rows", "icon.view.columns", "enable.button.home", "enable.button.config", "enable.button.playlist",
  "enable.button.user", "enable.button.root", "enable.button.parent"
];

export default class FileBrowser extends React.Component {
  handleChange = (event) => {
    this.props.updateState("alignment", event.target.value)
  }

  render() {
    const { classes, params, updateState, labels } = this.props;
    const style1 = { width: "30rem", marginBottom: "1.4rem" };
    const style2 = { width: "16rem", marginBottom: "1rem" };
    const style3 = { width: "15rem", marginTop: "1.2rem" };
    const style4 = { width: "16rem", marginTop: "0.3rem", marginBottom: "1rem" };
    const style5 = { width: "15rem" };
    const style6 = { width: "10rem", marginTop: "1.2rem" };
    const style7 = { width: "10rem", marginTop: "1.2rem", marginBottom: "1rem" };

    labels["list.view.rows"] = labels["list.view"] + ". " + labels["rows"];
    labels["list.view.columns"] = labels["list.view"] + ". " + labels["columns"];
    labels["icon.view.rows"] = labels["icon.view"] + ". " + labels["rows"];
    labels["icon.view.columns"] = labels["icon.view"] + ". " + labels["columns"];

    return (
      <div>
        <FormControl>
          {Factory.createTextField("audio.file.extensions", params, updateState, style1, classes, labels)}
          {Factory.createTextField("playlist.file.extensions", params, updateState, style1, classes, labels)}
          {Factory.createTextField("folder.images", params, updateState, style1, classes, labels)}
          {Factory.createTextField("cover.art.folders", params, updateState, style1, classes, labels)}
          {Factory.createTextField("image.file.extensions", params, updateState, style1, classes, labels)}
          {Factory.createTextField("show.embedded.images", params, updateState, style2, classes, labels)}
          {Factory.createTextField("file.types", params, updateState, style2, classes, labels)}
          {Factory.createNumberTextField("image.area", params, updateState, "percent", style4, classes, labels)}
          {Factory.createNumberTextField("image.size", params, updateState, "percent", style4, classes, labels)}
          {Factory.createNumberTextField("image.size.without.label", params, updateState, "percent", style4, classes, labels)}
          {Factory.createNumberTextField("icon.size", params, updateState, "percent", style4, classes, labels)}
        </FormControl>
        <FormControl style={{marginLeft:"2rem"}}>
          {Factory.createNumberTextField("list.view.rows", params, updateState, "", style5, classes, labels)}
          {Factory.createNumberTextField("list.view.columns", params, updateState, "", style3, classes, labels)}
          {Factory.createNumberTextField("icon.view.rows", params, updateState, "", style3, classes, labels)}
          {Factory.createNumberTextField("icon.view.columns", params, updateState, "", style3, classes, labels)}
          <FormControl style={{width: "10rem", marginTop: "1.2rem", marginBottom: "1.2rem"}}>
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
          {Factory.createCheckbox("sort.by.type", params, updateState, labels)}
          {Factory.createCheckbox("wrap.lines", params, updateState, labels)}
          {Factory.createCheckbox("horizontal.layout", params, updateState, labels)}
          {Factory.createCheckbox("ascending", params, updateState, labels)}
          {Factory.createNumberTextField("font.height", params, updateState, "percent", style6, classes, labels)}
          {Factory.createNumberTextField("padding", params, updateState, "percent", style7, classes, labels)}
          {Factory.createCheckbox("enable.folder.images", params, updateState, labels)}
          {Factory.createCheckbox("enable.embedded.images", params, updateState, labels)}
          {Factory.createCheckbox("enable.image.file.icon", params, updateState, labels)}
          {Factory.createCheckbox("hide.folder.name", params, updateState, labels)}
        </FormControl>
        <FormControl style={{marginLeft:"2rem"}}>
          {Factory.createCheckbox("enable.button.home", params, updateState, labels)}
          {Factory.createCheckbox("enable.button.config", params, updateState, labels)}
          {Factory.createCheckbox("enable.button.playlist", params, updateState, labels)}
          {Factory.createCheckbox("enable.button.user", params, updateState, labels)}
          {Factory.createCheckbox("enable.button.root", params, updateState, labels)}
          {Factory.createCheckbox("enable.button.parent", params, updateState, labels)}
        </FormControl>
      </div>
    );
  }
}
