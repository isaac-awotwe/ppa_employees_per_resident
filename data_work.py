# Import modules
import pandas as pd
import numpy as np
import copy
from stats_can import StatsCan
#from utils import load_config
from itertools import chain
#config=load_config("config.json")
import json



def retrieve_data(table_id:str,
                  date_col_name = 'REF_DATE',
                  date_to_year=False,
                  drop_cols=["DGUID","UOM",
                             "UOM_ID","SCALAR_FACTOR",
                             "SCALAR_ID","VECTOR",
                             "COORDINATE","STATUS",
                             "SYMBOL","TERMINATED",
                             "DECIMALS"],
                  )->pd.DataFrame:
    """
    Pulls a data table from the Statistics Canada (StatsCan) website and removes some extra columns.
    
    :param table_id: StatsCan table number as a string
    :param date_col_name: the name of the date column from the table when pulled from StatsCan website
     Enetered as a string, default is 'REF DATE' which is the current date column name
    :param date_to_year: if True, the date column will be transformed to year
     Takes booleans True or False. Default is False, in which case the date column remains unchanged
    :param drop_cols: a list of columns to drop
     These are current system columns in the data table that may not be relevant
     To keep all columns, enter and empty list
    :return: a DataFrame
    """

    sc = StatsCan()
    table_df = sc.table_to_df(table = table_id)
    sc.update_tables()
    if date_to_year == True:
        table_df['REF_YEAR'] = table_df[date_col_name].dt.year
    table_df.drop(drop_cols, axis=1, inplace=True)
    return table_df
        

def filter_data(df:pd.DataFrame,
                filter_dict:dict)->pd.DataFrame:
    """
    Applies filters to a dataframe.
    
    :param df: dataframe to be filtered
    :param filter_dict:  dictionary to use as filter
     the key is the column name to filter on (a string)
     value is a list of column values to keep.
    :return: a filtered DataFrame
    """
    
    for k,v in filter_dict.items():
        df = df[df[k].isin(v)]
    return df

def pivot(
    df:pd.DataFrame,
    idx="REF_YEAR",
    col="GEO",
    val="VALUE")->pd.DataFrame:
    """
    pivots a dataframe from long to wide
    df
    :param idx: name of columns to serve as index in new pivoted dataframe
    :param col: name of column whose values serve as new columns in the new dataframe
    :param val: takes the name of the column whose values populate the new pivoted data frame
    """
    pivot_df = df.pivot(index=idx,
                        columns=col,
                        values=val).reset_index()
    pivot_df.columns.name=None
    pivot_df=pivot_df[['REF_YEAR', 'Alberta',
                'British Columbia',
                'Canada',
                'Manitoba',
                'New Brunswick',
                'Newfoundland and Labrador',
                'Nova Scotia',
                'Ontario',
                'Prince Edward Island',
                'Quebec', 'Saskatchewan']]
    return pivot_df
    


def pivot_table(
    df:pd.DataFrame,
    idx="REF_YEAR",
    col="GEO",
    val="VALUE",
    func="mean")->pd.DataFrame:
    """
    pivots a dataframe from long to wide
    df
    :param idx: name of columns to serve as index in new pivoted dataframe
    :param col: name of column whose values serve as new columns in the new dataframe
    :param val: takes the name of the column whose values populate the new pivoted data frame
    :param func: takes the function to aggregate duplicate values
    """
    pivot_df = pd.pivot_table(data=df,
                              index=idx,
                              columns=col,
                              values=val,
                              aggfunc=func).reset_index()
    pivot_df.columns.name=None
    pivot_df=pivot_df[['REF_YEAR', 'Alberta',
                'British Columbia',
                'Canada',
                'Manitoba',
                'New Brunswick',
                'Newfoundland and Labrador',
                'Nova Scotia',
                'Ontario',
                'Prince Edward Island',
                'Quebec', 'Saskatchewan']]
    return pivot_df


def empl_pop_ratio(
    empl_df:pd.DataFrame,
    pop_df:pd.DataFrame,
    years=[*range(2001,2023)],
    geo=['Canada',
         'Newfoundland and Labrador',
         'Prince Edward Island',
         'Nova Scotia','New Brunswick',
         'Quebec','Ontario',
         'Manitoba','Saskatchewan',
         'Alberta','British Columbia'])->pd.DataFrame:
    
    """
    Calculates the number of employees per 1000 employees.
    
    """
    years_dict={"REF_YEAR":years}
    sorted_geo=sorted(geo)
    geo_dict={prov:np.round(empl_df[prov].values/pop_df[prov].values*1000, 1) for prov in sorted_geo}
    ratio_dict=dict(chain.from_iterable(d.items() for d in (years_dict, geo_dict)))
    ratio_df=pd.DataFrame(ratio_dict)
    return ratio_df


def wide_to_long(
    df:pd.DataFrame,
    id_vars:str,
    var_name='Geographical_Location',
    value_name='PPA Employees per 1000 Residents')->pd.DataFrame:
    """
    """
    melted_df=df.melt(id_vars=id_vars, var_name=var_name, value_name=value_name)
    return melted_df

def load_config(file_name):
    with open(file_name) as f:
        data = json.load(f)
    return data
