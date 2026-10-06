# Evaluation: Current Architecture and Historical Baselines

## Current Architecture (2026-10-06)

The application uses one LLM call for intent and tool selection. Backend results
are rendered locally; no final-answer LLM call is made. The shared current prompt
contains intent rules only. Its previous version is frozen in
`legacy_final_answer_prompt.py` exclusively for historical experiments.

`run_llm_eval.py` now uses `tool_choice=auto`, temperature 0.1 and the application's
argument validator. Invalid types are not coerced before scoring. It loads 64
existing intent cases plus 6 `routing_cases.json` cases requiring no tool call
(milk exclusions/allergies, unsupported nut allergy, unrelated question and
conflicting preferences). The report includes action accuracy; field accuracy
excludes no-tool cases, while a missing tool for a recipe request fails.
`expected.time_max=null` is the dataset notation for an omitted tool argument;
actual explicit null is rejected by the tool contract. No old labels were changed.
The report records the system prompt and temperature for reproducibility.

```powershell
venv\Scripts\python.exe evals\run_llm_eval.py --dry-run
venv\Scripts\python.exe evals\run_renderer_eval.py
```

The renderer eval runs offline on six controlled, separate fixtures, with exact
expected outputs or expected rejection: generic recipe, assigned branded SKU,
empty sections, empty results, unassigned SKU and fractional nutrition precision.
It does not repair or reuse incompatible historical final-answer payloads.
Its report `renderer_eval_report.json` is ignored by Git. This measures rendering
contracts, not model quality, Polish readability or semantic correctness of data.

Verification on 2026-10-06: renderer 6/6, intent dry-run 70 cases, unit/integration
suite 155 tests OK. No new live LLM measurement has been performed. Historical
58/64 is not a score for the new prompt, routing policy or stricter validator.
Live intent runs send only test user messages to the API, not database results:

```powershell
venv\Scripts\python.exe evals\run_llm_eval.py
```

`run_final_answer_eval.py` is **historical only** and uses the frozen old prompt.
It still makes paid API calls when run without `--dry-run`; it does not measure
the current application and must not be presented as a production safety score.

Method reference: [official function-calling documentation](https://developers.openai.com/api/docs/guides/function-calling).

## Historical Baseline Notes

This directory contains lightweight, manually triggered evaluations for the
LLM layer. These checks are intentionally separate from `unittest discover`
because they call the OpenAI API and may depend on model version, prompt
wording, credentials and network access.

## Scope

The historical baseline evaluates intent extraction and final-answer grounding. It does
not train the model.

## Intent contract

Each case expects the model to call `get_recommendations` with:

- `diet`: `none`, `vegan`, `vegetarian`, `pescetarian`
- `protein_preference`: `none`, `meat`, `fish`
- `restrictions`: zero or more supported restrictions: `gluten_free`, `lactose_free`
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

For a stability measurement, run:

```powershell
venv\Scripts\python.exe evals\run_final_answer_eval.py --repeats 3
```

The default remains one attempt. Each result includes an `attempt` number.
The summary reports success across all calls, per-attempt results and cases
passing every attempt. Failures are classified as persistent (every attempt
failed) or intermittent (some attempts failed). This classification includes
API errors; inspect individual errors before attributing failures to the model.
Any failed attempt makes the command exit with status 1. Dry run prints the
planned call count; repeat and limit counts must be positive.

The evaluator also rejects extra labelled nutrition values, unknown bullet
items in ingredient sections, and unknown brand-first product mentions.
SKU matching requires adjacent words with explicitly supported Polish
inflections. These checks are lexical: arbitrary paraphrases, claims in
prose, and all possible grammatical forms still need human review. Nutritional
numbers are checked as per-serving claims; total-nutrition presentations are
outside the current response contract.

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

## Lactose integration (2026-10-01)

The intent dataset now has 64 cases (50 existing + 14 new cases). The tool
exposes both restrictions; lactose-free is independent of vegan, protein
preference and nutrition goal. Cases cover explicit intolerance, negation,
both restrictions and unchanged defaults. Intent evaluation uses the same
system prompt as the application, rather than a simplified duplicate.

The final-answer dataset has 16 controlled cases (12 existing + 4 new).
New cases cover requests to invent an unreturned SKU, medical guarantees,
no-result recipe invention, and lactose-free milk versus dairy-free claims.
These fixtures are synthetic, not newly added database recipes. Final-answer
evaluation isolates rendering of supplied tool data, not the whole live
chat workflow. Two manual live smoke checks also exercised unsupported
milk-allergy/dairy-free requests with automatic tool selection.

The grader accepts the explicitly tested Polish forms bialko/bialka (with
Polish diacritics), warzywa/warzyw and mleko/mleka; it still rejects changed
nutrition numbers and unrelated products. Lexical checks cannot prove the
absence of every medical claim or hallucination. Human review remains needed.
temperature=0 is a measurement setting; the application uses 0.1/0.2, so
repeated evals do not establish stability for all production settings.

Methodological reference: [official OpenAI evaluation guidance](https://developers.openai.com/api/docs/guides/evaluation-best-practices).

Final measurement on 2026-10-01 (`gpt-4o-mini`):
- Intent exact match: 58/64 (90.6%); restrictions: 64/64; all 14 new cases pass.
- Final answers: 45/48 (93.8%), stable cases 15/16, 15/16 per attempt.
- Persistent failure: final_013 adds an unreturned vegetable broth SKU on
  explicit user request, in all three attempts. This is a real grounding
  failure, not a grader false positive. Do not treat the feature as proven
  safe against user-driven product invention.
- Intent failures: intent_003, 011, 015, 020, 032, 050. Protein source is
  inferred from high-protein/pescetarian requests; one light request misses
  low_kcal. Expected labels were not changed to match model errors.

Before prompt repair, the final score was 34/48 with the old grader and
41/48 when the same saved responses were rescored with the corrected grader.
Use 41/48 -> 45/48 for a like-for-like comparison of this small tuned dataset,
not 34/48 -> 45/48 as a model-only improvement. A holdout set is still needed.
Both eval commands exit 1 because failures remain; API calls completed.
