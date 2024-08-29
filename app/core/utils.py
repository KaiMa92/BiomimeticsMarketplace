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

def create_results(sp_js):
    results = []
    for specie,description in sp_js.items():
        img = wiki.get_image_url(specie)
        results.append({'title': specie, 'description': description, 'image': img, 'like_state': 0})
    return results


def string_to_json(string): 
    new_json = json.loads(string.replace('json', ''))
    return new_json