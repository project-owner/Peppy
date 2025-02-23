export const HomeIconType = 'gradient';
export const HomeIconCategory = 'line';

export const PaletteSlate = {
  colorTopLeft: 'rgb(178,198,230)',
  colorBottomRight: 'rgb(100,120,153)',
  colorMainPanel: 'rgba(0,0,30,0.3)',
  colorTitle: 'rgb(245,222,179)',
  colorGenreSelected: 'rgb(246,194,228)',
  colorArtistTime: 'rgb(222,184,135)',
  colorButtonsBackground: 'rgba(255,255,255,0.6)',
  colorButton: 'rgb(100,120,153)',
  colorSecondaryButton: 'rgba(10,15,30,0.2)',
  colorVolume: 'rgb(10,15,30)',
  colorHomeIcon1: 'rgb(100,120,153)',
  colorHomeIcon2: 'rgb(100,120,153)',
  colorHomeIcon3: 'rgb(200,15,50)',
  colorHomeIcon4: 'rgb(200,15,50)'
};

export const Palette = PaletteSlate;

const SeparatorShadowGradient = 'linear-gradient(rgb(205,200,210) 0px, transparent 20px)';

const BackgroundGradient = `
    linear-gradient(to bottom right, ${Palette.colorTopLeft}, ${Palette.colorBottomRight})
`;

export const Window = {
  width: '100%',
  height: '100vh',
  padding: 0,
  margin: 0,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center'
};

export const EmptyWindow = {
  width: '100%',
  height: '100vh',
  padding: 0,
  margin: 0,
  display: 'none',
  backgroundColor: 'white'
};

export const WindowBackground = {
  position: 'absolute',
  width: '100%',
  height: '100%',
  top: 0,
  left: 0,
  zIndex: -1,
  overflow: 'hidden',
  background: BackgroundGradient,
};

export const HomeIcon = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  paddingRight: '0.7rem',
  paddingLeft: '0.7rem',
}

export const PlayerFrame = {
  display: 'flex',
  flexDirection: 'column',
  // marginBottom: '10px',
  boxShadow: '10px 10px 20px rgba(0, 0, 0, 0.6)',
  height: '174px',
  marginTop: 'auto'
};

export const MainPanel = {
  zIndex: 2,
  position: 'relative',
  width: '500px',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: `${Palette.colorMainPanel}`,
  alignItems: 'flex-start',
  marginBottom: 'auto',
  overflow: 'hide'
};

export const ImageLabelsSlider = {
  display: 'flex',
  flexDirection: 'row',
  alignItems: 'center',
  height: '120px',
  justifyContent: 'space-between'
};

export const AlbumArt = {
  objectFit: 'cover',
  width: '120px',
  height: '120px',
  cursor: 'pointer',
  boxShadow: '0 0 5px rgba(0,0,0,0.4)',
  clipPath: 'inset(0px -10px 0px 0px)' // top, right, bottom, left
}

export const LabelsSlider = {
  display: 'flex',
  flexDirection: 'column',
  marginLeft: '1rem',
  justifyContent: 'center',
  width: '360px',
  height: '100%'
};

export const TextContainer = {
  width: '100%',
  display: 'flex',
  flexDirection: 'row',
  justifyContent: 'center'
};

export const Track = {
  color: `${Palette.colorTitle}`,
  fontSize: '1.4rem',
  textShadow: '2px 2px 3px rgba(0, 0, 0, 0.8)',
  paddingRight: '0.2rem',
  // paddingBottom: '0.5rem',
  cursor: 'pointer',
  overflow: 'scroll'
};

export const TrackGradient = `
    linear-gradient(to left, ${Palette.colorTopLeft}, white 20%)
`;

export const InfoContainer = {
  display: 'grid',
  gridTemplateColumns: 'auto auto auto auto auto',
  backgroundImage: `${SeparatorShadowGradient}`
};

export const InfoLabelFirst = {
  gridColumn: '1 / span 1',
  color: Palette.colorBottomRight,
  fontSize: '0.8rem',
  fontWeight: 'bold',
  paddingLeft: '1rem',
  paddingRight: '0.5rem',
  paddingTop: '1rem',
  paddingBottom: '0.2rem'
};

export const InfoLabel = {
  gridColumn: '1 / span 1',
  color: Palette.colorBottomRight,
  fontSize: '0.8rem',
  fontWeight: 'bold',
  paddingLeft: '1rem',
  paddingRight: '0.5rem',
  paddingTop: '0.2rem',
  paddingBottom: '0.2rem'
};

export const InfoLabelLast = {
  gridColumn: '1 / span 1',
  color: Palette.colorBottomRight,
  fontSize: '0.8rem',
  fontWeight: 'bold',
  paddingLeft: '1rem',
  paddingRight: '0.5rem',
  paddingTop: '0.2rem',
  paddingBottom: '1rem'
};

export const InfoTextFirst = {
  gridColumn: '2 / span 4',
  color: `black`,
  fontSize: '0.8rem',
  paddingLeft: '0.5rem',
  paddingTop: '1rem',
  paddingBottom: '0.2rem'
};

export const InfoText = {
  gridColumn: '2 / span 4',
  color: `black`,
  fontSize: '0.8rem',
  paddingLeft: '0.5rem',
  paddingTop: '0.2rem',
  paddingBottom: '0.2rem'
};

export const InfoTextLast = {
  gridColumn: '2 / span 4',
  color: `black`,
  fontSize: '0.8rem',
  paddingLeft: '0.5rem',
  paddingTop: '0.2rem',
  paddingBottom: '1rem'
};

export const Separator = {
  borderTop: '2px solid',
  borderImageSlice: '1',
  borderWidth: '100%',
  borderImageSource: 'linear-gradient(to right, red, orange)'
};

export const LyricsContainer = {
  backgroundImage: `${SeparatorShadowGradient}`
};

export const LyricsText = {
  color: `black`,
  fontSize: '0.8rem',
  whiteSpace: 'pre-line',
  padding: '1rem'
};

export const Album = {
  color: `${Palette.colorArtistTime}`,
  fontSize: '1rem',
  paddingRight: '0.2rem',
  textShadow: '1px 1px 3px rgba(0, 0, 0, 1)'
};

export const Artist = {
  color: `${Palette.colorArtistTime}`,
  fontSize: '0.8rem',
  paddingRight: '0.2rem',
  textShadow: '1px 1px 3px rgba(0, 0, 0, 1)'
};

export const TimeSliderPanel = {
  zIndex: 2,
  width: '100%',
  height: '30px',
  display: 'flex',
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'space-beetwen',
  marginTop: '0.2rem'
};

export const TimeStyle = {
  color: `${Palette.colorArtistTime}`,
  fontSize: '16px',
  paddingRight: '0.2rem',
  textShadow: '1px 1px 3px rgba(0, 0, 0, 1)'
};

export const TimeSliderStyle = {
  // color: 'rgb(230, 170, 140)',
  '& .MuiSlider-track': {
    border: 'none',
    backgroundColor: `${Palette.colorArtistTime}`,
    boxShadow: '1px 1px 2px rgba(0, 0, 0, 0.5)'
  },
  '& .MuiSlider-rail': {
    border: 'none',
    backgroundColor: `${Palette.colorArtistTime}`,
    boxShadow: '1px 1px 2px rgba(0, 0, 0, 0.5)'
  },
  '& .MuiSlider-thumb': {
    width: 12,
    height: 12,
    color: `${Palette.colorArtistTime}`,
    '&::before': {
      boxShadow: '2px 2px 6px rgba(0,0,0,0.4)',
    },
    '&:hover, &.Mui-focusVisible, &.Mui-active': {
      color: `${Palette.colorArtistTime}`,
      boxShadow: '1px 1px 2px rgba(0, 0, 0, 0.5)',
    },
  }
};

export const SliderPanel = {
  width: '80%',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'space-beetwen',
  margin: '1.5rem'
};

export const TimeLeftPanel = {
  width: 'auto',
  marginLeft: '1rem'
};

export const TimeRightPanel = {
  width: 'auto',
  marginRight: '1rem'
};

export const HomeButtonsPanel = {
  display: 'flex',
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'space-between',
  height: '90px'
};

export const ButtonPanel = {
  zIndex: 2,
  width: '500px',
  height: '54px',
  display: 'flex',
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'space-between',
  backgroundColor: Palette.colorButtonsBackground
};

export const ButtonCenterPanel = {
  width: '200px',
  height: '54px',
  display: 'flex',
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'center'
};

export const HomeButtonsCenterPanel = {
  display: 'flex',
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'center',
  marginRight: "1rem",
  padding: '0.2rem'
};

export const ButtonStyle = {
  boxShadow: `inset 1px 1px 1px 0px rgba(255, 255, 255, 1), inset -1px -1px 1px 0px rgba(100, 100, 100, 1), 1px 1px 4px 0px ${Palette.colorButton}`,
  margin: '0.1rem'
};

export const PlayButtonStyle = {
  fontSize: '1.8rem',
  color: `${Palette.colorButton}`
};

export const NextPreviousButtonStyle = {
  color: `${Palette.colorButton}`
};

export const VolumePanel = {
  display: 'flex',
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'center',
  width: '300px'
};

export const TrackPanel = {
  display: 'flex',
  flexDirection: 'column'
}

export const Mute = {
  width: '26px',
  height: '26px',
  filter: 'drop-shadow(2px 2px 2px rgba(0,0, 0, 0.4))'
};

export const VolumeSliderStyle = {
  '& .MuiSlider-track': {
    border: 'none',
    backgroundColor: `${Palette.colorVolume}`
  },
  '& .MuiSlider-valueLabel': {
    color: 'white',
    backgroundColor: `${Palette.colorBottomRight}`
  },
  '& .MuiSlider-rail': {
    color: `${Palette.colorVolume}`,
    border: 'none',
    boxShadow: '1px 1px 3px rgb(0, 0, 0)'
  },
  '& .MuiSlider-thumbColorPrimary': {
    color: 'red'
  },
  '& .MuiSlider-thumb': {
    width: 12,
    height: 12,
    backgroundColor: `${Palette.colorVolume}`,
    '&::before': {
      boxShadow: '2px 2px 6px rgba(0,0,0,0.4)'
    },
    '&:hover, &.Mui-focusVisible, &.Mui-active': {
      boxShadow: 'none'
    }
  }
};

export const Mode = {
  width: '40px',
  height: '40px',
  marginLeft: '1rem',
  marginRight: '1rem',
  filter: 'drop-shadow(1px 1px 1px rgba(0, 0, 0, 0.5))'
};

export const ModeText = {
  color: `${Palette.colorHomeIcon1}`,
  fontSize: '0.7rem',
  marginTop: '0.4rem',
  textShadow: '1px 1px 1px rgba(0, 0, 0, 0.2)'
};

export const RadioBrowserIconText = {
  color: `${Palette.colorTitle}`,
  fontSize: '0.8rem',
  // marginTop: '0.4rem',
  textShadow: '1px 1px 1px rgb(0, 0, 0)'
};

export const ModeIcon = {
  width: '26px',
  height: '26px'
};

export const TopDrawerPanel = {
  display: 'flex',
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'space-between',
  height: '90px',
  backgroundColor: Palette.colorBottomRight
};

export const TopDrawerCenterPanel = {
  display: 'flex',
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'center',
  marginLeft: "1rem",
  marginRight: "1rem",
  padding: '0.2rem'
};

export const TopDrawerText = {
  color: `${Palette.colorTitle}`,
  fontSize: '0.7rem',
  marginTop: '0.4rem',
  textShadow: '1px 1px 1px rgba(0, 0, 0, 0.6)'
};

export const TopDrawerIcon = {
  width: '34px',
  height: '34px',
  marginLeft: '1rem',
  marginRight: '1rem',
  filter: 'drop-shadow(1px 1px 1px rgba(0, 0, 0, 0.5))'
};

export const Genre = {
  color: `${Palette.colorArtistTime}`,
  fontSize: '1rem',
  paddingRight: '0.2rem',
  textShadow: '1px 1px 3px rgba(0, 0, 0, 1)',
  cursor: 'pointer'
};

export const Breadcrumb = {
  fontSize: '0.8rem',
  paddingLeft: '0.1rem',
  paddingRight: '0.1rem',
  color: 'black',
  '& .css-3mf706': {
    border: 'none'
  }
}

export const FileBrowserIcon = {
  width: '1.5rem',
  height: '1.5rem',
  padding: '0.5rem',
  cursor: 'pointer',
  color: PaletteSlate.colorTitle,
  filter: 'drop-shadow(1px 1px 1px rgb(0, 0, 0))'
};

export const RadioBrowserIcon = {
  width: '2rem',
  height: '2rem',
  cursor: 'pointer',
  color: PaletteSlate.colorTitle,
  filter: 'drop-shadow(1px 1px 1px rgb(0, 0, 0))'
};

export const BrowserIconsContainer = {
  width: 'inherit', 
  height: '2.5rem', 
  display: 'flex', 
  flexDirection: 'row', 
  alignItems: 'center', 
  justifyContent: 'center',
  backgroundColor: Palette.colorBottomRight
};

export const RadioBrowserIconsContainer = {
  width: 'inherit', 
  height: '4rem', 
  display: 'flex', 
  flexDirection: 'row', 
  alignItems: 'center', 
  justifyContent: 'center',
  backgroundColor: Palette.colorBottomRight
};

export const BreadcrumbsContainer = {
  width: '100%', 
  display: 'flex', 
  flexDirection: 'row', 
  alignItems: 'center', 
  justifyContent: 'center'
};

export const FilesContainer = {
  width: '100%', 
  height: "100%",
  overflow: 'scroll',
  backgroundImage: `${SeparatorShadowGradient}`
};

export const PlaylistContainer = {
  width: '100%', 
  height: "40%",
  overflow: 'scroll',
  backgroundImage: `${SeparatorShadowGradient}`
};

export const PlaylistFilesContainer = {
  width: '100%', 
  height: "60%",
  overflow: 'scroll',
  backgroundImage: `${SeparatorShadowGradient}`
};
