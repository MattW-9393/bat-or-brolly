import os
from flask import Flask, request, flash
from flask import render_template
from wtforms import Form, BooleanField, StringField, validators
import requests
from flask_wtf import FlaskForm


class WeatherForm(Form):
    location = StringField('Location', [validators.Length(min=1)])
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


def get_weather(coordinates):
    """Get weather using co-ordinates stored in a dict"""
    latitude = coordinates['lat']
    longitude = coordinates["long"]

    weather_url = (f'https://api.open-meteo.com/v1/'
                   f'forecast?latitude={latitude}'
                   f'&longitude={longitude}'
                   f'&hourly=temperature_2m&past_days=0'
                   f'&forecast_days=7')

    forecast_response = requests.get(weather_url)
    forecast_content = forecast_response.json()
    return forecast_content


def get_location(location_name):
    location_name = location_name
    # URL for GeoCodes
    location_url = (f'https://geocoding-api.open-meteo.com/v1/search?name={location_name}'
                    f'&count=10&language=en&format=json'
                    f'&countryCode=GB')

    # Get the Geocodes for the chosen location
    weather_location = requests.get(location_url)
    location_content = weather_location.json()
    latitude = location_content['results'][0]['latitude']
    longitude = location_content['results'][0]['longitude']
    coordinates = {"lat": latitude, "long": longitude}
    return coordinates


######## FLASK APP CODE ########
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
    def the_app():
        form = WeatherForm(request.form)
        if request.method == 'GET' and form.validate():
            location_name = form.location.data

            flash('Looking now')
        return render_template('app.html', form=form)

    return app
