# Authentication guide

Always re-check these anchors in the task's current OpenAPI snapshot. They describe the public specification when this skill was authored, not an out-of-band guarantee.

## Select from documented flows

The public security schemes currently distinguish:

- Client credentials: app-scoped, server-to-server access where requests act as the OAuth client rather than a signed-in Quake user.
- Authorization code: Quake login beginning at the scheme's documented authorization URL. The scheme description directs standard authorization-code token exchange to `/oauth/token` and user-delegated session exchange to `/oauth/session`.

Choose only from the flow the developer actually needs. Do not infer a user identity from a client-credentials token or assume a standard authorization-code token is a delegated session.

## Inspect the complete chain

For app-scoped or standard authorization-code tokens, inspect:

- security scheme flow and URLs;
- `oauthToken` and its request/response schemas; and
- the target operation's effective security and scope list.

For a delegated user session, inspect:

- the authorization-code security scheme;
- `oauthSessionExchange`;
- `oauthSessionRefresh` if rotation is required;
- `oauthSession` if session inspection is required; and
- `DelegatedSessionExchangeRequest`, `DelegatedSessionRefreshRequest`, `DelegatedSessionTokenResponse`, and their referenced schemas.

The current delegated-session operation description says granted scopes are filtered by requested scopes, the client's allowed scopes, and the signed-in dataset user's permissions. Present that as documented behavior, not as a general OAuth assumption.

## Required versus conditional inputs

Read the schema `required` array first, then property descriptions and composition branches. For example, the current delegated exchange schema requires `client_id`, `code`, and `redirect_uri`; it describes `client_secret` for confidential clients and `code_verifier` for public or PKCE clients. Verify this again before repeating it.

Never place a real secret or token in a command. If a code template is requested, refer to externally configured environment variables and show values only as placeholders.

## Scope analysis

1. Inspect the target operation's effective security requirement.
2. Preserve alternatives between security requirement objects and conjunctions within a requirement object.
3. Verify each named scope against the operation, not merely against the global security scheme's available scopes.
4. Do not say that a scope grants access beyond what the specification explicitly documents.

The live specification may contain inconsistencies. At authoring time, installed-app operations referenced a scheme named `Bearer` while `components.securitySchemes` defined OAuth2 schemes with different names. The helper reports this as `SECURITY_SCHEME_UNDEFINED`. Preserve the operation's documented scopes, report the unresolved scheme reference, and do not invent a mapping.

## Safe output example

```text
Operation: <operationId> — <METHOD> <path>
Documented security: <scheme reference and scopes>
Flow: <documented OAuth flow and reason>
Endpoints: <authorization/token/session endpoints from the snapshot>
Inputs: <required and conditional placeholders>
Uncertainty: <none, or the exact specification gap>
```
