"""
Визуализирует найденные срезанные импульсы с выделением областей среза
и показом максимального значения.
"""

import numpy as np
import matplotlib.pyplot as plt
import json
import os


def find_clipped_impulses(filepath, max_current_value):
    with np.load(filepath) as data:
        raw_data = data['data']
        t = raw_data[0]
        i = raw_data[2] / 50  # Конвертируем в амперы

        # Ищем последовательные точки с максимальным значением тока
        clipped_points = i == max_current_value

        # Находим границы срезанных импульсов
        clipped_impulses = []
        in_clipped_impulse = False
        start_idx = None

        for idx, is_clipped in enumerate(clipped_points):
            if is_clipped and not in_clipped_impulse:
                # Начало срезанного импульса
                start_idx = idx
                in_clipped_impulse = True
            elif not is_clipped and in_clipped_impulse:
                # Конец срезанного импульса
                if start_idx is not None:
                    clipped_impulses.append((start_idx, idx))
                in_clipped_impulse = False

        return clipped_impulses, t, i


# Загружаем максимальное значение тока
with open('../../примеры_кода_2_визуальный_анализ/current_limits.json', 'r') as f:
    limits = json.load(f)
    max_current = limits['max_current']

# Загружаем данные
directory = '../../sample_data'
npz_files = [f for f in os.listdir(directory) if f.endswith('.npz')]
filepath = os.path.join(directory, npz_files[0])

clipped_impulses, t, i = find_clipped_impulses(filepath, max_current)

# Визуализируем срезанные импульсы
if clipped_impulses:
    print(f"Найдено {len(clipped_impulses)} срезанных импульсов")

    for i, (start, end) in enumerate(clipped_impulses[:3]):  # Показываем первые 3
        # Расширяем область для лучшей видимости
        margin = 100
        start_show = max(0, start - margin)
        end_show = min(len(t), end + margin)

        plt.figure(figsize=(12, 6))

        # Конвертируем время в наносекунды
        t_ns = t[start_show:end_show] * 1e9
        i_show = i[start_show:end_show]

        plt.plot(t_ns, i_show, 'b-', linewidth=1)

        # Выделяем срезанную область
        clipped_start_time = t[start] * 1e9
        clipped_end_time = t[end] * 1e9
        plt.axvspan(clipped_start_time, clipped_end_time, color='red', alpha=0.3,
                   label='Срезанная область')

        # Показываем максимальное значение
        plt.axhline(y=max_current, color='red', linestyle='--', alpha=0.7,
                   label=f'Максимальное значение: {max_current:.6f} А')

        plt.xlabel('Время (нс)')
        plt.ylabel('Ток (А)')
        plt.title(f'Срезанный импульс {i+1}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

        print(f"Импульс {i+1}: срезан с {start} по {end} точку")
        print(f"  Длительность среза: {(end-start) * (t[1]-t[0]) * 1e9:.2f} нс")
        print(f"  Значение тока: {max_current:.6f} А")
else:
    print("Срезанные импульсы не найдены")
