export let State = {
  parameters: null,
  players: null,
  screensavers: null,
  playlists: {},
  podcasts: null,
  streams: null,
  parametersDirty: false,
  playersDirty: false,
  screensaversDirty: false,
  playlistsDirty: false,
  podcastsDirty: false,
  streamsDirty: false,
  language: "",
  open: true,
  tabIndex: 0,
  currentMenuItem: 0,
  openSnack: false,
  isRebootDialogOpen: false,
  isSaveAndRebootDialogOpen: false,
  isShutdownDialogOpen: false,
  isSaveAndShutdownDialogOpen: false,
  buttonsDisabled: false,
  showProgress: false,
  labels: null,
  notificationMessage: null,
  notificationVariant: "",
  hideUi: false,
  reboot: false,
  shutdown: false,
  playerWasRebooted: false,
  flags: null
}