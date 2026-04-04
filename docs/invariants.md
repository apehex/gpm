# Invariants

Hard constraints for this repository.

## Product Invariants (Stateless CLI)

- password derivation must be deterministic for the same normalized inputs and algorithm version
- no floating-point arithmetic in derivation logic
- no runtime randomness in derivation logic
- no network access required for core derive command
- algorithm version must be explicit and documented
- behavior changes must be intentional and versioned
- all derivation rules must be testable via stable golden vectors

## Engineering Invariants

- no hidden state in core derivation path
- inputs and normalization rules must be explicit
- failures must be explicit (no silent fallback)
- documentation and implementation must remain aligned

## Repository Invariants

- `src/python/gpm/` remains experimental
- `src/<lang>/gpm/` is the deterministic stateless CLI track
- strategic changes must be logged in `docs/decisions.md`
