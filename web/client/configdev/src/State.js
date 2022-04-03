/* Copyright 2019-2022 Peppy Player peppy.player@gmail.com
 
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

export let State = {
  parameters: null,
  players: null,
  screensavers: null,
  playlists: {},
  playlistsTexts: {},
  playlistBasePath: null,
  podcasts: null,
  streams: null,
  streamsText: null,
  streamsBasePath: null,
  parametersDirty: false,
  playersDirty: false,
  screensaversDirty: false,
  playlistsDirty: false,
  podcastsDirty: false,
  streamsDirty: false,
  backgroundDirty: false,
  nasDirty: false,
  shareDirty: false,
  language: "",
  open: true,
  tabIndex: 0,
  currentMenuItem: 0,
  openSnack: false,
  isRebootDialogOpen: false,
  isSaveAndRebootDialogOpen: false,
  isShutdownDialogOpen: false,
  isSaveAndShutdownDialogOpen: false,
  isSetDefaultsAndRebootDialogOpen: false,
  buttonsDisabled: false,
  showProgress: false,
  labels: null,
  notificationMessage: null,
  notificationVariant: "",
  hideUi: false,
  reboot: false,
  shutdown: false,
  playerWasRebooted: false,
  flags: null,
  background: null,
  fonts: null,
  system: null,
  log: null
}