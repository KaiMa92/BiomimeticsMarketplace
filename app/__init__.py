# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 1.0.
"""

from flask import Flask
from ragpipeline.indexmanager.csvindexmanager import OpenalexIndexManager

def create_app():
    app = Flask(__name__)

    app.bio_sim = OpenalexIndexManager(host = 'gwdg', llm = 'mistral-large-instruct', index_path = 'datasets/senckenberg_openalex/index')
    app.bio_sim.top_k = 30#100

    app.eng_sim = OpenalexIndexManager(host = 'gwdg', llm = 'mistral-large-instruct', index_path = 'datasets/livw_openalex/index')
    app.eng_sim.top_k = 30#100
    
    # Register Blueprints or other app components
    from .routes import main
    app.register_blueprint(main)

    return app
