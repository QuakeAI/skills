# Quake OpenAPI Skills

This context defines the customer-facing language used to design skills that help coding agents work from Quake's public OpenAPI specification.

## Language

**External developer**:
A Quake customer or customer-authorized developer using the public Quake API without access to Quake-internal systems or knowledge.
_Avoid_: Internal user, Quake operator

**Public API surface**:
The operations, authentication requirements, parameters, schemas, and responses present in the live public Quake OpenAPI document.
_Avoid_: Backend behavior, internal API

**Customer journey**:
An external developer's end-to-end goal for discovering and implementing an integration through the public API surface.
_Avoid_: Endpoint category, API tag

**Installed app**:
An application installation returned for the current dataset by the public Quake API, through which available app actions can be discovered.
_Avoid_: Published app, app catalog entry

**App action**:
A callable capability exposed by an installed app with documented input and output schemas.
_Avoid_: Generic API endpoint

**Installed-app action journey**:
The customer journey that discovers an installed app and action, interprets its schema, constructs an execution request, and handles its synchronous or asynchronous result.
_Avoid_: Connected-app gateway, generic request

**Live discovery**:
An explicitly requested mode that reads installed apps, app actions, action details, or run status using credentials already configured in the developer's environment.
_Avoid_: Action execution, credential setup

**Verified API claim**:
A statement about the Quake API that can be traced directly to the current public OpenAPI document.
_Avoid_: Assumption, remembered behavior

**Bounded uncertainty**:
An explicit statement that the public OpenAPI document does not establish the requested behavior, field, constraint, or guarantee.
_Avoid_: Best guess, invented default

**Golden prompt**:
A version-controlled customer request with an expected activation and outcome, used repeatedly to evaluate a skill's behavior.
_Avoid_: Demo prompt, ad hoc example

**Supported environment**:
An exact agent host, runtime, and installation path listed in a release's compatibility matrix and exercised by its release evaluations.
_Avoid_: Should work, universally compatible

**Community-tested environment**:
An environment reported working by a contributor but not included in Quake's release gate.
_Avoid_: Supported environment

**Repository support request**:
A public, non-sensitive report about skill installation, activation, guidance, examples, packaging, or compatibility, filed as a GitHub Issue.
_Avoid_: Account support, security report

**Product support request**:
A question about a Quake account, credentials, billing, live API availability, or production behavior, sent through <https://quake.dev/contact>.
_Avoid_: Repository support request

**Stable channel**:
The newest published plugin release offered for routine customer installation and upgrades.
_Avoid_: Main branch, latest code

**Pinned install**:
A plugin installation fixed to one immutable release version so its contents can be reproduced exactly.
_Avoid_: Stable channel, development install

**Rollback**:
Replacing the installed plugin with a previously published release version. It changes agent guidance only and does not reverse any API request or customer-data change.
_Avoid_: Undo API operation, restore customer data
