/**
 * @file FilterPanel.js
 * @description A row of filter buttons to switch between task views.
 */
import React from 'react';

/**
 * Renders a set of filter buttons (all, active, done, today).
 * @param {Object} props
 * @param {string} props.currentFilter - The currently active filter.
 * @param {Function} props.onFilterChange - Callback when a filter is selected.
 * @returns {JSX.Element}
 */
function FilterPanel({ currentFilter, onFilterChange }) {
  const filters = ['all', 'active', 'done', 'today'];
  return (
    <div className="filter-panel">
      {filters.map(f => (
        <button key={f} className={currentFilter === f ? 'active' : ''} onClick={() => onFilterChange(f)}>
          {f.charAt(0).toUpperCase() + f.slice(1)}
        </button>
      ))}
    </div>
  );
}
export default FilterPanel;
