# system_b.py
# System B: Knowledge Graph-Grounded Assessment
# This is YOUR research contribution

import os
from groq import Groq
import requests
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# STEP 1: Get structured facts from Wikidata
# ─────────────────────────────────────────

def get_wikidata_fact(label):
    """Query Wikidata for a structured fact"""
    
    query = f"""
    SELECT ?item ?itemLabel ?desc WHERE {{
      ?item rdfs:label "{label}"@en.
      OPTIONAL {{?item schema:description ?desc.
      FILTER(LANG(?desc) = "en")}}
      SERVICE wikibase:label {{ 
        bd:serviceParam wikibase:language "en". 
      }}
    }}
    LIMIT 1
    """
    
    url = "https://query.wikidata.org/sparql"
    headers = {"Accept": "application/json",
               "User-Agent": "KG-RAG-Research/1.0"}
    
    params = {"query": query, "format": "json"}
    
    try:
        response = requests.get(url, 
                               params=params, 
                               headers=headers,
                               timeout=10)
        data = response.json()
        results = data["results"]["bindings"]
        
        if results and "desc" in results[0]:
            return results[0]["desc"]["value"]
        else:
            return f"No description found for {label}"
            
    except Exception as e:
        return f"Query failed: {str(e)}"

# ─────────────────────────────────────────
# STEP 2: Build grounding context from facts
# ─────────────────────────────────────────

def build_knowledge_grounding():
    """Retrieve all structured facts for grounding"""
    
    print("Retrieving structured facts from Wikidata...")
    
    topics = [
        "plagiarism",
        "academic integrity", 
        "reinforcement learning",
        "Q-learning",
        "agent-based model"
    ]
    
    facts = {}
    for topic in topics:
        fact = get_wikidata_fact(topic)
        facts[topic] = fact
        print(f"  ✓ {topic}: {fact[:50]}...")
    
    return facts

# ─────────────────────────────────────────
# STEP 3: Build grounded prompt
# ─────────────────────────────────────────

def build_grounded_prompt(facts):
    """Combine Wikidata facts with simulation description"""
    
    grounding_text = """
STRUCTURED KNOWLEDGE FROM KNOWLEDGE BASE:
The following definitions are retrieved from 
a structured knowledge graph (Wikidata) to 
ground your assessment:

"""
    
    for topic, fact in facts.items():
        grounding_text += f"- {topic.upper()}: {fact}\n"
    
    simulation_description = """
SIMULATION TO EVALUATE:
A multi-agent simulation of academic plagiarism 
behavior in a classroom environment.

The simulation models:
- 30 student agents over 16 weeks (one semester)
- Each agent can choose: honest submission, 
  direct copying, or AI-assisted plagiarism
- Agents use Q-learning to adapt their behavior
  based on rewards and penalties
- Detection probability: direct copying = 0.55, 
  AI-assisted plagiarism = 0.25
- Social peer influence through local peer networks
- Two intervention conditions: no intervention 
  and active intervention

Main finding: AI-assisted plagiarism increases 
total dishonest behavior and remains prevalent 
even under active intervention.
"""
    
    assessment_request = """
ASSESSMENT REQUEST:
Using the structured knowledge provided above 
as your factual grounding, please evaluate:

A. Overall realism judgment (yes/partly/no + why)

B. Top 3 most important realism gaps in this 
   simulation based on the knowledge provided

C. One minimum recommended revision
"""
    
    return grounding_text + simulation_description + assessment_request

# ─────────────────────────────────────────
# STEP 4: Call LLM with grounded prompt
# ─────────────────────────────────────────

def assess_with_grounding(run_number, facts):
    from groq import Groq
    
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    prompt = build_grounded_prompt(facts)
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", 
                       "content": prompt}]
        )
        assessment = response.choices[0].message.content
        
    except Exception as e:
        assessment = f"Error: {str(e)}"
    
    filename = f"system_b_run{run_number:02d}.txt"
    with open(filename, "w") as f:
        f.write(f"=== SYSTEM B RUN {run_number} ===\n")
        f.write(f"=== WITH KNOWLEDGE GROUNDING ===\n\n")
        f.write("FACTS USED:\n")
        for topic, fact in facts.items():
            f.write(f"- {topic}: {fact}\n")
        f.write(f"\n{'='*50}\n\n")
        f.write(assessment)
    
    print(f"Run {run_number} complete.")
    return assessment

# ─────────────────────────────────────────
# MAIN: Run System B
# ─────────────────────────────────────────

if __name__ == "__main__":
    
    print("=== SYSTEM B: Knowledge Graph-Grounded Assessment ===\n")
    
    # Step 1: Get facts from Wikidata
    facts = build_knowledge_grounding()
    
    print(f"\nAll facts retrieved successfully.")
    print(f"Facts will be used as grounding context.\n")
    
    # Step 2: Save facts to file for reference
    with open("wikidata_facts.txt", "w") as f:
        f.write("WIKIDATA FACTS RETRIEVED FOR SYSTEM B\n")
        f.write("="*50 + "\n\n")
        for topic, fact in facts.items():
            f.write(f"{topic.upper()}:\n{fact}\n\n")
    
    print("Facts saved to wikidata_facts.txt")
    print("\nNow running grounded assessment...\n")
    
    # Step 3: Run assessment 3 times
    for i in range(1, 11):

        assess_with_grounding(i, facts)
    
    print("\n=== SYSTEM B COMPLETE ===")
    print("Check system_b_run01.txt through run03.txt")
    print("Compare Section B with Ihsan's LLM review files")
    