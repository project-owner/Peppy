/* Copyright 2024 Peppy Player peppy.player@gmail.com
 
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
import { Drawer } from '@mui/material';
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Typography from '@mui/material/Typography';
import FolderOutlinedIcon from '@material-ui/icons/FolderOutlined';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import { Breadcrumb, Palette, FileBrowserIcon, BrowserIconsContainer, 
  BreadcrumbsContainer, Separator, FilesContainer, PlaylistContainer, PlaylistFilesContainer } from './mincss';
import { rootIconUrl, userHomeIconUrl, playlistIconUrl } from "../Rest";

export default class FileBrowser extends React.Component {
  render() {
    const { openBrowser, toggleBrowser, files, goToFileSystemRoot, goToDefaultMusicFolder, selectBreadcrumb,
      handleFileClick, currentFileIndex, getFilePlaylists, fileBrowserMode, playlists, getFilePlaylist,
      playlist, handlePlaylistFileClick, currentPlaylistFileIndex } = this.props;

    if (files === null) {
      return null;
    }

    function mouseOver(event) {
      event.target.style.background = Palette.colorButton;
      event.target.style.color = 'white';
      event.target.style.cursor = 'pointer';
    }

    function mouseOut(event) {
      event.target.style.background = 'white';
      event.target.style.color = Palette.colorButton;
    }

    return (
      <Drawer open={openBrowser} onClose={toggleBrowser(false)} anchor='left' 
        PaperProps={{style: {width: '400px',display: 'flex', flexDirection: 'column'}}}>
        <div style={BrowserIconsContainer}>
          <img src={rootIconUrl} key='root' alt='root' style={FileBrowserIcon} onClick={() => { goToFileSystemRoot() }} />
          <img src={userHomeIconUrl} key='userHome' alt='userHome' style={FileBrowserIcon} onClick={() => { goToDefaultMusicFolder() }} />
          <img src={playlistIconUrl} key='playlist' alt='playlist' style={FileBrowserIcon} onClick={() => { getFilePlaylists() }} />
        </div>
        {fileBrowserMode === 'files' && <div style={BreadcrumbsContainer}>
          <Breadcrumbs separator={files.separator} style={{ width: '100%', padding: '0.5rem' }}>
            {files.start_from_separator && <div style={{ "display": "none" }} />}
            {files.breadcrumbs.map((value) => {
              return (
                <Typography
                  style={Breadcrumb}
                  onMouseOver={mouseOver}
                  onMouseOut={mouseOut}
                  onClick={() => selectBreadcrumb(value.path)}
                >
                  {value.name}
                </Typography>
              )
            })}
          </Breadcrumbs>
        </div>}
        {fileBrowserMode === 'files' && <div style={FilesContainer}>
          <List dense component="div" role="list">
            {files && files.content && files.content.map((value, index) => {
              return (
                <ListItem
                  disablePadding
                  key={index}
                  role="listitem"
                  onClick={() => { handleFileClick(index) }}
                >
                  <ListItemButton
                    role="listitem"
                    dense
                    selected={currentFileIndex === index}
                    autoFocus={currentFileIndex === index}
                  >
                    <div style={{ paddingRight: '1rem' }}>
                      {value.type === "folder" && <FolderOutlinedIcon style={{ paddingLeft: '0.8rem', color: Palette.colorButton }} />}
                    </div>
                    <ListItemText id={index} primary={value.name} style={{ wordWrap: "break-word", marginRight: '0.1rem' }} />
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
        </div>}
        {fileBrowserMode === 'playlists' && <div style={PlaylistContainer}>
          <List dense component="div" role="list">
            {playlists && playlists.map((value, index) => {
              return (
                <ListItem
                  disablePadding
                  key={index}
                  role="listitem"
                  onClick={() => { getFilePlaylist(index) }}
                >
                  <ListItemButton
                    role="listitem"
                    dense
                    selected={currentFileIndex === index}
                    autoFocus={currentFileIndex === index}
                  >
                    <ListItemText id={index} primary={value.name} style={{ wordWrap: "break-word", marginRight: '0.1rem' }} />
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
        </div>}
        {fileBrowserMode === 'playlists' && <div style={Separator}/>}
        {fileBrowserMode === 'playlists' && <div style={PlaylistFilesContainer}>
          <List dense component="div" role="list">
            {playlist && playlist.map((value, index) => {
              return (
                <ListItem
                  disablePadding
                  key={index}
                  role="listitem"
                  onClick={() => { handlePlaylistFileClick(value, index) }}
                >
                  <ListItemButton
                    role="listitem"
                    dense
                    selected={currentPlaylistFileIndex === index}
                    autoFocus={currentPlaylistFileIndex === index}
                  >
                    <ListItemText id={index} primary={value} style={{ wordWrap: "break-word", marginRight: '0.1rem' }} />
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
        </div>}
      </Drawer>
    );
  }
}
