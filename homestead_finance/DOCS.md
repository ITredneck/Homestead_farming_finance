# Homestead Finance

> **Early test version.** This app is a work in progress and not a complete product.
> Don't use it for real records or taxes yet. Data from test versions may not carry over.

Homestead Finance keeps farm records and real double-entry books for a homestead: animals,
crops, stock, products you make, sales and purchases. It's built for a phone in the barn as
much as for a computer at the desk.

## What works in this version

- The app opens from the Home Assistant sidebar and from the Home Assistant mobile app.
- The home screen shows the farm areas. The areas themselves are placeholders for now.
- **Settings** shows the app version, the database state and who you're signed in as.
- **Settings > Offline entry test** is a test page for checking how quick entry behaves when
  your phone loses its connection.

## Who can use it

Every Home Assistant user can open the app, not only administrators. Records note which
Home Assistant user entered them.

## Your data

- Everything stays on your Home Assistant system, in this app's own folder. Nothing is sent
  anywhere else.
- Home Assistant backups include the app's data. During a backup, Home Assistant stops the
  app for a moment so the database is saved in a consistent state; it starts again by itself.

## Configuration

| Option | What it does |
|---|---|
| `log_level` | How much detail the app writes to its log (`info` by default). Use `debug` when you report a problem. |

## Getting help

Report problems and ideas in the project's
[GitHub issues](https://github.com/ITredneck/Homestead_farming_finance/issues). Please don't
include personal details.
