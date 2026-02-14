import joblib
import numpy as np
import pandas as pd
from pathlib import Path


def save_model(model, model_name, model_dir='models'):
    Path(model_dir).mkdir(exist_ok=True)
    filepath = Path(model_dir) / f"{model_name}.pkl"
    joblib.dump(model, filepath)
    print(f"Model saved: {filepath}")
    return filepath


def load_model(model_name, model_dir='models'):
    filepath = Path(model_dir) / f"{model_name}.pkl"
    if not filepath.exists():
        raise FileNotFoundError(f"Model not found: {filepath}")
    
    model = joblib.load(filepath)
    print(f"Model loaded: {filepath}")
    return model


def predict(model, X):
    if isinstance(X, pd.DataFrame):
        X = X.values
    return model.predict(X)


def predict_with_uncertainty(model, X):
    preds = predict(model, X)
    uncertainty = np.std(preds) * 0.1
    
    return {
        'predictions': preds,
        'uncertainty': uncertainty}


def save_all_models(models_dict, model_dir='models'):
    for name, model in models_dict.items():
        save_model(model, name, model_dir)


def load_all_models(model_names, model_dir='models'):
    models = {}
    for name in model_names:
        models[name] = load_model(name, model_dir)
    return models


def ensemble_predict(models_dict, X, method='average'):
    predictions = []
    
    for model in models_dict.values():
        preds = predict(model, X)
        predictions.append(preds)
    pred_array = np.array(predictions)
    if method == 'average':
        return pred_array.mean(axis=0)
    elif method == 'median':
        return np.median(pred_array, axis=0)
    else:
        raise ValueError(f"Unknown method: {method}")