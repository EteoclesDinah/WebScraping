import React, { useState } from "react";
import './App.css';

const Home = () => {
    const [url, setUrl] = useState("");
    const [urls, setUrls] = useState([]);
    const [scrapingStatus, setScrapingStatus] = useState("");

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

        setScrapingStatus("Scraping in progress...");
    
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
                setScrapingStatus("Scraping completed. Check output.csv for results.");
            } else {
                setScrapingStatus(`Error: ${data.error}`);
            }
        } catch (error) {
            setScrapingStatus("Error connecting to the server.");
            console.error(error);
        }
    };

    return (
        <div className="container">
            <div className="homeDescription">
                <h1>Your Go-To Web Scraping Tool!!</h1>
                <p>Want to extract web content seamlessly?</p>
                <p>Look no further!</p>
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

                <p>{scrapingStatus}</p>  {/* Display scraping status */}
            </div>
        </div>
    );
};

export default Home;
