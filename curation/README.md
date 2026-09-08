# Data curation

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
