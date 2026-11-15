import { Alert, SimpleGrid, Stack } from '@mantine/core';
import { IconAlertTriangle } from '@tabler/icons-react';

import { AreaTile } from '../../components/AreaTile';
import { AREAS } from '../registry';

export function HomePage() {
  return (
    <Stack gap="lg">
      <Alert color="yellow" icon={<IconAlertTriangle />} title="Early test version">
        Homestead Finance is a work in progress. Don't use it for real records yet.
      </Alert>
      <SimpleGrid cols={{ base: 2, sm: 3, md: 4 }} spacing={{ base: 'sm', sm: 'md' }}>
        {AREAS.map((area) => (
          <AreaTile key={area.id} area={area} />
        ))}
      </SimpleGrid>
    </Stack>
  );
}
