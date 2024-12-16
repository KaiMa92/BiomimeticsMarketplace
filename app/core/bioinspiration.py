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
from .utils import create_results, string_to_json, create_product_ideas
from app.services.llm import assisted_chat, agent
from app.services.mongodb import store_query, load_assistant, store_result
import time
import uuid

def bioinspire(query, model, client, steps_config):
    steps = []
    input_data = query
    
    for step in steps_config:
        system_prompt = load_assistant(assistant_name = step)["system_prompt"]
        output_data = assisted_chat(input_data, system_prompt, model, client)
        steps.append({"step_name": step, "output": output_data})
        input_data = output_data  # Feed the output of one step as input to the next
    
    # Convert the final output to results
    sp_js = string_to_json(input_data)
    results = create_results(sp_js)

    # Store the query, steps, and results in MongoDB
    query_id = store_query(query, model, steps, results)

    return query_id

# def test_function_1(input_text): 
#     yield f'test_function 1 process started...'
#     time.sleep(2)
#     #process
#     return 'output data process 1'

# def test(input_text):
#     """
#     Simulates processing the input text and yields progress updates.
#     At the end, yields the final results.
#     """
    
#     # Simulate processing steps
#     for i in range(1, 5):
# # First message: 'Process i running...'
#         yield {'type': 'progress', 'message': f'Process {i} running...'}
#         time.sleep(2)  # Simulate some processing time
#         # Second message: '... {process output data}'
#         process_output_data = f'\t\tResult of process {i} for input "{input_text}"'
#         yield {'type': 'progress', 'message': f'... {process_output_data}'}

    
    
#     # After processing, yield the final results
#     results = [
#         {
#             'title': 'Podargidae',
#             'description': 'The family Podargidae, which includes frogmouth birds, is known for their specialized wing structures that are optimized for silent and efficient flight. Their feathers have a lightweight and composite structure that reduces wing loading and optimizes lift-to-drag ratio. This structural optimization is crucial for a biomimetic aerial payload delivery system that needs to be light and efficient.',
#             'image': 'https://upload.wikimedia.org/wikipedia/commons/9/90/Tawny_Frogmouth_%28Coverdale%29.jpg'
#         },
#         {
#             'title': 'Danaus plexippus',
#             'description': 'The Monarch butterfly (Danaus plexippus) showcases an exoskeleton with lightweight chitinous structures that provide strength without heavy mass. Their wings allow for highly efficient lift with low drag, crucial for long migratory flights. These traits can inspire lightweight composite materials for structural optimization in aerial delivery systems.',
#             'image': 'https://upload.wikimedia.org/wikipedia/commons/e/e4/Danaus_plexippus_MHNT.jpg'
#         }
#     ]

#     # Example data
#     query = input_text
#     model = 'm'
#     steps_str = '1 2 and 3'

#     # Call store_query and get query_id
#     query_id = store_query(query, model, steps_str, results)


#     yield {'type': 'results', 'data': results, 'query_id': query_id}

def format_multiline(text):
    formatted_data = text.replace('\n', '<br>')
    return formatted_data

def biomimetics_marketplace(query, model, client): 

    query_id = str(uuid.uuid4())
    categorizer = agent('Categorize1', model, client)

    
    yield {'type': 'progress', 'message': categorizer.process_prompt}
    categorie = categorizer.chat_and_safe(query, query_id, 0)
    yield {'type': 'progress', 'message': categorie}

    if "Engineering" in categorie: 
        #Condense input
        condenser = agent('QueryCondenser1', model, client)
        yield {'type': 'progress', 'message': condenser.process_prompt}
        condensed_query = condenser.chat_and_safe(query, query_id, 1)
        yield {'type': 'progress', 'message': condensed_query}

        #Brainstorm concepts
        brainstormer = agent("ConceptSuggestor1", model, client)
        yield {'type': 'progress', 'message': brainstormer.process_prompt}
        concepts = brainstormer.chat_and_safe(condensed_query, query_id, 2)
        print(concepts)
        yield {'type': 'progress', 'message': format_multiline(concepts)}

        # translate concepts
        #concept_translator = agent("ConceptTranslator1", model, client)
        #yield {'type': 'progress', 'message': concept_translator.process_prompt}
        #input_string = 'Query: ' + condensed_query + '\nConcept List ' + concepts
        #translated_concepts = concept_translator.chat_and_safe(input_string, query_id, 3)
        #print(translated_concepts)
        #yield {'type': 'progress', 'message': format_multiline(translated_concepts)}

        # get role models
        concept_rolemodels = agent("RoleModelsConcepts1", model, client)
        yield {'type': 'progress', 'message': concept_rolemodels.process_prompt}
        input_string = 'Query: ' + condensed_query + '\nBiological concepts: ' + concepts
        concept_rolemodel_lst = concept_rolemodels.chat_and_safe(input_string, query_id, 4)
        print(concept_rolemodel_lst)
        yield {'type': 'progress', 'message': format_multiline(concept_rolemodel_lst)}

        # to json
        json_agent = agent("ToJson1", model, client)
        yield {'type': 'progress', 'message': json_agent.process_prompt}
        input_string = 'Query: ' + condensed_query + '\nBiological concepts and Role models: ' + concept_rolemodel_lst
        js = json_agent.chat_and_safe(concept_rolemodel_lst, query_id, 5)
        print(js)
        print(type(js))
        yield {'type': 'progress', 'message': format_multiline(js)}

        # Convert the final output to results
        sp_js = string_to_json(js)
        yield {'type': 'progress', 'message': 'Add some pictures...'}
        results = create_results(sp_js, client)
        db_query_id = store_result(query, model, query_id, results)
        print(results)
        yield {'type': 'results', 'data': results, 'query_id': db_query_id}

    elif "Biology" in categorie: 
        # mindmap
        describer = agent("PhenomenonDescription", model, client)
        yield {'type': 'progress', 'message': describer.process_prompt}
        description = describer.chat_and_safe(query, query_id, 1)
        print(description)
        yield {'type': 'progress', 'message': format_multiline(description)}

        # mindmap
        mindmapper = agent("ProductMindMapper", model, client)
        yield {'type': 'progress', 'message': mindmapper.process_prompt}
        mindmap = mindmapper.chat_and_safe(description, query_id, 2)
        print(mindmap)
        yield {'type': 'progress', 'message': format_multiline(mindmap)}

        # scamper
        scamper_agent = agent("ScamperAgent1", model, client)
        yield {'type': 'progress', 'message': scamper_agent.process_prompt}
        ideas = scamper_agent.chat_and_safe(query + '\n'+ mindmap, query_id, 3)
        print(ideas)
        yield {'type': 'progress', 'message': format_multiline(ideas)}

        # to json
        tojson = agent("ScamperToJson1", model, client)
        yield {'type': 'progress', 'message': tojson.process_prompt}
        js = tojson.chat_and_safe(ideas, query_id, 4)
        print(js)
        yield {'type': 'progress', 'message': format_multiline(js)}

        # Convert the final output to results
        sp_js = string_to_json(js)
        yield {'type': 'progress', 'message': 'Add pictures...'}
        results = create_product_ideas(sp_js, client)
        db_query_id = store_result(query, model, query_id, results)
        print(results)
        yield {'type': 'results', 'data': results, 'query_id': db_query_id}

    else: 
        pass
