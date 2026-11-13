# Homestead Finance: notes for Claude

The product is a Home Assistant add-on (FastAPI + SQLite backend, React/TypeScript frontend) plus a companion HA integration (Python). The reference design is [docs/superpowers/specs/2026-11-13-homestead-finance-design.md](docs/superpowers/specs/2026-11-13-homestead-finance-design.md); read the parts relevant to the task before changing behavior.

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
- **Ingress:** the frontend uses relative URLs only, because HA ingress serves it under a dynamic base path. Never hardcode `/`.

## Commands
No code exists yet. M1 (Foundation) adds the build, test and run commands here.
