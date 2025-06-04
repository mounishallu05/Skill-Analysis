import { render, screen } from '@testing-library/react';
import App from './App';

test('renders LinkedIn Skill Analysis Bot title', () => {
  render(<App />);
  const titleElement = screen.getByText(/LinkedIn Skill Analysis Bot/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders upload form', () => {
  render(<App />);
  const urlInput = screen.getByPlaceholderText(/linkedin\.com\/in\/username/i);
  expect(urlInput).toBeInTheDocument();
  
  const fileInput = screen.getByLabelText(/Upload LinkedIn PDF/i);
  expect(fileInput).toBeInTheDocument();
  
  const submitButton = screen.getByText(/Analyze/i);
  expect(submitButton).toBeInTheDocument();
}); 