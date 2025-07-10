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
from pymongo import MongoClient
from openai import OpenAI
from .config.development import DevelopmentConfig as Config

from ragpipeline.load_models import load_gwdg_apikey, load_gwdg_embedding, load_gwdg_llm
from ragpipeline.indexmanager.scopusindexmanager import ScopusIndexManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load config from Config class
    app.secret_key = 'your_secret_key'

    # Initialize MongoDB
    mongo_client = MongoClient(app.config['MONGO_HOST'], app.config['MONGO_PORT'])
    app.db = mongo_client[app.config['MONGO_DB_NAME']]

    # Initialize OpenAI client
    #client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"),)
    #openai_client = OpenAI(api_key = app.config['OPENAI_API_KEY'],)
    #app.openai_client = openai_client
    
    app.llm = load_gwdg_llm('mistral-large-instruct')
    app.embedding = load_gwdg_embedding()
    app.bio_sim = ScopusIndexManager()
    app.eng_sim = ScopusIndexManager()
    
    
    # Register Blueprints or other app components
    from .routes import main
    app.register_blueprint(main)

    return app
