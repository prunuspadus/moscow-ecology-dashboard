# data_processing/run_processing.py
"""
Запускает обработку данных из ноутбуков
Этот скрипт нужен только если вы хотите автоматизировать перезапуск
"""

import subprocess
import sys
from pathlib import Path

def run_notebook(notebook_path: str):
    """Запускает Jupyter notebook в headless режиме"""
    cmd = [
        sys.executable, "-m", "jupyter", "nbconvert",
        "--to", "notebook",
        "--execute", notebook_path,
        "--output", notebook_path,
        "--ExecutePreprocessor.timeout=600"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def process_all_data():
    """Запускает все ноутбуки для обновления данных"""
    notebook_dir = Path(__file__).parent.parent / "notebooks"
    
    notebooks = [
        "eco_data_msk.ipynb",
        # "realty_data_msk.ipynb",  # когда добавите
    ]
    
    for nb in notebooks:
        nb_path = notebook_dir / nb
        if nb_path.exists():
            print(f"🔄 Запуск {nb}...")
            if run_notebook(str(nb_path)):
                print(f"✅ {nb} выполнен")
            else:
                print(f"❌ Ошибка в {nb}")

if __name__ == "__main__":
    process_all_data()