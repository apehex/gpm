# Specifications

This document defines the technical specifications used in this repository.

---

## Spec Index

| Spec ID | Name                              | Status  | Scope                            |
| ------- | --------------------------------- | ------- | -------------------------------- |
| GPM-001 | Stateless Password Derivation v1  | Draft   | Deterministic CLI core algorithm |
| GPM-002 | CLI Command Interface             | Draft   | Command-line flags and behavior  |
| GPM-003 | Test Vectors and Compatibility    | Draft   | Reproducibility and regression   |

---

## GPM-001 - Stateless Password Derivation v1 (Draft)

### Goals

- deterministic output for same inputs
- no floating-point operations
- no runtime randomness in derivation
- no network dependency
- explicit algorithm versioning

### Inputs

- `master_secret` (required)
- `target` (required) - service/site namespace (e.g. `github`)
- `identity` (required) - user/account identifier (e.g. `apehex`)
- `counter` (optional, default `1`) - rotation index
- `profile` (optional, default `default`) - output rules
- `algo_version` (required, default `gpm-v1`)

### Input Normalization Rules

All normalization must be explicit and stable:

- UTF-8 encoding
- Unicode normalization: NFKC
- trim leading/trailing spaces for `target` and `identity`
- lowercase `target`
- preserve case for `identity`
- `counter` is decimal ASCII integer (`1`, `2`, ...)
- field separator is `|` with escaped values if needed

Canonical context string format:

`gpm-v1|target=<target>|identity=<identity>|counter=<counter>|profile=<profile>`

### Key Derivation

1. `salt = SHA-256(context_string_utf8)`
2. `IKM = Argon2id(master_secret_utf8, salt, params_v1)`
3. `PRK = HKDF-Extract(salt_hkdf_v1, IKM)`
4. `OKM = HKDF-Expand(PRK, info=context_string_utf8, L=required_bytes)`

`params_v1` (initial draft):
- memory cost: 64 MiB
- iterations: 3
- parallelism: 1
- output length: 32 bytes

Note: parameter changes require a new algorithm version (e.g. `gpm-v2`).

### Password Materialization

Given `OKM` bytes and a profile charset:

- use rejection sampling to map bytes to charset indices
- avoid modulo bias unless explicitly documented
- continue HKDF expansion deterministically if more bytes are needed

### Constraints (optional, profile-defined)

Profiles may require classes:

- lowercase
- uppercase
- digits
- symbols

If required classes are configured, enforce deterministically:

- reserve fixed positions from derived stream
- fill required classes first
- fill remaining positions from global charset
- no random fallback

### Output

- derived password as UTF-8 string
- same inputs + same spec version => same output

---

## GPM-002 - CLI Command Interface (Draft)

### Command

`gpmanager derive [options]`

### Options (draft)

- `-k, --key` master secret (discouraged in shell history; prefer prompt/stdin)
- `-t, --target` service target (required)
- `-i, --identity` account identity (required)
- `-l, --length` output length
- `-p, --profile` profile name (default: `default`)
- `-c, --counter` rotation counter (default: `1`)
- `--algo-version` algorithm version (default: `gpm-v1`)
- `-w, --copy` copy to clipboard
- `--stdin-key` read master secret from stdin
- `--prompt-key` read master secret from hidden prompt
- `--no-symbols` profile override
- `--self-test` run built-in test vectors

### Behavior Rules

- no network calls in `derive`
- no password persistence by default
- deterministic errors with non-zero exit codes
- `--copy` should support auto-clear timeout if implemented

### Security UX Rules

- warn when `--key` is passed directly
- prefer `--prompt-key` for interactive use
- never print sensitive internals in debug logs

---

## GPM-003 - Test Vectors and Compatibility (Draft)

### Purpose

Prevent accidental derivation drift across:

- refactors
- dependency updates
- multi-language implementations

### Vector Format (draft)

Each vector must include:

- algorithm version
- normalized input fields
- profile
- expected password output
- optional notes

Example schema:

```yaml
- id: tv001
  algo_version: gpm-v1
  input:
    master_secret: "correct horse battery staple"
    target: "github"
    identity: "apehex"
    counter: 1
    profile: "default"
    length: 20
  expected:
    password: "<fixed expected output>"
```

### Compatibility Policy

- existing vectors for a released version must remain unchanged
- breaking behavior changes require new algorithm version
- CI must fail on vector mismatch for stable versions

---

## Versioning Policy

- Specs use semantic-like versioning at the algorithm level (`gpm-v1`, `gpm-v2`)
- Documentation changes that do not alter behavior do not require new algorithm version
- Any output-changing change requires:
  1. new version ID
  2. migration note in `docs/decisions.md`
  3. new test vectors

---

## Open Items

- finalize Argon2id parameter values for target hardware classes
- define built-in profile catalog (`default`, `web-basic`, `pin`, etc.)
- define escape rules for reserved characters in context fields
- define clipboard behavior per OS
