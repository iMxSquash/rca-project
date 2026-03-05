/**
 * @file SearchBar.test.js
 * @description Tests for the SearchBar component.
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import SearchBar from './SearchBar';

describe('SearchBar', () => {
    test('renders the search input', () => {
        render(<SearchBar onSearch={jest.fn()} />);
        expect(screen.getByPlaceholderText(/Search tasks/i)).toBeInTheDocument();
    });

    test('renders the search button', () => {
        render(<SearchBar onSearch={jest.fn()} />);
        expect(screen.getByText('🔍')).toBeInTheDocument();
    });

    test('calls onSearch on form submit', () => {
        const onSearch = jest.fn();
        render(<SearchBar onSearch={onSearch} />);
        const input = screen.getByPlaceholderText(/Search tasks/i);
        fireEvent.change(input, { target: { value: 'hello' } });
        fireEvent.submit(input.closest('form'));
        expect(onSearch).toHaveBeenCalledWith('hello');
    });

    test('calls onSearch with empty string when input is cleared', () => {
        const onSearch = jest.fn();
        render(<SearchBar onSearch={onSearch} />);
        const input = screen.getByPlaceholderText(/Search tasks/i);
        fireEvent.change(input, { target: { value: 'test' } });
        fireEvent.change(input, { target: { value: '' } });
        expect(onSearch).toHaveBeenCalledWith('');
    });

    test('updates input value on typing', () => {
        render(<SearchBar onSearch={jest.fn()} />);
        const input = screen.getByPlaceholderText(/Search tasks/i);
        fireEvent.change(input, { target: { value: 'query' } });
        expect(input.value).toBe('query');
    });
});
