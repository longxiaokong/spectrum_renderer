import matplotlib.pyplot as plt
from numpy import ndarray, matrix

from constants import *
import numpy as np


def clip_correction(xyz: matrix, m: matrix) -> ndarray:
    rgb_tmp = np.minimum(np.maximum(np.dot(xyz, m.T), 0), 1)
    xyz_new = np.array(np.dot(rgb_tmp, m.T.I))
    alpha = np.array(np.array(xyz[:, 1] / xyz_new[:, 1]))
    rgb_new = np.minimum(np.maximum(np.diag(alpha) * rgb_tmp, 0), 1)
    return rgb_new


def sRGB_correction(colour: float) -> float:
    if colour <= 0.0031308:
        return 12.92 * colour
    else:
        return 1.055 * np.power(colour, 1 / 2.4) - 0.055


def reverse_sRGB_correction(colour: float) -> float:
    if colour <= 0.04045:
        return colour / 12.92
    else:
        return np.power((colour + 0.055) / 1.055, 2.4)


def spectrum_to_srgb(spectrum_distribution: ndarray, max_illuminant: float) -> ndarray:
    observer_data = np.array(color_matching_function[spectrum_distribution[:, 0] - 390])
    n = max(observer_data[:, 1])
    xyz = observer_data / n * max_illuminant
    srgb = clip_correction(xyz, XYZ_to_sRGB_mat)
    srgb = np.vectorize(sRGB_correction)(srgb)
    return np.array(srgb)


def get_initial_illuminant(spectrum_distribution: ndarray, max_illuminant: float) -> ndarray:
    observer_data = np.array(color_matching_function[spectrum_distribution[:, 0] - 390])
    n = max(observer_data[:, 1])
    result = observer_data[:, 1] / n * max_illuminant
    return result


spectrum = np.array([[x, 1] for x in range(390, 800)])
rgb = spectrum_to_srgb(spectrum, Illuminant)
initial_illuminant = get_initial_illuminant(spectrum, Illuminant)


def wavelength_to_srgb(wavelength: int, illuminant: float) -> ndarray:
    observer_data = np.array(color_matching_function[wavelength - 390])
    n = observer_data[1]
    xyz = observer_data / n * initial_illuminant[wavelength - 390] * illuminant
    srgb = clip_correction(np.matrix([xyz]), XYZ_to_sRGB_mat)
    srgb = np.vectorize(sRGB_correction)(srgb)
    return np.array(srgb)


def generate_color_map(wavelength: int, count: int) -> ndarray:
    illuminant_array = np.linspace(0, 1, count)
    arr = [np.array([0, 0, 0])]
    for i in range(1, count):
        arr.append(wavelength_to_srgb(wavelength, illuminant_array[int(i)])[0, :])
    return np.array(arr)


if __name__ == "__main__":
    pic = np.zeros([100, 410, 3])
    pic = pic + rgb
    plt.xticks(np.arange(390, 800 + 1, step=50))
    plt.imshow(pic, extent=(390, 800 + 1, 0, 100))
    plt.yticks([])
    plt.show()
