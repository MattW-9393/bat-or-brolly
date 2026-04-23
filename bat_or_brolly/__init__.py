import os
from flask import Flask
from flask import render_template
import requests

# URL for GeoCodes
location_url = (f'https://geocoding-api.open-meteo.com/v1/search?name={location_name}'
                f'&count=10&language=en&format=json'
                f'&countryCode=GB')

# Get the Geocodes for the chosen location
weather_location = requests.get(location_url)
location_content = weather_location.json()
latitude = location_content['results'][0]['latitude']
longitude = location_content['results'][0]['longitude']

# Get forecast data
weather_url = (f'https://api.open-meteo.com/v1/'
               f'forecast?latitude={latitude}'
               f'&longitude={longitude}'
               f'&hourly=temperature_2m&past_days=0'
               f'&forecast_days=7')


class WeatherApp:
    def __init__(self):
        pass

    def get_weather(self, url):
        pass

    def get_location(self, location):
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
        return render_template('app.html')

    @app.route('/docs')
    def docs():
        return 'The docs are here'

    @app.route('/about')
    def about():
        return 'here is info, contact me here'

    return app
