# Secure LLM Application

An **AI Security Engineering portfolio project and training laboratory**: a small production-shaped FastAPI assistant designed to be reverse-engineered, threat-modeled, attacked in an authorized environment, defended, and explained. It defaults to a deterministic local mock model and requires no paid service.

> This is educational software, not a production identity system and not “fully secure.” Read the [security assessment](docs/security-assessment.md) before exposing it beyond localhost.

## Architecture and technologies

Browser UI → FastAPI security/validation/authentication → prompt service → `LLMProvider` → mock model → JSON/plain-text rendering. Cross-cutting controls provide structured events, safe errors, rate limiting, request IDs, and HTTP headers. See the [Mermaid architecture](docs/architecture.md), [request data flow](docs/data-flow.md), and [threat model](docs/threat-model.md).

- Python 3.11+, FastAPI, Pydantic Settings, Uvicorn
- PBKDF2 password verifiers and HMAC-signed short-lived educational sessions
- Minimal dependency-free HTML/CSS/JavaScript UI
- pytest, Ruff, Bandit, pip-audit, Docker, and GitHub Actions
- No database, model tools, retrieval, file uploads, or chat persistence

## Quick start (local or GitHub Codespaces)

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
cp .env.example .env
# Set SLLM_TOKEN_SECRET in .env to: python -c 'import secrets; print(secrets.token_urlsafe(32))'
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. In Codespaces, make port 8000 **private** and use the forwarded URL. Training accounts are `learner` / `LearnerPass!2026` and `reviewer` / `ReviewerPass!2026`. These public credentials are for localhost only; generate replacement verifier records with `python scripts/hash_password.py` before any shared use.

```bash
curl -s http://127.0.0.1:8000/health
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login -H 'Content-Type: application/json' -d '{"username":"learner","password":"LearnerPass!2026"}' | python -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')
curl -s -X POST http://127.0.0.1:8000/api/chat -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"message":"Explain trust boundaries briefly."}'
unset TOKEN
```

## Testing and security checks

```bash
pytest -q
ruff check .
bandit -c pyproject.toml -r app
pip-audit
docker build -t secure-llm-lab .
docker run --rm -p 127.0.0.1:8000:8000 -e SLLM_TOKEN_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" secure-llm-lab
```

Normal behavior is under `tests/`; abuse/regression cases are under `security_tests/`. CI repeats tests, lint, static analysis, dependency audit, image build, and non-root-user inspection. Scanner output requires human triage; a clean scan is not proof of security. Follow [evidence capture instructions](evidence/README.md) and never fabricate results.

The implementation environment's actual pass/limitation record is in [docs/test-results.md](docs/test-results.md); rerun it in your Codespace rather than treating that point-in-time record as proof.

## Security controls and attack surface

- Strict JSON structures, forbidden extra fields, bounded credentials/prompts, and control-character rejection.
- Salted 600,000-round PBKDF2 verifiers, generic login failures, dummy unknown-user work, signed expiring tokens, and current server-side role checks.
- Login source and per-user chat throttles; intentionally only per-process for the lab.
- Typed separation of system, application, and user prompt content. Suspicious-pattern events are telemetry—not prevention and never a claim that keywords solve injection.
- No model tools or command/URL/code execution. JSON API output and browser `textContent` keep model output in a text context.
- Generic client errors; request correlation; metadata-only structured events without passwords, tokens, or full prompts.
- CSP, anti-framing/MIME-sniffing/referrer/cache headers; environment secrets; production rejection of the known development signing secret.
- Digest-pinned slim image, reduced build context, non-root runtime, and least-privilege CI permissions.

Reachable routes and abuse cases are inventoried in the [threat model](docs/threat-model.md). Important limitations include public demo accounts, no MFA/revocation, hand-built sessions, process-local throttling, ASGI body buffering, no TLS in Uvicorn instructions, no distributed tenancy, no real-provider privacy controls, and fundamental residual prompt-injection/model-risk. Deployment must supply TLS, edge body/time limits, central secrets/logs/rate limits, monitoring, and runtime isolation.

## Portfolio study path and evidence

1. Read `app/main.py`, then trace authentication and authorization in `app/auth.py`.
2. Follow message data through `app/models.py`, `app/service.py`, and `app/llm/provider.py`.
3. Map each test to the threat register and reproduce its observable result.
4. Answer—not memorize—the [mastery checklist](docs/mastery-checklist.md).
5. Preserve sanitized terminal, container, log, and CI observations using `evidence/README.md`.

Screenshot placeholder: add a sanitized UI image under `evidence/artifacts/` for private portfolio assembly; artifacts are ignored by Git to prevent accidental sensitive evidence commits.

## Future improvements

Project 2 can add adversarial prompt corpora, indirect injection sources, security evaluations, and tightly scoped fake tools. Production-oriented evolution should prioritize managed identity/MFA, centralized revocation/rate limiting, proxy limits/TLS, audited provider governance, policy-based tenant authorization, alerting, privacy lifecycle controls, lockfiles/hashes, SBOM/signing, and container/runtime scanning.

See [SECURITY.md](SECURITY.md) for reporting, [official references](docs/references.md), and the assessment for controls intentionally omitted.
