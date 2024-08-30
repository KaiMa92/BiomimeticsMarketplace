# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 0.0.
"""

from flask import Blueprint, render_template, request, current_app
from .core.bioinspiration import bioinspire

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
    results = bioinspire(query, "gpt-4", openai_client, ["CoreKeywordFinder1","Synonymfinder2","SpeciestoJASON4"])
    
    # Return the results to the results.html page
    return render_template('results.html', results=results)

