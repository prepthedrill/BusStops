import base64
import codecs
import json
import time
from urllib.parse import parse_qs, urlparse

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .exeptions import InvalidParsingDataException


class YandexMapParser:
    def __init__(self, region, city, number_route, time_sleep=2):
        self.region = region
        self.city = city
        self.number_route = number_route
        self.time_sleep = time_sleep

        chrome_options = Options()
        chrome_options.add_experimental_option('w3c', True)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.yandex_map_link = 'https://yandex.ru/maps/'

    def _open_yandex_map(self):
        if self.driver.current_url != self.yandex_map_link:
            self.driver.get(self.yandex_map_link)
            time.sleep(self.time_sleep)

    def _perform_search(self, request_text):
        """Выполняет вставку текста в поисковое окно и выполняет поиск."""
        search_box_root = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='search-form-view__input']")
            )
        )
        search_box = search_box_root.find_element(
            By.XPATH, ".//input[@class='input__control _bold']"
        )
        # предварительно очищаем окно поиска
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.DELETE)
        # вставляем текст и выполняем запрос
        search_box.send_keys(request_text)
        search_box.send_keys(Keys.RETURN)
        time.sleep(self.time_sleep)
        time.sleep(self.time_sleep)

    def _open_variants_route(self):
        # нажимаем на кнопку "Другие варианты маршрута"
        button_variants_route = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='masstransit-card-header-view__another-threads']")
            )
        )
        button_variants_route.click()
        time.sleep(self.time_sleep)

    def _get_variants_route(self):
        root_variants_route = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//ul[@class='masstransit-threads-view__list']")
            )
        )
        list_variants_route = root_variants_route.find_elements(
            By.XPATH, ".//li[@class='masstransit-threads-view__item' or @class='masstransit-threads-view__item _is-active']"
        )
        time.sleep(self.time_sleep)

        result = []
        for variant_route in list_variants_route:
            name_variant_route = variant_route.text.replace('\n', ' > ')
            result.append(name_variant_route)
        return result

    def _create_new_tab(self):
        self.driver.execute_script("window.open('', '_blank');")
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def _close_new_tab(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def _get_data_network(self):
        network_entries = self.driver.execute_script("return window.performance.getEntriesByType('resource')")

        target_url = "https://yandex.ru/maps/api/masstransit/getLine?"

        is_invalid_request = True
        for entry in network_entries:
            if target_url in entry['name']:
                is_invalid_request = False
                self._create_new_tab()
                self.driver.get(entry['name'])
                time.sleep(2)
                response = self.driver.page_source
                self._close_new_tab()
                response = response[131:-20]
                with open("parser/result.json", "w", encoding='utf-8') as json_file:
                    json_file.write(response)
                break
        if is_invalid_request:
            raise InvalidParsingDataException('Переданы неверные данные для парсинга!')



    def _get_clear_data_routes(self, list_var_routes):
        with open("parser/result.json", "r", encoding='utf-8') as json_file:
            data = json.load(json_file)

        result = {}
        index_var_route = 0
        for routes in data['data']['features']:
            result[list_var_routes[index_var_route]] = []
            count = 1
            for data in routes['features']:
                if count % 2 != 0:
                    coordinate = data['coordinates']
                    coordinate.reverse()
                    bus_stop = {
                        'name': data['name'],
                        'coordinates': coordinate
                    }
                    result[list_var_routes[index_var_route]].append(bus_stop)
                else:
                    points = []
                    for coordinate in data['points']:
                        coordinate.reverse()
                        points.append(coordinate)
                    result[list_var_routes[index_var_route]].append(points)
                count += 1
            index_var_route += 1
        return result

    def start_parser(self):
        self._open_yandex_map()
        self._perform_search(f'{self.region}, {self.city}')
        time.sleep(2)
        self._perform_search(self.number_route)
        try:
            self._get_data_network()
        except InvalidParsingDataException:
            self.driver.close()
            return
        try:
            self._open_variants_route()
            return self._get_clear_data_routes(self._get_variants_route())
        except TimeoutException:
            return self._get_clear_data_routes([self.number_route])
