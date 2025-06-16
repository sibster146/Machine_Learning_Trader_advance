from simulator import Simulator
from model import BinaryClassifier
import pickle
import time
import sys
import joblib
from pathlib import Path

if __name__ == "__main__":

    repo_path = Path("simulations")  # Change this to your repo's path
    file_count = sum(1 for _ in repo_path.rglob('*') if _.is_file())

    filename = "3_update_lag_xgbclassifier2.pkl"
    simulation_run = f"simulation_{file_count+1}_{filename}"

    print(f"Running {simulation_run}...")
    with open(filename, 'rb') as file:
        loaded_model = pickle.load(file)

    filename_scaler = "3_update_lag_xgbclassifier2_scaler.pkl"
    with open(filename_scaler, "rb") as file:
        loaded_scaler = joblib.load(file)

    price_level_num = 10
    historical_inference_max_length = 200
    update_lag = 20
    prob_limit = 0.56
    buy_amount = 10
    binary_classifier = BinaryClassifier(binary_classifier=loaded_model, price_level_num=price_level_num, historical_inference_max_length=historical_inference_max_length, update_lag = update_lag, filename = filename, prob_limit=prob_limit, simple= False, scaler=loaded_scaler, buy_amount=buy_amount)

    simulator = Simulator(symbol ="BTC-USD", binary_classifier=binary_classifier, simulation_run=simulation_run)

    simulator.start()
    time.sleep(1800)
    simulator.stop()



































