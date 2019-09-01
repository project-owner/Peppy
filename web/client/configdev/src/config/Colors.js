import React from 'react';
import ColorPalette from "./ColorPalette";
import ScreenExample from "./ScreenExample";
import ColorSlider from "./ColorSlider";
import { Button } from "@material-ui/core";
import Divider from '@material-ui/core/Divider';

export const COLOR_DARK = "color.dark";
export const COLOR_DARK_LIGHT = "color.dark.light";
export const COLOR_MEDIUM = "color.medium";
export const COLOR_BRIGHT = "color.bright";
export const COLOR_CONTRAST = "color.contrast";
export const COLOR_LOGO = "color.logo";
export const COLOR_MUTE = "color.mute";
export const COLOR_WEB_BGR = "color.web.bgr";

const palettes = {
  original: {
    [COLOR_DARK]: [0, 70, 75],
    [COLOR_DARK_LIGHT]: [20, 90, 100],
    [COLOR_MEDIUM]: [70, 140, 150],
    [COLOR_BRIGHT]: [160, 190, 210],
    [COLOR_CONTRAST]: [255, 190, 120],
    [COLOR_LOGO]: [20, 190, 160],
    [COLOR_MUTE]: [242, 107, 106],
    [COLOR_WEB_BGR]: [0, 38, 40]
  },
  burgundy: {
    [COLOR_DARK]: [79, 5, 5],
    [COLOR_DARK_LIGHT]: [118, 49, 49],
    [COLOR_MEDIUM]: [184, 144, 144],
    [COLOR_BRIGHT]: [247, 201, 204],
    [COLOR_CONTRAST]: [249, 212, 175],
    [COLOR_LOGO]: [165, 184, 162],
    [COLOR_MUTE]: [221, 51, 80],
    [COLOR_WEB_BGR]: [39, 6, 15]
  },
  techno: {
    [COLOR_DARK]: [49, 67, 91],
    [COLOR_DARK_LIGHT]: [60, 80, 104],
    [COLOR_MEDIUM]: [111, 140, 172],
    [COLOR_BRIGHT]: [163, 192, 224],
    [COLOR_CONTRAST]: [243, 205, 210],
    [COLOR_LOGO]: [20, 190, 160],
    [COLOR_MUTE]: [197, 115, 142],
    [COLOR_WEB_BGR]: [27, 39, 55]
  },
  pinky: {
    [COLOR_DARK]: [97, 0, 122],
    [COLOR_DARK_LIGHT]: [119, 20, 146],
    [COLOR_MEDIUM]: [160, 58, 186],
    [COLOR_BRIGHT]: [208, 120, 232],
    [COLOR_CONTRAST]: [241, 227, 150],
    [COLOR_LOGO]: [255, 230, 255],
    [COLOR_MUTE]: [242, 107, 106],
    [COLOR_WEB_BGR]: [56, 31, 51]
  },
  navy: {
    [COLOR_DARK]: [2, 48, 84],
    [COLOR_DARK_LIGHT]: [7, 81, 142],
    [COLOR_MEDIUM]: [4, 148, 208],
    [COLOR_BRIGHT]: [74, 186, 255],
    [COLOR_CONTRAST]: [241, 210, 60],
    [COLOR_LOGO]: [131, 154, 252],
    [COLOR_MUTE]: [220, 70, 95],
    [COLOR_WEB_BGR]: [35, 35, 57]
  },
  earth: {
    [COLOR_DARK]: [11, 71, 68],
    [COLOR_DARK_LIGHT]: [31, 91, 89],
    [COLOR_MEDIUM]: [81, 140, 110],
    [COLOR_BRIGHT]: [183, 211, 164],
    [COLOR_CONTRAST]: [255, 170, 80],
    [COLOR_LOGO]: [220, 99, 80],
    [COLOR_MUTE]: [225, 134, 100],
    [COLOR_WEB_BGR]: [14, 39, 10]
  }
};

export default class Colors extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedTile: COLOR_DARK
    };
  }

  handleChange = name => event => {
    this.props.updateState(name, event.target.checked)
  };

  getName = name => {
    let newName = name.toLowerCase();
    if (newName.includes(" ")) {
      newName = newName.replace(/ /g, "_");
    }
    return newName;
  }

  setRed = (_, value) => {
    const v = Math.trunc(value);
    this.props.setColor(this.state.selectedTile, v, 0);
  };

  setGreen = (_, value) => {
    const v = Math.trunc(value);
    this.props.setColor(this.state.selectedTile, v, 1);
  };

  setBlue = (_, value) => {
    const v = Math.trunc(value);
    this.props.setColor(this.state.selectedTile, v, 2);
  };

  selectTile = (name) => {
    this.setState({ selectedTile: name });
  };

  setPalette = (event) => {
    const key = event.target.parentNode.parentNode.parentNode.id;
    this.props.setPalette(palettes[key]);
  };

  render() {
    const { classes, params, labels } = this.props;
    const LABEL_WIDTH = Math.max(labels.red.length, labels.green.length, labels.blue.length) * 20 + "px";
    const SLIDER_WIDTH = "320px";
    const SLIDER_HEIGHT = "30px";
    const PALETTE_WIDTH = 92;
    const PALETTE_HEIGHT = 46;

    return (
      <div className={classes.colorsContainer}>
        <h4 className={classes.colorsHeader}>{labels["current.palette"]}</h4>
        <Divider className={classes.colorsDivider} />
        <div className={classes.colorsPaletteRow}>
          <div colorName={classes.colorsCurrentPaletteContainer}>
            <ColorPalette
              classes={classes}
              width={320}
              height={110}
              colorSchema={params}
              selectTile={this.selectTile}
              selected={this.state.selectedTile}
            />
            <Button variant="contained" color="default" className={classes.colorsResetButton} onClick={this.props.reset}>
              {labels.reset}
            </Button>
          </div>
          <div className={classes.slidersContainer}>
            <ColorSlider
              classes={classes}
              width={SLIDER_WIDTH}
              height={SLIDER_HEIGHT}
              thumbColor={"red"}
              value={params[this.state.selectedTile][0]}
              label={labels.red}
              labelWidth={LABEL_WIDTH}
              onChange={this.setRed} />
            <ColorSlider
              classes={classes}
              width={SLIDER_WIDTH}
              height={SLIDER_HEIGHT}
              thumbColor={"green"}
              value={params[this.state.selectedTile][1]}
              label={labels.green}
              labelWidth={LABEL_WIDTH}
              onChange={this.setGreen} />
            <ColorSlider
              classes={classes}
              width={SLIDER_WIDTH}
              height={SLIDER_HEIGHT}
              thumbColor={"blue"}
              label={labels.blue}
              value={params[this.state.selectedTile][2]}
              labelWidth={LABEL_WIDTH}
              onChange={this.setBlue} />
          </div>
        </div>
        <h4 className={classes.colorsHeader}>{labels["screen.samples"]}</h4>
        <Divider className={classes.colorsDivider} />
        <ScreenExample colorSchema={params} classes={classes}/>
        <h4 className={classes.colorsHeader}>{labels["palettes"]}</h4>
        <Divider className={classes.colorsDivider} />
        <div className={classes.colorsPaletteRow}>
          <div id="original" onClick={this.setPalette}>
            <ColorPalette
              classes={classes}
              name={labels["palette.original"]}
              width={PALETTE_WIDTH}
              height={PALETTE_HEIGHT}
              colorSchema={palettes.original}
              disableSelection={true} />
          </div>
          <div id="burgundy" className={classes.colorsPalette} onClick={this.setPalette}>
            <ColorPalette
              classes={classes}
              name={labels["palette.burgundy"]}
              width={PALETTE_WIDTH}
              height={PALETTE_HEIGHT}
              colorSchema={palettes.burgundy}
              disableSelection={true} />
          </div>
          <div id="techno" className={classes.colorsPalette} onClick={this.setPalette}>
            <ColorPalette
              classes={classes}
              name={labels["palette.techno"]}
              width={PALETTE_WIDTH}
              height={PALETTE_HEIGHT}
              colorSchema={palettes.techno}
              disableSelection={true} />
          </div>
          <div id="pinky" className={classes.colorsPalette} onClick={this.setPalette}>
            <ColorPalette
              classes={classes}
              name={labels["palette.pinky"]}
              width={PALETTE_WIDTH}
              height={PALETTE_HEIGHT}
              colorSchema={palettes.pinky}
              disableSelection={true} />
          </div>
          <div id="navy" className={classes.colorsPalette} onClick={this.setPalette}>
            <ColorPalette
              classes={classes}
              name={labels["palette.navy"]}
              width={PALETTE_WIDTH}
              height={PALETTE_HEIGHT}
              colorSchema={palettes.navy}
              disableSelection={true} />
          </div>
          <div id="earth" className={classes.colorsPalette} onClick={this.setPalette}>
            <ColorPalette
              classes={classes}
              name={labels["palette.earth"]}
              width={PALETTE_WIDTH}
              height={PALETTE_HEIGHT}
              colorSchema={palettes.earth}
              disableSelection={true} />
          </div>
        </div>
      </div>
    );
  }
}
