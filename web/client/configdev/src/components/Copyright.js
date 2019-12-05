import React from "react";

export default class Copyright extends React.Component {
  render() {
    const { classes, release } = this.props;
    const name = release["product.name"];
    const edition = release["edition.name"];
    const year = release["year"];

    return (
      <div className={classes.footerCopyright}>
        {name} &copy; {year} {edition}
      </div>
    );
  }
}
