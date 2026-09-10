# Navigation guide

Use this guide after loading a single current OpenAPI snapshot for the task.

## Search strategy

Search in widening passes:

1. Exact operation ID or schema name when the developer supplied one.
2. Resource plus verb, such as `candidate update` or `installed app actions`.
3. Resource alone, then inspect tags and summaries among the strongest matches.
4. A related public term from a matching operation's description or referenced schema.

Lexical ranking is a shortlist, not proof. Select an operation only after `show operation` confirms its method, path, parameters, request body, responses, and security.

## Complete URLs

OpenAPI server precedence is operation, then path item, then document. The helper returns both `servers` and `servers_source` for the selected operation. Use the applicable server URL plus the documented path; preserve server variables and present alternatives when the specification defines them. If no server is documented, say that the complete base URL is not documented rather than deriving one from the specification URL.

## Schema traversal

- Follow request-body and response `$ref` links into `components.schemas`.
- Inspect array `items`, object `properties`, `additionalProperties`, and `allOf`/`anyOf`/`oneOf` branches.
- Determine requiredness from the containing object's `required` array, not from whether a property has a type.
- Determine nullability from a type that includes `null`, an explicit null composition branch, or a legacy `nullable: true`. Optional and nullable are different.
- Preserve conditional requiredness expressed through `oneOf` or `anyOf`; do not flatten it into “optional.” Requirements contributed by `allOf` remain required.
- Preserve enum members, formats, numeric and string bounds, patterns, defaults, examples, and array-item schemas exactly as written.
- A schema name or property name does not define business meaning. If no description supplies meaning, say it is undocumented.

## Helper result

Every helper command returns:

```json
{
  "ok": true,
  "source": {},
  "result": {},
  "diagnostics": []
}
```

`source.sha256` identifies the exact specification bytes used. A URL source includes `retrieved_at`; a file source includes `loaded_at`.

Important diagnostics include:

- `NO_SPEC_MATCH`: broaden the search; do not invent a capability.
- `OPERATION_NOT_UNIQUE`: use an exact operation ID or method and path.
- `REF_UNRESOLVED`: report the broken definition and stop relying on that shape.
- `REF_CYCLE`: inspect the recursive edge intentionally; a cycle is not automatically invalid.
- `SECURITY_SCHEME_UNDEFINED`: report the operation's reference and the missing component scheme without mapping it by assumption.
- `CLAIM_NOT_DOCUMENTED` or `CLAIM_MISMATCH`: correct or remove the unsupported claim.

Use `verify operation` for operation identity, method, path, scopes, and response statuses. Use `verify value` for exact facts elsewhere in the OpenAPI or a saved dynamic action response. `--pointer` uses local JSON Pointer syntax, `--equals` compares an exact JSON value, and repeatable `--contains` checks membership in an array, object, or string. Encode claim values as JSON.

Exit codes are `0` for success, `2` for command usage, `3` for specification/input/output failure, `4` for no unique match, `5` for reference or action-shape failure, and `6` for a failed claim.

## Bounded uncertainty

When the public specification does not settle the question:

1. State exactly what was inspected.
2. State what is documented.
3. Name the missing or conflicting detail.
4. Avoid a fabricated answer or undocumented workaround.
5. Suggest the closest safe next step, such as obtaining an identifier from a documented list operation or asking Quake support to clarify the public contract.
