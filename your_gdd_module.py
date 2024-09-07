import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
import logging


# Example function to calculate and predict GDD
def calculate_and_predict_gdd(start_date, end_date, model_max, model_min, predictors, data, base_temp=10):
    try:
        # Ensure start_date and end_date are in the correct format
        logging.info(f"Initial Start Date: {start_date}, Type: {type(start_date)}")
        logging.info(f"Initial End Date: {end_date}, Type: {type(end_date)}")

        if isinstance(start_date, pd.Timestamp):
            start_date = start_date.strftime('%Y-%m-%d')
        if isinstance(end_date, pd.Timestamp):
            end_date = end_date.strftime('%Y-%m-%d')

        logging.info(f"Processed Start Date: {start_date}, Type: {type(start_date)}")
        logging.info(f"Processed End Date: {end_date}, Type: {type(end_date)}")

        prediction_dates = pd.date_range(
            start=pd.to_datetime(start_date), 
            end=pd.to_datetime(end_date), 
            freq='D'
        )
        predictions = pd.DataFrame(index=prediction_dates)

        for date in prediction_dates:
            previous_year_date = date - pd.DateOffset(years=1)
            previous_year_date_str = previous_year_date.strftime('%Y-%m-%d')
            weather_data = fetch_weather_data(previous_year_date_str)
            
            if weather_data:
                # Constructing the predictors DataFrame with appropriate feature names
                predictors_values = pd.DataFrame({
                    "T2M_MAX": [weather_data["temperature_2m_max"][0]],
                    "T2M_MIN": [weather_data["temperature_2m_min"][0]]
                })

                predicted_max = model_max.predict(predictors_values)[0]
                predicted_min = model_min.predict(predictors_values)[0]
                gdd = max(((predicted_max + predicted_min) / 2) - base_temp, 0)

                predictions.loc[date, 'predicted_max'] = predicted_max
                predictions.loc[date, 'predicted_min'] = predicted_min
                predictions.loc[date, 'GDD'] = gdd
            else:
                logging.warning(f"No weather data found for {previous_year_date_str}")
                predictions.loc[date, 'GDD'] = np.nan

        predictions['cumulative_GDD'] = predictions['GDD'].cumsum()
        return predictions.reset_index().rename(columns={"index": "date"})

    except Exception as e:
        logging.error(f"Error in calculate_and_predict_gdd: {e}", exc_info=True)
        return pd.DataFrame()  # Return an empty DataFrame on error

def fetch_weather_data(date_str):
    # Placeholder function for fetching weather data
    logging.info(f"Fetching weather data for {date_str}")
    # Simulate a successful API call with dummy data
    return {
        "temperature_2m_max": [30],
        "temperature_2m_min": [20],
    }

def predict_growth_stages(gdd_data, growth_stages):
    """
    Predict the dates when each growth stage is reached based on cumulative GDD.
    Also, predict future dates for remaining stages based on average GDD accumulation.
    """

    # Sort the growth stages by their GDD start values
    stages = sorted(growth_stages.items(), key=lambda x: x[1][0])
    
    # Initialize variables to track cumulative GDD and stage achievement
    cumulative_gdd = 0
    stage_dates = {}
    reached_stages = set()

    # Iterate over the GDD data to determine when each stage is reached
    for i, row in gdd_data.iterrows():
        cumulative_gdd += row['GDD']
        
        # Check for each stage if cumulative GDD has reached its threshold
        for stage, (start_gdd, end_gdd) in stages:
            if stage not in reached_stages and cumulative_gdd >= start_gdd:
                stage_dates[stage] = row['date']
                reached_stages.add(stage)
    
    # If all stages have been reached, return the stage dates
    if len(reached_stages) == len(stages):
        return stage_dates
    
    # Estimate the future dates for the remaining stages
    remaining_stages = [stage for stage in stages if stage[0] not in reached_stages]
    
    # Calculate the average daily GDD accumulation so far
    avg_gdd_per_day = gdd_data['GDD'].mean()
    
    # Predict dates for remaining stages
    last_known_date = gdd_data['date'].max()
    
    for stage, (start_gdd, end_gdd) in remaining_stages:
        if cumulative_gdd < start_gdd:
            # Calculate the number of days required to reach the start GDD of the stage
            gdd_needed = start_gdd - cumulative_gdd
            days_needed = gdd_needed / avg_gdd_per_day if avg_gdd_per_day > 0 else float('inf')
            predicted_date = last_known_date + timedelta(days=round(days_needed))
            stage_dates[stage] = predicted_date
    
    return stage_dates


# New function to plot GDD data
def plot_gdd_vs_months(gdd_data):
    # Extracting month and year for grouping and labeling
    gdd_data['year_month'] = gdd_data['date'].dt.to_period('M')

    # Summing daily GDD by month
    monthly_gdd = gdd_data.groupby('year_month').agg({'GDD': 'sum', 'cumulative_GDD': 'last'}).reset_index()
    monthly_gdd['year_month'] = monthly_gdd['year_month'].dt.to_timestamp()

    # Set up the plot
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Plot monthly GDD as bars
    ax1.bar(monthly_gdd['year_month'], monthly_gdd['GDD'], width=16, color='orange', label='Monthly GDD')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Monthly GDD', color='orange')
    ax1.tick_params(axis='y', labelcolor='orange')

    # Creating a secondary axis for cumulative GDD
    ax2 = ax1.twinx()
    ax2.plot(monthly_gdd['year_month'], monthly_gdd['cumulative_GDD'], color='blue', marker='o', label='Cumulative GDD')
    ax2.set_ylabel('Cumulative GDD', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')

    # Improve aesthetics
    ax1.set_xticks(monthly_gdd['year_month'])  # Set x-ticks to the start of each month
    ax1.set_xticklabels(monthly_gdd['year_month'].dt.strftime('%b %Y'))  # Display month and year

    fig.suptitle('Monthly GDD and Cumulative GDD', fontsize=18)
    fig.tight_layout()
    plt.show()
