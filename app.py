from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
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

        response = {
            "crop": crop,
            "cumulative_GDD": cumulative_GDD,
            "current_stage": current_stage,
            "current_stage_range": growth_stages.get(current_stage, [0, 0]),
            "next_stage": next_stage,
            "pest_info": pest_info,
            "predicted_dates": predictions,
            "agricultural_practices": practices
        }

        return jsonify(response)

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
