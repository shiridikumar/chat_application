import logo from './logo.svg';
import './App.css';
import React, { Component } from 'react'
import {
  BrowserRouter,
  Routes,
  Route,
  createBrowserRouter,
} from "react-router-dom";
import Homescreen from './components/Homescree';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>

          <Route exact path="/" element={< Homescreen/>} />
          {/* <Route exact path="/signin" element={<Signin />} /> */}
          {/* <Route exact path="/dashboard" element={<Dashboard />} /> */}
          {/* <Route exact path="/signup" element={<SignUp />} /> */}

        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
