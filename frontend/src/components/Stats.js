/**
 * @file Stats.js
 * @description Displays task statistics (total, active, done) with auto-refresh.
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';

/**
 * Fetches and displays task statistics from the API, refreshing every 5 seconds.
 * @param {Object} props
 * @param {string} props.apiUrl - Base API URL to fetch stats from.
 * @returns {JSX.Element|null}
 */
function Stats({ apiUrl }) {
  const [stats, setStats] = useState(null);
  useEffect(() => {
    const fetchStats = async () => { try { const res = await axios.get(`${apiUrl}/stats`); setStats(res.data); } catch (e) { } };
    fetchStats(); const i = setInterval(fetchStats, 5000); return () => clearInterval(i);
  }, [apiUrl]);
  if (!stats) return null;
  return (
    <div style={{ display: 'flex', gap: 16 }}>
      <span style={{ fontSize: '0.85rem', padding: '4px 12px', background: '#f0f0f0', borderRadius: 12 }}>📊 {stats.total} total</span>
      <span style={{ fontSize: '0.85rem', padding: '4px 12px', background: '#f0f0f0', borderRadius: 12 }}>✅ {stats.active} active</span>
      <span style={{ fontSize: '0.85rem', padding: '4px 12px', background: '#f0f0f0', borderRadius: 12 }}>☑️ {stats.done} done</span>
    </div>
  );
}
export default Stats;
