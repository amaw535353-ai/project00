# Security assessment

## Implemented controls

The application implements schema allow-listing and length limits; PBKDF2 password verification; signed expiring sessions; server-side role checks; login/chat throttling; separated prompt trust classes; deterministic provider isolation; output-as-data rendering; safe error translation; security headers; environment secrets; metadata-only JSON logs; non-root container execution; pinned Python packages; and test/static/dependency scanning in CI.

## Known weaknesses and residual risks

- Authentication is educational: two code-defined accounts have documented demo passwords, no registration/reset/MFA, no lockout, no revocation, and a hand-built token format. Production should use an audited identity provider, opaque or standards-based sessions, MFA, key rotation, secure cookies plus CSRF controls where appropriate, and account lifecycle controls.
- PBKDF2 protects stored verifiers but demo credentials are public. Replace them before any shared deployment. The development signing default is public; production configuration rejects it.
- In-memory rate state is per process, disappears on restart, and does not solve distributed abuse. Use an atomic shared limiter and edge protections. Enforce request-body limits and timeouts at the proxy/server.
- Prompt injection remains possible. Pattern matching supplies a signal only. The strongest current mitigation is absence of tools, retrieval, and secrets from model context. Future tools require capabilities, argument validation, user confirmation, least privilege, and audit trails.
- CSP includes same-origin script and style; compromise of served JavaScript remains powerful. No automated CSP reporting, SRI, malware scanning, or WAF is present.
- Prompts are reflected by the mock and could expose shoulder-visible sensitive text. There is no content classification, DLP, moderation, conversation persistence, deletion workflow, or tenant isolation.
- There is no real provider adapter by design. Before adding one, assess retention, training use, region, credentials, egress, timeouts, retries, costs, response size, and contractual controls.
- Availability controls, TLS, log storage/access/retention, runtime seccomp/read-only filesystem, image signing/SBOM, and secret rotation are deployment responsibilities.

## Intentionally omitted

SQLite, chat history, RAG, file upload, tool execution, URL fetching, admin mutation, and a real model were omitted to keep the first lab's attack surface explainable. Their absence is a security design decision, not a claim that production systems do not need them.

## Production priorities

Adopt managed identity; central rate limiting; a reverse proxy with TLS/body/time limits; a secrets manager and rotated keys; centralized access-controlled logs with alerts; persistent audit event IDs; real tenant/resource authorization; dependency update automation; SBOM/image signing; hardened orchestration; privacy review; and adversarial evaluation for the selected model/provider.

This assessment is point-in-time and does **not** claim the application is fully secure.
