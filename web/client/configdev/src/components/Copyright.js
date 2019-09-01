import React from "react";

export default class Copyright extends React.Component {
  render() {
    const { classes } = this.props;
    return (
      <div className={classes.footerCopyright}>
        Peppy Player &copy; 2019 Holbein Edition
      </div>
    );
  }
}
