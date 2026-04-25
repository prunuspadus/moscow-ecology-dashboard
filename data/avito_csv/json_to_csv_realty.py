import json
import csv

# Загружаем JSON файл
with open('data/raw/avito_json/residential/all_districts_20260421_222320.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Открываем CSV файл для записи
with open('data/avito_csv/realty_data.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    
    # Записываем заголовки
    writer.writerow(['district', 'property_type', 'price_total', 'area', 'price_per_sqm'])
    
    # Проходим по всем элементам items
    for item in data['items']:
        writer.writerow([
            item['district'],
            item['property_type'],
            item['price_total'],
            item['area'],
            item['price_per_sqm']
        ])

print(f"Готово! Создан файл output.csv с {len(data['items'])} строками")