# README.md
# Auto.ru Parser - Page Object Pattern

Профессиональный парсер объявлений с auto.ru с использованием **Page Object Pattern** и параллельной обработкой.

## 📁 Структура проекта

```
📂 auto-ru-parser/
├── 📄 auto_parser.py           # Главный файл парсера
├── 📄 config.py                # Конфигурация приложения
├── 📄 requirements.txt          # Зависимости проекта
├── 📄 README.md                 # Документация
├── 📂 pages/                    # Page Objects
│   ├── 📄 __init__.py
│   ├── 📄 base_page.py          # Базовый класс для всех page objects
│   ├── 📄 listing_page.py       # Page Object для списка объявлений
│   └── 📄 car_detail_page.py    # Page Object для деталей объявления
└── 📂 tests/                    # Unit тесты (опционально)
    └── 📄 test_pages.py
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Запуск парсера

```bash
python auto_parser.py
```

### 3. Результат

Данные сохранятся в файл `auto_ru_cars.xlsx`

## ⚙️ Конфигурация

Все параметры находятся в файле `config.py`:

```python
MAX_PRICE = 1000000           # Максимальная цена в рублях
NUM_THREADS = 6               # Количество потоков
MAX_PAGES = None              # Количество страниц (None = все)
OUTPUT_FILENAME = 'auto_ru_cars.xlsx'  # Имя выходного файла
```

## 📋 Page Objects

### BasePage
Базовый класс для всех page objects. Содержит общие методы для работы с Selenium.

```python
from pages.base_page import BasePage

class MyPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
```

**Основные методы:**
- `get_element(locator)` - Получить элемент
- `get_elements(locator)` - Получить список элементов
- `wait_for_element(locator, timeout)` - Ждать элемента
- `click_element(locator)` - Кликнуть на элемент
- `enter_text(locator, text)` - Ввести текст
- `is_element_visible(locator)` - Проверить видимость

### ListingPage
Page Object для работы со списком объявлений.

```python
from pages.listing_page import ListingPage

listing_page = ListingPage(driver, base_url)
listing_page.open_page(1)
links = listing_page.get_car_links()
total_pages = listing_page.get_total_pages()
```

**Основные методы:**
- `open_page(page_num)` - Открыть страницу
- `get_car_links()` - Получить ссылки на объявления
- `get_total_pages()` - Получить количество страниц

### CarDetailPage
Page Object для работы с деталями объявления.

```python
from pages.car_detail_page import CarDetailPage

detail_page = CarDetailPage(car_url)
title = detail_page.get_title()
price = detail_page.get_price()
car_data = detail_page.get_car_data()
```

**Основные методы:**
- `get_title()` - Название марки
- `get_year()` - Год выпуска
- `get_price()` - Цена
- `get_car_data()` - Все данные объявления

## 🎯 Параметры парсера

### Использование с разными настройками

```python
from auto_parser import AutoRuParser

# Парсить только до 2 млн рублей
parser = AutoRuParser(max_price=2000000, num_threads=8)

# Парсить только 5 страниц
parser.parse_all_pages(max_pages=5)

# Сохранить в другой файл
parser.save_to_excel('my_cars.xlsx')
```

## 📊 Результаты

После парсинга получите Excel файл с колонками:
- Марка
- Год выпуска
- Пробег
- Владельцы
- Состояние
- Коробка
- Двигатель
- Дата объявления
- Количество просмотров
- Цена

Данные сортируются по дате объявления (от новых к старым).

## ⚡ Производительность

- **Скорость парсинга:** ~50-100 объявлений в минуту
- **Параллельная обработка:** 6 потоков
- **Оптимизации:**
  - Отключены изображения в Chrome
  - Используется requests для деталей вместо Selenium
  - Сокращённые таймауты
  - ThreadPoolExecutor для параллелизма

## 🔍 Логирование

Для включения подробного логирования:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

## 🛠️ Расширение

### Добавление новой страницы

1. Создайте класс в папке `pages`:

```python
# pages/new_page.py
from base_page import BasePage
from selenium.webdriver.common.by import By

class NewPage(BasePage):
    MY_LOCATOR = (By.XPATH, '//my-xpath')
    
    def do_something(self):
        return self.get_text(self.MY_LOCATOR)
```

2. Используйте в парсере:

```python
from pages.new_page import NewPage

new_page = NewPage(driver)
result = new_page.do_something()
```

## ❌ Устранение ошибок

### SSL Certificate Error
```bash
pip install certifi
```

### ChromeDriver не найден
1. Скачайте ChromeDriver с https://chromedriver.chromium.org/
2. Поместите в папку проекта или укажите путь в config.py

### Ошибка при открытии Excel
Закройте файл и перезапустите парсер.

## 📝 Лицензия

MIT License

## 👨‍💻 Автор

Создано с использованием Page Object Pattern для QA Testing.
