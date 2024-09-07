import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.linear_model import Ridge
from datetime import datetime, timedelta
from your_gdd_module import calculate_and_predict_gdd, predict_growth_stages, plot_gdd_vs_months
from your_crop_info_module import crop_database
import logging
import joblib
import os
import requests
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Matplotlib
import matplotlib.pyplot as plt


app = Flask(__name__)

CORS(app)  # Enable CORS for cross-origin requests

# Setup logging
logging.basicConfig(level=logging.INFO)

# Define the predictors globally
predictors = ["T2M_MAX", "T2M_MIN"]

# Load the models if they exist
if os.path.exists("model_max.pkl") and os.path.exists("model_min.pkl"):
    logging.info("Loading pre-trained models...")
    model_max = joblib.load("model_max.pkl")
    model_min = joblib.load("model_min.pkl")
else:
    logging.info("Training new models...")
    # Load and preprocess the dataset
    data = pd.read_csv("daily climate data.csv", index_col="DATE")
    data.dropna(inplace=True)
    data.index = pd.to_datetime(data.index, dayfirst=True)
    
    # Shift the target values to create predictions for the next year
    data['target_max'] = data["T2M_MAX"].shift(-365)
    data['target_min'] = data["T2M_MIN"].shift(-365)
    data.dropna(inplace=True)
    
    # Train the Ridge regression models
    model_max = Ridge(alpha=0.1)
    model_min = Ridge(alpha=0.1)
    
    # Train the models using historical data
    train = data.loc[:"2019-12-31"]
    model_max.fit(train[predictors], train['target_max'])
    model_min.fit(train[predictors], train['target_min'])

    # Save the models
    joblib.dump(model_max, "model_max.pkl")
    joblib.dump(model_min, "model_min.pkl")


def fetch_weather_data(start_date, end_date):
    """
    Fetch weather data from the Open Meteo API for the given date range.
    Returns weather data as a pandas DataFrame.
    """
    try:
        # Format API URL with provided dates
        api_url = f"https://archive-api.open-meteo.com/v1/archive?latitude=8.44&longitude=4.494&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
        logging.info(f"Fetching weather data from: {api_url}")
        
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        # Convert the response into a pandas DataFrame
        dates = data["daily"]["time"]
        temperature_max = data["daily"]["temperature_2m_max"]
        temperature_min = data["daily"]["temperature_2m_min"]

        weather_df = pd.DataFrame({
            "date": pd.to_datetime(dates),
            "T2M_MAX": temperature_max,
            "T2M_MIN": temperature_min
        })
        
        return weather_df
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch weather data: {e}")
        return None


def calculate_and_predict_gdd(start_date, end_date, model_max, model_min, predictors, base_temp=10):
    try:
        # Ensure the dates are in the correct format
        logging.info(f"Calculating GDD for range: {start_date} to {end_date}")

        # Fetch weather data for the previous year (for predictor values)
        previous_year_start = pd.to_datetime(start_date) - pd.DateOffset(years=1)
        previous_year_end = pd.to_datetime(end_date) - pd.DateOffset(years=1)
        weather_data = fetch_weather_data(previous_year_start.strftime('%Y-%m-%d'), previous_year_end.strftime('%Y-%m-%d'))

        if weather_data is None or weather_data.empty:
            logging.error("Failed to retrieve weather data.")
            return pd.DataFrame()  # Return an empty DataFrame on error
        
        # Use previous year's weather data to construct the predictor DataFrame
        predictors_values = pd.DataFrame({
            "T2M_MAX": weather_data["T2M_MAX"],
            "T2M_MIN": weather_data["T2M_MIN"],
        })
        
        # Predict for all dates at once
        predictions_max = model_max.predict(predictors_values)
        predictions_min = model_min.predict(predictors_values)
        
        # Calculate GDD for all dates
        gdd_values = np.maximum(((predictions_max + predictions_min) / 2) - base_temp, 0)
        
        # Prepare the predictions DataFrame with dates and GDD values
        prediction_dates = pd.date_range(start=pd.to_datetime(start_date), end=pd.to_datetime(end_date), freq='D')
        predictions = pd.DataFrame({
            "date": prediction_dates,
            "predicted_max": predictions_max,
            "predicted_min": predictions_min,
            "GDD": gdd_values
        })

        # Calculate cumulative GDD and convert it to an integer
        predictions['cumulative_GDD'] = predictions['GDD'].cumsum().astype(int)
        
        return predictions

    except Exception as e:
        logging.error(f"Error in calculate_and_predict_gdd: {e}", exc_info=True)
        return pd.DataFrame()  # Return an empty DataFrame on error


@app.route('/predict_gdd', methods=['POST'])
def predict_gdd():
    try:
        # Get the request data
        data = request.json
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        crop = data.get('crop')

        logging.info(f"Received request for crop: {crop}, start_date: {start_date}, end_date: {end_date}")
        
        # Validate request data
        if not start_date or not end_date or not crop:
            return jsonify({"error": "Missing required parameters"}), 400

        if crop not in crop_database:
            return jsonify({"error": "Crop not found"}), 404

        # Get the crop's growth stages
        growth_stages = crop_database[crop]['growth_stages']

        # Calculate and predict GDD
        logging.info("Calculating and predicting GDD...")
        gdd_data = calculate_and_predict_gdd(start_date, end_date, model_max, model_min, predictors, base_temp=10)

        if gdd_data.empty:
            logging.error("GDD calculation or prediction returned empty data.")
            return jsonify({"error": "GDD calculation or prediction failed"}), 500
        
        # Calculate the cumulative GDD and ensure it's a whole number
        cumulative_GDD = int(gdd_data['GDD'].sum())  # Convert to whole number

        # Determine current and next growth stages based on cumulative GDD
        current_stage, next_stage = determine_growth_stage(cumulative_GDD, growth_stages)

        # Get pest info based on cumulative GDD
        pest_info = get_pest_info(crop, cumulative_GDD)

        # Get agricultural practices based on the current stage
        practices = crop_database[crop]['agricultural_practices'].get(current_stage, [])

        # Calculate total water requirement for 1 hectare
        water_requirement_per_hectare = crop_database[crop]['water_requirements']

        # Convert gdd_data DataFrame to a list of dictionaries for JSON serialization
        gdd_data_dict = gdd_data.to_dict(orient='records')

        # Use predict_growth_stages to determine the stage dates
        predicted_stages = predict_growth_stages(gdd_data, growth_stages)

        # Ensure the static directory exists
        if not os.path.exists('static'):
            os.makedirs('static')

        # Plot the GDD data using the new function and save the plot
        plot_path = os.path.join('static', f"gdd_plot_{crop}_{start_date}_{end_date}.jpg")
        plot_gdd_vs_months(gdd_data)
        plt.savefig(plot_path)
        plt.close()  # Close the plot to avoid memory leaks

        # Prepare the response
        response = {
            "crop": crop,
            "cumulative_GDD": cumulative_GDD,  # Ensure cumulative GDD is a whole number
            "current_stage": current_stage,
            "current_stage_range": growth_stages.get(current_stage, [0, 0]),
            "next_stage": next_stage,
            "pest_info": pest_info,
            "predicted_stages": predicted_stages,  # Include the output from predict_growth_stages
            "agricultural_practices": practices,
            "water_requirement_per_hectare": water_requirement_per_hectare,
            "plot_path": plot_path,
            "gdd_data": gdd_data_dict  # Include GDD data in the response as a list of dictionaries
        }

        # Log types of all items in the response for debugging
        for key, value in response.items():
            logging.info(f"{key}: {type(value)}")

        return jsonify(response)

    except Exception as e:
        logging.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({"error": "Internal Server Error"}), 500


def determine_growth_stage(cumulative_GDD, growth_stages):
    """
    Determine the current and next growth stage based on cumulative GDD.
    """
    current_stage = "Unknown"
    next_stage = ""

    for stage, (start_gdd, end_gdd) in growth_stages.items():
        if start_gdd <= cumulative_GDD < end_gdd:
            current_stage = stage
            next_stage_found = False
            for next_stage_candidate, (next_start_gdd, _) in growth_stages.items():
                if next_start_gdd > cumulative_GDD:
                    next_stage = next_stage_candidate
                    next_stage_found = True
                    break
            if not next_stage_found:
                next_stage = ""
            break
    else:
        if cumulative_GDD >= max(end_gdd for _, end_gdd in growth_stages.values()):
            current_stage = "Maturity/Harvest"
            next_stage = ""

    return current_stage, next_stage


def get_pest_info(crop, cumulative_GDD):
    """
    Retrieve pest information based on the cumulative GDD for the given crop.
    """
    pest_info = []
    for pest in crop_database[crop]['pests_info']:
        start_gdd = int(pest['GDD_stage'][0])
        end_gdd = int(pest['GDD_stage'][1])
        if start_gdd <= cumulative_GDD < end_gdd:
            pest_info.append(pest)
    return pest_info


if __name__ == '__main__':
    app.run(debug=False)
