import matplotlib.pyplot as plt
import numpy as np
from numpy import ndarray, matrix

from constants import *


def clip_correction(xyz: matrix) -> ndarray:
    """
    以直接截取转化后0-1范围对xyz值进行矫正

    :param xyz: 待转化xyz值
    :return: 转化完成的xyz值
    """
    rgb_tmp = np.minimum(np.maximum(np.dot(xyz, XYZ_to_sRGB_mat.T), 0), 1)
    xyz_new = np.array(np.dot(rgb_tmp, XYZ_to_sRGB_mat.T.I))
    alpha = np.array(np.array(xyz[:, 1] / xyz_new[:, 1]))
    rgb_new = np.minimum(np.maximum(np.diag(alpha) * rgb_tmp, 0), 1)
    return rgb_new


def sRGB_correction(colour: float) -> float:
    """
    sRGB值矫正

    :param colour: 待矫正sRGB值
    :return: 矫正完成的sRGB值
    """
    if colour <= 0.0031308:
        return 12.92 * colour
    else:
        return 1.055 * np.power(colour, 1 / 2.4) - 0.055


def reverse_sRGB_correction(colour: float) -> float:
    """
    sRGB矫正逆过程
    是sRGB对xyz值的转换中的第一步

    :rtype: object
    """
    if colour <= 0.04045:
        return colour / 12.92
    else:
        return np.power((colour + 0.055) / 1.055, 2.4)


def spectrum_to_sRGB(spectrum_distribution: ndarray, max_illuminant: float) -> ndarray:
    """
    将特定的光谱分布转为sRGB值

    :param spectrum_distribution: 特定波长光的相对光强组成的数组
    :param max_illuminant: 最大光强，调整光谱颜色亮度
    :return: 光谱sRGB数组
    """
    observer_data = np.array(color_matching_function[spectrum_distribution[:, 0] - 390])
    n = max(observer_data[:, 1])
    xyz = observer_data / n * max_illuminant
    srgb = clip_correction(xyz)
    srgb = np.vectorize(sRGB_correction)(srgb)
    return np.array(srgb)


def get_initial_illuminant(spectrum_distribution: ndarray, max_illuminant: float) -> ndarray:
    """
    获取特定光谱分布下一系列颜色的y值
    用于双缝干涉中定点颜色计算

    :param spectrum_distribution: 特定波长光的相对光强组成的数组
    :param max_illuminant: 最大光强，调整光谱颜色亮度
    :return: y值数组
    """
    observer_data = np.array(color_matching_function[spectrum_distribution[:, 0] - 390])
    n = max(observer_data[:, 1])
    result = observer_data[:, 1] / n * max_illuminant
    return result


spectrum = np.array([[x, 1] for x in range(390, 800)])
rgb = spectrum_to_sRGB(spectrum, Illuminant)  # 光谱色rgb值
initial_illuminant = get_initial_illuminant(spectrum, Illuminant)  # 每种颜色对应的初始亮度值


def wavelength_to_sRGB(wavelength: int, illuminant: float) -> ndarray:
    """
    将特定波长和光强的光转为sRGB值

    :param wavelength: 波长，单位纳米
    :param illuminant: 光强，一般位于[0,1]
    :return: 光对应的sRGB数组
    """
    observer_data = np.array(color_matching_function[wavelength - 390])
    n = observer_data[1]
    xyz = observer_data / n * initial_illuminant[wavelength - 390] * illuminant
    srgb = clip_correction(np.matrix([xyz]))
    srgb = np.vectorize(sRGB_correction)(srgb)
    return np.array(srgb)


def generate_color_map(wavelength: int, count: int) -> ndarray:
    """
    生成颜色映射
    对于绘制图像有一定速度优化

    :param wavelength: 波长，单位纳米
    :param count: 细分度，值越大图像颜色越细腻
    :return: 颜色映射数组，请自行用ListedColormap转换
    """
    illuminant_array = np.linspace(0, 1, count)
    arr = [np.array([0, 0, 0])]
    for i in range(1, count):
        arr.append(wavelength_to_sRGB(wavelength, illuminant_array[int(i)])[0, :])
    return np.array(arr)


if __name__ == "__main__":
    pic = np.zeros([100, 410, 3])
    pic = pic + rgb
    plt.xticks(np.arange(390, 800 + 1, step=50))
    plt.imshow(pic, extent=(390, 800 + 1, 0, 100))
    plt.yticks([])
    plt.show()
