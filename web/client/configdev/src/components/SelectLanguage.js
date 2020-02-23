/* Copyright 2019 Peppy Player peppy.player@gmail.com
 
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
import { Select, MenuItem } from "@material-ui/core";

export default class SelectLanguage extends React.Component {
  render() {
    const { classes, languages, language, flags } = this.props;

    if (!languages || !flags) {
      return null;
    }

    let translations = {};
    languages.forEach((lang) => {
      if (lang.name === language) {
        translations = lang.translations;
      }
    })

    return (
      <div className={classes.language}>
        <Select
          className={classes.select}
          value={language}
          onChange={this.props.onChange}
          inputProps={{
            classes: {
              icon: classes.icon
            }
          }}
        >
          {languages.map((lang, index) => (
            <MenuItem key={index} value={lang.name}><img src={flags[lang.name]} alt={lang.name} className={classes.languageStyle}/>
              <span className={classes.languageFont}>{translations[lang.name]}</span>
            </MenuItem>
          ))}
        </Select>
      </div>
    );
  }
}
