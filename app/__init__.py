# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 0.0.
"""

from flask import Flask
from .config.base import Config

from ragpipeline.load_models import load_gwdg_embedding, load_gwdg_llm
from ragpipeline.indexmanager.scopusindexmanager import ScopusIndexManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load config from Config class
    app.secret_key = 'your_secret_key'
    
    gwdg_api_key = app.config["GWDG_API_KEY"]
    print('GWDG', gwdg_api_key)
    
    
    app.llm = load_gwdg_llm('qwen3-235b-a22b', api_key= gwdg_api_key)#
    #app.llm = load_gwdg_llm('mistral-large-instruct', api_key= gwdg_api_key)#
    print(app.llm)
    app.embedding = load_gwdg_embedding()
    app.bio_sim = ScopusIndexManager(llm = app.llm, embedding_model = app.embedding, index_path = 'datasets/senckenberg/index')
    app.bio_sim.top_k = 100
    app.eng_sim = ScopusIndexManager(llm = app.llm, embedding_model = app.embedding, index_path = 'datasets/livw/index')
    app.eng_sim.top_k = 100
    
    # Register Blueprints or other app components
    from .routes import main
    app.register_blueprint(main)

    return app
