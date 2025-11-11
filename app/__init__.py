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
import os
import secrets
from pathlib import Path


def _load_dotenv_if_present() -> None:
    """Load environment variables from a local .env file if available.

    - Uses python-dotenv when installed; otherwise falls back to a simple parser.
    - Does not overwrite variables that are already set in the environment.
    """
    # Try python-dotenv first (if present, this is the most robust)
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
        return
    except Exception:
        pass

def create_app():
    app = Flask(__name__)

    # Load variables from .env (if present) and configure SECRET_KEY
    _load_dotenv_if_present()
    secret = os.environ.get("SECRET_KEY")
    if not secret:
        raise RuntimeError(
            "SECRET_KEY not set. Define it in the environment or .env for production."
        )
    app.config["SECRET_KEY"] = secret

    # Optional cookie hardening (can be overridden via env or config)
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    if os.environ.get("SESSION_COOKIE_SECURE", "").lower() in ("1", "true", "yes"):    
        app.config["SESSION_COOKIE_SECURE"] = True

    app.bio_sim = OpenalexIndexManager(host = 'gwdg', llm = 'mistral-large-instruct', index_path = 'datasets/senckenberg_openalex/index')
    app.bio_sim.top_k = 30#100

    app.eng_sim = OpenalexIndexManager(host = 'gwdg', llm = 'mistral-large-instruct', index_path = 'datasets/livw_openalex/index')
    app.eng_sim.top_k = 30#100
    
    # Register Blueprints or other app components
    from .routes import main
    app.register_blueprint(main)

    return app
