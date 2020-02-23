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
import { List, ListItem, ListItemText } from "@material-ui/core";

export default class Navigator extends React.Component {
  render() {
    const { menu, classes, currentMenuItem } = this.props;

    if (!menu ) {
      return null;
    }

    return (
      <div className={classes.navigator}>
        {<List value={currentMenuItem}>
            {menu.map((text, index) => (
              <ListItem
                button
                key={text}
                selected={currentMenuItem === index}
                onClick={event => this.props.handleListItemClick(event, index)}
              >
                <ListItemText primary={text} classes={{ primary: classes.listItemText }} />
              </ListItem>
            ))}
          </List>
        }
      </div>
    );
  }
}
