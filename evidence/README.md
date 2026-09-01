# Evidence capture guide

Create local artifacts under ignored `evidence/artifacts/`; never commit tokens, passwords, `.env`, prompt content, IP addresses, or other personal data. Redact by creating a copy—do not edit the sole original. Record UTC time, commit SHA, exact command, exit status, tool version, and environment limitation. Evidence demonstrates an observation, not universal security.

Suggested captures (run only in your authorized environment):

```bash
mkdir -p evidence/artifacts
git rev-parse HEAD | tee evidence/artifacts/commit.txt
python --version | tee evidence/artifacts/python-version.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 2>&1 | tee evidence/artifacts/application.log
curl -i http://127.0.0.1:8000/health | tee evidence/artifacts/health.txt
pytest -q | tee evidence/artifacts/pytest.txt
ruff check . | tee evidence/artifacts/ruff.txt
bandit -c pyproject.toml -r app | tee evidence/artifacts/bandit.txt
pip-audit | tee evidence/artifacts/pip-audit.txt
docker build -t secure-llm-lab:local . | tee evidence/artifacts/docker-build.txt
docker inspect --format '{{.Config.User}}' secure-llm-lab:local | tee evidence/artifacts/docker-user.txt
```

Use `curl` with temporary shell variables to capture successful/failed authentication, missing authentication, malformed JSON, and 429 responses; redact `Authorization` and token response bodies before retention. Capture the GitHub Actions run URL and job summaries from GitHub rather than fabricating local CI evidence.
