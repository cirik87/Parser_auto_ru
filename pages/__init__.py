# pages/__init__.py
"""Page Objects для парсера auto.ru"""

from pages.base_page import BasePage
from pages.listing_page import ListingPage
from pages.car_detail_page import CarDetailPage

__all__ = [
    'BasePage',
    'ListingPage',
    'CarDetailPage'
]
