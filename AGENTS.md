# AGENTS.md

## Project overview

This repository is owned by Quake and contains AI-agent skills for working with the Quake OpenAPI. The skills should help coding agents discover, understand, and use the public Quake API effectively.

The authoritative OpenAPI document is:

- <https://api.quake.dev/openapi.json>

When API behavior, paths, schemas, parameters, or examples are in question, inspect the current OpenAPI document instead of relying on memory or assumptions.

## Audience

The primary audience is external Quake customers and developers who may be new to the Quake API. Write every skill as public, customer-facing material. Do not assume access to Quake's source code, private systems, internal documentation, employee knowledge, or non-public tooling.

## Goal and success metric

The goal is to make the Quake OpenAPI as seamless as possible for any new developer to use through a coding agent.

A successful skill enables an agent to:

- navigate the OpenAPI document efficiently;
- locate the relevant operation, schema, and supporting definitions for a task;
- distinguish verified API behavior from inference;
- produce correct, practical integration guidance grounded in the current specification;
- explain unfamiliar Quake concepts clearly to an external developer; and
- recover gracefully when an operation or capability is not present in the public specification.

Optimize for developer success, correctness, discoverability, and low time-to-first-working-request.

## Source-of-truth rules

- Treat the live OpenAPI document as the source of truth for the public API surface.
- Verify operation paths, HTTP methods, parameters, request bodies, response shapes, authentication requirements, and schema names against the specification before documenting them.
- Prefer stable discovery techniques, such as searching operation IDs, tags, paths, schema names, and `$ref` links, over instructions tied to a particular line number or document ordering.
- Clearly label any interpretation or inference that is not explicitly defined by the specification.
- Do not invent endpoints, fields, enum values, defaults, limits, guarantees, or error behavior.
- If the specification is ambiguous or incomplete, say so and guide the developer using only the public information available.

## Skill-writing guidelines

- Keep each skill focused on a concrete developer job or a reusable OpenAPI navigation technique.
- Teach agents how to find the answer, not merely a snapshot of the answer. The live specification can evolve.
- Use concise, actionable instructions and customer-relevant examples.
- Include verification steps where they materially reduce integration errors.
- Prefer examples that can be copied and adapted without Quake-internal context.
- Use placeholders for credentials, IDs, tenant-specific values, and other user-provided data.
- Never include real secrets, access tokens, customer data, or personally identifiable information.
- Avoid duplicating large sections of the OpenAPI document. Point agents to the relevant paths and schemas and explain how to traverse them.

## Public-content boundary

This is a customer-facing repository. Do not add anything private to Quake's internal operations, including:

- private architecture or infrastructure details;
- internal service names, repositories, environments, dashboards, or runbooks;
- non-public endpoints, schemas, features, roadmaps, or implementation details;
- internal incidents, operational procedures, security controls, or threat findings;
- employee-only workflows, terminology, credentials, or contact information; or
- confidential customer or partner information.

Only include information that is already public, present in the public OpenAPI document, or explicitly approved for customer-facing publication. If there is doubt about whether information is public, omit it and ask for confirmation.

## Contribution quality bar

Before considering a skill complete:

1. Validate its API claims against <https://api.quake.dev/openapi.json>.
2. Check that a developer without Quake-internal knowledge can follow it.
3. Confirm that examples contain no secrets, private identifiers, or internal-only details.
4. Test commands or code samples when practical.
5. Ensure the skill remains useful if unrelated parts of the OpenAPI document change.
6. Keep terminology consistent with the public specification.

When reviewing changes, prioritize factual accuracy, customer clarity, safe examples, and faithful grounding in the public OpenAPI specification.

## Project planning

- Track project plans and decisions in GitHub Issues for `QuakeAI/skills`; do not use a local Markdown issue tracker.
- Use GitHub sub-issues for Wayfinder decision tickets and GitHub's native blocking relationships for dependencies.
- Keep planning issues customer-safe and within the same public-content boundary as repository files.
