import { Badge, Card, Stack, Text, ThemeIcon } from '@mantine/core';
import type { ReactNode } from 'react';
import { Link } from 'react-router';

import type { Area } from '../areas/registry';
import classes from './AreaTile.module.css';

interface AreaTileProps {
  area: Area;
  /** Small status shown in the corner, e.g. "3 waiting" or "Low feed". */
  badge?: ReactNode;
}

export function AreaTile({ area, badge }: AreaTileProps) {
  const Icon = area.icon;
  return (
    <Card component={Link} to={`/${area.id}`} withBorder radius="lg" className={classes.tile}>
      {badge !== undefined && (
        <Badge className={classes.badge} color="orange" size="lg">
          {badge}
        </Badge>
      )}
      <Stack align="center" gap="xs">
        <ThemeIcon size={64} radius="xl" variant="light" aria-hidden>
          <Icon size={36} stroke={1.6} />
        </ThemeIcon>
        <Text fw={700} size="lg" c="var(--mantine-color-text)">
          {area.label}
        </Text>
      </Stack>
    </Card>
  );
}
