import requests
from datetime import datetime

def calculate_gdd(start_date, end_date):
    url = f'https://archive-api.open-meteo.com/v1/archive?latitude=8.44&longitude=4.494&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max,temperature_2m_min&timezone=auto'
    response = requests.get(url)
    weather_data = response.json()
    
    gdd_data = []
    daily_data = weather_data['daily']
    
    for i in range(len(daily_data['time'])):
        date = daily_data['time'][i]
        max_temp = daily_data['temperature_2m_max'][i]
        min_temp = daily_data['temperature_2m_min'][i]
        gdd = (max_temp + min_temp) / 2 - 10
        gdd = max(0, gdd)  # GDD cannot be negative
        gdd_data.append({"date": date, "GDD": gdd})
    
    return gdd_data

def predict_dates(start_date, growth_stages, gdd_data):
    cumulative_gdd = 0
    stage_dates = {}
    for gdd_entry in gdd_data:
        cumulative_gdd += gdd_entry['GDD']
        for stage, (start_gdd, end_gdd) in growth_stages.items():
            if start_gdd <= cumulative_gdd < end_gdd:
                stage_dates[stage] = gdd_entry['date']
    return stage_dates
