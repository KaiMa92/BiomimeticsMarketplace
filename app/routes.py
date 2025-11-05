# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 1.0.
"""

from flask import Blueprint, render_template, request, current_app, jsonify, session, Response, stream_with_context, redirect, url_for
from app.core.bioinspiration import biomimetics_marketplace, biomimetics_marketplace_dummy
from flask.sessions import SecureCookieSessionInterface
import json
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Prefer explicit error passed via query param; fallback to any session error
    error = request.args.get('error') or session.get('error_message', None)
    return render_template('index.html', error_message=error)

@main.route('/start')
def start():
    query = request.args.get('query', '')
    if not query or len(query.strip()) == 0:
        return "Query cannot be empty.", 400

    def generate():
        #print(current_app.llm)
        #for output in biomimetics_marketplace(query, current_app.llm, current_app.eng_sim, current_app.bio_sim):
        for output in biomimetics_marketplace(query, current_app.eng_sim, current_app.bio_sim):
            if output['type'] == 'progress':
                print("output['type'] == 'progress'")
                yield f"data: {output['message']}\n\n"
            elif output['type'] == 'redirect':
                print("output['type'] == 'redirect'")
                # Stream a redirect event that the frontend can handle
                yield f"event: redirect\ndata: {output['url']}\n\n"
                return
            elif output['type'] == 'results':
                print("output['type'] == 'results'")
                result_dct = output['data']
                print(f"result_dct = {output['data']}")
                # Persist json on harddrive
                print(f"os.getcwd() = {os.getcwd()}")
                if os.path.exists('result.json'):
                    print("remove json")
                    os.remove('result.json')
                print('save json')
                with open('result.json', 'w') as f:
                    json.dump(result_dct, f, indent=4)
                print(f"os.path.exists('result.json') = {os.path.exists('result.json')}")
                # Now yield the final done event
                yield f"event: done\ndata: {json.dumps(result_dct)}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@main.route('/results')
def results():
    # Retrieve the result_dct from the session and parse it as JSON
    print("load json")
    print(f"os.getcwd() = {os.getcwd()}")
    if os.path.exists('result.json'):
        print('json exist')
        print('read json')
        with open('result.json', 'r') as f:
            result_dct = json.loads(f.read())
        os.remove('result.json')
    else: 
        session['error_message'] = 'NO JSON ON DISK'
        return redirect(url_for('main.index'))

    print("results: result_dct:")
    print(result_dct)
    return render_template('results.html', results_data=result_dct)

@main.route('/impressum')
def impressum():
    """Rendert die Impressum-Seite."""
    return render_template('impressum.html')

@main.route('/privacy')
def privacy():
    """Rendert die Datenschutz-Seite."""
    return render_template('privacy.html')

@main.route('/dpia')
def dpia():
    """Rendert die DPIA-Dokumentations-Seite."""
    return render_template('dpia.html')

@main.route('/about')
def about():
    """Rendert die about Seite."""
    return render_template('about.html')
