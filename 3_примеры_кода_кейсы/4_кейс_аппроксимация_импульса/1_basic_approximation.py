"""
Аппроксимирует импульс тока аналитической моделью с использованием сигмоидальной
и экспоненциальной функций. Использует метод наименьших квадратов для подбора параметров.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


try:
    # Загружаем данные импульса
    impulse_data = np.load('../кейс_1_сбор_тестового_набора/saved_impulses/impulse_0003.npz')
    t_impulse = impulse_data['t']
    i_impulse = impulse_data['i']

    # Находим время пика из исходных данных
    t_peak = t_impulse[np.argmax(i_impulse)]

    # Определяем аналитическую модель импульса
    def impulse_model(t, A, k, lambda_):
        """
        Аналитическая модель импульса тока
        A - амплитуда
        k - параметр затухания
        lambda_ - параметр экспоненты
        """
        sigmoid = np.exp(-k * (t - t_peak))
        exponential = np.where(t > t_peak, np.exp(-lambda_ * (t - t_peak)), 1)
        return A * sigmoid * exponential

    # Начальные параметры для аппроксимации
    initial_guess = [np.max(i_impulse), 5.0, 1.0]

    # Выполняем аппроксимацию
    try:
        popt, pcov = curve_fit(impulse_model, t_impulse, i_impulse, p0=initial_guess, maxfev=40000)

        # Создаем аппроксимированную кривую
        i_fitted = impulse_model(t_impulse, *popt)
        print(f"Параметры аппроксимации: A={popt[0]:.6f}, k={popt[1]:.6f}, λ={popt[2]:.6f}")

        # Сдвигаем время на ноль
        t_offset = t_impulse[0]
        t_impulse_shifted = t_impulse - t_offset

        # Визуализируем результат
        plt.figure(figsize=(15, 6))
        plt.rcParams['figure.dpi'] = 400
        plt.plot(t_impulse_shifted * 1e9, i_impulse, 'k-', linewidth=3, label='Исходный импульс')
        plt.plot(t_impulse_shifted * 1e9, i_fitted, 'k:', linewidth=2, label='Аппроксимация', alpha=1.0)
        plt.xlabel('Время, нс', fontsize=20)
        plt.ylabel('Ток, А', fontsize=20)
        plt.title('Аппроксимация импульса аналитической моделью', fontsize=18)
        plt.legend(loc='upper left', fontsize=20)
        plt.grid(True, linestyle='-', alpha=0.7, which="both")
        plt.tick_params(axis='both', labelsize=20)
        plt.subplots_adjust(bottom=0.15, top=0.95)
        plt.show()

    except RuntimeError as e:
        print(f"Ошибка аппроксимации: {e}")

except Exception as e:
    print(f"Ошибка при загрузке файла импульса: {e}")
