import logging
import os
import shutil
import time
from datetime import datetime
from parser.parser import YandexMapParser

import folium
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWebEngineWidgets import QWebEngineView

from create_voice.create_voice import APIVoice
from data.rus_regions import rus_regions
from database.data_for_db import data_for_DisplayTypes, data_for_Languages
from database.db import SQLiteDatabase


class Ui_MainWindow(object):
    data_routes = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("BusStops")
        MainWindow.resize(804, 557)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 800, 530))
        self.tabWidget.setStyleSheet("QWidget{\n"
"    background-color: white;\n"
"}")
        self.tabWidget.setObjectName("tabWidget")
        self.tab_parser = QtWidgets.QWidget()
        self.tab_parser.setObjectName("tab_parser")
        self.frame_head_parser = QtWidgets.QFrame(parent=self.tab_parser)
        self.frame_head_parser.setGeometry(QtCore.QRect(0, 0, 800, 51))
        self.frame_head_parser.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.frame_head_parser.setStyleSheet("QFrame{\n"
"    background-color: #8B808D;\n"
"}")
        self.frame_head_parser.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_head_parser.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_head_parser.setObjectName("frame_head_parser")
        self.lineEdit_city = QtWidgets.QLineEdit(parent=self.frame_head_parser)
        self.lineEdit_city.setGeometry(QtCore.QRect(250, 10, 171, 31))
        self.lineEdit_city.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.lineEdit_city.setAutoFillBackground(False)
        self.lineEdit_city.setStyleSheet("QLineEdit{\n"
"    background-color: white; /* Красный цвет фона */\n"
"    color: black; /* Белый цвет текста */\n"
"    border: 1px solid #3B383D;\n"
"    border-radius: 2px; /* Радиус скругления в пикселях */\n"
"}")
        self.lineEdit_city.setText("")
        self.lineEdit_city.setCursorMoveStyle(QtCore.Qt.CursorMoveStyle.LogicalMoveStyle)
        self.lineEdit_city.setObjectName("lineEdit_city")
        self.lineEdit_letter_route = QtWidgets.QLineEdit(parent=self.frame_head_parser)
        self.lineEdit_letter_route.setGeometry(QtCore.QRect(430, 10, 41, 31))
        self.lineEdit_letter_route.setStyleSheet("QLineEdit{\n"
"    background-color: white; /* Красный цвет фона */\n"
"    color: black; /* Белый цвет текста */\n"
"    border: 1px solid #3B383D;\n"
"    border-radius: 2px; /* Радиус скругления в пикселях */\n"
"}")
        self.lineEdit_letter_route.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_letter_route.setObjectName("lineEdit_letter_route")
        self.lineEdit_num_route = QtWidgets.QLineEdit(parent=self.frame_head_parser)
        self.lineEdit_num_route.setGeometry(QtCore.QRect(480, 10, 71, 31))
        self.lineEdit_num_route.setStyleSheet("QLineEdit{\n"
"    background-color: white; /* Красный цвет фона */\n"
"    color: black; /* Белый цвет текста */\n"
"    border: 1px solid #3B383D;\n"
"    border-radius: 2px; /* Радиус скругления в пикселях */\n"
"}")
        self.lineEdit_num_route.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_num_route.setObjectName("lineEdit_num_route")
        self.toolButton = QtWidgets.QToolButton(parent=self.frame_head_parser)
        self.toolButton.setGeometry(QtCore.QRect(670, 10, 111, 31))
        self.toolButton.setStyleSheet("QToolButton {\n"
"    background-color: white; /* цвет фона */\n"
"    color: #3B383D; /* цвет текста */\n"
"    border: 1px solid #3B383D;\n"
"    border-radius: 2px; /* Радиус скругления в пикселях */\n"
"}\n"
"QToolButton:hover {\n"
"    background-color: #3B383D; /* цвет фона */\n"
"    color: white; /* цвет текста */\n"
"    border: 1px solid white;\n"
"    border-radius: 2px; /* Радиус скругления в пикселях */\n"
"}")
        self.toolButton.setAutoRepeat(False)
        self.toolButton.setObjectName("toolButton")
        self.comboBox_parser_set_transport = QtWidgets.QComboBox(parent=self.frame_head_parser)
        self.comboBox_parser_set_transport.setGeometry(QtCore.QRect(560, 10, 101, 31))
        self.comboBox_parser_set_transport.setStyleSheet("QComboBox {\n"
"    background-color: white; /* Серый цвет фона */\n"
"    color: #3B383D; /* Черный цвет текста */\n"
"    border: 1px solid #3B383D; /* 1 пиксель серая сплошная граница */\n"
"    border-radius: 2px; /* Радиус скругления в пикселях */\n"
"    padding: 5px; /* Внутренний отступ внутри элемента */\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 10px; /* Ширина кнопки выпадающего списка */\n"
"    border-left-width: 1px;\n"
"    border-left-color: darkgray;\n"
"    border-left-style: solid;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: white; /* Белый цвет фона выпадающего списка */\n"
"    color: #3B383D; /* Черный цвет текста в выпадающем списке */\n"
"    border: 1px solid #3B383D; /* 1 пиксель серая сплошная граница выпадающего списка */\n"
"    selection-background-color: #7A686D; /* Синий цвет фона для выбранного элемента в списке */\n"
"    selection-color: #FFFFFF; /* Белый цвет текста для выбранного элемента в списке */\n"
"}\n"
"")
        self.comboBox_parser_set_transport.setObjectName("comboBox_parser_set_transport")
        self.comboBox_parser_set_regions = QtWidgets.QComboBox(parent=self.frame_head_parser)
        self.comboBox_parser_set_regions.setGeometry(QtCore.QRect(10, 10, 231, 31))
        self.comboBox_parser_set_regions.setStyleSheet("QComboBox {\n"
"    background-color: white; /* Серый цвет фона */\n"
"    color: #3B383D; /* Черный цвет текста */\n"
"    border: 1px solid #3B383D; /* 1 пиксель серая сплошная граница */\n"
"    border-radius: 2px; /* Радиус скругления в пикселях */\n"
"    padding: 5px; /* Внутренний отступ внутри элемента */\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 10px; /* Ширина кнопки выпадающего списка */\n"
"    border-left-width: 1px;\n"
"    border-left-color: darkgray;\n"
"    border-left-style: solid;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: white; /* Белый цвет фона выпадающего списка */\n"
"    color: #3B383D; /* Черный цвет текста в выпадающем списке */\n"
"    border: 1px solid #3B383D; /* 1 пиксель серая сплошная граница выпадающего списка */\n"
"    selection-background-color: #7A686D; /* Синий цвет фона для выбранного элемента в списке */\n"
"    selection-color: #FFFFFF; /* Белый цвет текста для выбранного элемента в списке */\n"
"}\n"
"")
        self.comboBox_parser_set_regions.setObjectName("comboBox_parser_set_regions")
        self.frame_main_parser = QtWidgets.QFrame(parent=self.tab_parser)
        self.frame_main_parser.setGeometry(QtCore.QRect(0, 51, 800, 450))
        self.frame_main_parser.setStyleSheet("QFrame{\n"
"    background-color: #EDEBE1;\n"
"}")
        self.frame_main_parser.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_main_parser.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_main_parser.setObjectName("frame_main_parser")
        self.frame_for_map = QtWidgets.QFrame(parent=self.frame_main_parser)
        self.frame_for_map.setGeometry(QtCore.QRect(10, 10, 771, 431))
        self.frame_for_map.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_for_map.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_for_map.setObjectName("frame_for_map")
        self.tabWidget.addTab(self.tab_parser, "")
        self.tab_create_db = QtWidgets.QWidget()
        self.tab_create_db.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.tab_create_db.setObjectName("tab_create_db")
        self.frame_main_db = QtWidgets.QFrame(parent=self.tab_create_db)
        self.frame_main_db.setGeometry(QtCore.QRect(0, 51, 800, 550))
        self.frame_main_db.setStyleSheet("QFrame{\n"
"    background-color: #EDEBE1;\n"
"}")
        self.frame_main_db.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_main_db.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_main_db.setObjectName("frame_main_db")
        self.frame_for_map_2 = QtWidgets.QFrame(parent=self.frame_main_db)
        self.frame_for_map_2.setGeometry(QtCore.QRect(10, 130, 771, 311))
        self.frame_for_map_2.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_for_map_2.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_for_map_2.setObjectName("frame_for_map_2")
        self.comboBox_forward_db = QtWidgets.QComboBox(parent=self.frame_main_db)
        self.comboBox_forward_db.setGeometry(QtCore.QRect(10, 10, 771, 31))
        self.comboBox_forward_db.setStyleSheet("QComboBox {\n"
"    background-color: white; /* Серый цвет фона */\n"
"    color: #3B383D; /* Черный цвет текста */\n"
"    border: 1px solid #CCCCCC; /* 1 пиксель серая сплошная граница */\n"
"    border-radius: 2px; /* Радиус скругления в пикселях */\n"
"    padding: 5px; /* Внутренний отступ внутри элемента */\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 20px; /* Ширина кнопки выпадающего списка */\n"
"    border-left-width: 1px;\n"
"    border-left-color: darkgray;\n"
"    border-left-style: solid;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: white; /* Белый цвет фона выпадающего списка */\n"
"    color: #3B383D; /* Черный цвет текста в выпадающем списке */\n"
"    border: 1px solid #CCCCCC; /* 1 пиксель серая сплошная граница выпадающего списка */\n"
"    selection-background-color: #7A686D; /* Синий цвет фона для выбранного элемента в списке */\n"
"    selection-color: #FFFFFF; /* Белый цвет текста для выбранного элемента в списке */\n"
"}\n"
"")
        self.comboBox_forward_db.setObjectName("comboBox_forward_db")
        self.comboBox_reverse_db = QtWidgets.QComboBox(parent=self.frame_main_db)
        self.comboBox_reverse_db.setGeometry(QtCore.QRect(10, 70, 771, 31))
        self.comboBox_reverse_db.setStyleSheet("QComboBox {\n"
"    background-color: white; /* Серый цвет фона */\n"
"    color: #3B383D; /* Черный цвет текста */\n"
"    border: 1px solid #CCCCCC; /* 1 пиксель серая сплошная граница */\n"
"    border-radius: 2px; /* Радиус скругления в пикселях */\n"
"    padding: 5px; /* Внутренний отступ внутри элемента */\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 20px; /* Ширина кнопки выпадающего списка */\n"
"    border-left-width: 1px;\n"
"    border-left-color: darkgray;\n"
"    border-left-style: solid;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: white; /* Белый цвет фона выпадающего списка */\n"
"    color: #3B383D; /* Черный цвет текста в выпадающем списке */\n"
"    border: 1px solid #CCCCCC; /* 1 пиксель серая сплошная граница выпадающего списка */\n"
"    selection-background-color: #7A686D; /* Синий цвет фона для выбранного элемента в списке */\n"
"    selection-color: #FFFFFF; /* Белый цвет текста для выбранного элемента в списке */\n"
"}\n"
"")
        self.comboBox_reverse_db.setObjectName("comboBox_reverse_db")
        self.label = QtWidgets.QLabel(parent=self.frame_main_db)
        self.label.setGeometry(QtCore.QRect(10, 42, 771, 20))
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(parent=self.frame_main_db)
        self.label_2.setGeometry(QtCore.QRect(10, 103, 771, 20))
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.frame_head_db = QtWidgets.QFrame(parent=self.tab_create_db)
        self.frame_head_db.setGeometry(QtCore.QRect(0, 0, 800, 51))
        self.frame_head_db.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.frame_head_db.setStyleSheet("QFrame{\n"
"    background-color: #8B808D;\n"
"}")
        self.frame_head_db.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_head_db.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_head_db.setObjectName("frame_head_db")
        self.toolButton_create_db = QtWidgets.QToolButton(parent=self.frame_head_db)
        self.toolButton_create_db.setGeometry(QtCore.QRect(210, 10, 571, 31))
        self.toolButton_create_db.setStyleSheet("QToolButton {\n"
"    background-color: white; /* цвет фона */\n"
"    color: #3B383D; /* цвет текста */\n"
"    border: 1px solid #3B383D;\n"
"    border-radius: 2px; /* Радиус скругления в пикселях */\n"
"}\n"
"QToolButton:hover {\n"
"    background-color: #3B383D; /* цвет фона */\n"
"    color: white; /* цвет текста */\n"
"    border: 1px solid white;\n"
"    border-radius: 2px; /* Радиус скругления в пикселях */\n"
"}")
        self.toolButton_create_db.setAutoRepeat(False)
        self.toolButton_create_db.setObjectName("toolButton_create_db")
        self.lineEdit_db_index = QtWidgets.QLineEdit(parent=self.frame_head_db)
        self.lineEdit_db_index.setGeometry(QtCore.QRect(10, 10, 191, 31))
        self.lineEdit_db_index.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.lineEdit_db_index.setAutoFillBackground(False)
        self.lineEdit_db_index.setStyleSheet("QLineEdit{\n"
"    background-color: white; /* Красный цвет фона */\n"
"    color: black; /* Белый цвет текста */\n"
"    border: 1px solid #3B383D;\n"
"    border-radius: 2px; /* Радиус скругления в пикселях */\n"
"}")
        self.lineEdit_db_index.setText("")
        self.lineEdit_db_index.setCursorMoveStyle(QtCore.Qt.CursorMoveStyle.LogicalMoveStyle)
        self.lineEdit_db_index.setObjectName("lineEdit_db_index")
        self.tabWidget.addTab(self.tab_create_db, "")
        self.tab_create_voice = QtWidgets.QWidget()
        self.tab_create_voice.setObjectName("tab_create_voice")
        self.frame_head_voice = QtWidgets.QFrame(parent=self.tab_create_voice)
        self.frame_head_voice.setGeometry(QtCore.QRect(0, 0, 800, 51))
        self.frame_head_voice.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.frame_head_voice.setStyleSheet("QFrame{\n"
"    background-color: #8B808D;\n"
"}")
        self.frame_head_voice.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_head_voice.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_head_voice.setObjectName("frame_head_voice")
        self.toolButton_create_voice = QtWidgets.QToolButton(parent=self.frame_head_voice)
        self.toolButton_create_voice.setGeometry(QtCore.QRect(460, 10, 321, 31))
        self.toolButton_create_voice.setStyleSheet("QToolButton {\n"
"    background-color: white; /* цвет фона */\n"
"    color: #3B383D; /* цвет текста */\n"
"    border: 1px solid #3B383D;\n"
"    border-radius: 2px; /* Радиус скругления в пикселях */\n"
"}\n"
"QToolButton:hover {\n"
"    background-color: #3B383D; /* цвет фона */\n"
"    color: white; /* цвет текста */\n"
"    border: 1px solid white;\n"
"    border-radius: 2px; /* Радиус скругления в пикселях */\n"
"}")
        self.toolButton_create_voice.setAutoRepeat(False)
        self.toolButton_create_voice.setObjectName("toolButton_create_voice")
        self.lineEdit_token_voice = QtWidgets.QLineEdit(parent=self.frame_head_voice)
        self.lineEdit_token_voice.setGeometry(QtCore.QRect(10, 10, 441, 31))
        self.lineEdit_token_voice.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.lineEdit_token_voice.setAutoFillBackground(False)
        self.lineEdit_token_voice.setStyleSheet("QLineEdit{\n"
"    background-color: white; /* Красный цвет фона */\n"
"    color: black; /* Белый цвет текста */\n"
"    border: 1px solid #3B383D;\n"
"    border-radius: 2px; /* Радиус скругления в пикселях */\n"
"}")
        self.lineEdit_token_voice.setText("")
        self.lineEdit_token_voice.setCursorMoveStyle(QtCore.Qt.CursorMoveStyle.LogicalMoveStyle)
        self.lineEdit_token_voice.setObjectName("lineEdit_token_voice")
        self.frame_main_voice = QtWidgets.QFrame(parent=self.tab_create_voice)
        self.frame_main_voice.setGeometry(QtCore.QRect(0, 51, 800, 550))
        self.frame_main_voice.setStyleSheet("QFrame{\n"
"    background-color: #EDEBE1;\n"
"}")
        self.frame_main_voice.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_main_voice.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_main_voice.setObjectName("frame_main_voice")
        self.frame_for_map_3 = QtWidgets.QFrame(parent=self.frame_main_voice)
        self.frame_for_map_3.setGeometry(QtCore.QRect(10, 130, 771, 301))
        self.frame_for_map_3.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_for_map_3.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_for_map_3.setObjectName("frame_for_map_3")
        self.comboBox_forward_voice = QtWidgets.QComboBox(parent=self.frame_main_voice)
        self.comboBox_forward_voice.setGeometry(QtCore.QRect(10, 10, 771, 31))
        self.comboBox_forward_voice.setStyleSheet("QComboBox {\n"
"    background-color: white; /* Серый цвет фона */\n"
"    color: #3B383D; /* Черный цвет текста */\n"
"    border: 1px solid #CCCCCC; /* 1 пиксель серая сплошная граница */\n"
"    border-radius: 2px; /* Радиус скругления в пикселях */\n"
"    padding: 5px; /* Внутренний отступ внутри элемента */\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 20px; /* Ширина кнопки выпадающего списка */\n"
"    border-left-width: 1px;\n"
"    border-left-color: darkgray;\n"
"    border-left-style: solid;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: white; /* Белый цвет фона выпадающего списка */\n"
"    color: #3B383D; /* Черный цвет текста в выпадающем списке */\n"
"    border: 1px solid #CCCCCC; /* 1 пиксель серая сплошная граница выпадающего списка */\n"
"    selection-background-color: #7A686D; /* Синий цвет фона для выбранного элемента в списке */\n"
"    selection-color: #FFFFFF; /* Белый цвет текста для выбранного элемента в списке */\n"
"}\n"
"")
        self.comboBox_forward_voice.setObjectName("comboBox_forward_voice")
        self.comboBox_reverse_voice = QtWidgets.QComboBox(parent=self.frame_main_voice)
        self.comboBox_reverse_voice.setGeometry(QtCore.QRect(10, 70, 771, 31))
        self.comboBox_reverse_voice.setStyleSheet("QComboBox {\n"
"    background-color: white; /* Серый цвет фона */\n"
"    color: #3B383D; /* Черный цвет текста */\n"
"    border: 1px solid #CCCCCC; /* 1 пиксель серая сплошная граница */\n"
"    border-radius: 2px; /* Радиус скругления в пикселях */\n"
"    padding: 5px; /* Внутренний отступ внутри элемента */\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 20px; /* Ширина кнопки выпадающего списка */\n"
"    border-left-width: 1px;\n"
"    border-left-color: darkgray;\n"
"    border-left-style: solid;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: white; /* Белый цвет фона выпадающего списка */\n"
"    color: #3B383D; /* Черный цвет текста в выпадающем списке */\n"
"    border: 1px solid #CCCCCC; /* 1 пиксель серая сплошная граница выпадающего списка */\n"
"    selection-background-color: #7A686D; /* Синий цвет фона для выбранного элемента в списке */\n"
"    selection-color: #FFFFFF; /* Белый цвет текста для выбранного элемента в списке */\n"
"}\n"
"")
        self.comboBox_reverse_voice.setObjectName("comboBox_reverse_voice")
        self.label_3 = QtWidgets.QLabel(parent=self.frame_main_voice)
        self.label_3.setGeometry(QtCore.QRect(10, 42, 771, 20))
        self.label_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(parent=self.frame_main_voice)
        self.label_4.setGeometry(QtCore.QRect(10, 103, 771, 21))
        self.label_4.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.tabWidget.addTab(self.tab_create_voice, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 804, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        ########### Валидация для полей ввода ###########
        a = QtGui.QRegularExpressionValidator
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

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("BusStops", "BusStops"))
        self.lineEdit_city.setPlaceholderText(_translate("MainWindow", "Населенный пункт"))
        self.lineEdit_letter_route.setPlaceholderText(_translate("MainWindow", "Буква"))
        self.lineEdit_num_route.setPlaceholderText(_translate("MainWindow", "Номер маршрута"))
        self.toolButton.setText(_translate("MainWindow", "Запустить парсер"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_parser), _translate("MainWindow", "Парсер"))
        self.label.setText(_translate("MainWindow", "Выберите маршрут"))
        self.label_2.setText(_translate("MainWindow", "Выберите обратный маршрут (не обязательно)"))
        self.toolButton_create_db.setText(_translate("MainWindow", "Создать БД"))
        self.lineEdit_db_index.setPlaceholderText(_translate("MainWindow", "Начальный индекс остановок в БД"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_create_db), _translate("MainWindow", "Создание БД"))
        self.toolButton_create_voice.setText(_translate("MainWindow", "Создать озвучку для остановок"))
        self.lineEdit_token_voice.setPlaceholderText(_translate("MainWindow", "Ключ API"))
        self.label_3.setText(_translate("MainWindow", "Выберите маршрут"))
        self.label_4.setText(_translate("MainWindow", "Выберите обратный маршрут (не обязательно)"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_create_voice), _translate("MainWindow", "Создание озвучки"))

    ########################### Общие функции ###########################
    def button_handler(self):
        self.toolButton.clicked.connect(self.start_parser)
        self.toolButton_create_db.clicked.connect(self.create_db)
        self.toolButton_create_voice.clicked.connect(self.creating_voice_acting)

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
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.button_handler()
    MainWindow.show()
    sys.exit(app.exec())
