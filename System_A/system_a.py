# system_a.py
# System A: Ungrounded LLM Assessment
# Replicates what Ihsan did in his paper
# NO knowledge graph grounding

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Same simulation description as System B
# But NO Wikidata facts added
PROMPT = """
You are evaluating a research simulation.

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

ASSESSMENT REQUEST:
Please evaluate:

A. Overall realism judgment (yes/partly/no + why)

B. Top 3 most important realism gaps in this 
   simulation

C. One minimum recommended revision
"""

def assess_without_grounding(run_number):
    """System A: Direct LLM query with NO grounding"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": PROMPT}
            ]
        )
        assessment = response.choices[0].message.content
        
    except Exception as e:
        assessment = f"Error: {str(e)}"
    
    # Save result
    filename = f"system_a_run{run_number:02d}.txt"
    with open(filename, "w") as f:
        f.write(f"=== SYSTEM A RUN {run_number} ===\n")
        f.write(f"=== NO KNOWLEDGE GROUNDING ===\n\n")
        f.write(f"NO FACTS PROVIDED\n")
        f.write(f"Direct LLM query only\n")
        f.write(f"\n{'='*50}\n\n")
        f.write(assessment)
    
    print(f"Run {run_number} complete. Saved to {filename}")
    return assessment

if __name__ == "__main__":
    print("=== SYSTEM A: Ungrounded Assessment ===\n")
    print("NO knowledge grounding — baseline only\n")
    
    for i in range(1, 11):

        assess_without_grounding(i)
    
    print("\n=== SYSTEM A COMPLETE ===")
    print("Check system_a_run01.txt through run03.txt")