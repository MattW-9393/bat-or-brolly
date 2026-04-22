import os
from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # a simple page that says hello
    @app.route('/')
    def index():
        return 'This is the home page'

    @app.route('/bat-or-brolly')
    def hello():
        return 'This is the app'

    @app.route('/docs')
    def docs():
        return 'The docs are here'


    return app
