/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AppLayout } from './App';

// Mock child components to focus on AppLayout logic
jest.mock('@/pages/Notifications', () => ({
  Notifications: () => <div data-testid="notifications-page">Notifications Page</div>
}));

jest.mock('@/pages/PolicyChat', () => ({
  PolicyChat: () => <div data-testid="policy-chat-page">Policy Chat Page</div>
}));

jest.mock('@/components/Sidebar', () => ({
  Sidebar: ({ onClose }: { onClose?: () => void }) => (
    <div data-testid="sidebar">
      Sidebar Component
      {onClose && <button data-testid="close-sidebar" onClick={onClose}>Close</button>}
    </div>
  )
}));

jest.mock('@/components/404NotFound', () => ({
  NotFoundComponent: () => <div data-testid="not-found-page">404 Not Found</div>
}));

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Menu: () => <span data-testid="menu-icon">Menu</span>,
  X: () => <span data-testid="x-icon">X</span>
}));

describe('AppLayout Routing', () => {
  test('redirects from root / to /policy-chat', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <AppLayout />
      </MemoryRouter>
    );
    expect(screen.getByTestId('policy-chat-page')).toBeInTheDocument();
  });

  test('renders PolicyChat at /policy-chat', () => {
    render(
      <MemoryRouter initialEntries={['/policy-chat']}>
        <AppLayout />
      </MemoryRouter>
    );
    expect(screen.getByTestId('policy-chat-page')).toBeInTheDocument();
  });

  test('renders Notifications at /notifications', () => {
    render(
      <MemoryRouter initialEntries={['/notifications']}>
        <AppLayout />
      </MemoryRouter>
    );
    expect(screen.getByTestId('notifications-page')).toBeInTheDocument();
  });

  test('renders NotFoundComponent for invalid routes', () => {
    render(
      <MemoryRouter initialEntries={['/invalid-route']}>
        <AppLayout />
      </MemoryRouter>
    );
    expect(screen.getByTestId('not-found-page')).toBeInTheDocument();
  });
});

describe('AppLayout Layout & Interactions', () => {
  test('renders Sidebar on desktop', () => {
    render(
      <MemoryRouter>
        <AppLayout />
      </MemoryRouter>
    );
    // There are two sidebars in the code: one for mobile (conditional) and one for desktop (hidden on mobile)
    // We mock Sidebar, so we should see it.
    // The desktop sidebar is always rendered but hidden via CSS on mobile.
    // Since we are using JSDOM, CSS media queries might not apply strictly, but the element should be in the DOM.
    expect(screen.getByText('Sidebar Component')).toBeInTheDocument();
  });

  test('toggles mobile menu', () => {
    render(
      <MemoryRouter>
        <AppLayout />
      </MemoryRouter>
    );

    // Initially, the mobile overlay should not be visible.
    // The mobile sidebar is conditional: {mobileMenuOpen && ...}
    // The desktop sidebar is always there.
    // Let's check for the overlay specific structure or the close button which is only passed to the mobile sidebar in the mock?
    // In the code: <Sidebar onClose={() => setMobileMenuOpen(false)} /> is the mobile one.
    // The desktop one is: <Sidebar className="hidden md:flex" /> (no onClose prop).

    // Our mock renders a close button ONLY if onClose is provided.
    // So initially, we should NOT see the "Close" button from the mobile sidebar.
    expect(screen.queryByTestId('close-sidebar')).not.toBeInTheDocument();

    // Click the menu button to open mobile menu
    // The button has an onClick handler.
    // We need to find the button. It wraps the Menu/X icon.
    const menuButton = screen.getByRole('button'); // There might be multiple buttons if Sidebar has them, but our mock Sidebar has a button only if onClose is present.
    // Wait, the toggle button is in the main layout: <button ... onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>

    fireEvent.click(menuButton);

    // Now mobile menu should be open, so we should see the Close button in the mobile sidebar
    expect(screen.getByTestId('close-sidebar')).toBeInTheDocument();
    expect(screen.getByTestId('x-icon')).toBeInTheDocument(); // Icon should change to X

    // Click close button to close
    fireEvent.click(screen.getByTestId('close-sidebar'));

    // Should be closed again
    expect(screen.queryByTestId('close-sidebar')).not.toBeInTheDocument();
    expect(screen.getByTestId('menu-icon')).toBeInTheDocument(); // Icon should be Menu again
  });
});