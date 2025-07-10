# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 10:20:49 2024

@author: kaiser
"""
import requests

# Define the base URL and query
response = requests.get('https://api.openalex.org/works?search=shape memory alloy')


def search_openalex(search_query):
    openalex_search_url = 'https://api.openalex.org/works?search='
    response = requests.get(openalex_search_url+search_query)
    return response.json()


import pandas as pd

def generate_query_from_table(df):
    # Initialize an empty list to hold column queries
    column_queries = []
    
    # Iterate over each column in the DataFrame
    for col in df.columns:
        # Get all non-null values from the column (i.e., the keywords and synonyms)
        terms = df[col].dropna().tolist()
        
        # If the column has more than one term, join them with OR and wrap in parentheses
        if len(terms) > 1:
            column_query = f"({' OR '.join(terms)})"
        else:
            # If there's only one term, no need to wrap in parentheses
            column_query = terms[0]
        
        # Add the column query to the list
        column_queries.append(column_query)
    
    # Join all column queries with the operator (AND for inclusion, OR for exclusion)
    final_query = " AND ".join(column_queries)
    
    return final_query

def generate_search_query(include_df, exclude_df=None):
    # Generate the query for inclusion terms (AND across columns)
    include_query = generate_query_from_table(include_df)
    
    if exclude_df is not None:
        # Generate the query for exclusion terms (OR across columns)
        exclude_query = generate_query_from_table(exclude_df)
        # Combine inclusion and exclusion with NOT
        final_query = f"({include_query}) NOT ({exclude_query})"
    else:
        final_query = include_query
    
    return final_query

# Example usage

# Include table as a DataFrame
include_data = {
    'Column1': ['"Shape memory alloy"', 'NiTi', 'SMA', None],
    'Column2': ['SMAHC', 'Composite', None, None], 
    'Column3': ['Model', 'Design', None, None], 
    'Column4': ['Deflect', 'Bend', 'Morph', 'Adapt']
}
include_df = pd.DataFrame(include_data)

# Exclude table as a DataFrame
exclude_data = {
    'Column1': ['cookie', 'biscuit'],
    'Column2': ['monster', None]
}
exclude_df = pd.DataFrame(exclude_data)

# Generate the search query
search_query = generate_search_query(include_df, exclude_df = None)
# Output: ((elmo OR muppet) AND (sesame street OR other street)) NOT (cookie OR biscuit OR monster)
results = search_openalex(search_query)


