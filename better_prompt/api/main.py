"""
Better Prompt API - Main Application

FastAPI REST API for the Better Prompt engine.
Provides endpoints for prompt refinement, model selection, and plugin management.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
import logging
from datetime import datetime

from ..core.pipeline import PipelineOrchestrator
from ..core.classifier import TaskClassifier, TaskType
from ..core.format_selector import FormatSelector, OutputFormat
from ..core.refiner import ToneType
from ..core.plugins import PluginRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Pydantic Models (Request/Response schemas)
# ============================================================================

class ToneEnum(str, Enum):
    """Tone options for prompt refinement."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    FORMAL = "formal"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"


class FormatEnum(str, Enum):
    """Output format options."""
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    MARKDOWN = "markdown"
    TEXT = "text"


class ProcessPromptRequest(BaseModel):
    """Request model for prompt processing."""
    prompt: str = Field(..., description="The prompt to process and refine", min_length=1)
    model_name: Optional[str] = Field(None, description="Target LLM model (e.g., gpt-4, claude-3-opus)")
    provider: Optional[str] = Field(None, description="Model provider (e.g., OpenAI, Anthropic)")
    tone: Optional[ToneEnum] = Field(ToneEnum.PROFESSIONAL, description="Desired tone for the prompt")
    custom_constraints: Optional[List[str]] = Field(None, description="Additional constraints to add")
    apply_template: bool = Field(True, description="Whether to apply format template")
    plugins: Optional[List[str]] = Field(None, description="Plugin names to apply (future use)")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Write a Python function to validate email addresses",
                "model_name": "gpt-4",
                "provider": "OpenAI",
                "tone": "professional",
                "custom_constraints": ["Use regex", "Add error handling"],
                "apply_template": True
            }
        }


class BatchProcessRequest(BaseModel):
    """Request model for batch processing."""
    prompts: List[str] = Field(..., description="List of prompts to process", min_items=1)
    model_name: Optional[str] = Field(None, description="Target LLM model for all prompts")
    provider: Optional[str] = Field(None, description="Model provider for all prompts")
    tone: Optional[ToneEnum] = Field(ToneEnum.PROFESSIONAL, description="Tone for all prompts")

    class Config:
        json_schema_extra = {
            "example": {
                "prompts": [
                    "Write a Python function",
                    "Create an image of a sunset",
                    "Translate to Spanish"
                ],
                "model_name": "gpt-4",
                "provider": "OpenAI"
            }
        }


class ClassifyRequest(BaseModel):
    """Request model for task classification."""
    prompt: str = Field(..., description="The prompt to classify", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Write a Python function to sort an array"
            }
        }


class FormatRecommendationRequest(BaseModel):
    """Request model for format recommendation."""
    model_name: Optional[str] = Field(None, description="Target model name")
    provider: Optional[str] = Field(None, description="Model provider")
    task_type: Optional[str] = Field(None, description="Type of task")

    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "gpt-4",
                "provider": "OpenAI"
            }
        }


class ProcessPromptResponse(BaseModel):
    """Response model for prompt processing."""
    success: bool
    original_prompt: str
    refined_prompt: str
    task_type: str
    task_confidence: float
    recommended_format: str
    format_confidence: float
    improvements: List[str]
    stages_applied: List[str]
    metadata: Dict[str, Any]
    timestamp: str


class BatchProcessResponse(BaseModel):
    """Response model for batch processing."""
    success: bool
    total_prompts: int
    results: List[ProcessPromptResponse]
    statistics: Dict[str, Any]


class ClassifyResponse(BaseModel):
    """Response model for task classification."""
    success: bool
    task_type: str
    confidence: float
    reasoning: str
    metadata: Dict[str, Any]


class FormatRecommendationResponse(BaseModel):
    """Response model for format recommendation."""
    success: bool
    recommended_format: str
    confidence: float
    explanation: str
    template_skeleton: str


class ModelInfo(BaseModel):
    """Model information."""
    provider: str
    model: str
    preferred_format: str


class PluginInfo(BaseModel):
    """Plugin information."""
    name: str
    version: str
    plugin_type: str
    description: str
    enabled: bool


class SystemInfoResponse(BaseModel):
    """System information response."""
    version: str
    task_types: int
    supported_models: int
    output_formats: int
    tone_options: int
    plugins_loaded: int
    components: List[str]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    version: str


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: str


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Better Prompt API",
    description="REST API for prompt refinement and optimization",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware for Next.js integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
orchestrator = PipelineOrchestrator()
classifier = TaskClassifier()
format_selector = FormatSelector()
plugin_registry = PluginRegistry()


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )


# ============================================================================
# Health & Info Endpoints
# ============================================================================

@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root():
    """Root endpoint - health check."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="0.1.0"
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="0.1.0"
    )


@app.get("/info", response_model=SystemInfoResponse, tags=["System"])
async def system_info():
    """Get system information."""
    return SystemInfoResponse(
        version="0.1.0",
        task_types=15,
        supported_models=len(format_selector.list_supported_models()),
        output_formats=5,
        tone_options=7,
        plugins_loaded=len(plugin_registry.list_plugins()),
        components=[
            "Task Classifier",
            "Format Selector",
            "Refinement Pipeline",
            "Pipeline Orchestrator",
            "Plugin System",
            "LLM Gateway"
        ]
    )


# ============================================================================
# Core Processing Endpoints
# ============================================================================

@app.post("/api/v1/process", response_model=ProcessPromptResponse, tags=["Processing"])
async def process_prompt(request: ProcessPromptRequest):
    """
    Process and refine a single prompt.
    
    This endpoint takes a prompt and applies the full Better Prompt pipeline:
    - Task classification
    - Format selection
    - Prompt refinement
    - Template application
    
    Returns the refined prompt with metadata.
    """
    try:
        # Convert tone enum to ToneType
        tone_type = ToneType(request.tone.value) if request.tone else ToneType.PROFESSIONAL
        
        # Process the prompt
        result = orchestrator.process(
            prompt=request.prompt,
            model_name=request.model_name,
            provider=request.provider,
            tone=tone_type,
            custom_constraints=request.custom_constraints,
            apply_template=request.apply_template
        )
        
        return ProcessPromptResponse(
            success=True,
            original_prompt=result.original_prompt,
            refined_prompt=result.refined_prompt,
            task_type=result.task_classification.task_type.value,
            task_confidence=result.task_classification.confidence,
            recommended_format=result.format_recommendation.recommended_format.value,
            format_confidence=result.format_recommendation.confidence,
            improvements=result.refinement_result.improvements,
            stages_applied=result.refinement_result.stages_applied,
            metadata=result.metadata,
            timestamp=result.timestamp
        )
    
    except Exception as e:
        logger.error(f"Error processing prompt: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing prompt: {str(e)}"
        )


@app.post("/api/v1/batch", response_model=BatchProcessResponse, tags=["Processing"])
async def batch_process(request: BatchProcessRequest):
    """
    Process multiple prompts in batch.
    
    Efficiently processes multiple prompts and returns statistics.
    """
    try:
        # Convert tone enum to ToneType
        tone_type = ToneType(request.tone.value) if request.tone else ToneType.PROFESSIONAL
        
        # Process batch
        results = orchestrator.process_batch(
            prompts=request.prompts,
            model_name=request.model_name,
            provider=request.provider,
            tone=tone_type
        )
        
        # Get statistics
        stats = orchestrator.get_statistics(results)
        
        # Convert results to response format
        response_results = []
        for result in results:
            response_results.append(ProcessPromptResponse(
                success=True,
                original_prompt=result.original_prompt,
                refined_prompt=result.refined_prompt,
                task_type=result.task_classification.task_type.value,
                task_confidence=result.task_classification.confidence,
                recommended_format=result.format_recommendation.recommended_format.value,
                format_confidence=result.format_recommendation.confidence,
                improvements=result.refinement_result.improvements,
                stages_applied=result.refinement_result.stages_applied,
                metadata=result.metadata,
                timestamp=result.timestamp
            ))
        
        return BatchProcessResponse(
            success=True,
            total_prompts=len(request.prompts),
            results=response_results,
            statistics=stats
        )
    
    except Exception as e:
        logger.error(f"Error in batch processing: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch processing: {str(e)}"
        )


@app.post("/api/v1/classify", response_model=ClassifyResponse, tags=["Analysis"])
async def classify_prompt(request: ClassifyRequest):
    """
    Classify a prompt to identify its task type.
    
    Returns the detected task type with confidence score.
    """
    try:
        result = classifier.classify(request.prompt)
        
        return ClassifyResponse(
            success=True,
            task_type=result.task_type.value,
            confidence=result.confidence,
            reasoning=result.reasoning,
            metadata=result.metadata
        )
    
    except Exception as e:
        logger.error(f"Error classifying prompt: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error classifying prompt: {str(e)}"
        )


@app.post("/api/v1/format/recommend", response_model=FormatRecommendationResponse, tags=["Analysis"])
async def recommend_format(request: FormatRecommendationRequest):
    """
    Get format recommendation for a model.
    
    Returns the recommended output format with template.
    """
    try:
        result = format_selector.recommend_format(
            model_name=request.model_name,
            provider=request.provider,
            task_type=request.task_type
        )
        
        return FormatRecommendationResponse(
            success=True,
            recommended_format=result.recommended_format.value,
            confidence=result.confidence,
            explanation=result.explanation,
            template_skeleton=result.template_skeleton
        )
    
    except Exception as e:
        logger.error(f"Error recommending format: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recommending format: {str(e)}"
        )


# ============================================================================
# Model & Provider Endpoints
# ============================================================================

@app.get("/api/v1/models", response_model=List[ModelInfo], tags=["Models"])
async def list_models(
    provider: Optional[str] = None,
    format: Optional[FormatEnum] = None
):
    """
    List all supported models.
    
    Optional filters:
    - provider: Filter by provider name
    - format: Filter by preferred format
    """
    try:
        models = format_selector.list_supported_models()
        
        # Filter by provider if specified
        if provider:
            models = [m for m in models if m.lower().startswith(provider.lower())]
        
        # Filter by format if specified
        if format:
            format_type = OutputFormat(format.value)
            models = format_selector.get_models_by_format(format_type)
        
        # Convert to response format
        result = []
        for model_path in models:
            provider_name, model_name = model_path.split("/")
            rec = format_selector.recommend_format(model_name=model_name, provider=provider_name)
            
            result.append(ModelInfo(
                provider=provider_name,
                model=model_name,
                preferred_format=rec.recommended_format.value
            ))
        
        return result
    
    except Exception as e:
        logger.error(f"Error listing models: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing models: {str(e)}"
        )


@app.get("/api/v1/providers", response_model=List[str], tags=["Models"])
async def list_providers():
    """List all supported providers."""
    try:
        providers = set()
        for model_path in format_selector.list_supported_models():
            provider, _ = model_path.split("/")
            providers.add(provider)
        
        return sorted(list(providers))
    
    except Exception as e:
        logger.error(f"Error listing providers: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing providers: {str(e)}"
        )


# ============================================================================
# Plugin Endpoints (Future Use)
# ============================================================================

@app.get("/api/v1/plugins", response_model=List[PluginInfo], tags=["Plugins"])
async def list_plugins():
    """
    List all available plugins.
    
    Note: Plugin system is ready for future LLM integrations.
    """
    try:
        plugins = plugin_registry.list_plugins()
        
        result = []
        for plugin in plugins:
            result.append(PluginInfo(
                name=plugin.name,
                version=plugin.version,
                plugin_type=plugin.plugin_type.value,
                description=plugin.description or "",
                enabled=plugin.enabled
            ))
        
        return result
    
    except Exception as e:
        logger.error(f"Error listing plugins: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing plugins: {str(e)}"
        )


@app.post("/api/v1/plugins/{plugin_name}/enable", tags=["Plugins"])
async def enable_plugin(plugin_name: str):
    """Enable a plugin."""
    try:
        success = plugin_registry.enable_plugin(plugin_name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plugin '{plugin_name}' not found"
            )
        
        return {"success": True, "message": f"Plugin '{plugin_name}' enabled"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling plugin: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enabling plugin: {str(e)}"
        )


@app.post("/api/v1/plugins/{plugin_name}/disable", tags=["Plugins"])
async def disable_plugin(plugin_name: str):
    """Disable a plugin."""
    try:
        success = plugin_registry.disable_plugin(plugin_name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plugin '{plugin_name}' not found"
            )
        
        return {"success": True, "message": f"Plugin '{plugin_name}' disabled"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling plugin: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error disabling plugin: {str(e)}"
        )


# ============================================================================
# Utility Endpoints
# ============================================================================

@app.get("/api/v1/tones", response_model=List[str], tags=["Utilities"])
async def list_tones():
    """List all available tone options."""
    return [tone.value for tone in ToneType]


@app.get("/api/v1/formats", response_model=List[str], tags=["Utilities"])
async def list_formats():
    """List all available output formats."""
    return [fmt.value for fmt in OutputFormat]


@app.get("/api/v1/task-types", response_model=List[str], tags=["Utilities"])
async def list_task_types():
    """List all supported task types."""
    return [task.value for task in TaskType]


# ============================================================================
# Main entry point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
