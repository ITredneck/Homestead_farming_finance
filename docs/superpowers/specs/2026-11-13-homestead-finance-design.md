# Homestead Finance — Design & Roadmap

## Context
Homesteaders need to know what their animals, crops and farm products really cost and earn, and they need to hand an accountant a clean year-end package. Generic accounting tools (QuickBooks and similar) know nothing about herds, plantings or batches. Farm-record tools (farmOS and similar) aren't built around finance and are hard to deploy.

**Homestead Finance** is an open-source (AGPL-3.0) **Home Assistant add-on**. It joins farm records to real double-entry books and uses HA for login, remote access, backups, power metering and the farmer's own AI. It's simple by default for non-technical farmers, with optional advanced features per area.

This document records the goals, framework and layout agreed in the initial design session (2026-11-13). The work is tracked in GitHub: one milestone per session (M0–M14 plus "Later (optional)"), an issue for every deliverable, and the "Homestead Finance" project board. Where this document and the issues disagree on scope or status, the issues win. Design changes should update this document in the same PR.

## Decisions (from clarifying Q&A, 2026-11-13)
| Topic | Decision |
|---|---|
| Audience | Open source, each farm self-hosts. One farm per install in the UI; records belong to a `farm` row so multi-farm stays possible |
| Distribution | **HA add-on only** (HA OS/Supervised; amd64 + aarch64). The core doesn't depend on HA wrappers, so other packaging stays possible later. Test target: a real HA OS install |
| Devices | Phone and computer equally: responsive, mobile-first |
| Offline | "Dropout-proof" quick entry, proven by an S1 spike on Android in the HA Companion app |
| Tax | US, IRS Schedule F, **cash method**, calendar year, USD |
| Books | Double-entry inside, simple screens; journal view behind the Money area's advanced switch |
| Accountant pack | PDF summary + Excel workbook + receipt ZIP |
| Animals | Group costs split evenly across members on the date (advanced: by weight) + per-animal direct costs; any entry can target a group or an individual |
| Animal records | Feed, health/treatments, withdrawal dates, production counts, weights, breeding/births/lineage, purchase/sale/death, butchering → meat stock |
| Crops | Plantings (crop + season); place (field/bed/greenhouse) optional; perennials are multi-year plantings |
| Inventory | Per item: "track stock" or "expense on purchase" |
| Batches | Recipes, lot numbers + best-by, labor + power in cost, own produce at cost |
| Sales | Market/stand quick sale + invoices on account; sales tax optional per product |
| Invoices | PDF to print/download/share (no email in v1) |
| Receipts in | Phone camera / upload into an in-app inbox |
| AI | Abilities: receipts, logging activity, read-only questions, sales/invoices. Owner sets an access level (off / receipts / read-only / full). AI writes save directly, tagged "AI". Access goes **through HA's MCP server** via a companion integration. Receipt photos are read by **HA AI Task** |
| Power | Per-device HA energy sensors (kWh). Estimate with HA's Energy price, then match to the actual bill. Unmetered remainder goes to household or farm overhead (a setting) |
| Users | Every HA user sees everything; all records store who entered them and how |
| Labor | Hours for everyone (unpaid time valued at a rate, used only in true-cost reports) + hired wages as real expenses |
| Equipment | Flag purchases as equipment, giving an asset list for the accountant (no in-app depreciation) |
| Stack | Python (FastAPI) backend + React/TypeScript frontend |
| UI | Home = big area tiles; first-run setup hides unused areas; per-area Advanced switch |
| Name / IDs | Homestead Finance; add-on slug and integration domain `homestead_finance` |
| Order | After basics: Animals first. Farm data → HA sensors comes later and is optional |
| Tracking | **GitHub only.** One Project board (Status + milestone; Board and Roadmap views), one milestone per session, an issue for every deliverable. Detailed implementation steps live in the issues (sub-issues or checklists), not in plan files. Design specs stay in `docs/` as reference |
| Workflow | One branch + PR per session; the PR closes that milestone's issues |

## Architecture
```
Phone / PC ─ HA app or browser ─► Home Assistant (login, remote access, ingress)
                                        │ ingress proxy (base path + user headers)
                                        ▼
        ┌──────────── Homestead Finance add-on (one container) ────────────┐
        │ React SPA (static)        FastAPI  /api/*   /api/ai/tools/*       │
        │ areas: ledger · cost centers · purchases · inventory · animals ·  │
        │        crops · batches · labor · sales · power · reports · ai     │
        │ SQLite (WAL) + receipt/attachment files in /data (in HA backups)  │
        └───────┬──────────────────────────────────────────▲────────────────┘
  Supervisor API│ recorder statistics (kWh), energy prefs, │ internal API + key
  (token)       │ ai_task.generate_data (receipt image)    │ (from discovery)
                ▼                                          │
        Home Assistant Core ◄──── companion integration custom_components/homestead_finance
          ├ Recorder / Energy           registers LLM API "Homestead Finance"
          ├ AI Task (user's own AI)     (tools proxied from the add-on's registry)
          └ MCP Server + Assist ◄────── user's AI apps (Claude, ChatGPT, local) / voice
```
- **Add-on:** prebuilt per-arch images on GHCR (GitHub Actions). Ingress only: no ports exposed outside HA, and the companion integration reaches the add-on over HA's internal network. `homeassistant_api: true`. `media` mapped for temporary receipt copies sent to AI Task.
- **Backend:** Python 3.13+, FastAPI, SQLAlchemy 2 + Alembic, Pydantic v2, uv.
  - Folder per area: `models · schemas · service · router · tools`.
  - **Services are the only writers.** UI routes and AI tools both call the same services.
- **Frontend:** React + TS + Vite (`base: './'` so it works under ingress paths).
  - TanStack Query keeps cached lists and queued (paused) offline entries in IndexedDB.
  - Mantine for mobile-friendly forms.
  - Typed client generated from the backend's OpenAPI schema.
- **Companion integration:** Python, configured through Supervisor discovery (one click, no typing). It fetches tool definitions from the add-on and registers them as an HA LLM API, which HA's MCP Server and Assist (voice) can then use. Installed via HACS; whether the add-on can install it automatically gets evaluated in S9.
- **Identity:** the add-on accepts requests only from HA's ingress gateway and reads the HA user from ingress headers. Every record stores `entered_by`, `entered_via` (app / ai / system) and timestamps.

## Accounting model
- **Ledger = farm (management) books.** Journal entries are made of lines with signed amounts that sum to zero. Each line can carry a cost center, an item and a quantity. Corrections reverse and repost; nothing is silently edited.
- **Two dimensions on every money line:**
  - **Category:** the account, seeded with a chart mapped to Schedule F lines (editable).
  - **Cost center:** who the money is for. Types: farm overhead · **household** (personal: posts to owner draws, never an expense) · animal group · animal · planting · place · product line · batch.
- **Money handling:** amounts are integer cents. Quantities and unit costs are exact decimals. Splits use largest-remainder rounding so the parts always add up to the whole.
- **Owner money:** paying with personal funds is an owner contribution; household shares are owner draws.
- **Stock costing:** stock lots use FIFO.
  - Purchased stock and **made goods** (batch outputs, butchered meat) carry cost in stock and turn into cost of goods when sold.
  - **Raw daily production** (eggs, milk, harvests) enters stock at $0. Its cost per unit is calculated per period in farm reports. When used in a batch (own produce at cost), it moves at that per-unit cost.
- **Two report views over the same data:**
  - **Tax view (Schedule F, cash method):** built from source documents by date paid and category. Purchases count when paid, even if still in stock. Sales count when paid, excluding sales tax. Utility bills count only their farm share. Inventory and cost allocations don't affect it.
  - **Farm view (management):** the ledger by cost center. Costs follow use (feed fed, power used, transfers). Shows cost per dozen, per lb, per bar, and a **true-cost** column that adds unpaid labor (never in the ledger or the tax view).
- **Livestock flags for the accountant** (flagged, not computed): raised vs purchased, and market vs breeding.
  - Raised sales → line 2.
  - Purchased-for-resale sales, with their basis → lines 1a/1b.
  - Purchased breeding stock → asset list.
  - Breeding/dairy stock sales → flagged for Form 4797.
- **Year lock** once the accountant pack is final. Unlocking is logged.

## Areas (functional scope v1)
- **Money / Purchases:**
  - Receipt inbox: camera/upload, works offline-queued. Images are resized on the phone (~1600 px).
  - Purchases have line items. Each line gets a category plus a cost center, or a split (even / % / including household), an optional stock item and quantity, and an optional equipment flag (feeds the asset list).
  - Also: vendors, payment accounts (cash box, checking, card, personal), and an "AI-entered" filter.
- **Stock:**
  - Items: kind, buy unit vs use unit (bag = 50 lb), track vs expense, default category, reorder level, sellable/produced.
  - Lots: quantity, unit cost, lot number, best-by.
  - Movements: purchase, use (→ cost center), production/harvest in, batch in/out, sale, home use, spoilage, adjustment.
  - Low-stock alerts.
- **Animals:**
  - Species and breeds. Groups, either headcount-only (a flock) or with individuals. Individuals: tag, name, sex, birth date, dam/sire, raised/purchased, purpose, status. Group membership is date-ranged.
  - Feeding goes to a group or an animal. Health issues, treatments and vet visits use medicine from stock and set withdrawal dates per product (meat / milk / eggs).
  - Also: weights; breeding and births (offspring created automatically); production counts.
  - Dispositions: sold, died, culled, or butchered (the animal's built-up cost moves into meat lots).
  - Cost split: an individual's cost = its own costs + an even share of its group's costs.
- **Crops:**
  - Crops/varieties and plantings, with an optional place.
  - Inputs: seed and fertilizer use, direct expenses.
  - Harvests go into stock lots. Cost per unit harvested.
- **Products / batches:**
  - Recipes (advanced): inputs and expected yield.
  - A batch gets a lot number and best-by date. Its cost = stock inputs (FIFO) + own produce at cost + labor + power from claimed devices during the batch window → a product lot with a unit cost (plus a true-cost figure).
- **Labor:** people (family/unpaid with a rate, or hired); time logs against any cost center or batch; hired wages are a real expense (Schedule F "Labor hired").
- **Sales:**
  - Products and prices; sales tax optional per product (collected tax is a liability, with a report).
  - Quick sale: offline-capable, no customer needed, payment type.
  - Customers; invoices on account (number, due date, unpaid/partial/paid); payments.
  - Branded PDF invoice and customer receipt (with lot numbers when enabled). Animal sales use the same flow.
- **Power (HA):**
  - Map energy sensors to a cost center or % split, with effective dates. A batch can claim a device for its time window.
  - Hourly kWh comes from HA long-term statistics. Estimate = kWh × HA Energy price (or a typed rate).
  - When the bill is entered, the bill period is re-priced at bill $/kWh and costs are trued up. The unmetered remainder goes to household or overhead.
- **Reports:**
  - Tile badges (withdrawal active, low feed, unpaid invoices, waiting to sync).
  - Farm-view P&L by area/cost center, cost per unit, true cost, Schedule F (cash), stock on hand, withdrawals, unpaid invoices.
  - **Accountant pack:** PDF summary + Excel workbook (every transaction with category, cost center, vendor, receipt reference, AI flag) + receipt ZIP + asset list + livestock detail + year-end stock.
- **AI:**
  - One tool registry in the backend (Pydantic → JSON Schema). Each tool is tagged read / write / receipts, and the owner's access level is enforced in the add-on.
  - Ambiguous names ("the goats") return candidates rather than guesses.
  - **Receipt reading:** copy the image to a temporary file in `/media`, call `ai_task.generate_data` with a structure (vendor, date, totals, lines + suggested category/cost center from the farm's own lists), save the purchase tagged AI, then delete the temp copy. Hidden if no AI Task entity exists.

## Offline (dropout-proof quick entry)
- **Forms:** receipt photo, feeding, health note, production count, harvest, weight, time log, quick sale.
- **How:**
  - The client creates a UUID per entry, and the server's create endpoints are idempotent on it.
  - Reference lists and paused entries persist in IndexedDB and replay on reconnect, with a "N waiting" badge.
  - Entries are append-only events, so there are no merge conflicts. Editing or deleting existing records needs a connection.
- **Known HA-app limits:**
  - The app can't be opened from scratch offline.
  - The ingress session may need a reload after a long time offline (the queue survives).
  - Stored entries are tied to the HA address used (local vs remote URL).
  - **S1 spike decides go/no-go** on an Android phone.

## UI layout
- **Home:** big tiles: Animals · Crops · Stock · Products · Sales · Money · Reports (+ settings gear). Small badges on tiles. Unused areas hidden.
- **Area page:** big action buttons on top (e.g., Animals: Feed · Health · Eggs/Milk · Weigh · Birth · Move), then lists and search. Desktop uses the same structure with wider tables.
- **First-run setup:** farm name/address/logo, tax settings, which areas are used, payment accounts, power remainder setting, AI access level and AI Task entity.
- **Advanced switches:** weight split and lineage (Animals); lot numbers and lot picking (Stock); recipes (Products); journal, chart of accounts and Schedule F mapping (Money); device splits (Power).

## Repository layout (monorepo)
```
repository.yaml                          HA add-on repository manifest
homestead_finance/                       add-on: config.yaml, DOCS.md, CHANGELOG.md, icon/logo, translations/
custom_components/homestead_finance/     companion integration (HACS) + hacs.json at root
backend/   pyproject.toml, src/homestead_finance/{core,ledger,ha,ai,<area>/...}, alembic/, tests/
frontend/  src/{areas/<area>,components,offline,api}, vite.config.ts
docker/Dockerfile                        multi-stage: build SPA → HA Python base image (+ WeasyPrint deps)
.github/workflows/                       tests; multi-arch image → GHCR
docs/                                    design specs + user docs (implementation plans live in GitHub issues)
```
Initial libraries (confirm in S1):
- Backend: FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, pytest + hypothesis, httpx/websockets (HA), WeasyPrint (PDF from Jinja2 HTML), XlsxWriter.
- Frontend: React, Vite, TanStack Query (+ persister), React Router, Mantine, openapi-typescript, Vitest, Playwright.

## Roadmap — follow-up sessions
Each session is one GitHub milestone, and once created the milestones are the source of truth. A session runs:
1. A short brainstorm of that area.
2. Detailed steps added to the milestone's issues (sub-issues or checklists).
3. TDD build on a session branch.
4. Code review on the PR.
5. Merge, which closes the issues.

Each area session also adds its AI tools and offline quick-entry forms.

| # | Session | Delivers |
|---|---|---|
| 1 | Foundation + offline spike | Scaffold; FastAPI/SQLite/Alembic; React shell with tiles; ingress identity; add-on packaging + GHCR build; installs on a real HA OS; airplane-mode outbox test in the Android HA app; backup consistency approach |
| 2 | Ledger core + setup | Schedule F chart (line numbers checked against the current IRS form), posting engine + invariants, cost centers, payment accounts, owner contributions/draws, household, idempotent-entry pattern, first-run setup, area/advanced switches |
| 3 | Purchases + receipt inbox | Camera inbox (offline), split-line purchases, vendors, equipment/asset list, simple money summary |
| 4 | HA connection + AI receipts | Supervisor client, AI Task receipt reading, AI tool registry + access levels, first tools |
| 5 | Stock core | Items, track vs expense, lots/FIFO, use, home use/spoilage, low stock |
| 6 | Animals I | Species/groups/individuals, membership, feeding, health, withdrawal, group cost split |
| 7 | Animals II | Production counts, weights, breeding/births/lineage, dispositions + butchering, livestock flags |
| 8 | Sales + invoices | Products/prices, optional sales tax, offline quick sale, customers, invoices, payments, PDFs |
| 9 | Companion HA integration | Discovery config flow, LLM API proxy → HA MCP Server + Assist, HACS |
| 10 | Crops | Plantings, optional places, inputs, harvests, perennials |
| 11 | Labor + batches | People/time logs, recipes, batches, lots/best-by, own produce at cost, unit costs |
| 12 | Power from HA | Sensor mapping, hourly kWh sync, estimates, bill true-up, remainder, batch device claims |
| 13 | Reports + accountant pack | Farm view, Schedule F cash, cost per unit, PDF + Excel + receipt ZIP, year lock |
| 14 | v1.0 release | Onboarding polish, add-on docs, full data export, public release |

**Later (optional):**
- **HA side:** farm sensors and actions in HA.
- **AI access:** direct MCP endpoint, Claude Desktop extension.
- **Other installs:** desktop or standalone Docker install, companion phone app.
- **Sales:** email invoices, preorders/CSA, card-processor sync.
- **Accounting:** QuickBooks/Xero export, multiple tax rates, non-US tax forms.
- **Power:** other utilities, whole-meter % splits, switch on-time estimates.
- **Other:** roles, translations.

## Risks to verify early
- **Offline inside the HA app (S1):**
  - The "Unable to connect" overlay.
  - Ingress session expiry.
  - Storage tied to the local vs remote HA address.
- **Ingress (S1):**
  - The dynamic base path.
  - The user-identity headers.
  - Whether one repo can serve as both the add-on repo and the HACS repo.
- **AI Task (S4):** image attachment support per AI provider, and the media-source path from inside the add-on.
- **HA MCP Server (S9):** exposing a custom LLM API, and converting JSON Schema → voluptuous.
- **SQLite in HA backups (S1):** cold backup vs a pre-backup snapshot. **WeasyPrint (S8):** size on the HA base image, for both architectures.

## Verification (project-wide)
- **Backend:** pytest, plus property tests: every journal entry sums to zero, splits add up exactly, stock never goes negative. A golden-file test checks a sample farm year against hand-computed Schedule F totals.
- **Frontend:** Vitest for the outbox. A Playwright offline flow checks that entries made with the network off are saved exactly once after reconnect.
- **Add-on:** CI builds amd64 + aarch64. Install on a real HA OS; test from the sidebar and from the Android HA app.
