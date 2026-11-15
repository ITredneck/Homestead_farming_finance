import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';

import { renderApp } from '../../test/render';

const AREA_NAMES = ['Animals', 'Crops', 'Stock', 'Products', 'Sales', 'Money', 'Reports'];

describe('home screen', () => {
  it('shows a big tile for every area', () => {
    renderApp('/');

    for (const name of AREA_NAMES) {
      expect(screen.getByRole('link', { name })).toBeInTheDocument();
    }
  });

  it('warns that this is an early test version', () => {
    renderApp('/');

    expect(screen.getByText('Early test version')).toBeInTheDocument();
  });

  it('opens an area from its tile', async () => {
    const user = userEvent.setup();
    renderApp('/');

    await user.click(screen.getByRole('link', { name: 'Animals' }));

    expect(await screen.findByRole('heading', { name: 'Animals' })).toBeInTheDocument();
    expect(screen.getByText('Coming soon')).toBeInTheDocument();
  });

  it('opens settings from the gear', async () => {
    const user = userEvent.setup();
    renderApp('/');

    await user.click(screen.getByRole('link', { name: 'Settings' }));

    expect(await screen.findByRole('heading', { name: 'Settings' })).toBeInTheDocument();
  });

  it('shows not found for unknown pages', () => {
    renderApp('/goats-in-space');

    expect(screen.getByRole('heading', { name: 'Page not found' })).toBeInTheDocument();
  });
});
