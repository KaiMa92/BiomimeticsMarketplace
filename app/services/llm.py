# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 0.0.
"""

from app.services import mongodb as db
    
def assistant_conversation(client, model, user_content, assistant_content):
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": assistant_content},
            {"role": "user", "content": user_content}
        ],
        model=model,
    )
    return chat_completion

def assisted_chat(query, assistant_name, model, client): 
    assistant = db.load_assistant(assistant_name=assistant_name)
    results = assistant_conversation(client, model, query, assistant["system_prompt"])
    result = results.choices[0].message.content
    return result