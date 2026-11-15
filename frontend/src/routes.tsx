import type { RouteObject } from 'react-router';

import { AreaPage } from './areas/AreaPage';
import { HomePage } from './areas/home/HomePage';
import { SettingsPage } from './areas/settings/SettingsPage';
import { AppLayout } from './components/AppLayout';
import { NotFoundPage } from './components/NotFoundPage';
import { OutboxSpikePage } from './spike/OutboxSpikePage';

export const routes: RouteObject[] = [
  {
    element: <AppLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'settings', element: <SettingsPage /> },
      { path: 'spike', element: <OutboxSpikePage /> },
      { path: ':areaId', element: <AreaPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
];
