# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 14:49:27 2025

@author: kaiser
"""

import pandas as pd


def add_frankfurt_authors_column(df):
    # Initialize an empty list to store the Frankfurt authors for each row
    frankfurt_authors_column = []

    # Loop through each row of the dataframe
    for index, row in df.iterrows():
        # Extract the affiliations and full names for the current row
        awa = row['Authors with affiliations'].split(';')
        authors_fullname_lst = row['Author full names'].split(';')

        # List comprehension to find the indices of Frankfurt authors
        frankfurt_authors_idx = [i for i, awa in enumerate(awa) if 'Frankfurt' in awa]

        # Create the Frankfurt authors list using indices
        frankfurt_authors = [authors_fullname_lst[n] for n in frankfurt_authors_idx]

        # Join the Frankfurt authors into a single string and append to the list
        frankfurt_authors_column.append('; '.join(frankfurt_authors))

    # Add the Frankfurt authors as a new column in the dataframe
    df['Frankfurt authors'] = frankfurt_authors_column

    return df

def add_senckenberg_authors_column(df):
    # Initialize an empty list to store the Frankfurt authors for each row
    frankfurt_authors_column = []

    # Loop through each row of the dataframe
    for index, row in df.iterrows():
        # Extract the affiliations and full names for the current row
        awa = row['Authors with affiliations'].split(';')
        authors_fullname_lst = row['Author full names'].split(';')

        # List comprehension to find the indices of Frankfurt authors
        frankfurt_authors_idx = [i for i, awa in enumerate(awa) if 'Senckenberg' in awa]

        # Create the Frankfurt authors list using indices
        frankfurt_authors = [authors_fullname_lst[n] for n in frankfurt_authors_idx]

        # Join the Frankfurt authors into a single string and append to the list
        frankfurt_authors_column.append('; '.join(frankfurt_authors))

    # Add the Frankfurt authors as a new column in the dataframe
    df['Senckenberg authors'] = frankfurt_authors_column

    return df


def author_ranking(df, author_column, score_column = 'score'):
    # Create a dataframe with authors and corresponding scores
    authors_scores = df[[author_column, score_column]].copy()
    
    # Create a column with indices of the original dataframe where the author contributed
    authors_scores['nodes'] = df.index

    # Split authors by ';' and explode the rows correctly
    authors_scores[author_column] = authors_scores[author_column].str.split(';')
    authors_scores = authors_scores.explode(author_column).reset_index(drop=True)
    
    # Clean up any leading or trailing spaces in the authors' names
    authors_scores[author_column] = authors_scores[author_column].str.strip()

    # Remove rows where the author is None or empty
    authors_scores = authors_scores[authors_scores[author_column].notna() & (authors_scores[author_column] != '')]
    

    
    # Group by author, summing scores and counting occurrences
    author_rank = authors_scores.groupby(author_column).agg(
        total_score=(score_column, 'sum'),
        count=(score_column, 'size'),
        nodes = ('nodes', 'unique')
    ).sort_values(by='total_score', ascending=False)
    
    author_rank['ranking'] = range(1,len(author_rank)+1)
    
    return author_rank


def format_ieee_citation(df, node_id, nr):
    row = df.loc[node_id]
    return (
        f"[{nr}] {row['Authors']}, “{row['Title']},” <i>{row['Source title']}</i>, "
        f"vol. {row['Volume']}, no. {row['Issue']}, pp. {row['Page start']}-{row['Page end']}, {row['Year']}. "
        f"DOI: <a href=\"https://doi.org/{row['DOI']}\">{row['DOI']}</a>."
    )

def explain_all_nodes(sim, node_id_lst, query, id_mapping_df):
    
    query_text = query
    agent_text = "You are an expert in biomimicry, biology, anatomy and taxonomy. For a given technical query and a given retrieved document text you explain why the document is relevant to the query. Think abstract like an engineer and reason how the biological structure and or system can possibly contribute to a solution of the technical query or how the described technical system can possibly be enhanced by the biological role model. Avoid repetition of the query itself. Start with a brief summary paragraph of the document followed by a description tailored to materials and composite scientists of how the content of the document can contribute to solving the problem described in the query. Be concise, formal tone, scientific language, american english."
    explanation_lst = []
    for node_id in node_id_lst: 
        reference = id_mapping_df.loc[id_mapping_df['node_id']== node_id, 'reference'].values[0]
        query_text = 'Query: ' + query_text + 'System prompt:'
        explanation = sim.ask_node(node_id, query_text, agent_text) + ' ['+ str(reference) + ']'
        explanation_lst.append(explanation)
        # Always mention the Node id in Square brackets in the text e.g. In [1] an overview... or ... the relevance of moulding is described in [2].... 
    return explanation_lst
    

def summarize_nodes(sim, query_text, node_explanations, author_name):
    summarize_agent = '''
            "You are an expert in biomimicry, biology, anatomy and taxonomy. For a given technical query and a given text you explain why the author who is responsible for the text is the optimal fitting expert to give valuable input regarding the query. Think abstract like an engineer and reason how the biological structure and or system can possibly contribute to a solution of the technical query or how the described technical system can possibly be enhanced by the biological role model.

    Your primary goals are:

        Expert-Level Tone: Ensure the text reads fluently and maintains a professional, academic tone.
        Retain Key Information: Preserve all relevant details from the summaries, ensuring no critical information is lost.
        Translate for engineers: For specific termini from biology, anatomy, taxonomy, give brief explanation for mechanical engineers/material scientist
        Emphasize References: The reference numbers (e.g., "[2]") are crucial and must remain accurately associated with their content.
        Avoid Repetition: Identify and minimize redundancy while maintaining clarity and cohesion.
        Synthesize and Link: If multiple sources present similar findings or ideas, synthesize them and link their references appropriately (e.g., "In sources [1, 2], the authors explain the function of ductile fibers").
        Fluent Transitions: Create a coherent flow between points to make the review engaging and logical.
        Always speak of one single author.

    Important Constraints:

        There must be a strong relation to the given query.
        Avoid adding introductory, concluding, or extraneous text unrelated to your specified task.
        Do not include meta-commentary about the task or the process.

    Your ultimate goal is to produce a concise, authoritative, and well-structured review of the authors expertise to contribute solving the given query. 
    '''
    query_text = "Query: "+ query_text +'\nAuthor: ' + author_name+ '\nText: '+"\n".join(node_explanations)
    summary = sim.llm.complete(summarize_agent + '\n' + query_text)
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
        
 
def find_frankfurt_experts(sim, query, path, top = 3):   
    print(query)     
    print('retrieve')
    df = sim.retrieve(query)
    print('process')
    #df_new = add_frankfurt_authors_column(df)
    #ars = author_ranking(df_new, 'Frankfurt authors')
    ars = author_ranking(df, 'Authors with affiliations')
    df_top = ars.head(top)
    df_top["author_name"] = df_top.index.str.replace(r"\s\([^)]*\)", "", regex=True)
    unique_ids = sorted(set(id for sublist in df_top["nodes"] for id in sublist))
    id_mapping_df = pd.DataFrame({"node_id": unique_ids, "reference": range(1, len(unique_ids) + 1)})
    id_mapping_df["citation"] = id_mapping_df.apply(lambda row: format_ieee_citation(df,row["node_id"], row["reference"]), axis=1)
    df_top["explanation"] = df_top["nodes"].apply(lambda node_id_lst: explain_all_nodes(sim, node_id_lst, query, id_mapping_df))
    df_top["summary"] = df_top.apply(lambda row: summarize_nodes(sim, query, row["explanation"], row["author_name"]), axis=1)
    report = report_string(query, df_top, id_mapping_df)
    print('save')
    save_html(report, path)
    
def find_senckenberg_experts(sim, query, path, top = 3):   
    print(query)     
    print('retrieve')
    df = sim.retrieve(query)
    print('process')
# =============================================================================
#     df_new = add_frankfurt_authors_column(df)
#     ars = author_ranking(df_new, 'Frankfurt authors')
# =============================================================================
    df_new = add_senckenberg_authors_column(df)
    ars = author_ranking(df_new, 'Senckenberg authors')
# =============================================================================
#     ars = author_ranking(df, 'Authors with affiliations')
# =============================================================================
    df_top = ars.head(top)
    df_top["author_name"] = df_top.index.str.replace(r"\s\([^)]*\)", "", regex=True)
    unique_ids = sorted(set(id for sublist in df_top["nodes"] for id in sublist))
    id_mapping_df = pd.DataFrame({"node_id": unique_ids, "reference": range(1, len(unique_ids) + 1)})
    id_mapping_df["citation"] = id_mapping_df.apply(lambda row: format_ieee_citation(df,row["node_id"], row["reference"]), axis=1)
    df_top["explanation"] = df_top["nodes"].apply(lambda node_id_lst: explain_all_nodes(sim, node_id_lst, query, id_mapping_df))
    df_top["summary"] = df_top.apply(lambda row: summarize_nodes(sim, query, row["explanation"], row["author_name"]), axis=1)
    report = report_string(query, df_top, id_mapping_df)
    print('save')
    save_html(report, path)







