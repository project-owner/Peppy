/* Copyright 2022 Peppy Player peppy.player@gmail.com
 
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

import React from 'react';
import { Button } from '@material-ui/core';
import Share from "../components/Share";
import AddIcon from '@material-ui/icons/Add';

export default class ShareFolder extends React.Component {
  render() {
    const { classes, labels, shares, addShare, deleteShare, updateState } = this.props;

    if (shares === null || shares === undefined) {
      return labels["supported.for.Linux"];
    }

    return (
      <div style={{ width: "32rem", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
        <span style={{ width: "100%", display: "flex", flexDirection: "row", justifyContent: "space-between" }}>
          <div>
            <Button variant="contained" className={classes.addButton} style={{ justifyContent: "flex-start" }}
              onClick={() => { addShare() }}
            >
              {labels["share.folder"]}
              <AddIcon style={{ marginLeft: "1rem" }} />
            </Button>
          </div>
        </span>
        {shares && shares.length > 0 && shares.map(function (share, index) {
          return <Share key={index} index={index} classes={classes} labels={labels} share={share} deleteShare={deleteShare} updateState={updateState}/>
        })}
      </div>
    );
  }
}
