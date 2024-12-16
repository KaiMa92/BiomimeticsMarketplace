# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 0.0.
"""

from flask import Blueprint, render_template, request, current_app, jsonify, session, Response, stream_with_context
from app.services.mongodb import store_likes, load_query, store_query
from app.core.bioinspiration import bioinspire, biomimetics_marketplace
import uuid
import json


main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    print(session['session_id'])
    return render_template('index.html')

@main.route('/start')
def start():
    query = request.args.get('query', '')
    if not query or len(query.strip()) == 0:
        return "Query cannot be empty.", 400

    def generate():
        client = current_app.openai_client
        model = 'gpt-4o'#-mini' 
        for output in biomimetics_marketplace(query,model,client):
            if output['type'] == 'progress':
                yield f"data: {output['message']}\n\n"
            elif output['type'] == 'results':
                query_id = output['query_id']
                # Send 'done' event with 'query_id' as JSON data
                data = json.dumps({'query_id': str(query_id)})
                yield f"event: done\ndata: {data}\n\n"
    return Response(stream_with_context(generate()), mimetype='text/event-stream')




@main.route('/results')
def results():
    query_id = request.args.get('query_id')
    print('It works', query_id)
    if not query_id:
        return "No query ID provided.", 400
    print('Received query_id in /results route:', query_id)  # Debugging
    return render_template('results.html', query_id=query_id)



@main.route('/api/results/<query_id>')
def api_results(query_id):
    result_doc = load_query(query_id)
    if not result_doc or 'result' not in result_doc:
        return jsonify({'error': 'No results found'}), 404
    return jsonify({'result': result_doc['result']})


# @main.route('/api/results/<query_id>')
# def api_results(query_id):
#     result_doc = load_query(query_id)
#     if not result_doc or 'results' not in result_doc:
#         return jsonify({'error': 'No results found'}), 404
#     return jsonify({'results': result_doc['results']})

# # API endpoint to retrieve results as JSON
# @main.route('/api/results/<query_id>')
# def api_results(query_id):
#     result_doc = collection.find_one({'session_id': query_id})
#     if not result_doc or 'results' not in result_doc:
#         return jsonify({'error': 'No results found'}), 404
#     return jsonify(result_doc['results'])

# def get_results():
#     # Load results from the database
#     query = load_query(query_id)
    
#     if not query:
#         return jsonify({"error": "No results found for the given query ID."}), 404

#     return jsonify(query)


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

