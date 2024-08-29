# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 0.0.
"""

from flask import current_app

def get_db():
    # Access the database from the current app context
    return current_app.db

def insert_assistant(assistant):
    db = get_db()
    configs_collection = db.assistants
    result = configs_collection.insert_one(assistant)
    return result.inserted_id

def load_assistant(assistant_id=None,  assistant_name=None):
    db = get_db()
    configs_collection = db.assistants
    query = {}
    if  assistant_id:
        query["config_id"] =  assistant_id
    elif  assistant_name:
        query["name"] =  assistant_name
    else:
        raise ValueError("Either config_id or config_name must be provided")
    assistant = configs_collection.find_one(query)
    return assistant

def get_all_assistants():
    db = get_db()
    names = db.assistants.find({}, {"_id": 0, "name": 1})
    name_list = [doc["name"] for doc in names]
    return name_list


#assistant = {'name': 'name',
#   'type': 'type',
#   'system_prompt': 'system_prompt'}


def insert_chat(db, chat):
    chat_collection = db.chats
    result = chat_collection.insert_one(chat)
    return result.inserted_id
