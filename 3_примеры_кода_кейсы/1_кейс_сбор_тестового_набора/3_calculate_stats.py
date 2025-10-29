"""
Рассчитывает основные характеристики импульса: заряд (интеграл тока),
длительность и амплитуду. Использует численное интегрирование.
"""

import numpy as np
from scipy.integrate import trapezoid

# Загружаем один из сохраненных импульсов
impulse_file = 'saved_impulses/impulse_0002.npz'

try:
    with np.load(impulse_file) as data:
        t = data['t']  # время в секундах
        i = data['i']  # ток в амперах

    # Рассчитываем основные характеристики импульса
    duration = t[-1] - t[0]  # Длительность в секундах
    amplitude = np.max(np.abs(i))  # Амплитуда по модулю

    # Рассчитываем заряд как интеграл тока по времени
    charge = trapezoid(i, t)

    print(f"Заряд, перенесенный импульсом: {charge:.12f} Кл")
    print(f"Заряд в пикокулонах: {charge*1e12:.2f} пКл")
    print(f"Длительность импульса: {duration*1e9:.2f} нс")
    print(f"Амплитуда импульса: {amplitude:.6f} А")

except Exception as e:
    print(f"Ошибка при загрузке файла {impulse_file}: {e}")
