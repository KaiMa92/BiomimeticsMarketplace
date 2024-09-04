# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 0.0.
"""

from llama_index.core import StorageContext, load_index_from_storage, Settings
    
def assistant_conversation(client, model, user_content, assistant_content):
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": assistant_content},
            {"role": "user", "content": user_content}
        ],
        model=model,
    )
    return chat_completion

def assisted_chat(query, system_prompt, model, client): 
    results = assistant_conversation(client, model, query, system_prompt)
    result = results.choices[0].message.content
    return result

class index_chat:
    def __init__(self, index_path, embed_model, llm_model):
        self.llm_model = llm_model
        Settings.llm = llm_model
        self.index_path = index_path
        self.embed_model = embed_model
        self.storage_context = StorageContext.from_defaults(persist_dir=index_path)
        self.index = load_index_from_storage(self.storage_context, embed_model=embed_model, show_progress=True)
        self.query_engine = self.index.as_query_engine(streaming=False, similarity_top_k=5)

    def chat(self, query):
        return self.query_engine.query(query)
    
    def structured_response(self, query):
        response = self.chat(query)
        response_dct = {'response':response.response, 'metadata':response.metadata}
        return response_dct
    
