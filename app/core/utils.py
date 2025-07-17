# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 0.0.
"""

#from app.services import wikispecies as wiki
import json
#from app.services.llm import assisted_chat

def agent_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except Exception as e:
        return f"Error: {str(e)}"
    

# =============================================================================
# def create_results(sp_js, client):
#     results = []
#     system_prompt = 'For a given taxon Move to a higher taxonomic order. Only return the answer as one word.'
#     for specie,description in sp_js.items():
#         img = wiki.get_image_url(specie)
#         print('img: ',img)
#         if 'Wollmilchsau' in img: 
#             print('try to find another img')
#             more_common_name = assisted_chat(specie, system_prompt, 'gpt-4o-mini', client)
#             print(more_common_name)
#             img = wiki.get_image_url(more_common_name)
#         results.append({'title': specie, 'description': description, 'image': img, 'like_state': 0})
#     return results
# =============================================================================

def string_to_json(string): 
    try:
        new_json = json.loads(string.replace('json', ''))
    except: 
        new_json = json.loads(string)
    return new_json




