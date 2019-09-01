import React from 'react';
import ReactDOM from 'react-dom';
import Peppy from './Peppy';
import './index.css';
import * as serviceWorker from './serviceWorker';

ReactDOM.render(<Peppy />, document.getElementById('root'));
serviceWorker.unregister();
