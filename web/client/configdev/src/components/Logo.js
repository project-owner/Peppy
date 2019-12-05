import React from "react";

export default class Logo extends React.Component {
  render() {
    const { classes, release } = this.props;
    const imagePath = "/icon/peppy-logo.svg";
    const name = release["product.name"].toUpperCase();
    const edition = release["edition.name"].toUpperCase();

    return (
      <>
        <div className={classes.logoIcon}>
          <a href="/">
            <img src={imagePath} alt="Logo"/>
          </a>
        </div>
        <div className={classes.logoText}>
          <a href="/" className={classes.logoLink}>
            <div className={classes.logoNameText}>{name}</div>
            <div className={classes.logoEditionText}>{edition}</div>
          </a>
        </div>
      </>
    );
  }
}
