"""
Pipeline Orchestrator Module

This module orchestrates the entire Better Prompt pipeline:
classify → format_select → refine → validate
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from datetime import datetime

from ..classifier.task_classifier import TaskClassifier, TaskClassificationResult
from ..format_selector.format_selector import FormatSelector, FormatRecommendation, OutputFormat
from ..refiner.pipeline import RefinementPipeline, RefinementResult, ToneType


@dataclass
class PipelineResult:
    """
    Complete result from the Better Prompt pipeline.
    
    Attributes:
        original_prompt: The original input prompt
        refined_prompt: The final refined prompt
        task_classification: Result from task classification
        format_recommendation: Result from format selection
        refinement_result: Result from refinement pipeline
        metadata: Additional pipeline metadata
        timestamp: When the pipeline was executed
    """
    
    original_prompt: str
    refined_prompt: str
    task_classification: TaskClassificationResult
    format_recommendation: FormatRecommendation
    refinement_result: RefinementResult
    metadata: Dict[str, any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert result to dictionary format."""
        return {
            "original_prompt": self.original_prompt,
            "refined_prompt": self.refined_prompt,
            "task_classification": {
                "task_type": self.task_classification.task_type.value,
                "confidence": self.task_classification.confidence,
                "reasoning": self.task_classification.reasoning,
                "metadata": self.task_classification.metadata
            },
            "format_recommendation": {
                "format": self.format_recommendation.recommended_format.value,
                "confidence": self.format_recommendation.confidence,
                "explanation": self.format_recommendation.explanation,
                "metadata": self.format_recommendation.metadata
            },
            "refinement": {
                "stages_applied": self.refinement_result.stages_applied,
                "improvements": self.refinement_result.improvements,
                "metadata": self.refinement_result.metadata
            },
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the pipeline execution."""
        summary_lines = [
            "=" * 60,
            "BETTER PROMPT - Pipeline Summary",
            "=" * 60,
            "",
            f"Task Type: {self.task_classification.task_type.value}",
            f"Confidence: {self.task_classification.confidence:.2%}",
            "",
            f"Recommended Format: {self.format_recommendation.recommended_format.value}",
            f"Format Confidence: {self.format_recommendation.confidence:.2%}",
            "",
            "Improvements Made:",
        ]
        
        for improvement in self.refinement_result.improvements:
            summary_lines.append(f"  * {improvement}")  # Changed from •
        
        summary_lines.extend([
            "",
            "Refinement Stages:",
        ])
        
        for stage in self.refinement_result.stages_applied:
            summary_lines.append(f"  [x] {stage}")  # Changed from ✓
        
        summary_lines.extend([
            "",
            "=" * 60,
            "ORIGINAL PROMPT:",
            "-" * 60,
            self.original_prompt,
            "",
            "=" * 60,
            "REFINED PROMPT:",
            "-" * 60,
            self.refined_prompt,
            "=" * 60,
        ])
        
        return "\n".join(summary_lines)


class PipelineOrchestrator:
    """
    Orchestrates the complete Better Prompt pipeline.
    
    This class coordinates the task classification, format selection,
    and refinement stages to produce an optimized prompt.
    """
    
    def __init__(
        self,
        task_classifier: Optional[TaskClassifier] = None,
        format_selector: Optional[FormatSelector] = None,
        refinement_pipeline: Optional[RefinementPipeline] = None,
        default_tone: ToneType = ToneType.PROFESSIONAL
    ):
        """
        Initialize the pipeline orchestrator.
        
        Args:
            task_classifier: TaskClassifier instance (creates default if None)
            format_selector: FormatSelector instance (creates default if None)
            refinement_pipeline: RefinementPipeline instance (creates default if None)
            default_tone: Default tone for refinement
        """
        self.task_classifier = task_classifier or TaskClassifier()
        self.format_selector = format_selector or FormatSelector()
        self.refinement_pipeline = refinement_pipeline or RefinementPipeline(target_tone=default_tone)
        self.default_tone = default_tone
    
    def process(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        provider: Optional[str] = None,
        tone: Optional[ToneType] = None,
        custom_constraints: Optional[List[str]] = None,
        apply_template: bool = True,
        use_llm_classification: bool = False
    ) -> PipelineResult:
        """
        Process a prompt through the complete pipeline.
        
        Args:
            prompt: The original user prompt
            model_name: Target model name (e.g., "gpt-4", "claude-3-opus")
            provider: Provider name (e.g., "OpenAI", "Anthropic")
            tone: Desired tone for refinement (uses default if None)
            custom_constraints: Additional constraints to add
            apply_template: Whether to apply format template
            use_llm_classification: Whether to use LLM for task classification
            
        Returns:
            PipelineResult with complete pipeline output
        """
        # Stage 1: Task Classification
        task_classification = self.task_classifier.classify(
            prompt=prompt,
            use_llm_fallback=use_llm_classification
        )
        
        # Stage 2: Format Selection
        format_recommendation = self.format_selector.recommend_format(
            model_name=model_name,
            provider=provider,
            task_type=task_classification.task_type.value
        )
        
        # Stage 3: Refinement
        # Update tone if specified
        if tone and tone != self.refinement_pipeline.target_tone:
            self.refinement_pipeline = RefinementPipeline(target_tone=tone)
        
        # Get template if we should apply it
        template = None
        if apply_template:
            template = format_recommendation.template_skeleton
        
        refinement_result = self.refinement_pipeline.refine(
            prompt=prompt,
            task_type=task_classification.task_type.value,
            format_template=template,
            custom_constraints=custom_constraints
        )
        
        # Create pipeline result
        result = PipelineResult(
            original_prompt=prompt,
            refined_prompt=refinement_result.refined_prompt,
            task_classification=task_classification,
            format_recommendation=format_recommendation,
            refinement_result=refinement_result,
            metadata={
                "model_name": model_name,
                "provider": provider,
                "tone": (tone or self.default_tone).value,
                "template_applied": apply_template,
                "llm_classification_used": use_llm_classification
            }
        )
        
        return result
    
    def process_batch(
        self,
        prompts: List[str],
        model_name: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs
    ) -> List[PipelineResult]:
        """
        Process multiple prompts through the pipeline.
        
        Args:
            prompts: List of prompts to process
            model_name: Target model name
            provider: Provider name
            **kwargs: Additional arguments passed to process()
            
        Returns:
            List of PipelineResult objects
        """
        results = []
        for prompt in prompts:
            result = self.process(
                prompt=prompt,
                model_name=model_name,
                provider=provider,
                **kwargs
            )
            results.append(result)
        
        return results
    
    def get_statistics(self, results: List[PipelineResult]) -> Dict:
        """
        Get statistics from a batch of pipeline results.
        
        Args:
            results: List of PipelineResult objects
            
        Returns:
            Dictionary with statistics
        """
        if not results:
            return {}
        
        # Task type distribution
        task_types = {}
        for result in results:
            task_type = result.task_classification.task_type.value
            task_types[task_type] = task_types.get(task_type, 0) + 1
        
        # Format distribution
        formats = {}
        for result in results:
            format_type = result.format_recommendation.recommended_format.value
            formats[format_type] = formats.get(format_type, 0) + 1
        
        # Average confidences
        avg_task_confidence = sum(
            r.task_classification.confidence for r in results
        ) / len(results)
        
        avg_format_confidence = sum(
            r.format_recommendation.confidence for r in results
        ) / len(results)
        
        # Average improvements
        total_improvements = sum(
            len(r.refinement_result.improvements) for r in results
        )
        avg_improvements = total_improvements / len(results)
        
        return {
            "total_prompts": len(results),
            "task_type_distribution": task_types,
            "format_distribution": formats,
            "average_task_confidence": round(avg_task_confidence, 3),
            "average_format_confidence": round(avg_format_confidence, 3),
            "average_improvements_per_prompt": round(avg_improvements, 2),
            "total_improvements": total_improvements
        }
