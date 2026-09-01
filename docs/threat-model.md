# Threat model

## Scope, assets, actors, entry points

**Assets:** password verifiers, signing/API secrets, bearer tokens, prompts, user content, model responses, security logs, service availability, and authorization state.

**Actors:** normal users, authenticated malicious users, unauthenticated attackers, operators/log readers, dependency attackers, and a future external LLM provider.

**Externally reachable entry points:** `GET /`, `/app.js`, `/static.css`, `/health`; `POST /api/auth/login`; authenticated `GET /api/me`, `GET /api/reviewer`, and `POST /api/chat`. Container port 8000 and CI inputs/dependencies are administrative supply-chain entry points.

**Trust boundaries:** browser → API; routing → authentication/authorization; validated API → prompt layer; application → LLM provider; environment → configuration; application → standard-output logs; source repository → CI/dependency registries.

## Threat register

| Threat | Asset | Entry point / attack path | Impact | Existing control | Residual risk | Verification |
|---|---|---|---|---|---|---|
| Credential guessing/enumeration | Account/token | Repeated login attempts, response/timing comparison | Account takeover | Generic failure, PBKDF2, dummy hash, rate limit | Distributed guessing; known demo passwords | `test_invalid_authentication`, `test_rate_limiting` |
| Forged/stolen token | Authorization/user data | Modify claims or steal browser memory | Impersonation | HMAC signature, expiry, current-user/role lookup, no localStorage | XSS/client compromise; no revocation | auth and protected-endpoint tests |
| Missing object/role authorization | Reviewer resource | Direct call ignoring UI | Privilege escalation | Server-side dependency checks current role | Coarse two-role model | `test_server_side_authorization_rejects_user` |
| Parameter pollution/malformed JSON | Parser/service | Extra role, wrong type, broken JSON | Control bypass or error disclosure | `extra=forbid`, typed bounds, generic validation response | Parser/dependency flaws | `test_malformed_and_extra_fields_rejected` |
| Oversized request | Availability/memory | Very long prompt/body | Resource exhaustion/cost | Field length and configured cap | ASGI still buffers body; proxy body cap needed | `test_oversized_input_rejected` |
| Prompt injection | Instructions/secrets | User asks model to override/reveal | Policy bypass or leakage | Trust-class envelope, no tools/secrets in prompt, telemetry | Model may obey; detection is bypassable | `test_suspicious_prompt_is_data_and_logged_without_body` |
| Secret leakage | Secrets | Error, log, repo, prompt | Credential compromise | env settings, `.gitignore`, redacted logging, generic errors | Operator mistakes/core dumps | config and safe-error tests |
| Sensitive log exposure | Prompts/user data | Prompt copied to structured logs | Privacy loss | Events log length/category, not bodies/passwords | Username/IP are personal metadata | inspect captured logs |
| Unsafe model rendering | Browser/session | Model returns HTML/script/URL | XSS, phishing, command execution | JSON serialization + DOM `textContent`; no tool executor | Social engineering in plain text | `test_model_output_is_json_string_not_active_html` |
| Provider misuse/failure | Availability/privacy | Remote response/error or provider retains prompts | Outage/data exposure | isolated adapter, generic 502, local mock default | Future adapter governance not implemented | mock and safe-error tests |
| Denial of service | Availability | Login/chat flood, expensive PBKDF2 | CPU/memory exhaustion | per-process limiter, bounded message | multi-process bypass, IP rotation, request body buffering | rate-limit test |
| Dependency/container compromise | Code/secrets | Malicious/outdated package or root process | Arbitrary execution | pins, audit/static CI, digest-pinned slim base, non-root user | Registry/CI compromise; updates required | CI, `pip-audit`, container inspection |

## Explicit assumptions

TLS, network filtering, log access, backups, secret injection, proxy body limits, and host/container runtime controls belong to deployment. The training instance contains no high-value data. A security owner reviews dependency alerts and suspicious events. The model has no tools or retrieval access.
