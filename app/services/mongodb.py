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
from bson import ObjectId

def get_db():
    # Access the database from the current app context
    return current_app.db

def insert_assistant(name, system_prompt, process_prompt):
    db = get_db()
    configs_collection = db.agents
    assistant_dct = {'name': name,
                     'system_prompt':system_prompt, 
                     'process_prompt': process_prompt}
    result = configs_collection.insert_one(assistant_dct)
    return result.inserted_id

def load_assistant(assistant_id=None,  assistant_name=None):
    db = get_db()
    print(db)
    configs_collection = db.agents
    query = {}
    if  assistant_id:
        query["config_id"] =  assistant_id
    elif  assistant_name:
        query["name"] =  assistant_name
    else:
        raise ValueError("Either config_id or config_name must be provided")
    assistant = configs_collection.find_one(query)
    print(assistant)
    return assistant

def get_all_assistants():
    db = get_db()
    names = db.assistants.find({}, {"_id": 0, "name": 1})
    name_list = [doc["name"] for doc in names]
    return name_list

def store_query(query, model, query_id, query_counter, result):
    db = get_db()
    chat_collection = db.chats
    query_dct = {'query': query,
                 'model': model, 
                 'query_id': query_id,
                 'query_counter': query_counter,
                 'result': result}
    result = chat_collection.insert_one(query_dct)
    return result.inserted_id

def load_query(query_id):
    db = get_db()
    chat_collection = db.chats
    query = chat_collection.find_one({'_id': ObjectId(query_id)})
    query['_id'] = str(query['_id'])
    return query

def store_likes(query_id, title, like):
    db = get_db()
    like_collection = db.like
    like_dct = {'chats_id':query_id,
                'title':title,
                'like':like}
    result = like_collection.insert_one(like_dct)
    return result.inserted_id