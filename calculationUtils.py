import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtCore import pyqtSignal
from matplotlib.colors import ListedColormap

from colourUtils import generate_color_map
from constants import Illuminant


def calc_phase_difference(spacing: float, wavelength: int, pos: tuple) -> float:
    L1 = np.sqrt(np.square(pos[0]) + np.square(pos[1] - spacing / 2))
    L2 = np.sqrt(np.square(pos[0]) + np.square(pos[1] + spacing / 2))
    return 2 * np.pi * np.abs(L2 - L1) / (wavelength * (10 ** -9))


def calc_illuminant(spacing: float, wavelength: int, pos: tuple) -> float:
    """
    计算特定位置双缝干涉后光强

    :param spacing: 双缝间距，单位米
    :param wavelength: 光波长，单位纳米
    :param pos: 坐标，单为米
    :return: 浮点数，4以下的光强
    """
    return 4 * Illuminant * np.square(np.cos(calc_phase_difference(spacing, wavelength, pos) / 2))


def render_screen(spacing: float, distance: float, height: int, half_width: int, wavelength: int) -> np.ndarray:
    """
    渲染距离双缝平面一定距离的平行平面上的干涉条纹

    :param spacing: 双缝间距，单位米
    :param distance: 光屏与双缝间距离，单位米
    :param height: 渲染高度，单位毫米
    :param half_width: 渲染宽度的一半，单位0.01毫米
    :param wavelength: 光波长，单位纳米
    :return: 渲染好的亮度ndarray
    """
    pic = np.zeros([height + 1, half_width * 2 + 1])
    x = distance
    for y in range(0, half_width + 1):
        ty = y + half_width
        illuminant = calc_illuminant(spacing, wavelength, (x, y * (10 ** -5))) / 4
        pic[:, ty] = illuminant
        pic[:, -ty] = illuminant
    return pic


def render_horizontal_plane(spacing: float, distance: float, half_width: int, wavelength: int,
                            progress_bar_handler: pyqtSignal = None) -> np.ndarray:
    """
    渲染双缝平面前一定区域的水平面

    :param progress_bar_handler:
    :param spacing: 双缝间距，单位为米
    :param distance: 距双缝平面最远距离，单位米
    :param half_width: 渲染宽度的一半，单位0.01毫米
    :param wavelength: 光波长，单位纳米
    :return: 渲染好的ndarry
    """
    distance = int(distance * (10 ** 3))
    pic = np.zeros([distance + 1, 2 * half_width + 1])
    tot = (distance - 1) * half_width
    cnt = 0
    for tx in range(0, distance):
        for ty in range(0, half_width + 1):
            illuminant = calc_illuminant(spacing, wavelength, (tx * (10 ** -3), ty * (10 ** -5))) / 4
            # colour = wavelength_to_srgb(wavelength, illuminant)
            pic[tx, half_width + ty] = illuminant
            pic[tx, half_width - ty] = illuminant
            cnt += 1
            if progress_bar_handler is not None:
                progress_bar_handler.emit(cnt / tot * 100)
    return pic


if __name__ == "__main__":
    l = 0.6
    d = 0.2 * (10 ** -3)
    wavelength = 520
    half_width = 500
    height = 200
    newCmap = ListedColormap(generate_color_map(wavelength, 100))
    fig = plt.figure()
    screen_data = render_screen(d, l, height, half_width, wavelength)
    horizontal_data = render_horizontal_plane(d, l, half_width, wavelength)
    print(horizontal_data)
    fig.imshow(horizontal_data, extent=(-half_width, half_width, 0, l * (10 ** 3)),
               cmap=newCmap)
    fig.yticks([])
    fig.xticks(np.arange(-half_width, half_width + 1, step=half_width // 5))
    # plt.xlim(-half_width, half_width + 1)
    # plt.imshow(screen_data, extent=(-half_width, half_width, 0, height), cmap=newCmap)
    # plt.yticks([])
    # plt.xticks(np.arange(-half_width, half_width + 1, step=half_width // 5))
    plt.show()
