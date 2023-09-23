/* Copyright 2023 Peppy Player peppy.player@gmail.com

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

import * as React from 'react';
import Grid from '@mui/material/Grid';
import Button from '@mui/material/Button';
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Chip from '@mui/material/Chip';
import { IconButton } from '@material-ui/core';
import { COLOR_CHIP, COLOR_CHIP_CONTRAST, COLOR_MEDIUM, COLOR_DARK_LIGHT } from "../Style";
import DesktopWindowsIcon from '@material-ui/icons/DesktopWindows';
import PersonOutlineIcon from '@material-ui/icons/PersonOutline';
import KeyboardArrowRightOutlinedIcon from '@material-ui/icons/KeyboardArrowRightOutlined';
import FileList from '../components/FileList';
import Playlist from '../components/Playlist';
import { styled } from '@mui/material/styles';

export default class FilePlaylistsTab extends React.Component {
  render() {
    const { labels, currentFilePlaylist, updateState, openDeletePlaylistDialog, currentFilePlaylistName, 
      deleteTrack, files, handleFileClick, selectAllFiles, addFilesToPlaylist, selectAllFilesState, 
      goToDefaultMusicFolder, goToFileSystemRoot, selectBreadcrumb } = this.props;

    if (files === null) {
      return null;
    }

    const StyledBreadcrumb = styled(Chip)(() => {
      return {
        backgroundColor: COLOR_CHIP,
        height: "2rem",
        '&:hover, &:focus': {
          backgroundColor: COLOR_CHIP_CONTRAST
        }
      };
    });

    return (
      <main style={{ "paddingTop": "2rem" }}>
        <Grid container justifyContent="left" alignItems="center" style={{"paddingBottom": "1rem"}}>
          <Grid item>
            <IconButton style={{ color: COLOR_MEDIUM }} onClick={() => { goToFileSystemRoot() }}>
              <DesktopWindowsIcon/>
            </IconButton>
          </Grid>
          <Grid item>
            <IconButton style={{ color: COLOR_MEDIUM }} onClick={() => { goToDefaultMusicFolder() }}>
              <PersonOutlineIcon/>
            </IconButton>
          </Grid>
          <Grid item>
            <Breadcrumbs separator={files.separator}>
              {files.start_from_separator && <div style={{"display":"none"}}/>}
              {files.breadcrumbs.map((value, index) => {
                return(
                  <StyledBreadcrumb
                    id={index} 
                    key={index} 
                    href="#" 
                    label={value.name} 
                    onClick={() => selectBreadcrumb(value.path)}
                  />
                )
              })}
            </Breadcrumbs>
          </Grid>
        </Grid>
        <Grid container spacing={2} justifyContent="left" alignItems="center">
          <Grid item style={{ "paddingBottom": "6rem"}}>
            <FileList 
              title={labels["audio-files"]}
              files={files} 
              selectAllFiles={selectAllFiles}
              handleFileClick={handleFileClick}
              selectAllFilesState={selectAllFilesState}
            />
          </Grid>
          <Grid item>
              <Button
                  size="small"
                  variant="contained"
                  style={{"background": COLOR_DARK_LIGHT, "color": COLOR_CHIP}}
                  onClick={() => { addFilesToPlaylist() }}
              >
                <KeyboardArrowRightOutlinedIcon  fontSize="large" />
              </Button>
          </Grid>
          <Grid item style={{ "paddingBottom": "6rem"}}>
            <Playlist 
              title={labels["playlist"] + ": " + currentFilePlaylistName}
              deleteTrack={deleteTrack}
              openDeletePlaylistDialog={openDeletePlaylistDialog}
              currentFilePlaylist={currentFilePlaylist}
              currentFilePlaylistName={currentFilePlaylistName}
              updateState={updateState}>
            </Playlist>
          </Grid>
        </Grid>
      </main>
    );
  }
}
