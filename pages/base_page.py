# pages/base_page.py
"""Базовый класс для всех Page Objects"""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class BasePage:
    """Базовый класс для всех page объектов"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def get_element(self, locator):
        """Получить элемент"""
        return self.driver.find_element(*locator)
    
    def get_elements(self, locator):
        """Получить список элементов"""
        return self.driver.find_elements(*locator)
    
    def wait_for_element(self, locator, timeout=10):
        """Ждать элемента"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
    
    def click_element(self, locator):
        """Кликнуть на элемент"""
        element = self.wait_for_element(locator)
        element.click()
    
    def enter_text(self, locator, text):
        """Ввести текст"""
        element = self.wait_for_element(locator)
        element.clear()
        element.send_keys(text)
    
    def get_text(self, locator):
        """Получить текст элемента"""
        element = self.get_element(locator)
        return element.text
    
    def wait_for_url_change(self, old_url, timeout=10):
        """Ждать изменения URL"""
        WebDriverWait(self.driver, timeout).until(
            EC.url_changes(old_url)
        )
    
    def is_element_visible(self, locator):
        """Проверить видимость элемента"""
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except:
            return False
