"""
Simple test: verify all 12 template files exist.
"""
from pathlib import Path

template_dir = Path("src/templates/prompts")

expected_files = [
    "phase_1/brainstorm_chatgpt.jinja2",
    "phase_1/validate_claude.jinja2",
    "phase_2/deep_search_gemini.jinja2",
    "phase_2/fact_check_perplexity.jinja2",
    "phase_3/swot_chatgpt.jinja2",
    "phase_3/narrative_claude.jinja2",
    "phase_4/business_plan_claude.jinja2",
    "phase_4/outline_chatgpt.jinja2",
    "phase_4/charts_gemini.jinja2",
    "phase_5/verify_perplexity.jinja2",
    "phase_5/final_review_claude.jinja2",
    "phase_5/polish_claude.jinja2",
]

exist_count = 0
for file_path in expected_files:
    full_path = template_dir / file_path
    if full_path.exists():
        exist_count += 1
        print(f"✅ {file_path}")
    else:
        print(f"❌ {file_path} MISSING")

print(f"\n{'='*60}")
print(f"Result: {exist_count}/{len(expected_files)} templates exist")
assert exist_count == len(expected_files), f"Missing {len(expected_files) - exist_count} templates!"
print(f"{'='*60}")
