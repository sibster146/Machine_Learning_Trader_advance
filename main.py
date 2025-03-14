from simulator import Simulator
from model import BinaryClassifier
import pickle
import time
import sys
import joblib

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("No arguments provided.")
        sys.exit()

    simulation_run = "simulation_"+sys.argv[1]

    print(f"Running {simulation_run}...")
    filename = "3_update_lag_xgbclassifier1.pkl"
    with open(filename, 'rb') as file:
        loaded_model = pickle.load(file)

    filename_scaler = "3_update_lag_xgbclassifier1_scaler.pkl"
    with open(filename_scaler, "rb") as file:
        loaded_scaler = joblib.load(filename_scaler)

    price_level_num = 10
    historical_inference_max_length = 200
    update_lag = 20
    prob_limit = 0.75
    buy_amount = 10
    binary_classifier = BinaryClassifier(binary_classifier=loaded_model, price_level_num=price_level_num, historical_inference_max_length=historical_inference_max_length, update_lag = update_lag, filename = filename, prob_limit=prob_limit, simple= False, scaler=loaded_scaler, buy_amount=buy_amount)

    simulator = Simulator(symbol ="BTC-USD", binary_classifier=binary_classifier, simulation_run=simulation_run)

    simulator.start()
    time.sleep(1800)
    simulator.stop()



































