/**
 * @file SearchBar.js
 * @description Search input with live-clear and submit functionality.
 */
import React, { useState } from 'react';

/**
 * Renders a search form that triggers a callback on submit or when cleared.
 * @param {Object} props
 * @param {Function} props.onSearch - Callback invoked with the search query string.
 * @returns {JSX.Element}
 */
function SearchBar({ onSearch }) {
  const [query, setQuery] = useState('');
  return (
    <form onSubmit={e => { e.preventDefault(); onSearch(query); }} style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
      <input type="text" placeholder="Search tasks..." value={query} onChange={e => { setQuery(e.target.value); if (e.target.value === '') onSearch(''); }} style={{ flex: 1, padding: 10, border: '1px solid #ddd', borderRadius: 8 }} />
      <button type="submit" style={{ padding: '10px 16px', background: 'white', border: '1px solid #ddd', borderRadius: 8, cursor: 'pointer' }}>🔍</button>
    </form>
  );
}
export default SearchBar;
