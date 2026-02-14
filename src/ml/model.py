import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error


def calculate_rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))


def calculate_mae(y_true, y_pred):
    return mean_absolute_error(y_true, y_pred)


def calculate_r2(y_true, y_pred):
    return r2_score(y_true, y_pred)


def evaluate_model(y_true, y_pred):
    return {
        'rmse': calculate_rmse(y_true, y_pred),
        'mae': calculate_mae(y_true, y_pred),
        'r2': calculate_r2(y_true, y_pred)}


def compare_models(predictions_dict, y_true):
    results = []
    
    for model_name, y_pred in predictions_dict.items():
        metrics = evaluate_model(y_true, y_pred)
        metrics['model'] = model_name
        results.append(metrics)
    
    df = pd.DataFrame(results)
    df = df.sort_values('r2', ascending=False)
    
    return df


def print_metrics(y_true, y_pred, model_name="Model"):
    metrics = evaluate_model(y_true, y_pred)
    
    print(f"\n{model_name} Metrics:")
    print("-" * 40)
    for metric, value in metrics.items():
        print(f"  {metric:10s}: {value:.4f}")
    print("-" * 40)