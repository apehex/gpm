# References

External references used to guide architecture and implementation choices.

## Cryptography / Standards

- RFC 9106 - Argon2 Memory-Hard Function for Password Hashing and Proof-of-Work
- RFC 5869 - HMAC-based Extract-and-Expand Key Derivation Function (HKDF)
- NIST SP 800-132 - Recommendation for Password-Based Key Derivation

## Deterministic Password Generation Concepts

- LessPass (stateless password generation model)
- Spectre / Master Password family (deterministic, stateless derivation)

## Python / CLI Implementation References

- Python `argparse` documentation
- Python `hashlib`, `hmac`, and `secrets` documentation
- `pyperclip` (optional clipboard integration, if retained)

## Notes

References here are directional. Final implementation choices and parameters must be recorded in `docs/decisions.md`.
