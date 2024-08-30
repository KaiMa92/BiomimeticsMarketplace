# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 0.0.
"""

from flask import Blueprint, render_template, request, current_app, jsonify
from app.services.mongodb import store_likes
from .core.like import likeable

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    # Access openai_client from current_app
    openai_client = current_app.openai_client
    
    # Pass the client to the function
    results, query_id = likeable(query, "gpt-4", openai_client, ["CoreKeywordFinder1","Synonymfinder2","SpeciestoJASON4"])
    
    # Return the results to the results.html page
    return render_template('results.html', results=results, query_id=query_id)

@main.route('/like', methods=['POST'])
def like_result():
    document_id = request.form.get('query_id')
    title = request.form.get('title')
    like_state = 'like'  # Assuming this is a like action
    
    # Update MongoDB with the like state
    store_likes(document_id, title, like_state)
    return jsonify({"message": "Like state updated"}), 200

@main.route('/dislike', methods=['POST'])
def dislike_result():
    document_id = request.form.get('query_id')
    title = request.form.get('title')
    like_state = 'dislike'  # Assuming this is a dislike action
    
    # Update MongoDB with the dislike state
    store_likes(document_id, title, like_state)
    return jsonify({"message": "Dislike state updated"}), 200

