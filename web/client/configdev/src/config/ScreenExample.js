import React from 'react';
import Box from '@material-ui/core/Box';
import {COLOR_DARK, COLOR_DARK_LIGHT, COLOR_MEDIUM, COLOR_BRIGHT, COLOR_CONTRAST, 
  COLOR_LOGO, COLOR_MUTE, COLOR_WEB_BGR} from "./Colors";

export default class ScreenExample extends React.Component {
  getColors = (colorGroup, name) => {
    if (!colorGroup) {
      return "#000";
    }

    let r = colorGroup[0];
    let g = colorGroup[1];
    let b = colorGroup[2];

    if (this.props.selected === name) {
      r = this.props.currentColor[0];
      g = this.props.currentColor[1];
      b = this.props.currentColor[2];
    }
    return "rgb(" + r + "," + g + "," + b + ")";
  }

  render() {
    const { classes } = this.props;

    const colorSchema = { ...this.props.colorSchema };
    const color_web_bgr = colorSchema[COLOR_WEB_BGR];
    const color_dark = colorSchema[COLOR_DARK];
    const color_dark_light = colorSchema[COLOR_DARK_LIGHT];
    const color_medium = colorSchema[COLOR_MEDIUM];
    const color_bright = colorSchema[COLOR_BRIGHT];
    const color_contrast = colorSchema[COLOR_CONTRAST];
    const color_logo = colorSchema[COLOR_LOGO];
    const color_mute = colorSchema[COLOR_MUTE];
    return (
      <div className={classes.screenExamplesContainer}>
        <div className={classes.exampleContainer}>
          <div style={{ display: "flex" }}>
            <Box
              bgcolor={this.getColors(color_dark_light, "color_dark_light")}
              style={{ 
                width: "320px", 
                height: "40px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: this.getColors(color_contrast, "color_contrast")
              }}
            >          
              Title
            </Box>
          </div>
          <div style={{ display: "flex", flexDirection: "row"}}>
            <div style={{ display: "flex", flexDirection: "column"}}>
              <Box bgcolor={"black"} style={{width: "80px", height: "60px"}}/>          
              <Box
                bgcolor={this.getColors(color_dark_light, "color_dark_light")}
                style={{ 
                  width: "80px", 
                  height: "40px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: this.getColors(color_bright, "color_bright")
                }}
              >          
                <b>{"<<"}</b>          
              </Box>
              <Box bgcolor={"black"} style={{width: "80px", height: "60px"}}/>    
            </div>
            <Box
                bgcolor={this.getColors(color_dark, "color_dark")}
                style={{width: "160px", height: "160px"}}
              /> 
            <div style={{ display: "flex", flexDirection: "column"}}>
              <Box bgcolor={"black"} style={{width: "80px", height: "60px"}}/>          
              <Box
                bgcolor={this.getColors(color_dark_light, "color_dark_light")}
                style={{ 
                  width: "80px", 
                  height: "40px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: this.getColors(color_bright, "color_bright")
                }}
              >          
                <b>{">>"}</b>          
              </Box>
              <Box bgcolor={"black"} style={{width: "80px", height: "60px"}}/>    
            </div>     
          </div>
          <div
              style={{ 
                width: "320px", 
                height: "40px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background: this.getColors(color_dark_light, "color_dark_light"),
                color: this.getColors(color_contrast, "color_contrast")
              }}
            > 
              <Box 
                bgcolor={this.getColors(color_bright, "color_bright")} 
                borderRadius="10px" 
                style={{width: "20px", height: "20px", zIndex: "100"}}
              />
              <span style={{
                width: "280px", 
                height: "2px", 
                marginLeft: "-60px",
                background: this.getColors(color_medium, "color_medium")
              }}/>
              <Box 
                bgcolor={this.getColors(color_mute, "color_mute")} 
                borderRadius="10px" 
                style={{width: "20px", height: "20px", zIndex: "100", marginLeft: "-60px"}}
              />
            </div>
          </div>
          <div style={{marginLeft: "1rem"}}>
            <Box
              bgcolor={this.getColors(color_web_bgr, "color_web_bgr")}
              style={{ 
                width: "320px", 
                height: "240px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: this.getColors(color_logo, "color_logo")
              }}
            >          
              PYTHON PYGAME PLAYER
            </Box>
          </div>

      </div>
    );
  }
}

