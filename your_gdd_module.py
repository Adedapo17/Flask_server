import requests
from datetime import datetime, timedelta

def calculate_gdd(start_date, end_date):
    url = f'https://archive-api.open-meteo.com/v1/archive?latitude=8.44&longitude=4.494&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum&timezone=auto'
    
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

    if 'daily' not in weather_data or any(key not in weather_data['daily'] for key in ['time', 'temperature_2m_max', 'temperature_2m_min']):
        print("Invalid weather data format")
        return [], []

    gdd_data = []
    daily_data = weather_data['daily']
    
    for i in range(len(daily_data['time'])):
        date = daily_data['time'][i]
        try:
            max_temp = daily_data['temperature_2m_max'][i]
            min_temp = daily_data['temperature_2m_min'][i]
        except (IndexError, KeyError) as e:
            print(f"Missing data for date {date}: {e}")
            continue

        if max_temp is None or min_temp is None:
            print(f"Incomplete data for date {date}")
            continue

        gdd = (max_temp + min_temp) / 2 - 10
        gdd = max(0, gdd)  # GDD cannot be negative
        gdd_data.append({"date": date, "GDD": gdd})
    
    return gdd_data

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