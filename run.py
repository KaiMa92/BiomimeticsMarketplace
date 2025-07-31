# -*- coding: utf-8 -*-
"""
@author: Max kaiser
@mail: max.kaiser@leibniz-ivw.de
@facility: Leibniz Institut für Verbundwerkstoffe GmbH
@license: MIT License
@copyright: Copyright (c) 2023 Leibniz Institut für Verbundwerkstoffe GmbH
@Version: 0.0.
"""
from app import create_app

# Create an instance of the Flask app using the factory function
app = create_app()

if __name__ == '__main__':
    print('start')
    app.run(debug=True, use_reloader= True)