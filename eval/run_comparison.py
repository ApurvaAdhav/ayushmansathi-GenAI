
import json
from pathlib import Path

from app.llm import generate_response
from data.user_questions import user_questions

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_DIR = BASE_DIR / "prompts"
EVAL_DIR = BASE_DIR / "eval"

PROGRESS_FILE = EVAL_DIR / "comparison_progress.json"
OUTPUT_FILE = EVAL_DIR / "prompt_compare.md"

# Version A: Basic prompt
version_a = """
You are a healthcare information assistant.
Answer questions in simple and understandable language.
"""

# Version B: Improved prompt
version_b = (PROMPT_DIR / "system.txt").read_text(encoding="utf-8")

# Load saved responses
if PROGRESS_FILE.exists():
    progress = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
else:
    progress = {}

# Test all 10 questions
for number, question in enumerate(user_questions, start=1):

    print(f"\nTesting question {number}/10")

    for version, prompt_text in [
        ("A", version_a),
        ("B", version_b)
    ]:

        key = f"{number}_{version}"

        # Skip already completed responses
        if key in progress:
            print(f"Version {version} already completed. Skipping.")
            continue

        try:
            prompt = f"{prompt_text}\nQuestion: {question}"
            answer = generate_response(prompt)

            # Save immediately
            progress[key] = answer

            PROGRESS_FILE.write_text(
                json.dumps(progress, indent=4),
                encoding="utf-8"
            )

            print(f"Version {version} completed and saved.")

        except (RuntimeError, OSError) as error:
            print(f"Version {version} failed: {error}")
            print("Progress saved. Stopping comparison.")
            break

    else:
        continue

    break

# Generate comparison report
results = ["# AyushmanSathi - Prompt Comparison\n"]

completed = 0

for number, question in enumerate(user_questions, start=1):

    answer_a = progress.get(f"{number}_A", "Pending")
    answer_b = progress.get(f"{number}_B", "Pending")

    if f"{number}_A" in progress and f"{number}_B" in progress:
        completed += 1

    results.append(f"""
## Question {number}: {question}

### Version A - Basic Prompt
{answer_a}

### Version B - Improved Prompt
{answer_b}

---
""")

OUTPUT_FILE.write_text("\n".join(results), encoding="utf-8")

print(f"\nCompleted comparisons: {completed}/10")
print("Report saved:", OUTPUT_FILE)
print("Progress saved:", PROGRESS_FILE)
