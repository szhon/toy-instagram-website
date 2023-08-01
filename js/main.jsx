import React from 'react';
import ReactDOM from 'react-dom';
import Board from './board';

// console.log(document.getElementById('reactEntry'));

// This method is only called once
ReactDOM.render(
  // Insert the post component into the DOM
  <Board url="/api/v1/posts/" />,
  document.getElementById('reactEntry'),
);
