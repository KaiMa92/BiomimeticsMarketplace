# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 14:49:27 2025
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 1.0.
"""

import pandas as pd
from llama_index.core.llms import ChatMessage
from app.core.utils import agent_text

def filter_by_keyword(df, filter_keyword):
    # Initialize an empty list to store the Frankfurt authors for each row
    authors_column = []
    affiliations_column = []

    # Loop through each row of the dataframe
    for index, row in df.iterrows():
        try: 
            # Extract the affiliations and full names for the current row
            awa = row['Authors with affiliations'].split(';')
            authors_fullname_lst = row['Author full names'].split(';')
    
            # List comprehension to find the indices of Frankfurt authors
            authors_idx = [i for i, awa in enumerate(awa) if filter_keyword in awa]
    
            # Create the Frankfurt authors list using indices
            authors = [authors_fullname_lst[n] for n in authors_idx]
            affiliations = [awa[n].split(',', 1)[1].strip() for n in authors_idx]
    
            # Join the Frankfurt authors into a single string and append to the list
            authors_column.append('; '.join(authors))
            affiliations_column.append('; '.join(affiliations))
        except: 
            print(index)
            print(authors_idx)
            print(authors_fullname_lst)
            print(awa)

    # Add the Frankfurt authors as a new column in the dataframe
    df['filtered_authors'] = authors_column
    df['filtered_affiliation'] = affiliations_column

    return df


def author_ranking(df):
    score_column = 'score'
    author_column = 'filtered_authors'
    aff_column    = 'filtered_affiliation'

    # 1) Work on a copy with just the columns we need + original index
    authors_scores = df[[author_column, score_column, aff_column]].copy()
    authors_scores['nodes'] = df.index

    # 2) Split both columns into lists
    authors_scores[author_column] = authors_scores[author_column].str.split(';')
    authors_scores[aff_column]    = authors_scores[aff_column].str.split(';')

    # 3) Explode both at once (pandas ≥1.3.0)
    authors_scores = authors_scores.explode([author_column, aff_column]).reset_index(drop=True)

    # 4) Strip whitespace
    authors_scores[author_column] = authors_scores[author_column].str.strip()
    authors_scores[aff_column]    = authors_scores[aff_column].str.strip()

    # 5) Drop empty or missing authors
    mask = authors_scores[author_column].notna() & (authors_scores[author_column] != '')
    authors_scores = authors_scores[mask]

    # 6) Group by author, sum scores, count papers, collect nodes & unique affiliations
    author_rank = (
        authors_scores
        .groupby(author_column)
        .agg(
            total_score  = (score_column, 'sum'),
            count        = (score_column, 'size'),
            nodes        = ('nodes', 'unique'),
            affiliations = (aff_column, 'unique')
        )
        .sort_values('total_score', ascending=False)
    )

    # 7) Add a 1-based rank
    author_rank['ranking'] = range(1, len(author_rank) + 1)
    author_rank["author_name"] = author_rank.index.str.replace(r"\s\([^)]*\)", "", regex=True)
    author_rank = author_rank.reset_index(drop=True)
    author_rank = author_rank.drop_duplicates(subset='nodes')

    return author_rank


def format_ieee_citation(df, node_id, nr):
    row = df.loc[node_id]
    return (
    f"[{nr}] {row['Authors']}, “{row['Title']},” <i>{row['Source title']}</i>, "
    f"vol. {row['Volume']}, no. {row['Issue']}, pp. {row['Page start']}-{row['Page end']}, {row['Year']}. "
    f"DOI: <a href=\"https://doi.org/{row['DOI']}\" style=\"color: #7ed957; text-decoration: none;\">{row['DOI']}</a>.<br>"
)

def get_citations(row, retrieve_df):
    citations = []
    for i, node_id in enumerate(row['nodes'], start=1):
        citations.append(format_ieee_citation(retrieve_df, node_id, i))
    return citations

def explain_all_nodes(sim, node_id_lst, query, agent_text, id_mapping_df):
    explanation_lst = []
    for node_id in node_id_lst: 
        reference = id_mapping_df.loc[id_mapping_df['node_id']== node_id, 'reference'].values[0]
        query = 'Query: ' + query + 'System prompt:'
        explanation = sim.ask_node(node_id, query, agent_text) + ' ['+ str(reference) + ']'
        explanation_lst.append(explanation)
    return explanation_lst
    

def summarize_nodes(sim, query, summarize_agent, node_explanations, author_name):
    query = "Query: "+ query +'\nAuthor: ' + author_name + '\nDocument snippets: '+"\n".join(node_explanations)
    response = sim.llm.chat([ChatMessage(role="user", content=query), ChatMessage(role='system', content = summarize_agent)])
    summary = response.message.blocks[0].text
    return summary


def report_string(query, df_top, id_mapping_df):
    # Convert the query to an HTML formatted string (e.g., make it a heading)
    query_string = f"<h1>{query}</h1>"

    # Function to create HTML entries for authors and summaries
    def create_html_entry(author, summary):
        return f"<p><strong>{author}</strong>:<br>{summary}</p>"

    # Apply the function to each row and create a new column with HTML entries
    df_top["html_text"] = df_top.apply(lambda row: create_html_entry(row["author_name"], row["summary"]), axis=1)
    
    # Combine all the entries into one string
    html_combined = "".join(df_top["html_text"])

    # Sources formatting: Convert sources to an HTML list or plain text
    sources = '<br>'.join(id_mapping_df["citation"])
    sources = f"<p><strong>Sources:</strong><br>{sources}</p>"

    # Combine everything into one final HTML report
    report_html = f"<html><body>{query_string}{html_combined}{sources}</body></html>"

    return report_html

def save_html(string, path): 
    with open(path, "w", encoding= "utf-8") as html_file:
        html_file.write(string)

def find_experts(sim, query_text, explain_agent, summary_agent, location_filter, top): 
    print('retrieve')
    retrieve_df = sim.retrieve(query_text)
    print('filter')
    filtered_df = filter_by_keyword(retrieve_df, location_filter)
    print('rank authors')
    ranked_authors_df = author_ranking(filtered_df)    
    df_top = ranked_authors_df.head(top)
    
    print('sources')
    # Apply the function to generate citations for each node in the list
    df_top['sources'] = df_top.apply(get_citations, args=(retrieve_df,), axis=1)
    
    unique_ids = sorted(set(id for sublist in df_top["nodes"] for id in sublist))
    id_mapping_df = pd.DataFrame({"node_id": unique_ids, "reference": range(1, len(unique_ids) + 1)})
    
    print('explain')
    df_top["explanation"] = df_top["nodes"].apply(lambda node_id_lst: explain_all_nodes(sim, node_id_lst, query_text, explain_agent, id_mapping_df))
    print('summarize')
    df_top["summary"] = df_top.apply(lambda row: summarize_nodes(sim, query_text, summary_agent, row["explanation"], row["author_name"]), axis=1)
    df_top['affiliations'] = df_top['affiliations'].str[0]
    
    records = (
        df_top
        .sort_values("ranking")
        .loc[:, ["author_name", "summary", "affiliations", "sources"]]
        .to_dict(orient="records")
    )
    
    dct = {'Query': query_text, 
           'Location': location_filter, 
           'Authors': records}
    print(dct)
    return dct