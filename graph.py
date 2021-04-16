"""
This module contains our graph class, PackageGraph, and the vertices that
make it up, _PackageVertex.

It also contains our graph layout function, Danman Layout.

All heavy, graph-based computation takes place in this file.

Copyright and Usage Information
===============================
This file is Copyright (c) 2021 Daniel Hocevar and Roman Zupancic.

This files contents may not be modified or redistributed without written
permission from Daniel Hocevar and Roman Zupancic.
"""
from __future__ import annotations
from typing import Any, Callable
import pandas as pd
import networkx as nx
import plotly.graph_objects as plot
import python_ta


class _PackageVertex:
    """A vertex representing one package.

    The properties upstream_dependencies and downtream_dependencies are used to
    define edges in the graph.

    Attributes:
        - name: The name of the package
        - version: The version of the package at the time the data was gathered
        - description: A short piece of text describing the purpose of the package.
        - keywords: A list of words describing the category of the package's purpose
        - downloads_count: The number of times the package has been downloaded
        - dependents_count: The total number of packages in the entire database of
                            npm packages that depend on this package
        - quality: An indicator developed by npms.io
        - popularity: An indicator developed by npms.io
        - maintenance: An indicator developed by npms.io
        - maintainers: A list of strings representing maintainers of this package

        - upstream_dependencies: A list of Vertices representing upstream dependencies
        - downstream_dependencies: A list of Vertices repreysenting downstream dependencies
        - keyword_relationships: A list of Vertices that share keywords with self
        - maintainer_relationships: A set of packages that share maintainers with this package
    """
    name: str
    version: str
    description: str
    keywords: list[str]
    dependencies: dict[str, str]
    downloads_count: int
    dependents_count: int
    quality: float
    popularity: float
    maintenance: float
    maintainers: list[str]

    upstream_dependencies: set[_PackageVertex]
    downstream_dependencies: set[_PackageVertex]
    keyword_relationships: dict[_PackageVertex]
    maintainer_relationships: set[_PackageVertex]

    def __init__(self, package_data: list) -> None:
        """The constructor for our vertex.

        Preconditions:
            - package_data matches the format described by assemble_data.HEADERS
        """
        self.name = package_data[0]
        self.keywords = package_data[3]
        self.dependencies = package_data[4]
        self.downloads_count = package_data[7]
        self.dependents_count = package_data[9]
        self.quality = package_data[10]
        self.popularity = package_data[11]
        self.maintenance = package_data[12]
        self.maintainers = package_data[13]
        self.upstream_dependencies = set()
        self.downstream_dependencies = set()
        self.keyword_relationships = dict()
        self.maintainer_relationships = set()

    def add_upstream_dependency(self, other: _PackageVertex) -> None:
        """
        Add other to this vertex's upstream dependencies.
        """
        self.upstream_dependencies.add(other)

    def add_downstream_dependency(self, other: _PackageVertex) -> None:
        """
        Add other to this vertex's downstream dependencies.
        """
        self.downstream_dependencies.add(other)

    def add_keyword_relationship(self, other: _PackageVertex, keyword: 'str') -> None:
        """
        Add other to this vertex's keyword relationships.
        """
        if keyword in self.keyword_relationships:
            self.keyword_relationships[keyword].add(other)
        else:
            self.keyword_relationships[keyword] = {other}

    def add_maintainer_relationships(self, other_packages) -> None:
        """
        Add other packages that share maintianers
        with this package to self.maintainer_relationships
        """
        self.maintainer_relationships.update(other_packages)
        # The line of code above also adds the current package to maintainer relationships.
        # We need to remove it.
        self.maintainer_relationships.remove(self)

    def get_all_dependencies(self, visited: set) -> set:
        """
        Return a set of all dependencies of this package
        (including dependencies of dependencies...)
        """
        visited.add(self)
        total = {self.name}
        for vertex in self.upstream_dependencies:
            if vertex not in visited:
                total.update(vertex.get_all_dependencies(visited))
        return total

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

    def get_package_dependency_edges(self, visited: set) -> list[tuple[str, str]]:
        """
        Return a list of tuples with one tuple for every edge that this node is connected to,
        as well as a tupple for every upstream dependency edge.

        The first string in the tupple is the dependent and the second string is the dependency

        Apply the graph traversal pattern taught in CSC111
        https://www.teach.cs.toronto.edu/~csc110y/fall/notes/
        """
        new_visited = visited.union({self})
        relationships_so_far = []
        for vertex in self.upstream_dependencies:
            if vertex not in visited:
                relationships_so_far.append((self.name, vertex.name))
                relationships_so_far.extend(vertex.get_package_dependency_edges(new_visited))
        return relationships_so_far

    def get_package_dependency_depth_edges(self, visited: set, depth: int) -> list[tuple[str, str, int]]:
        """
        Return a list of tuples with one tuple for every edge that this node is connected to,
        as well as a tuple for every upstream dependency edge.

        The first string in the tuple is the dependent and the second string is the dependency.
        The third entry, int, is the depth.

        Extend the graph traversal pattern taught in class.
        https://www.teach.cs.toronto.edu/~csc110y/fall/notes/
        """
        new_visited = visited.union({self})
        relationships_so_far = []
        for vertex in self.upstream_dependencies:
            if vertex not in visited:
                relationships_so_far.append((self.name, vertex.name, depth + 1))
                relationships_so_far.extend(vertex.get_package_dependency_depth_edges(new_visited, depth + 1))
        return relationships_so_far

    def get_package_keywords_depth(self, visited: set, depth: int, max_depth: int = 1) -> list[tuple[str, str, int]]:
        """
        Return a list of tuples with one tuple for every edge that this node is connected to,
        as well as a tuple for every keyword relationship edge.

        The first string in the tuple is the dependent and the second string is the dependency.
        The third entry, int, is the depth.
        THe fourth entry, str, is the keyword associated with the edge.

        Apply the graph traversal pattern taught in class.
        https://www.teach.cs.toronto.edu/~csc110y/fall/notes/
        """
        visited.add(self)
        relationships_so_far = []
        for keyword in self.keyword_relationships:
            for vertex in self.keyword_relationships[keyword]:
                if vertex not in visited and depth < max_depth: # Max_depth
                    relationships_so_far.append((self.name, vertex.name, depth + 1, keyword))
                    relationships_so_far.extend(vertex.get_package_keywords_depth(visited,
                                                                                  depth + 1,
                                                                                  max_depth))
        return relationships_so_far

    def get_package_maintainers_local_net(self) -> list[tuple[str, str, int]]:
        """
        Return a list of tuples with one tuple for maintainer relationship that this package has,
        as well as tuples for every maintainer relationship between every package that this package
        shares maintainers with.

        Note: this function is not recursive, since we only want to get edges that define a local maintainer
        network (only edges that connect to adjacent nodes).
        """
        relationships_so_far = set()
        for vertex in self.maintainer_relationships:
            relationships_so_far.add((self.name, vertex.name, 1))
            secondary_edges = self.maintainer_relationships.intersection(vertex.maintainer_relationships)
            for other_vertex in secondary_edges:
                relationships_so_far.add((vertex.name, other_vertex.name, 2))

        return list(relationships_so_far)

    def get_metadata(self) -> dict[str, Any]:
        """
        Return the metadata for this package.

        Does not include dependencies!
        """
        return {'Keywords': self.keywords,
                'Downloads Count': self.downloads_count,
                'Dependents count': self.dependents_count,
                'Quality': self.quality,
                'Popularity': self.popularity,
                'Maintenance': self.maintenance}


class PackageGraph:
    """A graph representing the relationship between packages.

    Attributes:
        - _vertices: A dictionary of all vertices in this graph.
        Each key is a package name, and each value is a _PackageVertex object.
    """
    _vertices: dict[str, _PackageVertex]

    def __init__(self, package_rows: list[list]) -> None:
        """
        Initialize the graph of packages with the package data.

        Preconditions:
            - package_rows is a list of lists of the format described in assemble_data.
        """
        self._vertices = {}

        # Add packages as vertices
        for row in package_rows:
            self.add_vertex(row)

        self.construct_dependency_edges()
        self.construct_keyword_edges()
        self.construct_maintainer_edges()

    def __len__(self) -> int:
        """
        Return the number of vertices in this graph.
        """
        return len(self._vertices)

    def has_package(self, package: str) -> bool:
        """
        Return whether or not the package is contained in the graph.
        """
        return package in self._vertices

    def get_all_packages(self) -> list:
        """
        Return a list of names of all the packages in this graph.
        """
        return list(self._vertices.keys())

    def add_vertex(self, row: list) -> None:
        """
        Add a _PackageVertex to this graph with the data contained in
        row. The vertex is reffered to by it's package name, at row[0].

        Assumes that row matches the format described by HEADER in assemble_data.py2.
        """
        self._vertices[row[0]] = _PackageVertex(row)

    def construct_dependency_edges(self) -> None:
        """
        Form the appropriate dependency edges between all
        vertices in self._vertices.
        """
        for vertex in self._vertices:
            for dependency in self._vertices[vertex].dependencies:
                if dependency in self._vertices:
                    self.add_dependency_edges(dependency, vertex)

    def add_dependency_edges(self, upstream_package: str, downstream_package: str) -> None:
        """
        Add an edge between the two vertices specified as parameters: one
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

    def construct_maintainer_edges(self) -> None:
        """
        Finds all maintainer similarities in this graph
        and sets them as edges within its vertices.
        """
        all_maintainers = {}
        for vertex in self._vertices:
            for maintainer in self._vertices[vertex].maintainers:
                if maintainer in all_maintainers:
                    all_maintainers[maintainer].add(self._vertices[vertex])
                else:
                    all_maintainers[maintainer] = {self._vertices[vertex]}
        for maintainer in all_maintainers:
            for package in all_maintainers[maintainer]:
                package.add_maintainer_relationships(all_maintainers[maintainer])

    def construct_keyword_edges(self) -> None:
        """
        Form the approriate keyword edges between all vertices in self._vertices.
        """
        # Find all keywords, and the vertices they belong to
        keywords: dict[str, list[str]] = {}
        for vertex in self._vertices:
            for keyword in self._vertices[vertex].keywords:
                if keyword not in keywords:
                    keywords[keyword] = [vertex]
                else:
                    keywords[keyword].append(vertex)

        # Add the keywords as edges to each vertex
        for keyword in keywords:
            keyword_list = keywords[keyword]
            for first in range(0, len(keyword_list) - 1):
                for second in range(first + 1, len(keyword_list)):
                    self.add_keyword_edge(keyword_list[first], keyword_list[second], keyword)

    def add_keyword_edge(self, package1: str, package2: str, keyword: str) -> None:
        """
        Add a keyword edge between the two vertices specified as parameters.

        Preconditions:
            - package1 != package2
        """
        if package1 in self._vertices and package2 in self._vertices:
            package1_v = self._vertices[package1]
            package2_v = self._vertices[package2]

            package1_v.add_keyword_relationship(package2_v, keyword)
            package2_v.add_keyword_relationship(package1_v, keyword)
        else:
            raise KeyError(f'The vertices {package1} or {package2}'\
                           'do not exist in this graph')

    def get_all_dependencies(self, package: str) -> list:
        """
        Return a list of all dependencies for the given package
        (including dependencies of dependencies).
        """
        if package in self._vertices:
            vertex = self._vertices[package]
            return list(vertex.get_all_dependencies(set()))
        else:
            raise KeyError(f'A vertex with the name {package} does not exist in this graph')

    def get_direct_dependencies(self, package: str) -> list:
        """
        Return a list of direct dependencies for the given package.
        """
        if package in self._vertices:
            vertex = self._vertices[package]
            return list(v.name for v in vertex.upstream_dependencies)
        else:
            raise KeyError(f'A vertex with the name {package} does not exist in this graph')

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

    def get_num_package_direct_dependencies(self, package: str) -> int:
        """
        Return the number of direct dependencies of the given pacakge.
        """
        if package in self._vertices:
            vertex = self._vertices[package]
            return len(vertex.upstream_dependencies)
        else:
            raise KeyError(f'A vertex with the name {package} does not exist in this graph')

    def get_package_dependency_edges(self, package: str) -> list[tuple[str, str]]:
        """
        Return a list containing tuples containing two package names

        Each tuple in the list represents an edge between the two packages contained by the tuple.
        """
        if package in self._vertices:
            vertex = self._vertices[package]
            edges = vertex.get_package_dependency_edges(set())
            if len(edges) == 0:
                edges = [(package, package)]
            return edges
        else:
            raise KeyError(f'A vertex with the name {package} does not exist in this graph')

    def get_package_dependency_depth_edges(self, package: str) -> list[tuple[str, str, int]]:
        """
        Return a list containing tuples containing two package names.

        Each tuple in the list represents an edge between the two packages contained by the tuple
        """
        if package in self._vertices:
            vertex = self._vertices[package]
            edges = vertex.get_package_dependency_depth_edges(set(), 0)
            if len(edges) == 0:
                edges = [(package, package, 1)]
            return edges
        else:
            raise KeyError(f'A vertex with the name {package} does not exist in this graph')

    def get_package_keyword_relationships(self, package: str) -> list[tuple[str, str, int]]:
        """
        Return a list containing tuples containing two package names

        Each tuple in the list represents an edge between the two packages contained by the tuple
        """
        if package in self._vertices:
            vertex = self._vertices[package]
            edges = vertex.get_package_keywords_depth(set(), 0)
            if len(edges) == 0:
                edges = [(package, package, 1, 'None')]
            return edges
        else:
            raise KeyError(f'A vertex with the name {package} does not exist in this graph')

    def get_package_maintainers_local_net(self, package: str) -> list[tuple[str, str, int]]:
        """
        Return a list containing tuples containing two package names

        Each tuple in the list represents an edge representing that the two packages inside the
        tuple share at least 1 maintainer.
        """
        if package in self._vertices:
            vertex = self._vertices[package]
            edges = vertex.get_package_maintainers_local_net()
            if len(edges) == 0:
                edges = [(package, package, 1, 'None')]
            return edges
        else:
            raise KeyError(f'A vertex with the name {package} does not exist in this graph')

    def get_packages_with_common_maintainers(self, package: str) -> set:
        """
        Return a set containing the names of the other packages
        that the parameter package shares maintainers with.
        """
        if package in self._vertices:
            shared_maintainers = set()
            for package in self._vertices[package].maintainer_relationships:
                shared_maintainers.add(package.name)
            return shared_maintainers
        else:
            raise KeyError(f'A vertex with the name {package} does not exist in this graph')

    def most_dependencies_data(self) -> tuple[list[str], list[int]]:
        """
        Return a tuple with one list containing the names of the packages with the most dependencies
        and a second list containing the number of dependencies for each package respectively.
        """
        package_dependencies = []
        for package in self._vertices:
            val = self.get_num_dependencies(package)
            if type(val) != str:
                package_dependencies.append([self.get_num_dependencies(package), package])
        package_dependencies.sort()
        most_dependecies_names = [package[1] for package in
                                  package_dependencies[len(package_dependencies) - 25:]]
        most_dependecies_vals = [package[0] for package in
                                 package_dependencies[len(package_dependencies) - 25:]]
        return (most_dependecies_names, most_dependecies_vals)

    def most_keywords_data(self) -> tuple[list[str], list[int]]:
        """
        Return a tuple of two lists: the first list contains the top 25 most popular keywords
        in this graph, the second list contains the number of vertices each keyword applies to.
        """
        keyword_count = {}
        for package in self._vertices:
            vertex = self._vertices[package]
            for keyword in vertex.keywords:
                if keyword in keyword_count:
                    keyword_count[keyword] += 1
                else:
                    keyword_count[keyword] = 1

        sorted_tuples = sorted([(keyword_count[key], key) for key in keyword_count.keys()])
        keys = [tup[1] for tup in sorted_tuples]
        values = [tup[0] for tup in sorted_tuples]
        return (keys, values)

    def get_package_metadata(self, package) -> dict[str, Any]:
        """
        Return the metadata, including items such as description and downloads count for the
        input package.
        """
        return self._vertices[package].get_metadata()

    def get_package_plotly(self, package: str,
                                 layout_algo: callable,
                                 edge_type='dependencies'):
        """
        Return a plotly graph object used to visualize package dependencies.

        Preconditions:
            - edge_type in ['dependencies', 'keywords', 'maintainers']
            - layout_algo is a callable that is either danman_layout, or a layout
                function from networkx

        Inspired by https://plotly.com/python/network-graphs/.
        """
        # Identify a list of edges
        if edge_type == 'dependencies':
            edges = self.get_package_dependency_depth_edges(package)
        elif edge_type == 'maintainers':
            edges = self.get_package_maintainers_local_net(package)
        else:
            edges = self.get_package_keyword_relationships(package)

        # Generate positions for the vertices
        if hasattr(nx, layout_algo.__name__):
            graph = convert_edges_to_networkx(edges)
            vertex_pos = layout_algo(graph)
        else:
            vertex_pos = danman_layout(edges)

        # Define edge positions
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

        # Define node positions
        node_pos_x = []
        node_pos_y = []
        for node in vertex_pos:
            node_pos = vertex_pos[node]
            node_pos_x.append(node_pos[0])
            node_pos_y.append(node_pos[1])

        # Define a scatter plto for nodes
        node_scatter = plot.Scatter(
            marker=dict(size=7, color=[]),
            x=node_pos_x,
            y=node_pos_y,
            mode='markers+text',
            name='Dependencies',
            text=list(vertex_pos.keys()),
            hoverinfo='text',
            textposition='top center',
            textfont_size=9
        )

        # Define a scatter plto for edges
        edge_scatter = plot.Scatter(
            x=edge_pos_x, y=edge_pos_y,
            mode='lines',
            name='Edges',
            line=dict(width=1, color="#a6caed"),
            hoverinfo='skip'
        )

        # The following method of coloring each vertex is inspired by the
        # example code in the plotly documentation.
        # https://plotly.com/python/network-graphs/

        # Color code the vertices by quality
        vertex_colors = []
        color_dict = {'low': '#e8353b', 'acceptable': '#e8ab02', 'good': '#29cc54'}
        for node in vertex_pos:
            vertex = self._vertices[node]
            if vertex.quality < 0.50:
                vertex_colors.append(color_dict['low'])
            elif vertex.quality < 0.80:
                vertex_colors.append(color_dict['acceptable'])
            else:
                vertex_colors.append(color_dict['good'])

        node_scatter.marker.color = vertex_colors

        # Define a scatterplot to contain the node for the package being searched
        origin_pos_x, origin_pos_y = vertex_pos[package]
        origin_node = plot.Scatter(
            marker=dict(size=7, color='#000000'),
            x=[origin_pos_x],
            y=[origin_pos_y],
            mode='markers',
            name='Searched Package',
            hoverinfo='text',
            textposition='top center',
            text=[package]
        )

        # Define the plotly figure
        if edge_type == 'dependencies':
            graph_name = 'Dependency'
        elif edge_type == 'keywords':
            graph_name = 'Keyword'
        elif edge_type == 'maintainers':
            graph_name = 'Maintainer'
        visual = plot.Figure(data=[edge_scatter, node_scatter, origin_node],
                             layout=plot.Layout(title_text=f'{graph_name} Graph for {package}',
                             xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                             yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        ))

        # Create keyword labels if the graph type is Keyword
        if edge_type == 'keywords':
            for edge in edges:
                if edge[3] != 'None':
                    x_pos = (vertex_pos[edge[0]][0] + vertex_pos[edge[1]][0]) / 2
                    x_pos += (vertex_pos[edge[1]][0] - vertex_pos[edge[0]][0]) * 0.3
                    y_pos = (vertex_pos[edge[0]][1] + vertex_pos[edge[1]][1]) / 2
                    y_pos += (vertex_pos[edge[1]][1] - vertex_pos[edge[0]][1]) * 0.3
                    visual.add_annotation(x=x_pos,
                                        y=y_pos,
                                        text=edge[3],
                                        showarrow=True,
                                        arrowhead=1)

        return visual


def danman_layout(edges: list[tuple[str, str, int, Any]]) -> dict[str, tuple[int, int]]:
    """
    Return a custom graph layout for the vertices in edges.

    The returned dictionary uses packages as keywords, and each value is the (x, y) coordinate
    of that package in the graph.

    Packages are carried to their deepest dependency level (e.g. packages that appear
    at depth 2 and 7 will be located only at depth 7).

    Preconditions:
        - edges[0] and edges[1] are package names
        - edges[2] is the depth of the connection
        - edges[3:] can be anything (or not included)
    """
    # Separate the nodes into levels
    levels: dict[int, list] = {}
    deepest_level: dict[str, int] = {}
    for edge in edges:
        # Package 1
        # =========
        # If we've already encountered the package before
        if edge[0] in deepest_level:
            # Only add the package again if it is deeper than before
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
        else: # Otherwise, just add the package
            # Register it as the deepest level
            deepest_level[edge[0]] = edge[2] - 1
            # Add this package to the corresponding level in the levels dictionary
            if edge[2] - 1 in levels:
                if edge[0] not in levels[edge[2] - 1]:
                    levels[edge[2] - 1].append(edge[0])
            else:
                levels[edge[2] - 1] = [edge[0]]

        # Package 2
        # =========
        # If we've already encountered the package before
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

    # space between packages
    X_DELTA = 1000
    # Position the nodes based on their levels
    positions: dict[str, tuple[int, int]] = {}
    for depth in levels:
        # Find the starting point of the layer
        layer_size = len(levels[depth])
        current_loc = (-layer_size / 2) + ((0.5) * (depth % 2))

        # Assign positions to vertices at the current depth
        for vertex in levels[depth]:
            positions[vertex] = (current_loc * X_DELTA,
                                 -4 * depth + 0.3 * (current_loc % 3))  # Diagonal y pattern
            current_loc += 1

    return positions


def convert_edges_to_networkx(edges: list[tuple]) -> nx.Graph:
    """
    Convert this graph to a networkx graph.
    """
    netxG = nx.Graph()
    for edge in edges:
        netxG.add_edge(edge[0], edge[1])
    return netxG


if __name__ == '__main__':
    python_ta.check_all(
        config={
            'extra-imports': ['python_ta', 'requests', 'json', 'pandas', 'time', 'typing'],
            'allowed-io': ['get_detailed_data', 'all_package_dependencies', 'get_package'],
            'max-line-length': 100,
            'disable': ['E1136'],
            'max-nested-blocks': 4
        }
    )