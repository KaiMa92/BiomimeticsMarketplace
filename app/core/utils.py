# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 1.0.
"""
from pathlib import Path

def agent_text(file_name):
    file_path = Path('agents') / f"{file_name}.txt"
    
    try:
        content = file_path.read_text(encoding='utf-8')
        print(file_name, ': ', content)
        return content
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except Exception as e:
        return f"Error: {str(e)}"






