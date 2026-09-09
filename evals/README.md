# LLM evaluation baseline

This directory contains lightweight, manually triggered evaluations for the
LLM layer. These checks are intentionally separate from `unittest discover`
because they call the OpenAI API and may depend on model version, prompt
wording, credentials and network access.

## Scope

The baseline evaluates intent extraction and final-answer grounding. It does
not train the model.

## Intent contract

Each case expects the model to call `get_recommendations` with:

- `diet`: `none`, `vegan`, `vegetarian`, `pescetarian`
- `protein_preference`: `none`, `meat`, `fish`
- `restrictions`: zero or more supported restrictions; currently `gluten_free`
- `nutrition_goal`: `standard`, `low_kcal`, `high_protein`, `keto`
- `category`: `śniadanie`, `lunch`, `obiad`, `kolacja`, `deser`, `przekąska`
- `time_max`: integer minutes or `null`
- `top_n`: integer, usually `3`

Diet wording convention:

- plain "bez mięsa" maps to `diet=vegetarian`
- "bez mięsa, ale ryby mogą być" maps to `diet=pescetarian`
- explicit fish requests, such as "z rybą" or "rybny", map to `protein_preference=fish`
- explicit meat requests map to `protein_preference=meat`
- no dietary wording maps to `diet=none` and `protein_preference=none`

Restriction wording convention:

- "bez glutenu", "bezglutenowy" and an explicit gluten intolerance map to `["gluten_free"]`
- negated wording such as "nie musi być bezglutenowe" maps to `[]`
- `gluten_free` may be combined independently with diet, protein preference and nutrition goal

Category and time conventions:

- explicit "lunch" maps to `lunch`, not `obiad`
- explicit "obiad" maps to `obiad`, not `lunch`
- "lekki", "fit", "na redukcji" and "mało kalorii" map to `low_kcal`
  without implying any `time_max`
- "szybki", "na szybko", "ekspresowy" or an explicit minute limit may set
  `time_max`

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

## Latest baseline

Run on 2026-09-08 with `gpt-4o-mini` after adding ten `gluten_free` cases:

- exact match: `46/50` (`92%`)
- `diet`: `50/50` (`100%`)
- `protein_preference`: `47/50` (`94%`)
- `restrictions`: `50/50` (`100%`)
- `nutrition_goal`: `49/50` (`98%`)
- `category`: `50/50` (`100%`)
- `time_max`: `50/50` (`100%`)
- `top_n`: `50/50` (`100%`)

All ten new restriction cases passed, including combinations and negated
wording. The four remaining failures are older cases: high-protein wording is
sometimes mapped to meat, pescetarian wording is sometimes mapped to a fish
requirement, and one light-meal request missed `low_kcal`. These labels remain
unchanged so the report stays an honest baseline.

## Final-answer evaluation

`final_answer_cases.json` contains controlled payloads returned by
`get_recommendations`. `run_final_answer_eval.py` supplies a payload to the
second LLM call and checks that the final response preserves recipe titles,
time, kcal, B, T and W per serving, servings when stated, and promoted SKUs
for the matching recipe. It rejects unknown recipe headings, selected
unsupported claims, ingredient or preparation sections missing from the
payload, and the no-results path when it contains a recipe.

The current baseline has 12 controlled cases, including non-empty and empty
ingredients, multiple recipes and SKU, dietary restrictions, and no-results
responses. A single run is a point-in-time measurement; repeat it after any
prompt or model change.

```powershell
venv\Scripts\python.exe evals\run_final_answer_eval.py --dry-run
venv\Scripts\python.exe evals\run_final_answer_eval.py
```

The detailed report is written locally to `evals/final_answer_eval_report.json`
and is ignored by Git. Polish readability still requires a short human review;
the script reports only a basic heuristic for that criterion.
