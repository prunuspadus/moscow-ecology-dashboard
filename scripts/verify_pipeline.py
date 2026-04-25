#!/usr/bin/env python
"""Скрипт для проверки целостности пайплайна данных"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_file(path, description):
    exists = Path(path).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def main():
    print("=" * 50)
    print("ПРОВЕРКА ЦЕЛОСТНОСТИ ПРОЕКТА")
    print("=" * 50)
    
    # 1. Проверка сырых данных
    print("\n1. СЫРЫЕ ДАННЫЕ:")
    check_file("data/raw/eco_data/air_pollution.csv", "Экология - воздух")
    check_file("data/raw/eco_data/noise.csv", "Экология - шум")
    check_file("data/avito_csv/realty_data.csv", "Недвижимость Avito")
    check_file("data/raw/moscow_districts.geojson", "GeoJSON районов")
    
    # 2. Проверка обработанных данных
    print("\n2. ОБРАБОТАННЫЕ ДАННЫЕ:")
    check_file("data/processed/ecology_by_district_2025.csv", "Эко-индекс по районам")
    check_file("data/processed/realty_with_ecology_full.csv", "Финальный датасет")
    
    # 3. Проверка модулей
    print("\n3. МОДУЛИ:")
    check_file("dashboard/analytics_module.py", "Модуль аналитики")
    check_file("dashboard/map_module.py", "Модуль карты")
    check_file("dashboard/kpi_module.py", "Модуль KPI")
    check_file("data_processing/eco_processor.py", "Обработчик экологии")
    check_file("data_processing/realty_processor.py", "Обработчик недвижимости")
    
    # 4. Попытка импорта
    print("\n4. ИМПОРТЫ:")
    try:
        from data_processing.data_merger import load_final_dataset
        print("✅ data_processing.data_merger")
    except ImportError as e:
        print(f"❌ data_processing.data_merger: {e}")
    
    try:
        from dashboard.analytics_module import render_analytics_tab
        print("✅ dashboard.analytics_module")
    except ImportError as e:
        print(f"❌ dashboard.analytics_module: {e}")
    
    print("\n" + "=" * 50)
    print("ПРОВЕРКА ЗАВЕРШЕНА")
    print("=" * 50)

if __name__ == "__main__":
    main()