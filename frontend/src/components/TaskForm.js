/**
 * @file TaskForm.js
 * @description Form component to create a new task with title and optional description.
 */
import React, { useState } from 'react';

/**
 * Renders a form to add a new task. Expands to show a description field on focus.
 * @param {Object} props
 * @param {Function} props.onSubmit - Callback invoked with {title, description} on form submit.
 * @returns {JSX.Element}
 */
function TaskForm({ onSubmit }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [expanded, setExpanded] = useState(false);
  const handleSubmit = (e) => { e.preventDefault(); if (!title.trim()) return; onSubmit({ title, description }); setTitle(''); setDescription(''); setExpanded(false); };
  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: 20 }}>
      <div style={{ display: 'flex', gap: 8 }}>
        <input type="text" placeholder="Add a new task..." value={title} onChange={e => setTitle(e.target.value)} onFocus={() => setExpanded(true)} style={{ flex: 1, padding: 12, border: '1px solid #ddd', borderRadius: 8, fontSize: '1rem' }} />
        <button type="submit" style={{ padding: '12px 24px', background: '#4a90d9', color: 'white', border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: '1rem' }}>Add</button>
      </div>
      {expanded && <textarea placeholder="Description (optional)" value={description} onChange={e => setDescription(e.target.value)} rows={2} style={{ width: '100%', padding: 12, border: '1px solid #ddd', borderRadius: 8, marginTop: 8, fontSize: '0.9rem' }} />}
    </form>
  );
}
export default TaskForm;
