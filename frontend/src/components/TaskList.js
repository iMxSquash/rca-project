/**
 * @file TaskList.js
 * @description Renders a list of tasks with toggle and delete actions.
 */
import React from 'react';

/**
 * Displays a list of tasks with checkboxes to toggle status and delete buttons.
 * @param {Object} props
 * @param {Array} props.tasks - Array of task objects to display.
 * @param {Function} props.onToggle - Callback(id, isActive) to toggle a task.
 * @param {Function} props.onDelete - Callback(id) to delete a task.
 * @returns {JSX.Element}
 */
function TaskList({ tasks, onToggle, onDelete }) {
  if (tasks.length === 0) return <p style={{ textAlign: 'center', color: '#999', padding: 40 }}>No tasks found</p>;
  return (
    <ul style={{ listStyle: 'none' }}>
      {tasks.map(task => (
        <li key={task.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 16, marginBottom: 8, background: 'white', borderRadius: 8, boxShadow: '0 1px 3px rgba(0,0,0,0.1)', opacity: task.is_active ? 1 : 0.6 }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
            <input type="checkbox" checked={!task.is_active} onChange={() => onToggle(task.id, task.is_active)} />
            <div>
              <h3 style={{ fontSize: '1rem', textDecoration: task.is_active ? 'none' : 'line-through' }}>{task.title}</h3>
              {task.description && <p style={{ fontSize: '0.85rem', color: '#666' }}>{task.description}</p>}
              <span style={{ fontSize: '0.75rem', color: '#999' }}>{new Date(task.created_at).toLocaleDateString()}</span>
            </div>
          </div>
          <button onClick={() => onDelete(task.id)} style={{ background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer', opacity: 0.5 }}>🗑</button>
        </li>
      ))}
    </ul>
  );
}
export default TaskList;
