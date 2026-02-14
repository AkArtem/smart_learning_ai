from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import cross_val_score
import numpy as np

class LinearModel:
    def __init__(self):
        self.model = LinearRegression()
        self.is_trained = False
    
    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)
        self.is_trained = True
        return self
    
    def predict(self, X):
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        return self.model.predict(X)
    
    def get_name(self):
        return "LinearRegression"


class RandomForestModel:
    def __init__(self, n_trees=100):
        self.model = RandomForestRegressor(
            n_estimators=n_trees,
            max_depth=15,
            random_state=42,
            n_jobs=-1
        )
        self.is_trained = False
    
    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)
        self.is_trained = True
        return self
    
    def predict(self, X):
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        return self.model.predict(X)
    
    def get_name(self):
        return "RandomForest"


class GradientBoostingModel:
    def __init__(self, n_estimators=100):
        self.model = GradientBoostingRegressor(
            n_estimators=n_estimators,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.is_trained = False
    
    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)
        self.is_trained = True
        return self
    
    def predict(self, X):
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        return self.model.predict(X)
    
    def get_name(self):
        return "GradientBoosting"


def train_all_models(X_train, y_train):
    models = {
        'LinearRegression': LinearModel(),
        'RandomForest': RandomForestModel(),
        'GradientBoosting': GradientBoostingModel()
    }
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.train(X_train, y_train)
    
    return models


def cross_validate_model(model_obj, X, y, cv_folds=5):
    #R^2 score
    r2_scores = cross_val_score(model_obj.model, X, y, cv=cv_folds, scoring='r2')
    
    #RMSE score
    mse_scores = cross_val_score(model_obj.model, X, y, cv=cv_folds, scoring='neg_mean_squared_error')
    rmse_scores = np.sqrt(-mse_scores)
    
    return {
        'r2_mean': r2_scores.mean(),
        'r2_std': r2_scores.std(),
        'rmse_mean': rmse_scores.mean(),
        'rmse_std': rmse_scores.std()
    }