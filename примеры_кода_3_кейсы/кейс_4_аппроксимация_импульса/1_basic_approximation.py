"""
Аппроксимирует импульс тока аналитической моделью с использованием сигмоидальной
и экспоненциальной функций. Использует метод наименьших квадратов для подбора параметров.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


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

    # Визуализируем результат
    plt.figure(figsize=(12, 6))
    plt.plot(t_impulse * 1e9, i_impulse, 'b-', linewidth=1, label='Исходный импульс')
    plt.plot(t_impulse * 1e9, i_fitted, 'r--', linewidth=2, label='Аппроксимация')
    plt.xlabel('Время (нс)')
    plt.ylabel('Ток (А)')
    plt.title('Аппроксимация импульса аналитической моделью')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

except RuntimeError as e:
    print(f"Ошибка аппроксимации: {e}")
