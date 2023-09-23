/* Copyright 2023 Peppy Player peppy.player@gmail.com
 
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
import HomeScreen from "../config/HomeScreen";
import ScreensaverScreen from "../config/ScreensaverScreen";
import LanguageScreen from "../config/LanguageScreen";
import CollectionScreen from "../config/CollectionScreen";
import PlayerScreen from "../config/PlayerScreen";
import FileBrowser from "../config/FileBrowser";

export const configSections = [
  "home.menu", "home.navigator", "screensaver.menu", "screensaver.delay", "languages.menu", "collection.menu", 
  "player.screen"
];

export default class ConfigTab extends React.Component {
  render() {
    const { params, classes, topic, updateState, labels, languages, language } = this.props;

    return (
      <main className={classes.content}>
        <div className={classes.toolbar} />
        {topic === 0 && 
            <HomeScreen 
                menuParams={params["home.menu"]} 
                navigatorParams={params["home.navigator"]} 
                labels={labels} 
                classes={classes} 
                updateState={updateState} 
            />
        }
        {topic === 1 && 
            <ScreensaverScreen
                menuParams={params["screensaver.menu"]}
                delayParams={params["screensaver.delay"]["delay"]} 
                labels={labels} 
                classes={classes} 
                updateState={updateState}
            />
        }
        {topic === 2 && 
            <LanguageScreen 
                params={params["languages.menu"]} 
                labels={labels} 
                classes={classes} 
                updateState={updateState} 
                languages={languages} 
                language={language} 
            />
        }
        {topic === 3 && 
            <CollectionScreen 
                params={params["collection.menu"]} 
                labels={labels} 
                classes={classes} 
                updateState={updateState} 
            />
        }
        {topic === 4 && 
            <PlayerScreen 
                params={params["player.screen"]} 
                labels={labels} 
                classes={classes} 
                updateState={updateState} 
            />
        }
        {topic === 5 && 
            <FileBrowser 
                params={params["file.browser"]} 
                labels={labels} 
                classes={classes} 
                updateState={updateState} 
            />
        }
      </main>
    );
  }
}
