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
    if query == 'test':
        results =  [{'title': 'Podargidae', 'description': 'The family Podargidae, which includes frogmouth birds, is known for their specialized wing structures that are optimized for silent and efficient flight. Their feathers have a lightweight and composite structure that reduces wing loading and optimizes lift-to-drag ratio. This structural optimization is crucial for a biomimetic aerial payload delivery system that needs to be light and efficient.', 'image': 'https://upload.wikimedia.org/wikipedia/commons/9/90/Tawny_Frogmouth_%28Coverdale%29.jpg'}, {'title': 'Danaus plexippus', 'description': 'The Monarch butterfly (Danaus plexippus) showcases an exoskeleton with lightweight chitinous structures that provide strength without heavy mass. Their wings allow for highly efficient lift with low drag, crucial for long migratory flights. These traits can inspire lightweight composite materials for structural optimization in aerial delivery systems.', 'image': 'https://upload.wikimedia.org/wikipedia/commons/e/e4/Danaus_plexippus_MHNT.jpg'}]
        steps = [{'step_name':'test_step', 'output':'test'}]
        query_id = store_query(query, model, steps, results)
    else:
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

    return results, query_id



