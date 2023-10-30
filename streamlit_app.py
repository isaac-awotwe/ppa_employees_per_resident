# Import libs
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime
import copy
from stats_can import StatsCan
from utils import load_config
from itertools import chain
from data_work import retrieve_data, filter_data, pivot, pivot_table, empl_pop_ratio, wide_to_long
config=load_config("config.json")

# data
empl_data=retrieve_data(table_id=config["empl_data_id"], date_to_year = True)
empl_data_filtered=filter_data(df=empl_data, filter_dict=config["ppa_empl_filter"])
empl_data_pivot=pivot(df=empl_data_filtered)

pop_data=retrieve_data(table_id=config["pop_data_id"], date_to_year = True)
pop_data_pivot=pivot_table(df=pop_data)

ratio_df=empl_pop_ratio(empl_df=empl_data_pivot, pop_df=pop_data_pivot)

alta_df=pd.dataFrame(
    {"REF_YEAR":config["focus_years"],
     "ratio":ratio_df['Alberta'].values,
     "pop":pop_data_pivot["Alberta"].values})


ratio_df_melted=wide_to_long(df=ratio_df, id_vars="REF_YEAR")
#alta_df_final=wide_to_long(df=alta_df, id_vars="REF_YEAR")


#Dashboard
st.sidebar.header("Alberta Only or All Provinces")
add_sidebar = st.sidebar.selectbox('Please select dimension', ('Alberta Only', 'All Provinces'))

if add_sidebar=="Alberta Only":
    st.subheader("Please filter here:")
    years_filter=st.multiselect(
        "Select the years to include:",
        options=config["focus_years"],
        default=config["st_default_years"])
    
    st.markdown("##")
    
    df_selection=alta_df.query("REF_YEAR == @years_filter")
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add traces
    fig.add_trace(
        go.Scatter(x=df_selection['REF_YEAR'].values,
                   y=df_selection['ratio'].values,
                   name="Alberta Public Administration Employees per 1000 Albertans"),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=df_selection['REF_YEAR'].values,
                   y=df_selection['pop'].values,
                   name="Alberta Population"),
        secondary_y=True,
    )
    
    # Add figure title
    fig.update_layout(title_text="Chart 1: Alberta Only")
    
    # Set x-axis title
    fig.update_xaxes(title_text="xaxis title")
    
    # Set y-axes titles
    fig.update_yaxes(title_text="<b>primary</b> yaxis title", secondary_y=False)
    fig.update_yaxes(title_text="<b>secondary</b> yaxis title", secondary_y=True)
    st.plotly_chart(fig)

    
if add_sidebar=="All Provinces":
    st.subheader("Pleasae filter here:")
    col1, col2 = st.columns(2)
    with col1:
        years_filter=st.multiselect(
            "Select the years to include:",
            options=config["focus_years"],
            default=config["st_default_years"])
    with col2:
        geo_filter=st.multiselect(
            "Select the geographical locations to include:",
            options=config["focus_geo"],
            default=config["st_default_geo"])
    
    st.markdown("##")
    
    df_selection=ratio_df_melted.query("REF_YEAR == @years_filter & geo == @geo_filter")
    
    fig = px.line(df_selection, x=REF_YEAR, y="count", color="geo", markers=True)
    
    st.plotly_chart(fig)
    