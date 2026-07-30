# LLM evaluation baseline

This directory contains lightweight, manually triggered evaluations for the
LLM layer. These checks are intentionally separate from `unittest discover`
because they call the OpenAI API and may depend on model version, prompt
wording, credentials and network access.

## Scope

The baseline currently evaluates intent extraction: whether the model chooses
the correct arguments for the `get_recommendations` tool.

The eval does not train the model and does not evaluate final answer quality
yet. Final response guardrails should be added after the business contract is
more stable.

## Intent contract

Each case expects the model to call `get_recommendations` with:

- `user_pref`: `none`, `vegan`, `vegetarian`, `meat`, `fish`, `pescetarian`
- `nutrition_goal`: `standard`, `low_kcal`, `high_protein`, `keto`
- `category`: `śniadanie`, `lunch`, `obiad`, `kolacja`, `deser`, `przekąska`
- `time_max`: integer minutes or `null`
- `top_n`: integer, usually `3`

The runner canonicalizes the legacy alias `vege` to `vegetarian` before
scoring, because both are currently accepted by the production code.

## Usage

Validate the case file without calling the API:

```powershell
venv\Scripts\python.exe evals\run_llm_eval.py --dry-run
```

Run the baseline eval:

```powershell
venv\Scripts\python.exe evals\run_llm_eval.py
```

Optionally limit the number of cases during prompt iteration:

```powershell
venv\Scripts\python.exe evals\run_llm_eval.py --limit 10
```

The script prints a concise console summary and writes a detailed JSON report
to `evals/llm_eval_report.json`.
