import { Anchor, Group } from '@mantine/core';
import { IconArrowLeft } from '@tabler/icons-react';
import { Link } from 'react-router';

export function BackLink() {
  return (
    <Anchor component={Link} to="/" size="lg" w="fit-content">
      <Group gap={6}>
        <IconArrowLeft size={20} />
        Home
      </Group>
    </Anchor>
  );
}
