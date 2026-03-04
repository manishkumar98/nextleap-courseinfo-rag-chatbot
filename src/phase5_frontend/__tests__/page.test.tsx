import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import NextLeapChatApp from '../src/app/page';

describe('NextLeapChatApp UI', () => {
    it('renders the initial welcome message from the Academic Advisor', () => {
        render(<NextLeapChatApp />);
        expect(screen.getByText(/Hello! I am your/i)).toBeInTheDocument();
        expect(screen.getByText(/NextLeap Academic Advisor/i)).toBeInTheDocument();
    });

    it('renders the 3-column layout headers', () => {
        render(<NextLeapChatApp />);
        // Check left chats panel
        expect(screen.getByText('Chats')).toBeInTheDocument();
        // Check main chat header
        expect(screen.getByText('Theron Trump')).toBeInTheDocument();
        // Check right sources panel
        expect(screen.getByText('Sources & Verification')).toBeInTheDocument();
    });

    it('allows user to type a message in the input and render it', async () => {
        render(<NextLeapChatApp />);

        const inputElement = screen.getByPlaceholderText('Type your question about NextLeap...');
        fireEvent.change(inputElement, { target: { value: 'Who are the mentors for PM fellowship?' } });

        // Check if input value updated
        expect(inputElement).toHaveValue('Who are the mentors for PM fellowship?');

        // We mock fetch or just test if it adds user message to DOM. 
        // Without mocking fetch, it will hit error catch block, but it will still render user msg first.
        const sendButton = screen.getByRole('button', { name: /Send query/i });
        fireEvent.click(sendButton);

        // Ensure user message is in the document
        await waitFor(() => {
            expect(screen.getByText('Who are the mentors for PM fellowship?')).toBeInTheDocument();
        });
    });
});
