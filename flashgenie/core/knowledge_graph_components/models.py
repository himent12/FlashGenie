"""
Data models for knowledge graph system.

This module contains all the data classes and enums used by the knowledge graph system.
"""

from datetime import datetime
from typing import List, Dict, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class NodeType(Enum):
    """Types of nodes in the knowledge graph."""
    CONCEPT = "concept"  # Tag-based concept node
    CARD = "card"  # Individual flashcard node
    CLUSTER = "cluster"  # Group of related concepts
    MILESTONE = "milestone"  # Learning milestone


class RelationshipType(Enum):
    """Types of relationships between nodes."""
    PARENT_CHILD = "parent_child"  # Hierarchical relationship
    PREREQUISITE = "prerequisite"  # One concept requires another
    RELATED = "related"  # General relationship
    SIMILAR = "similar"  # Similar content
    SEQUENCE = "sequence"  # Sequential learning order


class MasteryLevel(Enum):
    """Levels of concept mastery."""
    UNKNOWN = 0
    INTRODUCED = 1
    PRACTICING = 2
    DEVELOPING = 3
    PROFICIENT = 4
    MASTERED = 5


@dataclass
class ConceptNode:
    """A node representing a concept in the knowledge graph."""
    id: str
    name: str
    node_type: NodeType
    mastery_level: MasteryLevel = MasteryLevel.UNKNOWN
    
    # Content information
    description: str = ""
    tags: Set[str] = field(default_factory=set)
    related_cards: List[str] = field(default_factory=list)  # Card IDs
    
    # Learning metrics
    total_cards: int = 0
    mastered_cards: int = 0
    accuracy_rate: float = 0.0
    last_studied: Optional[datetime] = None
    study_time_minutes: int = 0
    
    # Visual properties
    position: Tuple[float, float] = (0.0, 0.0)
    size: float = 1.0
    color: str = "#cccccc"
    
    # Additional metrics
    avg_difficulty: float = 0.5
    
    def get_mastery_percentage(self) -> float:
        """Get mastery percentage for this concept."""
        if self.total_cards == 0:
            return 0.0
        return self.mastered_cards / self.total_cards
    
    def update_mastery_level(self) -> None:
        """Update mastery level based on current metrics."""
        mastery_pct = self.get_mastery_percentage()
        
        if mastery_pct == 0.0:
            self.mastery_level = MasteryLevel.UNKNOWN
        elif mastery_pct < 0.2:
            self.mastery_level = MasteryLevel.INTRODUCED
        elif mastery_pct < 0.4:
            self.mastery_level = MasteryLevel.PRACTICING
        elif mastery_pct < 0.7:
            self.mastery_level = MasteryLevel.DEVELOPING
        elif mastery_pct < 0.9:
            self.mastery_level = MasteryLevel.PROFICIENT
        else:
            self.mastery_level = MasteryLevel.MASTERED


@dataclass
class ConceptRelationship:
    """A relationship between two concepts."""
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    strength: float = 1.0  # 0.0 to 1.0
    description: str = ""
    
    # Learning implications
    prerequisite_strength: float = 0.0  # How much target depends on source
    similarity_score: float = 0.0  # How similar the concepts are
    
    def __post_init__(self):
        """Set default values based on relationship type."""
        if self.relationship_type == RelationshipType.PREREQUISITE:
            self.prerequisite_strength = self.strength
        elif self.relationship_type == RelationshipType.SIMILAR:
            self.similarity_score = self.strength


@dataclass
class LearningPath:
    """A recommended path through the knowledge graph."""
    path_id: str
    name: str
    description: str
    nodes: List[str]  # Ordered list of concept IDs
    estimated_duration: int  # days
    difficulty_progression: List[float]
    prerequisites_met: bool = True


@dataclass
class KnowledgeGap:
    """An identified gap in knowledge."""
    concept_id: str
    gap_type: str  # "missing_prerequisite", "weak_foundation", "isolated_concept"
    severity: float  # 0.0 to 1.0
    description: str
    recommended_actions: List[str]


@dataclass
class KnowledgeGraph:
    """Complete knowledge graph structure."""
    nodes: List[ConceptNode]
    relationships: List[ConceptRelationship]
    learning_paths: List[LearningPath]
    knowledge_gaps: List[KnowledgeGap]
    
    def get_mastery_summary(self) -> Dict[str, Any]:
        """Get a summary of mastery across the graph."""
        if not self.nodes:
            return {}
        
        concept_nodes = [n for n in self.nodes if n.node_type == NodeType.CONCEPT]
        
        total_concepts = len(concept_nodes)
        total_cards = sum(node.total_cards for node in concept_nodes)
        mastered_cards = sum(node.mastered_cards for node in concept_nodes)
        
        # Mastery distribution
        mastery_distribution = {}
        for level in MasteryLevel:
            count = len([n for n in concept_nodes if n.mastery_level == level])
            if count > 0:
                mastery_distribution[level.name.lower()] = count
        
        return {
            "total_concepts": total_concepts,
            "total_cards": total_cards,
            "mastered_cards": mastered_cards,
            "overall_mastery_rate": mastered_cards / total_cards if total_cards > 0 else 0,
            "knowledge_gaps": len(self.knowledge_gaps),
            "learning_paths": len(self.learning_paths),
            "mastery_distribution": mastery_distribution
        }
    
    def export_for_visualization(self) -> Dict[str, Any]:
        """Export graph data for visualization."""
        return {
            "nodes": [
                {
                    "id": node.id,
                    "name": node.name,
                    "type": node.node_type.value,
                    "mastery": node.mastery_level.value,
                    "mastery_percentage": node.get_mastery_percentage(),
                    "position": node.position,
                    "size": node.size,
                    "color": node.color,
                    "total_cards": node.total_cards,
                    "mastered_cards": node.mastered_cards
                }
                for node in self.nodes
            ],
            "edges": [
                {
                    "source": rel.source_id,
                    "target": rel.target_id,
                    "type": rel.relationship_type.value,
                    "strength": rel.strength,
                    "description": rel.description
                }
                for rel in self.relationships
            ],
            "paths": [
                {
                    "id": path.path_id,
                    "name": path.name,
                    "nodes": path.nodes,
                    "duration": path.estimated_duration
                }
                for path in self.learning_paths
            ],
            "gaps": [
                {
                    "concept": gap.concept_id,
                    "type": gap.gap_type,
                    "severity": gap.severity,
                    "description": gap.description
                }
                for gap in self.knowledge_gaps
            ]
        }


@dataclass
class GraphMetrics:
    """Metrics for analyzing the knowledge graph."""
    node_count: int
    edge_count: int
    cluster_count: int
    average_degree: float
    density: float
    connected_components: int
    
    
@dataclass
class VisualizationConfig:
    """Configuration for graph visualization."""
    layout_algorithm: str = "force_directed"  # force_directed, hierarchical, circular
    node_size_factor: float = 1.0
    edge_thickness_factor: float = 1.0
    show_labels: bool = True
    show_mastery_colors: bool = True
    highlight_paths: bool = False
    filter_weak_edges: bool = True
    weak_edge_threshold: float = 0.3
