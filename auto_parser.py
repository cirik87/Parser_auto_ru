# auto_parser.py (ОПТИМИЗИРОВАННАЯ ВЕРСИЯ)
"""
Парсер автомобильных объявлений с сайта auto.ru - БЫСТРАЯ ВЕРСИЯ
Использует Page Object Pattern, Connection Pooling и асинхронность
"""

from selenium import webdriver
import pandas as pd
import time
import urllib3
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Импортируем Page Objects
from pages.listing_page import ListingPage
from pages.car_detail_page import CarDetailPage
from config import (
    MAX_PRICE, NUM_THREADS, MAX_PAGES, OUTPUT_FILENAME,
    BASE_URL_TEMPLATE, CHROMEDRIVER_PATH, CHROME_ARGS,
    PAGE_LOAD_DELAY, PAGINATION_DELAY
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AutoRuParser:
    """Быстрый парсер auto.ru с оптимизациями"""
    
    def __init__(self, max_price=MAX_PRICE, num_threads=NUM_THREADS):
        """Инициализация парсера
        
        Args:
            max_price (int): Максимальная цена для фильтрации
            num_threads (int): Количество параллельных потоков
        """
        self.base_url = f"{BASE_URL_TEMPLATE}{max_price}"
        self.max_price = max_price
        self.cars = []
        self.driver = None
        self.num_threads = num_threads
        self.lock = threading.Lock()
        self.stats = {'processed': 0, 'errors': 0}  # ✅ Статистика
    
    def setup_driver(self):
        """Инициализирует оптимизированный Selenium WebDriver"""
        options = webdriver.ChromeOptions()
        
        for arg in CHROME_ARGS:
            options.add_argument(arg)
        
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            if os.path.exists(CHROMEDRIVER_PATH):
                self.driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)
                print("✅ ChromeDriver загружен (оптимизировано)")
            else:
                self.driver = webdriver.Chrome(options=options)
                print("✅ ChromeDriver загружен из системы")
        except Exception as e:
            print(f"❌ Ошибка при загрузке ChromeDriver: {e}")
            raise
    
    def collect_all_links(self, max_pages=MAX_PAGES):
        """Собрать все ссылки на объявления (оптимизировано)
        
        Args:
            max_pages (int): Максимальное количество страниц
            
        Returns:
            list: Список ссылок на объявления
        """
        listing_page = ListingPage(self.driver, self.base_url)
        
        print(f"🔍 Определяю количество страниц...")
        total_pages = listing_page.get_total_pages()
        
        if max_pages:
            total_pages = min(total_pages, max_pages)
        
        all_links = []
        for page in range(1, total_pages + 1):
            print(f"📄 Страница {page}/{total_pages}...", end=' ')
            listing_page.open_page(page)
            
            links = listing_page.get_car_links()
            all_links.extend(links)
            print(f"✅ {len(links)} ссылок")
            
            if PAGINATION_DELAY > 0:
                time.sleep(PAGINATION_DELAY)
        
        return all_links
    
    def parse_car_thread(self, car_url):
        """Парсить объявление в отдельном потоке (оптимизировано)
        
        Args:
            car_url (str): URL объявления
        """
        try:
            detail_page = CarDetailPage(car_url)
            car_data = detail_page.get_car_data()
            
            if car_data['Цена'] == 0:
                return
            
            with self.lock:
                self.cars.append(car_data)
                self.stats['processed'] += 1
                
                # ✅ Прогресс каждые 20 объявлений
                if self.stats['processed'] % 20 == 0:
                    print(f"  ⚡ {self.stats['processed']} объявлений обработано")
        
        except Exception as e:
            with self.lock:
                self.stats['errors'] += 1
    
    def parse_all_pages(self, max_pages=MAX_PAGES):
        """Парсить все страницы с максимальным ускорением
        
        Args:
            max_pages (int): Максимальное количество страниц
        """
        self.setup_driver()
        
        try:
            # ✅ Собираем ссылки
            all_links = self.collect_all_links(max_pages)
            
            print(f"\n{'='*60}")
            print(f"📊 Всего собрано ссылок: {len(all_links)}")
            print(f"⚡ Запущено потоков: {self.num_threads}")
            print(f"{'='*60}\n")
            
            start_parsing = time.time()
            
            # ✅ Параллельная обработка с максимальной скоростью
            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                futures = [executor.submit(self.parse_car_thread, link) for link in all_links]
                
                for future in as_completed(futures):
                    try:
                        future.result()
                    except:
                        pass
            
            elapsed_parsing = time.time() - start_parsing
            print(f"\n⚡ Парсинг занял: {elapsed_parsing:.1f} сек")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Парсинг прерван")
        
        finally:
            self.driver.quit()
            CarDetailPage.close_session()  # ✅ Закрываем сессию
            print("🔴 Browser закрыт")
        
        return self.cars
    
    def save_to_excel(self, filename=OUTPUT_FILENAME):
        """Сохранить данные в Excel (оптимизировано)
        
        Args:
            filename (str): Имя выходного файла
        """
        if not self.cars:
            print("❌ Нет данных для сохранения")
            return
        
        start_save = time.time()
        print(f"\n⏳ Сохраняю {len(self.cars)} объявлений...")
        
        df = pd.DataFrame(self.cars)
        
        # ✅ Быстрая сортировка
        try:
            df['Дата объявления'] = pd.to_datetime(df['Дата объявления'], 
                                                   format='%d %B %Y', 
                                                   errors='coerce')
            df = df.sort_values('Дата объявления', ascending=False, na_position='last')
            df['Дата объявления'] = df['Дата объявления'].dt.strftime('%d.%m.%Y')
        except:
            pass
        
        df = df.drop('URL', axis=1)
        
        # ✅ Быстрый экспорт
        df.to_excel(filename, index=False, engine='openpyxl')
        
        elapsed_save = time.time() - start_save
        
        print(f"\n✅ Данные сохранены в {filename}")
        print(f"📊 Всего записей: {len(df)}")
        print(f"📈 Успешно: {len(df)} | Ошибок: {self.stats['errors']}")
        
        if len(df) > 0:
            print(f"💰 Средняя цена: {df['Цена'].mean():,.0f} руб")
            print(f"📉 Мин цена: {df['Цена'].min():,.0f} руб")
            print(f"📈 Макс цена: {df['Цена'].max():,.0f} руб")


# ==================== MAIN ====================

def main():
    """Главная функция"""
    total_start = time.time()
    
    parser = AutoRuParser(max_price=MAX_PRICE, num_threads=NUM_THREADS)
    
    print("\n" + "="*60)
    print("🚗 БЫСТРЫЙ ПАРСЕР AUTO.RU (Page Object Pattern)")
    print("="*60)
    print(f"💰 Фильтр цены: до {parser.max_price:,} руб")
    print(f"⚡ Параллельных потоков: {parser.num_threads}")
    print("="*60 + "\n")
    
    parser.parse_all_pages(max_pages=MAX_PAGES)
    parser.save_to_excel(OUTPUT_FILENAME)
    
    total_elapsed = time.time() - total_start
    
    print("\n" + "="*60)
    print(f"✅ ПАРСИНГ ЗАВЕРШЁН")
    print("="*60)
    print(f"⏱️  Общее время: {total_elapsed:.1f} сек")
    print(f"📊 Всего объявлений: {len(parser.cars)}")
    
    if total_elapsed > 0 and len(parser.cars) > 0:
        speed = len(parser.cars) / total_elapsed
        print(f"⚡ Скорость: ~{speed:.1f} объявл/сек")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
