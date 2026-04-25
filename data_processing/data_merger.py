# data_processing/data_merger.py
import pandas as pd
from pathlib import Path

def load_final_dataset() -> pd.DataFrame:
    """Загружает финальный датасет"""
    
    possible_paths = [
        Path('data/processed/realty_with_ecology_full.csv'),
        Path('../data/processed/realty_with_ecology_full.csv'),
        Path(__file__).parent.parent / 'data' / 'processed' / 'realty_with_ecology_full.csv',
    ]
    
    for path in possible_paths:
        if path.exists():
            df = pd.read_csv(path)
            print(f"✅ Загружены данные: {path} ({len(df)} записей)")
            return df
    
    print("⚠️ Файл realty_with_ecology_full.csv не найден")
    return pd.DataFrame()