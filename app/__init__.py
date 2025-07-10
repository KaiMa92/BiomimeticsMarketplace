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
from .config.development import DevelopmentConfig as Config

from ragpipeline.load_models import load_gwdg_embedding, load_gwdg_llm
from ragpipeline.indexmanager.scopusindexmanager import ScopusIndexManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load config from Config class
    app.secret_key = 'your_secret_key'
    
    gwdg_api_key = 
    
    app.llm = load_gwdg_llm('mistral-large-instruct', api_key= gwdg_api_key)
    app.embedding = load_gwdg_embedding()
    app.bio_sim = ScopusIndexManager()
    app.eng_sim = ScopusIndexManager()
    
    
    # Register Blueprints or other app components
    from .routes import main
    app.register_blueprint(main)

    return app
