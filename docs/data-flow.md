# Data flow

## Authentication

1. The browser sends JSON credentials over the browser-to-API boundary. TLS is required outside localhost.
2. Pydantic rejects unknown fields, malformed names, and unreasonable lengths.
3. The source-address limiter runs before password verification. The backend performs PBKDF2 and constant-time hash comparison, including dummy work for unknown users.
4. Logs contain outcome, username, and observed address—not the password. A successful response contains a short-lived signed bearer token.
5. The UI retains the token only in JavaScript memory. Refresh signs the user out; this reduces persistence but does not defeat same-origin script compromise.

## Authorized chat

1. Middleware creates a request ID. Pydantic bounds the JSON message at 2,000 characters and rejects extra properties/control characters.
2. The API verifies token signature, expiry, subject, and current role. It rate-limits by authenticated identity.
3. Prompt-pattern detection emits metadata only. It is an observable heuristic, not a blocker and not an injection solution.
4. The service constructs `PromptEnvelope(system_instructions, application_context, user_message)` without concatenating those trust classes.
5. The provider receives the envelope. A future remote adapter would create a new data-processing and egress boundary.
6. Returned model text is untrusted. FastAPI JSON-encodes it; browser JavaScript uses `textContent` rather than HTML parsing.
7. Expected provider errors become a generic 502. Validation errors and unexpected errors return a request ID but no stack trace or internal path.

## Data classification and retention

Passwords and signing secrets are secret. Tokens are bearer credentials. Prompts and responses may be sensitive user content. Security logs intentionally contain only event metadata and currently follow standard-output retention. The application has no database and does not intentionally persist chats.
