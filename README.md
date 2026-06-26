# Prompt Pipeline — Support Ticket Triage

A prompt-only task-completer built for the GenAI & Agentic AI Engineering programme (Day 2 Homework).

Three LLM stages chain together to turn raw bug reports into structured analysis and professional responses — with nothing but well-engineered prompts.

## Architecture

```
Raw input (bug report / message)
         │
         ▼
┌─────────────────────────────────────┐
│ Stage 1: Understand                 │
│ Role: Senior QA Engineer            │
│ Technique: Role + Structured Output │
│ Output: JSON with extracted fields  │
└─────────────┬───────────────────────┘
              │ JSON handoff
              ▼
┌─────────────────────────────────────┐
│ Stage 2: Reason                     │
│ Role: Staff Software Engineer       │
│ Technique: Chain-of-Thought         │
│ Output: JSON (root cause, priority, │
│          timeline, reasoning)       │
└─────────────┬───────────────────────┘
              │ JSON handoff
              ▼
┌─────────────────────────────────────┐
│ Stage 3: Produce                    │
│ Role: Technical Support Lead        │
│ Technique: Goal-Oriented + Constr.  │
│ Output: JSON (engineering report,   │
│          developer handoff,         │
│          customer reply)            │
└─────────────┬───────────────────────┘
              │
              ▼
     Final deliverables
```

## Setup

1. **Clone / navigate to the project**

   ```bash
   cd Prompt_Pipeline
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set your OpenRouter API key**

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and paste your key:
   ```
   OPENROUTER_API_KEY=sk-or-v1-your-actual-key
   ```

   Get a key at [openrouter.ai/keys](https://openrouter.ai/keys).

4. **Run the pipeline**

   ```bash
   python main.py
   ```

   This runs three test inputs and saves the output to the `runs/` directory.

## Test Inputs

| Run | File | Description |
|-----|------|-------------|
| run1_normal | `runs/run1_normal.txt` | Clear bug report — Alice Chen, PhotoEdit Pro v3.2, crash on export |
| run2_tricky | `runs/run2_tricky.txt` | Vague, emotional, missing details — angry customer, no product info |
| run3_broken | `runs/run3_broken.txt` | Gibberish — random words and emoji, no structured information |

## Technique Labels

| Stage | Technique | Why |
|-------|-----------|-----|
| 1 — Understand | Role + Structured Output | Senior QA Engineer persona pushes precise extraction; explicit JSON schema enforces structure |
| 2 — Reason | Chain-of-Thought | "Think step by step" prompts before final answer — essential for accurate root cause analysis |
| 3 — Produce | Goal-Oriented + Constraints | Three distinct deliverables with word limits and tone constraints; persona ensures professional quality |

## Reflection: Weakest Link

**Stage 2 (Reason)** is the weakest stage in this pipeline. It depends entirely on the quality of Stage 1's structured output — if Stage 1 misclassifies severity or misses a critical detail, the root cause analysis will be wrong regardless of how well Stage 2 reasons. You'd know it's failing when the pipeline produces confident-sounding but incorrect diagnoses (e.g. blaming frontend for a backend issue that Stage 1 mislabeled). A retrieval-augmented step (Day 4) could fix this by letting Stage 2 pull relevant past tickets or known error patterns from a knowledge base. A tool (Day 6) could let it actually reproduce the bug in a sandbox environment — turning guesswork into verification. Even without those, a simple self-consistency check (run Stage 2 twice and compare) would catch some failures.

## Project Files

| File | Purpose |
|------|---------|
| `main.py` | Pipeline orchestrator, runs 3 test inputs |
| `prompts.py` | All 3 prompt templates with system/user roles |
| `llm.py` | OpenRouter API wrapper (`call_llm`) |
| `utils.py` | JSON parsing with retry, pretty-printing, file saving |
| `.env` | API key (you create this) |
| `runs/` | Output files from each run |

## Project Status & Results

This project successfully runs the full three-stage prompt pipeline and produces structured outputs for three sample support tickets.

### Generated Output Files
- [runs/run1_normal.txt](runs/run1_normal.txt) — clear bug report input
- [runs/run2_tricky.txt](runs/run2_tricky.txt) — vague and emotional customer message
- [runs/run3_broken.txt](runs/run3_broken.txt) — broken or gibberish input

### What the pipeline does
1. Extracts structured bug report details from raw input.
2. Performs root cause reasoning and triage prioritization.
3. Produces an engineering report, developer handoff, and customer reply.

### How to view the results
Open the files in the [runs](runs) folder to inspect the generated outputs for each test case.

### Demo Summary
This project demonstrates how well-engineered prompts can be chained together to create a simple agent-like workflow for support ticket triage without requiring any complex tooling.