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
