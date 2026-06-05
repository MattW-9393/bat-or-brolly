import requests
from flask import Flask, request
from flask import render_template
from wtforms import Form, StringField, validators
from datetime import date, timedelta


class WeatherForm(Form):
    location = StringField('Location', [validators.Length(min=1)])


# Weather Functions
def get_weather(coordinates, date_str, time_str):
    """Get weather from Open-Meteo API using co-ordinates stored in a dict,
    at the user's chosen date and time."""
    latitude = coordinates['lat']
    longitude = coordinates["long"]

    weather_url = (f'https://api.open-meteo.com/v1/'
                   f'forecast?latitude={latitude}'
                   f'&longitude={longitude}'
                   f'&hourly=temperature_2m,precipitation_probability,wind_speed_10m'
                   f'&past_days=0'
                   f'&forecast_days=7')

    forecast_response = requests.get(weather_url)
    forecast_content = forecast_response.json()

##
    # Build the target datetime string to match Open-Meteo's format
    # e.g. "2026-05-13T14:00"
    target = f"{date_str}T{time_str}"
    times = forecast_content['hourly']['time']

    if target not in times:
        return None  # date/time outside the 7 day forecast window

    index = times.index(target)

    return{
        'temperature': forecast_content['hourly']['temperature_2m'][index],
        'rainfall':    forecast_content['hourly']['precipitation_probability'][index],
        'wind':        forecast_content['hourly']['wind_speed_10m'][index]
    }


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
        today = date.today().isoformat()
        max_date = (date.today() + timedelta(days=7)).isoformat()
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
            date_str = request.args.get('start-date')
            time_str = request.args.get('start-time')
    
            if coordinates:
                weather_data = get_weather(coordinates, date_str, time_str)
                if weather_data:
                    temperature = weather_data['temperature']
                    rainfall = weather_data['rainfall']
                    wind = weather_data['wind']
                    verdict = game_on(temperature, rainfall, wind)
                else:
                    location_error = True  # date/time outside forecast window
            else:
                location_error = True
        return render_template('app.html', 
                               today=today, max_date=max_date,
                               form=form,
                               location_name=location_name,
                               temperature=temperature,
                               rainfall=rainfall,
                               wind=wind,
                               verdict=verdict,
                               location_error=location_error,
                               nav_links=[{"href": '/', 'caption': 'Home'},
                                          {'href': '/docs', 'caption': 'docs'},
                                          {'href': '/about', 'caption': 'About & Contact Us'},
                                          {'href': '/bat_or_brolly', 'class': 'nav-cta', 'caption': 'Check conditions'}
                                          ])

    @app.route('/docs')
    def docs():
        return render_template('docs.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    return app
