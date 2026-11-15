import { ActionIcon, Anchor, AppShell, Box, Container, Group, Title } from '@mantine/core';
import { IconSettings } from '@tabler/icons-react';
import { Link, Outlet } from 'react-router';

import iconUrl from '../assets/brand/icon.svg';

/** Header and page share one centered column, so they line up on wide screens. */
export function AppLayout() {
  return (
    <AppShell header={{ height: 64 }} padding="md">
      <AppShell.Header>
        <Box px="md" h="100%">
          <Container size="lg" px={0} h="100%">
            <Group h="100%" justify="space-between" wrap="nowrap">
              <Anchor component={Link} to="/" underline="never" c="inherit">
                <Group gap="sm" wrap="nowrap">
                  <img src={iconUrl} alt="" width={36} height={36} />
                  <Title order={1} size="h3">
                    Homestead Finance
                  </Title>
                </Group>
              </Anchor>
              <ActionIcon component={Link} to="/settings" variant="subtle" aria-label="Settings">
                <IconSettings size={28} />
              </ActionIcon>
            </Group>
          </Container>
        </Box>
      </AppShell.Header>
      <AppShell.Main>
        <Container size="lg" px={0}>
          <Outlet />
        </Container>
      </AppShell.Main>
    </AppShell>
  );
}
