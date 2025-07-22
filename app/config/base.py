# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 1.0.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
#dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv = load_dotenv()

class Config:
    """Base configuration with common settings."""
    DEBUG = False
    TESTING = False

    # OpenAI Configuration
    GWDG_API_KEY = os.getenv("GWDG_API_KEY")
