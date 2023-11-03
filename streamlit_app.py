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
#from project_core.utils import load_config
from itertools import chain
#from project_core.data_work import retrieve_data, filter_data, pivot, pivot_table, empl_pop_ratio, wide_to_long
from data_work import *
#config=load_config("config.json")

# data
empl_data=retrieve_data(table_id="14-10-0202-01", date_to_year = True)
empl_data_filtered=filter_data(df=empl_data, filter_dict={
        "Type of employee": [
            "All employees"
        ],
        "North American Industry Classification System (NAICS)": [
            'Provincial and territorial public administration [912]'
        ],
        "REF_YEAR": [
            *range(2001,2023)
        ],
        "GEO": ['Alberta',
        'British Columbia',
        'Canada', 'Manitoba',
        'New Brunswick',
        'Newfoundland and Labrador',
        'Nova Scotia', 'Ontario',
        'Prince Edward Island',
        'Quebec',
        'Saskatchewan']
    })
empl_data_pivot=pivot(df=empl_data_filtered)

pop_data=retrieve_data(table_id="17-10-0009-01", date_to_year = True)
pop_data_filtered=filter_data(df=pop_data, filter_dict={
        "REF_YEAR": [*range(2001,2023)],
        "GEO": ['Alberta',
        'British Columbia',
        'Canada', 'Manitoba',
        'New Brunswick',
        'Newfoundland and Labrador',
        'Nova Scotia', 'Ontario',
        'Prince Edward Island',
        'Quebec',
        'Saskatchewan']
    })
pop_data_pivot=pivot_table(df=pop_data_filtered)

ratio_df=empl_pop_ratio(empl_df=empl_data_pivot, pop_df=pop_data_pivot)

alta_df=pd.DataFrame(
    {"REF_YEAR":[*range(2001,2023)],
     "ratio":ratio_df['Alberta'].values,
     "pop":pop_data_pivot["Alberta"].values})


ratio_df_melted=wide_to_long(df=ratio_df, id_vars="REF_YEAR")
#ratio_df_melted["REF_YEAR"]=pd.to_datetime(ratio_df_melted["REF_YEAR"])
#alta_df_final=wide_to_long(df=alta_df, id_vars="REF_YEAR")


#Dashboard
st.title("Provincial Public Administration Employees per 1000 Employees")
#st.set_page_config(page_title = "Provincial Public Administration Employees per 1000 Employees", 
 #                  page_icon=":bar_chart:",
  #                 layout="wide")

st.sidebar.header("Alberta Only or All Provinces")
add_sidebar = st.sidebar.selectbox('Please select dimension', ('Dashboard Description', 'Alberta Only', 'All Provinces'))

if add_sidebar=="Alberta Only":
    st.subheader("Please filter here:")
    years_filter=st.multiselect(
        "Select the years to include:",
        options=[*range(2001,2023)],
        default=[*range(2018,2023)])
    
    st.markdown("##")
    
    df_selection=alta_df.query("REF_YEAR == @years_filter")
    df_selection=df_selection.sort_values("REF_YEAR")

    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add traces
    fig.add_trace(
        go.Scatter(x=df_selection['REF_YEAR'].values,
                   y=df_selection['ratio'].values,
                   name="Alberta Public Administration Employees per 1000 Albertans",
                   line=dict(color="rgb(0, 112, 192)")
                  ),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=df_selection['REF_YEAR'].values,
                   y=df_selection['pop'].values,
                   name="Alberta Population",
                  line=dict(color="rgb(204, 51, 0)")),
        secondary_y=True,
    )
    
    # Add figure title
    fig.update_layout(title_text="Chart 1: Alberta Only", width=1200, height=600)
    
    # Set x-axis title
    fig.update_xaxes(title_text="xaxis title")
    
    # Set y-axes titles
    fig.update_yaxes(title_text="Alberta Public Administration Employees per 1000 Albertans",
                     secondary_y=False, title_font=dict(color="rgb(0, 112, 192)"))
    fig.update_yaxes(title_text="Alberta Population", secondary_y=True, title_font=dict(color="rgb(204, 51, 0)"))
    st.plotly_chart(fig)

    
if add_sidebar=="All Provinces":
    st.subheader("Please filter here:")
    col1, col2 = st.columns(2)
    with col1:
        years_filter=st.multiselect(
            "Select the years to include:",
            options=[*range(2001,2023)],
            default=[*range(2018,2023)])
    with col2:
        geo_filter=st.multiselect(
            "Select the geographical locations to include:",
            options=['Canada',
                     'Newfoundland and Labrador',
                     'Prince Edward Island','Nova Scotia',
                     'New Brunswick','Quebec','Ontario',
                     'Manitoba','Saskatchewan',
                     'Alberta','British Columbia'],
            default=["Alberta", 'British Columbia', 'Manitoba', 'Ontario', 'Quebec', 'Saskatchewan'])
    
    st.markdown("##")
    
    df_selection=ratio_df_melted.query("REF_YEAR == @years_filter & Geographical_Location == @geo_filter")
    df_selection=df_selection.sort_values("REF_YEAR")
    
    fig = px.line(df_selection,
                  x='REF_YEAR',
                  y='PPA Employees per 1000 Residents',
                  color='Geographical_Location',
                  markers=True,
                 height=600,
                 width=1200)
    
    st.plotly_chart(fig)


if add_sidebar=="Dashboard Description":
    st.markdown(
        
        """   
        
This dashboard visualiazations for the number of provincial public administration employees per 1000 residents in different provinces across Canada. The rationale is to:

    1. demosntrate the ability to automate Statistics Canada data acquisition instead of manually downlading CSV files from the website.
    2. find a fair basis for comparing the number of employees in various provincial governments across Canada.

## Data Sources
Two data series are used, both from Ststistics Canada. All data sources were pulled programatically (automatically using Python) from Statistics Canada's API called [**Web Data Services**](https://www.statcan.gc.ca/en/developers/wds). This demosntrates the ability to automate Statistics Canada data acquisition instead of manually downlading CSV files from the website.

### Employee Data
1. Statistics Canada refers to the employees included in this data as “Provincial Public Administration Employees” and describes them as follows:
    1. Provincial public administration comprises establishments of provincial or territorial governments primarily engaged in activities of a governmental nature, such as legislative activities, judicial activities, taxation, public order and safety, and the administration of provincial or territorial government programs
    2. Provincial public administration employment includes employees that are actively being paid in the reporting periods (employees paid by the hour, salaried employees and other employees.
    
2. Data Table: [Employee by Industry, Annual ( Table: 14-10-0202-01 (formerly CANSIM 281-0024))](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410020201)

3. Data pulled in October 22, 2023 and so represents the most current data as of the time of this report.
4. The data comes from the Survey of Employment, Payrolls and Hours (SEPH), a comprehensive monthly survey of the labour market
    1. The survey’s target population is composed of businesses in Canada that have at least one employee and, thus issued at least one payroll deduction remittance during the reference month
    2. Data are collected directly from survey respondents, extracted from administrative files and derived from other Statistics Canada surveys and/or other sources.
    3. Information for general government services is provided to SEPH on a monthly basis by the provincial, territorial and federal governments in the form of electronic files extracted from their payroll records.
    
**5. The annual employee headcount for a calendar year is an average of monthly headcounts in that calendar year**

### Population Data
1. Population data are based on quarterly estimates by Statistics Canada ([Table: 17-10-0009-01 (formerly CANSIM 051-0005) Population Estimates, Quarterly](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710000901))
2. Data pulled in October 2023 and so represents the most current numbers
        
        
        """
    )