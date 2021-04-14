import streamlit as st
import pandas as pd
import graph
import graphviz as gviz
import networkx as nx

#  Hackily adding a style to change the width of the web page
st.markdown('''
            <style>
                .reportview-container .main .block-container{
                    max-width: 1000px;
                }
            </style>
            ''',
            unsafe_allow_html=True)

GRAPH = graph.create_graph()

if 'saved_selected_package' not in st.__dir__():
    print('here')
    st.saved_selected_package = None
print('Printed Attribute')
print(st.__dict__.get('saved_selected_package'))
print('saved_selected_package' in st.__dict__)

LAYOUT_FUNCTIONS = {'Danman Layout Algorithm (Custom)': graph.danman_layout,
                    'Spring Layout':nx.spring_layout,
                    'Circular Layout':nx.circular_layout,
                    'Kamada Kawai Layout':nx.kamada_kawai_layout,
                    'Random Layout':nx.random_layout,
                    'Shell Layout':nx.shell_layout,
                    'Spectral Layout':nx.spectral_layout,
                    'Spiral Layout':nx.spiral_layout,
                    }

package_graph = GRAPH.get_package_digraph('firebase')

def draw_layout(package: str):
    st.title('DISSECTING NPM:')
    st.header('Using graphs to gain insights into the infamous package manager')
    # Streamlit bug requires manual spacing
    st.write(' ')
    st.write(' ')

    names, dependencies = graph.popular_package_data(GRAPH)

    fram = pd.DataFrame([dependencies], columns=names).transpose()
    st.bar_chart(fram)

    st.header('Package Search')
    #st.graphviz_chart(package_graph)
    all_packages = GRAPH.get_all_packages()
    if st.saved_selected_package is not None:
        print(f'Trying to set a saved selected package such that {st.__dict__.get("saved_selected_package")}')
        chosen_package = st.selectbox('Package Name:', all_packages, index=all_packages.index(f'{st.__dict__.get("saved_selected_package")}'))
    else:
        chosen_package = st.selectbox('Package Name:', all_packages, index=all_packages.index(package))

    if GRAPH.has_package(chosen_package):
        graph_layout_algo = st.selectbox('Select a graph layout:', list(LAYOUT_FUNCTIONS.keys()))
        edge_type = st.selectbox('Select an edge relationship:', ['dependencies', 'keywords'])

        # Other info:
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

        st.write(f'**List of dependencies for {chosen_package}:**')

        chosen_all_dependencies = GRAPH.get_all_dependencies(chosen_package)
        dependency_column_length = 4
        dep_per_col = len(chosen_all_dependencies) // dependency_column_length

        dependency_list_columns = st.beta_columns(dependency_column_length)
        for idx, column in enumerate(dependency_list_columns):
            for i in range(dep_per_col):
                col_package = chosen_all_dependencies[idx * dep_per_col + i]
                button = st.button(col_package)
                if button == True:
                    print(f'setting selected package to {col_package}')
                    st.saved_selected_package = col_package
                # answer = create_package_button(col_package)
                # if answer == True:
                #     return
                # link = f'[{col_package}](https://www.npmjs.com/package/{col_package})'
                # column.markdown(link, unsafe_allow_html=True)
    else:
        st.write('The package you are searching for is not in our database :(')


draw_layout('express')
# def create_package_button(package: str):
#     global new_layout 
#     global package_current
#     if button:
#         print('RUNNNNING')
#         new_layout = 'new'
#         #return 'clicked_baby'
#         package_current = 'package'
#         return True
        
# #chosen_package = draw_layout(chosen_package)

# #last_layout = draw_layout('express')
# new_layout = None
# package_current = 'express'
# while True:
#     if new_layout is None:
#         print(package_current)
#         draw_layout(package_current)
#     else:   
#         print('YYYYYYYYYYYYYYYYY')
#         new_layout = None     
#         draw_layout(package_current)
    
