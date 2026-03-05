/**
 * @file TaskList.test.js
 * @description Tests for the TaskList component.
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TaskList from './TaskList';

const mockTasks = [
    { id: 1, title: 'Task One', description: 'First', is_active: true, created_at: '2026-03-05T12:00:00' },
    { id: 2, title: 'Task Two', description: 'Second', is_active: false, created_at: '2026-03-04T10:00:00' },
];

describe('TaskList', () => {
    test('renders "No tasks found" when list is empty', () => {
        render(<TaskList tasks={[]} onToggle={jest.fn()} onDelete={jest.fn()} />);
        expect(screen.getByText(/No tasks found/i)).toBeInTheDocument();
    });

    test('renders all task titles', () => {
        render(<TaskList tasks={mockTasks} onToggle={jest.fn()} onDelete={jest.fn()} />);
        expect(screen.getByText('Task One')).toBeInTheDocument();
        expect(screen.getByText('Task Two')).toBeInTheDocument();
    });

    test('renders task descriptions', () => {
        render(<TaskList tasks={mockTasks} onToggle={jest.fn()} onDelete={jest.fn()} />);
        expect(screen.getByText('First')).toBeInTheDocument();
        expect(screen.getByText('Second')).toBeInTheDocument();
    });

    test('calls onToggle when checkbox is clicked', () => {
        const onToggle = jest.fn();
        render(<TaskList tasks={mockTasks} onToggle={onToggle} onDelete={jest.fn()} />);
        const checkboxes = screen.getAllByRole('checkbox');
        fireEvent.click(checkboxes[0]);
        expect(onToggle).toHaveBeenCalledWith(1, true);
    });

    test('calls onDelete when delete button is clicked', () => {
        const onDelete = jest.fn();
        render(<TaskList tasks={mockTasks} onToggle={jest.fn()} onDelete={onDelete} />);
        const deleteButtons = screen.getAllByText('🗑');
        fireEvent.click(deleteButtons[0]);
        expect(onDelete).toHaveBeenCalledWith(1);
    });

    test('applies line-through style to inactive tasks', () => {
        render(<TaskList tasks={mockTasks} onToggle={jest.fn()} onDelete={jest.fn()} />);
        const taskTwoTitle = screen.getByText('Task Two');
        expect(taskTwoTitle).toHaveStyle('text-decoration: line-through');
    });
});
