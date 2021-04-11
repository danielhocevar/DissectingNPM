import streamlit as st
import pandas as pd
import graph
import graphviz as gviz

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
graph_layout_algo = st.selectbox('Select a graph layout:', ('spring_layout', 'circular_layout',
                                                            'kamada_kawai_layout',
                                                            'planar_layout',
                                                            'random_layout',
                                                            'shell_layout',
                                                            'spectral_layout',
                                                            'spiral_layout',
                                                            'graphviz_layout'))
plotly_graph = GRAPH.get_package_plotly('firebase', graph_layout_algo)
plotly_graph.update_layout(width = 1000, height=1000)
st.plotly_chart(plotly_graph)
