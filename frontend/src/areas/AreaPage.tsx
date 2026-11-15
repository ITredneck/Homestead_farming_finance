import { Alert, Group, Stack, Text, ThemeIcon, Title } from '@mantine/core';
import { useParams } from 'react-router';

import { BackLink } from '../components/BackLink';
import { NotFoundPage } from '../components/NotFoundPage';
import { findArea } from './registry';

/** Placeholder until each area is built. */
export function AreaPage() {
  const { areaId } = useParams();
  const area = findArea(areaId);
  if (!area) {
    return <NotFoundPage />;
  }
  const Icon = area.icon;
  return (
    <Stack>
      <BackLink />
      <Group>
        <ThemeIcon size={56} radius="xl" variant="light" aria-hidden>
          <Icon size={32} stroke={1.6} />
        </ThemeIcon>
        <Title order={2}>{area.label}</Title>
      </Group>
      <Text size="lg">{area.description}</Text>
      <Alert color="gray" title="Coming soon">
        This part of Homestead Finance isn't built yet.
      </Alert>
    </Stack>
  );
}
