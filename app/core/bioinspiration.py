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

from app.core.expertfinder import find_bio_experts, find_eng_experts
from .utils import agent_text
from llama_index.core.llms import ChatMessage

def format_multiline(text):
    formatted_data = text.replace('\n', '<br>')
    return formatted_data

def biomimetics_marketplace(query, llm, eng_sim, bio_sim): 
    print('categorize')
    #Categorize querys
    yield {'type': 'progress', 'message': 'Categorizing user query...'}
    categorie = llm.chat([ChatMessage(role="user", content=query),ChatMessage(role='assistant', content = agent_text('agents/categorize.txt'))]).message.blocks[0].text

    if "Engineering" in categorie: 
        #Enrich engineering query
        yield {'type': 'progress', 'message': 'Enrich engineering query...'}
        enriched_query = llm.chat([ChatMessage(role="user", content=query),ChatMessage(role='assistant', content = agent_text('agents/enrich_eng_query.txt'))]).message.blocks[0].text
        
        #Search experts
        yield {'type': 'progress', 'message': 'Search experts for analogous biosystems...'}
        dct = find_bio_experts_dummy(bio_sim, enriched_query, location_filter = 'Frankfurt', top = 5)

        yield {'type': 'results', 'data': dct}

    elif "Biology" in categorie: 
        
        #Enrich engineering query
        yield {'type': 'progress', 'message': 'Enrich query...'}
        enriched_query = llm.chat([ChatMessage(role="user", content=query),ChatMessage(role='assistant', content = agent_text('agents/enrich_bio_query.txt'))]).message.blocks[0].text
        
        #Search experts
        yield {'type': 'progress', 'message': 'Search experts for analogous biosystems...'}
        dct = find_eng_experts(eng_sim, enriched_query, location_filter = 'Kaiserslautern', top = 5)

        yield {'type': 'results', 'data': dct}
        
    else: 
        pass
