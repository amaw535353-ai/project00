# Security references

These primary/official sources are starting points for the security owner. Record access dates and the exact section used when making a future design change.

- [OWASP Top 10 for Large Language Model Applications](https://genai.owasp.org/llm-top-10/) — prompt injection, insecure output handling, sensitive disclosure, and excessive agency.
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) — authentication responses and defenses.
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) — password hashing choices and work factors.
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) — security-event content and data exclusion.
- [OWASP HTTP Headers Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html) — browser response hardening.
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) — governance and lifecycle risk management.
- [MITRE ATLAS](https://atlas.mitre.org/) — adversarial tactics and techniques for AI-enabled systems.
- [FastAPI security documentation](https://fastapi.tiangolo.com/tutorial/security/) and [handling errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) — framework mechanisms used by the API.
- [Python `hashlib` documentation](https://docs.python.org/3/library/hashlib.html) and [`hmac` documentation](https://docs.python.org/3/library/hmac.html) — PBKDF2 and constant-time comparison primitives.
- [GitHub secure use reference](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions) — workflow permissions, third-party actions, and CI trust.
- [Docker build best practices](https://docs.docker.com/build/building/best-practices/) — image construction, base images, and build context.

Automated internet lookup was unavailable in the implementation environment; therefore this file uses stable official project documentation URLs and makes no claim that a particular revision was reviewed on 2026-08-31.
