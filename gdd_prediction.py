
#LATEST CODE MADE CHANGES TO THE CODES ABOVE, NOW CORRECTLY MATCHING PREDICTORS TO DATA FROM THE API


import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
import openmeteo_requests
import requests_cache
from retry_requests import retry

# Coordinates for Ilorin, Kwara State, Nigeria
latitude = 8.44
longitude = 4.494

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Function to fetch historical weather data from Open-Meteo API
def fetch_weather_data(date):
    """
    Fetches historical weather data for a specific date from the Open-Meteo API.

    Parameters:
    - date (str): Date in 'YYYY-MM-DD' format for which to fetch the data.

    Returns:
    - dict: A dictionary containing weather data for the specified date.
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": date,
        "end_date": date,
        "daily": ["temperature_2m_max", "temperature_2m_min", "wind_speed_10m_max", "temperature_2m_mean"],
        "timezone": "Africa/Lagos"
    }
    
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    
    # Process daily data
    daily = response.Daily()
    
    # Extract the necessary weather data
    weather_data = {
        "T2M_MAX": daily.Variables(0).ValuesAsNumpy()[0],  # temperature_2m_max
        "T2M_MIN": daily.Variables(1).ValuesAsNumpy()[0],  # temperature_2m_min
        "WS2M_MAX": daily.Variables(2).ValuesAsNumpy()[0],  # wind_speed_10m_max
        "T2M": daily.Variables(3).ValuesAsNumpy()[0],      # temperature_2m_mean
    }
    
    return weather_data

# Function to predict future temperatures and calculate GDD
def predict_future_temperatures_and_gdd(start_date, end_date, model_max, model_min, predictors, data, base_temp):
    """
    Predicts future temperatures for a user-defined date range based on the model trained
    on previous year's data, and calculates the Growing Degree Days (GDD).

    Parameters:
    - start_date (str): Start date of the prediction range in 'YYYY-MM-DD' format.
    - end_date (str): End date of the prediction range in 'YYYY-MM-DD' format.
    - model_max (sklearn model): Trained model for predicting max temperature.
    - model_min (sklearn model): Trained model for predicting min temperature.
    - predictors (list): List of predictor variable names.
    - data (pd.DataFrame): Original dataset used for training the model.
    - base_temp (float): Base temperature for GDD calculation.

    Returns:
    - pd.DataFrame: DataFrame with predicted max, min temperatures, daily GDD, and cumulative GDD for the future date range.
    """
    # Convert the start and end dates to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Generate date range for the prediction period
    prediction_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Initialize an empty DataFrame to store predictions and GDD
    predictions = pd.DataFrame(index=prediction_dates)
    
    # Loop through each date in the prediction range
    for date in prediction_dates:
        # Find the corresponding day in the previous year(s)
        previous_year_date = date - pd.DateOffset(years=1)
        
        # Fetch data for the previous year date from API
        previous_year_str = previous_year_date.strftime('%Y-%m-%d')
        weather_data = fetch_weather_data(previous_year_str)
        
        if weather_data:
            # Prepare the predictor values in the correct order
            predictors_values = np.array([
                weather_data["T2M_MAX"],
                weather_data["T2M_MIN"],
                weather_data["WS2M_MAX"],
                weather_data["T2M"]
            ]).reshape(1, -1)
            
            # Predict max and min temperatures
            predicted_max = model_max.predict(predictors_values)[0]
            predicted_min = model_min.predict(predictors_values)[0]
            
            # Calculate GDD
            gdd = max(((predicted_max + predicted_min) / 2) - base_temp, 0)
            
            # Store the predictions and GDD
            predictions.loc[date, 'predicted_max'] = predicted_max
            predictions.loc[date, 'predicted_min'] = predicted_min
            predictions.loc[date, 'GDD'] = gdd
        else:
            # If previous year's data is not available, assign NaN
            predictions.loc[date, 'predicted_max'] = np.nan
            predictions.loc[date, 'predicted_min'] = np.nan
            predictions.loc[date, 'GDD'] = np.nan
    
    # Calculate cumulative GDD
    predictions['cumulative_GDD'] = predictions['GDD'].cumsum()
    
    return predictions

# Load the dataset
data = pd.read_csv("daily climate data.csv", index_col="DATE")

# Clean the data by dropping rows with missing values
data.dropna(inplace=True)

# Convert the 'DATE' column to datetime and set it as index
data.index = pd.to_datetime(data.index, dayfirst=True)

# Shift the target values to create predictions for the next year
data['target_max'] = data["T2M_MAX"].shift(-365)
data['target_min'] = data["T2M_MIN"].shift(-365)

# Drop rows with NaN target values due to the shift
data.dropna(inplace=True)

# Train the Ridge regression models
reg_max = Ridge(alpha=0.1)
reg_min = Ridge(alpha=0.1)
predictors = ["T2M_MAX", "T2M_MIN", "WS2M_MAX", "T2M"]

train = data.loc[:"2019-12-31"]
reg_max.fit(train[predictors], train['target_max'])
reg_min.fit(train[predictors], train['target_min'])
