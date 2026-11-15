import { ActionIcon, Button, createTheme } from '@mantine/core';

/** Large touch targets (48 px or more): the app is used on phones, often outdoors. */
export const theme = createTheme({
  primaryColor: 'green',
  defaultRadius: 'md',
  fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
  components: {
    Button: Button.extend({ defaultProps: { size: 'lg' } }),
    ActionIcon: ActionIcon.extend({ defaultProps: { size: 48 } }),
  },
});
