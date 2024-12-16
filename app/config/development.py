# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 0.0.
"""

from .base import Config

class DevelopmentConfig(Config):
    """Development configuration with overrides for development environment."""
    
    DEBUG = True  # Enable debug mode for development
    
    # Optionally override database name or other settings
    MONGO_DB_NAME = "Development"

    # Add other development-specific configurations if needed

