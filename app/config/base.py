# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 0.0.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..','instance', '.env')
dotenv = load_dotenv(dotenv_path = dotenv_path)

class Config:
    """Base configuration with common settings."""
    DEBUG = False
    TESTING = False
    
    # MongoDB Configuration
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "DB")

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GWDG_API_KEY = os.getenv("GWDG_API_KEY")
