import requests
from flask import Flask, request
from flask import render_template
from wtforms import Form, StringField, validators


class WeatherForm(Form):
    location = StringField('Location', [validators.Length(min=1)])


# Weather Functions
def get_weather(coordinates):
    """Get weather from Open-Meteo API using co-ordinates stored in a dict"""
    latitude = coordinates['lat']
    longitude = coordinates["long"]

    weather_url = (f'https://api.open-meteo.com/v1/'
                   f'forecast?latitude={latitude}'
                   f'&longitude={longitude}'
                   f'&hourly=temperature_2m,precipitation_probability,windspeed_10m'
                   f'&past_days=0'
                   f'&forecast_days=7')

    forecast_response = requests.get(weather_url)
    forecast_content = forecast_response.json()
    return forecast_content


def get_location(location_name):
    """Get GeoCode co-ordinates in latitude/longitude format
        to be used in the open-meteo API call. Try except means that 'None'
        is returned gracefully."""
    try:
        location_url = (f'https://geocoding-api.open-meteo.com/v1/search?name={location_name}'
                        f'&count=10&language=en&format=json&countryCode=GB')
        weather_location = requests.get(location_url)
        location_content = weather_location.json()
        latitude = location_content['results'][0]['latitude']
        longitude = location_content['results'][0]['longitude']
        return {"lat": latitude, "long": longitude}
    except (KeyError, IndexError):
        return None


# Cricket Logic code
def game_on(temperature, rainfall, wind):
    if 18 < temperature < 25 and wind < 19 and rainfall < 40:
        verdict = "Excellent conditions"
    elif 14 < temperature <= 18 and wind < 25 and rainfall < 55:
        verdict = "Good conditions"
    elif 10 < temperature <= 14 and wind < 30 and rainfall < 70:
        verdict = "Playable but not ideal"
    elif 7 < temperature <= 10 or wind >= 30 or rainfall >= 70:
        verdict = "Poor conditions"
    else:
        verdict = "Game off"
    return verdict


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

    @app.route('/bat_or_brolly', methods=['GET'])
    def the_app():
        form = WeatherForm(request.args)
        temperature = None
        rainfall = None
        wind = None
        verdict = None
        location_error = False

        location_name = request.args.get('location')
        if location_name:
            location_name = location_name.title()
            coordinates = get_location(location_name)
            if coordinates:
                weather_data = get_weather(coordinates)
                # Time set at 14:00 of the current day for Weather Statistics
                temperature = weather_data['hourly']['temperature_2m'][14]
                rainfall = weather_data['hourly']['precipitation_probability'][14]
                wind = weather_data['hourly']['windspeed_10m'][14]
                verdict = game_on(temperature, rainfall, wind)
            else:
                location_error = True
        return render_template('app.html', form=form,
                               location_name=location_name,
                               temperature=temperature,
                               rainfall=rainfall,
                               wind=wind,
                               verdict=verdict,
                               location_error=location_error)

    @app.route('/docs')
    def docs():
        return render_template('docs.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    return app
