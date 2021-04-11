"""
Here we will define our Graph and _PackageVertex classes.
These two classes will be very similar to the ones learned
in class, and will makeup our Graph Data Structure.
"""
from __future__ import annotations
import csv
import pandas as pd
import ast
from typing import Any, Callable
import graphviz as gviz
import networkx as nx
import plotly.graph_objects as plot
import scipy
import pydot

import streamlit as st

class _PackageVertex:
    """A vertex representing one package.
    
    The properties upstream_dependencies and downstream_dependencies are used to 
    define edges in the graph.
    
    Attributes:
        - name: The name of the package
        - version: The version of the package at the time the data was gathered
        - description: A short piece of text describing the purpose of the package.
        - keywords: A list of words describing the category of the package's purpose
        - dependencies: A list of strings representing upstream dependencies
        - devDependencies: A list of other packages used to maintain the package (not 
                           necessary to use the package)
        - comunityInterest: An indication popularity indicator
        - downloadsCount: The number of times the package has been downloaded
        - downloadsAcceleration: SOMETHING THAT I DON'T UNDERSTAND
        - dependentsCount: The total number of packages in the entire database of
                           npm packages that depend on this package
        - quality: An indicator developed by npms.io
        - popularity: An indicator developed by npms.io
        - maintenance: An indicator developed by npms.io
        - upstream_dependencies: A list of Vertices representing upstream dependencies
        - downstream_dependencies: A list of Vertices representing downstream dependencies
        - keyword_relationships: A list of Vertices that share keywords with self
    """
    name: str
    version: str
    description: str
    keywords: list[str]
    dependencies: dict[str, str]
    devDependencies: dict[str, str]
    communityInterest: float
    downloadsCount: int
    downloadsAcceleration: float
    dependentsCount: int
    quality: float
    popularity: float
    maintenance: float
    upstream_dependencies: set[_PackageVertex]
    downstream_dependencies: set[_PackageVertex]
    keyword_relationships: dict[_PackageVertex]

    def __init__(self, package_data: list) -> None:
        """The constructor for our vertex."""
        self.name = package_data[0]
        self.version = package_data[1]
        self.description = package_data[2]
        self.keywords = package_data[3]
        self.dependencies = package_data[4]
        self.devDependencies = package_data[5]
        self.communityInterest = package_data[6]
        self.downloadsCount = package_data[7]
        self.downloadsAcceleration = package_data[8]
        self.dependentsCount = package_data[9]
        self.quality = package_data[10]
        self.popularity = package_data[11]
        self.maintenance = package_data[12]
    
        self.upstream_dependencies = set()
        self.downstream_dependencies = set()
        self.keyword_relationships = dict()
        
    def add_upstream_dependency(self, other: _PackageVertex) -> None:
        """Add other to this vertex's upstream dependencies"""
        self.upstream_dependencies.add(other)

    def add_downstream_dependency(self, other: _PackageVertex) -> None:
        """Add other to this vertex's upstream dependencies"""
        self.downstream_dependencies.add(other)

    def add_keyword_relationship(self, other: _PackageVertex, keyword: 'str') -> None:
        """Add other to this vertex's upstream dependencies"""
        if keyword in self.keyword_relationships:
            self.keyword_relationships[keyword].add(other)
        else:
            self.keyword_relationships[keyword] = {other}
    
    def get_num_dependencies(self, visited: set) -> int:
        """
        Return all upstream dependencies, including dependencies of dependencies
        
        Apply the graph traversal pattern taught in class
        """
        visited.add(self)
        total = 0
        for vertex in self.upstream_dependencies:
            if vertex not in visited:
                total = total + 1 + vertex.get_num_dependencies(visited)
        return total
    
    def get_package_dependencies(self, visited: set) -> list[tuple[str, str]]:
        """
        Return a list of tuples with one tupple for every edge that this node is connected to,
        as well as a tupple for every upstream dependency edge.

        The first string in the tupple is the dependent and the second string is the dependency

        Apply the graph traversal pattern taught in class
        """
        new_visited = visited.union({self})
        relationships_so_far = []
        for vertex in self.upstream_dependencies:
            if vertex not in visited:
                relationships_so_far.append((self.name, vertex.name))
                relationships_so_far.extend(vertex.get_package_dependencies(new_visited))
        return relationships_so_far
    
    
    def get_package_dependencies_depth(self, visited: set, depth: int) -> list[list[str, str, int]]:
        """
        Return a list of tuples with one tupple for every edge that this node is connected to,
        as well as a tupple for every upstream dependency edge.

        The first string in the tupple is the dependent and the second string is the dependency

        Apply the graph traversal pattern taught in class
        """
        new_visited = visited.union({self})
        relationships_so_far = []
        for vertex in self.upstream_dependencies:
            if vertex not in visited:
                relationships_so_far.append((self.name, vertex.name, depth + 1))
                relationships_so_far.extend(vertex.get_package_dependencies_depth(new_visited, depth + 1))
        return relationships_so_far


class PackageGraph:
    """A graph representing the relationship between packages.

    Attributes:
        - _vertices: A dictionary of all vertices in this graph. 
        Each key is a package name, and each value is a _PackageVertex object.
    """
    _vertices: dict[str, _PackageVertex]
    
    def __init__(self, package_rows: list[list]) -> None:
        """Initialize the graph of packages with the package data.
        """
        self._vertices = {}
    
        # Add packages as vertices
        for row in package_rows:
            self.add_vertex(row)

        print('Constructing Dependency edges...')
        self.construct_dependency_edges()
        print('Constructing Keyword edges...')
        self.construct_keyword_edges()

    def add_vertex(self, row: list) -> None:
        """Add a _PackageVertex to this graph with the data contained in
        row. The vertex is reffered to by it's package name, at row[0].
        
        Assumes that row matches the format described by HEADER in assemble_data.py2.
        """
        self._vertices[row[0]] = _PackageVertex(row)

    def has_vertex(self, item: str) -> None:
        """Check if item is a vertex in this graph.
        """
        return item in self._vertices

    def construct_dependency_edges(self) -> None:
        """Form the appropriate dependency edges between all vertices in self._vertices.
        """
        for vertex in self._vertices:
            for dependency in self._vertices[vertex].dependencies:
                if dependency in self._vertices:
                    self.add_dependency_edges(dependency, vertex)

    def add_dependency_edges(self, upstream_package: str, downstream_package: str) -> None:
        """Add an edge between the two vertices specified as parameters: one
        recieves a downstream edge, the other recieves an upstream edge. 
        """
        if upstream_package in self._vertices and downstream_package in self._vertices:
            downstream_vertex = self._vertices[downstream_package]
            upstream_vertex = self._vertices[upstream_package]

            downstream_vertex.add_upstream_dependency(upstream_vertex)
            upstream_vertex.add_downstream_dependency(downstream_vertex)
        else:
            raise KeyError(f'The vertices {upstream_package} or {downstream_package}'\
                           'do not exist in this graph')

    def construct_keyword_edges(self) -> None:
        """Form the approriate keyword edges between all vertices in self._vertices.
        """
        keywords: dict[str, list[str]] = {}
        for vertex in self._vertices:
            for keyword in self._vertices[vertex].keywords:
                if keyword not in keywords:
                    keywords[keyword] = [vertex]
                else:
                    keywords[keyword].append(vertex)

        i = 0
        for keyword in keywords:
            i += 0
            keyword_list = keywords[keyword]
            for first in range(0, len(keyword_list) - 1):
                for second in range(first + 1, len(keyword_list)):
                    self.add_keyword_edge(keyword_list[first], keyword_list[second], keyword)
            
    def add_keyword_edge(self, package1: str, package2: str, keyword: str) -> None:
        """Add a keyword edge between the two vertices specified as parameters.
        """
        if package1 in self._vertices and package2 in self._vertices:
            package1_v = self._vertices[package1]
            package2_v = self._vertices[package2]

            package1_v.add_keyword_relationship(package2_v, keyword)
            package2_v.add_keyword_relationship(package1_v, keyword)
        else:
            raise KeyError(f'The vertices {package1} or {package2}'\
                           'do not exist in this graph')
    
    def get_num_dependencies(self, package: str) -> int:
        """
        Return the number of dependencies of the given package.

        Include dependencies of dependencies in the count, by using the
        common graph traversal pattern to traverse all relavent nodes in the graph
        """
        if package in self._vertices:
            vertex = self._vertices[package]
            return vertex.get_num_dependencies(set())
        else:
            raise KeyError(f'A vertex with the name {package} does not exist in this graph')

    def popular_package_data(self) -> tuple[list[str], list[int]]:
        """Return dependency data on some hard-coded popular packages."""
        popular_packages = [
            'react',
            'firebase',
            'express',
            'graphql',
            'vue',
            'async',
            'jquery',
            'bootstrap',
        ]
        num_dependencies = []
        for package in popular_packages:
            num_dependencies.append(self.get_num_dependencies(package))
        return (popular_packages, num_dependencies)
        
    def get_package_dependencies(self, package: str) -> list[tuple[str, str]]:
        """ 
        Return a list containing tuples containing two package names

        Each tuple in the list represents an edge between the two packages contained by the tuple
        """
        if package in self._vertices:
            vertex = self._vertices[package]
            return vertex.get_package_dependencies(set())        
        else:
            raise KeyError(f'A vertex with the name {package} does not exist in this graph')
         
    def get_package_dependencies_depth(self, package: str) -> list[tuple[str, str, int]]:
        """ 
        Return a list containing tuples containing two package names

        Each tuple in the list represents an edge between the two packages contained by the tuple
        """
        if package in self._vertices:
            vertex = self._vertices[package]
            return vertex.get_package_dependencies_depth(set(), 0)        
        else:
            raise KeyError(f'A vertex with the name {package} does not exist in this graph')

    def get_package_digraph(self, package: str) -> gviz.Digraph:
        """
        Return a graphviz digraph object used to visualize package dependencies
        """
        if package in self._vertices:
            digraph = gviz.Digraph()
            for edge in self.get_package_dependencies(package):
                digraph.edge(edge[0], edge[1])

            return digraph
        else:
            raise KeyError(f'A vertex with the name {package} does not exist in this graph')

    def get_package_graph_networkx(self, package: str) -> nx.Graph:
        """
        Convert this graph to a networkx.
        """
        if package in self._vertices:
            netxG = nx.Graph()
            for edge in self.get_package_dependencies(package):
                netxG.add_edge(*edge)  # The * converts the tuple to two parameters
            return netxG
        else:
            raise KeyError(f'A vertex with the name {package} does not exist in this graph')

    def get_package_plotly(self, package: str, layout_algo: callable):
        """
        Return a plotly graph object used to visualize package dependencies.
        
        Inspired by https://plotly.com/python/network-graphs/.
        """
        if hasattr(nx, layout_algo.__name__):
            graph = self.get_package_graph_networkx(package)
            vertex_pos = layout_algo(graph)

            edge_pos_x = []
            edge_pos_y = []
            for edge in graph.edges(): 
                node_a_x, node_a_y = vertex_pos[edge[0]]
                node_b_x, node_b_y = vertex_pos[edge[1]]
                edge_pos_x.append(node_a_x)
                edge_pos_x.append(node_b_x)
                edge_pos_x.append(None)
                edge_pos_y.append(node_a_y)
                edge_pos_y.append(node_b_y)
                edge_pos_y.append(None)       

            node_pos_x = []
            node_pos_y = []
            for node in graph.nodes():
                node_pos = vertex_pos[node]
                node_pos_x.append(node_pos[0])
                node_pos_y.append(node_pos[1])
        else:
            edges = self.get_package_dependencies_depth(package)
            vertex_pos = danman_layout(edges)

            edge_pos_x = []
            edge_pos_y = []
            for edge in edges: 
                node_a_x, node_a_y = vertex_pos[edge[0]]
                node_b_x, node_b_y = vertex_pos[edge[1]]
                edge_pos_x.append(node_a_x)
                edge_pos_x.append(node_b_x)
                edge_pos_x.append(None)
                edge_pos_y.append(node_a_y)
                edge_pos_y.append(node_b_y)
                edge_pos_y.append(None)       

            node_pos_x = []
            node_pos_y = []
            for node in vertex_pos:
                node_pos = vertex_pos[node]
                node_pos_x.append(node_pos[0])
                node_pos_y.append(node_pos[1])
            

        node_scatter = plot.Scatter(
            marker=dict(size=7),            
            x=node_pos_x,
            y=node_pos_y,
            mode='markers+text',
            name='Packages',
            text=list(vertex_pos.keys()),
            hoverinfo='text',
            textposition='top center',
            textfont_size=9
        )

        edge_scatter = plot.Scatter(
            x=edge_pos_x, y=edge_pos_y,
            mode='lines+text',
            name='Edges',
            line=dict(width=1, color="#a6caed")
        )

        origin_pos_x, origin_pos_y = vertex_pos[package]
        origin_node = plot.Scatter(
            marker=dict(size=7),            
            x=[origin_pos_x],
            y=[origin_pos_y],
            mode='markers+text',
            name='Packages',
            hoverinfo='text',
            textposition='top center',
            text=[package]
        )

        visual = plot.Figure(data=[edge_scatter, node_scatter, origin_node], 
                           layout=plot.Layout(title_text=f'Dependency graph for {package}',
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        ))
        # visual.update_layout(
        #     autosize = False
        # )
        
        return visual


def danman_layout(edges: list[tuple[str, str, int]]) -> dict[str, tuple[int, int]]:
    """Return a custom graph layout for the vertices in edges.
    """
    # Separate the nodes into levels
    levels: dict[int, list] = {}
    deepest_level: dict[str, int] = {}
    for edge in edges:
        if edge[0] in deepest_level:
            if edge[0] in deepest_level and edge[2] - 1 > deepest_level[edge[0]]:
                # Remove from old position
                levels[deepest_level[edge[0]]].remove(edge[0])
                deepest_level[edge[0]] = edge[2] - 1
                
                # Add first node
                if edge[2] - 1 in levels:
                    if edge[0] not in levels[edge[2] - 1]:
                        levels[edge[2] - 1].append(edge[0])
                else:
                    levels[edge[2] - 1] = [edge[0]]
        else:
            deepest_level[edge[0]] = edge[2] - 1
            if edge[2] - 1 in levels:
                if edge[0] not in levels[edge[2] - 1]:
                    levels[edge[2] - 1].append(edge[0])
            else:
                levels[edge[2] - 1] = [edge[0]]

        if edge[1] in deepest_level:    
            if edge[2] > deepest_level[edge[1]]:
                # Remove from old position
                levels[deepest_level[edge[1]]].remove(edge[1])
                deepest_level[edge[1]] = edge[2]

                # Add second node
                if edge[2] in levels:
                    if edge[1] not in levels[edge[2]]:
                        levels[edge[2]].append(edge[1])
                else:
                    levels[edge[2]] = [edge[1]]
        else: 
            deepest_level[edge[1]] = edge[2]
            # Add second node
            if edge[2] in levels:
                if edge[1] not in levels[edge[2]]:
                    levels[edge[2]].append(edge[1])
            else:
                levels[edge[2]] = [edge[1]]
    
    X_DELTA = 1000
    # Position the nodes based on their levels
    positions: dict[str, tuple[int, int]] = {}
    for depth in levels:
        layer_size = len(levels[depth])
        current_loc = -layer_size // 2
        for vertex in levels[depth]:
            positions[vertex] = (current_loc * X_DELTA, -4 * depth + 0.3 * (current_loc % 3))
            current_loc += 1
    
    return positions
    

def _if_na_return_dict(x: Any) -> dict:
    """If x isna, then return an empty dict. Else, return x."""
    if pd.isna(x):
        return {}
    else:
        return x


def _literal_eval_if_able(x: Any, otherwise: Any = '') -> Any:
    """Literally evaluate the entry as long as it is not empty."""
    if x == '' or pd.isna(x):
        return otherwise
    else:
        # TODO: Maybe replace this with a custom function instead of relying on module?
        return ast.literal_eval(x)


@st.cache
def create_graph() -> PackageGraph:
    """Create a graph from our collected data."""
    # Apply data conversion to specific columns of our data
    converters = {4: _literal_eval_if_able, 
                  5: lambda x: _literal_eval_if_able(x, {}), 
                  6: lambda x: _literal_eval_if_able(x, {})
                  }
    # Read in the data
    package_df = pd.read_csv('big.csv', converters=converters)
    package_df = package_df.drop(package_df.columns[0], axis=1)  # Drop the first (index) column

    package_list = []
    for _, data in package_df.iterrows():
        package_list.append(list(data))

    graph = PackageGraph(package_list)
    print(f'Processed {len(graph._vertices)} vertices')
    return graph


if __name__ == '__main__':
    graph = create_graph()    
