import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import './App.css';
import HeaderSection from "./HeaderSection";
import Home from "./Home";
import About from "./About";
import Services from "./Services";
import FAQ from "./FAQ";
import Contact from "./Contact"; 

function App() {

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

      
    </div>
  )
}

export default App;