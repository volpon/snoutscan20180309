"""
The flask application package.
"""

import os
import logging

from flask import Flask
app = Flask(__name__)

from main.api.model import db

import main.api
import main.views

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500
