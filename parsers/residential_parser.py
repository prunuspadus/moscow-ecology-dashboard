#run_districts.py
"""
Упрощенный парсер Avito - только район, тип, цена, площадь
С приоритетным списком районов для экологических данных
"""

import sys
import time
import json
import os
from datetime import datetime

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.universal_avito_parser import UniversalAvitoParser

# Путь для сохранения данных
DATA_DIR = os.path.join('data', 'raw', 'avito_json', 'residential')

# Убеждаемся что директория существует
os.makedirs(DATA_DIR, exist_ok=True)

# Приоритетные районы (из экологических данных)
PRIORITY_DISTRICTS = [
    {"id": 616, "name": "Академический", "eco_name": "Академический район"},
    {"id": 622, "name": "Басманный", "eco_name": "Басманный район"},
    {"id": 641, "name": "Даниловский", "eco_name": "Даниловский район"},
    {"id": 642, "name": "Дмитровский", "eco_name": "Дмитровский район"},
    {"id": 643, "name": "Донской", "eco_name": "Донской район"},
    {"id": 673, "name": "Мещанский", "eco_name": "Мещанский район"},
    {"id": 675, "name": "Можайский", "eco_name": "Можайский район"},
    {"id": 689, "name": "Останкинский", "eco_name": "Останкинский район"},
    {"id": 696, "name": "Пресненский", "eco_name": "Пресненский район"},
    {"id": 700, "name": "Рязанский", "eco_name": "Рязанский район"},
    {"id": 702, "name": "Савёловский", "eco_name": "Савёловский район"},
    {"id": 717, "name": "Тверской", "eco_name": "Тверской район"},
    {"id": 620, "name": "Аэропорт", "eco_name": "район Аэропорт"},
    {"id": 627, "name": "Бирюлёво Западное", "eco_name": "район Бирюлёво Западное"},
    {"id": 628, "name": "Богородское", "eco_name": "район Богородское"},
    {"id": 646, "name": "Западное Дегунино", "eco_name": "район Западное Дегунино"},
    {"id": 651, "name": "Капотня", "eco_name": "район Капотня"},
    {"id": 652, "name": "Коньково", "eco_name": "район Коньково"},
    {"id": 653, "name": "Коптево", "eco_name": "район Коптево"},
    {"id": 654, "name": "Косино-Ухтомский", "eco_name": "район Косино-Ухтомский"},
    {"id": 658, "name": "Крюково", "eco_name": "район Крюково"},
    {"id": 667, "name": "Люблино", "eco_name": "район Люблино"},
    {"id": 670, "name": "Марьино", "eco_name": "район Марьино"},
    {"id": 672, "name": "Метрогородок", "eco_name": "район Метрогородок"},
    {"id": 685, "name": "Новокосино", "eco_name": "район Новокосино"},
    {"id": 688, "name": "Орехово-Борисово Южное", "eco_name": "район Орехово-Борисово Южное"},
    {"id": 693, "name": "Печатники", "eco_name": "район Печатники"},
    {"id": 698, "name": "Раменки", "eco_name": "район Раменки"},
    {"id": 701, "name": "Савёлки", "eco_name": "район Савёлки"},
    {"id": 707, "name": "Северное Тушино", "eco_name": "район Северное Тушино"},
    {"id": 709, "name": "Силино", "eco_name": "район Силино"},
    {"id": 710, "name": "Сокол", "eco_name": "район Сокол"},
    {"id": 721, "name": "Тропарёво-Никулино", "eco_name": "район Тропарёво-Никулино"},
    {"id": 725, "name": "Хамовники", "eco_name": "район Хамовники"},
    {"id": 727, "name": "Хорошёво-Мнёвники", "eco_name": "район Хорошёво-Мнёвники"},
    {"id": 729, "name": "Царицыно", "eco_name": "район Царицыно"},
    {"id": 735, "name": "Южное Бутово", "eco_name": "район Южное Бутово"},
    {"id": 736, "name": "Южное Медведково", "eco_name": "район Южное Медведково"},
]

# Остальные районы (если нужны будут после приоритетных)
OTHER_DISTRICTS = [
    {"id": 617, "name": "Алексеевский"},
    {"id": 618, "name": "Алтуфьевский"},
    {"id": 619, "name": "Арбат"},
    {"id": 621, "name": "Бабушкинский"},
    {"id": 623, "name": "Беговой"},
    {"id": 624, "name": "Бескудниковский"},
    {"id": 625, "name": "Бибирево"},
    {"id": 626, "name": "Бирюлёво Восточное"},
    {"id": 629, "name": "Братеево"},
    {"id": 630, "name": "Бутырский"},
    {"id": 631, "name": "Вешняки"},
    {"id": 632, "name": "Внуково"},
    {"id": 633, "name": "Войковский"},
    {"id": 634, "name": "Восточное Дегунино"},
    {"id": 635, "name": "Восточное Измайлово"},
    {"id": 636, "name": "Восточный"},
    {"id": 637, "name": "Выхино-Жулебино"},
    {"id": 638, "name": "Гагаринский"},
    {"id": 639, "name": "Головинский"},
    {"id": 640, "name": "Гольяново"},
    {"id": 644, "name": "Дорогомилово"},
    {"id": 645, "name": "Замоскворечье"},
    {"id": 647, "name": "Зюзино"},
    {"id": 648, "name": "Зябликово"},
    {"id": 649, "name": "Ивановское"},
    {"id": 650, "name": "Измайлово"},
    {"id": 655, "name": "Котловка"},
    {"id": 656, "name": "Красносельский"},
    {"id": 657, "name": "Крылатское"},
    {"id": 659, "name": "Кузьминки"},
    {"id": 660, "name": "Кунцево"},
    {"id": 661, "name": "Куркино"},
    {"id": 662, "name": "Левобережный"},
    {"id": 663, "name": "Лефортово"},
    {"id": 664, "name": "Лианозово"},
    {"id": 665, "name": "Ломоносовский"},
    {"id": 666, "name": "Лосиноостровский"},
    {"id": 668, "name": "Марфино"},
    {"id": 669, "name": "Марьина Роща"},
    {"id": 671, "name": "Матушкино"},
    {"id": 674, "name": "Митино"},
    {"id": 676, "name": "Молжаниновский"},
    {"id": 677, "name": "Москворечье-Сабурово"},
    {"id": 678, "name": "Нагатино-Садовники"},
    {"id": 679, "name": "Нагатинский Затон"},
    {"id": 680, "name": "Нагорный"},
    {"id": 681, "name": "Некрасовка"},
    {"id": 682, "name": "Нижегородский"},
    {"id": 683, "name": "Ново-Переделкино"},
    {"id": 684, "name": "Новогиреево"},
    {"id": 686, "name": "Обручевский"},
    {"id": 687, "name": "Орехово-Борисово Северное"},
    {"id": 690, "name": "Отрадное"},
    {"id": 691, "name": "Очаково-Матвеевское"},
    {"id": 692, "name": "Перово"},
    {"id": 694, "name": "Покровское-Стрешнево"},
    {"id": 695, "name": "Преображенское"},
    {"id": 697, "name": "Проспект Вернадского"},
    {"id": 699, "name": "Ростокино"},
    {"id": 703, "name": "Свиблово"},
    {"id": 704, "name": "Северное Бутово"},
    {"id": 705, "name": "Северное Измайлово"},
    {"id": 706, "name": "Северное Медведково"},
    {"id": 708, "name": "Северный"},
    {"id": 711, "name": "Соколиная Гора"},
    {"id": 712, "name": "Сокольники"},
    {"id": 713, "name": "Солнцево"},
    {"id": 714, "name": "Старое Крюково"},
    {"id": 715, "name": "Строгино"},
    {"id": 716, "name": "Таганский"},
    {"id": 718, "name": "Текстильщики"},
    {"id": 719, "name": "Тёплый Стан"},
    {"id": 720, "name": "Тимирязевский"},
    {"id": 722, "name": "Тушино"},
    {"id": 723, "name": "Филёвский Парк"},
    {"id": 724, "name": "Фили"},
    {"id": 726, "name": "Ховрино"},
    {"id": 728, "name": "Хорошёвский"},
    {"id": 730, "name": "Черёмушки"},
    {"id": 731, "name": "Чертаново Северное"},
    {"id": 732, "name": "Чертаново Центральное"},
    {"id": 733, "name": "Чертаново Южное"},
    {"id": 734, "name": "Щукино"},
    {"id": 737, "name": "Южное Тушино"},
    {"id": 738, "name": "Южнопортовый"},
    {"id": 739, "name": "Якиманка"},
    {"id": 740, "name": "Ярославский"},
    {"id": 741, "name": "Ясенево"},
]

# Объединяем: сначала приоритетные, потом остальные
ALL_DISTRICTS = PRIORITY_DISTRICTS + OTHER_DISTRICTS

def show_priority_districts():
    """Показывает приоритетные районы"""
    print("\n🏢 ПРИОРИТЕТНЫЕ РАЙОНЫ (есть в экологических данных):")
    print("-" * 50)
    for i, d in enumerate(PRIORITY_DISTRICTS, 1):
        filepath = os.path.join(DATA_DIR, f"{d['name']}_{d['id']}.json")
        status = "✅" if os.path.exists(filepath) else "⭕"
        print(f"  {status} {i:3d}. {d['name']} (ID: {d['id']})")
    print(f"\nВсего приоритетных районов: {len(PRIORITY_DISTRICTS)}")

def get_start_index():
    """Получает индекс района, с которого начинать парсинг"""
    show_priority_districts()
    
    print("\nСпособы указать начальный район:")
    print("  1. Ввести номер (например, 5 - начнет с 5-го приоритетного района)")
    print("  2. Ввести название (например, Коньково)")
    print("  3. Нажать Enter - начать с первого неспарсенного приоритетного района")
    print()
    
    # Проверяем уже спарсенные районы
    parsed_districts = []
    if os.path.exists(DATA_DIR):
        for f in os.listdir(DATA_DIR):
            if f.endswith('.json') and not f.startswith('all'):
                name = f.split('_')[0] if '_' in f else f.replace('.json', '')
                parsed_districts.append(name)
    
    if parsed_districts:
        print(f"Уже спарсены: {', '.join(parsed_districts[:10])}")
        if len(parsed_districts) > 10:
            print(f"  ... и еще {len(parsed_districts) - 10} районов")
        print()
    
    while True:
        user_input = input("Начальный район (номер/название/Enter): ").strip()
        
        if user_input == "":
            for i, d in enumerate(ALL_DISTRICTS):
                if d['name'] not in parsed_districts:
                    print(f"Начинаем с {d['name']} (индекс {i+1} в общем списке)")
                    return i
            return 0
        
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(ALL_DISTRICTS):
                return idx
            else:
                print(f"Номер должен быть от 1 до {len(ALL_DISTRICTS)}")
                continue
        
        for i, d in enumerate(ALL_DISTRICTS):
            if d['name'].lower() == user_input.lower():
                return i
        
        print(f"Район '{user_input}' не найден. Попробуйте снова.")

def map_to_target_format(ad, district_name):
    """Упрощенное преобразование"""
    return {
        'district': district_name,
        'property_type': ad.get('property_type', 'квартира'),
        'price_total': ad.get('price', 0),
        'area': ad.get('area', 0.0),
        'price_per_sqm': ad.get('price_per_sqm', 0),
    }

def load_existing_data():
    """Загружает уже собранные данные из всех файлов"""
    all_items = []
    if not os.path.exists(DATA_DIR):
        return all_items
    
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json') and not filename.startswith('all'):
            filepath = os.path.join(DATA_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    items = json.load(f)
                    if isinstance(items, list):
                        all_items.extend(items)
            except Exception as e:
                print(f"Ошибка загрузки {filename}: {e}")
    
    return all_items

def main():
    print("=" * 60)
    print("ПАРСЕР AVITO (ТОЛЬКО ПРОДАЖА)")
    print("=" * 60)
    print(f"Директория данных: {DATA_DIR}")
    print(f"Всего районов в списке: {len(ALL_DISTRICTS)}")
    print(f"Приоритетных районов: {len(PRIORITY_DISTRICTS)}")
    
    # Определяем начальный район
    start_idx = get_start_index()
    
    # Сколько парсить
    num = int(input("\nСколько районов спарсить (рекомендуется 3-5 за раз): ") or "3")
    
    # Желаемое количество объявлений на район
    target_per_district = int(input("Желаемое количество объявлений на район (80-100): ") or "80")
    
    # Загружаем существующие данные
    existing_items = load_existing_data()
    print(f"\nЗагружено существующих объявлений: {len(existing_items)}")
    
    # Определяем районы для парсинга
    districts_to_parse = ALL_DISTRICTS[start_idx:start_idx + num]
    
    print(f"\nБудут спарсены районы (с {start_idx + 1} по {start_idx + num}):")
    for i, d in enumerate(districts_to_parse, 1):
        priority_mark = "⭐" if d in PRIORITY_DISTRICTS else "  "
        print(f"  {priority_mark} {i}. {d['name']} (ID: {d['id']})")
    
    confirm = input("\nПродолжить? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Отменено")
        return
    
    all_items = existing_items.copy()
    new_items_count = 0
    
    for i, district in enumerate(districts_to_parse, 1):
        print(f"\n{'='*50}")
        print(f"Район {start_idx + i}/{start_idx + num}: {district['name']} (ID: {district['id']})")
        print("-" * 40)
        
        # Формируем URL
        base_url = "https://www.avito.ru/moskva/kvartiry/prodam-ASgBAgICAUSSA8YQ"
        context = "context=H4sIAAAAAAAA_wEtANL_YToxOntzOjg6ImZyb21QYWdlIjtzOjE2OiJzZWFyY2hGb3JtV2lkZ2V0Ijt9F_yIfi0AAAA"
        url = f"{base_url}?{context}&district={district['id']}&localPriority=0"
        
        parser = UniversalAvitoParser(use_chrome=False)
        
        try:
            parser.setup_driver()
            print(f"URL: {url}")
            
            pages_needed = max(2, (target_per_district + 50) // 50)
            pages_to_parse = min(pages_needed, 5)
            
            print(f"Цель: {target_per_district} объявлений, парсим {pages_to_parse} страниц")
            
            ads = parser.parse_avito(url, pages=pages_to_parse)
            
            if ads:
                formatted = [map_to_target_format(ad, district['name']) for ad in ads]
                all_items.extend(formatted)
                new_items_count += len(formatted)
                
                # Сохраняем файл района - используем DATA_DIR
                filename = os.path.join(DATA_DIR, f"{district['name']}_{district['id']}.json")
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(formatted, f, ensure_ascii=False, indent=2)
                
                print(f"✅ Спарсено: {len(formatted)} объявлений")
                print(f"💾 Сохранено: {filename}")
                
                if formatted:
                    first = formatted[0]
                    print(f"\nПример:")
                    print(f"  Цена: {first['price_total']:,} ₽")
                    print(f"  Площадь: {first['area']} м²")
                    print(f"  Цена/м²: {first['price_per_sqm']:,} ₽")
            else:
                print("⚠️ Объявления не найдены")
            
            parser.driver.quit()
            
            if i < len(districts_to_parse):
                delay = 20
                print(f"\n⏳ Ждем {delay} сек перед следующим районом...")
                time.sleep(delay)
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            try:
                parser.driver.quit()
            except:
                pass
    
    # Сохраняем все данные - используем DATA_DIR
    if all_items:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_file = os.path.join(DATA_DIR, f"all_districts_{timestamp}.json")
        
        district_summary = {}
        for item in all_items:
            d = item['district']
            if d not in district_summary:
                district_summary[d] = {'count': 0, 'prices': [], 'areas': []}
            district_summary[d]['count'] += 1
            district_summary[d]['prices'].append(item['price_total'])
            district_summary[d]['areas'].append(item['area'])
        
        summary = {
            'parsed_at': datetime.now().isoformat(),
            'total_districts': len(district_summary),
            'total_items': len(all_items),
            'district_stats': {
                d: {
                    'count': stats['count'],
                    'avg_price': sum(stats['prices'])/len(stats['prices']) if stats['prices'] else 0,
                    'avg_area': sum(stats['areas'])/len(stats['areas']) if stats['areas'] else 0,
                }
                for d, stats in district_summary.items()
            },
            'items': all_items
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print("ИТОГО ЗА СЕССИЮ")
        print("=" * 60)
        print(f"✅ Новых объявлений: {new_items_count}")
        print(f"✅ Всего объявлений: {len(all_items)}")
        print(f"✅ Всего районов: {len(district_summary)}")
        print(f"💾 Файл: {summary_file}")
        
        print("\n🏢 ПРОГРЕСС ПО ПРИОРИТЕТНЫМ РАЙОНАМ:")
        print("-" * 50)
        for d in PRIORITY_DISTRICTS:
            name = d['name']
            if name in district_summary:
                count = district_summary[name]['count']
                status = "✅" if count >= target_per_district else "🟡"
                print(f"  {status} {name}: {count} объявлений")
            else:
                print(f"  ❌ {name}: не спарсен")
        
        all_prices = [i['price_total'] for i in all_items if i['price_total'] > 0]
        all_areas = [i['area'] for i in all_items if i['area'] > 0]
        
        if all_prices:
            print(f"\n💰 Средняя цена: {sum(all_prices)/len(all_prices):,.0f} ₽")
            print(f"💰 Медианная цена: {sorted(all_prices)[len(all_prices)//2]:,.0f} ₽")
        if all_areas:
            print(f"📐 Средняя площадь: {sum(all_areas)/len(all_areas):.1f} м²")
        
    else:
        print("\n❌ Не удалось спарсить данные")

if __name__ == "__main__":
    main()