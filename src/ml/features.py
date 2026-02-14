import pandas as pd
import numpy as np


def create_features(df):
    features = {}
    
    features['avg_focus'] = df['focus_level'].mean()
    features['max_focus'] = df['focus_level'].max()
    features['min_focus'] = df['focus_level'].min()
    features['avg_duration'] = df['duration_minutes'].mean()
    features['total_duration'] = df['duration_minutes'].sum()
    features['avg_score'] = df['test_score'].mean() if 'test_score' in df.columns else 0
    features['max_score'] = df['test_score'].max() if 'test_score' in df.columns else 0
    features['total_sessions'] = len(df)
    features['sessions_with_score'] = (df['test_score'] > 0).sum() if 'test_score' in df.columns else 0
    
    if 'start_timestamp' in df.columns:
        try:
            df['start_timestamp'] = pd.to_datetime(df['start_timestamp'], errors='coerce')
            features['sessions_per_week'] = df.set_index('start_timestamp').resample('W').size().mean()
            features['morning_sessions'] = (df['start_timestamp'].dt.hour < 12).sum()
            features['afternoon_sessions'] = ((df['start_timestamp'].dt.hour >= 12) & (df['start_timestamp'].dt.hour < 18)).sum()
            features['evening_sessions'] = (df['start_timestamp'].dt.hour >= 18).sum()
        except:
            pass
    
    features['focus_consistency'] = (df['focus_level'] >= 4).sum() / len(df) if len(df) > 0 else 0

    if len(df) > 1:
        features['focus_improvement'] = df['focus_level'].iloc[-1] - df['focus_level'].iloc[0]
        if 'test_score' in df.columns:
            features['score_improvement'] = df['test_score'].iloc[-1] - df['test_score'].iloc[0]
    
    return pd.DataFrame([features])


def build_features(df):
    return create_features(df)