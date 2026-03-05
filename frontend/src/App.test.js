/**
 * @file App.test.js
 * @description Tests for the main App component.
 */
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import App from './App';

jest.mock('axios');

describe('App', () => {
    beforeEach(() => {
        axios.get.mockResolvedValue({ data: [] });
    });

    afterEach(() => {
        jest.restoreAllMocks();
    });

    test('renders the app title', async () => {
        render(<App />);
        expect(screen.getByText(/Task Manager/i)).toBeInTheDocument();
    });

    test('renders the search bar', async () => {
        render(<App />);
        expect(screen.getByPlaceholderText(/Search tasks/i)).toBeInTheDocument();
    });

    test('renders filter buttons', async () => {
        render(<App />);
        expect(screen.getByText('All')).toBeInTheDocument();
        expect(screen.getByText('Active')).toBeInTheDocument();
        expect(screen.getByText('Done')).toBeInTheDocument();
        expect(screen.getByText('Today')).toBeInTheDocument();
    });

    test('fetches tasks on mount', async () => {
        render(<App />);
        await waitFor(() => {
            expect(axios.get).toHaveBeenCalledWith('/api/tasks', expect.anything());
        });
    });

    test('displays tasks when API returns data', async () => {
        axios.get.mockResolvedValueOnce({
            data: [
                { id: 1, title: 'Test Task', description: 'Desc', is_active: true, created_at: '2026-03-05T12:00:00' },
            ],
        });

        render(<App />);
        await waitFor(() => {
            expect(screen.getByText('Test Task')).toBeInTheDocument();
        });
    });

    test('shows loading state initially', () => {
        axios.get.mockReturnValue(new Promise(() => { })); // never resolves
        render(<App />);
        expect(screen.getByText(/Loading/i)).toBeInTheDocument();
    });
});
