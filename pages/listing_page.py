# pages/listing_page.py
"""Page Object для списка объявлений на auto.ru - ФИНАЛЬНАЯ"""

from selenium.webdriver.common.by import By
from lxml import html
import time
from pages.base_page import BasePage


class ListingPage(BasePage):
    """Page Object для списка объявлений"""
    
    # ==================== LOCATORS ====================
    CAR_LINKS = (By.XPATH, '//a[contains(@href, "/cars/used/sale/")]')
    PAGINATION_ITEMS = (By.XPATH, '//div[@class="Pagination__item"]/text()')
    NEXT_PAGE_BUTTONS = (By.XPATH, '//a[contains(@href, "page=")]/@href')
    PAGINATION_CONTAINER = (By.XPATH, '//div[@class="Pagination"]')
    
    # ==================== INIT ====================
    def __init__(self, driver, base_url):
        """Инициализация ListingPage"""
        super().__init__(driver)
        self.base_url = base_url
    
    # ==================== PAGE ACTIONS ====================
    def open_page(self, page_num=1):
        """Открыть страницу со списком объявлений
        
        Args:
            page_num (int): Номер страницы
        """
        # ✅ ИСПРАВЛЕНО: Используем правильный формат URL
        # base_url уже содержит "?price_to=9999999"
        url = f"{self.base_url}&page={page_num}"
        
        print(f"   📍 Открываю: {url}")
        self.driver.get(url)
        
        # ✅ Ожидание загрузки
        time.sleep(1.5)
        
        # ✅ Ждём загрузки списка объявлений
        try:
            self.wait_for_element(self.CAR_LINKS, timeout=15)
        except Exception as e:
            print(f"   ⚠️  Предупреждение: {e}")
            time.sleep(1)
    
    def go_to_page(self, page_num):
        """Перейти на конкретную страницу"""
        self.open_page(page_num)
    
    def get_next_page_url(self):
        """Получить URL следующей страницы"""
        try:
            next_button = self.driver.find_element(By.XPATH, '//a[@rel="next"]')
            return next_button.get_attribute('href')
        except:
            return None
    
    # ==================== PAGE ELEMENTS ====================
    def get_car_links(self):
        """Получить ссылки на все объявления со страницы
        
        Returns:
            list: Список ссылок на объявления
        """
        car_links = []
        try:
            # ✅ Получаем HTML и парсим с lxml
            page_source = self.driver.page_source
            tree = html.fromstring(page_source)
            
            # ✅ Извлекаем ссылки на объявления
            links = tree.xpath('//a[contains(@href, "/cars/used/sale/")]/@href')
            
            if not links:
                print(f"   ⚠️  Ссылки не найдены на странице")
                return car_links
            
            for href in links:
                if href and '/cars/used/sale/' in href:
                    # ✅ Очищаем параметры URL
                    clean_url = href.split('?')[0] if '?' in href else href
                    if clean_url not in car_links:
                        car_links.append(clean_url)
        
        except Exception as e:
            print(f"   ⚠️  Ошибка при поиске ссылок: {e}")
        
        return car_links
    
    def get_total_pages(self):
        """Получить общее количество страниц
        
        Returns:
            int: Количество страниц
        """
        try:
            # ✅ Открываем первую страницу
            print(f"   📍 Загружаю первую страницу: {self.base_url}&page=1")
            self.driver.get(f"{self.base_url}&page=1")
            time.sleep(2)
            
            page_source = self.driver.page_source
            tree = html.fromstring(page_source)
            
            # ✅ Пробуем найти счётчик результатов
            counter_text = tree.xpath('//span[contains(text(), "найдено")]/text()')
            
            if counter_text:
                try:
                    count_str = counter_text[0]
                    # Пример: "найдено 58273"
                    total_count = int(''.join(filter(str.isdigit, count_str)))
                    # 50 объявлений на странице
                    total_pages = (total_count // 50) + (1 if total_count % 50 else 0)
                    print(f"   📊 Найдено {total_count} объявлений (~{total_pages} страниц)\n")
                    return total_pages
                except Exception as e:
                    print(f"   ⚠️  Не удалось спарсить счётчик: {e}")
            
            # ✅ Альтернативный метод - через пагинацию
            pagination_links = tree.xpath('//a[contains(@href, "page=")]/@href')
            
            if pagination_links:
                try:
                    page_numbers = []
                    for link in pagination_links:
                        try:
                            # Извлекаем номер страницы из URL
                            page_num = int(link.split('page=')[1].split('&')[0])
                            page_numbers.append(page_num)
                        except:
                            pass
                    
                    if page_numbers:
                        max_page = max(page_numbers)
                        print(f"   📊 Найдено ~{max_page} страниц\n")
                        return max_page
                except Exception as e:
                    print(f"   ⚠️  Ошибка при парсинге пагинации: {e}")
            
            print(f"   ⚠️  Не удалось определить количество страниц, использую 1200\n")
            return 1200
        
        except Exception as e:
            print(f"   ❌ Ошибка при определении количества страниц: {e}\n")
            return 1200
    
    def is_pagination_visible(self):
        """Проверить видимость пагинации"""
        return self.is_element_visible(self.PAGINATION_CONTAINER)
    
    def get_current_page_number(self):
        """Получить номер текущей страницы"""
        try:
            page_source = self.driver.page_source
            tree = html.fromstring(page_source)
            
            active_page = tree.xpath('//button[@class="Pagination__button Pagination__button_active"]/text()')
            if active_page:
                return int(active_page[0])
            
            return 1
        except:
            return 1
