# Better Prompt

**Better Prompt** is a sophisticated prompt refinement system that takes raw user prompts and transforms them into optimized, structured prompts tailored for specific LLM models and tasks.

## 🎯 Overview

Better Prompt analyzes your prompts, identifies their purpose, selects the optimal output format for your target model, and applies a multi-stage refinement pipeline to produce production-ready prompts.

### Key Features

- **🔍 Task Classification**: Hybrid heuristic + LLM-based classification for 15+ task types
- **📋 Format Selection**: RAG-based format recommendations (JSON, XML, YAML, Markdown, Text)
- **✨ Multi-Stage Refinement**: Cleanup, constraint expansion, tone adjustment, token optimization
- **🔌 Plugin System**: Extensible architecture for custom processors
- **🌐 LLM Gateway**: Abstract interface for multiple LLM providers
- **📊 Batch Processing**: Process multiple prompts efficiently with statistics

## 📁 Project Structure

```
better-prompt/
├── better_prompt/
│   ├── core/
│   │   ├── classifier/          # Task classification
│   │   │   ├── __init__.py
│   │   │   └── task_classifier.py
│   │   ├── format_selector/     # Format recommendation
│   │   │   ├── __init__.py
│   │   │   └── format_selector.py
│   │   ├── refiner/             # Refinement pipeline
│   │   │   ├── __init__.py
│   │   │   └── pipeline.py
│   │   ├── pipeline/            # Orchestration
│   │   │   ├── __init__.py
│   │   │   └── orchestrator.py
│   │   ├── plugins/             # Plugin system
│   │   │   ├── __init__.py
│   │   │   ├── manifest.py
│   │   │   └── registry.py
│   │   ├── llm_gateway/         # LLM providers
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── dummy_provider.py
│   │   └── resources/
│   │       └── format_mapping.json
│   └── __init__.py
├── examples/
│   └── demo.py                  # Example usage
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 🚀 Phase 1 - Core Engine (Current)

Phase 1 implements the foundational components without web UI or CLI.

### Components Implemented

#### 1. Task Classifier
Identifies the purpose of a prompt using pattern matching and optional LLM fallback.

**Supported Task Types:**
- Image Generation
- Video Generation
- Code Generation
- Code Review
- Code Debug
- SQL Query
- Research
- Story Writing
- Data Analysis
- Translation
- Summarization
- Question Answering
- Creative Writing
- Technical Writing
- General

**Example:**
```python
from better_prompt.core.classifier import TaskClassifier

classifier = TaskClassifier()
result = classifier.classify("Write a Python function to sort an array")

print(result.task_type)  # TaskType.CODE_GENERATION
print(result.confidence)  # 0.9
print(result.reasoning)  # "Classified as code_generation based on..."
```

#### 2. Format Selector
Recommends the best output format based on the target model and task type.

**Supported Formats:**
- JSON
- XML
- YAML
- Markdown
- Plain Text

**Example:**
```python
from better_prompt.core.format_selector import FormatSelector

selector = FormatSelector()
result = selector.recommend_format(
    model_name="gpt-4",
    provider="OpenAI"
)

print(result.recommended_format)  # OutputFormat.MARKDOWN
print(result.template_skeleton)   # Template structure
```

#### 3. Refinement Pipeline
Multi-stage prompt enhancement with modular functions.

**Refinement Stages:**
1. **Cleanup**: Remove noise, fix formatting
2. **Expand Constraints**: Add task-specific context
3. **Tone Adjustment**: Adjust to target tone (7 tone types)
4. **Token Optimization**: Reduce redundancy
5. **Apply Template**: Structure using format template
6. **Validate**: Ensure quality and completeness

**Example:**
```python
from better_prompt.core.refiner import RefinementPipeline, ToneType

pipeline = RefinementPipeline(target_tone=ToneType.PROFESSIONAL)
result = pipeline.refine(
    prompt="write code to sort array",
    task_type="code_generation"
)

print(result.refined_prompt)
print(result.improvements)
```

#### 4. Pipeline Orchestrator
Coordinates the entire workflow: classify → format_select → refine → validate

**Example:**
```python
from better_prompt.core.pipeline import PipelineOrchestrator

orchestrator = PipelineOrchestrator()
result = orchestrator.process(
    prompt="create a function that validates email addresses",
    model_name="gpt-4",
    provider="OpenAI",
    apply_template=True
)

print(result.get_summary())  # Human-readable summary
print(result.to_dict())      # Dictionary format
```

#### 5. LLM Gateway
Abstract interface for LLM provider interactions.

**Features:**
- Abstract base class for providers
- Message/Response dataclasses
- Factory pattern for provider registration
- Dummy provider for testing

**Example:**
```python
from better_prompt.core.llm_gateway import LLMProviderFactory
from better_prompt.core.llm_gateway.base import Message, MessageRole

# Create provider
provider = LLMProviderFactory.create_provider("dummy")

# Generate completion
messages = [
    Message(role=MessageRole.USER, content="Hello!")
]
response = provider.completion(model="dummy-gpt-4", messages=messages)
```

#### 6. Plugin System
Foundation for extensibility with manifest-based plugin loading.

**Features:**
- Plugin manifest (JSON-based)
- Plugin registry with discovery
- Support for 6 plugin types
- Enable/disable functionality

**Example:**
```python
from better_prompt.core.plugins import PluginRegistry, PluginManifest
from pathlib import Path

registry = PluginRegistry()
registry.add_plugin_directory(Path("./plugins"))
registry.discover_plugins()

# List plugins
for plugin in registry.list_plugins():
    print(plugin)
```

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- pip

### Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

## 💻 Usage

### Quick Start

```python
from better_prompt.core.pipeline import PipelineOrchestrator

# Create orchestrator
orchestrator = PipelineOrchestrator()

# Process a prompt
result = orchestrator.process(
    prompt="Write a function to calculate fibonacci numbers",
    model_name="gpt-4",
    provider="OpenAI"
)

# Print summary
print(result.get_summary())
```

### Batch Processing

```python
prompts = [
    "generate an image of a sunset",
    "write sql query to find top customers",
    "debug this python code",
]

results = orchestrator.process_batch(
    prompts=prompts,
    model_name="claude-3-opus",
    provider="Anthropic"
)

# Get statistics
stats = orchestrator.get_statistics(results)
print(stats)
```

### Custom Tone and Constraints

```python
from better_prompt.core.refiner import ToneType

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
```

## 🧪 Running Examples

```bash
# Run the demo script
python examples/demo.py
```

This will run 7 comprehensive examples demonstrating all features.

## 📊 Format Mapping

Better Prompt uses a curated mapping of models to their preferred formats:

| Provider | Model | Preferred Format |
|----------|-------|------------------|
| OpenAI | gpt-4, gpt-4o | Markdown |
| OpenAI | o1-research | JSON |
| Anthropic | claude-3-opus, claude-4-opus | XML |
| Google | gemini-pro | JSON |
| Google | gemini-ultra | YAML |
| Alibaba | qwen3-max | JSON |
| DeepSeek | deepseek-v3.1 | JSON |
| xAI | grok-4 | Markdown |

*See `better_prompt/core/resources/format_mapping.json` for complete mapping*

## 🔧 Configuration

### Task Classifier Configuration

```python
from better_prompt.core.classifier import TaskClassifier

classifier = TaskClassifier(
    llm_provider=None,  # Optional LLM for fallback
    confidence_threshold=0.7  # Minimum confidence before LLM fallback
)
```

### Format Selector Configuration

```python
from better_prompt.core.format_selector import FormatSelector

selector = FormatSelector(
    mapping_path="path/to/custom/mapping.json"  # Optional custom mapping
)
```

### Refinement Pipeline Configuration

```python
from better_prompt.core.refiner import RefinementPipeline, ToneType

pipeline = RefinementPipeline(
    target_tone=ToneType.PROFESSIONAL  # Default tone
)
```

## 🎨 Tone Types

Better Prompt supports 7 tone types:

- **PROFESSIONAL**: Formal, business-appropriate
- **CASUAL**: Relaxed, conversational
- **TECHNICAL**: Precise, implementation-focused
- **CREATIVE**: Imaginative, exploratory
- **FORMAL**: Very formal, academic
- **FRIENDLY**: Warm, approachable
- **NEUTRAL**: Balanced, objective

## 📈 Pipeline Result

The `PipelineResult` object contains:

```python
{
    "original_prompt": str,
    "refined_prompt": str,
    "task_classification": {
        "task_type": str,
        "confidence": float,
        "reasoning": str,
        "metadata": dict
    },
    "format_recommendation": {
        "format": str,
        "confidence": float,
        "explanation": str,
        "template_skeleton": str
    },
    "refinement": {
        "stages_applied": list,
        "improvements": list,
        "metadata": dict
    },
    "metadata": dict,
    "timestamp": str
}
```

## 🔌 Extending Better Prompt

### Creating a Custom Plugin

1. Create a plugin manifest (`manifest.json`):

```json
{
  "name": "my-custom-plugin",
  "version": "1.0.0",
  "plugin_type": "refiner",
  "description": "My custom refiner",
  "author": "Your Name",
  "entry_point": "my_plugin.refiner:CustomRefiner",
  "dependencies": [],
  "config": {},
  "enabled": true
}
```

2. Implement your plugin class
3. Register with the plugin registry

### Creating a Custom LLM Provider

```python
from better_prompt.core.llm_gateway import BaseLLMProvider, LLMResponse

class MyProvider(BaseLLMProvider):
    def completion(self, model, messages, **kwargs):
        # Implement completion logic
        return LLMResponse(...)
    
    def embeddings(self, model, texts, **kwargs):
        # Implement embeddings logic
        return EmbeddingResponse(...)
    
    def list_models(self):
        return ["my-model-1", "my-model-2"]

# Register provider
from better_prompt.core.llm_gateway import LLMProviderFactory
LLMProviderFactory.register_provider("myprovider", MyProvider)
```

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=better_prompt
```

## 📝 Development Roadmap

### ✅ Phase 1 - Core Engine (Current)
- [x] Task Classifier
- [x] Format Selector
- [x] Refinement Pipeline
- [x] Pipeline Orchestrator
- [x] LLM Gateway (Abstract)
- [x] Plugin System Foundation

### 🔄 Phase 2 - Interfaces (Future)
- [ ] FastAPI Server
- [ ] CLI with Typer
- [ ] Web UI (React)

### 🔄 Phase 3 - Integrations (Future)
- [ ] OpenAI Provider
- [ ] Anthropic Provider
- [ ] Google Provider
- [ ] LangChain Integration
- [ ] LangGraph Support

### 🔄 Phase 4 - Advanced Features (Future)
- [ ] Prompt Templates Library
- [ ] A/B Testing Framework
- [ ] Analytics Dashboard
- [ ] Prompt Version Control

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Format mapping curated from official model documentation
- Inspired by best practices in prompt engineering
- Built with modern Python best practices

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: [your-email@example.com]

---

**Better Prompt** - Transform your prompts, elevate your results. 🚀
