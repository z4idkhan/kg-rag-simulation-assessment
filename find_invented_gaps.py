"""
Flag gaps that may contradict the simulation description.
Output is a CSV for MANUAL review — the script only finds candidates.
"""
import csv, json, os, re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
EXPERIMENT_ID = os.getenv("EXPERIMENT_ID", "experiment_20261020_02")
DIRS = {"A": BASE_DIR / "System_A" / "results" / EXPERIMENT_ID,
        "B": BASE_DIR / "System_B" / "results" / EXPERIMENT_ID}
MODELS = json.loads((DIRS["A"] / "run_manifest.json").read_text())["models"]

# Features the description EXPLICITLY states.
STATED = {
    "learning algorithm (Q-learning)": ["q-learning", "learning algorithm", "reinforcement learning", "learning mechanism"],
    "peer interaction": ["peer", "social influence", "social network", "interaction between students"],
    "detection probabilities": ["detection probabilit", "detection rate"],
    "intervention conditions": ["intervention"],
    "action types": ["direct copying", "ai-assisted", "honest submission"],
}
# Words suggesting the model claims something is absent.
ABSENT = ["not specified", "not consider", "does not", "doesn't", "lack", "missing",
          "absent", "not mention", "unspecified", "not include", "no information",
          "not described", "not defined", "not explain", "not provide"]

def safe(v): return re.sub(r"[^A-Za-z0-9_.-]+", "_", v)

def path(system, model, run):
    n = safe(model["name"])
    if system == "A":
        return DIRS["A"] / f"system_a_{n}_run{run:02d}.txt"
    return DIRS["B"] / f"system_b_{safe(model['provider'])}_{n}_run{run:02d}.txt"

def section_b(text):
    body = re.split(r"^={40,}\s*$", text, flags=re.M)[-1]
    m = re.search(r"^\s*[#>*_]*\s*B\s*[.):\-–—](.*?)^\s*[#>*_]*\s*C\s*[.):\-–—]", body, re.S | re.M | re.I)
    return m.group(1) if m else ""

rows = []
for model in MODELS:
    for system in ("A", "B"):
        for run in range(1, 11):
            p = path(system, model, run)
            if not p.is_file():
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            if "STATUS: SUCCESS" not in text:
                continue
            for sentence in re.split(r"(?<=[.!?])\s+|\n", section_b(text)):
                s = sentence.lower()
                if not any(w in s for w in ABSENT):
                    continue
                for feature, keys in STATED.items():
                    if any(k in s for k in keys):
                        rows.append({"system": system, "model": model["name"], "run": run,
                                     "feature": feature, "sentence": sentence.strip()[:300],
                                     "invented (Y/N)": ""})

out = BASE_DIR / f"invented_gap_candidates_{safe(EXPERIMENT_ID)}.csv"
with out.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["system", "model", "run", "feature", "sentence", "invented (Y/N)"])
    w.writeheader(); w.writerows(rows)
print(f"{len(rows)} candidate sentences written to {out}")