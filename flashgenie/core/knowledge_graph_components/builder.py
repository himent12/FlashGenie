"""
Knowledge graph builder for constructing graphs from flashcard data.

This module handles the construction of knowledge graphs from deck data.
"""

from typing import List, Dict, Optional, Set, Any
from pathlib import Path
import json
import math

from ..content_system.deck import Deck
from ..content_system.flashcard import Flashcard
from ..content_system.tag_manager import TagManager
from .models import (
    ConceptNode, ConceptRelationship, LearningPath, KnowledgeGap,
    NodeType, RelationshipType, MasteryLevel, KnowledgeGraph
)


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
        """
        Initialize the knowledge graph builder.
        
        Args:
            tag_manager: Tag manager for handling tag relationships
            data_path: Optional path for storing graph data
        """
        self.tag_manager = tag_manager
        self.data_path = Path(data_path or "data/knowledge_graph")
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Graph components
        self.nodes: Dict[str, ConceptNode] = {}
        self.relationships: List[ConceptRelationship] = []
        
        # Analysis results
        self.learning_paths: List[LearningPath] = []
        self.knowledge_gaps: List[KnowledgeGap] = []
    
    def build_graph(self, deck: Deck) -> KnowledgeGraph:
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
        self.learning_paths.clear()
        self.knowledge_gaps.clear()
        
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
                if (node1.id != node2.id and 
                    hasattr(node1, 'avg_difficulty') and 
                    hasattr(node2, 'avg_difficulty')):
                    
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
        
        # Group nodes by mastery level
        mastery_groups = {}
        for node in concept_nodes:
            level = node.mastery_level
            if level not in mastery_groups:
                mastery_groups[level] = []
            mastery_groups[level].append(node)
        
        # Create learning paths from low to high mastery
        path_id = 1
        for start_level in [MasteryLevel.UNKNOWN, MasteryLevel.INTRODUCED]:
            if start_level in mastery_groups:
                for start_node in mastery_groups[start_level][:3]:  # Limit to 3 paths per level
                    path = self._create_learning_path(start_node, concept_nodes, path_id)
                    if path:
                        self.learning_paths.append(path)
                        path_id += 1
    
    def _create_learning_path(self, start_node: ConceptNode, all_nodes: List[ConceptNode], path_id: int) -> Optional[LearningPath]:
        """Create a learning path starting from a given node."""
        path_nodes = [start_node.id]
        current_node = start_node
        
        # Simple path creation - follow prerequisite relationships
        for _ in range(5):  # Limit path length
            next_node = self._find_next_node_in_path(current_node, all_nodes)
            if next_node and next_node.id not in path_nodes:
                path_nodes.append(next_node.id)
                current_node = next_node
            else:
                break
        
        if len(path_nodes) >= 2:
            return LearningPath(
                path_id=f"path_{path_id}",
                name=f"Learning path from {start_node.name}",
                description=f"Recommended learning sequence starting with {start_node.name}",
                nodes=path_nodes,
                estimated_duration=len(path_nodes) * 3,  # 3 days per concept
                difficulty_progression=[
                    node.avg_difficulty for node in all_nodes 
                    if node.id in path_nodes
                ]
            )
        
        return None
    
    def _find_next_node_in_path(self, current_node: ConceptNode, all_nodes: List[ConceptNode]) -> Optional[ConceptNode]:
        """Find the next node in a learning path."""
        # Look for nodes that have this node as a prerequisite
        for rel in self.relationships:
            if (rel.source_id == current_node.id and 
                rel.relationship_type == RelationshipType.PREREQUISITE):
                
                target_node = next((n for n in all_nodes if n.id == rel.target_id), None)
                if target_node and target_node.mastery_level.value <= current_node.mastery_level.value + 1:
                    return target_node
        
        return None
    
    def _detect_knowledge_gaps(self) -> None:
        """Detect knowledge gaps in the graph."""
        concept_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.CONCEPT]
        
        for node in concept_nodes:
            # Check for weak foundations
            if node.mastery_level in [MasteryLevel.UNKNOWN, MasteryLevel.INTRODUCED]:
                if node.total_cards > 0:
                    gap = KnowledgeGap(
                        concept_id=node.id,
                        gap_type="weak_foundation",
                        severity=1.0 - node.get_mastery_percentage(),
                        description=f"Weak foundation in {node.name}",
                        recommended_actions=[
                            f"Review basic concepts in {node.name}",
                            f"Practice more cards in {node.name}",
                            f"Focus on accuracy in {node.name}"
                        ]
                    )
                    self.knowledge_gaps.append(gap)
            
            # Check for isolated concepts (no relationships)
            has_relationships = any(
                rel.source_id == node.id or rel.target_id == node.id
                for rel in self.relationships
            )
            
            if not has_relationships and node.total_cards > 0:
                gap = KnowledgeGap(
                    concept_id=node.id,
                    gap_type="isolated_concept",
                    severity=0.6,
                    description=f"{node.name} is isolated from other concepts",
                    recommended_actions=[
                        f"Connect {node.name} to related topics",
                        f"Add prerequisite concepts for {node.name}",
                        f"Expand content around {node.name}"
                    ]
                )
                self.knowledge_gaps.append(gap)
    
    def _optimize_graph_layout(self) -> None:
        """Optimize the visual layout of the graph."""
        # Simple circular layout for now
        concept_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.CONCEPT]
        
        if concept_nodes:
            angle_step = 2 * math.pi / len(concept_nodes)
            radius = max(3.0, len(concept_nodes) * 0.5)
            
            for i, node in enumerate(concept_nodes):
                angle = i * angle_step
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                node.position = (x, y)
        
        # Position clusters in the center
        cluster_nodes = [n for n in self.nodes.values() if n.node_type == NodeType.CLUSTER]
        for i, node in enumerate(cluster_nodes):
            node.position = (i * 2.0 - len(cluster_nodes), 0.0)
