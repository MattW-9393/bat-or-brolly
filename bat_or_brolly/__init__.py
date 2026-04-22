import os
from flask import Flask
from flask import render_template


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # a simple page that says hello
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/bat-or-brolly')
    def hello():
        return 'This is the app'

    @app.route('/docs')
    def docs():
        return 'The docs are here'


    return app
