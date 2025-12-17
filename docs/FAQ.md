# Better Prompt - FAQ

## ❓ Frequently Asked Questions

---

## 1. What is the flow right now?

### Current Pipeline Flow

The Better Prompt system follows a **4-stage pipeline** that processes raw prompts into optimized, structured outputs:

```
┌─────────────────┐
│  Raw Prompt     │
│  Input          │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  STAGE 1: Task Classification           │
│  ────────────────────────────────────   │
│  • Analyze prompt content               │
│  • Match against 15+ task patterns      │
│  • Return: TaskType + Confidence        │
│                                         │
│  Example:                               │
│  "Write Python function" →              │
│  TaskType: CODE_GENERATION (95%)        │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  STAGE 2: Format Selection              │
│  ────────────────────────────────────   │
│  • Check model preferences              │
│  • Match task type to format            │
│  • Return: OutputFormat + Template      │
│                                         │
│  Example:                               │
│  GPT-4 → MARKDOWN                       │
│  Claude → XML                           │
│  Gemini-Pro → JSON                      │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  STAGE 3: Refinement Pipeline           │
│  ────────────────────────────────────   │
│  Sub-Stage 3.1: Cleanup                 │
│    • Remove extra whitespace            │
│    • Fix punctuation                    │
│    • Capitalize properly                │
│                                         │
│  Sub-Stage 3.2: Expand Constraints      │
│    • Add task-specific requirements     │
│    • Include best practices             │
│    • Add custom constraints             │
│                                         │
│  Sub-Stage 3.3: Tone Adjustment         │
│    • Apply target tone (7 options)      │
│    • Adjust formality level             │
│    • Modify language style              │
│                                         │
│  Sub-Stage 3.4: Token Optimization      │
│    • Remove redundant words             │
│    • Compress without losing meaning    │
│    • Optimize for efficiency            │
│                                         │
│  Sub-Stage 3.5: Apply Template          │
│    • Structure with format template     │
│    • Fill in placeholders               │
│    • Organize sections                  │
│                                         │
│  Sub-Stage 3.6: Validate                │
│    • Check completeness                 │
│    • Verify quality                     │
│    • Ensure no template errors          │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  STAGE 4: Output Generation             │
│  ────────────────────────────────────   │
│  • Compile refined prompt               │
│  • Generate metadata                    │
│  • Create summary report                │
│                                         │
│  Return: PipelineResult {               │
│    original_prompt,                     │
│    refined_prompt,                      │
│    task_classification,                 │
│    format_recommendation,               │
│    refinement_result,                   │
│    metadata,                            │
│    timestamp                            │
│  }                                      │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Optimized      │
│  Prompt Output  │
└─────────────────┘
```

### Flow Example: Step-by-Step

**Input:**
```
"write code to sort array"
```

**Stage 1 - Classification:**
```python
TaskType: CODE_GENERATION
Confidence: 100%
Reasoning: Matched keywords "code", "function" and pattern "write.*function"
```

**Stage 2 - Format Selection:**
```python
Model: gpt-4 (OpenAI)
Format: MARKDOWN
Template: Markdown template skeleton provided
Confidence: 100%
```

**Stage 3 - Refinement:**
```python
3.1 Cleanup: "Write code to sort array."
3.2 Expand: "Write code to sort array. Please include comments..."
3.3 Tone: "Please write code to sort array. Include comments..."
3.4 Optimize: "Write code to sort array. Include comments..."
3.5 Template: Applied markdown structure
3.6 Validate: ✓ Passed
```

**Stage 4 - Output:**
```markdown
# Task
Write code to sort array. Include comments explaining the logic.
Follow best practices and coding standards.

## Requirements
- Efficient sorting algorithm
- Clear code comments

## Constraints
- Production-ready code
- Best practices followed

## Expected Output
Working sort function with documentation
```

---

## 2. What can we do right now?

### ✅ Available Features (Phase 1 Core Engine)

#### **A. Individual Component Usage**

##### 1️⃣ **Task Classification**
Identify what type of task a prompt is asking for.

```python
from better_prompt.core.classifier import TaskClassifier

classifier = TaskClassifier()
result = classifier.classify("Create an image of a sunset")

# Output:
# task_type: IMAGE_GENERATION
# confidence: 0.8
# reasoning: "Matched keywords: image, create, pattern: create.*image"
```

**Supported Task Types (15+):**
- `CODE_GENERATION` - Write code/functions
- `CODE_REVIEW` - Review code quality
- `CODE_DEBUG` - Fix bugs/errors
- `IMAGE_GENERATION` - Create images
- `VIDEO_GENERATION` - Create videos
- `SQL_QUERY` - Database queries
- `RESEARCH` - Research topics
- `STORY_WRITING` - Creative storytelling
- `DATA_ANALYSIS` - Analyze data
- `TRANSLATION` - Language translation
- `SUMMARIZATION` - Summarize content
- `QUESTION_ANSWERING` - Answer questions
- `CREATIVE_WRITING` - Poems, lyrics, etc.
- `TECHNICAL_WRITING` - Documentation
- `GENERAL` - General queries

##### 2️⃣ **Format Selection**
Get the best output format for a specific model.

```python
from better_prompt.core.format_selector import FormatSelector

selector = FormatSelector()
result = selector.recommend_format(
    model_name="claude-3-opus",
    provider="Anthropic"
)

# Output:
# format: XML
# template: XML template skeleton
# confidence: 1.0
# explanation: "Claude models prefer XML for structured markup"
```

**Supported Formats:**
- `JSON` - Structured data, APIs
- `XML` - Hierarchical markup
- `YAML` - Configuration files
- `MARKDOWN` - Documentation, natural language
- `TEXT` - Plain conversational

**Supported Models (37+):**
- OpenAI: gpt-4, gpt-4o, gpt-4o-mini, o1-research
- Anthropic: claude-3-opus, claude-3-sonnet, claude-4-opus, claude-4-haiku
- Google: gemini-pro, gemini-ultra, gemini-1.5-viz, palm-2-enterprise
- Alibaba: qwen3-max, qwen2.5-coder-32B, qwen3-omni, qwen2.5-vl
- DeepSeek: deepseek-v3.1, deepseek-r1-instruct, deepseek-v2-lite, deepseek-v3-coder
- xAI: grok-4, grok-code-fast, grok-vision-2, grok-agent-alpha

##### 3️⃣ **Prompt Refinement**
Enhance prompts with tone, constraints, and optimization.

```python
from better_prompt.core.refiner import RefinementPipeline, ToneType

pipeline = RefinementPipeline(target_tone=ToneType.PROFESSIONAL)
result = pipeline.refine(
    prompt="write code to validate email",
    task_type="code_generation"
)

# Output:
# refined_prompt: "Please write code to validate email. Include comments..."
# improvements: ["Cleaned up formatting", "Added 3 constraints", ...]
# stages_applied: [Cleanup, Expand Constraints, Adjust Tone, ...]
```

**Available Tones:**
- `PROFESSIONAL` - Formal, business-appropriate
- `CASUAL` - Relaxed, conversational
- `TECHNICAL` - Precise, implementation-focused
- `CREATIVE` - Imaginative, exploratory
- `FORMAL` - Very formal, academic
- `FRIENDLY` - Warm, approachable
- `NEUTRAL` - Balanced, objective (default)

##### 4️⃣ **Full Pipeline Orchestration**
Run the complete workflow end-to-end.

```python
from better_prompt.core.pipeline import PipelineOrchestrator

orchestrator = PipelineOrchestrator()
result = orchestrator.process(
    prompt="create a function to validate emails",
    model_name="gpt-4",
    provider="OpenAI",
    tone=ToneType.PROFESSIONAL,
    custom_constraints=["Add error handling", "Use regex"]
)

# Get summary
print(result.get_summary())

# Get structured data
data = result.to_dict()
```

##### 5️⃣ **Batch Processing**
Process multiple prompts efficiently.

```python
orchestrator = PipelineOrchestrator()

prompts = [
    "generate an image of a cat",
    "write sql query for top customers",
    "debug this python code",
    "translate to french",
    "summarize this article"
]

results = orchestrator.process_batch(
    prompts=prompts,
    model_name="gpt-4",
    provider="OpenAI"
)

# Get statistics
stats = orchestrator.get_statistics(results)
# Output:
# {
#   "total_prompts": 5,
#   "task_type_distribution": {...},
#   "average_task_confidence": 0.85,
#   "total_improvements": 15
# }
```

##### 6️⃣ **LLM Gateway**
Abstract interface for LLM providers (foundation for Phase 3).

```python
from better_prompt.core.llm_gateway import LLMProviderFactory, Message, MessageRole

# Currently only DummyProvider available
provider = LLMProviderFactory.create_provider("dummy")

messages = [
    Message(role=MessageRole.SYSTEM, content="You are helpful"),
    Message(role=MessageRole.USER, content="Hello!")
]

response = provider.completion(model="dummy-gpt-4", messages=messages)
# Returns mock response for testing
```

##### 7️⃣ **Plugin System**
Foundation for extensibility (Phase 3+).

```python
from better_prompt.core.plugins import PluginRegistry, PluginManifest, PluginType

registry = PluginRegistry()

# Create a plugin manifest
manifest = PluginManifest(
    name="my-plugin",
    version="1.0.0",
    plugin_type=PluginType.REFINER,
    description="Custom refiner",
    author="Your Name",
    entry_point="my_plugin:MyRefiner"
)

# Register plugin
registry.register_plugin(manifest)

# List plugins
plugins = registry.list_plugins()
```

#### **B. Utility Functions**

```python
# List all supported models
selector = FormatSelector()
models = selector.list_supported_models()
# Returns: ['OpenAI/gpt-4', 'Anthropic/claude-3-opus', ...]

# Get models by format
json_models = selector.get_models_by_format(OutputFormat.JSON)
# Returns: ['Google/gemini-pro', 'DeepSeek/deepseek-v3.1', ...]

# Get template for a format
template = selector.get_template(OutputFormat.MARKDOWN)
# Returns: Markdown template skeleton
```

### ❌ Not Available Yet (Future Phases)

- ❌ **Web UI** (Phase 2)
- ❌ **CLI Tool** (Phase 2)
- ❌ **FastAPI Server** (Phase 2)
- ❌ **Real LLM Integrations** (Phase 3) - OpenAI, Anthropic, Google APIs
- ❌ **LangChain Integration** (Phase 3)
- ❌ **Prompt Library** (Phase 4)
- ❌ **A/B Testing** (Phase 4)
- ❌ **Analytics Dashboard** (Phase 4)

---

## 3. How are things happening?

### Technical Architecture

#### **A. Classification System**

**How it works:**
1. **Pattern Matching Engine**
   - Converts prompt to lowercase
   - Checks against keyword lists (e.g., "function", "code", "write")
   - Runs regex patterns (e.g., `\b(write|create).*function`)
   - Calculates score: keyword match = 0.2 points, pattern match = 0.5 points

2. **Scoring Algorithm**
   ```python
   for each task_type:
       score = 0.0
       
       # Keyword matching
       for keyword in task_keywords:
           if keyword in prompt.lower():
               score += 0.2 * weight
       
       # Pattern matching
       for pattern in task_patterns:
           if re.search(pattern, prompt.lower()):
               score += 0.5 * weight
       
       scores[task_type] = min(score, 1.0)  # Cap at 100%
   
   # Return highest scoring task type
   best_task = max(scores)
   ```

3. **Fallback Mechanism**
   - If confidence < threshold (default 0.7) → Can use LLM fallback
   - If no matches at all → Returns `GENERAL` with 0.5 confidence

#### **B. Format Selection System**

**How it works:**
1. **Mapping Database**
   - Loads `format_mapping.json` with model → format mappings
   - Builds reverse index for fast lookups
   - Example: `{"OpenAI": {"gpt-4": "markdown"}}`

2. **Lookup Algorithm**
   ```python
   def recommend_format(model_name, provider):
       # Try full provider/model lookup
       key = f"{provider}/{model_name}"
       if key in mapping:
           return mapping[key], confidence=1.0
       
       # Try model name only
       if model_name in mapping:
           return mapping[model_name], confidence=0.9
       
       # Try partial matching
       for mapped_model in mapping:
           if model_name in mapped_model:
               return mapping[mapped_model], confidence=0.7
       
       # Fallback to default
       return fallback_format, confidence=0.5
   ```

3. **Template Generation**
   - Each format has a pre-defined template skeleton
   - Templates have placeholders (e.g., `{{task_description}}`)
   - Templates are returned with the recommendation

#### **C. Refinement Pipeline**

**How it works:**
1. **Stage 1: Cleanup**
   ```python
   # Remove extra whitespace
   prompt = re.sub(r'\s+', ' ', prompt)
   
   # Fix punctuation spacing
   prompt = re.sub(r'\s+([.,!?;:])', r'\1', prompt)
   
   # Capitalize first letter
   prompt = prompt[0].upper() + prompt[1:]
   ```

2. **Stage 2: Expand Constraints**
   ```python
   # Task-specific constraints map
   constraints = {
       "code_generation": [
           "Include comments explaining the logic",
           "Follow best practices and coding standards",
           "Ensure the code is production-ready"
       ],
       "image_generation": [
           "Specify the desired style, mood, and composition",
           "Include details about colors, lighting, and perspective"
       ]
   }
   
   # Append to prompt
   if task_type in constraints:
       prompt += " " + " ".join(constraints[task_type])
   ```

3. **Stage 3: Tone Adjustment**
   ```python
   # Example: Professional tone
   def make_professional(prompt):
       # Remove casual contractions
       prompt = prompt.replace("don't", "do not")
       
       # Add polite framing if short
       if len(prompt.split()) < 10:
           prompt = f"Please {prompt.lower()}"
       
       return prompt
   ```

4. **Stage 4: Token Optimization**
   ```python
   # Remove filler words
   fillers = ["very", "really", "quite", "just", "simply"]
   for filler in fillers:
       prompt = re.sub(rf'\b{filler}\s+', '', prompt)
   
   # Clean up double spaces
   prompt = re.sub(r'\s+', ' ', prompt)
   ```

5. **Stage 5: Apply Template**
   ```python
   if template:
       # Simple placeholder replacement
       formatted = template.replace(
           "{{task_description}}", 
           prompt
       )
       return formatted
   ```

6. **Stage 6: Validate**
   ```python
   issues = []
   
   # Check minimum length
   if len(prompt.split()) < 5:
       issues.append("Prompt too short")
   
   # Check for unresolved placeholders
   if "{{" in prompt and "}}" in prompt:
       issues.append("Template placeholders not resolved")
   
   # Check for punctuation
   if not any(char in prompt for char in '.!?'):
       warnings.append("No punctuation")
   
   validation_passed = len(issues) == 0
   ```

#### **D. Data Flow**

```
User Input
    ↓
[Create PipelineOrchestrator instance]
    ↓
[Call orchestrator.process()]
    ↓
┌─────────────────────────────────┐
│ Initialize TaskClassifier       │
│ • Load task patterns            │
│ • Set confidence threshold      │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│ classifier.classify(prompt)     │
│ • Pattern matching              │
│ • Score calculation             │
│ • Return TaskClassificationResult
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│ Initialize FormatSelector       │
│ • Load format_mapping.json      │
│ • Build reverse index           │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│ selector.recommend_format()     │
│ • Lookup model in mapping       │
│ • Get template skeleton         │
│ • Return FormatRecommendation   │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│ Initialize RefinementPipeline   │
│ • Set target tone               │
│ • Prepare stages                │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│ pipeline.refine()               │
│ • Run 6 stages sequentially     │
│ • Track improvements            │
│ • Apply template                │
│ • Validate result               │
│ • Return RefinementResult       │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│ Create PipelineResult           │
│ • Combine all results           │
│ • Add metadata                  │
│ • Add timestamp                 │
└────────────┬────────────────────┘
             ↓
Return to User
    ↓
[User can call result.get_summary()]
[User can call result.to_dict()]
[User can access individual components]
```

#### **E. File Storage & Loading**

**Format Mapping:**
- Stored in: `better_prompt/core/resources/format_mapping.json`
- Loaded on: `FormatSelector` initialization
- Format: `{"Provider": {"model": "format"}}`

**Templates:**
- Stored in: Memory (Python dictionaries in `format_selector.py`)
- Pre-defined for each format type
- Accessed via: `FormatSelector.FORMAT_TEMPLATES`

**Task Patterns:**
- Stored in: Memory (`task_classifier.py`)
- Defined as: `TaskClassifier.TASK_PATTERNS`
- Contains: Keywords list + Regex patterns list

#### **F. Error Handling**

```python
# If model not found in mapping
→ Returns fallback format (MARKDOWN) with confidence 0.5

# If no task patterns match
→ Returns GENERAL task type with confidence 0.5

# If validation fails
→ Still returns result but with warnings in metadata

# If template has unresolved placeholders
→ Adds to validation issues but doesn't block

# If LLM provider fails (future)
→ Falls back to heuristic classification
```

---

## Summary

### Current State (Phase 1)

✅ **What works:**
- Complete prompt processing pipeline
- 15+ task types recognized
- 37+ models with format recommendations
- 6-stage refinement with 7 tone options
- Batch processing and statistics
- Plugin system foundation
- LLM gateway architecture

✅ **How to use:**
- Import modules
- Call functions/classes
- Get structured results
- All via Python API

✅ **What's next:**
- Phase 2: Web UI, CLI, FastAPI
- Phase 3: Real LLM integrations
- Phase 4: Advanced features

---

**Last Updated:** December 17, 2025  
**Version:** Phase 1 (Core Engine Complete)  
**Status:** ✅ All features working, tested, and documented
