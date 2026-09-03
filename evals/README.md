# Evaluation cases

“Golden prompts” here are representative customer questions with explicit success and safety criteria. They are not prescribed wording or a single perfect response. Their purpose is to check that an agent can complete the real customer journey reliably as the OpenAPI evolves.

`cases/v0.1.json` covers general navigation, authentication, and the main Quake gateway journey: discover a dataset's installed apps, select an action, understand every dynamic schema field, and build a synchronous or asynchronous request.

The cases contain no credentials and authorize no action execution. Expected operation IDs are verification anchors for the current API; an evaluator should fetch the live specification, detect drift, and update a case only when the public contract intentionally changes.

## Run

Preflight all expectations against one newly fetched specification without starting model runs:

```bash
python3 evals/run.py --preflight-only
```

Run every case three times in a fresh, ephemeral, read-only Codex session:

```bash
python3 evals/run.py
```

Use `--case <id>` for a focused run and `--spec <saved-openapi.json>` to reproduce an exact snapshot. Results are written under ignored `.artifacts/evals/` as `eval-report.json`, JUnit XML, a concise Markdown summary, normalized agent output, and Codex event logs.

Hard gates verify skill activation, expected operation selection, exact method/path/scope/response claims, JSON-Pointer field claims, requested code presence and basic safety/syntax, and a GET-only discovery trace. Every case must pass at least two of three runs; aggregate activation and operation selection must reach 90%. Semantic `must` and `must_not` criteria remain visible for human or advisory-model review and cannot override a failed hard gate.
