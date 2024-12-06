# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 0.0.
"""

from app.services import wikispecies as wiki
import json
from app.services.llm import assisted_chat

def create_results(sp_js, client):
    results = []
    system_prompt = 'For a given taxon Move to a higher taxonomic order. Only return the answer as one word.'
    for specie,description in sp_js.items():
        img = wiki.get_image_url(specie)
        print('img: ',img)
        if 'Wollmilchsau' in img: 
            print('try to find another img')
            more_common_name = assisted_chat(specie, system_prompt, 'gpt-4o-mini', client)
            print(more_common_name)
            img = wiki.get_image_url(more_common_name)
        results.append({'title': specie, 'description': description, 'image': img, 'like_state': 0})
    return results

def create_product_ideas(sp_js, client):
    results = []
    assistant_content = '''GPT Instruction: Suggest a Related Entity for Product Visualization
Purpose:

Given a product title and description, suggest one real-world entity that:

    Relates to the product at a higher abstraction level.
    Provides a visual hint of its use, context, or environment.
    Can be commonly found as an image on Wikimedia Commons.

Guidelines:

    Be General: Use broad or widely recognizable terms.
    Provide Context: Suggest where or how the product is used.
    Focus on Similarity: Include related or similar products if appropriate.
    Ensure Image Availability: Suggest entities likely to have Wikimedia Commons images.

Output Format:

    A single name of the suggested entity with not more than two words. Example: "Beach shovel"'''
    for title,description in sp_js.items():
        user_content = 'Title: ' + title + '\nDescription: ' + description
        search_term = assisted_chat(user_content, assistant_content, 'gpt-4o-mini', client)
        print(search_term)
        img = wiki.fetch_first_image_url(search_term)
        print(img)
        results.append({'title': title, 'description': description, 'image': img, 'like_state': 0})
    return results


def string_to_json(string): 
    try:
        new_json = json.loads(string.replace('json', ''))
    except: 
        new_json = json.loads(string)
    return new_json




