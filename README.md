# vidhi-lang

**v0.1 — Early development.** API and schemas may change before 1.0.

**vidhi-lang** is an open vocabulary for expressing regulatory obligations and data processing in India.

It provides a shared, machine-readable language for describing:

* data categories
* processing activities
* regulatory obligations
* and potential areas of conflict across regulators

vidhi-lang is designed for India's regulatory landscape — including the Digital Personal Data Protection Act, 2023, IRDAI regulations, RBI directives, and others — where multiple authorities impose overlapping requirements on the same data.

Inspired by fideslang, vidhi-lang adapts the concept to India's regulatory environment.

---

## Why vidhi-lang?

Regulations are written in text.
Systems operate on structured data.

This gap leads to:

* inconsistent compliance decisions
* manual interpretation across teams
* difficulty implementing regulation in software systems

vidhi-lang provides a common language to bridge this gap.

---

## What vidhi-lang does

vidhi-lang enables:

* Standardized representation of data processing activities
* Mapping of regulatory obligations to data and systems
* Identification of potential compliance conflicts
* Generation of structured artifacts such as RoPA (Record of Processing Activities)

---

## What vidhi-lang does NOT do

vidhi-lang does **not**:

* provide legal interpretation
* prescribe conflict resolution decisions
* act as a compliance enforcement engine

These responsibilities are left to implementing systems and organizations.

---

## Example (End-to-End)

### 1. Define data categories

```yaml
# taxonomies/data_categories.yaml

- id: health_data
  description: Medical records and health information

- id: kyc_data
  description: Identity data such as PAN, Aadhaar
```

---

### 2. Define regulatory obligations

```yaml
# obligations/irdai.yaml

- id: IRDAI_7_YEARS
  description: Retain health records for 7 years
  applies_to:
    - health_data
```

```yaml
# obligations/dpdp.yaml

- id: DPDP_ERASURE
  description: Data principal has right to erasure
  applies_to:
    - health_data
    - kyc_data
```

---

### 3. Describe a processing activity (manifest)

```yaml
# manifests/sample.yaml

activity: act_health_records
source_tables:
  - patient_records
data_subjects:
  - health_policyholders
legal_basis: consent_and_contract
data_used:
  - health_data
retention_rule: IRDAI_7_YEARS
```

---

### 4. Expected structured output

```json
{
  "activity": "act_health_records",
  "data_subjects": ["health_policyholders"],
  "data_categories": ["health_data"],
  "obligations": [
    "IRDAI: retain health records for 7 years",
    "DPDP: right to erasure"
  ],
  "potential_conflicts": [
    "retention_vs_erasure"
  ]
}
```

---

## Design principle
vidhi-lang separates:
* **What the law says** — open vocabulary (taxonomy, obligations, citations)
* **What to do about it** — implementation-specific decision logic

This ensures vidhi-lang remains a shared standard without embedding legal interpretation.

---

## Repository structure

```text
vidhi-lang/
├── taxonomies/
│   ├── data_categories.yaml
│   └── legal_bases.yaml
├── obligations/
│   ├── dpdp.yaml
│   └── irdai.yaml
├── conflicts/
│   └── retention_vs_erasure.yaml
├── manifests/
│   └── sample.yaml
├── examples/
└── README.md
```

---

## Initial scope (v0.1)

The first version focuses on:
* DPDP Act 2023 vocabulary
* IRDAI insurance-related examples
* core data categories
* processing activities
* obligation mappings
* conflict types (identification only)
* RoPA-ready structured outputs

---

## Getting started

Coming soon.

Initial release will include:

* sample YAML vocabularies
* example manifests
* a basic RoPA generator
* validation examples

---

## Status
Early stage — building v0.1

---

## License

Apache License 2.0
