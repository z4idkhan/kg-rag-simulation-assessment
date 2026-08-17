# KG-RAG Simulation Assessment

## Overview
This project investigates whether grounding 
LLM plausibility assessments with structured 
knowledge from Wikidata improves consistency 
compared to direct ungrounded LLM querying.

It extends Ibrahim et al. (2026) by addressing 
their explicitly stated limitation: LLM-based 
plausibility assessment was conducted without 
structured knowledge grounding.

## Research Question
Can knowledge graph-grounded LLM querying 
produce more consistent and accurate 
plausibility assessments of multi-agent 
simulations than direct ungrounded 
LLM querying?

## Systems

### System A — Baseline (Ungrounded)
- Sends simulation description directly to LLM
- No external knowledge provided
- Replicates original approach from 
  Ibrahim et al. (2026)
- Code: System_A/system_a.py

### System B — Proposed (KG-Grounded)
- Retrieves structured facts from Wikidata 
  via SPARQL queries
- Combines facts with simulation description
- Sends grounded prompt to LLM
- Code: System_B/system_b.py

## SPARQL Facts Retrieved (Wikidata)
- Plagiarism: using another author's work 
  as if it was one's own original work
- Academic Integrity: moral code or 
  ethical policy of academia
- Reinforcement Learning: type of machine 
  learning where an agent learns how to behave 
  by performing actions and receiving rewards
- Q-Learning: model-free reinforcement 
  learning algorithm
- Agent-Based Model: type of computational models

## Preliminary Results (3 runs each)

| Metric | System A | System B |
|--------|----------|----------|
| Run 1 verdict | Yes | Partly |
| Run 2 verdict | Yes | Partly |
| Run 3 verdict | No | Partly |
| Verdict consistency | LOW | HIGH |
| Gap descriptions | Generic | Fact-grounded |

### Key Finding
System B produced a consistent "partly" 
verdict across all 3 runs.
System A varied between "yes" and "no".
Knowledge grounding stabilizes overall 
realism judgment.

## Project Structure

                        KG_RAG_PROJECT/
                           ├── System_A/
                           │ ├── system_a.py
                           │ ├── system_a_run01.txt
                           │ ├── system_a_run02.txt
                           │ └── system_a_run03.txt
                           ├── System_B/
                           │ ├── system_b.py
                           │ ├── system_b_run01.txt
                           │ ├── system_b_run02.txt
                           │ └── system_b_run03.txt
                           ├── wikidata_facts.txt
                           └── README.md

## Evaluation Measures
- Consistency of verdicts across runs
- Specificity of gap identification
- Alignment with Wikidata structured facts

## Next Steps
- Run both systems 10 times each
- Build full comparison table
- Measure consistency statistically

## References
- Ibrahim et al. (2026) — Base simulation paper
- Lewis et al. (2020) — RAG foundation
- Pan et al. (2023) — LLM + KG roadmap
- Fukuta (2015, 2016) — Ontology mapping
