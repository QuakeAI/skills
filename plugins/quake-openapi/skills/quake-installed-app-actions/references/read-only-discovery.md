# Authenticated read-only discovery

Use this procedure only after the developer explicitly requests live discovery and confirms that their environment already has an authenticated Quake client. If no such client exists, provide setup guidance with placeholders and stop. Do not ask for or inspect a credential value.

## Allowlist

Authenticated network calls are limited to these operations after the current OpenAPI snapshot confirms that each is still a `GET`:

- `listInstalledApps`
- `listInstalledAppActions`
- `getInstalledAppAction`
- `getInstalledAppActionRun`, only when the developer asks about an existing async run

Public catalog discovery may additionally use the unauthenticated `GET` operations `listApps`, `listAppActions`, and `getAppAction`. It cannot establish installation.

`executeInstalledAppAction` is never allowlisted because it is a mutating `POST`.

## Procedure

1. Use the bundled helper to inspect each planned operation against the saved OpenAPI snapshot.
2. Reject the plan unless every network call resolves to one of the allowlisted operation IDs and method `GET`.
3. Use the developer's existing authenticated client or command wrapper by its configured name. Do not read, print, interpolate into logs, or persist the underlying credential. Do not enable verbose HTTP logging or shell tracing.
4. Save raw discovery responses only in a task-local temporary directory outside the repository. Restrict displayed or retained output to the fields needed for selection and schema interpretation; remove customer records and identifiers from any shared diagnostic.
5. Record a sanitized trace containing only timestamp, operation ID, method, templated path, and status. Never record headers, query values, response bodies, or resolved identifiers.
6. Before completion, assert that every trace entry used method `GET`, every operation ID was allowlisted, and no path ended in `/execute`.
7. Delete or leave cleanup instructions for task-local raw responses according to the developer's environment policy. Never commit them.

If the existing client cannot produce a safe trace or prevent non-GET calls, do not perform live discovery. Generate the read-only request templates for the developer instead.
