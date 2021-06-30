#!/usr/bin/env python
# -*- coding utf-8 -*-

import os
import mlflow
from loguru import logger
from flask import Flask


def register_blueprints(app):
    from interfaces import get_blueprint

    blueprint = get_blueprint()
    app.register_blueprint(blueprint)

def create_app(test_config=None):
    flask_app = Flask(__name__)

    if test_config is None:
        # Load the instance config, if it exists, when not testing.
        flask_app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in.
        flask_app.config.update(test_config)

    register_blueprints(flask_app)

    return flask_app


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=port)
