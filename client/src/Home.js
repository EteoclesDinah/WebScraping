import React, { useState } from "react";
import './App.css';

const Home = () => {
    const [url, setUrl] = useState("");
    const [urls, setUrls] = useState([]);

    const handleAddUrl = () => {
        if (url.trim()) {
            setUrls([...urls, url]);
            setUrl("");
        }
    };

    const handleRemoveUrl = (indexToRemove) => {
        const filteredUrls = urls.filter((_, index) => index !== indexToRemove);
        setUrls(filteredUrls);
    };

    const handleSearch = async () => {
        if (urls.length === 0) {
            alert("Please add at least one URL.");
            return;
        }
    
        try {
            const response = await fetch("http://localhost:5000/scrape", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ urls }),
            });
    
            const data = await response.json();
    
            if (response.ok) {
                alert("Scraping started successfully");
            } else {
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            alert("Error connecting to the server.");
            console.error(error);
        }
    };
    

    return (
        <div className="container">
            <div className="homeDescription">
                <h1>Your Go-To Web Scraping Tool!!</h1>
                <p>Want to extract web content seamlessly?</p>
                <p>Look no further!</p>
                <p>Harness the power of web scraping to collect data efficiently.<br /> Whether you're gathering information for research,<br />
                    monitoring trends, or compiling useful resources, <br />our tool simplifies the process for you.</p>
            </div>

            <div className="scrappingContent">
                <input
                    type="text"
                    placeholder="Paste URL here"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                />

                <button className="addButton" onClick={handleAddUrl}>Add</button>

                <div className="urlList">
                    <h2>Added URLs</h2>
                    <ul>
                        {urls.map((url, index) => (
                            <li key={index}>
                                {url}
                                <button
                                    className="removeButton"
                                    onClick={() => handleRemoveUrl(index)}
                                >
                                    Remove
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>

                <button className="searchButton" onClick={handleSearch}>Search</button>

                
            </div>
        </div>
    );
};

export default Home;
