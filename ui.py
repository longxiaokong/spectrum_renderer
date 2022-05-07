# coding:utf-8
import os.path
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QHBoxLayout, QSlider, QVBoxLayout, QLabel, QRadioButton, QButtonGroup, QProgressBar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.colors import ListedColormap
from numpy import ndarray

from calculationUtils import render_horizontal_plane, render_screen
from colourUtils import generate_color_map

matplotlib.use('Qt5Agg')


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class horizontal_screen_thread(QThread):
    _signal = pyqtSignal(ndarray, float, int, ListedColormap)

    def __init__(self, d: float, l: float, half_width: int, wavelength: int,
                 new_cmap: ListedColormap, progress_bar_handler: pyqtSignal):
        super().__init__()
        self.d: float = d
        self.l: float = l
        self.new_cmap = new_cmap
        self.half_width: int = half_width
        self.wavelength: int = wavelength
        self.progress_bar_handler = progress_bar_handler

    def run(self) -> None:
        horizontal_data = render_horizontal_plane(self.d, self.l, self.half_width, self.wavelength,
                                                  self.progress_bar_handler)
        self._signal.emit(horizontal_data, self.l, self.half_width, self.new_cmap)


class My_Main_window(QtWidgets.QDialog):
    progress_signal = pyqtSignal(float)

    def __init__(self, parent=None):
        # 父类初始化方法
        super(My_Main_window, self).__init__(parent)

        # 几个QWidgets
        self.setWindowIcon(QIcon(get_resource_path('icon.png')))
        self.horizontal_screen_thread = None
        self.setWindowTitle("双缝干涉模拟")
        self.screen_figure = plt.figure()
        self.horizontal_figure = plt.figure()
        self.screen_canvas = FigureCanvas(self.screen_figure)
        self.horizontal_canvas = FigureCanvas(self.horizontal_figure)
        self.wavelength_slider = QSlider(Qt.Horizontal, self)
        self.wavelength_slider.setMinimum(400)
        self.wavelength_slider.setMaximum(800)
        self.wavelength_slider.setValue(520)
        self.wavelength_slider.setSingleStep(1)
        self.distance_slider = QSlider(Qt.Horizontal, self)
        self.distance_slider.setMinimum(50)
        self.distance_slider.setMaximum(100)
        self.distance_slider.setValue(50)
        self.distance_slider.setSingleStep(5)
        self.spacing = self.distance = self.wavelength = 0
        self.spectrum_label = QLabel(self)
        self.spectrum_label.setPixmap(QPixmap(get_resource_path('spectrum.png')))
        self.spacing_choice_20 = QRadioButton('0.20mm', self)
        self.spacing_choice_25 = QRadioButton('0.25mm', self)
        self.spacing_choice = QButtonGroup(self)
        self.spacing_choice.addButton(self.spacing_choice_20, 20)
        self.spacing_choice.addButton(self.spacing_choice_25, 25)
        self.spacing_choice_20.setChecked(True)
        self.spacing_label = QLabel("双缝间距".format(self.spacing * (10 ** -3)))
        self.spacing_label.setAlignment(Qt.AlignCenter)
        self.wavelength_label = QLabel("波长: {0}nm".format(self.wavelength_slider.value()), self)
        self.wavelength_label.setAlignment(Qt.AlignCenter)
        self.distance_label = QLabel("距离: {0}cm".format(self.distance_slider.value()), self)
        self.distance_label.setAlignment(Qt.AlignCenter)
        self.render_label = QLabel("渲染进度".format(self.distance_slider.value()), self)
        self.render_label.setAlignment(Qt.AlignCenter)
        self.render_progress = QProgressBar()

        self.wavelength_slider.sliderReleased.connect(self.plot_)
        self.wavelength_slider.valueChanged.connect(self.update_wavelength_value)
        self.distance_slider.sliderReleased.connect(self.plot_)
        self.distance_slider.valueChanged.connect(self.update_distance_value)
        self.spacing_choice.buttonClicked.connect(self.plot_)
        self.progress_signal.connect(self.render_progress.setValue)
        # 设置布局
        choice_horizontal_box = QHBoxLayout()
        choice_horizontal_box.addStretch(1)
        choice_horizontal_box.addWidget(self.spacing_choice_20)
        choice_horizontal_box.addStretch(1)
        choice_horizontal_box.addWidget(self.spacing_choice_25)
        choice_horizontal_box.addStretch(1)

        adjusting_vertical_box = QVBoxLayout()
        adjusting_vertical_box.addStretch(1)
        adjusting_vertical_box.addWidget(self.render_label)
        adjusting_vertical_box.addWidget(self.render_progress)
        adjusting_vertical_box.addStretch(1)
        adjusting_vertical_box.addWidget(self.spectrum_label)
        adjusting_vertical_box.addStretch(1)
        adjusting_vertical_box.addWidget(self.wavelength_label)
        adjusting_vertical_box.addStretch(1)
        adjusting_vertical_box.addWidget(self.wavelength_slider)
        adjusting_vertical_box.addStretch(1)
        adjusting_vertical_box.addWidget(self.distance_label)
        adjusting_vertical_box.addStretch(1)
        adjusting_vertical_box.addWidget(self.distance_slider)
        adjusting_vertical_box.addStretch(1)
        adjusting_vertical_box.addWidget(self.spacing_label)
        adjusting_vertical_box.addStretch(1)
        adjusting_vertical_box.addLayout(choice_horizontal_box)
        adjusting_vertical_box.addStretch(1)

        canvas_vertical_box = QVBoxLayout()
        canvas_vertical_box.addStretch(1)
        canvas_vertical_box.addWidget(self.screen_canvas)
        canvas_vertical_box.addStretch(1)
        canvas_vertical_box.addWidget(self.horizontal_canvas)
        canvas_vertical_box.addStretch(1)

        main_horizontal_box = QHBoxLayout()
        main_horizontal_box.addStretch(1)
        main_horizontal_box.addLayout(adjusting_vertical_box)
        main_horizontal_box.addStretch(1)
        main_horizontal_box.addLayout(canvas_vertical_box)
        main_horizontal_box.addStretch(1)
        self.setLayout(main_horizontal_box)
        self.plot_()

    def lock_all_interactions(self):
        self.distance_slider.setDisabled(True)
        self.wavelength_slider.setDisabled(True)
        self.spacing_choice_20.setDisabled(True)
        self.spacing_choice_25.setDisabled(True)

    def unlock_all_interactions(self):
        self.distance_slider.setDisabled(False)
        self.wavelength_slider.setDisabled(False)
        self.spacing_choice_20.setDisabled(False)
        self.spacing_choice_25.setDisabled(False)

    def on_render_done(self, horizontal_data, l, half_width, new_cmap):
        plt.figure(num=self.horizontal_figure.number)
        plt.imshow(horizontal_data.T, extent=(0, l * (10 ** 3), -half_width, half_width), origin='lower', cmap=new_cmap)
        plt.yticks(np.arange(-half_width, half_width + 1, step=half_width // 5))
        plt.xticks([])
        self.horizontal_canvas.draw()
        self.unlock_all_interactions()

    # 连接的绘制的方法
    def plot_(self):
        if (self.wavelength_slider.value() == self.wavelength) and (
                self.distance_slider.value() * (10 ** -2) == self.distance) and (
                self.spacing_choice.checkedId() * (10 ** -5) == self.spacing):
            return
        self.lock_all_interactions()
        self.wavelength = self.wavelength_slider.value()
        self.spacing = self.spacing_choice.checkedId() * (10 ** -5)
        self.distance = self.distance_slider.value() * (10 ** -2)
        l = self.distance
        d = self.spacing
        wavelength = self.wavelength
        half_width = 500
        height = 200
        new_cmap = ListedColormap(generate_color_map(wavelength, 100))
        plt.figure(num=self.screen_figure.number)
        screen_data = render_screen(d, l, height, half_width, wavelength)
        plt.imshow(screen_data, extent=(-half_width, half_width, 0, height), cmap=new_cmap)
        plt.yticks([])
        plt.xticks(np.arange(-half_width, half_width + 1, step=half_width // 5))
        self.screen_canvas.draw()
        self.horizontal_screen_thread = horizontal_screen_thread(d, l, half_width, wavelength, new_cmap,
                                                                 self.progress_signal)
        self.horizontal_screen_thread._signal.connect(self.on_render_done)
        self.horizontal_screen_thread.start()

    def update_wavelength_value(self):
        self.wavelength_label.setText("波长: {0}nm".format(self.wavelength_slider.value()))

    def update_distance_value(self):
        self.distance_label.setText("距离: {0}cm".format(self.distance_slider.value()))
