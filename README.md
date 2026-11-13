# Homestead Finance

Farm finance and records for homesteads, as a **Home Assistant add-on**.

> **Status: design phase.** Nothing is usable yet. The design is done and the work is planned in GitHub milestones and issues.

## What it will do

- **Animals:** feed, health issues and treatments (with medicine withdrawal dates), production (eggs, milk, wool, honey), weights, breeding and births. Track by herd or flock, by individual animal, or both, with costs split fairly between them.
- **Crops:** plantings by season, with optional fields and beds. Seed, fertilizer and power use, and harvests.
- **Stock:** feed, seed, medicine, supplies and finished goods. Choose per item whether to track stock or just expense it.
- **Farm goods:** batches made from recipes (canning, cheese, soap, meat), with lot numbers, best-by dates and a real cost per unit.
- **Receipts:** snap a photo in the app. Type it in, or let the AI you already set up in Home Assistant read it.
- **Sales and invoices:** quick farm-stand and market sales (they keep working if the signal drops) and invoices on account, with PDF invoices and receipts.
- **Power costs:** Home Assistant energy sensors split the electric bill across animals, crops and batches.
- **For your accountant:** a year-end pack with a Schedule F summary (US, cash method), an Excel workbook and a ZIP of all receipts.
- **Your own AI:** the companion Home Assistant integration lets AI apps connected to Home Assistant's MCP server log chores, answer questions and record sales.

Simple screens by default, with optional advanced features in each area for those who want them.

## How it runs

- A Home Assistant add-on (HA OS / Supervised, amd64 and aarch64), opened from the HA sidebar or the HA mobile app.
- Data stays on your own Home Assistant box and is included in HA backups.

## Project docs

- Design: [docs/superpowers/specs/2026-11-13-homestead-finance-design.md](docs/superpowers/specs/2026-11-13-homestead-finance-design.md)
- Roadmap and tasks: this repository's **milestones**, **issues** and the **Homestead Finance** project board.

## License

[AGPL-3.0](LICENSE)
