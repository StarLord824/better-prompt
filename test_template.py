"""
Test script to demonstrate the improved template filling.
"""

from better_prompt.core.pipeline import PipelineOrchestrator
from better_prompt.core.refiner import ToneType

# Create orchestrator
orchestrator = PipelineOrchestrator()

# Test prompt
prompt = "Write a Python function to validate email addresses"

# Process with template
result = orchestrator.process(
    prompt=prompt,
    model_name="gpt-4",
    provider="OpenAI",
    tone=ToneType.PROFESSIONAL,
    apply_template=True
)

print("="*80)
print("ORIGINAL PROMPT:")
print("="*80)
print(result.original_prompt)
print()

print("="*80)
print("REFINED PROMPT WITH FILLED TEMPLATE:")
print("="*80)
print(result.refined_prompt)
print()

print("="*80)
print("IMPROVEMENTS:")
print("="*80)
for improvement in result.refinement_result.improvements:
    print(f"  • {improvement}")
print()

print("="*80)
print("METADATA:")
print("="*80)
template_meta = result.refinement_result.metadata.get("apply_template", {})
print(f"  Template Applied: {template_meta.get('template_applied', False)}")
print(f"  Placeholders Filled: {template_meta.get('placeholders_filled', 0)}")
