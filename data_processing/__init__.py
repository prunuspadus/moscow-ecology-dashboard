# data_processing/__init__.py
"""
Модуль обработки данных
Содержит логику загрузки данных для дашборда
"""

from .data_merger import load_final_dataset

__all__ = ['load_final_dataset']