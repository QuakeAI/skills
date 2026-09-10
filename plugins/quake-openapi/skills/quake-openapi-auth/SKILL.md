---
name: quake-openapi-auth
description: Explain public Quake OAuth flows, token exchange, delegated sessions, bearer use, operation security requirements, and scopes from the live OpenAPI. Use when a developer asks how to authenticate, choose a documented OAuth flow, obtain or refresh a token, determine scopes, or diagnose a specification-level authentication mismatch. Never obtain, expose, persist, or use credentials.
license: Apache-2.0
metadata:
  compatibility: Requires Python 3 and outbound HTTPS access to api.quake.dev.
---

# Understand Quake OpenAPI Authentication

Use the current public specification at `https://api.quake.dev/openapi.json`. Authentication details are security-sensitive and may change; never answer from memory.

## Workflow

1. Identify the target operation and whether the developer needs app-scoped access or a user-delegated session. If the target operation is unknown, use this skill's bundled helper `find` command, then inspect the exact match.
2. Fetch one task-local snapshot with the bundled helper and reuse it.
3. Inspect every documented security scheme:

   ```bash
   python3 <skill-directory>/scripts/quake_openapi.py --spec <snapshot> show security
   ```

4. Inspect the target operation. Its operation-level `security` overrides document-level security, including an explicit empty array:

   ```bash
   python3 <skill-directory>/scripts/quake_openapi.py --spec <snapshot> show operation --id <operationId>
   ```

5. Inspect the documented authorize, token, session-exchange, refresh, or session operation and every referenced request and response schema that applies.
6. Verify required scope and response-status claims with `verify operation`. Verify exact security-scheme and request-field claims with `verify value` and a JSON Pointer.
7. Explain the documented flow, endpoints, required inputs, scopes, and token use with placeholders only. Label every ambiguity or inconsistency.

Read [references/auth-guide.md](references/auth-guide.md) before selecting a flow or producing an authentication example.

## Safety boundary

- Never ask the developer to paste a client secret, access token, refresh token, authorization code, or session value into chat.
- Never obtain, exchange, refresh, persist, print, validate, or use credentials on the developer's behalf.
- Use placeholders such as `<QUAKE_CLIENT_ID>` and environment-variable references in examples.
- Do not imply that a documented scope alone guarantees access; report only what the specification says.
- If an operation references a missing security scheme, report the mismatch exactly. Do not silently map it to a similarly named scheme.

## Output contract

Provide:

- the target operation and its documented security requirement;
- the chosen documented OAuth flow and why it fits the stated use case;
- documented authorization, token, session, or refresh endpoints as applicable;
- required and conditional inputs, with secrets represented only by placeholders;
- documented scopes and response statuses; and
- any unresolved specification gaps that prevent a confident answer.

Do not generate runnable secret-bearing commands. A template with empty placeholders is acceptable when requested.
