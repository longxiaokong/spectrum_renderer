import matplotlib.pyplot as plt
from numpy import ndarray, matrix

from constants import *
import numpy as np


def calc_delta_phi(d: float, wavelength: int, pos: tuple) -> float:
    L1 = np.sqrt(np.square(pos[0]) + np.square(pos[1] - d))
    L2 = np.sqrt(np.square(pos[0]) + np.square(pos[1] + d))
    return 2 * np.pi * np.abs(L2 - L1) / wavelength


def calc_illuminant(d: float, wavelength: int, pos: tuple) -> float:
    return 4 * Illuminant * np.square(np.cos(calc_delta_phi(d, wavelength, pos) / 2))


def clip_correction(xyz: matrix, m: matrix) -> ndarray:
    rgb = np.vectorize(min)(np.vectorize(max)(np.dot(xyz, m.T), 0), 1)
    xyz_new = np.array(np.dot(rgb, m.T.I))
    alpha = np.array(np.array(xyz[:, 1]) / xyz_new[:, 1])
    rgb = np.vectorize(min)(np.vectorize(max)(np.diag(alpha) * rgb, 0), 1)
    return rgb


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


def wavelength_to_srgb(wavelength: int, illuminant: float) -> ndarray:
    observer_data = np.array(color_matching_function[wavelength - 390])
    n = observer_data[1]
    xyz = observer_data / n * illuminant
    srgb = clip_correction(np.matrix([xyz]), XYZ_to_sRGB_mat)
    srgb = np.vectorize(sRGB_correction)(srgb)
    return np.array(srgb)


def spectrum_to_srgb(spectrum_distribution: ndarray, max_illuminant: float) -> ndarray:
    observer_data = np.array(color_matching_function[spectrum_distribution[:, 0] - 390])
    n = max(observer_data[:, 1])
    xyz = observer_data / n * max_illuminant
    srgb = clip_correction(xyz, XYZ_to_sRGB_mat)
    print(srgb[560 - 400, :])
    srgb = np.vectorize(sRGB_correction)(srgb)
    return np.array(srgb)


# spectrum = np.array([[x, 1] for x in range(400, 780)])
# rgb = spectrum_to_srgb(spectrum, 0.75)
# pic = np.zeros([100, 380, 3])
# pic = pic + rgb

pic = np.zeros([100, 380, 3])
pic += wavelength_to_srgb(625, 0.75)

plt.imshow(pic)
plt.yticks([])
plt.show()