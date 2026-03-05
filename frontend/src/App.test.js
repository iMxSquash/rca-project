/**
 * @file App.test.js
 * @description Tests for the main App component.
 */
import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import App from './App';

jest.mock('axios');

/**
 * Helper: mock axios.get to return different data depending on the URL.
 * @param {Array} tasks - tasks to return for /api/tasks
 * @param {Object|null} stats - stats to return for /api/stats
 */
function mockAxiosGet(tasks = [], stats = null) {
    axios.get.mockImplementation((url) => {
        if (url.includes('/stats')) {
            return Promise.resolve({ data: stats || { total: 0, active: 0, done: 0 } });
        }
        return Promise.resolve({ data: tasks });
    });
}

describe('App', () => {
    beforeEach(() => {
        jest.useFakeTimers();
        mockAxiosGet();
    });

    afterEach(async () => {
        // Flush pending timers inside act() to avoid act() warnings
        // from Stats setInterval triggering setStats
        await act(async () => {
            jest.runOnlyPendingTimers();
        });
        jest.useRealTimers();
        jest.restoreAllMocks();
    });

    test('renders the app title', async () => {
        await act(async () => { render(<App />); });
        expect(screen.getByText(/Task Manager/i)).toBeInTheDocument();
    });

    test('renders the search bar', async () => {
        await act(async () => { render(<App />); });
        expect(screen.getByPlaceholderText(/Search tasks/i)).toBeInTheDocument();
    });

    test('renders filter buttons', async () => {
        await act(async () => { render(<App />); });
        expect(screen.getByText('All')).toBeInTheDocument();
        expect(screen.getByText('Active')).toBeInTheDocument();
        expect(screen.getByText('Done')).toBeInTheDocument();
        expect(screen.getByText('Today')).toBeInTheDocument();
    });

    test('fetches tasks on mount', async () => {
        await act(async () => { render(<App />); });
        await waitFor(() => {
            expect(axios.get).toHaveBeenCalledWith('/api/tasks', expect.anything());
        });
    });

    test('displays tasks when API returns data', async () => {
        mockAxiosGet(
            [{ id: 1, title: 'Test Task', description: 'Desc', is_active: true, created_at: '2026-03-05T12:00:00' }],
            { total: 1, active: 1, done: 0 }
        );

        await act(async () => { render(<App />); });
        await waitFor(() => {
            expect(screen.getByText('Test Task')).toBeInTheDocument();
        });
    });

    test('shows loading state initially', () => {
        axios.get.mockImplementation(() => new Promise(() => { }));
        render(<App />);
        expect(screen.getByText(/Loading/i)).toBeInTheDocument();
    });
});
