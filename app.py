import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from sklearn.linear_model import Ridge
from Flask_server.gdd_prediction import predict_future_temperatures_and_gdd
from your_gdd_module import calculate_gdd, predict_dates
from your_crop_info_module import crop_database

app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict_gdd', methods=['POST'])
def predict_gdd():
    try:
        data = request.json
        print("Received data:", data)  # Log received data

        start_date = data.get('start_date')
        end_date = data.get('end_date')
        crop = data.get('crop')

        if not start_date or not end_date or not crop:
            return jsonify({"error": "Missing required parameters"}), 400

        if crop not in crop_database:
            return jsonify({"error": "Crop not found"}), 404

        gdd_data = calculate_gdd(start_date, end_date)
        if not gdd_data:
            return jsonify({"error": "GDD data is empty or invalid"}), 500

        growth_stages = crop_database[crop]['growth_stages']
        if not all(isinstance(value, (tuple, list)) and len(value) == 2 for value in growth_stages.values()):
            return jsonify({"error": "Invalid growth stages format"}), 500

        predictions = predict_dates(start_date, growth_stages, gdd_data)
        cumulative_GDD = round(sum([entry['GDD'] for entry in gdd_data]))

        current_stage = "Unknown"
        next_stage = ""

        for stage, (start_gdd, end_gdd) in growth_stages.items():
            if start_gdd <= cumulative_GDD < end_gdd:
                current_stage = stage
                next_stage_found = False
                for next_stage_candidate in growth_stages:
                    if growth_stages[next_stage_candidate][0] > cumulative_GDD:
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

        pest_info = [pest for pest in crop_database[crop]['pests_info'] if pest['GDD_stage'][0] <= cumulative_GDD < pest['GDD_stage'][1]]
        practices = crop_database[crop]['agricultural_practices'].get(current_stage, [])

        # Calculate total water requirement (assuming it's for 1 hectare)
        water_requirement_per_hectare = crop_database[crop]['water_requirements']
        
        response = {
            "crop": crop,
            "cumulative_GDD": cumulative_GDD,
            "current_stage": current_stage,
            "current_stage_range": growth_stages.get(current_stage, [0, 0]),
            "next_stage": next_stage,
            "pest_info": pest_info,
            "predicted_dates": predictions,
            "agricultural_practices": practices,
            "water_requirement_per_hectare": water_requirement_per_hectare  # Add water requirement to the response
        }

        return jsonify(response)

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/predict_future_gdd', methods=['POST'])
def predict_future_gdd():
    try:
        data = request.json
        print("Received data:", data)  # Log received data

        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not start_date or not end_date:
            return jsonify({"error": "Missing required parameters"}), 400

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

        # Make predictions and calculate GDD
        base_temperature = 10
        future_predictions = predict_future_temperatures_and_gdd(start_date, end_date, reg_max, reg_min, predictors, data, base_temperature)

        # Calculate total cumulative GDD
        cumulative_GDD = future_predictions['cumulative_GDD'].iloc[-1]

        # Plot the predicted max and min temperatures, and the GDD for visualization
        fig, ax1 = plt.subplots(figsize=(14, 7))
        ax1.plot(future_predictions.index, future_predictions['GDD'], label='Daily GDD', color='blue')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Daily GDD')

        ax2 = ax1.twinx()
        ax2.plot(future_predictions.index, future_predictions['cumulative_GDD'], label='Cumulative GDD', color='green')
        ax2.set_ylabel('Cumulative GDD')

        # Create a single legend that includes labels from both axes
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc=0)

        plt.title('Daily and Cumulative Growing Degree Days (GDD)')
        plt.savefig('gdd_plot.jpg', transparent=True)

        response = {
            "cumulative_GDD": cumulative_GDD,
            "graph": "gdd_plot.jpg"
        }

        return jsonify(response)

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/get_graph', methods=['GET'])
def get_graph():
    return send_file('gdd_plot.png', mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)