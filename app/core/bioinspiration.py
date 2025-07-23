# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 1.0.
"""

#categorize --> off-topic, Biology push, Technology pull

from app.core.expertfinder import filter_by_keyword, author_ranking, get_citations, summarize_nodes, explain_all_nodes
from .utils import agent_text
from llama_index.core.llms import ChatMessage
import pandas as pd

def format_multiline(text):
    formatted_data = text.replace('\n', '<br>')
    return formatted_data

def biomimetics_marketplace(query, llm, eng_sim, bio_sim): 
    initial_query = query
    location_filter = 'Frankfurt'
    top = 2


    print('categorize')
    #Categorize querys
    yield {'type': 'progress', 'message': 'Categorizing user query...'}
    categories = llm.chat([ChatMessage(role="user", content=query),ChatMessage(role='assistant', content = agent_text('agents/categorize.txt'))]).message.blocks[0].text
    print(categories)

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
        print('Should not land here')
        pass #error message necessary
    
    #Enrich engineering query
    yield {'type': 'progress', 'message': 'Enrich query...'}
    query = llm.chat([ChatMessage(role="user", content=query),ChatMessage(role='system', content = enrich_agent)]).message.blocks[0].text
    
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

    yield {'type': 'progress', 'message': 'Read abstracts...'}
    explanations = []
    # iterate through the values in the "nodes" column
    total_number_abstracts = sum(len(node_id_lst) for node_id_lst in df_top["nodes"])
    number_abstract = 0
    for node_id_lst in df_top["nodes"]:
        explanation_lst = []
        for node_id in node_id_lst: 
            number_abstract += 1
            paper_title = retrieve_df.loc[node_id]['Title']
            yield {'type': 'progress', 'message': 'Read abstract ' + str(number_abstract) + '/' + str(total_number_abstracts)+': "' + paper_title + '"...'}
            reference = id_mapping_df.loc[id_mapping_df['node_id']== node_id, 'reference'].values[0]
            explanation = '['+ str(reference) + '] ' + sim.ask_node(node_id, 'Query: ' + query, explain_agent)
            explanation_lst.append(explanation)
        explanations.append(explanation_lst)
    # assign the list back as the new column
    df_top["explanation"] = explanations

    yield {'type': 'progress', 'message': 'Summarize author expertise...'}
    summaries = []
    for _, row in df_top.iterrows():
        yield {'type': 'progress', 'message': 'Summarize work of ' + row['author_name'] + '...'}
        summary = summarize_nodes(
            sim,
            initial_query,
            summary_agent,
            row["explanation"],
            row["author_name"]
        )
        summaries.append(summary)
    df_top["summary"] = summaries

    df_top['affiliations'] = df_top['affiliations'].str[0]
    yield {'type': 'progress', 'message': 'Transform output...'}
    
    records = (
        df_top
        .sort_values("ranking")
        .loc[:, ["author_name", "summary", "affiliations", "sources"]]
        .to_dict(orient="records")
    )
    
    dct = {'Query': initial_query, 
        'Location': location_filter, 
        'Authors': records}
    print(dct)
    yield {'type': 'results', 'data': dct}


def biomimetics_marketplace_dummy(query, llm, eng_sim, bio_sim):
    dct = {'Query': 'I am doing FE Simulation on the Pelvis and the results do deviate from experiments. Need help from engineer. ',
        'Location': 'Frankfurt',
        'Authors': [{'author_name': 'Kullmer, Ottmar',
                    'summary': " Kullmer, Ottmar, has expertise in using finite element analysis (FEA) to study biomechanics, particularly in dental contexts. His work incorporates realistic loading conditions derived from experimental kinematics data, such as occlusal contact between human molars [1, 4]. This approach, which considers dynamic contact interactions and complex loading conditions, can be adapted to enhance the validation of pelvis biomechanics FE simulations. By integrating realistic loading scenarios based on kinematic analysis, Kullmer's methodology can reduce deviations from experimental results, improving the accuracy of pelvic biomechanics simulations [2, 3].",
                    'affiliations': 'Department of Palaeoanthropology and Messel Research, Senckenberg Research Institute, Frankfurt am Main, Germany', 
                    'sources': ['[1] Benazzi S.; Nguyen H.N.; Kullmer O.; Kupczik K., “Dynamic modelling of tooth deformation using occlusal kinematics and finite element analysis,” <i>PLoS ONE</i>, vol. 11, no. 3, pp. nan-nan, 2016. DOI: <a href="https://doi.org/10.1371/journal.pone.0152663" style="color: #7ed957; text-decoration: none;">10.1371/journal.pone.0152663</a>.<br>', 
                                '[2] Benazzi S.; Kullmer O.; Grosse I.R.; Weber G.W., “Using occlusal wear information and finite element analysis to investigate stress distributions in human molars,” <i>Journal of Anatomy</i>, vol. 219, no. 3, pp. 259-272, 2011. DOI: <a href="https://doi.org/10.1111/j.1469-7580.2011.01396.x" style="color: #7ed957; text-decoration: none;">10.1111/j.1469-7580.2011.01396.x</a>.<br>', 
                                '[3] Benazzi S.; Kullmer O.; Grosse I.R.; Weber G.W., “Brief communication: Comparing loading scenarios in lower first molar supporting bone structure using 3D finite element analysis,” <i>American Journal of Physical Anthropology</i>, vol. 147, no. 1, pp. 128-134, 2012. DOI: <a href="https://doi.org/10.1002/ajpa.21607" style="color: #7ed957; text-decoration: none;">10.1002/ajpa.21607</a>.<br>', 
                                '[4] Benazzi S.; Grosse I.R.; Gruppioni G.; Weber G.W.; Kullmer O., “Comparison of occlusal loading conditions in a lower second premolar using three-dimensional finite element analysis,” <i>Clinical Oral Investigations</i>, vol. 18, no. 2, pp. 369-375, 2014. DOI: <a href="https://doi.org/10.1007/s00784-013-0973-8" style="color: #7ed957; text-decoration: none;">10.1007/s00784-013-0973-8</a>.<br>']}, 
                    {'author_name': 'Webb, Nicole M.', 'summary': " Nicole M. Webb's research on the human pelvis, focusing on sexual dimorphism and geometric morphometrics, provides valuable insights into the variability and accuracy of pelvic structure analysis [5]. This expertise can aid in refining finite element (FE) simulations by incorporating more precise and inclusive biomechanical models, which account for the diverse anatomical variations in the pelvis. Additionally, her work on hipbone trabecular microarchitecture in mammals [6] offers insights into how trabecular bone adapts to mechanical stresses, potentially enhancing the design of load-bearing structures in engineering applications.", 
                    'affiliations': 'Institute of Evolutionary Medicine, University of Zurich, Zurich, Switzerland, Senckenberg Society for Nature Research, Leibniz Institution for Biodiversity and Earth System Research, Frankfurt, Germany, Institute of Archaeological Sciences, Senckenberg Centre for Human Evolution and Palaeoenvironment, Eberhard Karls University of Tübingen, Tübingen, Germany', 
                    'sources': ['[1] Krenn V.A.; Webb N.M.; Fornai C.; Haeusler M., “Sex classification using the human sacrum: Geometric morphometrics versus conventional approaches,” <i>PLoS ONE</i>, vol. 17, no. 4 April 2022, pp. nan-nan, 2022. DOI: <a href="https://doi.org/10.1371/journal.pone.0264770" style="color: #7ed957; text-decoration: none;">10.1371/journal.pone.0264770</a>.<br>', 
                                '[2] Webb N.M., “The Functional and Allometric Implications of Hipbone Trabecular Microarchitecture in a Sample of Eutherian and Metatherian Mammals,” <i>Evolutionary Biology</i>, vol. 48, no. 3, pp. 346-365, 2021. DOI: <a href="https://doi.org/10.1007/s11692-021-09543-z" style="color: #7ed957; text-decoration: none;">10.1007/s11692-021-09543-z</a>.<br>']}]}

    yield {'type': 'results', 'data': dct}