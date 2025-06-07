"""
Knowledge Graph module for FlashGenie.

This module provides knowledge graph functionality including building,
visualization, and analysis of learning relationships.
"""

from .builder import KnowledgeGraphBuilder
from .visualizer import KnowledgeGraphVisualizer
from .models import (
    ConceptNode, ConceptRelationship, KnowledgeGraph as KnowledgeGraphData,
    VisualizationConfig, GraphMetrics, LearningPath, KnowledgeGap
)

__all__ = [
    'KnowledgeGraphBuilder',
    'KnowledgeGraphVisualizer',
    'ConceptNode',
    'ConceptRelationship', 
    'KnowledgeGraphData',
    'VisualizationConfig',
    'GraphMetrics',
    'LearningPath',
    'KnowledgeGap'
]
