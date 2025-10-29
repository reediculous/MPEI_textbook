"""
Загружает и визуализирует один сохраненный импульс с информацией о его
характеристиках (длительность, максимальный ток).
"""

import numpy as np
import matplotlib.pyplot as plt

# Загружаем один из сохраненных импульсов
impulse_file = 'saved_impulses/impulse_0003.npz'

try:
    with np.load(impulse_file) as data:
        t = data['t']  # время в секундах
        i = data['i']  # ток в амперах

    # Сдвигаем время на ноль
    t_offset = t[0]
    t_shifted = t - t_offset

    # Создаем график
    plt.figure(figsize=(15, 6))
    plt.rcParams['figure.dpi'] = 400
    plt.plot(t_shifted * 1e9, i, 'k-', linewidth=3)  # время в наносекундах
    plt.xlabel('Время, нс', fontsize=20)
    plt.ylabel('Ток, А', fontsize=20)
    plt.title('Импульс тока', fontsize=18)
    plt.grid(True, linestyle='-', alpha=0.7, which="both")
    plt.tick_params(axis='both', labelsize=20)

    # Добавляем информацию о импульсе
    plt.text(0.98, 0.98, f'Файл: {impulse_file}\nДлительность: {(t[-1] - t[0])*1e9:.2f} нс\nМакс. ток: {i.max()*1000:.2f} мА',
            transform=plt.gca().transAxes, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7), fontsize=16)

    plt.subplots_adjust(bottom=0.15, top=0.95)
    plt.show()

except Exception as e:
    print(f"Ошибка при загрузке файла {impulse_file}: {e}")
