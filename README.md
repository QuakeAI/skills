# Quake OpenAPI skills

Customer-facing AI-agent skills for building against the public [Quake OpenAPI](https://api.quake.dev/openapi.json). They help a coding agent find the right API operation, understand documented authentication, and use Quake as a gateway to actions provided by a developer's installed apps.

## Included skills

- `quake-openapi-navigate` finds and explains public operations, parameters, request bodies, responses, schemas, and `$ref` chains.
- `quake-openapi-auth` explains documented OAuth flows, delegated sessions, token exchange, operation security, and scopes without handling credentials.
- `quake-installed-app-actions` discovers installed apps and actions, explains their dynamic schemas, and generates sync or async request templates without executing them.

The skills use the live public OpenAPI as their source of truth. They do not contain Quake-internal operations or require access to Quake's source code.

## Install the current pre-release

Until the first customer release publishes a `stable` branch, install the current repository version from `main`:

```bash
codex plugin marketplace add QuakeAI/skills --ref main
codex plugin add quake-openapi@quake
codex plugin list --json
```

Confirm that `quake-openapi@quake` reports version `0.1.0`, then restart Codex so it discovers the skills.

After the first customer release, new customer installations should use `--ref stable`. Release documentation will announce when that branch exists; do not use it before then.

Example prompts:

```text
Use $quake-openapi-navigate to find the operation and schemas for listing candidates.
Use $quake-openapi-auth to explain the scopes required by this Quake operation.
Use $quake-installed-app-actions to find a connected app action and build a TypeScript request for it.
```

## Develop and verify

The canonical dependency-free helper is `tooling/quake_openapi.py`. Each skill bundles the same file so it remains portable. After editing the helper, synchronize and test it:

```bash
python3 scripts/sync_skill_helpers.py
python3 scripts/sync_skill_helpers.py --check
python3 -m unittest discover -s tests -v
python3 evals/run.py --preflight-only
```

Validate each `SKILL.md` with the Agent Skills validator before release. All API claims, fixtures, and examples must remain public, customer-safe, and grounded in the current specification.

See [AGENTS.md](AGENTS.md) for the repository quality and public-content rules.

## Upgrade or roll back

Refresh the stable marketplace and reinstall the plugin:

```bash
codex plugin marketplace upgrade quake
codex plugin remove quake-openapi@quake
codex plugin add quake-openapi@quake
codex plugin list --json
```

To roll back, replace `<RELEASE_TAG>` with a previously published tag:

```bash
codex plugin remove quake-openapi@quake
codex plugin marketplace remove quake
codex plugin marketplace add QuakeAI/skills --ref <RELEASE_TAG>
codex plugin add quake-openapi@quake
codex plugin list --json
```

Restart Codex after an upgrade or rollback.

## Support

- For a skill, helper, installation, or repository documentation defect, open a [GitHub issue](https://github.com/QuakeAI/skills/issues). Include the skill name, sanitized prompt, observed result, expected result, and OpenAPI snapshot hash. Never include credentials or customer data.
- For Quake API runtime behavior, account access, OAuth-client configuration, or an installed app that should be available to your dataset, use [Quake's public contact channel](https://quake.dev/contact). Do not post account-specific details in a public issue.
