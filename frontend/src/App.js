/**
 * @file App.js
 * @description Main application component. Manages task state, filtering, and API interactions.
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TaskList from './components/TaskList';
import TaskForm from './components/TaskForm';
import SearchBar from './components/SearchBar';
import Stats from './components/Stats';
import './App.css';

/** Base URL for backend API calls (proxied via nginx). */
const API_URL = '/api';

/**
 * Root application component.
 * Handles task CRUD operations, filtering, and search.
 * @returns {JSX.Element} The rendered application.
 */
function App() {
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  /** Fetch tasks from the API with the current filter applied. */
  const fetchTasks = async () => {
    try {
      setLoading(true);
      const params = {};
      // Explicitly filter status to avoid sending "today" as a status,
      // which causes conflicts in the backend query logic.
      if (filter === 'active' || filter === 'done') params.status = filter;
      if (filter === 'today') params.today = new Date().toISOString().split('T')[0]; //
      const res = await axios.get(`${API_URL}/tasks`, { params });
      setTasks(res.data);
    } catch (err) { console.error('Failed to fetch tasks:', err); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchTasks(); }, [filter]);

  /**
   * Create a new task via the API.
   * @param {Object} task - The task data with title and optional description.
   */
  const addTask = async (task) => {
    try { await axios.post(`${API_URL}/tasks`, task); fetchTasks(); }
    catch (err) { console.error('Failed to create task:', err); }
  };
  /**
   * Toggle a task's active status.
   * @param {number} id - The task ID.
   * @param {boolean} isActive - The current active state.
   */
  const toggleTask = async (id, isActive) => {
    try { await axios.put(`${API_URL}/tasks/${id}`, { is_active: !isActive }); fetchTasks(); }
    catch (err) { console.error('Failed to update task:', err); }
  };
  /**
   * Delete a task by ID.
   * @param {number} id - The task ID to delete.
   */
  const deleteTask = async (id) => {
    try { await axios.delete(`${API_URL}/tasks/${id}`); fetchTasks(); }
    catch (err) { console.error('Failed to delete task:', err); }
  };
  /**
   * Search tasks by query string, or reload all tasks if query is empty.
   * @param {string} query - The search query.
   */
  const searchTasks = async (query) => {
    if (!query.trim()) { fetchTasks(); return; }
    try { const res = await axios.get(`${API_URL}/search`, { params: { q: query } }); setTasks(res.data); }
    catch (err) { console.error('Search failed:', err); }
  };

  return (
    <div className="app">
      <header><h1>📋 Task Manager</h1><Stats apiUrl={API_URL} /></header>
      <main>
        <SearchBar onSearch={searchTasks} />
        <div className="filters">
          {['all', 'active', 'done', 'today'].map(f => (
            <button key={f} className={filter === f ? 'active' : ''} onClick={() => setFilter(f)}>
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
        <TaskForm onSubmit={addTask} />
        {loading ? <p className="loading">Loading...</p> : <TaskList tasks={tasks} onToggle={toggleTask} onDelete={deleteTask} />}
      </main>
    </div>
  );
}
export default App;
