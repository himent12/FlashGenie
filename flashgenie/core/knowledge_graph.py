"""
Knowledge Graph Visualization for FlashGenie v1.5

This module implements visual representation of knowledge connections using tag
hierarchies and card relationships to show learning progress and identify gaps.
"""

from datetime import datetime
from typing import List, Dict, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import math
from pathlib import Path

from flashgenie.core.flashcard import Flashcard
from flashgenie.core.deck import Deck
from flashgenie.core.tag_manager import TagManager


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


class KnowledgeGraphBuilder:
    """
    Builds and maintains a knowledge graph from flashcard data.
    
    The knowledge graph visualizes:
    - Concept relationships based on tag hierarchies
    - Learning progress and mastery levels
    - Knowledge gaps and prerequisites
    - Optimal learning paths
    """
    
    def __init__(self, tag_manager: TagManager, data_path: Optional[str] = None):
        self.tag_manager = tag_manager
        self.data_path = Path(data_path or "data/knowledge_graph")
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Graph components
        self.nodes: Dict[str, ConceptNode] = {}
        self.relationships: List[ConceptRelationship] = []
        
        # Analysis results
        self.learning_paths: List[LearningPath] = []
        self.knowledge_gaps: List[KnowledgeGap] = []
        
        # Load existing graph data
        self._load_graph_data()
    
    def build_graph(self, deck: Deck) -> 'KnowledgeGraph':
        """
        Build a knowledge graph from a deck of flashcards.
        
        Args:
            deck: The deck to analyze
            
        Returns:
            Complete knowledge graph
        """
        # Clear existing graph
        self.nodes.clear()
        self.relationships.clear()
        
        # Build concept nodes from tags
        self._build_concept_nodes(deck)
        
        # Build relationships between concepts
        self._build_concept_relationships(deck)
        
        # Calculate mastery levels
        self._calculate_mastery_levels(deck)
        
        # Identify learning paths
        self._identify_learning_paths()
        
        # Detect knowledge gaps
        self._detect_knowledge_gaps()
        
        # Optimize layout
        self._optimize_graph_layout()
        
        # Save graph data
        self._save_graph_data()
        
        return KnowledgeGraph(
            nodes=list(self.nodes.values()),
            relationships=self.relationships,
            learning_paths=self.learning_paths,
            knowledge_gaps=self.knowledge_gaps
        )
    
    def _build_concept_nodes(self, deck: Deck) -> None:
        """Build concept nodes from tag hierarchies and card content."""
        # Get all unique tags from the deck
        all_tags = set()
        for card in deck.flashcards:
            all_tags.update(card.tags)
        
        # Create nodes for each tag/concept
        for tag in all_tags:
            concept_id = f"concept_{tag.replace(' ', '_').lower()}"
            
            # Get tag hierarchy information
            tag_hierarchy = self.tag_manager.get_tag_hierarchy(tag)
            
            # Find related cards
            related_cards = [
                card.id for card in deck.flashcards 
                if tag in card.tags
            ]
            
            # Calculate initial metrics
            total_cards = len(related_cards)
            mastered_cards = len([
                card for card in deck.flashcards
                if card.id in related_cards and self._is_card_mastered(card)
            ])
            
            accuracy_rate = 0.0
            if related_cards:
                accuracies = [
                    card.calculate_accuracy() for card in deck.flashcards
                    if card.id in related_cards and card.review_count > 0
                ]
                accuracy_rate = sum(accuracies) / len(accuracies) if accuracies else 0.0
            
            # Create concept node
            node = ConceptNode(
                id=concept_id,
                name=tag,
                node_type=NodeType.CONCEPT,
                description=tag_hierarchy.description if tag_hierarchy else "",
                tags={tag},
                related_cards=related_cards,
                total_cards=total_cards,
                mastered_cards=mastered_cards,
                accuracy_rate=accuracy_rate
            )
            
            # Update mastery level
            node.update_mastery_level()
            
            self.nodes[concept_id] = node
        
        # Create cluster nodes for major concept groups
        self._create_cluster_nodes(deck)
    
    def _create_cluster_nodes(self, deck: Deck) -> None:
        """Create cluster nodes for major concept groups."""
        # Group concepts by parent tags
        parent_groups = {}
        
        for tag in set().union(*(card.tags for card in deck.flashcards)):
            hierarchy = self.tag_manager.get_tag_hierarchy(tag)
            if hierarchy and hierarchy.parent:
                parent = hierarchy.parent
                if parent not in parent_groups:
                    parent_groups[parent] = []
                parent_groups[parent].append(tag)
        
        # Create cluster nodes for parents with multiple children
        for parent, children in parent_groups.items():
            if len(children) >= 2:  # Only create clusters for 2+ concepts
                cluster_id = f"cluster_{parent.replace(' ', '_').lower()}"
                
                # Aggregate metrics from children
                total_cards = sum(
                    self.nodes[f"concept_{child.replace(' ', '_').lower()}"].total_cards
                    for child in children
                    if f"concept_{child.replace(' ', '_').lower()}" in self.nodes
                )
                
                mastered_cards = sum(
                    self.nodes[f"concept_{child.replace(' ', '_').lower()}"].mastered_cards
                    for child in children
                    if f"concept_{child.replace(' ', '_').lower()}" in self.nodes
                )
                
                cluster_node = ConceptNode(
                    id=cluster_id,
                    name=parent,
                    node_type=NodeType.CLUSTER,
                    description=f"Cluster of {len(children)} related concepts",
                    tags={parent},
                    total_cards=total_cards,
                    mastered_cards=mastered_cards,
                    size=1.5  # Larger size for clusters
                )
                
                cluster_node.update_mastery_level()
                self.nodes[cluster_id] = cluster_node
    
    def _build_concept_relationships(self, deck: Deck) -> None:
        """Build relationships between concepts."""
        # Parent-child relationships from tag hierarchy
        self._build_hierarchical_relationships()
        
        # Content similarity relationships
        self._build_similarity_relationships(deck)
        
        # Prerequisite relationships (inferred)
        self._build_prerequisite_relationships(deck)
    
    def _build_hierarchical_relationships(self) -> None:
        """Build parent-child relationships from tag hierarchy."""
        for node in self.nodes.values():
            if node.node_type == NodeType.CONCEPT:
                tag = list(node.tags)[0]  # Get the primary tag
                hierarchy = self.tag_manager.get_tag_hierarchy(tag)
                
                if hierarchy and hierarchy.parent:
                    parent_id = f"concept_{hierarchy.parent.replace(' ', '_').lower()}"
                    cluster_id = f"cluster_{hierarchy.parent.replace(' ', '_').lower()}"
                    
                    # Relationship to parent concept
                    if parent_id in self.nodes:
                        self.relationships.append(ConceptRelationship(
                            source_id=parent_id,
                            target_id=node.id,
                            relationship_type=RelationshipType.PARENT_CHILD,
                            strength=1.0,
                            description=f"{hierarchy.parent} contains {tag}"
                        ))
                    
                    # Relationship to cluster
                    if cluster_id in self.nodes:
                        self.relationships.append(ConceptRelationship(
                            source_id=cluster_id,
                            target_id=node.id,
                            relationship_type=RelationshipType.PARENT_CHILD,
                            strength=0.8,
                            description=f"Part of {hierarchy.parent} cluster"
                        ))
    
    def _build_similarity_relationships(self, deck: Deck) -> None:
        """Build relationships based on content similarity."""
        concept_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.CONCEPT]
        
        for i, node1 in enumerate(concept_nodes):
            for node2 in concept_nodes[i+1:]:
                similarity = self._calculate_concept_similarity(node1, node2, deck)
                
                if similarity > 0.3:  # Threshold for similarity
                    self.relationships.append(ConceptRelationship(
                        source_id=node1.id,
                        target_id=node2.id,
                        relationship_type=RelationshipType.SIMILAR,
                        strength=similarity,
                        similarity_score=similarity,
                        description=f"Similar concepts (similarity: {similarity:.2f})"
                    ))
    
    def _build_prerequisite_relationships(self, deck: Deck) -> None:
        """Build prerequisite relationships based on learning patterns."""
        # Simple heuristic: concepts with higher average difficulty
        # might be prerequisites for concepts with lower difficulty
        concept_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.CONCEPT]
        
        for node in concept_nodes:
            # Calculate average difficulty of cards in this concept
            related_cards = [
                card for card in deck.flashcards
                if card.id in node.related_cards
            ]
            
            if related_cards:
                avg_difficulty = sum(card.difficulty for card in related_cards) / len(related_cards)
                node.avg_difficulty = avg_difficulty
        
        # Create prerequisite relationships
        for node1 in concept_nodes:
            for node2 in concept_nodes:
                if node1.id != node2.id and hasattr(node1, 'avg_difficulty') and hasattr(node2, 'avg_difficulty'):
                    # If node1 is significantly easier than node2, it might be a prerequisite
                    difficulty_diff = node2.avg_difficulty - node1.avg_difficulty
                    
                    if difficulty_diff > 0.2:  # Threshold for prerequisite relationship
                        # Check if they're related (share parent or similar)
                        are_related = any(
                            rel.source_id in [node1.id, node2.id] and 
                            rel.target_id in [node1.id, node2.id]
                            for rel in self.relationships
                        )
                        
                        if are_related:
                            prerequisite_strength = min(0.8, difficulty_diff)
                            self.relationships.append(ConceptRelationship(
                                source_id=node1.id,
                                target_id=node2.id,
                                relationship_type=RelationshipType.PREREQUISITE,
                                strength=prerequisite_strength,
                                prerequisite_strength=prerequisite_strength,
                                description=f"{node1.name} may be prerequisite for {node2.name}"
                            ))
    
    def _calculate_concept_similarity(self, node1: ConceptNode, node2: ConceptNode, deck: Deck) -> float:
        """Calculate similarity between two concepts."""
        # Get cards for each concept
        cards1 = [card for card in deck.flashcards if card.id in node1.related_cards]
        cards2 = [card for card in deck.flashcards if card.id in node2.related_cards]
        
        if not cards1 or not cards2:
            return 0.0
        
        # Calculate tag overlap
        tags1 = set().union(*(card.tags for card in cards1))
        tags2 = set().union(*(card.tags for card in cards2))
        
        tag_overlap = len(tags1.intersection(tags2)) / len(tags1.union(tags2))
        
        # Calculate difficulty similarity
        avg_diff1 = sum(card.difficulty for card in cards1) / len(cards1)
        avg_diff2 = sum(card.difficulty for card in cards2) / len(cards2)
        
        difficulty_similarity = 1.0 - abs(avg_diff1 - avg_diff2)
        
        # Combine metrics
        similarity = (tag_overlap * 0.7) + (difficulty_similarity * 0.3)
        
        return similarity
    
    def _calculate_mastery_levels(self, deck: Deck) -> None:
        """Calculate and update mastery levels for all nodes."""
        for node in self.nodes.values():
            if node.node_type == NodeType.CONCEPT:
                # Update based on related cards
                related_cards = [
                    card for card in deck.flashcards
                    if card.id in node.related_cards
                ]
                
                if related_cards:
                    # Update mastery metrics
                    node.mastered_cards = len([
                        card for card in related_cards
                        if self._is_card_mastered(card)
                    ])
                    
                    # Update accuracy rate
                    accuracies = [
                        card.calculate_accuracy() for card in related_cards
                        if card.review_count > 0
                    ]
                    node.accuracy_rate = sum(accuracies) / len(accuracies) if accuracies else 0.0
                    
                    # Update last studied
                    last_studied_dates = [
                        card.last_reviewed for card in related_cards
                        if card.last_reviewed
                    ]
                    if last_studied_dates:
                        node.last_studied = max(last_studied_dates)
                
                # Update mastery level
                node.update_mastery_level()
                
                # Set visual properties based on mastery
                node.color = self._get_mastery_color(node.mastery_level)
                node.size = 0.5 + (node.get_mastery_percentage() * 1.5)
    
    def _is_card_mastered(self, card: Flashcard) -> bool:
        """Check if a card is considered mastered."""
        return (card.review_count >= 3 and 
                card.calculate_accuracy() >= 0.9 and 
                card.difficulty < 0.4)
    
    def _get_mastery_color(self, mastery_level: MasteryLevel) -> str:
        """Get color for mastery level."""
        colors = {
            MasteryLevel.UNKNOWN: "#cccccc",
            MasteryLevel.INTRODUCED: "#ffcccc",
            MasteryLevel.PRACTICING: "#ffddaa",
            MasteryLevel.DEVELOPING: "#ffffaa",
            MasteryLevel.PROFICIENT: "#ccffcc",
            MasteryLevel.MASTERED: "#aaffaa"
        }
        return colors.get(mastery_level, "#cccccc")
    
    def _identify_learning_paths(self) -> None:
        """Identify optimal learning paths through the graph."""
        # Simple path identification - can be enhanced with graph algorithms
        concept_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.CONCEPT]
        
        # Sort by mastery level and difficulty
        sorted_concepts = sorted(
            concept_nodes,
            key=lambda n: (n.mastery_level.value, n.get_mastery_percentage())
        )
        
        # Create a basic learning path
        if len(sorted_concepts) >= 3:
            path = LearningPath(
                path_id="basic_progression",
                name="Basic Learning Progression",
                description="Recommended order for studying concepts",
                nodes=[node.id for node in sorted_concepts],
                estimated_duration=len(sorted_concepts) * 7,  # 1 week per concept
                difficulty_progression=[
                    getattr(node, 'avg_difficulty', 0.5) for node in sorted_concepts
                ]
            )
            self.learning_paths.append(path)
    
    def _detect_knowledge_gaps(self) -> None:
        """Detect gaps in knowledge and understanding."""
        for node in self.nodes.values():
            if node.node_type == NodeType.CONCEPT:
                # Check for weak foundations
                if node.mastery_level.value < 3 and node.total_cards > 5:
                    gap = KnowledgeGap(
                        concept_id=node.id,
                        gap_type="weak_foundation",
                        severity=1.0 - (node.mastery_level.value / 5.0),
                        description=f"Weak understanding of {node.name}",
                        recommended_actions=[
                            "Review basic concepts",
                            "Practice with easier cards",
                            "Study prerequisites"
                        ]
                    )
                    self.knowledge_gaps.append(gap)
                
                # Check for missing prerequisites
                prerequisites = [
                    rel for rel in self.relationships
                    if (rel.target_id == node.id and 
                        rel.relationship_type == RelationshipType.PREREQUISITE)
                ]
                
                for prereq_rel in prerequisites:
                    prereq_node = self.nodes.get(prereq_rel.source_id)
                    if (prereq_node and 
                        prereq_node.mastery_level.value < node.mastery_level.value):
                        gap = KnowledgeGap(
                            concept_id=prereq_node.id,
                            gap_type="missing_prerequisite",
                            severity=prereq_rel.prerequisite_strength,
                            description=f"Prerequisite {prereq_node.name} not mastered",
                            recommended_actions=[
                                f"Study {prereq_node.name} before advancing",
                                "Review foundational concepts"
                            ]
                        )
                        self.knowledge_gaps.append(gap)
    
    def _optimize_graph_layout(self) -> None:
        """Optimize the visual layout of the graph."""
        # Simple circular layout - can be enhanced with force-directed algorithms
        concept_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.CONCEPT]
        
        if not concept_nodes:
            return
        
        # Arrange concepts in a circle
        angle_step = 2 * math.pi / len(concept_nodes)
        radius = max(100, len(concept_nodes) * 10)
        
        for i, node in enumerate(concept_nodes):
            angle = i * angle_step
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            node.position = (x, y)
        
        # Position clusters in the center
        cluster_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.CLUSTER]
        cluster_radius = radius * 0.3
        
        if cluster_nodes:
            cluster_angle_step = 2 * math.pi / len(cluster_nodes)
            for i, node in enumerate(cluster_nodes):
                angle = i * cluster_angle_step
                x = cluster_radius * math.cos(angle)
                y = cluster_radius * math.sin(angle)
                node.position = (x, y)
    
    def _load_graph_data(self) -> None:
        """Load existing graph data from storage."""
        # Placeholder for loading saved graph data
        pass
    
    def _save_graph_data(self) -> None:
        """Save graph data to storage."""
        # Placeholder for saving graph data
        pass


@dataclass
class KnowledgeGraph:
    """Complete knowledge graph with all components."""
    nodes: List[ConceptNode]
    relationships: List[ConceptRelationship]
    learning_paths: List[LearningPath]
    knowledge_gaps: List[KnowledgeGap]
    
    def get_node_by_id(self, node_id: str) -> Optional[ConceptNode]:
        """Get a node by its ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_relationships_for_node(self, node_id: str) -> List[ConceptRelationship]:
        """Get all relationships involving a specific node."""
        return [
            rel for rel in self.relationships
            if rel.source_id == node_id or rel.target_id == node_id
        ]
    
    def get_mastery_summary(self) -> Dict[str, Any]:
        """Get a summary of mastery across the graph."""
        concept_nodes = [n for n in self.nodes if n.node_type == NodeType.CONCEPT]
        
        if not concept_nodes:
            return {}
        
        mastery_counts = {}
        for level in MasteryLevel:
            mastery_counts[level.name] = len([
                n for n in concept_nodes if n.mastery_level == level
            ])
        
        total_cards = sum(node.total_cards for node in concept_nodes)
        mastered_cards = sum(node.mastered_cards for node in concept_nodes)
        
        return {
            'total_concepts': len(concept_nodes),
            'mastery_distribution': mastery_counts,
            'total_cards': total_cards,
            'mastered_cards': mastered_cards,
            'overall_mastery_rate': mastered_cards / total_cards if total_cards > 0 else 0.0,
            'knowledge_gaps': len(self.knowledge_gaps),
            'learning_paths': len(self.learning_paths)
        }
    
    def export_for_visualization(self) -> Dict[str, Any]:
        """Export graph data in a format suitable for visualization."""
        return {
            'nodes': [
                {
                    'id': node.id,
                    'name': node.name,
                    'type': node.node_type.value,
                    'mastery_level': node.mastery_level.value,
                    'mastery_percentage': node.get_mastery_percentage(),
                    'position': node.position,
                    'size': node.size,
                    'color': node.color,
                    'total_cards': node.total_cards,
                    'mastered_cards': node.mastered_cards
                }
                for node in self.nodes
            ],
            'edges': [
                {
                    'source': rel.source_id,
                    'target': rel.target_id,
                    'type': rel.relationship_type.value,
                    'strength': rel.strength,
                    'description': rel.description
                }
                for rel in self.relationships
            ],
            'learning_paths': [
                {
                    'id': path.path_id,
                    'name': path.name,
                    'description': path.description,
                    'nodes': path.nodes,
                    'duration': path.estimated_duration
                }
                for path in self.learning_paths
            ],
            'knowledge_gaps': [
                {
                    'concept_id': gap.concept_id,
                    'type': gap.gap_type,
                    'severity': gap.severity,
                    'description': gap.description,
                    'actions': gap.recommended_actions
                }
                for gap in self.knowledge_gaps
            ]
        }
