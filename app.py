from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)
API_KEY = '30d4741c779ba94c470ca1f63045390a'
recent_searches = []


def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if data.get('cod') != 200:
        return None

    # Determine condition class
    condition = data['weather'][0]['main'].lower()
    temp = data['main']['temp']
    icon_code = data['weather'][0]['icon']  # e.g., "01d", "01n"

    if "rain" in condition:
        condition_class = "rain"
    elif "snow" in condition or temp < 5:
        condition_class = "snow"
    elif "clear" in condition and "n" in icon_code:
        condition_class = "night"
    elif "clear" in condition and "d" in icon_code and temp >= 25:
        condition_class = "sunny"
    else:
        condition_class = "cloudy"

    return {
        'city': city.title(),
        'temperature': temp,
        'condition': data['weather'][0]['description'].title(),
        'humidity': data['main']['humidity'],
        'wind': data['wind']['speed'],
        'condition_class': condition_class
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    weather = None

    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            weather = get_weather_data(city)
            if weather:
                if city.title() not in recent_searches:
                    recent_searches.insert(0, city.title())
                    if len(recent_searches) > 5:
                        recent_searches.pop()
    elif request.args.get('city'):
        city = request.args.get('city')
        weather = get_weather_data(city)

    return render_template('index.html', weather=weather, recent=recent_searches)


if __name__ == '__main__':
    app.run(debug=True)
