# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 0.0.
"""

#categorize --> off-topic, Biology push, Technology pull

from app.core.expertfinder import find_bio_experts, find_eng_experts, find_bio_experts_dummy, filter_by_keyword, author_ranking, get_citations, summarize_nodes, explain_all_nodes
from .utils import agent_text
from llama_index.core.llms import ChatMessage
import pandas as pd

def format_multiline(text):
    formatted_data = text.replace('\n', '<br>')
    return formatted_data

def biomimetics_marketplace(query, llm, eng_sim, bio_sim): 
    location_filter = 'Frankfurt'
    top = 5


    print('categorize')
    #Categorize querys
    yield {'type': 'progress', 'message': 'Categorizing user query...'}
    categories = llm.chat([ChatMessage(role="user", content=query),ChatMessage(role='assistant', content = agent_text('agents/categorize.txt'))]).message.blocks[0].text

    if "Engineering" in categories: 
        summary_agent = agent_text('agents/bio_expert_summarize.txt')
        explain_agent = agent_text('agents/bio_documents_explain.txt')
        enrich_agent = agent_text('agents/enrich_eng_query.txt')
        search_expert_text = 'Search experts for analogous biosystems...'
        sim = bio_sim

    elif "Biology" in categories:
        summary_agent = agent_text('agents/bio_expert_summarize.txt')
        explain_agent = agent_text('agents/bio_documents_explain.txt')
        enrich_agent = agent_text('agents/enrich_eng_query.txt')
        search_expert_text = 'Search for skilled engineers...'
        sim = eng_sim
    
    else: 
        pass #error message necessary
    
    #Enrich engineering query
    yield {'type': 'progress', 'message': 'Enrich query...'}
    query = llm.chat([ChatMessage(role="user", content=query),ChatMessage(role='assistant', content = enrich_agent)]).message.blocks[0].text
    
    #Search experts
    yield {'type': 'progress', 'message': search_expert_text}
    retrieve_df = sim.retrieve(query)
    yield {'type': 'progress', 'message': 'Filter experts by location...'}
    filtered_df = filter_by_keyword(retrieve_df, location_filter)
    yield {'type': 'progress', 'message': 'Rank authors...'}
    ranked_authors_df = author_ranking(filtered_df)    
    df_top = ranked_authors_df.head(top)
    yield {'type': 'progress', 'message': 'Make IEEE references for sources...'}
    df_top['sources'] = df_top.apply(get_citations, args=(retrieve_df,), axis=1)
    unique_ids = sorted(set(id for sublist in df_top["nodes"] for id in sublist))
    id_mapping_df = pd.DataFrame({"node_id": unique_ids, "reference": range(1, len(unique_ids) + 1)})

    yield {'type': 'progress', 'message': 'Read author papers...'}
    explanations = []
    # iterate through the values in the "nodes" column
    for node_id_lst in df_top["nodes"]:
        explanation_lst = []
        for node_id in node_id_lst: 
            reference = id_mapping_df.loc[id_mapping_df['node_id']== node_id, 'reference'].values[0]
            query = 'Query: ' + query + 'System prompt:'
            explanation = sim.ask_node(node_id, query, agent_text) + ' ['+ str(reference) + ']'
            explanation_lst.append(explanation)
            paper_title = retrieve_df.loc[node_id]['Title']
            yield {'type': 'progress', 'message': 'Read "' + paper_title + '"...'}
        explanations.append(explanation_lst)
    # assign the list back as the new column
    df_top["explanation"] = explanations

    df_top["explanation"] = df_top["nodes"].apply(lambda node_id_lst: explain_all_nodes(sim, node_id_lst, query, explain_agent, id_mapping_df))
    yield {'type': 'progress', 'message': 'Summarize author expertise...'}


    summaries = []

    for _, row in df_top.iterrows():
        yield {'type': 'progress', 'message': 'Summarize work of ' + row['author_name'] + '...'}
        summary = summarize_nodes(
            sim,
            query,
            summary_agent,
            row["explanation"],
            row["author_name"]
        )
        summaries.append(summary)
        df_top["summary"] = summaries
        df_top["summary"] = df_top.apply(lambda row: summarize_nodes(sim, query, summary_agent, row["explanation"], row["author_name"]), axis=1)

    df_top['affiliations'] = df_top['affiliations'].str[0]
    yield {'type': 'progress', 'message': 'Transform output...'}
    
    records = (
        df_top
        .sort_values("ranking")
        .loc[:, ["author_name", "summary", "affiliations", "sources"]]
        .to_dict(orient="records")
    )
    
    dct = {'Query': query, 
        'Location': location_filter, 
        'Authors': records}
    print(dct)
    yield {'type': 'results', 'data': dct}

