# Data curation

## Lactose concept classification

`lactose_concept_policy.csv` explicitly covers C001-C376: 327 allowed,
48 excluded and 1 pending as of 2026-10-01. Empty status means unknown,
never allowed. `lactose_manual_review.md` lists pending concepts for human
review. Update the CSV as the source of truth and keep that review list in sync.

These are concept-level decisions, not manufacturer certifications. Allowed
simple concepts mean pure ingredients without dairy additions. C094 is allowed
because its definition explicitly requires lactose-free milk, not because a
particular SKU was verified. No SKU inherits this status. General dietary
evidence and catalog definitions support the decisions; the source column
does not imply that NIDDK individually certified every item. `reviewed_at`
records the concept review date, not an inspected product-label date.

The owner's manual classification defines the catalog recipes of composite
products; it does not certify arbitrary retail variants. C108 means only
Parmigiano Reggiano DOP and C109 means Grana Padano DOP. Ghee (C104)
remains pending: tolerance or a limit of 0.1 g/100 g is not proof of
compliance with 0.01 g/100 g. SKU still require independent verification.
`apply_data_curation.py --lactose-only` imports both lactose policies.
The backend supports lactose_free filtering; the LLM tool does not expose it yet.
See `docs/lactose_free_contract.md`.

## Lactose SKU classification

`winiary_sku_lactose_policy.csv` covers all 20 existing SKU: 8 allowed,
0 confirmed exclusions and 12 pending. Decisions include evidence URLs,
review date and a manual action for unknowns. See
`lactose_sku_manual_review.md` for the outstanding evidence.
Allowed means composition-based MVP compatibility, not measured lactose
content or manufacturer lactose-free certification. Milk trace warnings and
unmatched package variants remain unknown. Nullable database columns and
policy import and backend filtering are enabled. Product label changes
require renewed review.

The importer rejects duplicate IDs, invalid states and mismatches between
policy IDs and the database catalog before assigning any flags. Empty CSV
states become NULL. Both policies are committed together; reruns overwrite
only lactose flags with the explicit source decisions. Schema migration is
idempotent and commits separately; on a failed import, new columns can remain
present with NULL values. No new records or ingredient substitutions are made.

## Gluten-free policy

`gluten_unsafe_concepts.csv` contains concepts that must not pass the
`gluten_free` restriction. A row may mean that the concept contains a gluten
cereal or that a generic processed concept is not sufficiently verified.

The policy currently covers the manually reviewed catalog range C001-C376.
Concepts in that range that are absent from the unsafe file are assigned
`is_gluten_free=1`. A concept outside the reviewed range makes
`apply_data_curation.py` fail until it is classified deliberately.

`winiary_sku_gluten_policy.csv` materializes the review of the source dataset's
`allergens_pl` and `may_contain_pl` declarations. Wheat or gluten declarations
result in `is_gluten_free=0`. Keeping the reviewed result here avoids a runtime
dependency on the ignored raw-data directory. The runtime may brand a
gluten-free recommendation only with a SKU explicitly marked as allowed.

This MVP flag describes compatibility according to the catalog data. It is not
a medical guarantee, product certification, or assurance against
cross-contamination. Commercial use requires verified manufacturer data and a
defined review process.
