# KG-RAG Simulation Assessment

## Research Overview
This project extends Ibrahim et al. (2026) 
by addressing the stated limitation of 
ungrounded LLM plausibility assessment 
in multi-agent simulations.

## Research Question
Can knowledge graph-grounded LLM querying 
produce more consistent and accurate 
plausibility assessments of multi-agent 
simulations than direct ungrounded 
LLM querying?

## Approach

### System A — Baseline (Ungrounded)
Simulation description sent directly 
to LLM without external knowledge.
Replicates original approach from 
Ibrahim et al. (2026).

### System B — Proposed (KG-Grounded)
Before querying LLM:
1. Retrieve structured facts from 
   Wikidata using SPARQL queries
2. Combine structured facts with 
   simulation description
3. Query LLM with grounded context

## Evaluation Measures
- Consistency across 10 runs
- Accuracy against educational research
- Gap identification quality

## Target Supervisor
Professor Naoki Fukuta
Shizuoka University, Japan

## Status
Week 2 — Building and testing both systems

## References
- Ibrahim et al. (2026) — Base simulation
- Lewis et al. (2020) — RAG foundation  
- Pan et al. (2023) — LLM + KG roadmap
- Fukuta (2015, 2016) — Ontology mapping
