"""
System A: Ungrounded assessment baseline.
System A and System B must share the same assessment instructions and settings.
"""

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
load_dotenv(PROJECT_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_NIM_API_KEY") or os.getenv("NVIDIA_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError(f"GROQ_API_KEY missing from {PROJECT_DIR / '.env'}")
if not NVIDIA_API_KEY:
    raise RuntimeError("NVIDIA_NIM_API_KEY (or NVIDIA_API_KEY) is missing from .env")

groq_client = Groq(api_key=GROQ_API_KEY, timeout=120.0, max_retries=2)
nvidia_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY,
    timeout=120.0,
    max_retries=2,
)

MODELS = [
    {"name": "allam-2-7b", "provider": "groq"},
    {"name": "openai/gpt-oss-20b", "provider": "groq"},
    {"name": "nvidia/nemotron-3.5-lightning-30b-a3b", "provider": "nvidia"},
    {"name": "openai/gpt-oss-120b", "provider": "groq"},
    {"name": "qwen/qwen3.8-27b", "provider": "groq"},
    {"name": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning", "provider": "nvidia"},
]
MAX_OUTPUT_TOKENS = 1000
RUNS_PER_MODEL = 10
TEMPERATURE = 0.6
REQUEST_DELAY_SECONDS = 5
EXPERIMENT_ID = os.getenv("EXPERIMENT_ID", "experiment_20261020_01")
OUTPUT_DIR = BASE_DIR / "results" / EXPERIMENT_ID
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SIMULATION_DESCRIPTION = """
A simulated academic-integrity environment contains 30 student agents over 16 weeks.
Students can choose honest submission, direct copying, or AI-assisted plagiarism.
The model uses Q-learning: agents update behavior based on rewards and penalties.
The detection probability is 0.55 for direct copying and 0.25 for AI-assisted plagiarism.
Students interact through local peer networks. The experiment compares a no-intervention
condition with an active-intervention condition. The main reported finding is that
AI-assisted plagiarism increases total dishonest behavior and remains prevalent under
intervention.
""".strip()

# Keep this exact text synchronized with System B.
ASSESSMENT_INSTRUCTIONS = """
Assess the simulation described below. Use only the information explicitly provided
for claims about what the simulation does. Do not assume a feature is absent merely
because it is not mentioned. Separate evidence-backed concerns from hypotheses that
would need more information. If you use a knowledge statement, explain how it is
relevant and do not treat a short definition as proof that the simulation is valid
or invalid. Be concise, specific, and balanced.

Return exactly these three sections:

A. OVERALL REALISM
Choose exactly one verdict: YES, PARTLY, or NO.
Explain the verdict in 2–4 sentences.

B. TOP 3 REALISM GAPS
List up to three gaps, ranked from most important to least important. For each, state
(1) the gap, (2) why it matters, and (3) whether it is directly supported by the
description or is a hypothesis needing more information. Do not invent details.

C. ONE MINIMUM REVISION
Recommend exactly one smallest practical revision. State what to change and how to
evaluate whether that change improves the simulation. Do not list multiple alternatives.
""".strip()

PROMPT = (
    "SIMULATION DETAILS\n" + SIMULATION_DESCRIPTION + "\n\n" + ASSESSMENT_INSTRUCTIONS
)

def safe_filename(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)

def call_model(model, prompt):
    messages = [
        {"role": "system", "content": "Follow the assessment instructions exactly. Be concise and evidence-conscious."},
        {"role": "user", "content": prompt},
    ]
    if model["provider"] == "groq":
        response = groq_client.chat.completions.create(
            model=model["name"], messages=messages,
            max_tokens=MAX_OUTPUT_TOKENS, temperature=TEMPERATURE,
        )
    elif model["provider"] == "nvidia":
        response = nvidia_client.chat.completions.create(
            model=model["name"], messages=messages,
            max_tokens=MAX_OUTPUT_TOKENS, temperature=TEMPERATURE,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
    else:
        raise ValueError(f"Unsupported provider: {model['provider']}")

    if not response.choices:
        return "", "no_choices", "REVIEW", "No choices returned"
    choice = response.choices[0]
    content = choice.message.content or ""
    reason = str(choice.finish_reason or "unknown")
    lower_reason = reason.lower()
    if "length" in lower_reason or "max_tokens" in lower_reason:
        status = "INCOMPLETE"
    elif content.strip() and ("stop" in lower_reason or "end_turn" in lower_reason):
        status = "SUCCESS"
    else:
        status = "REVIEW"
    usage = str(response.usage) if getattr(response, "usage", None) else "Not available"
    return content, reason, status, usage

def write_manifest():
    manifest = {
        "system": "A", "experiment_id": EXPERIMENT_ID,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "models": MODELS, "runs_per_model": RUNS_PER_MODEL,
        "temperature": TEMPERATURE, "max_output_tokens": MAX_OUTPUT_TOKENS,
        "request_delay_seconds": REQUEST_DELAY_SECONDS, "grounding": False,
        "simulation_description": SIMULATION_DESCRIPTION,
        "assessment_instructions": ASSESSMENT_INSTRUCTIONS,
    }
    (OUTPUT_DIR / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

def main():
    write_manifest()
    totals = {"SUCCESS": 0, "INCOMPLETE": 0, "FAILED": 0, "REVIEW": 0}
    print("=== SYSTEM A: Ungrounded Assessment ===")
    print(f"Experiment ID: {EXPERIMENT_ID}")
    print(f"Models: {len(MODELS)} | Runs/model: {RUNS_PER_MODEL}")
    print(f"Planned assessments: {len(MODELS) * RUNS_PER_MODEL}")
    print(f"Output directory: {OUTPUT_DIR}\n")

    for model in MODELS:
        print(f"\nModel: {model['name']} ({model['provider']})")
        for run_number in range(1, RUNS_PER_MODEL + 1):
            print(f"  Run {run_number:02d}/{RUNS_PER_MODEL}: ", end="", flush=True)
            try:
                content, reason, status, usage = call_model(model, PROMPT)
            except Exception as exc:
                content, reason, status, usage = f"{type(exc).__name__}: {exc}", "error", "FAILED", "Not available"
            filename = OUTPUT_DIR / f"system_a_{safe_filename(model['name'])}_run{run_number:02d}.txt"
            with filename.open("w", encoding="utf-8") as f:
                f.write(f"=== SYSTEM A | {model['name']} | RUN {run_number:02d} ===\n")
                f.write(f"EXPERIMENT ID: {EXPERIMENT_ID}\nPROVIDER: {model['provider']}\n")
                f.write(f"STATUS: {status}\nFINISH REASON: {reason}\n")
                f.write(f"TEMPERATURE: {TEMPERATURE}\nMAX OUTPUT TOKENS: {MAX_OUTPUT_TOKENS}\nUSAGE: {usage}\n")
                f.write("GROUNDING: NONE\n\n" + "=" * 60 + "\n\n")
                f.write(content.rstrip() + "\n")
            totals[status] += 1
            print(status)
            time.sleep(REQUEST_DELAY_SECONDS)

    print("\n=== SYSTEM A SUMMARY ===")
    for status, count in totals.items():
        print(f"{status}: {count}")
    print(f"Total attempts: {sum(totals.values())}")
    print(f"Results: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
