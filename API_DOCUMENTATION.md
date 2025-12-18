# Better Prompt API - Documentation

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install fastapi uvicorn[standard]

# Or install all requirements
pip install -r requirements.txt
```

### Run the API

```bash
# Basic
python run_api.py

# With auto-reload (development)
python run_api.py --reload

# Custom host/port
python run_api.py --host 127.0.0.1 --port 3000
```

### Access Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 📋 API Endpoints

### Health & System

#### `GET /`
Root endpoint - health check.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-17T18:00:00.000Z",
  "version": "0.1.0"
}
```

#### `GET /health`
Health check endpoint.

#### `GET /info`
Get system information.

**Response:**
```json
{
  "version": "0.1.0",
  "task_types": 15,
  "supported_models": 37,
  "output_formats": 5,
  "tone_options": 7,
  "plugins_loaded": 0,
  "components": [
    "Task Classifier",
    "Format Selector",
    "Refinement Pipeline",
    "Pipeline Orchestrator",
    "Plugin System",
    "LLM Gateway"
  ]
}
```

---

### Core Processing

#### `POST /api/v1/process`
Process and refine a single prompt.

**Request:**
```json
{
  "prompt": "Write a Python function to validate email addresses",
  "model_name": "gpt-4",
  "provider": "OpenAI",
  "tone": "professional",
  "custom_constraints": ["Use regex", "Add error handling"],
  "apply_template": true
}
```

**Response:**
```json
{
  "success": true,
  "original_prompt": "Write a Python function to validate email addresses",
  "refined_prompt": "# Task\nPlease write a python function to validate email addresses\n\n## Requirements\n- Efficient and optimized implementation\n- Clear code comments and documentation\n- Error handling and edge cases covered\n\n## Constraints\n- Please include comments explaining the logic.\n- Follow best practices and coding standards.\n- Ensure the code is production-ready.\n- Use regex\n- Add error handling\n\n## Expected Output\nWorking, well-documented code that meets all requirements",
  "task_type": "code_generation",
  "task_confidence": 1.0,
  "recommended_format": "markdown",
  "format_confidence": 1.0,
  "improvements": [
    "Prepared 5 constraint(s) for template",
    "Adjusted tone to professional",
    "Applied format template for structure",
    "Validation passed - prompt is well-formed"
  ],
  "stages_applied": [
    "Cleanup",
    "Expand Constraints",
    "Adjust Tone",
    "Optimize Tokens",
    "Apply Template",
    "Validate"
  ],
  "metadata": {
    "model_name": "gpt-4",
    "provider": "OpenAI",
    "tone": "professional",
    "template_applied": true
  },
  "timestamp": "2025-12-17T18:00:00.000Z"
}
```

#### `POST /api/v1/batch`
Process multiple prompts in batch.

**Request:**
```json
{
  "prompts": [
    "Write a Python function",
    "Create an image of a sunset",
    "Translate to Spanish"
  ],
  "model_name": "gpt-4",
  "provider": "OpenAI",
  "tone": "professional"
}
```

**Response:**
```json
{
  "success": true,
  "total_prompts": 3,
  "results": [
    {
      "success": true,
      "original_prompt": "Write a Python function",
      "refined_prompt": "...",
      "task_type": "code_generation",
      "task_confidence": 1.0,
      ...
    }
  ],
  "statistics": {
    "total_prompts": 3,
    "task_type_distribution": {
      "code_generation": 1,
      "image_generation": 1,
      "translation": 1
    },
    "format_distribution": {
      "markdown": 3
    },
    "average_task_confidence": 0.85,
    "average_format_confidence": 1.0,
    "total_improvements": 12
  }
}
```

---

### Analysis

#### `POST /api/v1/classify`
Classify a prompt to identify its task type.

**Request:**
```json
{
  "prompt": "Write a Python function to sort an array"
}
```

**Response:**
```json
{
  "success": true,
  "task_type": "code_generation",
  "confidence": 1.0,
  "reasoning": "Classified as code_generation based on heuristic analysis. Matched: keyword: function, keyword: python, pattern: \\b(write|create|generate|implement)\\s+.*\\s+(function|class|script|program|code)",
  "metadata": {
    "method": "heuristic",
    "matches": ["keyword: function", "keyword: python"],
    "all_scores": {
      "code_generation": 1.0
    }
  }
}
```

#### `POST /api/v1/format/recommend`
Get format recommendation for a model.

**Request:**
```json
{
  "model_name": "gpt-4",
  "provider": "OpenAI"
}
```

**Response:**
```json
{
  "success": true,
  "recommended_format": "markdown",
  "confidence": 1.0,
  "explanation": "Based on format mapping, OpenAI gpt-4 prefers markdown. Markdown format is excellent for natural language tasks, documentation, and models trained on web content.",
  "template_skeleton": "# Task\n{{task_description}}\n\n## Requirements\n- {{requirement_1}}\n- {{requirement_2}}\n\n## Constraints\n{{constraints_list}}\n\n## Expected Output\n{{output_description}}"
}
```

---

### Models & Providers

#### `GET /api/v1/models`
List all supported models.

**Query Parameters:**
- `provider` (optional): Filter by provider
- `format` (optional): Filter by preferred format

**Response:**
```json
[
  {
    "provider": "OpenAI",
    "model": "gpt-4",
    "preferred_format": "markdown"
  },
  {
    "provider": "OpenAI",
    "model": "gpt-4o",
    "preferred_format": "markdown"
  },
  {
    "provider": "Anthropic",
    "model": "claude-3-opus",
    "preferred_format": "xml"
  }
]
```

#### `GET /api/v1/providers`
List all supported providers.

**Response:**
```json
[
  "Alibaba",
  "Anthropic",
  "DeepSeek",
  "Google",
  "OpenAI",
  "xAI"
]
```

---

### Plugins (Future Use)

#### `GET /api/v1/plugins`
List all available plugins.

**Response:**
```json
[
  {
    "name": "openai-provider",
    "version": "1.0.0",
    "plugin_type": "llm_provider",
    "description": "OpenAI LLM provider integration",
    "enabled": true
  }
]
```

#### `POST /api/v1/plugins/{plugin_name}/enable`
Enable a plugin.

#### `POST /api/v1/plugins/{plugin_name}/disable`
Disable a plugin.

---

### Utilities

#### `GET /api/v1/tones`
List all available tone options.

**Response:**
```json
[
  "professional",
  "casual",
  "technical",
  "creative",
  "formal",
  "friendly",
  "neutral"
]
```

#### `GET /api/v1/formats`
List all available output formats.

**Response:**
```json
[
  "json",
  "xml",
  "yaml",
  "markdown",
  "text"
]
```

#### `GET /api/v1/task-types`
List all supported task types.

**Response:**
```json
[
  "image_generation",
  "video_generation",
  "code_generation",
  "code_review",
  "code_debug",
  "research",
  "story_writing",
  "sql_query",
  "chatbot",
  "data_analysis",
  "translation",
  "summarization",
  "question_answering",
  "creative_writing",
  "technical_writing",
  "general"
]
```

---

## 🔧 Integration Examples

### Next.js Integration

```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function processPrompt(data: {
  prompt: string;
  model_name?: string;
  provider?: string;
  tone?: string;
  custom_constraints?: string[];
  apply_template?: boolean;
}) {
  const response = await fetch(`${API_BASE_URL}/api/v1/process`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Failed to process prompt');
  }

  return response.json();
}

export async function listModels(provider?: string) {
  const url = new URL(`${API_BASE_URL}/api/v1/models`);
  if (provider) {
    url.searchParams.append('provider', provider);
  }

  const response = await fetch(url.toString());
  return response.json();
}

export async function classifyPrompt(prompt: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/classify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt }),
  });

  return response.json();
}
```

### React Component Example

```tsx
// components/PromptRefiner.tsx
import { useState } from 'react';
import { processPrompt } from '@/lib/api';

export default function PromptRefiner() {
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const data = await processPrompt({
        prompt,
        model_name: 'gpt-4',
        provider: 'OpenAI',
        tone: 'professional',
        apply_template: true,
      });
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your prompt..."
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Refine Prompt'}
        </button>
      </form>

      {result && (
        <div>
          <h3>Refined Prompt:</h3>
          <pre>{result.refined_prompt}</pre>
          
          <h4>Improvements:</h4>
          <ul>
            {result.improvements.map((imp, i) => (
              <li key={i}>{imp}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

---

## 🔐 CORS Configuration

The API is configured with permissive CORS for development:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**For production**, update to specific origins:

```python
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

---

## 📊 Response Format

All endpoints return JSON with consistent structure:

**Success Response:**
```json
{
  "success": true,
  ...data
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message",
  "detail": "Detailed error information",
  "timestamp": "2025-12-17T18:00:00.000Z"
}
```

---

## 🚀 Deployment

### Docker (Future)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "better_prompt.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```bash
# .env
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=info
```

---

## 📝 Testing

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Process prompt
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function",
    "model_name": "gpt-4",
    "provider": "OpenAI"
  }'

# List models
curl http://localhost:8000/api/v1/models?provider=OpenAI
```

### Using Python requests

```python
import requests

# Process prompt
response = requests.post(
    "http://localhost:8000/api/v1/process",
    json={
        "prompt": "Write a Python function to validate emails",
        "model_name": "gpt-4",
        "provider": "OpenAI",
        "tone": "professional"
    }
)

result = response.json()
print(result["refined_prompt"])
```

---

## 🎯 Future Endpoints (Planned)

### LLM Integration
- `POST /api/v1/llm/complete` - Direct LLM completion
- `POST /api/v1/llm/chat` - Chat completion
- `GET /api/v1/llm/models` - List available LLM models

### Plugin Management
- `POST /api/v1/plugins/install` - Install plugin
- `DELETE /api/v1/plugins/{name}` - Uninstall plugin
- `GET /api/v1/plugins/{name}/config` - Get plugin config

### Analytics
- `GET /api/v1/analytics/usage` - Usage statistics
- `GET /api/v1/analytics/popular-models` - Popular models
- `GET /api/v1/analytics/task-distribution` - Task distribution

---

**Better Prompt API** - Ready for Next.js integration! 🚀
