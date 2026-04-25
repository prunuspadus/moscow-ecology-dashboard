# dashboard/analytics_module.py 
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy import stats

def calculate_correlation_stats(df: pd.DataFrame, x_col: str, y_col: str):
    """Рассчитывает статистические метрики корреляции"""
    data = df[[x_col, y_col]].dropna()
    x = data[x_col]
    y = data[y_col]
    
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
    significance_text = "статистически значимо" if is_significant else "статистически не значимо"
    
    return {
        'r': r,
        'p_value': p_value,
        'r_squared': r_squared,
        'interpretation': interpretation,
        'significance': significance_text,
        'is_significant': is_significant,
        'n_samples': len(x)
    }


def render_analytics_tab(df: pd.DataFrame):
    """Отображает вкладку с графиками аналитики"""
    
    st.subheader("Взаимосвязь цены и экологии")
    
    # Статистическая карточка
    with st.expander("Статистический анализ корреляции", expanded=True):
        stats_mean = calculate_correlation_stats(df, 'eco_index', 'price_per_sqm_mean')
        stats_median = calculate_correlation_stats(df, 'eco_index', 'price_per_sqm_median')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Средняя цена**")
            _render_stats_card(stats_mean)
        with col2:
            st.markdown("**Медианная цена**")
            _render_stats_card(stats_median)
    
    # Scatter plot с линией тренда
    st.subheader("Диаграмма рассеяния")
    _render_scatter_plot_with_trend(df, stats_mean)
    
    # Box plot
    st.subheader("Распределение цен по категориям экологии")
    _render_box_plot(df)
    
    # Тепловая карта
    st.subheader("Матрица корреляций")
    _render_correlation_matrix(df)
    
    # Рейтинги
    st.subheader("Рейтинги районов")
    col1, col2 = st.columns(2)
    with col1:
        _render_top_eco_districts(df)
    with col2:
        _render_top_price_districts(df)


def _render_stats_card(stats: dict):
    """Отображает карточку со статистикой"""
    st.metric("Коэффициент корреляции (r)", f"{stats['r']:.3f}")
    st.caption(f"p-value: {stats['p_value']:.4f}")
    st.metric("Коэффициент детерминации (R²)", f"{stats['r_squared']:.3f}")
    st.caption(f"Интерпретация: {stats['interpretation']}")
    status = "значимо" if stats['is_significant'] else "не значимо"
    st.caption(f"Статистическая значимость: {status}")
    st.caption(f"Количество районов: {stats['n_samples']}")


def _render_scatter_plot_with_trend(df: pd.DataFrame, stats: dict):
    """Scatter plot с линией линейного тренда"""
    plot_df = df[['eco_index', 'price_per_sqm_mean', 'eco_category', 'area_mean', 'District']].dropna()
    
    fig = go.Figure()
    
    # Точки
    fig.add_trace(go.Scatter(
        x=plot_df['eco_index'],
        y=plot_df['price_per_sqm_mean'],
        mode='markers',
        marker=dict(
            size=plot_df['area_mean'] / 10,
            color=plot_df['eco_category'].map({
                'A (Отлично)': '#2ecc71',
                'B (Хорошо)': '#f1c40f', 
                'C (Удовлетворительно)': '#e67e22'
            }).fillna('#95a5a6'),
            showscale=False,
            opacity=0.7
        ),
        text=plot_df['District'],
        hovertemplate='<b>%{text}</b><br>Эко-индекс: %{x:.1f}<br>Цена: %{y:,.0f} ₽<extra></extra>',
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
        name=f'Тренд: y = {z[0]:.0f}x + {z[1]:.0f}<br>r = {stats["r"]:.3f}'
    ))
    
    fig.update_layout(
        xaxis_title='Экологический индекс (выше = лучше)',
        yaxis_title='Цена за кв.м (₽)',
        height=500,
        hovermode='closest'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _render_box_plot(df: pd.DataFrame):
    """Box plot по категориям экологии"""
    plot_df = df[df['eco_category'] != 'Нет данных'].copy()
    
    if len(plot_df) == 0:
        st.info("Недостаточно данных для box plot")
        return
    
    fig = px.box(
        plot_df,
        x='eco_category',
        y='price_per_sqm_mean',
        color='eco_category',
        title='Распределение цен по категориям экологии',
        labels={
            'eco_category': 'Категория экологии',
            'price_per_sqm_mean': 'Цена за кв.м (₽)'
        },
        color_discrete_map={
            'A (Отлично)': '#2ecc71',
            'B (Хорошо)': '#f1c40f',
            'C (Удовлетворительно)': '#e67e22'
        }
    )
    fig.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def _render_correlation_matrix(df: pd.DataFrame):
    """Тепловая карта корреляции"""
    available_cols = ['price_per_sqm_mean', 'eco_index', 'area_mean']
    
    for col in ['air_quality_score', 'noise_quality', 'ads_count']:
        if col in df.columns:
            available_cols.append(col)
    
    corr_matrix = df[available_cols].corr()
    
    rename_map = {
        'price_per_sqm_mean': 'Цена за м²',
        'eco_index': 'Эко-индекс',
        'area_mean': 'Площадь',
        'air_quality_score': 'Качество воздуха',
        'noise_quality': 'Качество шума',
        'ads_count': 'Кол-во объявлений'
    }
    corr_matrix = corr_matrix.rename(index=rename_map, columns=rename_map)
    
    fig = px.imshow(
        corr_matrix,
        text_auto='.2f',
        aspect='auto',
        title='Матрица корреляции показателей',
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)


def _render_top_eco_districts(df: pd.DataFrame):
    """Топ-5 самых экологичных районов"""
    st.markdown("**Топ-5 экологичных районов**")
    
    top_eco = df.nlargest(5, 'eco_index')[
        ['District', 'eco_index', 'eco_category', 'price_per_sqm_formatted']
    ]
    
    for i, (_, row) in enumerate(top_eco.iterrows(), 1):
        st.markdown(f"""
        **{i}. {row['District']}**
        - Эко-индекс: {row['eco_index']:.1f} ({row['eco_category']})
        - Цена: {row['price_per_sqm_formatted']}
        ---
        """)


def _render_top_price_districts(df: pd.DataFrame):
    """Топ-5 самых дорогих районов"""
    st.markdown("**Топ-5 дорогих районов**")
    
    top_price = df.nlargest(5, 'price_per_sqm_mean')[
        ['District', 'price_per_sqm_formatted', 'eco_index', 'eco_category']
    ]
    
    for i, (_, row) in enumerate(top_price.iterrows(), 1):
        st.markdown(f"""
        **{i}. {row['District']}**
        - Цена: {row['price_per_sqm_formatted']}
        - Эко-индекс: {row['eco_index']:.1f} ({row['eco_category']})
        ---
        """)