"""
Graph Database Manager

This module provides graph database functionality for storing and querying
relationships between entities. It supports:
- Node and edge management
- Graph traversal (BFS, DFS)
- Path finding (shortest path, all paths)
- Relationship queries
- Graph analytics (degree, centrality, clustering)
- Persistence (save/load)
- Optional NetworkX integration for advanced algorithms

Author: HyFuzz Team
Version: 2.0.0
"""

from __future__ import annotations
import json
import logging
import pickle
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any, Callable
from collections import defaultdict, deque

# Optional NetworkX import for advanced graph algorithms
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False


@dataclass
class Node:
    """Graph node with properties"""
    id: str
    properties: Dict[str, Any] = field(default_factory=dict)
    labels: Set[str] = field(default_factory=set)


@dataclass
class Edge:
    """Graph edge with properties"""
    source: str
    target: str
    relationship_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    directed: bool = True


class GraphDBManager:
    """
    Graph Database Manager

    Manages nodes, edges, and relationships with support for
    graph traversal, path finding, and analytics.

    Example:
        >>> db = GraphDBManager()
        >>> db.add_node("CVE-2024-1234", {"severity": "high"}, ["vulnerability"])
        >>> db.add_node("CWE-89", {"name": "SQL Injection"}, ["weakness"])
        >>> db.add_edge("CVE-2024-1234", "CWE-89", "EXPLOITS")
        >>> paths = db.find_shortest_path("CVE-2024-1234", "CWE-89")
    """

    def __init__(self, use_networkx: bool = True):
        """
        Initialize Graph Database

        Args:
            use_networkx: Use NetworkX for advanced algorithms if available
        """
        self.logger = logging.getLogger(__name__)
        self.use_networkx = use_networkx and NETWORKX_AVAILABLE

        # Storage
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []

        # Adjacency lists for fast traversal
        self.outgoing_edges: Dict[str, List[Edge]] = defaultdict(list)
        self.incoming_edges: Dict[str, List[Edge]] = defaultdict(list)

        # NetworkX graph for advanced algorithms
        self.nx_graph = None
        if self.use_networkx:
            self.nx_graph = nx.DiGraph()

        self.logger.info(f"Graph DB initialized: networkx={self.use_networkx}")

    def add_node(
        self,
        node_id: str,
        properties: Optional[Dict[str, Any]] = None,
        labels: Optional[List[str]] = None
    ) -> None:
        """
        Add or update node

        Args:
            node_id: Unique node identifier
            properties: Node properties
            labels: Node labels/types
        """
        node = Node(
            id=node_id,
            properties=properties or {},
            labels=set(labels or [])
        )

        self.nodes[node_id] = node

        if self.use_networkx and self.nx_graph is not None:
            self.nx_graph.add_node(node_id, **properties or {})

        self.logger.debug(f"Added node: {node_id}, labels={labels}")

    def add_nodes_batch(self, nodes: List[Tuple[str, Dict[str, Any], List[str]]]) -> None:
        """
        Add multiple nodes efficiently

        Args:
            nodes: List of (node_id, properties, labels) tuples
        """
        for node_id, properties, labels in nodes:
            self.add_node(node_id, properties, labels)

        self.logger.info(f"Added {len(nodes)} nodes in batch")

    def add_edge(
        self,
        source: str,
        target: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
        directed: bool = True
    ) -> None:
        """
        Add edge between nodes

        Args:
            source: Source node ID
            target: Target node ID
            relationship_type: Type of relationship
            properties: Edge properties
            directed: Whether edge is directed
        """
        # Ensure nodes exist
        if source not in self.nodes:
            self.add_node(source)
        if target not in self.nodes:
            self.add_node(target)

        edge = Edge(
            source=source,
            target=target,
            relationship_type=relationship_type,
            properties=properties or {},
            directed=directed
        )

        self.edges.append(edge)
        self.outgoing_edges[source].append(edge)
        self.incoming_edges[target].append(edge)

        # Add to NetworkX graph
        if self.use_networkx and self.nx_graph is not None:
            self.nx_graph.add_edge(
                source,
                target,
                relationship=relationship_type,
                **(properties or {})
            )

        self.logger.debug(
            f"Added edge: {source} -{relationship_type}-> {target}, "
            f"directed={directed}"
        )

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get node by ID"""
        return self.nodes.get(node_id)

    def get_neighbors(
        self,
        node_id: str,
        relationship_type: Optional[str] = None,
        direction: str = 'outgoing'
    ) -> List[str]:
        """
        Get neighboring nodes

        Args:
            node_id: Node ID
            relationship_type: Filter by relationship type
            direction: 'outgoing', 'incoming', or 'both'

        Returns:
            List of neighbor node IDs
        """
        neighbors = []

        if direction in ('outgoing', 'both'):
            for edge in self.outgoing_edges.get(node_id, []):
                if relationship_type is None or edge.relationship_type == relationship_type:
                    neighbors.append(edge.target)

        if direction in ('incoming', 'both'):
            for edge in self.incoming_edges.get(node_id, []):
                if relationship_type is None or edge.relationship_type == relationship_type:
                    neighbors.append(edge.source)

        return neighbors

    def find_shortest_path(
        self,
        source: str,
        target: str,
        relationship_type: Optional[str] = None
    ) -> Optional[List[str]]:
        """
        Find shortest path between nodes

        Args:
            source: Source node ID
            target: Target node ID
            relationship_type: Filter by relationship type

        Returns:
            List of node IDs forming the path, or None if no path exists
        """
        if source not in self.nodes or target not in self.nodes:
            return None

        # Use NetworkX if available
        if self.use_networkx and self.nx_graph is not None:
            try:
                return nx.shortest_path(self.nx_graph, source, target)
            except nx.NetworkXNoPath:
                return None

        # BFS fallback
        return self._bfs_shortest_path(source, target, relationship_type)

    def _bfs_shortest_path(
        self,
        source: str,
        target: str,
        relationship_type: Optional[str]
    ) -> Optional[List[str]]:
        """BFS-based shortest path finding"""
        if source == target:
            return [source]

        queue = deque([(source, [source])])
        visited = {source}

        while queue:
            current, path = queue.popleft()

            for neighbor in self.get_neighbors(current, relationship_type, 'outgoing'):
                if neighbor in visited:
                    continue

                new_path = path + [neighbor]

                if neighbor == target:
                    return new_path

                visited.add(neighbor)
                queue.append((neighbor, new_path))

        return None

    def find_all_paths(
        self,
        source: str,
        target: str,
        max_depth: int = 10,
        relationship_type: Optional[str] = None
    ) -> List[List[str]]:
        """
        Find all paths between nodes

        Args:
            source: Source node ID
            target: Target node ID
            max_depth: Maximum path length
            relationship_type: Filter by relationship type

        Returns:
            List of paths (each path is a list of node IDs)
        """
        if source not in self.nodes or target not in self.nodes:
            return []

        # Use NetworkX if available
        if self.use_networkx and self.nx_graph is not None:
            try:
                return list(nx.all_simple_paths(
                    self.nx_graph,
                    source,
                    target,
                    cutoff=max_depth
                ))
            except nx.NetworkXNoPath:
                return []

        # DFS fallback
        return self._dfs_all_paths(source, target, max_depth, relationship_type)

    def _dfs_all_paths(
        self,
        source: str,
        target: str,
        max_depth: int,
        relationship_type: Optional[str]
    ) -> List[List[str]]:
        """DFS-based all paths finding"""
        all_paths = []

        def dfs(current: str, path: List[str], depth: int):
            if depth > max_depth:
                return

            if current == target:
                all_paths.append(path.copy())
                return

            for neighbor in self.get_neighbors(current, relationship_type, 'outgoing'):
                if neighbor not in path:  # Avoid cycles
                    path.append(neighbor)
                    dfs(neighbor, path, depth + 1)
                    path.pop()

        dfs(source, [source], 0)
        return all_paths

    def traverse_bfs(
        self,
        start_node: str,
        visitor: Optional[Callable[[str, int], None]] = None,
        max_depth: Optional[int] = None
    ) -> List[str]:
        """
        Breadth-first traversal

        Args:
            start_node: Starting node ID
            visitor: Optional callback function(node_id, depth)
            max_depth: Maximum traversal depth

        Returns:
            List of visited node IDs in BFS order
        """
        if start_node not in self.nodes:
            return []

        visited = []
        queue = deque([(start_node, 0)])
        seen = {start_node}

        while queue:
            current, depth = queue.popleft()

            if max_depth is not None and depth > max_depth:
                continue

            visited.append(current)

            if visitor:
                visitor(current, depth)

            for neighbor in self.get_neighbors(current, None, 'outgoing'):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append((neighbor, depth + 1))

        return visited

    def traverse_dfs(
        self,
        start_node: str,
        visitor: Optional[Callable[[str, int], None]] = None,
        max_depth: Optional[int] = None
    ) -> List[str]:
        """
        Depth-first traversal

        Args:
            start_node: Starting node ID
            visitor: Optional callback function(node_id, depth)
            max_depth: Maximum traversal depth

        Returns:
            List of visited node IDs in DFS order
        """
        if start_node not in self.nodes:
            return []

        visited = []
        seen = set()

        def dfs(current: str, depth: int):
            if max_depth is not None and depth > max_depth:
                return

            if current in seen:
                return

            seen.add(current)
            visited.append(current)

            if visitor:
                visitor(current, depth)

            for neighbor in self.get_neighbors(current, None, 'outgoing'):
                dfs(neighbor, depth + 1)

        dfs(start_node, 0)
        return visited

    def query_nodes(
        self,
        labels: Optional[List[str]] = None,
        property_filter: Optional[Dict[str, Any]] = None
    ) -> List[Node]:
        """
        Query nodes by labels and properties

        Args:
            labels: Filter by node labels
            property_filter: Filter by properties

        Returns:
            List of matching nodes
        """
        results = []

        for node in self.nodes.values():
            # Check labels
            if labels and not any(label in node.labels for label in labels):
                continue

            # Check properties
            if property_filter:
                match = all(
                    node.properties.get(key) == value
                    for key, value in property_filter.items()
                )
                if not match:
                    continue

            results.append(node)

        return results

    def get_node_degree(self, node_id: str, direction: str = 'both') -> int:
        """
        Get node degree (number of connections)

        Args:
            node_id: Node ID
            direction: 'outgoing', 'incoming', or 'both'

        Returns:
            Node degree
        """
        degree = 0

        if direction in ('outgoing', 'both'):
            degree += len(self.outgoing_edges.get(node_id, []))

        if direction in ('incoming', 'both'):
            degree += len(self.incoming_edges.get(node_id, []))

        return degree

    def get_connected_components(self) -> List[Set[str]]:
        """
        Get connected components in the graph

        Returns:
            List of sets, each containing node IDs in a component
        """
        if self.use_networkx and self.nx_graph is not None:
            # Use NetworkX for undirected components
            undirected = self.nx_graph.to_undirected()
            return [set(component) for component in nx.connected_components(undirected)]

        # Fallback: simple DFS-based component finding
        components = []
        visited = set()

        for node_id in self.nodes:
            if node_id not in visited:
                component = set()
                stack = [node_id]

                while stack:
                    current = stack.pop()
                    if current in visited:
                        continue

                    visited.add(current)
                    component.add(current)

                    # Add all neighbors (treat as undirected)
                    neighbors = self.get_neighbors(current, None, 'both')
                    stack.extend(n for n in neighbors if n not in visited)

                components.append(component)

        return components

    def delete_node(self, node_id: str) -> bool:
        """
        Delete node and all connected edges

        Args:
            node_id: Node ID to delete

        Returns:
            True if deleted, False if not found
        """
        if node_id not in self.nodes:
            return False

        # Remove node
        del self.nodes[node_id]

        # Remove connected edges
        self.edges = [
            e for e in self.edges
            if e.source != node_id and e.target != node_id
        ]

        # Update adjacency lists
        del self.outgoing_edges[node_id]
        del self.incoming_edges[node_id]

        # Clean up references in other adjacency lists
        for edges in self.outgoing_edges.values():
            edges[:] = [e for e in edges if e.target != node_id]

        for edges in self.incoming_edges.values():
            edges[:] = [e for e in edges if e.source != node_id]

        # Remove from NetworkX
        if self.use_networkx and self.nx_graph is not None:
            self.nx_graph.remove_node(node_id)

        self.logger.debug(f"Deleted node: {node_id}")
        return True

    def clear(self) -> None:
        """Clear all nodes and edges"""
        self.nodes.clear()
        self.edges.clear()
        self.outgoing_edges.clear()
        self.incoming_edges.clear()

        if self.use_networkx and self.nx_graph is not None:
            self.nx_graph.clear()

        self.logger.info("Graph database cleared")

    def size(self) -> Tuple[int, int]:
        """
        Get graph size

        Returns:
            Tuple of (node_count, edge_count)
        """
        return len(self.nodes), len(self.edges)

    def save(self, filepath: str | Path) -> None:
        """
        Save graph to file

        Args:
            filepath: Path to save file (.pkl)
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'nodes': {
                node_id: {
                    'properties': node.properties,
                    'labels': list(node.labels)
                }
                for node_id, node in self.nodes.items()
            },
            'edges': [
                {
                    'source': edge.source,
                    'target': edge.target,
                    'relationship_type': edge.relationship_type,
                    'properties': edge.properties,
                    'directed': edge.directed
                }
                for edge in self.edges
            ]
        }

        with open(filepath, 'wb') as f:
            pickle.dump(data, f)

        self.logger.info(
            f"Saved graph to {filepath}: "
            f"{len(self.nodes)} nodes, {len(self.edges)} edges"
        )

    @classmethod
    def load(cls, filepath: str | Path, use_networkx: bool = True) -> 'GraphDBManager':
        """
        Load graph from file

        Args:
            filepath: Path to load file
            use_networkx: Use NetworkX

        Returns:
            Loaded GraphDBManager instance
        """
        with open(filepath, 'rb') as f:
            data = pickle.load(f)

        # Create new instance
        db = cls(use_networkx=use_networkx)

        # Restore nodes
        for node_id, node_data in data['nodes'].items():
            db.add_node(
                node_id,
                node_data['properties'],
                node_data['labels']
            )

        # Restore edges
        for edge_data in data['edges']:
            db.add_edge(
                edge_data['source'],
                edge_data['target'],
                edge_data['relationship_type'],
                edge_data['properties'],
                edge_data['directed']
            )

        db.logger.info(
            f"Loaded graph from {filepath}: "
            f"{len(db.nodes)} nodes, {len(db.edges)} edges"
        )
        return db

    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        node_count, edge_count = self.size()

        stats = {
            'node_count': node_count,
            'edge_count': edge_count,
            'use_networkx': self.use_networkx,
            'avg_degree': edge_count * 2 / node_count if node_count > 0 else 0,
        }

        if self.use_networkx and self.nx_graph is not None:
            try:
                stats['density'] = nx.density(self.nx_graph)
                stats['is_connected'] = nx.is_weakly_connected(self.nx_graph)
            except Exception:
                pass

        return stats


def _self_test() -> bool:
    """Basic smoke test for module."""
    try:
        # Create graph
        db = GraphDBManager()

        # Add nodes
        db.add_node("CVE-2024-1234", {"severity": "high", "score": 9.8}, ["vulnerability"])
        db.add_node("CVE-2024-5678", {"severity": "medium", "score": 6.5}, ["vulnerability"])
        db.add_node("CWE-89", {"name": "SQL Injection"}, ["weakness"])
        db.add_node("CWE-79", {"name": "XSS"}, ["weakness"])

        # Add edges
        db.add_edge("CVE-2024-1234", "CWE-89", "EXPLOITS")
        db.add_edge("CVE-2024-5678", "CWE-79", "EXPLOITS")
        db.add_edge("CWE-89", "CWE-79", "RELATED_TO", directed=False)

        # Test queries
        neighbors = db.get_neighbors("CVE-2024-1234")
        assert "CWE-89" in neighbors

        # Test path finding
        path = db.find_shortest_path("CVE-2024-1234", "CWE-89")
        assert path == ["CVE-2024-1234", "CWE-89"]

        # Test traversal
        visited = db.traverse_bfs("CVE-2024-1234")
        assert len(visited) >= 2

        # Test queries
        vulns = db.query_nodes(labels=["vulnerability"])
        assert len(vulns) == 2

        high_severity = db.query_nodes(property_filter={"severity": "high"})
        assert len(high_severity) == 1

        # Test stats
        stats = db.get_stats()
        assert stats['node_count'] == 4
        assert stats['edge_count'] == 3

        print(f"Graph DB self-test passed! Stats: {stats}")
        return True

    except Exception as exc:
        print(f"Self test failed: {exc}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    print("="*70)
    print("GRAPH DATABASE MANAGER - SELF TEST")
    print("="*70)
    print(f"NetworkX available: {NETWORKX_AVAILABLE}")
    print()

    success = _self_test()
    print()
    print("="*70)
    print(f"Result: {'✅ PASSED' if success else '❌ FAILED'}")
    print("="*70)
