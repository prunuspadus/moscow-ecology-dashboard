# app.py 
import streamlit as st
from pathlib import Path
import pandas as pd

# Настройка страницы
st.set_page_config(
    page_title="Экология и недвижимость Москвы",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Загрузка данных
@st.cache_data
def load_data():
    path = Path('data/processed/realty_with_ecology_full.csv')
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("Не удалось загрузить данные")
    st.stop()

# KPI карточки
from dashboard.kpi_module import render_kpi
render_kpi(df)

# Вкладки
tab1, tab2 = st.tabs(["Аналитика", "Карта Москвы"])

with tab1:
    from dashboard.analytics_module import render_analytics_tab
    render_analytics_tab(df)

with tab2:
    from dashboard.map_module import render_map_tab
    render_map_tab(df)

# Подвал
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Дашборд создан для анализа взаимосвязи экологических показателей "
    "и цен на недвижимость в Москве<br>"
    "Данные: data.mos.ru (экология) | Avito (цены)"
    "</div>",
    unsafe_allow_html=True
)