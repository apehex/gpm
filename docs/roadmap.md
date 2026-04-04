# Roadmap

Planning and progress tracker.

## Phase 0 - Repository Structuring

- [ ] create `docs/` structure
- [ ] move/update README content into `docs/` as needed
- [ ] split source layout into:
  - [ ] `src/python/gpm/` (experimental)
  - [ ] `src/<lang>/gpm/` (stateless CLI)

## Phase 1 - CLI Specification (v1)

- [ ] define command contract and flags
- [ ] define canonical input normalization rules
- [ ] define deterministic derivation algorithm
- [ ] define output profile system (length, charset, constraints)
- [ ] define error model and exit codes
- [ ] publish first stable spec draft in docs

## Phase 2 - Reference Implementation

- [ ] implement minimal derive command
- [ ] implement profile handling
- [ ] add clipboard option with explicit behavior
- [ ] add self-test command
- [ ] add deterministic golden vectors

## Phase 3 - Hardening

- [ ] threat model document
- [ ] side-effect and logging review
- [ ] reproducibility checks across platforms
- [ ] docs review for operator clarity

## Open Questions

- [ ] exact namespace and naming for the CLI package (`gpm` vs alternatives)
- [ ] migration/compatibility story between future algorithm versions
- [ ] minimum supported Python version for CLI track
