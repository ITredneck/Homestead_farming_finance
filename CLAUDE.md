# Homestead Finance: notes for Claude

The product is a Home Assistant app (HA's name for add-ons since 2026.2; FastAPI + SQLite backend, React/TypeScript frontend) plus a companion HA integration (Python) that lives in its own repository and installs from HA's Marketplace. The reference design is [docs/superpowers/specs/2026-11-13-homestead-finance-design.md](docs/superpowers/specs/2026-11-13-homestead-finance-design.md); read the parts relevant to the task before changing behavior.

## Task tracking: GitHub only
- All tracking lives in GitHub: the **Homestead Finance** project board, milestones (M0–M14 + "Later (optional)") and issues. Don't keep TODO lists or plan files in the repo.
- **Each session is one milestone.** Start by reading that milestone's open issues. Before coding, refine them with detailed steps as sub-issues or checklists. Plans from planning skills (such as writing-plans) go into the issues, not into `docs/`.
- **One branch and one PR per session.** Branch name `m<N>-<short-slug>`. The PR body lists `Closes #<n>` for every issue it finishes. Keep each item's Status (Todo / In progress / Done) current on the project board.
- Work discovered along the way gets its own issue in the right milestone, with a `type:*` label and an `area:*` label.
- Issue and PR text is public. No personal details (names, emails, devices, home setup).
- If the design changes, update the spec in the same PR.

## Invariants (don't break these)
- **Money:** amounts are integer cents. Quantities and unit costs are exact decimals, never floats. Splits use the largest-remainder helper so the parts add up to the whole.
- **Ledger:** every journal entry sums to zero. Corrections reverse and repost; don't edit posted lines in place.
- **Services are the only writers.** API routers and AI tools call services; they never write to the database directly.
- **Provenance:** every record stores `entered_by`, `entered_via` (app / ai / system) and timestamps. Creates carry a client-generated UUID and are idempotent, because offline entries replay.
- **Two report views, kept apart:**
  - The tax view (Schedule F, cash method) is computed from source documents by date paid.
  - The farm view comes from the ledger by cost center.
- **Household cost center:** postings go to owner draws, never to an expense.
- **AI:** AI writes are tagged as AI. The owner's AI access level (off / receipts / read-only / full) is enforced in the backend.
- **Ingress:** the frontend uses relative URLs only, because HA ingress serves it under a dynamic base path. Never hardcode `/`. Routing uses hash routes (`#/animals`) so the page URL stays at the ingress root.
- **Ingress gateway:** only the Supervisor (`172.30.32.2`) may connect. The HA user comes from `X-Remote-User-Id`; `entered_by` stores that id, not the name.
- **Database sessions:** services that write take a `WriteSession` (it starts `BEGIN IMMEDIATE`); read-only code takes a `ReadSession`.
- **Repo layout:** only `homestead_finance/` may contain a file named `config.yaml`, `config.yml` or `config.json`. The Supervisor reads any such file in the repo as an app. A pre-commit hook and CI enforce this.

## Commands
One-time setup: install [uv](https://docs.astral.sh/uv/) and Node 24, run `corepack enable pnpm`, then `uvx pre-commit install`.

**Backend** (run in `backend/`):

- `uv sync`: install dependencies. uv fetches Python 3.14 itself.
- `uv run python -m homestead_finance --dev --reload`: API on <http://127.0.0.1:8099> with a stub HA user and data in `backend/.data`.
- `uv run pytest`: tests.
- `uv run ruff check . && uv run ruff format --check . && uv run pyright`: lint, format check, strict types.
- New migration after changing models (run the app once first so `.data` is at head): `uv run alembic -x url=sqlite:///.data/homestead_finance.db revision --autogenerate --rev-id 0003 -m "..."`. A test fails if models and migrations drift apart.

**Frontend** (run in `frontend/`):

- `pnpm install`, then `pnpm dev`: Vite on <http://localhost:5173>, proxying `/api` to the backend above.
- `pnpm test`, `pnpm lint`, `pnpm format:check`, `pnpm typecheck`, `pnpm build`.
- `pnpm gen:api`: regenerate the typed API client after changing backend endpoints. CI fails if it's stale.
- `pnpm build && pnpm ingress`: the built app behind a fake HA ingress at <http://127.0.0.1:8123/api/hassio_ingress/dev/>.
- `pnpm e2e`: Playwright through the fake ingress. Needs `pnpm build` first, and `pnpm exec playwright install chromium` once.
- `pnpm icons`: re-render the app store `icon.png` and `logo.png` from `src/assets/brand/*.svg`.

**Everything at once:** `uvx pre-commit run --all-files`.
