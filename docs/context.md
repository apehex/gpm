# Context

## Project Purpose

This repository explores password generation from a single master secret without storing per-service passwords.

The project currently contains (or will contain) two tracks:

1. `src/python/gpm/`: an experimental Python package, including neural-network-related ideas.
2. `src/python/gpm/`: a deterministic stateless CLI designed for practical and reliable use.

## Motivation

The practical objective is to build a password manager that is:

- stateless
- local-first
- explicit in behavior
- deterministic across time and environments (within a versioned spec)
- easy to inspect and audit

## Scope

In scope:

- deterministic password derivation from explicit inputs
- documented algorithm and format constraints
- reproducibility via test vectors
- shell-friendly CLI interface

Out of scope (for now):

- cloud sync
- remote APIs
- account storage backends
- browser extension integration
- hidden automation or "magic" behaviors

## Current Status

Early structuring and documentation phase.

Main upcoming work:

- split code layout cleanly between experimental and practical tracks
- define a stable derivation specification for the CLI
- implement and validate deterministic test vectors
