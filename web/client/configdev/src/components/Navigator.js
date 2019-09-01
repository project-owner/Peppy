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
