"""
Визуализирует рассчитанный емкостной ток вместе с напряжением на двух осях Y
для сравнения фазовых соотношений.
"""

import numpy as np
import matplotlib.pyplot as plt
import os


def calculate_capacitor_current(filepath):
    """
    Рассчитывает емкостной ток для файла
    """
    with np.load(filepath) as data:
        raw_data = data['data']
        t = raw_data[0]
        v = raw_data[1]
        i = raw_data[2] / 50  # Конвертируем в амперы

        # Параметры емкостного тока (из расчета)
        capacitor_current_amp = 1.478774e-04  # Амплитуда емкостного тока
        capacitor_current_delay = -7.068553539992742e-06  # Задержка в секундах

        # Находим индекс пика напряжения
        v_peak_idx = np.argmax(v)
        t_v_peak = t[v_peak_idx]
        # Находим индекс пика тока (сдвинут относительно напряжения)
        t_c_peak = t_v_peak + capacitor_current_delay

        # Параметры синусоиды
        omega = 2 * np.pi * 30000  # Угловая частота, рад/с

        # Фаза синуса: пик синуса должен быть в t_c_peak
        # sin(ω t + φ) достигает максимума при ω t + φ = π/2
        # Отсюда: φ = π/2 - ω * t_c_peak
        phi = np.pi/2 - omega * t_c_peak

        # Рассчитываем емкостной ток
        capacitor_current = capacitor_current_amp * np.sin(omega * t + phi)
        return capacitor_current, t, v, i


# Загружаем данные
directory = '../../sample_data'
npz_files = [f for f in os.listdir(directory) if f.endswith('.npz')]
filepath = os.path.join(directory, npz_files[0])

# Рассчитываем емкостной ток
ci, t, v, i = calculate_capacitor_current(filepath)

# Визуализация емкостного тока и напряжения

# Создаем график с двумя осями Y
fig, ax1 = plt.subplots(figsize=(12, 6))

# Строим график емкостного тока
ax1.plot(t * 1e9, ci, 'b-', label='Емкостной ток', linewidth=1.5)
ax1.set_xlabel('Время (нс)')
ax1.set_ylabel('Емкостной ток (А)', color='b')
ax1.tick_params(axis='y', labelcolor='b')

# Создаем вторую ось для напряжения
ax2 = ax1.twinx()
ax2.step(t * 1e9, v, 'r-', label='Напряжение', linewidth=1, alpha=0.7)
ax2.set_ylabel('Напряжение (В)', color='r')
ax2.tick_params(axis='y', labelcolor='r')
ax2.set_ylim(-2600, 2600)

plt.title('Емкостной ток и напряжение')
plt.tight_layout()
plt.show()
