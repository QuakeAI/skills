# Live Quake OpenAPI profile for skill and evaluation design

## Research question

Which structural patterns, authentication shapes, schema relationships, and representative API domains in the live public Quake OpenAPI must the skill contracts, query tooling, and evaluations handle?

## Source and method

The sole source for Quake API facts in this note is the public [Quake OpenAPI document](https://api.quake.dev/openapi.json). It was fetched on 2026-08-05 at 10:41 UTC. At that moment it identified itself as OpenAPI `3.1.0`, API title `Quake Core API`, API version `0.1.0`, and production server `https://api.quake.dev`. The fetched JSON was 482,836 bytes with SHA-256 `2ff49fd301645c9000b6d8fc98ecd5b516ef228216fc8152908b3aa538c915c9`.[^spec]

Counts below were obtained by enumerating HTTP-method entries under `paths`, not by assuming every path item is an operation. Because the live document is authoritative and can change, these counts are a dated profile, not constants to embed in a skill.

## Decision

The three v1 skills and their tooling should treat the document as a searchable graph, not a flat endpoint catalog. They must be able to select an operation by several signals, preserve operation-level security exactly, traverse arbitrary local schema references and JSON Schema composition, and report response envelopes and ambiguity without normalization or invention. The golden evaluation set should cover the structural families and explicit irregularities below rather than sampling only straightforward CRUD operations.[^spec]

## Structural profile

At the time of inspection, the document contained 127 paths, 199 operations, 28 declared tags, 205 component schemas, two security schemes, no webhooks, and no reusable component parameters. The operations were distributed across 84 `GET`, 57 `POST`, 28 `DELETE`, 25 `PATCH`, and five `PUT` methods. The largest tag was `Skills` with 30 operations; `Candidates` had 14, `Custom Lists` 12, `Job Leads` and `Tags` 10 each, and the remaining domains ranged from one to nine operations.[^spec]

Operation lookup cannot depend on one index:

- All operations had exactly one tag, but one `PUT /recruitment/applications/{id_token}` operation had no `operationId`.
- No `operationId` was duplicated.
- The operation tag `AI Chat` was not declared in the top-level tag list, while the declared `External Chat` tag had no operation using that exact name.
- 169 operations had summaries, 146 had descriptions, and 14 descriptions contained Markdown headings. Some descriptions carry essential encoding, filtering, authorization, ordering, or lifecycle rules that are not expressible in the surrounding schema.

The navigation skill and query CLI should therefore search and return path, method, `operationId` when present, tag, summary, and description. Tag and `operationId` indexes are useful accelerators, but neither is a validity boundary. The CLI should also offer validation findings for missing IDs and tag declaration mismatches without refusing to inspect those operations.[^spec]

## Authentication and security shapes

The document defines two OAuth 2.0 component security schemes:[^spec]

- `Oauth2 Client Credentials` uses a client-credentials flow with token URL `/oauth/token`.
- `Oauth2 Authorization Code` uses authorization URL `https://app.quake.dev/api/openapi/authorize` and token URL `/oauth/token`.

Both scheme definitions enumerate the same 90 scope names. Across operation security requirements, 40 distinct enumerated scope names were used. Most protected operations name a domain read, write, or delete scope. The authentication surface also documents two different authorization-code outcomes: standard exchange at `/oauth/token`, or a delegated session exchange at `/oauth/session`, with refresh at `/oauth/session/refresh` and session inspection at `GET /session`. The three token/session exchange operations accept both JSON and form-urlencoded bodies.[^spec]

The security data has important irregularities that must remain visible:

- There is no top-level `security` requirement.
- Operation requirements refer to a scheme named `Bearer`, but no `Bearer` scheme exists under `components.securitySchemes`; only the two OAuth schemes above are defined.
- Eleven operations omit an operation-level `security` field. This set includes the five `Auth` operations, app discovery operations, `POST /core/search`, and the public application submission operation. Some prose still refers to a presented bearer token or authorization behavior, so the skills must call this an ambiguity rather than silently equating “field absent” with a verified usage claim.
- Six custom-entity record operations encode `[{"Bearer": []}]`, while their descriptions state dynamic requirements such as `customEntities.<customEntityId>:read` or `customEntities.<customEntityId>:write`. Those dynamic strings are not members of the 90 enumerated scopes.
- `GET /core/ai-chat-defaults`, `GET /core/ai-agents`, and `GET /core/llm-models/allowed` each contain two separate security requirement objects, one naming `agentChats:write` and the other `ai_agents:read`.
- `POST /core/options/records` places seven read scopes in a single security requirement object. The tooling must preserve the distinction between separate requirement objects and multiple scopes within one object.

The authentication skill should use the OAuth flow definitions to explain flow inputs and endpoints, while taking required scopes from the selected operation. It should never repair the `Bearer`/OAuth scheme-name mismatch on its own. When the selected operation has missing, empty, dynamic, or structurally ambiguous security metadata, the answer should quote the relevant fields and description and explicitly state what the document does and does not establish.[^spec]

## Parameters, request bodies, and encoding

All 261 parameters were operation-local: 146 query, 110 path, and five header parameters. None used component `$ref`, parameter `content`, or explicit `style`/`explode`. There were 116 required and 145 optional parameters. Common names recur across domains, but their constraints are not uniform: `limit` and `offset` are common, custom entities use `page` and `pageSize`, custom lists use `page` and `page_size`, and placements expose both limit/offset and page-style names. The five header parameters are `if-none-match` on settings endpoints, paired with documented ETag-related response headers and `304` responses.[^spec]

Several list endpoints encode structured input inside string query parameters. For example, candidate and job list operations define `filters` and `search` as JSON strings, while `sort` or `select` may be comma-separated strings. Limits, defaults, allowed fields, search behavior, and response selection are operation-specific and often live in descriptions. A request generator must URL-encode these strings and must not turn them into JSON request bodies or infer one domain's caps and fields from another.[^spec]

There were 87 operations with request bodies. All offered `application/json`; the three token/session exchange operations additionally offered `application/x-www-form-urlencoded`. Seventy-one JSON media entries referred directly to component schemas and 16 used inline schemas. Only one request body explicitly set `required: true`; the other 86 omitted it. This is distinct from required properties inside the selected body schema and must be represented separately.[^spec]

The request skill should produce a compact, lossless operation view containing:

1. path, method, server, and path substitution requirements;
2. each parameter's location, required flag, schema constraints, default, example, and description;
3. available body media types and the request body's own required flag;
4. the recursively resolved body schema while retaining `$ref` provenance, composition, required-property arrays, and `additionalProperties`; and
5. all documented success and error responses, including headers and body absence.

## Responses and documented errors

The 199 operations declared 788 response entries. Documented success statuses included `200`, `201`, `202`, `204`, `302`, and `304`. Twenty-three responses had no body schema. Success bodies varied materially: 114 were direct schema references, 29 were inline arrays, and 40 were inline objects. List shapes are not standardized: candidates return a bare array, jobs return an object with `data` and `total`, and custom-entity records return `data`, `total`, `page`, and `pageSize`. A skill must report the selected operation's exact envelope rather than inventing a universal pagination wrapper.[^spec]

The spec includes 582 error response entries covering `400`, `401`, `403`, `404`, `409`, `422`, `429`, `500`, `502`, and `503`. Of those, 578 point to `ErrorResponse`, an object requiring string fields `error` and `message`. Four candidate-document deletion errors instead use `CandidateDocumentDeleteFailure`, which requires `status: "fail"` and `error`. Status descriptions also carry operation-specific distinctions, so a generator should include both status and description and must not assume all errors share one body.[^spec]

Two asynchronous patterns make good request/response tests: installed-app action execution may return either `200` or `202`, and notes batch creation returns `202`. Separately, `204`, redirect, cache-validation, and multi-success-status operations test whether generated code handles bodyless or alternate responses rather than always parsing JSON.[^spec]

## Schema graph and JSON Schema patterns

Every `$ref` in the inspected document was local and targeted `#/components/schemas/...`; there were 932 occurrences and 205 unique targets. All targets resolved, and every component schema was referenced somewhere. This is a healthy closed graph, but traversal still needs cycle protection and JSON Pointer decoding rather than textual substitution.[^spec]

The graph uses more than plain objects:

- Top-level component schemas include `allOf`, `anyOf`, and `oneOf`; these constructs also appear nested inside properties and array items.
- OpenAPI 3.1 type arrays such as `["string", "null"]` and `["object", "null"]` are common. Required presence and nullability therefore need separate treatment.
- Both closed objects (`additionalProperties: false`) and open/dynamic objects (`additionalProperties: {}` or a value schema) occur.
- Enums, formats, defaults, numeric/string/array constraints, examples, and descriptions can occur at nested levels.
- Two valid component names contain spaces: `Required when using PKCE` and `Required when using authorization_code grant type`; `TokenRequest` references them. Schema lookup must use exact JSON Pointer targets rather than an identifier-name regular expression.
- Create, update, upsert, list-item, and response schemas are separate in many resource families. Eleven explicit upsert operations exist, and some upsert schemas use composition. A skill must not substitute a read schema for a write schema based on a shared prefix.

Custom entities are the clearest dynamic-schema case. A definition's `attributes` describe customer-defined fields, while record create/update bodies carry a `data` object with arbitrary keys and specify that keys are attribute IDs. Correct guidance may therefore require traversing both the operation's static record schema and the custom-entity definition model; the skill cannot manufacture concrete record fields from the static schema alone.[^spec]

## Representative domains for the golden set

The evaluation suite should sample behaviors, not simply tags. This matrix provides a minimum useful portfolio grounded in the current document:[^spec]

| Evaluation family | Representative public operation or schema | Behavior under test |
| --- | --- | --- |
| Operation discovery | `PUT /recruitment/applications/{id_token}` | Find an operation without `operationId`; preserve inline request and response schemas. |
| Tag resilience | `GET /core/ai-chat-defaults` | Find an operation whose tag is absent from top-level tag declarations. |
| Candidate navigation | `GET /core/candidates` | JSON-string filters/search, CSV sort/select, constrained pagination, bare-array response, response header. |
| Cross-domain contrast | `GET /core/jobs` | Different filter details, limit constraint, and `{data,total}` response despite a similar list job. |
| Standard writes | candidate/job/client create, update, and upsert families | Select the operation-specific write schema, required fields, status, and response schema. |
| OAuth client flow | `POST /oauth/token` plus `TokenRequest` | Choose JSON or form encoding and distinguish client credentials from standard authorization-code exchange. |
| Delegated flow | `/oauth/authorize`, `/oauth/session`, `/oauth/session/refresh`, `/session` | Trace a multi-operation flow and use exact request/response models without handling real credentials. |
| Security ambiguity | a normal protected operation | Report its `Bearer` scope requirement alongside the unresolved scheme-name mismatch. |
| Security alternatives | `GET /core/ai-chat-defaults` | Preserve separate security requirement objects. |
| Multiple scopes | `POST /core/options/records` | Preserve multiple scopes in one requirement and inspect prose about model filtering. |
| Dynamic authorization and records | custom-entity definition and record operations | Surface description-defined dynamic scopes and arbitrary attribute-ID keyed data. |
| Schema composition | `NoteBatchCreateRequest`, `NoteBatchCreatedBy`, and an upsert schema | Resolve nested `oneOf`/`allOf`, retain branch constraints, and avoid flattening away meaning. |
| Async result | installed-app action execution or notes batches | Handle `202`, alternate success shapes, and polling-related models only where documented. |
| Errors | ordinary CRUD plus candidate document deletion | Use `ErrorResponse` normally and the documented special error body where applicable. |
| Bodyless/header response | a `204` delete and a settings endpoint with `304` | Avoid unconditional JSON parsing; preserve response headers. |
| Negative capability | a user request with no matching operation | Search all relevant fields, then state that the capability is not present instead of inventing an endpoint. |
| Terminology collision | the `Skills` API tag | Distinguish Quake tenant-managed skill catalog operations from this repository's agent skills. |

Each case should have direct, indirect, and incomplete phrasings where useful. Assertions should validate operation selection and every emitted API fact—method, path, parameters, media type, scope strings, schema fields, response statuses, and uncertainty statements—against a fresh live fetch. A pinned fixture can make regression tests deterministic, but drift checks should re-run the same selectors against the live source.[^spec]

## Required CLI capabilities

A small standard-library Python CLI is sufficient if it exposes stable, composable queries rather than hard-coded domain knowledge:

- `summary`: report document identity, server, and dated counts.
- `find-operations`: rank exact `operationId`, method/path, tag, summary, and description matches; support filters without requiring any one field.
- `show-operation`: return the complete operation together with path/method context and diagnostics for missing IDs, undeclared tags, and security-scheme references.
- `show-schema`: look up exact component names, including spaces, and optionally resolve a bounded graph while retaining original `$ref` locations.
- `trace-refs`: emit reachable schema nodes with cycle detection and report unresolved or non-local references.
- `security`: show defined flows/scopes separately from the selected operation's raw security requirement and description-derived requirement text.
- `validate`: detect missing/duplicate operation IDs, undeclared/unused tags, unresolved references, undefined security schemes, and operation scopes absent from enumerated OAuth scopes.

Outputs should be JSON by default so other agents can reason over exact structure, with a concise human-readable mode for exploration. Fetch failures, invalid JSON, unsupported OpenAPI versions, absent fields, and validation findings should be explicit results. The tool must not silently “fix” the live document, apply generic pagination, infer body requiredness, or flatten schemas in a way that loses composition or nullability.

## Consequences for the three skill contracts

`quake-openapi-navigate` should own discovery, ranking, exact operation inspection, schema traversal, and negative-capability handling. Its success condition is a cited operation and schema chain or a transparent no-match result—not merely a plausible endpoint name.

`quake-openapi-auth` should own flow selection, documented authorize/token/session inputs, and exact operation-scope reporting. It must distinguish defined schemes from operation requirement keys and make the current mismatch or dynamic-scope ambiguity visible. It should use placeholders only and should not obtain, retain, or exercise credentials.

`quake-openapi-request` should consume a selected operation rather than rediscovering one from memory. It should generate protocol-first examples with exact parameter encodings, a request schema appropriate to that operation, and response handling that respects all documented statuses, envelopes, headers, and bodyless cases. It should name any ambiguity instead of resolving it by convention.

Together these contracts cover the public document as it exists without baking in a brittle snapshot. The dated counts are useful for drift detection; the durable design is the set of graph operations, diagnostics, and behavior families above.

[^spec]: Quake, [live public OpenAPI document](https://api.quake.dev/openapi.json), retrieved 2026-08-05.
