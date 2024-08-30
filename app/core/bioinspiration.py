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
from .utils import create_results, string_to_json
from app.services.llm import assisted_chat
from app.services.mongodb import store_query

#["CoreKeywordFinder1","Synonymfinder2","SpeciestoJASON4"]

def bioinspire(query, model, client, steps_config):
    steps = []
    input_data = query
    
    for step in steps_config:
        output_data = assisted_chat(input_data, step, model, client)
        steps.append({"step_name": step, "output": output_data})
        input_data = output_data  # Feed the output of one step as input to the next
    
    # Convert the final output to results
    sp_js = string_to_json(input_data)
    results = create_results(sp_js)

    # Store the query, steps, and results in MongoDB
    query_id = store_query(query, model, steps, results)

    return results



