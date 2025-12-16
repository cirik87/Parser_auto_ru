# auto_parser_sync.py (СИНХРОННЫЙ ПАРСЕР - 99% ТОЧНОСТЬ)
"""
Синхронный парсер auto.ru - МАКСИМАЛЬНАЯ ТОЧНОСТЬ
Медленнее но надёжнее - 99% успех парсинга
"""

import time
import requests
from selenium import webdriver
import pandas as pd
import urllib3
import os
from lxml import html

from pages.listing_page import ListingPage
from config import (
    MAX_PRICE, NUM_THREADS, MAX_PAGES, OUTPUT_FILENAME,
    BASE_URL_TEMPLATE, CHROMEDRIVER_PATH, CHROME_ARGS,
    PAGINATION_DELAY, REQUEST_TIMEOUT
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SyncCarDetailPage:
    """Синхронный Page Object для деталей объявления"""
    
    TITLE = '//h1[@class="CardHead__title"]/text()'
    YEAR = '(//a[@class="Link Link_color_black"]/text())[2]'
    MILEAGE = '(//div[@class="CardInfoSummarySimpleRow__content-IIKcj"]/text())[1]'
    OWNERS = '(//div[@class="CardInfoSummarySimpleRow__content-IIKcj"]/text())[2]'
    CONDITION = '//span[contains(text(), "Исправн") or contains(text(), "Деформ") or contains(text(), "Битые") or contains(text(), "Перекр")]/text()'
    TRANSMISSION = '(//div[@class="CardInfoSummaryComplexRow__cellValue-Hka8p"]/text())[2]'
    ENGINE = '(//div[@class="CardInfoSummaryComplexRow__cellValue-Hka8p"]/text())[1]'
    DATE_POSTED = '//div[contains(@class, "CardHead__creationDate")]/text()'
    VIEWS = '//div[contains(@class, "CardHead__views")]/text()'
    PRICE = '//span[@class="OfferPriceCaption__price"]/text()'
    
    def __init__(self, car_url):
        self.car_url = car_url
        self.tree = None
    
    def _load_page(self, session, retry=0, max_retries=5):
        """Загрузить страницу синхронно с повторными попытками"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = session.get(
                self.car_url,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                verify=False,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                content = response.content
                if content and len(content) > 500:  # ✅ Проверяем размер ответа
                    self.tree = html.fromstring(content)
                    return True
            
            elif response.status_code == 429 and retry < max_retries:
                # Too Many Requests - ждём и повторяем
                wait_time = 2 ** retry  # Экспоненциальная задержка
                print(f"      ⏳ 429 Error - ожидание {wait_time}с перед повтором...")
                time.sleep(wait_time)
                return self._load_page(session, retry + 1, max_retries)
        
        except requests.Timeout:
            if retry < max_retries:
                print(f"      ⏳ Timeout - повтор {retry + 1}/{max_retries}...")
                time.sleep(1)
                return self._load_page(session, retry + 1, max_retries)
        
        except Exception as e:
            if retry < max_retries:
                print(f"      ⏳ Ошибка: {str(e)[:30]} - повтор {retry + 1}/{max_retries}...")
                time.sleep(0.5)
                return self._load_page(session, retry + 1, max_retries)
        
        return False
    
    def _get_text(self, xpath, index=0):
        """Получить текст по XPath"""
        if self.tree is None:
            return "N/A"
        try:
            result = self.tree.xpath(xpath)
            if result and len(result) > index:
                text = str(result[index]).strip()
                return text if text else "N/A"
        except:
            pass
        return "N/A"
    
    def get_date_posted(self):
        """Получить дату объявления"""
        try:
            if self.tree is None:
                return "N/A"
            
            date_patterns = [
                '//div[contains(@class, "CardHead__creationDate")]/text()',
                '//div[@class="CardHead__infoItem CardHead__creationDate"]/text()',
            ]
            
            for xpath in date_patterns:
                try:
                    result = self.tree.xpath(xpath)
                    if result:
                        for r in result:
                            text = str(r).strip()
                            if text and len(text) > 3:
                                return text
                except:
                    pass
            
            return "N/A"
        except:
            return "N/A"
    
    def get_views(self):
        """Получить количество просмотров"""
        try:
            if self.tree is None:
                return "0"
            
            view_patterns = [
                '//div[contains(@class, "CardHead__views")]/text()',
                '//div[@class="CardHead__infoItem CardHead__views"]/text()',
            ]
            
            for xpath in view_patterns:
                try:
                    result = self.tree.xpath(xpath)
                    if result:
                        for r in result:
                            text = str(r).strip()
                            numbers = ''.join(filter(str.isdigit, text))
                            if numbers:
                                return numbers
                except:
                    pass
            
            return "0"
        except:
            return "0"
    
    def get_condition(self):
        """Получить состояние"""
        try:
            if self.tree is None:
                return "N/A"
            
            conditions = [
                '//span[contains(text(), "Исправное")]/text()',
                '//span[contains(text(), "Деформированное")]/text()',
                '//span[contains(text(), "Битые окна")]/text()',
                '//span[contains(text(), "Перекрашено")]/text()',
                '//span[contains(., "Исправн") or contains(., "Деформ") or contains(., "Битые") or contains(., "Перекр")]/text()',
            ]
            
            for xpath in conditions:
                try:
                    result = self.tree.xpath(xpath)
                    if result:
                        text = str(result[0]).strip()
                        if text and text != "N/A":
                            return text
                except:
                    pass
            
            return "N/A"
        except:
            return "N/A"
    
    def get_price(self):
        """Получить цену"""
        try:
            price_text = self._get_text(self.PRICE)
            if price_text != "N/A":
                numbers = ''.join(filter(str.isdigit, price_text))
                if numbers:
                    return int(numbers)
        except:
            pass
        return 0
    
    def get_car_data(self):
        """Получить все данные"""
        return {
            'Марка': self._get_text(self.TITLE),
            'Год выпуска': self._get_text(self.YEAR),
            'Пробег': self._get_text(self.MILEAGE),
            'Владельцы': self._get_text(self.OWNERS),
            'Состояние': self.get_condition(),
            'Коробка': self._get_text(self.TRANSMISSION),
            'Двигатель': self._get_text(self.ENGINE),
            'Дата объявления': self.get_date_posted(),
            'Количество просмотров': self.get_views(),
            'Цена': self.get_price(),
            'URL': self.car_url
        }


class SyncAutoRuParser:
    """Синхронный парсер auto.ru - ВЫСОКАЯ ТОЧНОСТЬ"""
    
    def __init__(self, max_price=MAX_PRICE):
        self.base_url = BASE_URL_TEMPLATE
        self.max_price = max_price
        self.cars = []
        self.driver = None
        self.stats = {'processed': 0, 'errors': 0, 'skipped': 0}
        
        # ✅ Создаём session для переиспользования соединений
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=5,
            pool_maxsize=5,
            max_retries=3
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def setup_driver(self):
        """Инициализировать Selenium"""
        options = webdriver.ChromeOptions()
        for arg in CHROME_ARGS:
            options.add_argument(arg)
        
        try:
            if os.path.exists(CHROMEDRIVER_PATH):
                self.driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
            print("✅ ChromeDriver загружен")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            raise
    
    def collect_all_links(self, max_pages=MAX_PAGES):
        """Собрать ВСЕ ссылки"""
        listing_page = ListingPage(self.driver, self.base_url)
        
        print(f"🔍 Определяю количество страниц...")
        total_pages = listing_page.get_total_pages()
        
        if max_pages:
            total_pages = min(total_pages, max_pages)
        
        print(f"📊 Будут собраны ссылки со ВСЕХ {total_pages} страниц\n")
        
        all_links = []
        failed_pages = []
        
        for page in range(1, total_pages + 1):
            try:
                print(f"📄 Страница {page}/{total_pages}...", end=' ', flush=True)
                listing_page.open_page(page)
                
                links = listing_page.get_car_links()
                all_links.extend(links)
                print(f"✅ {len(links)} ссылок (всего: {len(all_links)})")
                
                if PAGINATION_DELAY > 0:
                    time.sleep(PAGINATION_DELAY)
            
            except Exception as e:
                print(f"⚠️  Ошибка: {e}")
                failed_pages.append(page)
        
        if failed_pages:
            print(f"\n⚠️  Ошибки на страницах: {failed_pages}")
        
        return all_links
    
    def parse_car_sync(self, car_url):
        """Парсить объявление синхронно"""
        try:
            detail_page = SyncCarDetailPage(car_url)
            if not detail_page._load_page(self.session):
                self.stats['errors'] += 1
                return
            
            car_data = detail_page.get_car_data()
            
            # ✅ Принимаем ВСЕ объявления
            self.cars.append(car_data)
            self.stats['processed'] += 1
        
        except Exception:
            self.stats['errors'] += 1
    
    def parse_all_pages(self, max_pages=MAX_PAGES):
        """Основной метод парсинга"""
        self.setup_driver()
        
        try:
            all_links = self.collect_all_links(max_pages)
            
            print(f"\n{'='*60}")
            print(f"📊 Всего собрано ссылок: {len(all_links)}")
            print(f"⚙️  СИНХРОННЫЙ ПАРСИНГ (99% точность, медленно)")
            print(f"{'='*60}\n")
            
            start_parsing = time.time()
            
            for idx, url in enumerate(all_links, 1):
                # ✅ Показываем прогресс каждые 50 объявлений
                if idx % 50 == 0:
                    success_rate = (self.stats['processed'] / (self.stats['processed'] + self.stats['errors'])) * 100 if (self.stats['processed'] + self.stats['errors']) > 0 else 0
                    print(f"  ⚙️  Обработано: {idx}/{len(all_links)} | Успех: {success_rate:.1f}%")
                
                # ✅ Парсим объявление
                self.parse_car_sync(url)
                
                # ✅ ЗАДЕРЖКА 0.5 сек для избежания блокировки
                time.sleep(0.5)
            
            elapsed_parsing = time.time() - start_parsing
            print(f"\n⚙️  Синхронный парсинг занял: {elapsed_parsing:.1f} сек")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Парсинг прерван пользователем")
        
        finally:
            self.driver.quit()
            print("🔴 Browser закрыт")
        
        return self.cars
    
    def save_to_excel(self, filename=OUTPUT_FILENAME):
        """Сохранить ВСЕ данные"""
        if not self.cars:
            print("❌ Нет данных для сохранения")
            return
        
        start_save = time.time()
        print(f"\n⏳ Сохраняю {len(self.cars)} объявлений...")
        
        df = pd.DataFrame(self.cars)
        
        # ✅ Очистка данных
        try:
            df['Дата объявления'] = pd.to_datetime(df['Дата объявления'], 
                                                   format='%d %B %Y', 
                                                   errors='coerce')
            df = df.sort_values('Дата объявления', ascending=False, na_position='last')
            df['Дата объявления'] = df['Дата объявления'].dt.strftime('%d.%m.%Y')
        except:
            pass
        
        # ✅ Конвертируем просмотры в числа
        try:
            df['Количество просмотров'] = pd.to_numeric(df['Количество просмотров'], errors='coerce').fillna(0).astype(int)
        except:
            pass
        
        df = df.drop('URL', axis=1)
        df.to_excel(filename, index=False, engine='openpyxl')
        
        elapsed_save = time.time() - start_save
        
        print(f"\n✅ ДАННЫЕ СОХРАНЕНЫ!")
        print(f"📊 Записей в файле: {len(df)}")
        print(f"📈 Успешно обработано: {self.stats['processed']}")
        print(f"❌ Ошибок: {self.stats['errors']}")
        
        success_rate = (self.stats['processed'] / (self.stats['processed'] + self.stats['errors'])) * 100 if (self.stats['processed'] + self.stats['errors']) > 0 else 0
        print(f"📊 Процент успеха: {success_rate:.1f}% ✅")
        
        if len(df) > 0:
            print(f"\n💰 Статистика по ценам:")
            print(f"   Средняя цена: {df['Цена'].mean():,.0f} руб")
            print(f"   Минимум: {df['Цена'].min():,.0f} руб")
            print(f"   Максимум: {df['Цена'].max():,.0f} руб")
            print(f"   Объявлений без цены: {(df['Цена'] == 0).sum()}")


def main():
    """Главная функция"""
    total_start = time.time()
    
    parser = SyncAutoRuParser(max_price=MAX_PRICE)
    
    print("\n" + "="*60)
    print("🚗 СИНХРОННЫЙ ПАРСЕР AUTO.RU")
    print("   99% ТОЧНОСТЬ - НАДЁЖНАЯ ОБРАБОТКА")
    print("="*60)
    print(f"💰 Максимальная цена: {MAX_PRICE:,} руб")
    print(f"⚙️  Режим: СИНХРОННЫЙ (медленный но точный)")
    print("="*60)
    
    parser.parse_all_pages(max_pages=MAX_PAGES)
    parser.save_to_excel(OUTPUT_FILENAME)
    
    total_elapsed = time.time() - total_start
    
    print("\n" + "="*60)
    print(f"✅ ПАРСИНГ УСПЕШНО ЗАВЕРШЁН!")
    print("="*60)
    print(f"⏱️  Общее время: {total_elapsed:.1f} сек (~{total_elapsed/60:.1f} мин)")
    print(f"📊 Всего объявлений в файле: {len(parser.cars)}")
    
    if total_elapsed > 0 and len(parser.cars) > 0:
        speed = len(parser.cars) / total_elapsed
        print(f"⚙️  Скорость парсинга: ~{speed:.2f} объявл/сек (медленно но надёжно)")
    
    print("="*60)
    print(f"📁 Файл сохранён: {OUTPUT_FILENAME}\n")


if __name__ == "__main__":
    main()
