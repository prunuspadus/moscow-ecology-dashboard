# dashboard/kpi_module.py 
import streamlit as st
import pandas as pd
from scipy import stats

def render_kpi(df: pd.DataFrame):
    """Отображает KPI карточки с основными метриками"""
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_price = df['price_per_sqm_mean'].mean()
        st.metric("Средняя цена за м²", f"{avg_price:,.0f} ₽")
    
    with col2:
        median_price = df['price_per_sqm_median'].median()
        st.metric("Медианная цена за м²", f"{median_price:,.0f} ₽")
    
    with col3:
        avg_eco = df['eco_index'].mean()
        st.metric("Средний эко-индекс", f"{avg_eco:.1f}")
    
    with col4:
        # Корреляция по средней цене (как в блокноте)
        r, p = stats.pearsonr(df['price_per_sqm_mean'], df['eco_index'])
        st.metric("Корреляция r", f"{r:.3f}")
    
    with col5:
        total = len(df)
        st.metric("Районов в анализе", f"{total}")