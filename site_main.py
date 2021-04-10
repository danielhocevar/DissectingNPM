import streamlit as st
import pandas as pd
import graph

GRAPH = graph.create_graph()

st.title('DISSECTING NPM:')
st.header('Using graphs to gain insights') 
st.header('into the infamous package manager')

names, dependencies = GRAPH.popular_package_data()
print(names)
print(dependencies)
fram = pd.DataFrame([dependencies], columns=names).transpose()
print(fram)
st.bar_chart(fram)
