import {
  IconBuildingStore,
  IconBuildingWarehouse,
  IconCheese,
  IconHorse,
  IconPlant2,
  IconReceipt2,
  IconReportAnalytics,
  type TablerIcon,
} from '@tabler/icons-react';

export interface Area {
  id: string;
  label: string;
  description: string;
  icon: TablerIcon;
}

/** The home screen tiles, in order. First-run setup will hide the areas a farm doesn't use. */
export const AREAS = [
  {
    id: 'animals',
    label: 'Animals',
    description: 'Herds, flocks and individual animals: feeding, health and production.',
    icon: IconHorse,
  },
  {
    id: 'crops',
    label: 'Crops',
    description: 'Plantings, inputs and harvests.',
    icon: IconPlant2,
  },
  {
    id: 'stock',
    label: 'Stock',
    description: 'Feed, seed, medicine, supplies and finished goods.',
    icon: IconBuildingWarehouse,
  },
  {
    id: 'products',
    label: 'Products',
    description: 'Batches you make, like cheese, soap or canned goods.',
    icon: IconCheese,
  },
  {
    id: 'sales',
    label: 'Sales',
    description: 'Market and farm-stand sales, customers and invoices.',
    icon: IconBuildingStore,
  },
  {
    id: 'money',
    label: 'Money',
    description: 'Purchases, receipts and payment accounts.',
    icon: IconReceipt2,
  },
  {
    id: 'reports',
    label: 'Reports',
    description: 'Farm results and the year-end pack for your accountant.',
    icon: IconReportAnalytics,
  },
] as const satisfies readonly Area[];

export type AreaId = (typeof AREAS)[number]['id'];

export function findArea(id: string | undefined): Area | undefined {
  return AREAS.find((area) => area.id === id);
}
