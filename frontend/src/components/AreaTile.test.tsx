import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { AREAS } from '../areas/registry';
import { renderWithProviders } from '../test/render';
import { AreaTile } from './AreaTile';

const animals = AREAS[0];

describe('AreaTile', () => {
  it('links to its area with a relative hash route', () => {
    renderWithProviders(<AreaTile area={animals} />);

    const link = screen.getByRole('link', { name: 'Animals' });
    expect(link.getAttribute('href')).toBe('/animals');
  });

  it('shows a badge when one is given', () => {
    renderWithProviders(<AreaTile area={animals} badge="3 waiting" />);

    expect(screen.getByText('3 waiting')).toBeInTheDocument();
  });

  it('shows no badge by default', () => {
    renderWithProviders(<AreaTile area={animals} />);

    expect(screen.queryByText(/waiting/)).not.toBeInTheDocument();
  });
});
