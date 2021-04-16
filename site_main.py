"""
This module builds a graph from pre-generated data and begins the visualization
of the streamlit website.

Copyright and Usage Information
===============================
This file is Copyright (c) 2021 Daniel Hocevar and Roman Zupancic. 

This files contents may not be modified or redistributed without written
permission from Daniel Hocevar and Roman Zupancic
"""
# External Imports
from typing import Any
import ast
import pandas as pd
import networkx as nx

# Project Imports
import site_functions as sf
from graph import PackageGraph, danman_layout


def main() -> None:
    """Render individual sections from site_functions as a cohesive website.
    """
    # Functions to be used by the search section for visualizing the graph.
    layout_functions = {'Danman Layout Algorithm (Custom)': danman_layout,
                        'Spring Layout':nx.spring_layout,
                        'Circular Layout':nx.circular_layout,
                        'Kamada Kawai Layout':nx.kamada_kawai_layout,
                        'Random Layout':nx.random_layout,
                        'Shell Layout':nx.shell_layout,
                        'Spectral Layout':nx.spectral_layout,
                        'Spiral Layout':nx.spiral_layout,
                        }

    package_graph = create_graph()

    sf.setup()
    sf.introduction()
    sf.dependency_overview(package_graph)
    sf.keyword_overview(package_graph)
    sf.package_search(package_graph, layout_functions)


def create_graph() -> PackageGraph:
    """Create a graph from our collected data."""
    # Apply data conversion to specific columns of our data
    # Add 1 to your desired column
    converters = {1: lambda x: str(x),
                  4: _literal_eval_if_able,
                  5: lambda x: _literal_eval_if_able(x, {}),
                  6: lambda x: _literal_eval_if_able(x, {}),
                  14: lambda x: _literal_eval_if_able(x, []),
                  }
    # Read in the data
    package_df = pd.read_csv('big_v2.csv', converters=converters)
    package_df = package_df.drop(package_df.columns[0], axis=1)  # Drop the first (index) column

    package_list = []
    for _, data in package_df.iterrows():
        #if type(data[0]) == str:
        package_list.append(list(data))

    graph = PackageGraph(package_list)
    print(f'Processed {len(graph)} vertices')
    return graph


def _if_na_return_dict(x: Any) -> dict:
    """Return an empty dictionary if x is Nan (not a number). 
    Otherwise, return x.
    
    This function serves as a filter for pandas to apply as it converts a 
    CSV file to a python-compatable dataframe.
    """
    if pd.isna(x):
        return {}
    else:
        return x


def _literal_eval_if_able(x: Any, otherwise: Any = '') -> Any:
    """Return parameter otherwise if x is an empty string or null.
    Otherwise, return the python evaluation of x.
    
    This function serves as a filter for pandas to apply as it converts a
    CSV file to a python compatable dataframe: if x is some kind of python expression,
    the literal value of that expression will be saved to the dataframe, allowing us to
    interact with it through code.
    """
    if x == '' or pd.isna(x):
        return otherwise
    else:
        # TODO: Maybe replace this with a custom function instead of relying on module?
        return ast.literal_eval(x)


if __name__ == '__main__':
    main()