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
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import FolderOutlinedIcon from '@material-ui/icons/FolderOutlined';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import {
  Breadcrumb, Palette, RadioBrowserIcon, RadioBrowserIconsContainer, HomeIcon, RadioBrowserIconText,
  BreadcrumbsContainer, Separator, FilesContainer, PlaylistContainer, PlaylistFilesContainer
} from './mincss';
import { countryIconUrl, languageIconUrl, genreIconUrl, nameIconUrl } from "../Rest";

export default class RadioBrowser extends React.Component {
  render() {
    const { labels, openBrowser, toggleBrowser, getRadioBrowserCountries, searchByLanguage, searchByGenre, searchByName,
      countries, radioBrowserCategory, currentRadioBrowserStationIndex, setRadioBrowserCountry } = this.props;

    // if (files === null) {
    //   return null;
    // }

    return (
      <Drawer open={openBrowser} onClose={toggleBrowser(false)} anchor='left'
        PaperProps={{ style: { width: '400px', display: 'flex', flexDirection: 'column' } }}>
        <div style={RadioBrowserIconsContainer}>
          <IconButton onClick={getRadioBrowserCountries} style={HomeIcon}>
            <img src={countryIconUrl} key='country' alt='country' style={RadioBrowserIcon} />
            <Typography noWrap style={RadioBrowserIconText}>{labels['country']}</Typography>
          </IconButton>
          <IconButton onClick={searchByLanguage} style={HomeIcon}>
            <img src={languageIconUrl} key='language' alt='language' style={RadioBrowserIcon} />
            <Typography noWrap style={RadioBrowserIconText}>{labels['language']}</Typography>
          </IconButton>
          <IconButton onClick={searchByGenre} style={HomeIcon}>
            <img src={genreIconUrl} key='genre' alt='genre' style={RadioBrowserIcon} />
            <Typography noWrap style={RadioBrowserIconText}>{labels['genre']}</Typography>
          </IconButton>
          <IconButton onClick={searchByName} style={HomeIcon}>
            <img src={nameIconUrl} key='name' alt='name' style={RadioBrowserIcon} />
            <Typography noWrap style={RadioBrowserIconText}>{labels['name']}</Typography>
          </IconButton>
        </div>
        
        {radioBrowserCategory === 'countries' && <div style={PlaylistContainer}>
          <List dense component="div" role="list">
            {countries && countries.map((value, index) => {
              return (
                <ListItem
                  disablePadding
                  key={index}
                  role="listitem"
                  onClick={() => { setRadioBrowserCountry(index) }}
                >
                  <ListItemButton
                    role="listitem"
                    dense
                    selected={currentRadioBrowserStationIndex === index}
                    autoFocus={currentRadioBrowserStationIndex === index}
                  >
                    <ListItemText id={index} primary={`${value.name} (${value.stationcount})`} style={{ wordWrap: "break-word", marginRight: '0.1rem' }} />
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
        </div>}
        {radioBrowserCategory === 'countries' && <div style={Separator}/>}
        {/* radioBrowserCategory === 'playlists' && <div style={PlaylistFilesContainer}>
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
        </div>} */}
      </Drawer>
    );
  }
}
