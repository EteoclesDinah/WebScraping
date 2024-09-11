import React from "react";
import { useState, useEffect } from "react";

import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import './App.css';
import HeaderSection from "./HeaderSection";
import Home from "./Home";
import About from "./About";
import Services from "./Services";
import FAQ from "./FAQ";
import Contact from "./Contact"; 

function App() {

  const [data, setData] = useState([{}])

  useEffect(() => {
    fetch("/members").then(
      res => res.json()
    ).then(
      data => {
        setData(data)
        console.log(data)
      }
    )
  }, [])

  return (
    <div>
      <Router>
      <div className="appContainer">
        <HeaderSection />
        <Routes>
          <Route path="/home" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/services" element={<Services />} />
          <Route path="/faq" element={<FAQ />} />
          <Route path="/contact" element={<Contact />} />
        </Routes>
        </div>
       </Router> 

      {(typeof data.members === 'undefined') ? (
        <p>Loading......</p>
      ) : (
        data.members.map((member, i) => (
          <p key={i}>{member}</p>
        ))
      )}
    </div>
  )
}

export default App;