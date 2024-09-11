import React from "react";
import './App.css'
import { NavLink } from "react-router-dom";

const HeaderSection = () => {
    return (
        <header className="header">
            <div className="logo">
                <img 
                src=""/>
            </div>
            <nav className="nav-bar">
                <ul>
                    <li>
                        <NavLink to="/Home" exact activeClassName="active">
                            Home
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/About" activeClassName="active">
                            About
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/Services" activeClassName="active">
                            Services
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/FAQ" activeClassName="active">
                            FAQ
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/Contact" activeClassName="active">
                            Contact
                        </NavLink>
                    </li>
                </ul>
            </nav>
        </header>
    );
};

export default HeaderSection;