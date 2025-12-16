# pages/car_detail_page.py
"""Page Object для деталей объявления на auto.ru - ОПТИМИЗИРОВАННАЯ"""

import requests
from lxml import html
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import REQUEST_TIMEOUT, CONNECTION_POOL_CONNECTIONS, CONNECTION_POOL_MAXSIZE, RETRIES


class CarDetailPage:
    """Page Object для деталей объявления (использует requests)"""
    
    # ==================== КЛАСС-ПЕРЕМЕННЫЕ ====================
    _session = None  # ✅ Переиспользуемая сессия
    
    # ==================== LOCATORS (XPath) - ИСПРАВЛЕННЫЕ ====================
    TITLE = '//h1[@class="CardHead__title"]/text()'
    YEAR = '(//a[@class="Link Link_color_black"]/text())[2]'
    MILEAGE = '(//div[@class="CardInfoSummarySimpleRow__content-IIKcj"]/text())[1]'
    OWNERS = '(//div[@class="CardInfoSummarySimpleRow__content-IIKcj"]/text())[2]'
    # ✅ ИСПРАВЛЕНО: Состояние может быть в разных позициях
    CONDITION = '//span[contains(text(), "состояни") or contains(text(), "Состояни")]/following-sibling::*/text() | //div[contains(@class, "CardInfoSummarySimpleRow")]/following-sibling::div//div[contains(text(), "Исправн") or contains(text(), "Деформ") or contains(text(), "Битые") or contains(text(), "Перекр")]/text()'
    TRANSMISSION = '(//div[@class="CardInfoSummaryComplexRow__cellValue-Hka8p"]/text())[2]'
    ENGINE = '(//div[@class="CardInfoSummaryComplexRow__cellValue-Hka8p"]/text())[1]'
    # ✅ ИСПРАВЛЕНО: Дата объявления - более надёжный селектор
    DATE_POSTED = '//div[contains(@class, "CardHead__creationDate")]/text()'
    # ✅ ИСПРАВЛЕНО: Количество просмотров - правильный селектор
    VIEWS = '//div[contains(@class, "CardHead__views")]/text()'
    PRICE = '//span[@class="OfferPriceCaption__price"]/text()'
    
    # ==================== INIT ====================
    def __init__(self, car_url):
        """Инициализация CarDetailPage
        
        Args:
            car_url (str): URL объявления
        """
        self.car_url = car_url
        self.tree = None
        self._load_page()
    
    # ==================== SESSION MANAGEMENT ====================
    @classmethod
    def get_session(cls):
        """Получить или создать сессию requests с переиспользованием соединений
        
        Returns:
            requests.Session: Оптимизированная сессия
        """
        if cls._session is None:
            cls._session = requests.Session()
            
            retry_strategy = Retry(
                total=RETRIES,
                backoff_factor=0.1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET"]
            )
            
            adapter = HTTPAdapter(
                max_retries=retry_strategy,
                pool_connections=CONNECTION_POOL_CONNECTIONS,
                pool_maxsize=CONNECTION_POOL_MAXSIZE
            )
            
            cls._session.mount('http://', adapter)
            cls._session.mount('https://', adapter)
        
        return cls._session
    
    # ==================== PAGE LOADING ====================
    def _load_page(self):
        """Загрузить страницу объявления"""
        try:
            session = self.get_session()
            response = session.get(
                self.car_url, 
                timeout=REQUEST_TIMEOUT, 
                verify=False,
                headers={'Connection': 'keep-alive'}
            )
            response.encoding = 'utf-8'
            self.tree = html.fromstring(response.content)
        except:
            pass
    
    def _get_text(self, xpath, index=0):
        """Получить текст по XPath (оптимизировано)
        
        Args:
            xpath (str): XPath выражение
            index (int): Индекс элемента в списке результатов
            
        Returns:
            str: Текст или "N/A"
        """
        if self.tree is None:
            return "N/A"
        
        try:
            result = self.tree.xpath(xpath)
            if result and len(result) > index:
                text = str(result[index]).strip() if hasattr(result[index], 'strip') else str(result[index]).strip()
                return text or "N/A"
        except:
            pass
        return "N/A"
    
    # ==================== IMPROVED GETTERS ====================
    def get_title(self):
        """Получить название марки"""
        return self._get_text(self.TITLE)
    
    def get_year(self):
        """Получить год выпуска"""
        return self._get_text(self.YEAR)
    
    def get_mileage(self):
        """Получить пробег"""
        return self._get_text(self.MILEAGE)
    
    def get_owners(self):
        """Получить количество владельцев"""
        return self._get_text(self.OWNERS)
    
    def get_condition(self):
        """Получить состояние (ИСПРАВЛЕНО)"""
        # ✅ Улучшенная логика парсинга состояния
        try:
            if self.tree is None:
                return "N/A"
            
            # Пробуем разные варианты XPath
            conditions = [
                '//span[contains(text(), "Исправн") or contains(text(), "Деформ") or contains(text(), "Битые") or contains(text(), "Перекр")]/text()',
                '//div[contains(@class, "CardInfoSummarySimpleRow")]//text()[contains(., "Исправн") or contains(., "Деформ") or contains(., "Битые") or contains(., "Перекр")]',
                '(//div[@class="CardInfoSummarySimpleRow__content-IIKcj"]/text())[3]',
                '(//div[@class="CardInfoSummarySimpleRow__content-IIKcj"]/text())[4]',
            ]
            
            for xpath in conditions:
                result = self.tree.xpath(xpath)
                if result:
                    text = str(result[0]).strip()
                    if text and text != "N/A":
                        return text
            
            return "N/A"
        except:
            return "N/A"
    
    def get_transmission(self):
        """Получить тип коробки"""
        return self._get_text(self.TRANSMISSION)
    
    def get_engine(self):
        """Получить тип двигателя"""
        return self._get_text(self.ENGINE)
    
    def get_date_posted(self):
        """Получить дату объявления (ИСПРАВЛЕНО)"""
        # ✅ Улучшенная логика парсинга даты
        try:
            if self.tree is None:
                return "N/A"
            
            date_patterns = [
                '//div[contains(@class, "CardHead__creationDate")]/text()',
                '//div[@class="CardHead__infoItem CardHead__creationDate"]/text()',
                '//span[contains(text(), "Объавлено")]/following-sibling::text()',
                '(//div[@class="CardHead__info"]/div/text())[1]',
            ]
            
            for xpath in date_patterns:
                result = self.tree.xpath(xpath)
                if result:
                    text = str(result[0]).strip()
                    if text and text != "N/A" and len(text) > 3:
                        return text
            
            return "N/A"
        except:
            return "N/A"
    
    def get_views(self):
        """Получить количество просмотров (ИСПРАВЛЕНО)"""
        # ✅ Улучшенная логика парсинга просмотров
        try:
            if self.tree is None:
                return "N/A"
            
            view_patterns = [
                '//div[contains(@class, "CardHead__views")]/text()',
                '//div[@class="CardHead__infoItem CardHead__views"]/text()',
                '//span[contains(text(), "Просмотр")]/preceding-sibling::text()',
                '//div[contains(text(), "просмотр")]/preceding-sibling::text()',
                '(//div[@class="CardHead__info"]/div/text())[2]',
            ]
            
            for xpath in view_patterns:
                result = self.tree.xpath(xpath)
                if result:
                    # ✅ Ищем числа в тексте
                    text = str(result[0]).strip()
                    numbers = ''.join(filter(str.isdigit, text))
                    if numbers:
                        return numbers
            
            return "N/A"
        except:
            return "N/A"
    
    def get_price(self):
        """Получить цену
        
        Returns:
            int: Цена в рублях или 0
        """
        try:
            price_text = self._get_text(self.PRICE)
            if price_text != "N/A":
                return int(''.join(filter(str.isdigit, price_text)))
        except:
            pass
        return 0
    
    # ==================== DATA EXPORT ====================
    def get_car_data(self):
        """Получить все данные объявления (оптимизировано)
        
        Returns:
            dict: Словарь со всеми данными объявления
        """
        return {
            'Марка': self.get_title(),
            'Год выпуска': self.get_year(),
            'Пробег': self.get_mileage(),
            'Владельцы': self.get_owners(),
            'Состояние': self.get_condition(),
            'Коробка': self.get_transmission(),
            'Двигатель': self.get_engine(),
            'Дата объявления': self.get_date_posted(),
            'Количество просмотров': self.get_views(),
            'Цена': self.get_price(),
            'URL': self.car_url
        }
    
    @classmethod
    def close_session(cls):
        """Закрыть глобальную сессию"""
        if cls._session:
            cls._session.close()
            cls._session = None
