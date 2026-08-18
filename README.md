# Notebook Knowledge Distillation

**A source-to-skill workflow for converting external knowledge into
validated reusable agent capability.**

`NATIVE AI` · `INTERNAL UTILITY` · `INTERNAL EVALUATION`

> **Native AI question:** How can a collection of external sources
> become a reusable skill without simply copying unverified notes into
> agent memory?

------------------------------------------------------------------------

## Why this exists

Reading sources is not the same as building organizational capability.

``` text
External sources
      ↓
Notebook / source collection
      ↓
density / relevance scan
      ↓
multi-source distillation
      ↓
cross-source validation
      ↓
skill candidate
      ↓
skill-tester
      ↓
reusable organizational skill
```

NotebookLM is the current source workspace. It should not define the
long-term identity of the project.

------------------------------------------------------------------------

## Core mechanisms

-   source-density scan;
-   multi-source validation;
-   iterative distillation;
-   gap detection;
-   test-case generation;
-   skill packaging;
-   internal quality evaluation.

------------------------------------------------------------------------

## Evidence

The repository currently reports a **TopPrism internal skill-tester
score of 8.75/10**.

Label it exactly that way. It is not an industry benchmark.

The stronger evidence to add next is an end-to-end example:

``` text
Source set
   ↓
Distilled skill
   ↓
Test cases
   ↓
Later task where the skill triggers
   ↓
Measured improvement
```

------------------------------------------------------------------------

## Boundaries

-   source agreement can still be collectively wrong;
-   source quality matters more than source count;
-   distillation can remove nuance;
-   skill trigger design can cause false activation;
-   copyrighted / confidential source material must not be republished
    improperly.

Add source-handling and IP guidance.

------------------------------------------------------------------------

## TopPrism metadata

``` yaml
topprism:
  purpose: native-ai
  capability: source-to-skill-distillation
  platform_layer: organizational-intelligence
  maturity: internal-utility
  evidence:
    type: internal-evaluation
  related:
    - skill-tester
    - agent-nurture-framework
```
