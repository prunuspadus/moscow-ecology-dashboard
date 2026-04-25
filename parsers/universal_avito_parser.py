# universal_avito_parser.py
"""
Универсальный парсер Avito с парсингом данных из заголовка
"""

import os
import sys
import time
import json
import re
from datetime import datetime
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class UniversalAvitoParser:
    """Универсальный парсер с парсингом данных из заголовка"""
    
    def __init__(self, use_chrome=False):  # По умолчанию Safari пока
        self.use_chrome = use_chrome
        self.driver = None
        self.all_ads = []
        
    def find_chromedriver(self):
        """Найти chromedriver в системе"""
        possible_paths = [
            '/usr/local/bin/chromedriver',
            '/opt/homebrew/bin/chromedriver',
            '/usr/bin/chromedriver',
            '/usr/local/Caskroom/chromedriver/*/chromedriver-mac-x64/chromedriver',
            '/usr/local/Caskroom/chromedriver/*/chromedriver',
            '/opt/homebrew/Caskroom/chromedriver/*/chromedriver',
            os.path.expanduser('~/.wdm/drivers/chromedriver/*/chromedriver'),
            '/Applications/Google Chrome.app/Contents/MacOS/chromedriver',
            # Добавим путь для chromedriver из PATH
            subprocess.run(['which', 'chromedriver'], capture_output=True, text=True).stdout.strip()
        ]
        
        for path in possible_paths:
            if isinstance(path, str) and path:
                # Проверяем шаблоны с *
                if '*' in path:
                    import glob
                    matches = glob.glob(path)
                    if matches:
                        # Сортируем по дате, берем самый новый
                        matches.sort(key=os.path.getmtime, reverse=True)
                        # Проверяем что это исполняемый файл, а не текстовый
                        for match in matches:
                            if os.path.isfile(match) and os.access(match, os.X_OK):
                                if 'THIRD_PARTY_NOTICES' not in match:
                                    return match
                elif os.path.exists(path) and os.access(path, os.X_OK):
                    if 'THIRD_PARTY_NOTICES' not in path:
                        return path
        
        return None
    
    def setup_driver(self):
        """Настройка драйвера с автоопределением"""
        if self.use_chrome:
            self.setup_chrome_driver()
        else:
            self.setup_safari_driver()
    
    def setup_chrome_driver(self):
        """Настройка Chrome драйвера с webdriver-manager"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            # Пробуем использовать webdriver-manager для автоматической установки
            try:
                from selenium.webdriver.chrome.service import Service
                from webdriver_manager.chrome import ChromeDriverManager
                
                chrome_options = Options()
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                
                # Случайный User-Agent
                import random
                user_agents = [
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                ]
                chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
                
                # Используем webdriver-manager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
                logger.info("✅ Chrome драйвер инициализирован (webdriver-manager)")
                
            except ImportError:
                # Если webdriver-manager не установлен, пробуем обычный способ
                logger.warning("⚠️  webdriver-manager не установлен, пробую обычный способ...")
                self.setup_chrome_driver_manual()
                
        except Exception as e:
            logger.error(f"❌ Ошибка Chrome: {e}")
            logger.warning("🔄 Пробую Safari...")
            self.use_chrome = False
            self.setup_safari_driver()
    
    def setup_chrome_driver_manual(self):
        """Настройка Chrome драйвера вручную"""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        # Находим chromedriver
        chromedriver_path = self.find_chromedriver()
        
        if not chromedriver_path:
            logger.warning("⚠️  Chromedriver не найден, пробую Safari...")
            self.use_chrome = False
            self.setup_safari_driver()
            return
        
        logger.info(f"✅ Найден chromedriver: {chromedriver_path}")
        
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # Случайный User-Agent
        import random
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        # Создаем сервис с найденным путем
        service = Service(executable_path=chromedriver_path)
        
        # Создаем драйвер
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Скрываем WebDriver
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("✅ Chrome драйвер инициализирован (ручная установка)")
    
    def setup_safari_driver(self):
        """Настройка Safari драйвера"""
        try:
            from selenium import webdriver
            
            self.driver = webdriver.Safari()
            self.driver.set_window_size(1400, 900)
            time.sleep(2)
            
            logger.info("✅ Safari драйвер инициализирован")
            
        except Exception as e:
            logger.error(f"❌ Ошибка Safari: {e}")
            raise
    
    def parse_avito(self, url, pages=2):
        """Парсинг Avito"""
        logger.info(f"📊 Начинаю парсинг: {url}")
        
        ads_data = []
        
        for page in range(1, pages + 1):
            try:
                page_url = f"{url}?p={page}" if page > 1 else url
                logger.info(f"📄 Страница {page}/{pages}")
                
                self.driver.get(page_url)
                time.sleep(8)  # Даем время на загрузку
                
                # Проверяем капчу
                if self.check_captcha():
                    logger.warning("⚠️  Капча обнаружена. Ожидание 20 секунд...")
                    time.sleep(20)
                    # Прокручиваем для имитации поведения
                    self.driver.execute_script("window.scrollBy(0, 500)")
                    time.sleep(3)
                
                # Парсим страницу
                page_ads = self.parse_page()
                if page_ads:
                    ads_data.extend(page_ads)
                    logger.info(f"✅ Найдено {len(page_ads)} объявлений")
                
                if page < pages:
                    # Случайная пауза между страницами
                    import random
                    pause = random.uniform(3, 7)
                    time.sleep(pause)
                    
            except Exception as e:
                logger.error(f"❌ Ошибка на странице {page}: {e}")
                continue
        
        return ads_data
    
    def parse_page(self):
        """Парсинг страницы"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        ads = []
        
        try:
            # Ждем загрузки объявлений
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-marker="item"]'))
            )
            
            # Даем дополнительное время для полной загрузки
            time.sleep(3)
            
            ad_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-marker="item"]')
            
            logger.info(f"🔍 Найдено {len(ad_elements)} элементов объявлений")
            
            for i, element in enumerate(ad_elements):
                try:
                    ad_data = self.parse_element_from_title(element)
                    if ad_data and ad_data.get('price', 0) > 0:
                        ads.append(ad_data)
                        
                        if len(ads) % 10 == 0:
                            logger.info(f"  Обработано {len(ads)} объявлений")
                            
                except Exception as e:
                    logger.debug(f"Ошибка парсинга {i+1}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга страницы: {e}")
        
        return ads
    
    def parse_element_from_title(self, element):
        """Парсинг элемента объявления - упрощенная версия"""
        from selenium.webdriver.common.by import By
        
        try:
            # Получаем весь текст элемента
            text = element.text
            
            if len(text) < 20:
                return None
            
            # Парсим данные
            parsed_data = self.parse_all_from_text(text)
            
            if not parsed_data['price'] or parsed_data['price'] <= 0:
                return None
            
            # Формируем результат только с нужными полями
            result = {
                'property_type': parsed_data['property_type'],
                'price': parsed_data['price'],
                'price_per_sqm': parsed_data['price_per_sqm'],
                'area': parsed_data['area'],
                'floor_info': {
                    'floor': parsed_data['floor'],
                    'total_floors': parsed_data['total_floors']
                },
            }
            
            return result
            
        except Exception as e:
            logger.debug(f"Ошибка парсинга элемента: {e}")
            return None
    
    def parse_all_from_text(self, text):
        """Парсинг всех данных из текста объявления"""
        result = {
            'rooms': None,
            'property_type': 'квартира',
            'area': 0.0,
            'floor': 0,
            'total_floors': 0,
            'price': 0,
            'price_per_sqm': 0,
            'address': '',
            'metro': '',
            'district': '',
        }
        
        # 1. Комнаты
        if 'студия' in text.lower():
            result['rooms'] = 0
            result['property_type'] = 'студия'
        else:
            rooms_match = re.search(r'(\d+)-к\.', text)
            if rooms_match:
                result['rooms'] = int(rooms_match.group(1))
        
        # 2. Тип недвижимости
        if 'апартамент' in text.lower():
            result['property_type'] = 'апартаменты'
        elif 'квартира' in text.lower() and result['rooms'] is not None:
            result['property_type'] = 'квартира'
        
        # 3. Площадь
        area_match = re.search(r'(\d+[.,]?\d*)\s*м²', text)
        if area_match:
            result['area'] = float(area_match.group(1).replace(',', '.'))
        
        # 4. Этаж
        floor_match = re.search(r'(\d+)/(\d+)\s*эт', text)
        if floor_match:
            result['floor'] = int(floor_match.group(1))
            result['total_floors'] = int(floor_match.group(2))
        
        # 5. Цена (основная)
        price_match = re.search(r'(\d[\d\s]*)\s*₽(?!\s*за\s*м²)', text)
        if price_match:
            price_str = price_match.group(1).replace(' ', '').replace('\xa0', '')
            if price_str.isdigit():
                result['price'] = int(price_str)
        
        # 6. Цена за м²
        sqm_match = re.search(r'(\d[\d\s]*)\s*₽\s*за\s*м²', text)
        if sqm_match:
            sqm_str = sqm_match.group(1).replace(' ', '').replace('\xa0', '')
            if sqm_str.isdigit():
                result['price_per_sqm'] = int(sqm_str)
        elif result['price'] > 0 and result['area'] > 0:
            # Вычисляем если не указана явно
            price_per_sqm = int(result['price'] / result['area'])
            if 1000 <= price_per_sqm <= 1000000:
                result['price_per_sqm'] = price_per_sqm
        
        # 7. Адрес - ищем по паттернам
        address_patterns = [
            # "ул. Ленина, 15"
            r'([А-Яа-я]+\.[\s\-]*[А-Яа-я][А-Яа-я\s\-]+,\s*\d+[А-Яа-я]?(?:\s*к\.\s*\d+)?(?:\s*с\.\s*\d+)?)',
            # "проспект Мира, 25"
            r'([А-Яа-я][а-я]+\.[\s\-]*[А-Яа-я][А-Яа-я\s\-]+,\s*\d+[А-Яа-я]?)',
            # "Шмитовский пр., 8"
            r'([А-Яа-я][А-Яа-я\s\-]+[а-я]+\.[\s\-]*[А-Яа-я][А-Яа-я\s\-]*,\s*\d+)',
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, text)
            if match:
                result['address'] = match.group(1).strip()
                break
        
        # 8. Метро - ищем после адреса или "м."
        if result['address']:
            address_index = text.find(result['address'])
            if address_index != -1:
                after_address = text[address_index + len(result['address']):]
                # Ищем "Улица 1905 года, 11-15 мин"
                metro_match = re.search(r'([А-Яа-я][А-Яа-я\s\-]+),\s*\d+[\–\-]\d+\s*мин', after_address)
                if metro_match:
                    result['metro'] = metro_match.group(1).strip()
                else:
                    # Ищем "м. Авиамоторная"
                    metro_match = re.search(r'м\.\s*([А-Яа-я][А-Яа-я\s\-]+)', after_address)
                    if metro_match:
                        result['metro'] = metro_match.group(1).strip()
        
        # 9. Район - ищем в тексте
        moscow_districts = [
            'ЦАО', 'САО', 'СВАО', 'ВАО', 'ЮВАО', 'ЮАО', 'ЮЗАО', 'ЗАО', 'СЗАО',
            'Арбат', 'Хамовники', 'Тверской', 'Пресненский', 'Таганский',
            'Басманный', 'Замоскворечье', 'Красносельский', 'Мещанский',
            'Аэропорт', 'Беговой', 'Сокол', 'Дмитровский', 'Тимирязевский',
            'Бибирево', 'Отрадное', 'Медведково', 'Алтуфьевский', 'Лианозово',
            'Измайлово', 'Перово', 'Новогиреево', 'Гольяново', 'Сокольники',
            'Люблино', 'Марьино', 'Братеево', 'Зябликово', 'Чертаново',
            'Бутово', 'Ясенево', 'Коньково', 'Тёплый Стан', 'Кунцево',
            'Фили', 'Солнцево', 'Раменки', 'Митино', 'Строгино', 'Щукино',
        ]
        
        search_text = text.lower()
        for district in moscow_districts:
            if district.lower() in search_text:
                result['district'] = district
                break
        
        return result
    
    def clean_title(self, text):
        """Очистка заголовка"""
        # Удаляем "ЕщёX фото" в начале
        text = re.sub(r'^Ещё\d+\s*(фото|видео|фотографий)', '', text, flags=re.IGNORECASE)
        text = text.strip()
        
        # Если начинается с знаков препинания, удаляем
        text = re.sub(r'^[.,;:\s]+', '', text)
        
        # Берем только первую часть до длинного описания
        # Ищем точку перехода к описанию
        desc_patterns = [
            r'(Продается|Продаю|Предлагается|Сдается|Сдаю|Сдам)',
            r'[.!?]\s*[А-Я]',
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, text)
            if match:
                text = text[:match.start()].strip()
                break
        
        return text
    
    def extract_id_from_url(self, url, text):
        """Извлечение ID из URL или текста"""
        # Из URL
        if url:
            match = re.search(r'/(\d+)\?', url)
            if match:
                return match.group(1)
        
        # Из текста
        match = re.search(r'\b\d{9,10}\b', text)
        if match:
            return match.group(0)
        
        # Генерируем
        return f"id_{int(time.time())}_{hash(text) % 1000000}"
    
    def check_captcha(self):
        """Проверка на капчу"""
        try:
            page_source = self.driver.page_source.lower()
            return any(word in page_source for word in ['captcha', 'вы робот', 'robot', 'доступ ограничен'])
        except:
            return False
    
    def save_data(self, filename_prefix="universal_avito"):
        """Сохранение данных"""
        if not self.all_ads:
            logger.warning("⚠️  Нет данных для сохранения")
            return None
        
        # Путь для сохранения JSON файлов
        save_dir = os.path.join('data', 'raw', 'avito_json')
        os.makedirs(save_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = os.path.join(save_dir, f"{filename_prefix}_{timestamp}.json")
        
        try:
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(self.all_ads, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 JSON сохранен: {json_filename}")
            
            # CSV сохраняем в ту же папку
            csv_filename = os.path.join(save_dir, f"{filename_prefix}_{timestamp}.csv")
            self.save_to_csv(self.all_ads, csv_filename)
            
            return json_filename, csv_filename
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения: {e}")
            return None
    
    def save_to_csv(self, data, filename):
        """Сохранение в CSV"""
        if not data:
            logger.warning("⚠️  Нет данных для CSV")
            return
        
        try:
            import csv
            
            # Определяем все возможные поля
            all_fields = set()
            for item in data:
                all_fields.update(item.keys())
            
            fields = list(all_fields)
            
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"💾 CSV сохранен: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения CSV: {e}")
    
    def show_results(self):
        """Показать результаты"""
        if not self.all_ads:
            print("❌ Нет данных")
            return
        
        total = len(self.all_ads)
        print(f"\n📊 ИТОГО: {total:,} объявлений")
        
        # Статистика
        print("\n📈 СТАТИСТИКА:")
        print("-"*80)
        
        # Заполненность полей
        fields_to_check = ['price', 'price_per_sqm', 'area', 'address', 'district', 'metro']
        for field in fields_to_check:
            filled = sum(1 for ad in self.all_ads if ad.get(field))
            percentage = (filled / total) * 100
            print(f"  {field}: {filled}/{total} ({percentage:.1f}%)")
        
        # Типы недвижимости
        print("\n🏠 ТИПЫ НЕДВИЖИМОСТИ:")
        type_counts = {}
        for ad in self.all_ads:
            prop_type = ad.get('property_type', 'неизвестно')
            type_counts[prop_type] = type_counts.get(prop_type, 0) + 1
        
        for prop_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            print(f"  {prop_type}: {count} ({percentage:.1f}%)")
        
        # Примеры данных
        print("\n📋 ПРИМЕРЫ ДАННЫХ (первые 3):")
        print("="*80)
        
        for i, ad in enumerate(self.all_ads[:3], 1):
            print(f"\n#{i}:")
            print(f"  Заголовок: {ad['title'][:80]}...")
            print(f"  Тип: {ad['property_type']}")
            print(f"  Цена: {ad['price']:,} ₽")
            if ad.get('price_per_sqm'):
                print(f"  Цена за м²: {ad['price_per_sqm']:,} ₽")
            if ad.get('area'):
                print(f"  Площадь: {ad['area']} м²")
            if ad.get('rooms') is not None:
                rooms_text = 'студия' if ad['rooms'] == 0 else f"{ad['rooms']}к"
                print(f"  Комнат: {rooms_text}")
            if ad.get('address'):
                print(f"  Адрес: {ad['address']}")
            if ad.get('district'):
                print(f"  Район: {ad['district']}")
            if ad.get('metro'):
                print(f"  Метро: {ad['metro']}")
            if ad.get('floor_info'):
                floor_info = ad['floor_info']
                if floor_info.get('floor') and floor_info.get('total_floors'):
                    print(f"  Этаж: {floor_info['floor']}/{floor_info['total_floors']}")
    
    def run(self):
        """Запуск парсера"""
        print("="*70)
        print("🌐 УНИВЕРСАЛЬНЫЙ ПАРСЕР AVITO")
        print("="*70)
        print(f"Браузер: {'Chrome' if self.use_chrome else 'Safari'}")
        
        json_file = None
        csv_file = None
        
        try:
            self.setup_driver()
            
            # URL для парсинга
            url = "https://www.avito.ru/moskva/kvartiry/prodam-ASgBAgICAUSSA8YQ"
            
            # Парсим данные
            ads = self.parse_avito(url, pages=2)
            self.all_ads = ads
            
            # Сохраняем
            result = self.save_data()
            if result:
                json_file, csv_file = result
            
            # Показываем результаты
            self.show_results()
            
            if json_file and csv_file:
                print(f"\n💾 Файлы сохранены:")
                print(f"  JSON: {json_file}")
                print(f"  CSV: {csv_file}")
            else:
                print("\n❌ Не удалось сохранить данные")
            
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            if self.driver:
                self.driver.quit()
                print("✅ Браузер закрыт")

def main():
    """Основная функция"""
    # Пока используем Safari, пока не починим Chrome
    parser = UniversalAvitoParser(use_chrome=True)
    parser.run()

if __name__ == "__main__":
    main()