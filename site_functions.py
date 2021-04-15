"""
This module includes functions that represent different sections of the website.

Only graph data-accessing happens in this file, all heavy computation exists in graph.py.

Copyright and Usage Information
===============================
This file is Copyright (c) 2021 Daniel Hocevar and Roman Zupancic. 

This files contents may not be modified or redistributed without written
permission from Daniel Hocevar and Roman Zupancic
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Callable

from graph import PackageGraph

# Constant values
APP_COL_LENGTH = 4



def setup() -> None:
    """Preform page initialization tweaks."""

    #  Hackily adding a style to change the width of the web page
    st.markdown('''
                <style>
                    .reportview-container .main .block-container{
                        max-width: 1000px;
                    }
                </style>
                ''',
                unsafe_allow_html=True)


def introduction() -> None:
    """The introduction section of the webpage.
    """
    st.title('DISSECTING NPM:')
    st.header('Using graphs to gain insights into the infamous package manager')
    # Streamlit bug requires manual spacing
    st.write(' ')
    st.write(' ')
    st.write('''The goal of this project is to provide developers with a deeper 
                understanding of the packages that they use in their projects. Specifically,
                we want to provide developers with a means of visualizing their package
                dependency hierarchy as well search for packages with similar keywords or
                maintainers to the packages that they are already using. We have procured a
                dataset of package data using the npms.io API. Our dataset does not include
                every npm package, rather only a sample of popular packages along with their
                dependencies. At the bottom of this page is our flagship feature: the package
                search. This feature creates graph visualizations for dependency, keyword and
                maintainer relationships for any package that the user searches for.''')


def dependency_overview(package_graph: PackageGraph) -> None:
    """This section includes explanations about dependencies, and a short sample showcasing
    packages in our database with the largest dependecy graphs.
    """
    st.header('Dependency Relationships Overview')
    st.write('''The following bar graph displays the packages in our dataset with the most
                dependencies''')
    
    names, dependencies = package_graph.most_dependencies_data()
    fram = pd.DataFrame([dependencies], columns=names).transpose()
    fram = fram.rename(columns={0: 'Number of dependencies'})
    fram['Packages']=fram.index
    
    plotly_chart_most_dependencies = px.bar(fram, x='Number of dependencies', 
                                            y='Packages',
                                            title='Packages with the most dependencies')
    
    plotly_chart_most_dependencies.update_layout(width = 1000, height=600)
    st.plotly_chart(plotly_chart_most_dependencies)

    st.write('''When looking at the above graph, a few things come to mind: namely, why does 'Jest' keep
             appearing, and what do these packages all have in common?''')
    st.write('''On examining Jest, we see that there are only three direct dependencies, two
             of which are Jest sub-packages (jest-cli and @jest/core). Crucially, we notice 
             that both these modules are also immediately below jest on our dependency chart.
             Looking at a generated dependancy graph of jest (which you can do below!), we confirm
             our suspicions: that since Jest is closely connected to most of its sub-packages 
             (within two or three path-lengths), the number of dependencies are roughly the same
             between them. So our most-dependencies chart will keep recording Jest packages
             until we move far enough down the dependency graph to dilute the numbers.''')
    st.write('''So what do all these packages have in common? In relation to dependencies, 
             we notice that most of these packages are compartmentalizable: they have
             been written with a component based architecture in mind. react-scripts, for example,
             is a collection of tools for different aspects of web development: it makes
             more sense to keep a package for development tools (like eslint) away from packages
             that transpile typescript (like babble) away from packages that help style css.
             So instead of re-writting a collection of loosely related tools into one package,
             the maintainers of react-scripts have decided to leverage the npm ecosystem to 
             compartmentalize for them. This reasoning translates well to gulp, node-sass,
             and other packages: having distinct components make it easy to understand and maintain
             a package.''')


def keyword_overview(package_graph: PackageGraph) -> None:
    """This section includes explanations about keywords, and a short sample showcasing
    keywords that appear in the highest number of packages.
    """
    st.header('Keywords Overview')
    keywords, number = package_graph.most_keywords_data()

    # What keywords are most popular?
    fram = pd.DataFrame([number[-25:]], columns=keywords[-25:]).transpose()
    fram = fram.rename(columns={0: 'Number of occurances'})
    fram['Keywords']=fram.index
    plotly_chart_most_keywords = px.bar(fram, y='Number of occurances', 
                                            x='Keywords',
                                            title='Top 25 most common keywords.')
    plotly_chart_most_keywords.update_layout(width = 1000, height=600)
    st.plotly_chart(plotly_chart_most_keywords)

    st.write('''Unsurprisingly, many of the popular keywords are technically inclined, where words like
             'http', 'css', 'cli', and 'regex' directly describe some pattern or technology. This
             fits a popular use-case for keywords: using them to search for and relate packages together.''')

    # How many keywords occur only once? Twice? ...
    # Get occurencces
    lst_of_counts = [number.count(count) for count in range(1, 18)] + [len([item for item in number if item >= 18])]
    lst_of_counts_columns = [str(count) for count in range(1, 18)] + ['18+']
    # Write to dataframe
    number_fram = pd.DataFrame([lst_of_counts], columns=lst_of_counts_columns).transpose()
    number_fram = number_fram.rename(columns={0: 'Frequency'})
    number_fram['Number of key occurrences']=number_fram.index
    plotly_chart_most_key_occurrences = px.area(number_fram, y='Frequency', 
                                            x='Number of key occurrences',
                                            title='Frequency of number of occurrences of keywords')
    plotly_chart_most_key_occurrences.update_layout(width = 1000, height=600)
    st.plotly_chart(plotly_chart_most_key_occurrences)

    st.write('''**Takeaway:** most keywords don't catch on, but the more times a keyword is used,
             the more likely it is to get used again in new packages.''')

    st.write('''Some other facts about keywords used to describe vertices in our graph:''')
    st.write(f'''
             - There are {len(keywords)} total keywords, and {sum(number)} 
             total occurences of keywords throughout our package graph.
             - The Top 25 keywords account for {round(sum(number[-25:])/sum(number) * 100, 2)}% of all occurences of keywords in this graph.
             - {number.count(1)} ({round(number.count(1)/sum(number) * 100, 2)}% of) keywords only occur once throughout the entire graph.''')



def maintainers_overview(package_graph: PackageGraph) -> None:
    """This section includes explanations about keywords, and a short sample showcasing
    keywords that appear in the highest number of packages.
    """
    st.header('Maintainers Overview')


def package_search(package_graph: PackageGraph, 
                   layout_functions: dict[str, Callable]) -> None:
    """The package search (application) portion of the web page.
    """
    st.header('Package Search')

    # Prompt for package search
    all_packages = package_graph.get_all_packages()
    chosen_package = st.selectbox('Package Name:', all_packages, index=all_packages.index('express'), key='abc')

    if package_graph.has_package(chosen_package):
        # Prompt for layout and edge selection
        graph_layout_algo = st.selectbox('Select a graph layout:', list(layout_functions.keys()))
        edge_type = st.selectbox('Select an edge relationship:', ['dependencies', 'maintainers', 'keywords'])

        # Other info (only if relevant to selections)
        if edge_type == 'dependencies':
            chosen_direct_dependencies = package_graph.get_num_package_direct_dependencies(chosen_package)
            chosen_total_dependencies = package_graph.get_num_dependencies(chosen_package)
            st.write(f'''The package **{chosen_package}** has
            **{chosen_direct_dependencies} direct dependencies** and
            **{chosen_total_dependencies} total dependencies** (which include 
            dependencies of dependencies of dependencies...).''')

        # Plotly Graph
        plotly_graph = package_graph.get_package_plotly(chosen_package,
                                                layout_functions[graph_layout_algo],
                                                edge_type)

        plotly_graph.update_layout(width = 1000, height=1000)
        st.plotly_chart(plotly_graph)

        show_deps = st.checkbox('List dependencies?')
        if show_deps:
            chosen_all_dependencies = package_graph.get_all_dependencies(chosen_package)
            chosen_all_dependencies.remove(chosen_package)

            if len(chosen_all_dependencies) > 0:
                chosen_direct_dependencies = package_graph.get_direct_dependencies(chosen_package)

                chosen_indirect_dependencies = [dep for dep in chosen_all_dependencies 
                                                if dep not in chosen_direct_dependencies]

                st.write(f'**This package has {len(chosen_all_dependencies)} total dependencies:**')

                st.write(f'There are {len(chosen_direct_dependencies)} direct dependencies:')
                _list_package_columns(chosen_direct_dependencies, APP_COL_LENGTH)

                st.write(f'And {len(chosen_all_dependencies) - len(chosen_direct_dependencies)} indirect dependencies:')
                _list_package_columns(chosen_indirect_dependencies, APP_COL_LENGTH)
            else:
                st.write(f'{chosen_package} has no dependencies!')

        # Spacing
        st.write(' ')

        # Maintainer list
        show_maintainers = st.checkbox('List packages with shared maintainers?')
        if show_maintainers:
            chosen_maintainer_share = list(package_graph.get_packages_with_common_maintainers(chosen_package))
            st.write(f'''**This package shares at least one 
                    maintainer with {len(chosen_maintainer_share)} package(s).**''')
            _list_package_columns(chosen_maintainer_share, APP_COL_LENGTH)
        
    else:
        st.write('The package you are searching for is not in our database :(')


def _list_package_columns(lst: list, col_length: int) -> None:
    """Organize package names in lst as a column list of packages.
    col_length is the number of columns used.
    
    Each package in list is clickable and redirects to the npmjs.com page.
    """
    package_per_col = (len(lst) // col_length) + 1
    package_list_columns = st.beta_columns(col_length)

    for idx, column in enumerate(package_list_columns):
        for i in range(package_per_col):
            if idx * package_per_col + i < len(lst):
                col_package = lst[idx * package_per_col + i]
                link = f'[{col_package}](https://www.npmjs.com/package/{col_package})'
                column.markdown(link, unsafe_allow_html=True)