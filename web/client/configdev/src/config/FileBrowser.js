import React from 'react';
import { FormControl } from '@material-ui/core';
import Factory from "../Factory";

export const fileBrowserSections = [
  "audio.file.extensions", "playlist.file.extensions", "folder.images", "cover.art.folders", 
  "folder.image.scale.ratio", "hide.folder.name", "auto.play.next.track", "cyclic.playback"
];

export default class FileBrowser extends React.Component {
  render() {
    const { classes, params, updateState, labels } = this.props;
    const style1 = { width: "30rem", marginBottom: "1.4rem" };
    const style2 = { width: "14rem", marginBottom: "1rem" };

    return (
      <FormControl>
        {Factory.createTextField(fileBrowserSections[0], params, updateState, style1, classes, labels)}
        {Factory.createTextField(fileBrowserSections[1], params, updateState, style1, classes, labels)}
        {Factory.createTextField(fileBrowserSections[2], params, updateState, style1, classes, labels)}
        {Factory.createTextField(fileBrowserSections[3], params, updateState, style1, classes, labels)}
        {Factory.createNumberTextField(fileBrowserSections[4], params, updateState, "", style2, classes, labels)}
        {Factory.createCheckbox(fileBrowserSections[5], params, updateState, labels)}
        {Factory.createCheckbox(fileBrowserSections[6], params, updateState, labels)}
        {Factory.createCheckbox(fileBrowserSections[7], params, updateState, labels)}
      </FormControl>
    );
  }
}
