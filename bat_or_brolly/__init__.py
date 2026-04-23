import os
from flask import Flask
from flask import render_template

class WeatherApp:
    def __init__(self):
        pass

    def get_weather(self, url):
        pass


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # a simple page that says hello
    @app.route('/')
    def index():
        return render_template('index.html',
                               home_href='/',
                               docs_href='/docs',
                               about_href='/about',
                               app_href='/bat_or_brolly',
                               nav_links=[{"href": '/', 'caption': 'Home'},
                                          {'href': '/docs', 'caption': 'docs'},
                                          {'href': '/about', 'caption': 'About & Contact Us'},
                                          {'href': '/bat_or_brolly', 'class': 'nav-cta', 'caption': 'Check conditions'}
                                          ])

    @app.route('/bat_or_brolly')
    def hello():
        return 'This is the app'

    @app.route('/docs')
    def docs():
        return 'The docs are here'

    @app.route('/about')
    def about():
        return 'here is info, contact me here'

    return app
