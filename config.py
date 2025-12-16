# config.py
"""Конфигурация парсера auto.ru"""

# ==================== PARSER SETTINGS ====================
# ✅ ИСПРАВЛЕНО: Максимальная цена 1000000 руб
MAX_PRICE = 1000000

# Количество одновременных потоков для параллельной обработки
NUM_THREADS = 12

# ✅ ИСПРАВЛЕНО: Парсим ВСЕ страницы (None = все)
MAX_PAGES = None

# Имя выходного Excel файла
OUTPUT_FILENAME = 'auto_ru_cars_all.xlsx'

# ==================== URL SETTINGS ====================
# Регион для парсинга
REGION = 'moskva'

# ✅ ИСПРАВЛЕНО: Правильный базовый URL с параметром price_to
# Используется для сбора ВСЕ объявлений в регионе до 1000000 руб
BASE_URL_TEMPLATE = f"https://auto.ru/{REGION}/cars/all/?price_to={MAX_PRICE}"

# ==================== SELENIUM SETTINGS ====================
# Путь к ChromeDriver
CHROMEDRIVER_PATH = "./chromedriver.exe"

# Timeout для WebDriver операций (в секундах)
WEBDRIVER_TIMEOUT = 5

# Implicit wait для элементов (в секундах)
IMPLICIT_WAIT = 3

# ==================== REQUEST SETTINGS ====================
# Timeout для requests (в секундах)
REQUEST_TIMEOUT = 3

# User Agent для requests
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# ==================== PARSER DELAYS ====================
# Задержка между загрузкой страниц (в секундах)
PAGE_LOAD_DELAY = 0.3

# Задержка между загрузкой объявлений (в секундах)
CAR_LOAD_DELAY = 0.0

# Задержка между страницами при сборе ссылок (в секундах)
PAGINATION_DELAY = 0.0

# Подключение к пулу (в секундах)
CONNECTION_POOL_TIMEOUT = 1

# ==================== LOGGING ====================
# Формат логирования
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Уровень логирования
LOG_LEVEL = 'INFO'

# ==================== CHROME OPTIONS ====================
CHROME_ARGS = [
    '--disable-ssl-certificate-error',
    '--disable-ssl-certificate-validation',
    '--disable-blink-features=AutomationControlled',
    '--ignore-certificate-errors',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-extensions',
    '--disable-plugins',
    '--disable-images',
    '--disable-popup-blocking',
    '--disable-sync',
    '--disable-gpu',
    '--disable-web-resources',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-default-apps',
    '--disable-preconnect',
    '--disable-component-extensions-with-background-pages',
    '--disable-background-networking',
    '--disable-hang-monitor',
    '--disable-prompt-on-repost',
    '--disable-sync-preferences',
]

# ==================== PAGINATION ====================
# XPath для ссылок на объявления
CAR_LINK_XPATH = '//a[contains(@href, "/cars/used/sale/")]'

# XPath для пагинации
PAGINATION_XPATH = '//div[@class="Pagination__item"]/text()'

# ==================== CAR DETAILS ====================
# Locators для деталей объявлений
CAR_DETAIL_LOCATORS = {
    'title': '//h1[@class="CardHead__title"]/text()',
    'year': '(//a[@class="Link Link_color_black"]/text())[2]',
    'mileage': '(//div[@class="CardInfoSummarySimpleRow__content-IIKcj"]/text())[1]',
    'owners': '(//div[@class="CardInfoSummarySimpleRow__content-IIKcj"]/text())[2]',
    'condition': '(//div[@class="CardInfoSummarySimpleRow__content-IIKcj"]/text())[5]',
    'transmission': '(//div[@class="CardInfoSummaryComplexRow__cellValue-Hka8p"]/text())[2]',
    'engine': '(//div[@class="CardInfoSummaryComplexRow__cellValue-Hka8p"]/text())[1]',
    'date_posted': '//div[@class="CardHead__infoItem CardHead__creationDate"]/text()',
    'views': '//div[@class="CardHead__infoItem CardHead__views"]/text()',
    'price': '//span[@class="OfferPriceCaption__price"]/text()',
}

# ==================== EXCEL EXPORT ====================
# Столбцы для экспорта
EXPORT_COLUMNS = [
    'Марка',
    'Год выпуска',
    'Пробег',
    'Владельцы',
    'Состояние',
    'Коробка',
    'Двигатель',
    'Дата объявления',
    'Количество просмотров',
    'Цена'
]

# Формат даты для Excel
DATE_FORMAT = '%d.%m.%Y'

# Формат цены (с разделителями)
PRICE_FORMAT = '{:,}'

# ==================== CONNECTION POOLING ====================
# Максимальное количество соединений в пуле
CONNECTION_POOL_CONNECTIONS = 20

# Максимальное количество соединений в пуле на хост
CONNECTION_POOL_MAXSIZE = 20

# Повторные попытки подключения
RETRIES = 3
