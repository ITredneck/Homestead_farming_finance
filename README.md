# Homestead Finance

> [!WARNING]
> **Work in progress.** This is not a complete project. It's an early test build: most
> features aren't built yet, and data from test versions may not carry over. Don't use it
> for real farm records or taxes.

Farm finance and records for homesteads, as a **Home Assistant app** (what Home Assistant
called an add-on before 2026.2).

## What it will do

- **Animals:** feed, health issues and treatments (with medicine withdrawal dates), production (eggs, milk, wool, honey), weights, breeding and births. Track by herd or flock, by individual animal, or both, with costs split fairly between them.
- **Crops:** plantings by season, with optional fields and beds. Seed, fertilizer and power use, and harvests.
- **Stock:** feed, seed, medicine, supplies and finished goods. Choose per item whether to track stock or just expense it.
- **Farm goods:** batches made from recipes (canning, cheese, soap, meat), with lot numbers, best-by dates and a real cost per unit.
- **Receipts:** snap a photo in the app. Type it in, or let the AI you already set up in Home Assistant read it.
- **Sales and invoices:** quick farm-stand and market sales (they keep working if the signal drops) and invoices on account, with PDF invoices and receipts.
- **Power costs:** Home Assistant energy sensors split the electric bill across animals, crops and batches.
- **For your accountant:** a year-end pack with a Schedule F summary (US, cash method), an Excel workbook and a ZIP of all receipts.
- **Your own AI:** a companion Home Assistant integration (its own repository, installed from Home Assistant's Marketplace) lets AI apps connected to Home Assistant's MCP server log chores, answer questions and record sales.

Simple screens by default, with optional advanced features in each area for those who want them.

## How it runs

- A Home Assistant app (Home Assistant OS or Supervised, amd64 and aarch64), opened from the Home Assistant sidebar or the mobile app.
- Data stays on your own Home Assistant system and is included in Home Assistant backups.

## Trying a test build

For testers only, see the warning above.

1. In Home Assistant, go to **Settings > Apps > App store**, open the menu (⋮) and choose **Repositories**.
2. Add `https://github.com/ITredneck/Homestead_farming_finance`.
3. Find **Homestead Finance** in the store, install it and start it. It appears in the sidebar.

## Project docs

- Design: [docs/superpowers/specs/2026-11-13-homestead-finance-design.md](docs/superpowers/specs/2026-11-13-homestead-finance-design.md)
- Roadmap and tasks: this repository's **milestones**, **issues** and the **Homestead Finance** project board.
- Development commands: the Commands section of [CLAUDE.md](CLAUDE.md).

## License

[AGPL-3.0](LICENSE)
