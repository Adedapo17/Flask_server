import requests
from datetime import datetime, timedelta

def calculate_gdd(start_date, end_date, latitude, longitude):
    url = f'https://archive-api.open-meteo.com/v1/archive?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum&timezone=auto'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return [], []

    try:
        weather_data = response.json()
    except ValueError as e:
        print(f"Error parsing weather data: {e}")
        return [], []

    required_keys = ['time', 'temperature_2m_max', 'temperature_2m_min', 'precipitation_sum', 'rain_sum']
    if 'daily' not in weather_data or any(key not in weather_data['daily'] for key in required_keys):
        print("Invalid weather data format")
        return [], []

    gdd_data = []
    daily_data = weather_data['daily']
    
    for i in range(len(daily_data['time'])):
        date = daily_data['time'][i]
        try:
            max_temp = daily_data['temperature_2m_max'][i]
            min_temp = daily_data['temperature_2m_min'][i]
            precipitation = daily_data['precipitation_sum'][i]
            rain = daily_data['rain_sum'][i]
        except (IndexError, KeyError) as e:
            print(f"Missing data for date {date}: {e}")
            continue

        if max_temp is None or min_temp is None or precipitation is None or rain is None:
            print(f"Incomplete data for date {date}")
            continue

        gdd = (max_temp + min_temp) / 2 - 10
        gdd = max(0, gdd)  # GDD cannot be negative
        gdd_data.append({"date": date, "GDD": gdd})
        
    
    return gdd_data,

def predict_dates(start_date, growth_stages, gdd_data):
    cumulative_gdd = 0
    stage_dates = {}
    stages_reached = set()
    
    for gdd_entry in gdd_data:
        cumulative_gdd += gdd_entry['GDD']
        for stage, (start_gdd, end_gdd) in growth_stages.items():
            if start_gdd <= cumulative_gdd < end_gdd and stage not in stages_reached:
                stage_dates[stage] = gdd_entry['date']
                stages_reached.add(stage)
    
    # Predict future dates for remaining stages
    if gdd_data:
        last_date = datetime.strptime(gdd_data[-1]['date'], "%Y-%m-%d")
        daily_gdd_average = cumulative_gdd / len(gdd_data)
        
        if daily_gdd_average > 0:
            for stage, (start_gdd, end_gdd) in growth_stages.items():
                if stage not in stage_dates:
                    days_needed = (start_gdd - cumulative_gdd) / daily_gdd_average
                    future_date = last_date + timedelta(days=int(days_needed))
                    stage_dates[stage] = future_date.strftime("%Y-%m-%d")
    
    return stage_dates

# Example usage
start_date = "2023-05-01"
end_date = "2023-07-01"
latitude = 40.7128  # Example: Latitude for New York City
longitude = -74.0060  # Example: Longitude for New York City

gdd_data, = calculate_gdd(start_date, end_date, latitude, longitude)
print(gdd_data)

growth_stages = {
    "stage_1": (0, 100),
    "stage_2": (100, 200),
    "stage_3": (200, 300)
}

stage_dates = predict_dates(start_date, growth_stages, gdd_data)
print(stage_dates)
