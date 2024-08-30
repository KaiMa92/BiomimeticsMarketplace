# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 0.0.
"""

from app.services.mongodb import store_query
from .bioinspiration import bioinspire

def likeable(query, model, client, steps_config): 
    results = bioinspire(query,model,client,steps_config)
    document_id = store_query(query, model, results)
    titles = [result['data']['title'] for result in results]
    return results, document_id, titles