"""
Загружает и визуализирует один сохраненный импульс с информацией о его
характеристиках (длительность, максимальный ток).
"""

import numpy as np
import matplotlib.pyplot as plt

# Загружаем один из сохраненных импульсов
impulse_file = 'saved_impulses/impulse_0003.npz'

with np.load(impulse_file) as data:
    t = data['t']  # время в секундах
    i = data['i']  # ток в амперах

# Создаем график
plt.figure(figsize=(10, 6))
plt.plot(t / 1e9, i, 'b-', linewidth=2)  # время в микросекундах
plt.xlabel('Время (c)')
plt.ylabel('Ток (A)')
plt.title('Импульс тока')
plt.grid(True, alpha=0.3)

# Добавляем информацию о импульсе
plt.text(0.98, 0.98, f'Файл: {impulse_file}\nДлительность: {(t[-1] - t[0])*1e9:.2f} нс\nМакс. ток: {i.max()*1000:.2f} мА',
         transform=plt.gca().transAxes, verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

plt.tight_layout()
plt.show()
