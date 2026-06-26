"""
Prompt Pipeline — Support Ticket Triage.

Three stages:
  1. Understand  (Senior QA Engineer)    — structured output → JSON
  2. Reason      (Staff Software Engineer) — chain-of-thought → JSON
  3. Produce     (Technical Support Lead)  — goal-oriented → report + handoff + reply
"""
from prompts import (
    STAGE1_SYSTEM, STAGE1_USER,
    STAGE2_SYSTEM, STAGE2_USER,
    STAGE3_SYSTEM, STAGE3_USER,
)
from utils import parse_json_with_retry, show, save_run


# ── Pipeline stages ────────────────────────────────────────────────────────

def stage1_understand(raw_text: str) -> dict:
    """Stage 1: Senior QA Engineer — extract structured info."""
    user_prompt = STAGE1_USER.format(raw_text=raw_text)
    return parse_json_with_retry(STAGE1_SYSTEM, user_prompt)


def stage2_reason(brief: dict) -> dict:
    """Stage 2: Staff Software Engineer — root cause analysis."""
    user_prompt = STAGE2_USER.format(**brief)
    return parse_json_with_retry(STAGE2_SYSTEM, user_prompt)


def stage3_produce(brief: dict, decision: dict) -> dict:
    """Stage 3: Technical Support Lead — generate deliverables."""
    user_prompt = STAGE3_USER.format(**brief, **decision)
    return parse_json_with_retry(STAGE3_SYSTEM, user_prompt)


# ── Pipeline runner ────────────────────────────────────────────────────────

def run(input_text: str, run_name: str) -> dict:
    """Run the full pipeline on one input, printing every stage."""
    print(f"\n{'#' * 70}")
    print(f"#  RUN: {run_name}")
    print(f"{'#' * 70}")
    print(f"\nINPUT:\n{input_text}\n")

    stages = []

    # Stage 1
    print("▸ Stage 1: Understand (Senior QA Engineer) ...")
    brief = stage1_understand(input_text)
    show("STAGE 1  —  Understand", brief)
    stages.append({"label": "Understand (Senior QA Engineer)", "output": brief})

    # Stage 2
    print("▸ Stage 2: Reason (Staff Software Engineer) ...")
    decision = stage2_reason(brief)
    show("STAGE 2  —  Reason", decision)
    stages.append({"label": "Reason (Staff Software Engineer)", "output": decision})

    # Stage 3
    print("▸ Stage 3: Produce (Technical Support Lead) ...")
    output = stage3_produce(brief, decision)
    show("STAGE 3  —  Produce", output)
    stages.append({"label": "Produce (Technical Support Lead)", "output": output})

    # Save run
    save_run(run_name, input_text, stages)

    return output


# ── Test inputs ─────────────────────────────────────────────────────────────

def main():
    # Input 1: Normal — clear bug report with all details
    input_normal = (
        "Hi, my name is Alice Chen. I'm using your PhotoEdit Pro v3.2 on Windows 11. "
        "When I try to export a project as PNG, the app crashes every time. "
        "This has been happening for 4 days now. I've tried reinstalling but it didn't help. "
        "Steps: Open app → Load project → File → Export → Select PNG format → Crashes."
    )

    # Input 2: Tricky — vague, emotional, missing information
    input_tricky = (
        "URGENT!!! Your app is AWFUL it's been BROKEN for over a week now "
        "and I can't get ANY work done!! This is costing me money!! "
        "Fix it NOW or I'm switching to your competitor!!! "
        "— signed, a VERY frustrated customer"
    )

    # Input 3: Broken — gibberish, no structured information
    input_broken = (
        "xylophone 42 banana 🍌🍌🍌 "
        "kjhfsdkjfhsd fhdsjfhdskjfhdskj lorem ipsum dolor sit amet "
        "!!!???"
    )

    runs = [
        ("run1_normal", input_normal, "Normal ticket — Alice Chen, clear bug report"),
        ("run2_tricky", input_tricky, "Tricky ticket — vague, emotional, missing details"),
        ("run3_broken", input_broken, "Broken input — gibberish, no useful info"),
    ]

    for run_name, input_text, description in runs:
        print(f"\n{'=' * 70}")
        print(f"  RUN: {run_name}  —  {description}")
        print(f"{'=' * 70}")
        try:
            run(input_text, run_name)
        except Exception as e:
            print(f"\n  [ERROR] {e}")
            # Save error run
            error_stages = []
            if 'brief' in locals() and brief:
                error_stages.append({"label": "Understand", "output": brief})
            if 'decision' in locals() and decision:
                error_stages.append({"label": "Reason", "output": decision})
            error_stages.append({"label": f"Error — {e}", "output": str(e)})
            save_run(run_name, input_text, error_stages)
        print(f"\n{'=' * 70}\n")

    print("\n✓ All runs complete. See runs/ directory for full output.")


if __name__ == "__main__":
    main()