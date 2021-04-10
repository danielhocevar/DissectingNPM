"""
Here we will define our Graph and _PackageVertex classes.
These two classes will be very similar to the ones learned
in class, and will makeup our Graph Data Structure.
"""
from __future__ import annotations
import csv
import pandas as pd
import ast
from typing import Any


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
        new_visited = visited.union({self})
        total = 0
        for vertex in self.upstream_dependencies:
            if vertex not in visited:
                total = total + 1 + vertex.get_num_dependencies(new_visited)
        return total


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
    
    def get_num_dependencies(self, package) -> int:
        """
        Return the number of dependencies of the given package.

        Include dependencies of dependencies in the count, by using the
        common graph traversal pattern to traverse all relavent nodes in the graph
        """
        vertex = self._vertices[package]
        return vertex.get_num_dependencies(set())

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
