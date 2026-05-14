"""Модуль карты - визуализация районов Москвы"""

import streamlit as st
import folium
from streamlit_folium import folium_static
import json
import pandas as pd
from pathlib import Path

def render_map_tab(df: pd.DataFrame):
    """Отображает вкладку с интерактивной картой"""
    
    st.subheader("🗺️ Экологическая карта районов Москвы")
    
    geojson_data = _load_geojson()
    
    if geojson_data is None:
        st.warning("GeoJSON файл не найден")
        return
    
    district_data = _prepare_district_data(df)
    geojson_districts = [f['properties'].get('district', '') for f in geojson_data['features']]
    
    m = folium.Map(location=[55.76, 37.64], zoom_start=11, control_scale=True)
    
    _add_choropleth_layer(m, geojson_data, district_data, geojson_districts)
    _add_markers_layer(m, geojson_data, district_data, geojson_districts)
    _add_legend(m)
    
    matched_count = sum(1 for d in geojson_districts if _find_district_data(d, district_data, geojson_districts) is not None)
    
    st.success(f"✅ На карту добавлено {matched_count} районов с информацией")
    folium_static(m, width=1100, height=750)
    
    # Увеличенная подпись под картой
    st.markdown("<p style='font-size: 16px; color: #666;'>💡 Нажмите на маркер для детальной информации | Используйте +/- для масштабирования</p>", unsafe_allow_html=True)


def _load_geojson():
    paths = [
        Path('data/raw/moscow_districts.geojson'),
        Path('data/moscow_districts.geojson'),
    ]
    for path in paths:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    return None


def _prepare_district_data(df: pd.DataFrame):
    district_data = {}
    for _, row in df.iterrows():
        district_name = row['District']
        district_data[district_name] = {
            'price_formatted': row.get('price_per_sqm_formatted', 'Нет данных'),
            'price_mean': row.get('price_per_sqm_mean', 0),
            'eco_index': row.get('eco_index', 0),
            'eco_category': row.get('eco_category', 'Нет данных'),
            'air_quality': row.get('air_quality_category', 'Нет данных'),
            'noise_level': row.get('noise_level', 'Нет данных'),
            'area_mean': row.get('area_mean', 0)
        }
    return district_data


def _normalize_name(name: str) -> str:
    if not name:
        return name
    name = name.strip()
    name = name.replace(' район', '').replace('район', '')
    return ' '.join(name.split())


def _find_district_data(geo_name, district_data, geojson_districts):
    normalized = _normalize_name(geo_name)
    
    if normalized in district_data:
        return district_data[normalized]
    if geo_name in district_data:
        return district_data[geo_name]
    if geo_name.replace('район ', '') in district_data:
        return district_data[geo_name.replace('район ', '')]
    
    return None


def _get_color(eco_index):
    if eco_index is None or pd.isna(eco_index):
        return '#95a5a6'
    elif eco_index >= 80:
        return '#2ecc71'
    elif eco_index >= 60:
        return '#f1c40f'
    elif eco_index >= 40:
        return '#e67e22'
    else:
        return '#e74c3c'


def _add_choropleth_layer(m, geojson_data, district_data, geojson_districts):
    def style_function(feature):
        geo_name = feature['properties'].get('district', '')
        data = _find_district_data(geo_name, district_data, geojson_districts)
        eco_index = data['eco_index'] if data else 0
        return {
            'fillColor': _get_color(eco_index),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.5,
        }
    
    folium.GeoJson(
        geojson_data,
        name='Районы Москвы',
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['district'],
            aliases=['Район:'],
            localize=True
        )
    ).add_to(m)


def _add_markers_layer(m, geojson_data, district_data, geojson_districts):
    """Добавление маркеров с информацией (только цена и экология)"""
    for feature in geojson_data['features']:
        geo_name = feature['properties'].get('district', '')
        data = _find_district_data(geo_name, district_data, geojson_districts)
        
        if data is None:
            continue
        
        coords = _get_polygon_center(feature['geometry'])
        if coords is None:
            continue
        
        # Упрощённый попап: только цена и эко-индекс
        popup_html = f"""
        <div style="min-width: 250px; font-family: Arial, sans-serif;">
            <h4 style="font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #2c3e50;">🏘️ {geo_name}</h4>
            <hr style="margin: 8px 0;">
            <p style="font-size: 16px; margin: 6px 0;"><b>💰 Цена:</b> {data['price_formatted']}</p>
            <p style="font-size: 16px; margin: 6px 0;"><b>🌿 Эко-индекс:</b> {data['eco_index']:.1f} ({data['eco_category']})</p>
        </div>
        """
        
        folium.Marker(
            location=[coords[1], coords[0]],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{geo_name} | Эко: {data['eco_index']:.0f} | Цена: {data['price_formatted']}",
            icon=folium.Icon(color='blue', icon='info-sign', prefix='glyphicon')
        ).add_to(m)

def _get_polygon_center(geometry):
    try:
        if geometry['type'] == 'Polygon':
            coords = geometry['coordinates'][0]
        elif geometry['type'] == 'MultiPolygon':
            coords = geometry['coordinates'][0][0]
        else:
            return None
        
        lats = [c[1] for c in coords]
        lons = [c[0] for c in coords]
        return [sum(lons)/len(lons), sum(lats)/len(lats)]
    except:
        return None


def _add_legend(m):
    """Добавление легенды с увеличенным шрифтом"""
    legend_html = '''
    <div style="position: fixed; bottom: 50px; right: 50px; background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); z-index: 1000; font-family: Arial, sans-serif; min-width: 200px;">
        <b style="font-size: 16px;">🌿 Экологический индекс</b><br><br>
        <span style="background:#2ecc71; width:18px;height:18px;display:inline-block;border-radius:3px;"></span> <span style="font-size: 15px;">80-100 Отлично</span><br>
        <span style="background:#f1c40f; width:18px;height:18px;display:inline-block;border-radius:3px;"></span> <span style="font-size: 15px;">60-80 Хорошо</span><br>
        <span style="background:#e67e22; width:18px;height:18px;display:inline-block;border-radius:3px;"></span> <span style="font-size: 15px;">40-60 Удовлетворительно</span><br>
        <span style="background:#e74c3c; width:18px;height:18px;display:inline-block;border-radius:3px;"></span> <span style="font-size: 15px;">0-40 Плохо</span><br>
        <hr style="margin: 10px 0;">
        <span style="background:#4285F4; width:18px;height:18px;display:inline-block;border-radius:50%;"></span> <span style="font-size: 15px;">📍 Маркеры с инфо</span>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))