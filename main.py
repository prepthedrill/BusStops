import logging
import os
import shutil
import time
from datetime import datetime
from parser.parser import YandexMapParser

import folium
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtWebEngineWidgets import QWebEngineView

from create_voice.create_voice import APIVoice
from data.rus_regions import rus_regions
from database.data_for_db import data_for_DisplayTypes, data_for_Languages
from database.db import SQLiteDatabase


class BusStopsApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('PyQt/gui.ui', self)

        self.ui.toolButton.clicked.connect(self.start_parser)
        self.ui.toolButton_create_db.clicked.connect(self.create_db)
        self.ui.toolButton_create_voice.clicked.connect(self.creating_voice_acting)

        ########### Валидация для полей ввода ###########
        name_city_validator = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r'^[а-яА-Яa-zA-Z, \-]{1,150}$'))
        letter_route_validator = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r'^[а-яА-Яa-zA-Z\-]{1,5}$'))
        number_route_validator = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r'^\d{1,5}$'))
        api_token = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r'^[a-zA-Z0-9\-\.,!?;:()\'" ]{1,100}$'))
        index_db = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r'^[0-9]{1,6}$'))

        self.lineEdit_city.setValidator(name_city_validator)
        self.lineEdit_token_voice.setValidator(api_token)
        self.lineEdit_letter_route.setValidator(letter_route_validator)
        self.lineEdit_num_route.setValidator(number_route_validator)
        self.lineEdit_db_index.setValidator(index_db)

        ########### Добавление карты ###########
        layout_parser = QtWidgets.QVBoxLayout(self.frame_for_map)
        self.webview_parser = QWebEngineView(self.frame_for_map)
        layout_parser.addWidget(self.webview_parser)

        layout_db = QtWidgets.QVBoxLayout(self.frame_for_map_2)
        self.webview_db = QWebEngineView(self.frame_for_map_2)
        layout_db.addWidget(self.webview_db)

        layout_voice = QtWidgets.QVBoxLayout(self.frame_for_map_3)
        self.webview_voice = QWebEngineView(self.frame_for_map_3)
        layout_voice.addWidget(self.webview_voice)

        self.map_parser = folium.Map(location=[58.5966, 49.6601], zoom_start=13)
        data = self.map_parser._repr_html_()

        self.webview_parser.setHtml(data)
        self.webview_db.setHtml(data)
        self.webview_voice.setHtml(data)

        ########### Добавление видов транспорта и регионов ###########
        self.comboBox_parser_set_transport.addItems(['автобус', 'трамвай', 'тройлебус', 'маршрутное такси'])
        self.comboBox_parser_set_regions.addItems(rus_regions)

        self.show()


    ########################## Общие функции ##########################
    def show_msg_info(self, window_title: str, text: str):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle(window_title)
        msg.setText(text)
        msg.setIcon(QtWidgets.QMessageBox.Icon.NoIcon)
        msg.exec()

    def create_dir(self, path):
        if os.path.exists(path):
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Icon.Question)
            btn = msg.standardButtons()

            msg.setWindowTitle('Внимание!')
            msg.setText(f'{path} уже существует!\nПерезаписать?')
            msg.setStandardButtons(btn.Yes | btn.No)

            confirmation = msg.exec()

            if confirmation == btn.Yes:
                shutil.rmtree(path, ignore_errors=True)
                os.mkdir(path)
                return True
            else:
                return False
        else:
            os.mkdir(path)
            return True

    def show_save_dialog(self):
        qt_dialog = QtWidgets.QFileDialog()
        path_dir = qt_dialog.getExistingDirectory()
        return path_dir

    ########################### Парсер ###########################
    def start_parser(self):
        if len(self.lineEdit_city.text()) == 0 or len(self.lineEdit_num_route.text()) == 0:
            self.show_msg_info('Внимание!', 'Обязательные поля не заполнены!')
            return
        region = self.comboBox_parser_set_regions.currentText()
        city = self.lineEdit_city.text()
        if self.lineEdit_letter_route.text():
            number_route = (f'{self.comboBox_parser_set_transport.currentText()}'
                            f' {self.lineEdit_letter_route.text()}'
                            f' {self.lineEdit_num_route.text()}')
        else:
            number_route = (f'{self.comboBox_parser_set_transport.currentText()}'
                            f' {self.lineEdit_num_route.text()}')

        try:
            parser = YandexMapParser(region, city, number_route)
            self.data_routes = parser.start_parser()
            self.add_routes_to_map(self.data_routes)
        except Exception as e:
            self.show_msg_info(
                'Внимание!',
                'Возникла ошибка при парсинге данных!\n'
                'Убедитесь, что заданы верные данные для парсинга!'
            )
            logging.error(f'Ошибка при парсинге данных: {e}')


    def add_routes_to_map(self, data_routes):
        self.map_parser = folium.Map(location=[58.5966, 49.6601], zoom_start=13)

        self.comboBox_forward_db.clear()
        self.comboBox_reverse_db.clear()
        self.comboBox_forward_voice.clear()
        self.comboBox_reverse_voice.clear()
        self.comboBox_reverse_db.addItem('-нет-')
        self.comboBox_reverse_voice.addItem('-нет-')

        for name_var, route in data_routes.items():
            layer = folium.FeatureGroup(name=name_var)
            self.comboBox_forward_db.addItem(name_var)
            self.comboBox_reverse_db.addItem(name_var)
            self.comboBox_forward_voice.addItem(name_var)
            self.comboBox_reverse_voice.addItem(name_var)
            self.map_parser.add_child(layer)

            line_coords = []
            number = 1
            for data in route:
                if isinstance(data, dict):
                    html = f'''
                    <div style="position: relative;
                                width: 20px;
                                height: 20px;
                                line-height: 20px;
                                text-align: center;
                                border-radius: 50%;
                                background-color: white;
                                border: 2px solid green;
                                color: green;
                                font-size: 10px;">
                        {number}
                    </div>
                    '''
                    marker = folium.Marker(location=data['coordinates'], popup=data['name'])
                    marker.add_child(folium.DivIcon(html=html))
                    marker.add_to(layer)
                    number += 1
                else:
                    line_coords += data

            line = folium.PolyLine(locations=line_coords, color='green')
            line.add_to(layer)
            self.map_parser.location = [line_coords[0][0], line_coords[0][1]]
        folium.LayerControl().add_to(self.map_parser)
        data = self.map_parser._repr_html_()
        self.webview_parser.setHtml(data)
        self.webview_db.setHtml(data)
        self.webview_voice.setHtml(data)

    ########################### БД ###########################
    def create_db(self):
        if len(self.comboBox_forward_db.currentText()) == 0:
            self.show_msg_info('Внимание!', 'Необходимо сначала спарсить маршрут!')
        else:
            path_dir = self.show_save_dialog()
            if not path_dir:
                return
            save_path = f'{path_dir}/acrDB.db'

            while True:
                if os.path.exists(save_path):
                    self.show_msg_info('Внимание!', 'В выбранной вами директории уже существует файл с БД!\nПерезаписать БД?')
                    save_path = f'{self.show_save_dialog()}/acrDB.db'
                else:
                    break

            db = SQLiteDatabase(save_path)
            db.connect()
            db.create_tables()
            for data in data_for_DisplayTypes:
                db.insert_data('DisplayTypes', name=data)
            for data in data_for_Languages:
                db.insert_data('Languages', name=data)

            if len(self.lineEdit_db_index.text()) == 0:
                index_bus_stop = 0
            else:
                index_bus_stop = int(self.lineEdit_db_index.text())
            for select_route in [self.comboBox_forward_db.currentText(), self.comboBox_reverse_db.currentText()]:
                if select_route != '-нет-':
                    for route_data in self.data_routes[select_route]:
                        if isinstance(route_data, dict):
                            db.insert_data(
                                'Stops',
                                stopIdInPr=index_bus_stop,
                                name=route_data['name'],
                                # nameNat={},
                                lat=route_data['coordinates'][0],
                                lng=route_data['coordinates'][1],
                                userEdited=1,
                                actualDate=datetime.now().date()
                            )
                            index_bus_stop += 1
            self.show_msg_info('Внимание!', f'БД успешно создана!\n{save_path}')

    ########################### Озвучка ###########################
    def get_text_for_api(self, stops: list) -> list:
        result = []
        for i in range(len(stops) - 1):
            result.append(f"остановка {stops[i].replace('(', '').replace(')', '').replace('№', 'номер ')}")
            result.append(f"следущая остановка {stops[i + 1].replace('(', '').replace(')', '').replace('№', 'номер ')}")
        result.append(f'остановка {stops[-1]}')
        return result

    def creating_voice_acting(self):
        # проверяем есть ли маршрут
        if len(self.comboBox_forward_voice.currentText()) == 0:
            self.show_msg_info('Внимание!', 'Необходимо сначала спарсить маршрут!')
            return

        # проверяем заполнено ли поле с токеном
        if len(self.lineEdit_token_voice.text()) == 0:
            self.show_msg_info('Внимание!', 'Заполните поле с токеном!')
            return

        # выбираем директорию для сохранения озвучки
        path_dir_to_voice_acting = f'{self.show_save_dialog()}/Озвучка'

        # если пользователь не выбрал директорию
        if path_dir_to_voice_acting == '/Озвучка':
            return

        # создаем директории для сохранения озвучки
        if not self.create_dir(path_dir_to_voice_acting):
            self.show_msg_info('Внимание!', 'Создание озвучуи отменено!')
        if not self.create_dir(f'{path_dir_to_voice_acting}/forward'):
            self.show_msg_info('Внимание!', 'Создание озвучуи отменено!')
        if not self.create_dir(f'{path_dir_to_voice_acting}/reverse'):
            self.show_msg_info('Внимание!', 'Создание озвучуи отменено!')

        forward_name_list = []
        for data_route in self.data_routes[self.comboBox_forward_voice.currentText()]:
            if isinstance(data_route, dict):
                forward_name_list.append(data_route['name'])
        forward_name_list = self.get_text_for_api(forward_name_list)

        reverse_name_list = []
        if self.comboBox_reverse_voice.currentText() != '-нет-':
            for data_route in self.data_routes[self.comboBox_reverse_voice.currentText()]:
                if isinstance(data_route, dict):
                    reverse_name_list.append(data_route['name'])
            reverse_name_list = self.get_text_for_api(reverse_name_list)

        list_texts = list(set(forward_name_list + reverse_name_list))

        # создаем прогрессбар
        progress = QtWidgets.QProgressDialog(
            "Создание озвучки...",
            None,
            0,
            (len(list_texts) * 2) + len(forward_name_list) + len(reverse_name_list) + 1
        )
        progress.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        # progress.setValue(1)

        api = APIVoice(self.lineEdit_token_voice.text())

        progress_val = 0 # значение прогресс бара
        text_process = dict()
        is_problems = False

        # цикл отправки запросов к api
        index = 0
        count_error = 0
        while index < len(list_texts):
            logging.info('Попытка отправить POST запрос...')
            text = list_texts[index]
            response = api.send_text(text)
            logging.info(f'POST запрос отправлен. Текст: {text}')
            logging.info(f'Ответ API:\n{response}')
            if response['status'] == 401:
                self.show_msg_info('Внимание!', 'Проблемы с авторизацией, проверьте токен!')
                return
            if response['status'] == 429:
                self.show_msg_info('Внимание!', 'Сервер API перегружен, ждем 65 секунд...')
                time.sleep(65)
                continue
            if response['status'] != 205:
                if count_error <= 5:
                    count_error += 1
                    time.sleep(5)
                    continue
                else:
                    self.show_msg_info(
                        'Внимание!',
                        'При отправке запросов на создание озвучки API дало сбой!\n'
                        f'Код ответа: {response["status"]}\nСоздание озвучки отменено!'
                    )
                    return

            index += 1
            count_error = 0
            text_process[text] = response['process']
            progress.setValue(progress_val)
            progress_val += 1

        # цикл получения ссылок
        text_download_link = dict()
        count_error = 0
        index = 0
        keys_list = list(text_process.keys())
        while index < len(keys_list):
            text = keys_list[index]
            process = text_process[text]
            logging.info('Попытка отправить запрос на получение ссылки...')
            response = api.get_link_download(process)
            logging.info(f'Запрос на получение ссылки отправлен')
            logging.info(f'Ответ API:\n{response}')
            if response['status'] == 401:
                self.show_msg_info('Внимание!', 'Проблемы с авторизацией, проверьте токен')
                return
            if response['status'] == 429:
                self.show_msg_info('Внимание!', 'Сервер API перегружен, ждем 65 секунд...')
                time.sleep(65)
                continue
            if response['status'] != 200:
                logging.error(f'API ответила кодом {response["status"]}')
                if count_error <= 5:
                    count_error += 1
                    time.sleep(5)
                    logging.info('Попытка еще раз отпарвить запрос на получение ссылки')
                    continue
                else:
                    self.show_msg_info(
                        'Внимание!',
                        'При отправке запросов на получение ссылок для скачивания API дало сбой!\n'
                        f'Код ответа: {response["status"]}\nСоздание озвучки отменено!'
                    )
                    return

            index += 1
            count_error = 0
            text_download_link[text] = response['message']
            progress.setValue(progress_val)
            progress_val += 1

        # цикл заргрузки озвучки
        for name_dir, name_list in {
            'forward': forward_name_list,
            'reverse': reverse_name_list
        }.items():
            for i, text in enumerate(name_list):
                if text in text_download_link:
                    try:
                        if api.download_file(text_download_link[text], f'{path_dir_to_voice_acting}/{name_dir}/{i} - {text}.mp3') == 429:
                            while True:
                                self.show_msg_info('Внимание!', 'Сервер API перегружен, ждем 65 секунд...')
                                time.sleep(65)
                                if api.download_file(text_download_link[text], f'{path_dir_to_voice_acting}/{name_dir}/{i} - {text}.mp3') == 200:
                                    break
                        logging.info(f'Файл "{i} - {text}.mp3" загрузился')
                    except Exception as e:
                        logging.error(f'Не удалось загрузить файл "{i} - {text}.mp3", ошибка: {e}')
                        self.show_msg_info(
                            'Внимание!',
                            f'Не удалось загрузить файл "{i} - {text}.mp3", ошибка:\n{e}'
                        )
                        return

                    progress.setValue(progress_val)
                    progress_val += 1

        progress.setValue((len(list_texts) * 2) + len(forward_name_list) + len(reverse_name_list) + 1)

        logging.info('Конец обработки озвучки')
        self.show_msg_info('Внимание!', f'Аудиофалы успешно созданы!\nОни находятся в директории {path_dir_to_voice_acting}')


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = BusStopsApp()
    sys.exit(app.exec())
