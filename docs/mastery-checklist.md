# Mastery checklist

Do not use this as a trivia sheet. Trace code, draw the boundary, change one variable, predict the outcome, run the named test, and preserve evidence. Answer in your own words.

## HTTP composition and middleware (`app/main.py`)

- **WHAT:** What endpoints and middleware exist? What data does a request ID represent?
- **WHY:** Why centralize safe validation/unexpected-error responses and security headers?
- **WHERE:** Where does untrusted HTTP become application data? Where should a proxy boundary sit?
- **HOW:** How does middleware order affect exceptions and headers? How could forged request IDs or proxy headers be abused?
- **WHEN:** When are headers attached? Which server/protocol failures could bypass application handlers?
- **DEFENSE:** Which headers address MIME sniffing, framing, referrers, caching, and script policy? What do they not address?
- **VERIFICATION:** Which assertions in `test_health_and_security_headers` prove observable behavior? Inspect with `curl -i`.
- **CHANGE:** Remove one header or exception handler in a temporary branch. Which attack or disclosure becomes more plausible?

## Configuration and secrets (`app/config.py`, `.env.example`)

- **WHAT:** Which values are configuration, which are secrets, and which defaults are deliberately unsafe only for local use?
- **WHY:** Why use environment injection and `SecretStr`? Why does `SecretStr` not solve runtime compromise?
- **WHERE:** Where does configuration cross into the process? Where can `.env`, CI, shell history, and container metadata leak it?
- **HOW:** How is production-default rejection validated? How would key rotation affect existing tokens?
- **WHEN:** When is configuration read and cached? When must the cache be cleared in tests?
- **DEFENSE:** What would a managed secret store, short-lived workload identity, or dual-key rotation improve?
- **VERIFICATION:** Run `test_production_rejects_default_secret`; inspect tracked files with `git grep` and a secret scanner.
- **CHANGE:** Predict startup and token behavior after changing environment, secret, or TTL.

## Password authentication and sessions (`app/auth.py`)

- **WHAT:** What are salt, verifier, PBKDF2 iteration cost, signature, claims, and bearer credential?
- **WHY:** Why compare in constant time and compute a dummy hash for unknown users? Why are public demo credentials still unacceptable in deployment?
- **WHERE:** Where are authentication and token trust decisions made? Where does the browser hold the token?
- **HOW:** Trace password → verifier comparison → signed token → claim validation. Attempt signature, role, expiry, and subject modifications.
- **WHEN:** When does authentication fail before authorization? When would token revocation be required but unavailable?
- **DEFENSE:** Compare this design with Argon2id, secure server sessions, OAuth/OIDC, MFA, HttpOnly cookies, and CSRF tokens.
- **VERIFICATION:** Map valid/invalid/protected tests to each branch; measure but do not overinterpret timing distributions.
- **CHANGE:** Reduce iterations, remove signature validation, persist in localStorage, or skip current-role lookup—what changes?

## Authorization (`require_reviewer`, protected routes)

- **WHAT:** What is authentication versus authorization? What resources and roles exist?
- **WHY:** Why must the API enforce role checks even when the UI hides a feature?
- **WHERE:** Where is the policy decision and where is it enforced? Is that separation sufficient for more roles/resources?
- **HOW:** How could claim tampering, direct endpoint access, or confused-deputy flows target it?
- **WHEN:** When is the reviewer dependency evaluated? Which future object operations need ownership checks?
- **DEFENSE:** Compare RBAC with ABAC/ReBAC and centralized policy engines.
- **VERIFICATION:** Explain every step of `test_server_side_authorization_rejects_user`; repeat with both demo roles.
- **CHANGE:** Replace `require_reviewer` with `current_user` and predict the result before testing.

## Validation and rate limiting (`app/models.py`, `app/rate_limit.py`)

- **WHAT:** Which structure, type, length, character, and extra-field constraints exist? What does the limiter count?
- **WHY:** Why validate at both schema and configured-policy layers? Why bound authentication and chat independently?
- **WHERE:** Where is a body buffered before validation? Where should edge body limits exist?
- **HOW:** Trace malformed JSON, whitespace, control characters, oversized input, and repeated requests. Identify limiter keys.
- **WHEN:** When does a request consume a slot? Are failures counted? What happens on restart or with multiple workers?
- **DEFENSE:** Compare token bucket/sliding window, Redis atomic scripts, gateway limits, timeouts, concurrency and cost quotas.
- **VERIFICATION:** Run malformed, oversized, and rate tests; inspect `Retry-After` and logs.
- **CHANGE:** Modify window, identity key, or `extra=forbid`. Which bypasses or denial scenarios appear?

## Prompt construction and injection telemetry (`app/service.py`)

- **WHAT:** Distinguish system instruction, application context, and user message. What does the heuristic detect?
- **WHY:** Why keep trust classes separate? Why is a system prompt or keyword list not a security boundary?
- **WHERE:** Where could secrets/tools/retrieved text enter in Project 2? Mark every future indirect-injection source.
- **HOW:** Follow harmless override attempts through the envelope. How can casing, encoding, languages, indirection, or model behavior bypass detection?
- **WHEN:** When is telemetry emitted? Why is the request currently allowed rather than blocked?
- **DEFENSE:** Explore least-privilege tools, capability tokens, confirmation, provenance, context isolation, output schemas, monitoring, and model evaluations.
- **VERIFICATION:** Inspect `test_suspicious_prompt_is_data_and_logged_without_body`; add variants without converting the regex into a claimed defense.
- **CHANGE:** Concatenate all prompt fields or add a secret to context. Explain the new leakage path.

## Provider abstraction (`app/llm/provider.py`)

- **WHAT:** What contract does `LLMProvider` define? What makes the mock deterministic?
- **WHY:** Why isolate provider-specific transport from authentication and authorization?
- **WHERE:** Where would the external data/availability/cost boundary appear for a real adapter?
- **HOW:** Map serialization, TLS, timeouts, retries, response bounds, provider errors, and data retention needed by an adapter.
- **WHEN:** When should retries occur, and when could they duplicate cost or amplify denial of service?
- **DEFENSE:** What egress allow-list, credentials scope, contracts, privacy controls, circuit breakers, and quotas are alternatives?
- **VERIFICATION:** Run the deterministic mock and safe-provider-error tests; design a fake timeout test.
- **CHANGE:** Make the mock nondeterministic or let it read configuration secrets. Which testability/security properties disappear?

## Output handling and browser UI (`app/static/`)

- **WHAT:** Why is model output untrusted? What is the difference between `textContent` and `innerHTML`?
- **WHY:** Why prohibit automatic execution/navigation/tool calls even if output looks structured?
- **WHERE:** Where does model text cross API → DOM? Where could URL, Markdown, or code renderers add interpreters?
- **HOW:** Trace HTML-like output through JSON escaping and DOM assignment. Test text that resembles scripts, commands, and links.
- **WHEN:** When would output schema validation, sanitization, sandboxing, or confirmation be needed?
- **DEFENSE:** Compare plain text, sanitizer allow-lists, sandboxed origins/iframes, and CSP as layered—not interchangeable—controls.
- **VERIFICATION:** Explain `test_model_output_is_json_string_not_active_html`; inspect the DOM, not just source text.
- **CHANGE:** Substitute `innerHTML`; use a harmless marker to observe changed interpretation, then revert immediately.

## Logging and telemetry (`app/logging_config.py`)

- **WHAT:** Which security event categories and allow-listed fields exist? What is deliberately absent?
- **WHY:** Why are prompt bodies/passwords excluded? Why do request IDs help incident investigation?
- **WHERE:** Where do stdout logs cross into operator/collector trust? Who can read, retain, or export them?
- **HOW:** Trigger each event and correlate it without user text. Check newline/structured-log injection behavior.
- **WHEN:** When should an event become an alert? Which baselines and false-positive process are needed?
- **DEFENSE:** Consider field schemas, pseudonymization, access controls, encryption, retention/deletion, tamper evidence, and SIEM rules.
- **VERIFICATION:** Capture local logs according to `evidence/README.md`; confirm secrets and prompt bodies are absent.
- **CHANGE:** Log request bodies for debugging. Enumerate privacy, compliance, credential, and injection consequences.

## Container, dependencies, and CI

- **WHAT:** What runs as non-root, what is pinned, and which tests/scanners execute?
- **WHY:** Why digest-pin a base, omit secrets/build context, and separate independent CI checks?
- **WHERE:** Mark source → GitHub Actions → package registry → image trust boundaries.
- **HOW:** Inspect image user/history/layers and dependency tree. How could a compromised action/package/base enter?
- **WHEN:** When are pins updated and vulnerability findings triaged rather than blindly suppressed?
- **DEFENSE:** Add least-privilege workflow permissions, hashes/lockfiles, Dependabot, SBOM, signing, provenance, read-only runtime, and scanning.
- **VERIFICATION:** Reproduce every CI command locally and preserve actual output. Inspect `docker image inspect` user.
- **CHANGE:** Run as root, copy `.env`, use floating action/package tags, or disable a scan. Describe the increased risk.
