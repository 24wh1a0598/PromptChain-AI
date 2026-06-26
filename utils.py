"""
Utility functions: JSON parsing with retry, pretty-printing, saving runs.
"""
import json
import os
import re
from llm import call_llm


# ── JSON extraction & retry ────────────────────────────────────────────────

def extract_json(text: str) -> str | None:
    """Extract a JSON object string from model output.

    Handles:
      - ```json ... ``` code fences
      - ``` ... ``` code fences
      - Raw JSON objects { ... }
    """
    # Try code fences first: ```json ... ``` or ``` ... ```
    pattern = r"```(?:json)?\s*\n?([\s\S]*?)```"
    matches = re.findall(pattern, text)
    for match in matches:
        match = match.strip()
        if match.startswith("{") and match.endswith("}"):
            return match
        if match.startswith("[") and match.endswith("]"):
            return match

    # Try raw JSON object (first { to last })
    brace_match = re.search(r"\{[\s\S]*\}", text)
    if brace_match:
        return brace_match.group(0)

    return None


def parse_json_with_retry(system_prompt: str, user_prompt: str,
                          max_retries: int = 3) -> dict:
    """Call the LLM, parse response as JSON. Re-prompt on failure."""
    for attempt in range(max_retries):
        raw = call_llm(system_prompt, user_prompt)
        json_str = extract_json(raw)

        if json_str:
            try:
                parsed = json.loads(json_str)
                return parsed
            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:
                    user_prompt = (
                        f"Your previous response was not valid JSON.\n"
                        f"Error: {e}\n\n"
                        f"Raw output:\n{raw}\n\n"
                        f"Respond with ONLY valid JSON. No markdown, no extra text."
                    )
                else:
                    raise ValueError(
                        f"JSON parse failed after {max_retries} attempts: {e}"
                    )
        else:
            if attempt < max_retries - 1:
                user_prompt = (
                    f"Your previous response did not contain valid JSON.\n"
                    f"Raw output:\n{raw}\n\n"
                    f"Respond with ONLY valid JSON. No markdown, no extra text."
                )
            else:
                raise ValueError(
                    f"Failed to extract JSON after {max_retries} attempts. "
                    f"Raw: {raw[:300]}"
                )


# ── Pretty-printing & saving ──────────────────────────────────────────────

def show(label: str, data):
    """Print a labelled stage output clearly."""
    sep = "=" * 60
    print(f"\n{sep}")
    print(f"  {label}")
    print(sep)
    if isinstance(data, dict):
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif isinstance(data, str):
        print(data)
    else:
        print(data)
    print(sep)


def save_run(run_name: str, input_text: str, stages: list):
    """Save a run's full trace to runs/{run_name}.txt."""
    os.makedirs("runs", exist_ok=True)
    filename = f"runs/{run_name}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"=== {run_name} ===\n\n")
        f.write(f"INPUT:\n{input_text}\n\n")

        for i, stage in enumerate(stages, 1):
            f.write(f"--- Stage {i}: {stage['label']} ---\n")
            if 'prompt' in stage:
                f.write(f"  User prompt:\n{stage['prompt']}\n\n")
            f.write(f"  Output:\n{stage['output']}\n\n")

        f.write("=== END ===\n")

    print(f"  [Saved to {filename}]")
    return filename