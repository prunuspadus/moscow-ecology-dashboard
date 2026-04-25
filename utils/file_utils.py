# utils/file_utils.py
from pathlib import Path
import streamlit as st

def get_project_root():
    """Возвращает корневую директорию проекта"""
    return Path(__file__).parent.parent

def get_data_path(filename: str, subdir: str = 'processed') -> Path:
    """Возвращает путь к файлу в data/"""
    root = get_project_root()
    
    paths = [
        root / 'data' / subdir / filename,
        root / 'data' / filename,
        root / filename,
    ]
    
    for path in paths:
        if path.exists():
            return path
    
    return paths[0]  # возвращаем ожидаемый путь даже если файла нет