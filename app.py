import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.linear_model import Ridge
from datetime import datetime, timedelta
from your_gdd_module import calculate_and_predict_gdd, predict_growth_stages
from your_crop_info_module import crop_database
import logging
import joblib
import os
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Setup logging
logging.basicConfig(level=logging.INFO)

# Define the predictors globally
predictors = ["T2M_MAX", "T2M_MIN", "WS2M_MAX", "T2M"]

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
        gdd_data = calculate_and_predict_gdd(start_date, end_date, model_max, model_min, predictors, data, base_temp=10)

        if gdd_data.empty:
            logging.error("GDD calculation or prediction returned empty data.")
            return jsonify({"error": "GDD calculation or prediction failed"}), 500
        
        # Calculate the cumulative GDD
        cumulative_GDD = 0
        for index, entry in gdd_data.iterrows():
            gdd = entry.get('GDD', 0)
            cumulative_GDD += gdd
            gdd_data.at[index, 'cumulative_GDD'] = int(cumulative_GDD)  # Convert cumulative GDD to a whole number

        # Determine current and next growth stages based on cumulative GDD
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

        # Get pest info based on cumulative GDD
        pest_info = []
        for pest in crop_database[crop]['pests_info']:
            start_gdd = int(pest['GDD_stage'][0])
            end_gdd = int(pest['GDD_stage'][1])
            if start_gdd <= cumulative_GDD < end_gdd:
                pest_info.append(pest)

        # Get agricultural practices based on the current stage
        practices = crop_database[crop]['agricultural_practices'].get(current_stage, [])

        # Calculate total water requirement for 1 hectare
        water_requirement_per_hectare = crop_database[crop]['water_requirements']

        # **Convert gdd_data DataFrame to a list of dictionaries**
        gdd_data_dict = gdd_data.to_dict(orient='records')

        # Use predict_growth_stages to determine the stage dates
        predicted_stages = predict_growth_stages(gdd_data, growth_stages)

        # Prepare the response
        response = {
            "crop": crop,
            "cumulative_GDD": cumulative_GDD,
            "current_stage": current_stage,
            "current_stage_range": growth_stages.get(current_stage, [0, 0]),
            "next_stage": next_stage,
            "pest_info": pest_info,
            "predicted_stages": predicted_stages,  # Include the output from predict_growth_stages
            "agricultural_practices": practices,
            "water_requirement_per_hectare": water_requirement_per_hectare,
            "gdd_data": gdd_data_dict  # Include GDD data in the response as a list of dictionaries
        }

        # Log types of all items in the response for debugging
        for key, value in response.items():
            logging.info(f"{key}: {type(value)}")

        return jsonify(response)

    except Exception as e:
        logging.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == '__main__':
    app.run(debug=False)
