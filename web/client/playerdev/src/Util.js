/* Copyright 2024 Peppy Player peppy.player@gmail.com
 
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

export function getSecondsFromString(str) {
  if (!str) {
    return 0;
  }
  var nums = str.split(":");
  var result = 0;

  if (nums.length === 3) {
    result = (parseInt(nums[0]) * 3600) + (parseInt(nums[1]) * 60) + (parseInt(nums[2]));
  } else if (nums.length === 2) {
    result = (parseInt(nums[0]) * 60) + (parseInt(nums[1]));
  }

  return result;
};

export function getStringFromSeconds(sec) {
  if (sec === null || sec === 'undefined') {
    return "";
  }

  var s = parseInt(sec);
  var hours = parseInt(s / 3600);
  var minutes = parseInt(s / 60);
  var seconds = parseInt(s % 60);
  var label = "";

  if (hours !== 0) {
    label += hours.toString();
    if (label.length === 1) {
      label = "0" + label;
    }
    label += ":";
    minutes = parseInt((s - hours * 3600) / 60);
  }

  const min = minutes.toString();
  if (min.length === 1) {
    label += "0";
  }
  label += min + ":";

  const secs = seconds.toString();
  if (secs.length === 1) {
    label += "0";
  }
  label += secs;

  return label;
};