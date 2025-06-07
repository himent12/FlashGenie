"""
Knowledge Graph for FlashGenie.

This module provides the main KnowledgeGraph class that serves as the
public interface for knowledge graph functionality.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path

from .content_system.deck import Deck
from .content_system.tag_manager import TagManager
from .knowledge_graph_components.builder import KnowledgeGraphBuilder
from .knowledge_graph_components.visualizer import KnowledgeGraphVisualizer
from .knowledge_graph_components.models import VisualizationConfig


class KnowledgeGraph:
    """
    Main interface for knowledge graph functionality.
    
    This class provides a simplified interface to the knowledge graph
    system while maintaining backward compatibility.
    """
    
    def __init__(self, tag_manager: TagManager, data_path: Optional[str] = None):
        """
        Initialize the knowledge graph.
        
        Args:
            tag_manager: Tag manager for handling tag relationships
            data_path: Optional path for storing graph data
        """
        self.builder = KnowledgeGraphBuilder(tag_manager, data_path)
        self.visualizer = KnowledgeGraphVisualizer()
        self._current_graph = None
    
    def build_graph(self, deck: Deck) -> Dict[str, Any]:
        """
        Build a knowledge graph from a deck of flashcards.
        
        Args:
            deck: The deck to analyze
            
        Returns:
            Dictionary with graph data and metrics
        """
        # Build the graph
        self._current_graph = self.builder.build_graph(deck)
        
        # Calculate metrics
        metrics = self.visualizer.calculate_metrics(self._current_graph)
        
        # Get mastery summary
        mastery_summary = self._current_graph.get_mastery_summary()
        
        return {
            "node_count": metrics.node_count,
            "edge_count": metrics.edge_count,
            "cluster_count": metrics.cluster_count,
            "density": metrics.density,
            "connected_components": metrics.connected_components,
            "mastery_summary": mastery_summary,
            "learning_paths": len(self._current_graph.learning_paths),
            "knowledge_gaps": len(self._current_graph.knowledge_gaps),
            "key_concepts": self._get_key_concepts(),
            "success": True
        }
    
    def get_learning_paths(self) -> List[Dict[str, Any]]:
        """
        Get recommended learning paths.
        
        Returns:
            List of learning paths as dictionaries
        """
        if not self._current_graph:
            return []
        
        return [
            {
                "id": path.path_id,
                "name": path.name,
                "description": path.description,
                "concepts": path.nodes,
                "duration": path.estimated_duration,
                "difficulty_progression": path.difficulty_progression,
                "prerequisites_met": path.prerequisites_met
            }
            for path in self._current_graph.learning_paths
        ]
    
    def get_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """
        Get identified knowledge gaps.
        
        Returns:
            List of knowledge gaps as dictionaries
        """
        if not self._current_graph:
            return []
        
        return [
            {
                "concept": gap.concept_id,
                "type": gap.gap_type,
                "severity": gap.severity,
                "description": gap.description,
                "actions": gap.recommended_actions
            }
            for gap in self._current_graph.knowledge_gaps
        ]
    
    def get_mastery_overview(self) -> Dict[str, Any]:
        """
        Get an overview of mastery across all concepts.
        
        Returns:
            Dictionary with mastery overview
        """
        if not self._current_graph:
            return {}
        
        return self._current_graph.get_mastery_summary()
    
    def export_html(self, output_path: Path, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Export knowledge graph as interactive HTML visualization.
        
        Args:
            output_path: Path to save the HTML file
            config: Optional visualization configuration
        """
        if not self._current_graph:
            raise ValueError("No graph built. Call build_graph() first.")
        
        # Convert config dict to VisualizationConfig if provided
        viz_config = None
        if config:
            viz_config = VisualizationConfig(
                layout_algorithm=config.get("layout_algorithm", "force_directed"),
                node_size_factor=config.get("node_size_factor", 1.0),
                edge_thickness_factor=config.get("edge_thickness_factor", 1.0),
                show_labels=config.get("show_labels", True),
                show_mastery_colors=config.get("show_mastery_colors", True),
                highlight_paths=config.get("highlight_paths", False),
                filter_weak_edges=config.get("filter_weak_edges", True),
                weak_edge_threshold=config.get("weak_edge_threshold", 0.3)
            )
        
        self.visualizer.export_html(self._current_graph, output_path, viz_config)
    
    def export_json(self, output_path: Path) -> None:
        """
        Export knowledge graph as JSON data.
        
        Args:
            output_path: Path to save the JSON file
        """
        if not self._current_graph:
            raise ValueError("No graph built. Call build_graph() first.")
        
        self.visualizer.export_json(self._current_graph, output_path)
    
    def get_concept_details(self, concept_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific concept.
        
        Args:
            concept_name: Name of the concept
            
        Returns:
            Dictionary with concept details or None if not found
        """
        if not self._current_graph:
            return None
        
        # Find the concept node
        concept_node = None
        for node in self._current_graph.nodes:
            if node.name.lower() == concept_name.lower():
                concept_node = node
                break
        
        if not concept_node:
            return None
        
        # Get relationships
        relationships = []
        for rel in self._current_graph.relationships:
            if rel.source_id == concept_node.id or rel.target_id == concept_node.id:
                relationships.append({
                    "type": rel.relationship_type.value,
                    "strength": rel.strength,
                    "description": rel.description,
                    "other_concept": rel.target_id if rel.source_id == concept_node.id else rel.source_id
                })
        
        return {
            "name": concept_node.name,
            "type": concept_node.node_type.value,
            "mastery_level": concept_node.mastery_level.name.lower(),
            "mastery_percentage": concept_node.get_mastery_percentage(),
            "total_cards": concept_node.total_cards,
            "mastered_cards": concept_node.mastered_cards,
            "accuracy_rate": concept_node.accuracy_rate,
            "avg_difficulty": concept_node.avg_difficulty,
            "last_studied": concept_node.last_studied.isoformat() if concept_node.last_studied else None,
            "study_time_minutes": concept_node.study_time_minutes,
            "relationships": relationships,
            "tags": list(concept_node.tags),
            "description": concept_node.description
        }
    
    def get_prerequisite_chain(self, concept_name: str) -> List[str]:
        """
        Get the prerequisite chain for a concept.
        
        Args:
            concept_name: Name of the concept
            
        Returns:
            List of concept names in prerequisite order
        """
        if not self._current_graph:
            return []
        
        # Find the concept node
        concept_node = None
        for node in self._current_graph.nodes:
            if node.name.lower() == concept_name.lower():
                concept_node = node
                break
        
        if not concept_node:
            return []
        
        # Build prerequisite chain
        chain = []
        current_id = concept_node.id
        visited = set()
        
        while current_id and current_id not in visited:
            visited.add(current_id)
            
            # Find the node
            current_node = next((n for n in self._current_graph.nodes if n.id == current_id), None)
            if current_node:
                chain.append(current_node.name)
            
            # Find prerequisite
            prerequisite_rel = next((
                rel for rel in self._current_graph.relationships
                if rel.target_id == current_id and rel.relationship_type.value == "prerequisite"
            ), None)
            
            if prerequisite_rel:
                current_id = prerequisite_rel.source_id
            else:
                break
        
        return list(reversed(chain))  # Return in learning order
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the knowledge graph.
        
        Returns:
            Dictionary with graph statistics
        """
        if not self._current_graph:
            return {}
        
        metrics = self.visualizer.calculate_metrics(self._current_graph)
        mastery_summary = self._current_graph.get_mastery_summary()
        
        # Additional statistics
        concept_nodes = [n for n in self._current_graph.nodes if n.node_type.value == "concept"]
        cluster_nodes = [n for n in self._current_graph.nodes if n.node_type.value == "cluster"]
        
        # Relationship type distribution
        rel_types = {}
        for rel in self._current_graph.relationships:
            rel_type = rel.relationship_type.value
            rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
        
        return {
            "basic_metrics": {
                "total_nodes": metrics.node_count,
                "concept_nodes": len(concept_nodes),
                "cluster_nodes": len(cluster_nodes),
                "total_edges": metrics.edge_count,
                "density": metrics.density,
                "average_degree": metrics.average_degree,
                "connected_components": metrics.connected_components
            },
            "mastery_metrics": mastery_summary,
            "learning_metrics": {
                "learning_paths": len(self._current_graph.learning_paths),
                "knowledge_gaps": len(self._current_graph.knowledge_gaps),
                "avg_path_length": self._calculate_avg_path_length(),
                "most_connected_concept": self._find_most_connected_concept()
            },
            "relationship_distribution": rel_types,
            "complexity_score": self._calculate_complexity_score(metrics)
        }
    
    def _get_key_concepts(self) -> List[Dict[str, Any]]:
        """Get key concepts from the graph."""
        if not self._current_graph:
            return []
        
        concept_nodes = [n for n in self._current_graph.nodes if n.node_type.value == "concept"]
        
        # Sort by total cards and mastery
        key_concepts = sorted(
            concept_nodes,
            key=lambda n: (n.total_cards, n.get_mastery_percentage()),
            reverse=True
        )[:10]  # Top 10 key concepts
        
        return [
            {
                "name": node.name,
                "connections": self._count_node_connections(node.id),
                "mastery": node.get_mastery_percentage(),
                "total_cards": node.total_cards
            }
            for node in key_concepts
        ]
    
    def _count_node_connections(self, node_id: str) -> int:
        """Count connections for a node."""
        if not self._current_graph:
            return 0
        
        return len([
            rel for rel in self._current_graph.relationships
            if rel.source_id == node_id or rel.target_id == node_id
        ])
    
    def _calculate_avg_path_length(self) -> float:
        """Calculate average learning path length."""
        if not self._current_graph or not self._current_graph.learning_paths:
            return 0.0
        
        total_length = sum(len(path.nodes) for path in self._current_graph.learning_paths)
        return total_length / len(self._current_graph.learning_paths)
    
    def _find_most_connected_concept(self) -> Optional[str]:
        """Find the most connected concept."""
        if not self._current_graph:
            return None
        
        concept_nodes = [n for n in self._current_graph.nodes if n.node_type.value == "concept"]
        
        if not concept_nodes:
            return None
        
        most_connected = max(
            concept_nodes,
            key=lambda n: self._count_node_connections(n.id)
        )
        
        return most_connected.name
    
    def _calculate_complexity_score(self, metrics) -> float:
        """Calculate a complexity score for the graph."""
        # Simple complexity score based on nodes, edges, and density
        if metrics.node_count == 0:
            return 0.0
        
        # Normalize components
        node_complexity = min(metrics.node_count / 20, 1.0)  # Max at 20 nodes
        edge_complexity = min(metrics.edge_count / 50, 1.0)  # Max at 50 edges
        density_complexity = metrics.density
        
        # Weighted average
        complexity = (node_complexity * 0.4 + edge_complexity * 0.4 + density_complexity * 0.2)
        
        return round(complexity, 2)
