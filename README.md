# KG-RAG Simulation Assessment

## Overview
This project tests whether grounding LLM plausibility assessments with structured
knowledge from Wikidata makes them more reliable than ungrounded assessment.

It extends Ibrahim et al. (2026), whose LLM-based plausibility assessment of a
multi-agent plagiarism simulation was conducted without structured knowledge grounding.

## Research Question
Can knowledge graph-grounded LLM querying produce more consistent and accurate
plausibility assessments of multi-agent simulations than direct ungrounded LLM querying?

## Systems
- **System A (baseline):** simulation description → LLM → assessment. No external knowledge.
- **System B (grounded):** Wikidata facts retrieved via SPARQL + simulation description → LLM → assessment.

Both systems use the same models, instructions, and settings. The only difference is
the Wikidata knowledge block.

## Wikidata Facts (manually verified entity IDs)
| Concept | Entity |
|---|---|
| Plagiarism | Q164666 |
| Academic integrity | Q4671278 |
| Reinforcement learning | Q830687 |
| Q-learning | Q2664563 |
| Agent-based model | Q392811 |

## Results

### Pilot (August 2026) — confounded
An early pilot suggested consistency rose from 40% to 70% with grounding. However,
System A used an 8B model and System B a 70B model, so the difference cannot be
attributed to grounding. Pilot files are kept for transparency.

### Controlled experiment (October 2026)
Six models, 10 runs each per system, temperature 0.6, identical prompts.

| Model | A consistency | B consistency | A verdict | B verdict |
|---|---|---|---|---|
| allam-2-7b | 80% | 56% | YES | PARTLY |
| gpt-oss-20b | 100% | 100% | PARTLY | PARTLY |
| nemotron-3.5-lightning-30b | 100% | 100% | PARTLY | PARTLY |
| gpt-oss-120b | 100% | 100% | PARTLY | PARTLY |
| qwen3.8-27b | 100% | 100% | PARTLY | PARTLY |
| nemotron-3-nano-30b-reasoning | 89% | 70% | NO | NO |

Consistency is computed over runs with a readable verdict; valid counts are in
`comparison_results_experiment_20261020_02.txt`.

### Findings
- Larger models gave identical verdicts with and without grounding.
- The two weakest models became **less** consistent with grounding.
- Grounding shifted allam-2-7b's verdict from YES to PARTLY, matching larger models.
- Weak models occasionally reported "gaps" contradicted by the description
  (about 2–3 of 168 flagged sentences, roughly equal in A and B).

Short definitional knowledge did not improve consistency. Consistency also does not
measure correctness.

## Next Steps
- Test richer domain knowledge instead of one-line definitions
- Measure factual accuracy of identified gaps more systematically
- Use structured knowledge as a post-hoc check on LLM claims

## Running
```bash
export EXPERIMENT_ID=experiment_YYYYMMDD_NN
python System_A/system_a.py
python System_B/system_b.py
python compare.py
```
API keys go in a `.env` file in the project root (excluded from git).

## References
- Ibrahim et al. (2026) — base simulation and LLM assessment
- Lewis et al. (2020) — retrieval-augmented generation
- Pan et al. (2023) — LLMs and knowledge graphs
- Kato, Hattori, Yoshizoe (2025) — LLM-based agents in MAS
- Fukuta (2015, 2016) — ontology mapping and Linked Open Data