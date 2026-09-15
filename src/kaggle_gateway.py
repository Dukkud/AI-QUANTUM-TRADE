"""Kaggle historical-data boundary. API credentials must be injected as secrets."""
import os

def config():
    return {
        'dataset_id': os.getenv('KAGGLE_DATASET_ID','feriandanaputra/comprehensive-xauusd-historical-price-data'),
        'api_token_configured': bool(os.getenv('KAGGLE_API_TOKEN')),
    }

def require_credentials():
    if not os.getenv('KAGGLE_API_TOKEN'):
        raise RuntimeError('KAGGLE_API_TOKEN is not configured')
