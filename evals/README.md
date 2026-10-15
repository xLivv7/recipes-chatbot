# Evaluation: Current Architecture and Historical Baselines

## Post-Measurement Prompt Correction (2026-10-15)

The current prompt now contains five complete JSON argument examples instead
of partial argument fragments. All include protein_preference and every other
required field; no-time examples omit only optional time_max. The schema and
runtime validation were not relaxed and no missing fields are silently repaired.
211 tests pass, including five new prompt-completeness checks. A dry-run loads
76 regression cases. No live measurement of this corrected prompt has been made.
The reports below describe the earlier frozen prompt, not this new version;
keep them unchanged and use new output paths for future measurements.

## Repeats and Holdout v1 (Measured 2026-10-15)

`run_routing_eval.py` now supports `--repeats 3` and `--holdout` (only the
frozen 24-case dataset, without development cases). Reports contain attempts,
per-case persistent/intermittent failures, stable-case counts and checkpoints.
Partial checkpoints have complete=false; completed reports have complete=true.
Default holdout reports use separate ignored filenames. Each run overwrites
its output path; preserve attempts using `--output` under dokumentacja pracy.

```powershell
venv\Scripts\python.exe evals\run_routing_eval.py --mode raw --repeats 3 --dry-run
venv\Scripts\python.exe evals\run_routing_eval.py --mode application --holdout --repeats 3 --dry-run
```

The live campaign is complete. Clean full holdout reruns: raw 51/72 (17/24
stable), application 59/72 (19/24 stable). Earlier runs had substantial API
connection failures and remain documented, not discarded. No prompt or labels
were changed during measurement. Holdout v1 is now exposed; future tuning
requires a new v2 for independent testing. See `docs/holdout_v1_protocol.md`
and `docs/evaluation_results_2026-10-15.md` for all runs, caveats and findings.

## Recommended Separated Evaluation (2026-10-15)

Use `run_routing_eval.py` for new measurements. It separates raw model quality
from actual application guards/validation/dispatch, with a stub at the recipe
tool boundary. It does not evaluate SQL results or send database payloads.
The earlier `run_llm_eval.py` remains compatible, but its coarse metrics and
historical `application_intent_routing` label do not measure the preflight.

```powershell
venv\Scripts\python.exe evals\run_routing_eval.py --mode raw --dry-run
venv\Scripts\python.exe evals\run_routing_eval.py --mode application --dry-run
```

Both modes load 76 cases. Dry-runs plan 76 raw vs 66 application API calls.
Actual live measurements require removing `--dry-run` and are paid separately.
Reports default to `raw_routing_eval_report.json` and
`application_routing_eval_report.json` (ignored, each overwritten per run).
Use `--output` to keep separate attempts. No live run was made in this stage.

Diagnostics preserve raw calls/counts and distinguish API, protocol, argument,
decision, semantic and preflight errors. Guarded cases are not counted as
model successes. Conditional field metrics exclude unassessable cases while
overall pass counts retain all failures. Two deliberate false-positive cases
remain failures, rather than changing their expected labels to match guards.
See `docs/separated_routing_evaluation.md` for denominators, costs and limits.

## Current Architecture (2026-10-06)

Update 2026-10-15 (time/goal stage): prompt and parameter descriptions now
explicitly cover szybki/szybka/szybkie, na szybko and lekki/lekka/lekkie.
Speed without a number means 30 minutes; an explicit limit takes precedence.
Low-calorie wording alone never supplies a time limit; negated speed does not
supply one either. Runtime arguments are not repaired or defaulted to 30.

`time_goal_cases.json` contains 16 development/regression cases: unchanged
intent_008/015/025 plus 13 variants and contrasts (including no-time, negations
and explicit 15/45-minute limits). This is not a holdout. The baseline 64-case
file remains unchanged. Run a targeted dry-run with:

```powershell
venv\Scripts\python.exe evals\run_llm_eval.py --cases evals\time_goal_cases.json --dry-run
```

This loads 22 cases because the six default routing cases are also included.
To measure live later without overwriting the baseline report:

```powershell
venv\Scripts\python.exe evals\run_llm_eval.py --cases evals\time_goal_cases.json --output "dokumentacja pracy\time_goal_live_report.json"
```

Verification: 189 tests OK, baseline dry-run 70, targeted dry-run 22; no new
live LLM measurement. Mocked tests establish argument preservation and absence
of runtime repair, not the model's ability to interpret these utterances.

Update 2026-10-15: application and raw intent eval both send
`parallel_tool_calls=false`, with `tool_choice=auto` unchanged. The prompt and
top_n description explicitly distinguish proposal count from call count:
two proposals mean one call with top_n=2. Reports now record this API setting.
Six new mocked regression tests cover intent_007/intent_059, one backend call,
two rendered results, and rejection of multiple calls. Full suite: 182 tests OK;
dry-run: 70 cases. This is not a new live LLM quality measurement. Old reports
without the flag describe the earlier configuration and remain unchanged.

The application now has a conservative allergy-mention preflight before the
LLM call (see `docs/allergy_request_boundary.md`). `run_llm_eval.py` deliberately
continues to measure the raw model, without this guard. Passing application
guard tests must not be counted as improved LLM routing accuracy. Since
2026-10-15, a separate limited lexical exclusion preflight also runs before
the model; see `docs/unsupported_exclusions_contract.md` for coverage, deliberate
false positives and missed paraphrases. Raw-model evals still bypass both guards.

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
