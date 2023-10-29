# Import modules
import pandas as pd
import numpy as np
import copy
from stats_can import StatsCan



def retrieve_data(
    table_id:str, 
    date_col_name = 'REF_DATE',
    date_to_year = False,
    drop_cols = ["DGUID", "UOM",
                  "UOM_ID", "SCALAR_FACTOR",
                  "SCALAR_ID", "VECTOR",
                  "COORDINATE", "STATUS",
                  "SYMBOL", "TERMINATED",
                  "DECIMALS"])->pd.DataFrame:
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
    sc.update_tables()
    table_df = sc.table_to_df(table = table_id)
    if date_to_year == True:
        table_df['REF_YEAR'] = table_df[date_col_name].dt.year
        table_df.drop(date_col_name, axis=1, inplace=True)
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
    idx:str,
    col:str,
    val:str)->pd.DataFrame:
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
    return pivot_df
    


def pivot_table(
    df:pd.DataFrame,
    idx:str,
    col:str,
    val:str,
    func='mean')->pd.DataFrame:
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
    return pivot_df
