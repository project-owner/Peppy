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

import React from "react";
import Drawer from '@mui/material/Drawer';
import Typography from '@mui/material/Typography';
import { TrackPanel, InfoContainer, InfoLabelFirst, InfoLabel, InfoLabelLast, InfoTextFirst, 
  InfoText, InfoTextLast, Separator,  LyricsText, LyricsContainer } from './mincss';

export default class Track extends React.Component {

  render() {
    const { openTrack, toggleTrack, info, labels, lyrics } = this.props;
    const generalInfoAvailable = isGeneralInfoAvailable();
    const technicalInfoAvailable = isTechnicalInfoAvailable();
    const infoAvailable = isInfoAvailable();

    function isPresent(attr) {
      return info && labels && Object.hasOwn(info, attr) && info[attr] !== null &&
        info[attr] !== undefined ? true : false;
    }

    function isGeneralInfoAvailable() {
      return isPresent('title') || isPresent('album') || isPresent('artist') || isPresent('genre') ||
        isPresent('composer') || isPresent('performer') || isPresent('date') ? true : false;
    }

    function isTechnicalInfoAvailable() {
      return isPresent('filename') || isPresent('filesize') || isPresent('sample_rate') ||
        isPresent('bits_per_sample') || isPresent('bitrate') || isPresent('channels') ? true : false;
    }

    function isInfoAvailable() {
      return generalInfoAvailable || technicalInfoAvailable || lyrics ? true : false;
    }

    return (
      <Drawer
        open={openTrack && infoAvailable}
        onClose={toggleTrack(false)}
        anchor='right'
        PaperProps={{
          style: {
            width: '22rem',
            // background: TrackGradient
          }
        }}
      >
        <div style={{ TrackPanel }}>
          {technicalInfoAvailable && <div style={Separator}/>}
          {generalInfoAvailable && <div style={InfoContainer}>
            {isPresent('title') && <Typography style={InfoLabelFirst}>{labels["title"]}</Typography>}
            {isPresent('title') && <Typography style={InfoTextFirst}>{info.title}</Typography>}
            {isPresent('album') && <Typography style={InfoLabel}>{labels["album"]}</Typography>}
            {isPresent('album') && <Typography style={InfoText}>{info.album}</Typography>}
            {isPresent('artist') && <Typography style={InfoLabel}>{labels["artist"]}</Typography>}
            {isPresent('artist') && <Typography style={InfoText}>{info.artist}</Typography>}
            {isPresent('genre') && <Typography style={InfoLabel}>{labels["genre"]}</Typography>}
            {isPresent('genre') && <Typography style={InfoText}>{info.genre}</Typography>}
            {isPresent('composer') && <Typography style={InfoLabel}>{labels["composer"]}</Typography>}
            {isPresent('composer') && <Typography style={InfoText}>{info.composer}</Typography>}
            {isPresent('performer') && <Typography style={InfoLabel}>{labels["performer"]}</Typography>}
            {isPresent('performer') && <Typography style={InfoText}>{info.performer}</Typography>}
            {isPresent('date') && <Typography style={InfoLabelLast}>{labels["date"]}</Typography>}
            {isPresent('date') && <Typography style={InfoTextLast}>{info.date}</Typography>}
            </div>
          }
          {technicalInfoAvailable && <div style={Separator}/>}
          {technicalInfoAvailable && <div style={InfoContainer}>
            {isPresent('filename') && <Typography style={InfoLabelFirst}>{labels["filename"]}</Typography>}
            {isPresent('filename') && <Typography style={InfoTextFirst}>{info.filename}</Typography>}
            {isPresent('filesize') && <Typography style={InfoLabel}>{labels["file.size"]}</Typography>}
            {isPresent('filesize') && <Typography style={InfoText}>{info.filesize} {labels["bytes"]}</Typography>}
            {isPresent('sample_rate') && <Typography style={InfoLabel}>{labels["sample.rate"]}</Typography>}
            {isPresent('sample_rate') && <Typography style={InfoText}>{info.sample_rate} {labels["hz"]}</Typography>}
            {isPresent('bits_per_sample') && <Typography style={InfoLabel}>{labels["bits.per.sample"]}</Typography>}
            {isPresent('bits_per_sample') && <Typography style={InfoText}>{info.bits_per_sample}</Typography>}
            {isPresent('bitrate') && <Typography style={InfoLabel}>{labels["bit.rate"]}</Typography>}
            {isPresent('bitrate') && <Typography style={InfoText}>{Math.ceil(info.bitrate/1000)} {labels["kbps"]}</Typography>}
            {isPresent('channels') && <Typography style={InfoLabelLast}>{labels["channels"]}</Typography>}
            {isPresent('channels') && <Typography style={InfoTextLast}>{info.channels}</Typography>}
            </div>
          }
          {lyrics && labels && <div style={Separator}/>}
          {lyrics && labels && <div style={LyricsContainer}>
              {lyrics && labels && <Typography noWrap style={LyricsText}>{lyrics}</Typography>}
            </div>
          }
        </div>
      </Drawer>
    );
  }
}
