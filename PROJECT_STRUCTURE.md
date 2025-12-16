# Better Prompt - Project Structure

```
better-prompt/
│
├── .git/                           # Git repository
├── .github/                        # GitHub configuration
├── .gitignore                      # Git ignore rules
│
├── README.md                       # Main documentation
├── QUICKSTART.md                   # Quick start guide
├── PHASE1_SUMMARY.md               # Phase 1 implementation summary
├── pyproject.toml                  # Modern Python packaging
├── requirements.txt                # Project dependencies
│
├── mapping.json                    # Original format mapping (reference)
├── prompt.json                     # Example prompt file
├── prompt.xml                      # Example prompt file
├── Contraint.png                   # Reference image
│
├── better_prompt/                  # Main package
│   ├── __init__.py                 # Package initialization
│   │
│   └── core/                       # Core engine
│       ├── __init__.py             # Core module initialization
│       │
│       ├── classifier/             # Task Classification
│       │   ├── __init__.py         # Exports: TaskClassifier, TaskClassificationResult, TaskType
│       │   └── task_classifier.py  # Main classifier implementation
│       │
│       ├── format_selector/        # Format Selection
│       │   ├── __init__.py         # Exports: FormatSelector, FormatRecommendation, OutputFormat
│       │   └── format_selector.py  # Format selector implementation
│       │
│       ├── refiner/                # Refinement Pipeline
│       │   ├── __init__.py         # Exports: RefinementPipeline, RefinementResult, ToneType
│       │   └── pipeline.py         # Refinement pipeline implementation
│       │
│       ├── pipeline/               # Orchestration
│       │   ├── __init__.py         # Exports: PipelineOrchestrator, PipelineResult
│       │   └── orchestrator.py     # Pipeline orchestrator implementation
│       │
│       ├── plugins/                # Plugin System
│       │   ├── __init__.py         # Exports: PluginRegistry, PluginManifest, PluginType
│       │   ├── manifest.py         # Plugin manifest handling
│       │   └── registry.py         # Plugin registry implementation
│       │
│       ├── llm_gateway/            # LLM Gateway
│       │   ├── __init__.py         # Exports: BaseLLMProvider, LLMResponse, etc.
│       │   ├── base.py             # Abstract base classes
│       │   └── dummy_provider.py   # Dummy provider for testing
│       │
│       └── resources/              # Resources
│           └── format_mapping.json # Model-to-format mapping database
│
├── examples/                       # Example scripts
│   └── demo.py                     # Comprehensive demo (7 examples)
│
├── tests/                          # Test suite
│   └── test_core.py                # Core functionality tests (7 tests)
│
└── plugins/                        # External plugins directory (gitignored)
```

## File Count Summary

### Python Files
- **Core Modules**: 11 files
  - `better_prompt/__init__.py`
  - `better_prompt/core/__init__.py`
  - `better_prompt/core/classifier/__init__.py`
  - `better_prompt/core/classifier/task_classifier.py`
  - `better_prompt/core/format_selector/__init__.py`
  - `better_prompt/core/format_selector/format_selector.py`
  - `better_prompt/core/refiner/__init__.py`kw
  - `better_prompt/core/refiner/pipeline.py`
  - `better_prompt/core/pipeline/__init__.py`
  - `better_prompt/core/pipeline/orchestrator.py`
  - `better_prompt/core/plugins/__init__.py`
  - `better_prompt/core/plugins/manifest.py`
  - `better_prompt/core/plugins/registry.py`
  - `better_prompt/core/llm_gateway/__init__.py`
  - `better_prompt/core/llm_gateway/base.py`
  - `better_prompt/core/llm_gateway/dummy_provider.py`

- **Examples**: 1 file
  - `examples/demo.py`

- **Tests**: 1 file
  - `tests/test_core.py`

### Documentation Files
- `README.md` - Main documentation (12.7 KB)
- `QUICKSTART.md` - Quick start guide
- `PHASE1_SUMMARY.md` - Implementation summary

### Configuration Files
- `pyproject.toml` - Modern Python packaging
- `requirements.txt` - Dependencies
- `.gitignore` - Git ignore rules

### Resource Files
- `better_prompt/core/resources/format_mapping.json` - Format mapping database

## Total Statistics

- **Python Files**: 18
- **Documentation Files**: 3
- **Configuration Files**: 3
- **Resource Files**: 1
- **Total Lines of Code**: ~3,500+
- **Test Coverage**: 7/7 tests passing (100%)

## Module Dependencies

```
better_prompt
└── core
    ├── classifier (standalone)
    ├── format_selector (standalone)
    ├── refiner (standalone)
    ├── pipeline (depends on: classifier, format_selector, refiner)
    ├── plugins (standalone)
    └── llm_gateway (standalone)
```

## Import Paths

```python
# Task Classification
from better_prompt.core.classifier import TaskClassifier, TaskType

# Format Selection
from better_prompt.core.format_selector import FormatSelector, OutputFormat

# Refinement
from better_prompt.core.refiner import RefinementPipeline, ToneType

# Orchestration
from better_prompt.core.pipeline import PipelineOrchestrator

# Plugins
from better_prompt.core.plugins import PluginRegistry, PluginManifest, PluginType

# LLM Gateway
from better_prompt.core.llm_gateway import (
    BaseLLMProvider,
    LLMProviderFactory,
    DummyProvider,
    Message,
    MessageRole
)
```

## Key Features by Module

### classifier/
- 15+ task types
- Heuristic pattern matching
- Confidence scoring
- LLM fallback architecture

### format_selector/
- 37+ model mappings
- 5 output formats
- Template generation
- RAG-based recommendations

### refiner/
- 6-stage pipeline
- 7 tone types
- Token optimization
- Constraint expansion

### pipeline/
- End-to-end orchestration
- Batch processing
- Statistics tracking
- Result serialization

### plugins/
- Manifest loading
- Plugin discovery
- Registry management
- 6 plugin types

### llm_gateway/
- Provider abstraction
- Factory pattern
- Message handling
- Dummy provider for testing

---

**Status**: ✅ Phase 1 Complete  
**Test Status**: ✅ 7/7 Passing  
**Documentation**: ✅ Complete
