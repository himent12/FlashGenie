"""
Knowledge graph visualization utilities.

This module provides functions for visualizing and exporting knowledge graphs.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json

from .models import (
    KnowledgeGraph, VisualizationConfig, GraphMetrics
)


class KnowledgeGraphVisualizer:
    """Handles visualization and export of knowledge graphs."""
    
    def __init__(self):
        """Initialize the visualizer."""
        self.config = VisualizationConfig()
    
    def export_html(self, graph: KnowledgeGraph, output_path: Path, config: Optional[VisualizationConfig] = None) -> None:
        """
        Export knowledge graph as interactive HTML visualization.
        
        Args:
            graph: The knowledge graph to visualize
            output_path: Path to save the HTML file
            config: Optional visualization configuration
        """
        if config:
            self.config = config
        
        # Get graph data for visualization
        graph_data = graph.export_for_visualization()
        
        # Generate HTML content
        html_content = self._generate_html_visualization(graph_data)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def export_json(self, graph: KnowledgeGraph, output_path: Path) -> None:
        """
        Export knowledge graph as JSON data.
        
        Args:
            graph: The knowledge graph to export
            output_path: Path to save the JSON file
        """
        graph_data = graph.export_for_visualization()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
    
    def calculate_metrics(self, graph: KnowledgeGraph) -> GraphMetrics:
        """
        Calculate metrics for the knowledge graph.
        
        Args:
            graph: The knowledge graph to analyze
            
        Returns:
            Graph metrics
        """
        node_count = len(graph.nodes)
        edge_count = len(graph.relationships)
        
        # Count clusters
        cluster_count = len([n for n in graph.nodes if n.node_type.value == "cluster"])
        
        # Calculate average degree
        if node_count > 0:
            total_degree = edge_count * 2  # Each edge contributes to 2 nodes
            average_degree = total_degree / node_count
        else:
            average_degree = 0.0
        
        # Calculate density
        if node_count > 1:
            max_edges = node_count * (node_count - 1) / 2
            density = edge_count / max_edges
        else:
            density = 0.0
        
        # Simple connected components calculation
        connected_components = self._count_connected_components(graph)
        
        return GraphMetrics(
            node_count=node_count,
            edge_count=edge_count,
            cluster_count=cluster_count,
            average_degree=average_degree,
            density=density,
            connected_components=connected_components
        )
    
    def _generate_html_visualization(self, graph_data: Dict[str, Any]) -> str:
        """Generate HTML content for graph visualization."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlashGenie Knowledge Graph</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2em;
        }}
        
        .controls {{
            padding: 15px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .controls button {{
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            margin: 0 5px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
        
        .controls button:hover {{
            background: #0056b3;
        }}
        
        .graph-container {{
            position: relative;
            height: 600px;
            overflow: hidden;
        }}
        
        .node {{
            stroke: #fff;
            stroke-width: 2px;
            cursor: pointer;
        }}
        
        .node:hover {{
            stroke-width: 3px;
        }}
        
        .link {{
            stroke: #999;
            stroke-opacity: 0.6;
            stroke-width: 1px;
        }}
        
        .node-label {{
            font-size: 12px;
            font-weight: bold;
            text-anchor: middle;
            pointer-events: none;
            fill: #333;
        }}
        
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 8px;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
        }}
        
        .legend {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 4px;
            font-size: 12px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 2px 0;
        }}
        
        .legend-color {{
            width: 12px;
            height: 12px;
            margin-right: 5px;
            border-radius: 2px;
        }}
        
        .stats {{
            padding: 15px;
            background: #f8f9fa;
            border-top: 1px solid #dee2e6;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧞‍♂️ FlashGenie Knowledge Graph</h1>
            <p>Visual representation of your learning progress and concept relationships</p>
        </div>
        
        <div class="controls">
            <button onclick="resetZoom()">Reset View</button>
            <button onclick="toggleLabels()">Toggle Labels</button>
            <button onclick="highlightPaths()">Highlight Paths</button>
            <button onclick="filterWeakEdges()">Filter Weak Edges</button>
        </div>
        
        <div class="graph-container">
            <svg id="graph"></svg>
            <div class="tooltip" id="tooltip"></div>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: #aaffaa;"></div>
                    <span>Mastered</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #ccffcc;"></div>
                    <span>Proficient</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #ffffaa;"></div>
                    <span>Developing</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #ffddaa;"></div>
                    <span>Practicing</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #ffcccc;"></div>
                    <span>Introduced</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #cccccc;"></div>
                    <span>Unknown</span>
                </div>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">{len(graph_data.get('nodes', []))}</div>
                <div class="stat-label">Concepts</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(graph_data.get('edges', []))}</div>
                <div class="stat-label">Connections</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(graph_data.get('paths', []))}</div>
                <div class="stat-label">Learning Paths</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(graph_data.get('gaps', []))}</div>
                <div class="stat-label">Knowledge Gaps</div>
            </div>
        </div>
    </div>

    <script>
        // Graph data
        const graphData = {json.dumps(graph_data, indent=2)};
        
        // Set up SVG
        const svg = d3.select("#graph");
        const container = d3.select(".graph-container");
        const width = container.node().getBoundingClientRect().width;
        const height = container.node().getBoundingClientRect().height;
        
        svg.attr("width", width).attr("height", height);
        
        // Create zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }});
        
        svg.call(zoom);
        
        // Create main group
        const g = svg.append("g");
        
        // Create force simulation
        const simulation = d3.forceSimulation(graphData.nodes)
            .force("link", d3.forceLink(graphData.edges).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(d => d.size * 20 + 5));
        
        // Create links
        const link = g.append("g")
            .selectAll("line")
            .data(graphData.edges)
            .enter().append("line")
            .attr("class", "link")
            .style("stroke-width", d => Math.sqrt(d.strength * 3));
        
        // Create nodes
        const node = g.append("g")
            .selectAll("circle")
            .data(graphData.nodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", d => d.size * 15)
            .style("fill", d => d.color)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended))
            .on("mouseover", showTooltip)
            .on("mouseout", hideTooltip);
        
        // Create labels
        const labels = g.append("g")
            .selectAll("text")
            .data(graphData.nodes)
            .enter().append("text")
            .attr("class", "node-label")
            .text(d => d.name)
            .style("font-size", d => Math.max(10, d.size * 8) + "px");
        
        // Update positions on simulation tick
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
            
            labels
                .attr("x", d => d.x)
                .attr("y", d => d.y + 4);
        }});
        
        // Drag functions
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        // Tooltip functions
        function showTooltip(event, d) {{
            const tooltip = d3.select("#tooltip");
            tooltip.style("opacity", 1)
                .html(`
                    <strong>${{d.name}}</strong><br>
                    Type: ${{d.type}}<br>
                    Mastery: ${{(d.mastery_percentage * 100).toFixed(1)}}%<br>
                    Cards: ${{d.mastered_cards}}/${{d.total_cards}}
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        }}
        
        function hideTooltip() {{
            d3.select("#tooltip").style("opacity", 0);
        }}
        
        // Control functions
        function resetZoom() {{
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity
            );
        }}
        
        let labelsVisible = true;
        function toggleLabels() {{
            labelsVisible = !labelsVisible;
            labels.style("opacity", labelsVisible ? 1 : 0);
        }}
        
        function highlightPaths() {{
            // Simple path highlighting - can be enhanced
            link.style("stroke", d => d.type === "prerequisite" ? "#ff6b6b" : "#999");
        }}
        
        let weakEdgesFiltered = false;
        function filterWeakEdges() {{
            weakEdgesFiltered = !weakEdgesFiltered;
            link.style("opacity", d => {{
                if (weakEdgesFiltered && d.strength < 0.3) {{
                    return 0.1;
                }}
                return 0.6;
            }});
        }}
    </script>
</body>
</html>
        """
    
    def _count_connected_components(self, graph: KnowledgeGraph) -> int:
        """Count connected components in the graph."""
        if not graph.nodes:
            return 0
        
        # Simple connected components counting
        visited = set()
        components = 0
        
        # Create adjacency list
        adjacency = {}
        for node in graph.nodes:
            adjacency[node.id] = set()
        
        for rel in graph.relationships:
            if rel.source_id in adjacency and rel.target_id in adjacency:
                adjacency[rel.source_id].add(rel.target_id)
                adjacency[rel.target_id].add(rel.source_id)
        
        # DFS to find components
        def dfs(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            for neighbor in adjacency.get(node_id, []):
                dfs(neighbor)
        
        for node in graph.nodes:
            if node.id not in visited:
                dfs(node.id)
                components += 1
        
        return components
