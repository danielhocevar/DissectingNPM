import streamlit as st
import pandas as pd
import graph
import graphviz as gviz
import networkx as nx


# Constant values
APP_COL_LENGTH = 4

GRAPH = graph.create_graph()

LAYOUT_FUNCTIONS = {'Danman Layout Algorithm (Custom)': graph.danman_layout,
                    'Spring Layout':nx.spring_layout,
                    'Circular Layout':nx.circular_layout,
                    'Kamada Kawai Layout':nx.kamada_kawai_layout,
                    'Random Layout':nx.random_layout,
                    'Shell Layout':nx.shell_layout,
                    'Spectral Layout':nx.spectral_layout,
                    'Spiral Layout':nx.spiral_layout,
                    }


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


def introduction(GRAPH: graph.PackageGraph) -> None:
    """The introduction section of the webpage.
    """
    st.title('DISSECTING NPM:')
    st.header('Using graphs to gain insights into the infamous package manager')
    # Streamlit bug requires manual spacing
    st.write(' ')
    st.write(' ')

    names, dependencies = GRAPH.most_dependencies_data()

    fram = pd.DataFrame([dependencies], columns=names).transpose()
    st.bar_chart(fram)


def package_search(GRAPH) -> None:
    """The package search (application) portion of the web page.
    """
    st.header('Package Search')

    # Prompt for package search
    all_packages = GRAPH.get_all_packages()
    chosen_package = st.selectbox('Package Name:', all_packages, index=all_packages.index('express'), key='abc')

    if GRAPH.has_package(chosen_package):
        # Prompt for layout and edge selection
        graph_layout_algo = st.selectbox('Select a graph layout:', list(LAYOUT_FUNCTIONS.keys()))
        edge_type = st.selectbox('Select an edge relationship:', ['dependencies', 'keywords'])

        # Other info (only if relevant to selections)
        if edge_type == 'dependencies':
            chosen_direct_dependencies = GRAPH.get_num_package_direct_dependencies(chosen_package)
            chosen_total_dependencies = GRAPH.get_num_dependencies(chosen_package)
            st.write(f'''The package **{chosen_package}** has
            **{chosen_direct_dependencies} direct dependencies** and
            **{chosen_total_dependencies} total dependencies** (which include 
            dependencies of dependencies of dependencies...).''')

        # Plotly Graph
        plotly_graph = GRAPH.get_package_plotly(chosen_package,
                                                LAYOUT_FUNCTIONS[graph_layout_algo],
                                                edge_type)

        plotly_graph.update_layout(width = 1000, height=1000)
        st.plotly_chart(plotly_graph)

        # Dependency list (if applicable)
        if edge_type == 'dependencies':
            show_deps = st.checkbox('List dependencies?')
            if show_deps:
                st.write(f'**List of dependencies for {chosen_package}:**')

                chosen_all_dependencies = GRAPH.get_all_dependencies(chosen_package)
                chosen_all_dependencies.remove(chosen_package)
                dep_per_col = (len(chosen_all_dependencies) // APP_COL_LENGTH) + 1
                dependency_list_columns = st.beta_columns(APP_COL_LENGTH)

                for idx, column in enumerate(dependency_list_columns):
                    for i in range(dep_per_col):
                        if idx * dep_per_col + i < len(chosen_all_dependencies):
                            col_package = chosen_all_dependencies[idx * dep_per_col + i]
                            link = f'[{col_package}](https://www.npmjs.com/package/{col_package})'
                            column.markdown(link, unsafe_allow_html=True)

        st.write(' ')
        # Maintainer list
        show_maintainers = st.checkbox('List maintainers?')
        if show_maintainers:
            chosen_maintainer_share = list(GRAPH.get_packages_with_common_maintainers(chosen_package))
            st.write(f'''**This package shares at least one 
                    maintainer with {len(chosen_maintainer_share)} package(s).**''')
            maintain_per_col = (len(chosen_maintainer_share) // APP_COL_LENGTH) + 1
            maintain_list_columns = st.beta_columns(APP_COL_LENGTH)

            for idx, column in enumerate(maintain_list_columns):
                for i in range(maintain_per_col):
                    if idx * maintain_per_col + i < len(chosen_maintainer_share):
                        col_package = chosen_maintainer_share[idx * maintain_per_col + i]
                        link = f'[{col_package}](https://www.npmjs.com/package/{col_package})'
                        column.markdown(link, unsafe_allow_html=True)
        
    else:
        st.write('The package you are searching for is not in our database :(')


if __name__ == '__main__':
    setup()
    introduction(GRAPH)
    package_search(GRAPH)