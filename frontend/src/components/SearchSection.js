import React, { useState } from 'react';
import axios from 'axios';

const API_GATEWAY_URL = 'https://ur2wyo21r1.execute-api.us-east-1.amazonaws.com/prod';
const API_KEY = 'EFFxLhQZQC5PmtAZww5953OrhluY72A2bNZAVFG4';

function SearchSection({ showMessage }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      showMessage('Please enter a search query', 'error');
      return;
    }

    setLoading(true);
    setResults([]);

    try {
      const response = await axios.get(`${API_GATEWAY_URL}/search`, {
        params: { q: query },
        headers: { 'x-api-key': API_KEY }
      });

      if (response.data && response.data.results) {
        setResults(response.data.results);
        showMessage(`Found ${response.data.results.length} photos`, 'success');
      } else {
        setResults([]);
        showMessage('No photos found', 'error');
      }
    } catch (error) {
      console.error('Search error:', error);
      showMessage(`Search failed: ${error.response?.data?.message || error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="section">
      <h2>🔍 Search Photos</h2>
      <form onSubmit={handleSearch}>
        <div className="search-container">
          <input
            type="text"
            placeholder="Try: 'Show me dogs' or 'Find flowers'"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading && <span className="spinner"></span>}
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {results.length > 0 && (
        <div className="results">
          <h3>Search Results ({results.length})</h3>
          <div className="image-grid">
            {results.map((url, index) => (
              <div key={index} className="image-card">
                <img src={url} alt={`Result ${index + 1}`} />
                <p>{url.split('/').pop()}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default SearchSection;
