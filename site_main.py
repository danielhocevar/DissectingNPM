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

if 'GRAPH' not in locals() or 'GRAPH' not in globals():
    GRAPH = graph.create_graph()
else:
    print('Memoized the graph!')

package_graph = GRAPH.get_package_digraph('firebase')

st.title('DISSECTING NPM:')
st.header('Using graphs to gain insights into the infamous package manager')
# Streamlit bug requires manual spacing
st.write(' ')
st.write(' ')

names, dependencies = GRAPH.popular_package_data()

fram = pd.DataFrame([dependencies], columns=names).transpose()
st.bar_chart(fram)

#st.graphviz_chart(package_graph)
layout_functions = {'Danman Layout Algorithm (Custom)': graph.danman_layout,
                    'Spring Layout':nx.spring_layout, 
                    'Circular Layout':nx.circular_layout, 
                    'Kamada Kawai Layout':nx.kamada_kawai_layout,
                    'Random Layout':nx.random_layout, 
                    'Shell Layout':nx.shell_layout, 
                    'Spectral Layout':nx.spectral_layout, 
                    'Spiral Layout':nx.spiral_layout,                     
                    }
chosen_package = st.text_input('Choose Package:', 'aws-sdk')
st.balloons()
graph_layout_algo = st.selectbox('Select a graph layout:', list(layout_functions.keys()))
plotly_graph = GRAPH.get_package_plotly(chosen_package, layout_functions[graph_layout_algo])
plotly_graph.update_layout(width = 1000, height=1000)
st.plotly_chart(plotly_graph)
