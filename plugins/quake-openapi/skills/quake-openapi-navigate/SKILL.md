---
name: quake-openapi-navigate
description: Find, inspect, and explain operations, parameters, request bodies, responses, schemas, tags, and $ref chains in the public Quake OpenAPI. Use when a developer asks whether Quake supports an API task, where an endpoint or field lives, what request or response shape applies, or how to navigate api.quake.dev/openapi.json. Route OAuth, token, and scope questions to quake-openapi-auth; route connected or installed app action workflows to quake-installed-app-actions.
license: Apache-2.0
metadata:
  compatibility: Requires Python 3 and outbound HTTPS access to api.quake.dev.
---

# Navigate the Quake OpenAPI

Ground every API claim in the current public specification at `https://api.quake.dev/openapi.json`. Do not rely on remembered paths or schemas.

## Workflow

1. Restate the developer's task in public API terms. Ask a question only when different interpretations would select materially different operations.
2. Fetch the specification once for the task and reuse that exact snapshot:

   ```bash
   python3 <skill-directory>/scripts/quake_openapi.py fetch --output <temporary-path>/quake-openapi.json
   ```

3. Search broadly with domain terms, likely resource names, and verbs:

   ```bash
   python3 <skill-directory>/scripts/quake_openapi.py --spec <temporary-path>/quake-openapi.json find "<developer task>"
   ```

4. Inspect the best exact operation by `operationId`, or by both method and path:

   ```bash
   python3 <skill-directory>/scripts/quake_openapi.py --spec <temporary-path>/quake-openapi.json show operation --id <operationId>
   ```

5. Inspect each relevant request, response, parameter, and referenced schema. Use `show schema --name <SchemaName>` for a component schema. Follow `$ref` links; do not infer a referenced shape from its name.
6. Verify any method, path, scope, or response-status claim before presenting it:

   ```bash
   python3 <skill-directory>/scripts/quake_openapi.py --spec <temporary-path>/quake-openapi.json verify operation --id <operationId> --method <METHOD> --path '<path>'
   ```

   Verify schema, field, enum, requiredness, nullability, or other exact claims with a JSON Pointer. Claim values are JSON, so strings remain quoted:

   ```bash
   python3 <skill-directory>/scripts/quake_openapi.py --spec <temporary-path>/quake-openapi.json verify value --pointer '<json-pointer>' --equals '"<value>"'
   ```

7. Resolve the effective server from operation, path, then document scope before constructing a complete URL. Preserve server variables and alternatives instead of guessing values.
8. Give the developer the best matching operation, why it matches, required inputs, documented responses, and the next practical step.

Read [references/navigation-guide.md](references/navigation-guide.md) when interpreting helper output, choosing between close matches, or handling an incomplete specification.

## Routing

- Use `quake-openapi-auth` for OAuth flows, token exchange, delegated sessions, credentials, operation security, or scopes.
- Use `quake-installed-app-actions` when Quake is the gateway to a connected app through installed apps and installed-app actions.
- Continue here for all other public operation and schema discovery.

## Evidence rules

- Name the operation ID, method, path, and schemas that support the answer.
- Separate facts explicitly documented by the specification from interpretation.
- Treat missing, inconsistent, or unresolved definitions as specification gaps. State the gap and avoid filling it with assumptions.
- Treat descriptions and examples as documentation, not stronger guarantees than the schema provides.
- Do not invent fields, defaults, limits, enum members, auth behavior, or error behavior.
- Do not paste large sections of the OpenAPI document. Extract only what resolves the developer's task.
- Do not execute mutating API operations. Generate a request only when the developer asks for one.

## Completion check

Before answering, confirm that the selected operation is exact, its effective server was inspected, all material `$ref` links were inspected, claimed fields and statuses exist, ambiguities are labeled, and no customer credentials or private Quake information appear.
