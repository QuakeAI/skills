# Contributing

Contributions should reduce the time it takes an external developer and their coding agent to reach a correct Quake API request.

## Before changing a skill

1. Read `AGENTS.md` and preserve its public-content boundary.
2. Fetch the current specification from `https://api.quake.dev/openapi.json`.
3. Verify every path, operation, field, scope, and response mentioned by the change.
4. Keep instructions focused on how an agent finds and verifies an answer.
5. Use placeholders for identifiers and credentials; never add customer data or secrets.

## Verification

```bash
python3 scripts/sync_skill_helpers.py --check
python3 -m unittest discover -s tests -v
python3 evals/run.py --preflight-only
```

Then validate every skill directory with the Agent Skills validator. Track proposed work, decisions, and follow-ups in GitHub Issues for `QuakeAI/skills`.
