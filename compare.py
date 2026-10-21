"""
Compare System A and System B within the same experiment folder.
Consistency is repeatability, not truth or factual accuracy.
"""
import json
import os
import re
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
EXPERIMENT_ID = os.getenv("EXPERIMENT_ID", "experiment_20261020_01")
SYSTEM_A_DIR = BASE_DIR / "System_A" / "results" / EXPERIMENT_ID
SYSTEM_B_DIR = BASE_DIR / "System_B" / "results" / EXPERIMENT_ID

MANIFEST = SYSTEM_A_DIR / "run_manifest.json"
if not MANIFEST.is_file():
    raise SystemExit(f"Manifest not found: {MANIFEST}. Run System A first.")
MODELS = json.loads(MANIFEST.read_text(encoding="utf-8"))["models"]

NUM_RUNS = 10
VALID_VERDICTS = {"YES", "NO", "PARTLY"}


def safe_filename(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def result_path(system, model, run_number):
    name = safe_filename(model["name"])
    if system == "A":
        return SYSTEM_A_DIR / f"system_a_{name}_run{run_number:02d}.txt"
    return SYSTEM_B_DIR / (
        f"system_b_{safe_filename(model['provider'])}_{name}_run{run_number:02d}.txt"
    )


def split_report(text):
    match = re.search(r"^STATUS:\s*([A-Z_]+)\s*$", text, re.MULTILINE)
    status = match.group(1).upper() if match else "UNKNOWN"
    pieces = re.split(r"^={40,}\s*$", text, flags=re.MULTILINE)
    return status, pieces[-1] if len(pieces) > 1 else text


def find_section(lines, letter):
    pattern = re.compile(rf"^\s*(?:[#>*_]+\s*)?{letter}\s*[.):\-–—]\s*(.*)$", re.I)
    for i, line in enumerate(lines):
        if pattern.match(line):
            return i
    return None


def extract_verdict(body):
    lines = body.splitlines()
    start = find_section(lines, "A")
    if start is None:
        match = re.search(
            r"\b(?:verdict|overall realism)\s*[:\-]\s*(YES|NO|PARTLY|PARTIAL|PARTIALLY)\b",
            body, re.I)
        if not match:
            return "UNCLEAR"
        word = match.group(1).upper()
    else:
        end = len(lines)
        for letter in ("B", "C"):
            nxt = find_section(lines, letter)
            if nxt is not None and nxt > start:
                end = min(end, nxt)
        section = "\n".join(lines[start:end])
        explicit = re.search(
            r"\b(?:verdict|choose exactly one verdict|overall realism)\s*[:\-]\s*(YES|NO|PARTLY|PARTIAL|PARTIALLY)\b",
            section, re.I)
        quoted = re.search(r'["“](YES|NO|PARTLY|PARTIAL|PARTIALLY)[.,]?["”]', section, re.I)
        if explicit:
            word = explicit.group(1).upper()
        elif quoted:
            word = quoted.group(1).upper()
        else:
            first_lines = "\n".join(lines[start:min(end, start + 5)])
            match = re.search(
                r"^\s*(?:[-*]\s*)?(YES|NO|PARTLY|PARTIAL|PARTIALLY)\b",
                first_lines, re.I | re.M)
            if not match:
                return "UNCLEAR"
            word = match.group(1).upper()
    if word in {"PARTIAL", "PARTIALLY"}:
        return "PARTLY"
    return word if word in VALID_VERDICTS else "UNCLEAR"


def extract_gap(body):
    lines = body.splitlines()
    start = find_section(lines, "B")
    if start is None:
        return "SECTION B NOT FOUND"
    end = len(lines)
    c_start = find_section(lines, "C")
    if c_start is not None and c_start > start:
        end = c_start
    content = [line.strip() for line in lines[start + 1:end] if line.strip()]
    if not content:
        return "SECTION B EMPTY"
    first = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s*", "", content[0]).strip()
    first = re.sub(r"[*_`#]", "", first)
    if len(first) < 8 and len(content) > 1:
        first = re.sub(r"[*_`#]", "", " ".join(content[:2]))
    return first[:180]


def load_result(path):
    if not path.is_file():
        return {"status": "FILE_NOT_FOUND", "verdict": "MISSING", "gap": "FILE NOT FOUND"}
    text = path.read_text(encoding="utf-8", errors="replace")
    status, body = split_report(text)
    if status != "SUCCESS":
        return {"status": status, "verdict": "INVALID_STATUS", "gap": f"INVALID STATUS: {status}"}
    verdict = extract_verdict(body)
    gap = extract_gap(body)
    if verdict == "UNCLEAR":
        gap = "VERDICT UNCLEAR | " + gap
    return {"status": status, "verdict": verdict, "gap": gap}


def score_consistency(records):
    verdicts = [r["verdict"] for r in records if r["verdict"] in VALID_VERDICTS]
    if not verdicts:
        return None, 0, 0, "N/A"
    counts = Counter(verdicts)
    mode, count = counts.most_common(1)[0]
    return round(100 * count / len(verdicts)), count, len(verdicts), mode


def main():
    print("=" * 78)
    print("SYSTEM A vs SYSTEM B — EXPERIMENT COMPARISON")
    print("=" * 78)
    print(f"Experiment ID: {EXPERIMENT_ID}")
    print(f"System A: {SYSTEM_A_DIR}")
    print(f"System B: {SYSTEM_B_DIR}")
    if not SYSTEM_A_DIR.is_dir() or not SYSTEM_B_DIR.is_dir():
        print("\nERROR: Result folder missing. Run both systems using the same EXPERIMENT_ID.")
        return

    summary = []
    for model in MODELS:
        print("\n" + "-" * 78 + f"\nMODEL: {model['name']}\n" + "-" * 78)
        data = {}
        for system, label in (("A", "SYSTEM A (Ungrounded)"), ("B", "SYSTEM B (Wikidata-grounded)")):
            records = []
            print(f"\n{label}:")
            for run_number in range(1, NUM_RUNS + 1):
                rec = load_result(result_path(system, model, run_number))
                records.append(rec)
                print(f"  Run {run_number:02d} | {rec['verdict']:<15} | {rec['gap'][:100]}")
            pct, agreed, valid, mode = score_consistency(records)
            print(f"  Verdict consistency: {pct}% ({agreed}/{valid} agree on {mode}; valid={valid}/{NUM_RUNS})"
                  if pct is not None else "  Verdict consistency: N/A (0 valid verdicts)")
            print(f"  Status counts: {dict(Counter(r['status'] for r in records))}")
            data[system] = (pct, valid, mode)

        a_pct, a_valid, a_mode = data["A"]
        b_pct, b_valid, b_mode = data["B"]
        change = None if a_pct is None or b_pct is None else b_pct - a_pct
        summary.append((model["name"], a_pct, b_pct, change, a_valid, b_valid, a_mode, b_mode))

    report = [
        "SYSTEM A vs SYSTEM B — SUMMARY", f"Experiment ID: {EXPERIMENT_ID}", "",
        "Model | A consistency | B consistency | Change (pp) | A valid | B valid | A verdict | B verdict",
    ]
    for name, a, b, change, av, bv, am, bm in summary:
        report.append(f"{name} | {str(a)+'%' if a is not None else 'N/A'} | "
                      f"{str(b)+'%' if b is not None else 'N/A'} | "
                      f"{f'{change:+d}' if change is not None else 'N/A'} | "
                      f"{av}/{NUM_RUNS} | {bv}/{NUM_RUNS} | {am} | {bm}")
    report += ["", "Interpretation: consistency measures repeatability, not correctness or realism.",
               "Review the actual outputs and manually verify whether gaps are evidence-supported."]
    report_path = BASE_DIR / f"comparison_results_{safe_filename(EXPERIMENT_ID)}.txt"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\nSUMMARY")
    print("\n".join(report[3:]))
    print(f"\nSummary saved to: {report_path}")


if __name__ == "__main__":
    main()