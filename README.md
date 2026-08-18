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
Sends simulation description directly to LLM.
No external knowledge provided.
Replicates original approach from 
Ibrahim et al. (2026).

### System B — Proposed (KG-Grounded)
Retrieves structured facts from Wikidata 
via SPARQL, combines with simulation 
description, queries LLM with grounded context.

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

## Results (10 runs each system)

| Metric | System A | System B |
|--------|----------|----------|
| Verdict consistency | 40% | 70% |
| Dominant verdict | Scattered | NO (7/10) |
| Explicit "academic integrity" mentions | 0/10 | 4/10 |

### Key Finding
Knowledge graph grounding improved verdict 
consistency by 30 percentage points (40% → 70%) 
across 10 independent runs. 
System B's assessments frequently referenced the specific 
Wikidata facts provided, confirming the LLM 
actively used the structured grounding rather 
than ignoring it.

## Project Structure

                        KG_RAG_PROJECT/
                           ├── System_A/
                           │ ├── system_a.py
                           │ ├── system_a_run01-10.txt
                           ├── System_B/
                           │ ├── system_b.py
                           │ ├── system_b_run01-10.txt
                           ├── compare.py
                           ├── comparison_results.txt
                           ├── wikidata_facts.txt
                           └── README.md

## Methodology
1. Retrieved 5 structured facts from Wikidata 
   via SPARQL (plagiarism, academic integrity, 
   reinforcement learning, Q-learning, 
   agent-based model)
2. Built System A (ungrounded) and System B 
   (grounded with facts above)
3. Ran both systems 10 times each using 
   identical simulation description
4. Compared verdict consistency and gap 
   specificity across runs

## LLM Used
Llama3-8b via Groq API

## Next Steps
- Test with multiple LLM families 
  (as Ibrahim et al. did with 5 models)
- Test with additional simulation descriptions
- Statistical significance testing
- Expand knowledge grounding to more facts

## References
- Ibrahim et al. (2026) — Base simulation paper
- Lewis et al. (2020) — RAG foundation
- Pan et al. (2023) — LLM + KG roadmap
- Fukuta (2015, 2016) — Ontology mapping
