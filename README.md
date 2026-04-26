# Moscow Ecology & Real Estate Dashboard

Анализ взаимосвязи экологических показателей и цен на недвижимость в Москве. Интерактивный дашборд на Streamlit с визуализацией на карте города.

## Быстрый старт

```bash
# Клонировать репозиторий

# Создать conda окружение
conda create -n moscow_ecology python=3.10 -y
conda activate moscow_ecology

# Установить зависимости
conda install -c conda-forge geopandas folium -y
pip install -r requirements.txt

# Запустить дашборд
streamlit run app.py
Структура
text
├── app.py                 # Главный файл дашборда
├── dashboard/             # Модули визуализации
├── data_processing/       # Обработка данных
├── parsers/               # Сбор данных с Avito
├── notebooks/             # Jupyter ноутбуки
└── data/                  # Данные (raw, processed)


Источники данных
Экология: data.mos.ru (качество воздуха, шум)

Недвижимость: Avito (парсинг)
