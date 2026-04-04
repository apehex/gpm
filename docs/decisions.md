# Decisions

Record of design and process decisions.

---

## 2026-04-04 - Split repository into two tracks

### Decision

Keep two separate source tracks in the same repository:

- `src/python/gpm/` for experimentation
- `src/<lang>/gpm/` for production-oriented stateless CLI

### Rationale

- preserve research freedom without destabilizing the practical CLI
- make expectations explicit for contributors and agents
- avoid mixing experimental NN logic with deterministic password derivation

### Consequences

- clearer boundaries and review criteria
- separate test strategy per track
- documentation must state purpose of each track

---

## 2026-04-04 - CLI must be deterministic and auditable

### Decision

The stateless CLI will avoid floating-point and runtime RNG in password derivation.

### Rationale

- reproducibility and long-term stability are core requirements
- avoid instability from numeric implementation differences

### Consequences

- derivation path should rely on deterministic cryptographic primitives
- behavior must be versioned and covered by golden test vectors

---

## 2026-04-04 - Local-first and explicit operations

### Decision

No synchronization, remote hosting dependency, or implicit side effects in core CLI behavior.

### Rationale

- reduce trust surface
- keep operational model simple and inspectable

### Consequences

- simpler threat model
- less convenience features, more predictability
