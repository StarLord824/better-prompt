# Better Prompt - Quick Start Guide

## Installation

### Prerequisites
- Python 3.9 or higher
- pip

### Install Dependencies

```bash
cd better-prompt
pip install -r requirements.txt
```

## Quick Start

### 1. Basic Usage

```python
from better_prompt.core.pipeline import PipelineOrchestrator

# Create orchestrator
orchestrator = PipelineOrchestrator()

# Process a prompt
result = orchestrator.process(
    prompt="Write a Python function to sort an array",
    model_name="gpt-4",
    provider="OpenAI"
)

# Print summary
print(result.get_summary())
```

### 2. Task Classification Only

```python
from better_prompt.core.classifier import TaskClassifier

classifier = TaskClassifier()
result = classifier.classify("Create an image of a sunset")

print(f"Task: {result.task_type.value}")
print(f"Confidence: {result.confidence:.2%}")
```

### 3. Format Selection Only

```python
from better_prompt.core.format_selector import FormatSelector

selector = FormatSelector()
result = selector.recommend_format(
    model_name="claude-3-opus",
    provider="Anthropic"
)

print(f"Format: {result.recommended_format.value}")
print(f"Template:\n{result.template_skeleton}")
```

### 4. Refinement Only

```python
from better_prompt.core.refiner import RefinementPipeline, ToneType

pipeline = RefinementPipeline(target_tone=ToneType.PROFESSIONAL)
result = pipeline.refine(
    prompt="write code to validate emails",
    task_type="code_generation"
)

print(f"Original: {result.original_prompt}")
print(f"Refined: {result.refined_prompt}")
print(f"Improvements: {result.improvements}")
```

### 5. Batch Processing

```python
from better_prompt.core.pipeline import PipelineOrchestrator

orchestrator = PipelineOrchestrator()

prompts = [
    "generate an image",
    "write sql query",
    "debug code"
]

results = orchestrator.process_batch(
    prompts=prompts,
    model_name="gpt-4",
    provider="OpenAI"
)

# Get statistics
stats = orchestrator.get_statistics(results)
print(f"Total: {stats['total_prompts']}")
print(f"Task Distribution: {stats['task_type_distribution']}")
```

### 6. Custom Tone and Constraints

```python
from better_prompt.core.pipeline import PipelineOrchestrator
from better_prompt.core.refiner import ToneType

orchestrator = PipelineOrchestrator()

result = orchestrator.process(
    prompt="explain quantum computing",
    model_name="gemini-pro",
    provider="Google",
    tone=ToneType.CASUAL,
    custom_constraints=[
        "Keep it under 200 words",
        "Use simple analogies"
    ]
)

print(result.refined_prompt)
```

## Running Examples

### Run All Examples

```bash
python examples/demo.py
```

This will run 7 comprehensive examples demonstrating all features.

### Run Tests

```bash
python tests/test_core.py
```

Expected output: `Test Results: 7 passed, 0 failed`

## Supported Models

Better Prompt has built-in format recommendations for 37+ models:

### OpenAI
- gpt-4, gpt-4o, gpt-4o-mini → Markdown
- o1-research → JSON

### Anthropic
- claude-3-opus, claude-4-opus → XML
- claude-3-sonnet, claude-4-haiku → XML

### Google
- gemini-pro → JSON
- gemini-ultra → YAML
- gemini-1.5-viz → Markdown

### Alibaba
- qwen3-max, qwen2.5-coder-32B → JSON
- qwen2.5-vl → YAML

### DeepSeek
- deepseek-v3.1, deepseek-r1-instruct → JSON
- deepseek-v2-lite → YAML

### xAI
- grok-4, grok-code-fast → Markdown
- grok-agent-alpha → XML

## Task Types

Better Prompt can classify 15+ task types:

- **Code**: code_generation, code_review, code_debug
- **Creative**: image_generation, video_generation, story_writing, creative_writing
- **Data**: sql_query, data_analysis
- **Language**: translation, summarization
- **Writing**: technical_writing
- **Research**: research, question_answering
- **General**: general, chatbot

## Tone Types

Choose from 7 tone types for refinement:

- **PROFESSIONAL**: Formal, business-appropriate
- **CASUAL**: Relaxed, conversational
- **TECHNICAL**: Precise, implementation-focused
- **CREATIVE**: Imaginative, exploratory
- **FORMAL**: Very formal, academic
- **FRIENDLY**: Warm, approachable
- **NEUTRAL**: Balanced, objective

## Output Formats

Better Prompt supports 5 output formats:

- **JSON**: Structured data, API interactions
- **XML**: Hierarchical markup, metadata
- **YAML**: Human-readable configuration
- **Markdown**: Natural language, documentation
- **Text**: Simple, conversational

## Next Steps

1. ✅ Read the [README.md](README.md) for detailed documentation
2. ✅ Run `python examples/demo.py` to see all features
3. ✅ Run `python tests/test_core.py` to verify installation
4. ✅ Check [PHASE1_SUMMARY.md](PHASE1_SUMMARY.md) for implementation details

## Troubleshooting

### Import Errors

If you get import errors, make sure you're in the project directory:

```bash
cd better-prompt
python -c "import better_prompt; print('Success!')"
```

### Test Failures

If tests fail, check Python version:

```bash
python --version  # Should be 3.9 or higher
```

### Module Not Found

If running examples fails, add the project to your path:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

## Support

For issues or questions:
- Check the [README.md](README.md)
- Review [PHASE1_SUMMARY.md](PHASE1_SUMMARY.md)
- Run the examples: `python examples/demo.py`

---

**Better Prompt** - Transform your prompts, elevate your results. 🚀
