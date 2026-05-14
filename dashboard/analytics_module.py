import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy import stats

def calculate_correlation_stats(df: pd.DataFrame):
    """Рассчитывает статистические метрики корреляции для средней цены"""
    data = df[['price_per_sqm_mean', 'eco_index']].dropna()
    x = data['eco_index']
    y = data['price_per_sqm_mean']
    
    r, p_value = stats.pearsonr(x, y)
    r_squared = r ** 2
    
    abs_r = abs(r)
    if abs_r < 0.1:
        strength = "очень слабая"
    elif abs_r < 0.3:
        strength = "слабая"
    elif abs_r < 0.5:
        strength = "умеренная"
    elif abs_r < 0.7:
        strength = "заметная"
    elif abs_r < 0.9:
        strength = "высокая"
    else:
        strength = "очень высокая"
    
    direction = "положительная" if r > 0 else "отрицательная"
    interpretation = f"{strength} {direction} связь"
    is_significant = p_value < 0.05
    
    return {
        'r': r,
        'p_value': p_value,
        'r_squared': r_squared,
        'interpretation': interpretation,
        'is_significant': is_significant,
        'n_samples': len(x)
    }


def render_analytics_tab(df: pd.DataFrame):
    """Отображает вкладку с графиками аналитики (компактная версия)"""
    
    # Статистический анализ корреляции (свернутый по умолчанию)
    with st.expander("📊 Статистический анализ корреляции", expanded=False):
        stats = calculate_correlation_stats(df)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Коэффициент корреляции (r)", f"{stats['r']:.3f}")
            st.caption(f"p-value: {stats['p_value']:.4f}")
        with col2:
            st.metric("Коэффициент детерминации (R²)", f"{stats['r_squared']:.3f}")
            st.caption(f"n = {stats['n_samples']} районов")
        with col3:
            st.metric("Интерпретация", stats['interpretation'])
        with col4:
            status = "✅ значимо" if stats['is_significant'] else "⚠️ не значимо"
            st.metric("Статистическая значимость", status)
    
    # Основные графики в 2 колонки
    col_left, col_right = st.columns(2, gap="medium")
    
    with col_left:
        st.subheader("📉 Диаграмма рассеяния")
        _render_scatter_plot_compact(df)
    
    with col_right:
        st.subheader("🔥 Матрица корреляций")
        _render_correlation_matrix_compact(df)
    
    # Второй ряд
    col_left2, col_right2 = st.columns(2, gap="medium")
    
    with col_left2:
        st.subheader("📦 Распределение цен по экологии")
        _render_box_plot_compact(df)
    
    with col_right2:
        st.subheader("🏆 Топ-5 районов")
        _render_top_districts_compact(df)


def _render_scatter_plot_compact(df: pd.DataFrame):
    """Компактный scatter plot"""
    plot_df = df[['eco_index', 'price_per_sqm_mean', 'eco_category', 'area_mean', 'District']].dropna()
    stats = calculate_correlation_stats(df)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=plot_df['eco_index'],
        y=plot_df['price_per_sqm_mean'],
        mode='markers',
        marker=dict(
            size=8,
            color=plot_df['eco_category'].map({
                'A (Отлично)': '#2ecc71',
                'B (Хорошо)': '#f1c40f', 
                'C (Удовлетворительно)': '#e67e22'
            }).fillna('#95a5a6'),
            showscale=False,
            opacity=0.7,
            line=dict(width=0)
        ),
        text=plot_df['District'],
        hovertemplate='<b>%{text}</b><br>🌿 Эко-индекс: %{x:.1f}<br>💰 Цена: %{y:,.0f} ₽<extra></extra>',
        name='Районы'
    ))
    
    # Линия тренда
    z = np.polyfit(plot_df['eco_index'], plot_df['price_per_sqm_mean'], 1)
    p = np.poly1d(z)
    x_trend = np.linspace(plot_df['eco_index'].min(), plot_df['eco_index'].max(), 100)
    y_trend = p(x_trend)
    
    fig.add_trace(go.Scatter(
        x=x_trend,
        y=y_trend,
        mode='lines',
        line=dict(color='red', width=2, dash='dash'),
        name=f'r = {stats["r"]:.3f}'
    ))
    
    fig.update_layout(
        height=350,
        margin=dict(l=40, r=20, t=20, b=40),
        xaxis_title='Эко-индекс',
        yaxis_title='Цена, ₽',
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _render_correlation_matrix_compact(df: pd.DataFrame):
    """Компактная тепловая карта корреляции"""
    available_cols = ['price_per_sqm_mean', 'eco_index', 'area_mean']
    
    for col in ['air_quality_score', 'noise_quality', 'ads_count']:
        if col in df.columns:
            available_cols.append(col)
    
    corr_matrix = df[available_cols].corr()
    
    rename_map = {
        'price_per_sqm_mean': 'Цена',
        'eco_index': 'Эко',
        'area_mean': 'Площадь',
        'air_quality_score': 'Воздух',
        'noise_quality': 'Шум',
        'ads_count': 'Объявления'
    }
    corr_matrix = corr_matrix.rename(index=rename_map, columns=rename_map)
    
    fig = px.imshow(
        corr_matrix,
        text_auto='.2f',
        aspect='auto',
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1
    )
    
    fig.update_layout(
        height=350,
        margin=dict(l=40, r=20, t=20, b=40),
        coloraxis_colorbar=dict(title="r", thickness=15)
    )
    fig.update_traces(textfont=dict(size=10))
    
    st.plotly_chart(fig, use_container_width=True)


def _render_box_plot_compact(df: pd.DataFrame):
    """Компактный box plot"""
    plot_df = df[df['eco_category'] != 'Нет данных'].copy()
    
    if len(plot_df) == 0:
        st.info("Недостаточно данных")
        return
    
    fig = px.box(
        plot_df,
        x='eco_category',
        y='price_per_sqm_mean',
        color='eco_category',
        color_discrete_map={
            'A (Отлично)': '#2ecc71',
            'B (Хорошо)': '#f1c40f',
            'C (Удовлетворительно)': '#e67e22'
        }
    )
    
    fig.update_layout(
        height=350,
        margin=dict(l=40, r=20, t=20, b=40),
        xaxis_title='Категория экологии',
        yaxis_title='Цена, ₽',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _render_top_districts_compact(df: pd.DataFrame):
    """Компактные рейтинги (в одну строку)"""
    
    # Легенда категорий
    st.markdown("""
    <div style='font-size: 12px; margin-bottom: 10px;'>
        <span style='color:#2ecc71;'>●</span> A (80-100) 
        <span style='color:#f1c40f; margin-left: 8px;'>●</span> B (60-80) 
        <span style='color:#e67e22; margin-left: 8px;'>●</span> C (40-60)
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🌿 Топ-5 экологичных районов**")
        top_eco = df.nlargest(5, 'eco_index')
        for i, (_, row) in enumerate(top_eco.iterrows(), 1):
            price_k = row['price_per_sqm_mean'] / 1000
            st.markdown(f"{i}. **{row['District']}** — эко-индекс {row['eco_index']:.0f}, {price_k:.0f} тыс ₽")
    
    with col2:
        st.markdown("**💰 Топ-5 дорогих районов**")
        top_price = df.nlargest(5, 'price_per_sqm_mean')
        for i, (_, row) in enumerate(top_price.iterrows(), 1):
            price_k = row['price_per_sqm_mean'] / 1000
            st.markdown(f"{i}. **{row['District']}** — {price_k:.0f} тыс ₽, эко-индекс {row['eco_index']:.0f}")