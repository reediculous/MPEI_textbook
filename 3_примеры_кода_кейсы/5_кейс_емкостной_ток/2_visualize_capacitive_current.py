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
    try:
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

    except Exception as e:
        print(f"Ошибка при загрузке файла {filepath}: {e}")
        return None, None, None, None


# Загружаем данные
directory = '../../sample_data'
npz_files = [f for f in os.listdir(directory) if f.endswith('.npz')]
filepath = os.path.join(directory, npz_files[0])

# Рассчитываем емкостной ток
ci, t, v, i = calculate_capacitor_current(filepath)

if ci is not None:
    # Сдвигаем время на ноль
    t_offset = t[0]
    t_shifted = t - t_offset

    # Даунсэмплинг напряжения для более четкого отображения
    downsample_factor = 1000  # Берем каждую 1000-ю точку
    v_downsampled = v[::downsample_factor]
    t_shifted_downsampled = t_shifted[::downsample_factor]

    # Визуализация емкостного тока и напряжения

    # Создаем график с двумя осями Y
    fig, ax1 = plt.subplots(figsize=(15, 6))

    # Строим график емкостного тока
    ax1.plot(t_shifted * 1e9, ci, 'k-', label='Емкостной ток', linewidth=2, alpha=1.0)
    ax1.set_xlabel('Время, нс', fontsize=20)
    ax1.set_ylabel('Емкостной ток, А', fontsize=20)
    ax1.tick_params(axis='both', labelsize=20)

    # Создаем вторую ось для напряжения
    ax2 = ax1.twinx()
    ax2.step(t_shifted_downsampled * 1e9, v_downsampled, 'k.', label='Напряжение', linewidth=3)
    ax2.set_ylabel('Напряжение, В', fontsize=20)
    ax2.tick_params(axis='y', labelsize=20)
    ax2.set_ylim(-3200, 3200)

    # Legend
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', fontsize=20)

    # Grid
    ax1.grid(True, linestyle='-', alpha=0.7, which="both")

    plt.subplots_adjust(bottom=0.15, top=0.95)
    plt.show()
else:
    print("Не удалось загрузить данные для визуализации")
