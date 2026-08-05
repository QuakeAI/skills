# Portable skill and OpenAI plugin packaging constraints

Research date: 2026-08-05

## Question

What current requirements and constraints from the Open Agent Skills specification and official OpenAI skill/plugin guidance must the repository blueprint satisfy for portable authoring, local testing, GitHub marketplace distribution, and later public submission?

## Answer

Author the three Quake workflows as self-contained Open Agent Skills, then package them as one OpenAI skills-only plugin. Keep the plugin in a dedicated subdirectory and put the repository marketplace catalog at `.agents/plugins/marketplace.json`. This cleanly separates portable skill content from OpenAI distribution metadata, supports GitHub-backed installation, and lets the plugin directory itself become the one-root ZIP uploaded for later public submission.

The recommended shape is:

```text
.
├── .agents/
│   └── plugins/
│       └── marketplace.json
├── plugins/
│   └── quake-openapi/
│       ├── .codex-plugin/
│       │   └── plugin.json
│       ├── assets/
│       └── skills/
│           ├── quake-openapi-navigate/
│           │   ├── SKILL.md
│           │   ├── agents/openai.yaml
│           │   └── scripts/query_openapi.py
│           ├── quake-openapi-auth/
│           │   ├── SKILL.md
│           │   ├── agents/openai.yaml
│           │   └── scripts/query_openapi.py
│           └── quake-openapi-request/
│               ├── SKILL.md
│               ├── agents/openai.yaml
│               └── scripts/query_openapi.py
├── evals/
├── research/
└── scripts/
```

The `plugins/quake-openapi/` nesting is a recommendation, not a universal plugin rule. OpenAI permits other paths, but its repo-marketplace example uses a repository-level catalog pointing to plugin directories under `./plugins/`; marketplace paths resolve from the marketplace root, not from `.agents/plugins/`. Keeping the plugin isolated also satisfies the public uploader's requirement for exactly one identifiable plugin root when that directory alone is archived. [OpenAI package and marketplace guidance](https://developers.openai.com/plugins/build/plugins#install-a-local-plugin-manually) [OpenAI ZIP root checks](https://developers.openai.com/plugins/deploy/submission-errors#plugin-root-errors)

## Portable skill authoring requirements

Each skill must be a directory containing `SKILL.md`. That file must start with YAML frontmatter and have a non-empty Markdown body. The portable standard requires `name` and `description`; `license`, `compatibility`, `metadata`, and experimental `allowed-tools` are optional. A skill name must be 1–64 characters, use lowercase letters, digits, and hyphens, avoid leading, trailing, or consecutive hyphens, and match its parent directory. The description must be 1–1,024 characters and state both what the skill does and when it applies. [Open Agent Skills specification](https://agentskills.io/specification#skillmd-format)

For maximum portability, keep the portable frontmatter small:

```yaml
---
name: quake-openapi-navigate
description: Find and explain public Quake OpenAPI operations and schemas. Use when a developer needs to discover the correct endpoint, parameters, request body, response, or related schema.
compatibility: Requires Python 3 and outbound HTTPS access to api.quake.dev.
---
```

Use `compatibility` because these skills intentionally depend on Python and live network access. Do not use `allowed-tools` in v1: the standard marks it experimental and says host support may vary. Do not put essential behavior in arbitrary `metadata`; clients may ignore it. [Open Agent Skills frontmatter fields](https://agentskills.io/specification#frontmatter)

`scripts/`, `references/`, and `assets/` are optional conventions. Scripts should be self-contained or document their dependencies, report useful errors, and handle edge cases. Supporting files must be referenced with paths relative to the skill root, and the specification recommends shallow, one-level reference chains. It also recommends a `SKILL.md` body below 5,000 tokens and 500 lines, with resources loaded only when needed. [Open Agent Skills optional directories and progressive disclosure](https://agentskills.io/specification#optional-directories) [Open Agent Skills file references](https://agentskills.io/specification#file-references)

That path model has an important repository consequence: the installed skill must not depend on repository-relative siblings such as `../../../scripts/query_openapi.py`. Each packaged skill should contain every runtime file it needs. Small duplicated Python utilities are acceptable; alternatively, repository tooling may generate identical copies before validation, but the final plugin must contain self-sufficient skill trees. OpenAI likewise instructs authors to place supporting material next to each skill and reference it from `SKILL.md`. [OpenAI skill resource guidance](https://developers.openai.com/plugins/build/skills#add-supporting-resources)

## OpenAI-specific metadata and plugin manifest

OpenAI-specific UI and invocation metadata belongs in optional `agents/openai.yaml`, not in portable `SKILL.md` metadata. If that file is present, OpenAI validation requires an `interface` map with non-empty `display_name` and `short_description`. It may also contain icons, a brand color, a default prompt, invocation policy, and tool dependencies. The plugin submission validator explicitly ignores `SKILL.md` `metadata` for configuring the OpenAI interface. [OpenAI skill metadata guidance](https://learn.chatgpt.com/docs/build-skills#optional-metadata) [OpenAI skill-agent validation rules](https://developers.openai.com/plugins/deploy/submission-errors#skill-agent-metadata-errors)

The plugin requires `.codex-plugin/plugin.json`; `plugin.json` should be the only file inside `.codex-plugin/`. A minimal skills-only manifest has a stable kebab-case `name`, a semantic `version`, a description, and a `skills` path relative to the plugin root and beginning with `./`. Published packages commonly add author, repository, license, keywords, public listing copy, branding, and legal/support links. [OpenAI plugin structure and manifest fields](https://developers.openai.com/plugins/build/plugins#plugin-structure) [OpenAI path rules](https://developers.openai.com/plugins/build/plugins#path-rules)

Recommended initial manifest shape:

```json
{
  "name": "quake-openapi",
  "version": "0.1.0",
  "description": "Help coding agents navigate and use the public Quake OpenAPI",
  "author": {
    "name": "Quake",
    "url": "https://quake.dev"
  },
  "homepage": "https://quake.dev",
  "repository": "https://github.com/QuakeAI/skills",
  "license": "Apache-2.0",
  "skills": "./skills/",
  "interface": {
    "displayName": "Quake OpenAPI",
    "shortDescription": "Build with the Quake API",
    "longDescription": "Discover public Quake API operations and schemas, select documented authentication, and generate adaptable requests grounded in the live OpenAPI document.",
    "developerName": "Quake",
    "category": "Developer Tools",
    "websiteURL": "https://quake.dev"
  }
}
```

Confirm the exact supported category and final field-length limits against the submission portal before release. At the current public-directory boundary, the package name and version are required; the version must be SemVer, display and short-description fields are limited to 30 characters, long description to 4,000 characters, and developer name to 80 characters. The combined OpenAI skill identity, `plugin-name:skill-name`, must not exceed 64 characters, and skill names must be unique within the plugin. [OpenAI final metadata and skill checks](https://developers.openai.com/plugins/deploy/submission-errors#final-directory-submission)

Because v1 is skills-only, its package must not include `mcpServers`, `.mcp.json`, `apps`, `.app.json`, or `interface.screenshots`. Those fields route the package into MCP-backed submission rules; screenshots are allowed only for custom UI. Lifecycle hooks are technically supported by plugins, but v1 should omit them because they are Codex-specific executable behavior, reduce portability, and do not help the agreed read-only guidance workflows. [OpenAI skills-only upload rules](https://developers.openai.com/plugins/deploy/submission-errors#skills-only-zip-upload-errors-and-warnings) [OpenAI plugin structure](https://developers.openai.com/plugins/build/plugins#plugin-structure)

## Validation and local testing

Use three validation layers:

1. Run `skills-ref validate <skill-directory>` for each portable skill. The Agent Skills specification names this validator for frontmatter and naming checks. Its own repository warns that the reference library is demonstrative rather than production-ready, so it should be a compatibility check, not the only CI gate. [Agent Skills validation guidance](https://agentskills.io/specification#validation) [skills-ref repository](https://github.com/agentskills/agentskills/tree/main/skills-ref)
2. Add repository checks for all package constraints known before upload: manifest JSON, SemVer, safe relative paths, unique names, combined identity lengths, existence of declared files, absence of MCP/app/screenshot fields, Python syntax, live OpenAPI reachability, and fixtures/evaluations. OpenAI's submission error reference is the authoritative checklist for these checks; passing local checks does not guarantee portal acceptance because final directory submission applies stricter scans and attestations. [OpenAI submission error reference](https://developers.openai.com/plugins/deploy/submission-errors)
3. Install the complete package from the repo marketplace and test it in a new conversation. Preserve prompts and results across versions. The official evaluation set should include direct, indirect, incomplete/follow-up, negative, and boundary prompts; review both activation and output quality, supporting-resource resolution, and unsupported-action behavior. [OpenAI skill testing guidance](https://developers.openai.com/plugins/build/skills#test-the-skill) [OpenAI complete-plugin testing](https://developers.openai.com/plugins/deploy/connect-chatgpt#test-the-complete-plugin)

The current docs do not identify a public offline command that fully reproduces the submission portal's plugin validation and safety scan. Treat portal upload validation as a required release-candidate step rather than claiming that CI exactly matches it.

## GitHub repo marketplace distribution

Create `.agents/plugins/marketplace.json` at the repository root and point its plugin entry to `./plugins/quake-openapi`. Every entry should include its name, source, install policy, authentication policy, and category. The marketplace source path must start with `./`, remain within the marketplace root, and resolve from that root. [OpenAI marketplace metadata](https://developers.openai.com/plugins/build/plugins#marketplace-metadata)

```json
{
  "name": "quake",
  "interface": {
    "displayName": "Quake"
  },
  "plugins": [
    {
      "name": "quake-openapi",
      "source": {
        "source": "local",
        "path": "./plugins/quake-openapi"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Developer Tools"
    }
  ]
}
```

Customers can add the GitHub repository as a marketplace source with `codex plugin marketplace add QuakeAI/skills` or pin a Git ref with `--ref`. Adding the marketplace makes it discoverable; installation and complete local testing occur through the Plugins Directory in the ChatGPT desktop app. [OpenAI Git-backed marketplace commands](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli)

OpenAI requires the manifest version to be SemVer and requires a changed version for a new published release. Git tags are not an OpenAI manifest requirement, but the repository should adopt a release policy that pairs manifest version `X.Y.Z` with a protected tag `vX.Y.Z`, never moves released tags, and documents both latest and pinned installation commands. This makes `--ref vX.Y.Z` reproducible. For strongest immutability, marketplace sources also accept Git SHA selectors. [OpenAI version validation](https://developers.openai.com/plugins/deploy/submission-errors#plugin-manifest-errors) [OpenAI Git marketplace sources](https://developers.openai.com/plugins/build/plugins#marketplace-metadata)

Keep one package version as the release authority. Do not add per-skill versions in portable `metadata` unless the project later needs independent skill release cycles.

## Later public submission

Archive `plugins/quake-openapi/`, not the whole repository. A skills-only ZIP must contain a supported plugin manifest and at least one real `skills/<skill-name>/SKILL.md`. It must expose exactly one plugin root, either at the ZIP root or inside one top-level directory. Current upload limits include 100 MB compressed, 512 MiB extracted, 5,000 entries, paths no deeper than 20 segments, safe relative `/` paths, and regular files/directories rather than special entries. [OpenAI ZIP and root validation](https://developers.openai.com/plugins/deploy/submission-errors#zip-structure-and-limit-errors)

Before submission, Quake must have a verified developer or business identity and the submitter must have Apps Management write access. Prepare production listing copy and branding, public website/support/privacy/terms links, starter prompts, a final skill bundle, release notes, region availability, and reviewer-ready tests. Skills-only URLs are currently optional in the final error table, but Quake should supply customer-facing support and legal links where the portal permits them. Every bundled skill must pass OpenAI safety and security scanning. [OpenAI submission preparation](https://developers.openai.com/plugins/deploy/submission#prepare-required-materials) [OpenAI final submission checks](https://developers.openai.com/plugins/deploy/submission-errors#final-directory-submission)

The submission guide asks for five positive and three negative reviewer test cases. Maintain that exact reviewer set even for the skills-only release so it is ready if the portal requests it; the stricter error reference explicitly mandates those counts for MCP-backed submissions. Test cases must be runnable without Quake-internal context. [OpenAI submission testing](https://developers.openai.com/plugins/deploy/submission#testing)

Submission starts review; it does not publish immediately. After approval, Quake chooses when to publish, after which the same listing appears in the universal Plugins Directory shared by ChatGPT and Codex. Each subsequent public release needs a new manifest version, an updated final bundle, release notes, another review, and publication of the approved version. [OpenAI public publishing flow](https://developers.openai.com/plugins/deploy/submission#public-publishing-flow)

## Blueprint acceptance checklist

- [ ] Each skill directory name and `SKILL.md` `name` match and satisfy the portable naming rules.
- [ ] Each `SKILL.md` has a precise activation description, an explicit workflow boundary, and only public Quake material.
- [ ] Each skill carries its own required scripts/references/assets and uses only skill-root-relative references.
- [ ] Python/network requirements are stated in `compatibility`; no experimental `allowed-tools` dependency is required.
- [ ] OpenAI-only metadata lives in valid `agents/openai.yaml` files.
- [ ] `.codex-plugin/plugin.json` is the only file under `.codex-plugin/`, uses safe `./` paths, and has a stable name plus SemVer.
- [ ] The skills-only package contains no MCP, app, UI, credential, or internal-operations content; the v1 portability policy also excludes hooks.
- [ ] `.agents/plugins/marketplace.json` resolves `./plugins/quake-openapi` from the repository root.
- [ ] CI performs portable validation, package-structure validation, Python checks, and golden-prompt/OpenAPI checks.
- [ ] A release candidate is installed from the repo marketplace and tested in a new conversation.
- [ ] `vX.Y.Z` release tags match the manifest version and are treated as immutable repository policy.
- [ ] The public-submission ZIP is built from only the plugin directory and passes portal validation and skill scans.
- [ ] Verified Quake publisher identity, public support/legal materials, starter prompts, reviewer tests, and release notes are ready before universal-directory submission.

## Sources

- [Open Agent Skills specification](https://agentskills.io/specification)
- [Agent Skills reference validator](https://github.com/agentskills/agentskills/tree/main/skills-ref)
- [OpenAI: Build skills](https://developers.openai.com/plugins/build/skills)
- [OpenAI: Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [OpenAI: Connect and test your plugin](https://developers.openai.com/plugins/deploy/connect-chatgpt)
- [OpenAI: Submit plugins](https://developers.openai.com/plugins/deploy/submission)
- [OpenAI: Plugin submission errors](https://developers.openai.com/plugins/deploy/submission-errors)
