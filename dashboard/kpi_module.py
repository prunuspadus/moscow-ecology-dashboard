import streamlit as st
import pandas as pd
from scipy import stats

def render_kpi(df: pd.DataFrame):
    """Отображает KPI карточки с основными метриками"""
    
    # Увеличенные KPI карточки
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_price = df['price_per_sqm_mean'].mean()
        st.metric("💰 Средняя цена за м²", f"{avg_price:,.0f} ₽")
    
    with col2:
        avg_eco = df['eco_index'].mean()
        st.metric("🌿 Средний эко-индекс", f"{avg_eco:.1f}")
    
    with col3:
        r, p = stats.pearsonr(df['price_per_sqm_mean'], df['eco_index'])
        st.metric("📈 Корреляция r", f"{r:.3f}")
    
    with col4:
        total = len(df)
        st.metric("🏘️ Районов в анализе", f"{total}")
    
    with col5:
        avg_area = df['area_mean'].mean()
        st.metric("📐 Средняя площадь", f"{avg_area:.1f} м²")