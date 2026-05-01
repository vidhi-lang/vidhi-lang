# vidhi-lang

An open vocabulary for Indian privacy and sector-regulator compliance.

vidhi-lang gives compliance teams, software vendors, and regulators a
shared, machine-readable language for describing data processing
activities, regulatory obligations, and the conflicts between them.

It is built for India's regulatory landscape — DPDP Act 2023, IRDAI
regulations, RBI directives, and the standards that follow — where
multiple regulators impose overlapping and sometimes contradictory
requirements on the same data.

Where fideslang describes data under GDPR, vidhi-lang describes data
under Indian law

## Quick example

```python
from vidhi_lang import Vocabulary, Evaluator

# Load the standard vocabulary
vocab = Vocabulary.load_default()

# Describe your processing activity in vidhi-lang terms
manifest = {
    "activity": "act_health_records",
    "source_tables": ["patient_records"],
    "data_subjects": ["health_policyholders"],
    "legal_basis": "consent_and_contract"
}

# Check it against IRDAI + DPDP rules
result = Evaluator(vocab).evaluate(manifest)

print(result.conflicts)
# [Conflict(
#   irdai="IRDAI Health Reg 14: retain 7 years",
#   dpdp="DPDP S.12: right to erasure",
#   resolution="Compliance hold under legal obligation carveout"
# )]
```

That's the project's value in twelve lines: vocabulary in, conflicts out, with citations.
