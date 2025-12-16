"""
Task Classification Module

This module provides hybrid task classification using heuristics and optional LLM fallback.
It identifies the purpose and intent of a user's prompt.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, List
import re


class TaskType(Enum):
    """Enumeration of supported task types."""
    
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    CODE_DEBUG = "code_debug"
    RESEARCH = "research"
    STORY_WRITING = "story_writing"
    SQL_QUERY = "sql_query"
    CHATBOT = "chatbot"
    DATA_ANALYSIS = "data_analysis"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
    CREATIVE_WRITING = "creative_writing"
    TECHNICAL_WRITING = "technical_writing"
    GENERAL = "general"


@dataclass
class TaskClassificationResult:
    """
    Result of task classification.
    
    Attributes:
        task_type: The identified task type
        confidence: Confidence score (0.0 to 1.0)
        reasoning: Explanation of why this classification was chosen
        metadata: Additional metadata about the classification
    """
    
    task_type: TaskType
    confidence: float
    reasoning: str
    metadata: Dict[str, any] = None
    
    def __post_init__(self) -> None:
        """Validate confidence score."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        if self.metadata is None:
            self.metadata = {}


class TaskClassifier:
    """
    Hybrid task classifier using heuristics and optional LLM fallback.
    
    The classifier uses pattern matching and keyword analysis to identify
    the purpose of a prompt. If confidence is low, it can optionally
    fall back to an LLM for classification.
    """
    
    # Keyword patterns for each task type
    TASK_PATTERNS: Dict[TaskType, Dict[str, any]] = {
        TaskType.IMAGE_GENERATION: {
            "keywords": [
                "image", "picture", "photo", "illustration", "draw", "paint",
                "visualize", "render", "generate image", "create image", "design"
            ],
            "patterns": [
                r"\b(create|generate|make|draw|paint)\s+(an?\s+)?(image|picture|photo|illustration)",
                r"\bvisuali[sz]e\b",
                r"\brender\s+(an?\s+)?(image|scene|3d)",
            ],
            "weight": 1.0
        },
        TaskType.VIDEO_GENERATION: {
            "keywords": [
                "video", "animation", "movie", "clip", "footage", "animate",
                "motion", "sequence", "frames"
            ],
            "patterns": [
                r"\b(create|generate|make|produce)\s+(an?\s+)?(video|animation|movie|clip)",
                r"\banimate\b",
                r"\bmotion\s+(graphics|design)",
            ],
            "weight": 1.0
        },
        TaskType.CODE_GENERATION: {
            "keywords": [
                "code", "function", "class", "script", "program", "implement",
                "write code", "create function", "build", "develop", "python", "javascript"
            ],
            "patterns": [
                r"\b(write|create|generate|implement)\s+.*\s+(function|class|script|program|code)",
                r"\bimplement\s+\w+\s+in\s+(python|javascript|java|c\+\+|go|rust)",
                r"\bcreate\s+(a\s+)?(\w+\s+)?(function|class|module)",
                r"\b(python|javascript|java|c\+\+|go|rust)\s+(function|class|script)",
            ],
            "weight": 1.0
        },
        TaskType.CODE_REVIEW: {
            "keywords": [
                "review", "check code", "analyze code", "code quality",
                "best practices", "refactor", "improve code", "optimize"
            ],
            "patterns": [
                r"\breview\s+(this|my|the)\s+code",
                r"\bcheck\s+(this|my|the)\s+code",
                r"\banalyze\s+(this|my|the)\s+(code|implementation)",
                r"\bcode\s+review\b",
            ],
            "weight": 1.0
        },
        TaskType.CODE_DEBUG: {
            "keywords": [
                "debug", "fix", "error", "bug", "issue", "problem",
                "not working", "broken", "troubleshoot"
            ],
            "patterns": [
                r"\b(debug|fix)\s+(this|my|the)\s+(code|error|bug|issue)",
                r"\b(error|bug|issue|problem)\s+in\s+(my|the)\s+code",
                r"\bnot\s+working\b",
                r"\bbroken\b",
            ],
            "weight": 1.0
        },
        TaskType.SQL_QUERY: {
            "keywords": [
                "sql", "query", "database", "select", "insert", "update",
                "delete", "join", "table", "mysql", "postgresql", "sqlite"
            ],
            "patterns": [
                r"\b(write|create|generate)\s+(an?\s+)?sql\s+query",
                r"\bselect\s+.*\s+from\b",
                r"\b(mysql|postgresql|sqlite|oracle)\b",
                r"\bdatabase\s+query\b",
            ],
            "weight": 1.0
        },
        TaskType.RESEARCH: {
            "keywords": [
                "research", "investigate", "explore", "study", "analyze",
                "find information", "learn about", "explain", "what is"
            ],
            "patterns": [
                r"\b(research|investigate|explore|study)\s+",
                r"\bfind\s+information\s+(about|on)",
                r"\blearn\s+about\b",
                r"\bwhat\s+is\b",
                r"\bexplain\s+(what|how|why)",
            ],
            "weight": 0.8
        },
        TaskType.STORY_WRITING: {
            "keywords": [
                "story", "tale", "narrative", "fiction", "novel", "chapter",
                "character", "plot", "write story"
            ],
            "patterns": [
                r"\b(write|create|tell)\s+(a\s+)?(story|tale|narrative)",
                r"\bfiction\b",
                r"\bnovel\b",
                r"\bcharacter\s+(development|arc)",
            ],
            "weight": 1.0
        },
        TaskType.DATA_ANALYSIS: {
            "keywords": [
                "analyze data", "data analysis", "statistics", "trends",
                "insights", "metrics", "dataset", "correlation"
            ],
            "patterns": [
                r"\banalyze\s+(this|the)\s+data",
                r"\bdata\s+analysis\b",
                r"\bstatistical\s+analysis\b",
                r"\bfind\s+(trends|patterns|insights)",
            ],
            "weight": 1.0
        },
        TaskType.TRANSLATION: {
            "keywords": [
                "translate", "translation", "convert to", "in spanish",
                "in french", "in german", "in chinese", "in japanese"
            ],
            "patterns": [
                r"\btranslate\s+(this|to|into)",
                r"\bin\s+(spanish|french|german|chinese|japanese|korean|arabic)",
                r"\bconvert\s+to\s+\w+\s+(language)?",
            ],
            "weight": 1.0
        },
        TaskType.SUMMARIZATION: {
            "keywords": [
                "summarize", "summary", "tldr", "brief", "condense",
                "key points", "main ideas", "overview"
            ],
            "patterns": [
                r"\bsummari[sz]e\s+(this|the)",
                r"\btl;?dr\b",
                r"\b(give|provide)\s+(a\s+)?(brief|short)\s+summary",
                r"\bkey\s+points\b",
            ],
            "weight": 1.0
        },
        TaskType.QUESTION_ANSWERING: {
            "keywords": [
                "what", "why", "how", "when", "where", "who",
                "can you", "could you", "answer", "question"
            ],
            "patterns": [
                r"^\s*(what|why|how|when|where|who)\s+",
                r"\bcan\s+you\s+(tell|explain|answer)",
                r"\bcould\s+you\s+(tell|explain|answer)",
            ],
            "weight": 0.6
        },
        TaskType.CREATIVE_WRITING: {
            "keywords": [
                "poem", "poetry", "lyrics", "song", "creative", "imaginative",
                "metaphor", "verse"
            ],
            "patterns": [
                r"\b(write|create|compose)\s+(a\s+)?(poem|poetry|lyrics|song)",
                r"\bcreative\s+writing\b",
            ],
            "weight": 1.0
        },
        TaskType.TECHNICAL_WRITING: {
            "keywords": [
                "documentation", "technical doc", "api doc", "readme",
                "user guide", "manual", "tutorial", "how-to"
            ],
            "patterns": [
                r"\b(write|create)\s+(a\s+)?(documentation|readme|manual|tutorial)",
                r"\bapi\s+documentation\b",
                r"\buser\s+guide\b",
                r"\bhow-to\s+guide\b",
            ],
            "weight": 1.0
        },
    }
    
    def __init__(self, llm_provider: Optional[any] = None, confidence_threshold: float = 0.7):
        """
        Initialize the TaskClassifier.
        
        Args:
            llm_provider: Optional LLM provider for fallback classification
            confidence_threshold: Minimum confidence to avoid LLM fallback (default: 0.7)
        """
        self.llm_provider = llm_provider
        self.confidence_threshold = confidence_threshold
    
    def classify(self, prompt: str, use_llm_fallback: bool = False) -> TaskClassificationResult:
        """
        Classify a prompt to determine its task type.
        
        Args:
            prompt: The user's input prompt
            use_llm_fallback: Whether to use LLM fallback if confidence is low
            
        Returns:
            TaskClassificationResult with task type, confidence, and reasoning
        """
        # First, try heuristic classification
        result = self._classify_heuristic(prompt)
        
        # If confidence is low and LLM fallback is enabled, use LLM
        if (use_llm_fallback and 
            result.confidence < self.confidence_threshold and 
            self.llm_provider is not None):
            result = self._classify_with_llm(prompt)
            result.metadata["fallback_used"] = True
        
        return result
    
    def _classify_heuristic(self, prompt: str) -> TaskClassificationResult:
        """
        Classify using heuristic pattern matching.
        
        Args:
            prompt: The user's input prompt
            
        Returns:
            TaskClassificationResult
        """
        prompt_lower = prompt.lower()
        scores: Dict[TaskType, float] = {}
        matches: Dict[TaskType, List[str]] = {}
        
        # Calculate scores for each task type
        for task_type, config in self.TASK_PATTERNS.items():
            score = 0.0
            task_matches = []
            
            # Check keywords
            for keyword in config["keywords"]:
                if keyword.lower() in prompt_lower:
                    score += 0.2 * config["weight"]  # Increased from 0.1
                    task_matches.append(f"keyword: {keyword}")
            
            # Check regex patterns
            for pattern in config["patterns"]:
                if re.search(pattern, prompt_lower, re.IGNORECASE):
                    score += 0.5 * config["weight"]  # Increased from 0.3
                    task_matches.append(f"pattern: {pattern}")
            
            if score > 0:
                scores[task_type] = min(score, 1.0)  # Cap at 1.0
                matches[task_type] = task_matches
        
        # If no matches, default to GENERAL
        if not scores:
            return TaskClassificationResult(
                task_type=TaskType.GENERAL,
                confidence=0.5,
                reasoning="No specific task patterns detected, classified as general query",
                metadata={"method": "heuristic", "matches": []}
            )
        
        # Get the task type with highest score
        best_task = max(scores.items(), key=lambda x: x[1])
        task_type, confidence = best_task
        
        reasoning = (
            f"Classified as {task_type.value} based on heuristic analysis. "
            f"Matched: {', '.join(matches[task_type][:3])}"
        )
        
        return TaskClassificationResult(
            task_type=task_type,
            confidence=confidence,
            reasoning=reasoning,
            metadata={
                "method": "heuristic",
                "matches": matches[task_type],
                "all_scores": {k.value: v for k, v in scores.items()}
            }
        )
    
    def _classify_with_llm(self, prompt: str) -> TaskClassificationResult:
        """
        Classify using LLM fallback (placeholder for future implementation).
        
        Args:
            prompt: The user's input prompt
            
        Returns:
            TaskClassificationResult
        """
        # TODO: Implement LLM-based classification
        # This will be implemented when we integrate actual LLM providers
        
        return TaskClassificationResult(
            task_type=TaskType.GENERAL,
            confidence=0.6,
            reasoning="LLM classification not yet implemented, using fallback",
            metadata={"method": "llm_fallback", "provider": str(type(self.llm_provider))}
        )
