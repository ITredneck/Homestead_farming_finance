import { Stack, Text, Title } from '@mantine/core';

import { BackLink } from './BackLink';

export function NotFoundPage() {
  return (
    <Stack>
      <BackLink />
      <Title order={2}>Page not found</Title>
      <Text>This page doesn't exist. Use the link above to go back home.</Text>
    </Stack>
  );
}
