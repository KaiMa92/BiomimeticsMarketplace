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
from app.core.bioinspiration import biomimetics_marketplace
import json

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/start')
def start():
    query = request.args.get('query', '')
    if not query or len(query.strip()) == 0:
        return "Query cannot be empty.", 400

    def generate():
        print(current_app.llm)
        for output in biomimetics_marketplace(query, current_app.llm, current_app.eng_sim, current_app.bio_sim):
            if output['type'] == 'progress':
                yield f"data: {output['message']}\n\n"
            elif output['type'] == 'results':
                result_dct = output['data']
                 # Store the result_dct in the session
                session['result_dct'] = json.dumps(result_dct)
                # Send 'done' event with 'result_dct' as JSON data
                yield f"event: done\ndata: {json.dumps(result_dct)}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@main.route('/results')
def results():
    # Retrieve the result_dct from the session and parse it as JSON
    result_dct_json = session.get('result_dct', '{}')
    result_dct = json.loads(result_dct_json)
    return render_template('results.html', results_data=result_dct)
