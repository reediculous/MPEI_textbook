"""
Находит импульсы, которые достигли максимального значения измерительной системы
(срезаны). Сохраняет такие импульсы в отдельные файлы.
"""

import numpy as np
import json
import os


def find_and_save_clipped_impulses(filepath, max_current_value):
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

        # Сохраняем найденные срезанные импульсы
        impulse_count = 0
        for start, end in clipped_impulses:
            impulse_data = {
                't': t[start:end],
                'i': i[start:end]
            }

            filename = f"clipped_impulses/clipped_impulse_{impulse_count:04d}.npz"
            np.savez(filename, **impulse_data)
            impulse_count += 1

        print(f"Найдено и сохранено {impulse_count} срезанных импульсов")
        return impulse_count


# Загружаем максимальное значение тока из сохраненного файла
with open('../../примеры_кода_2_визуальный_анализ/current_limits.json', 'r') as f:
    limits = json.load(f)
    max_current = limits['max_current']

# Пример использования
directory = '../../sample_data'
npz_files = [f for f in os.listdir(directory) if f.endswith('.npz')]
for npz_file in npz_files:
    filepath = os.path.join(directory, npz_file)
    clipped_count = find_and_save_clipped_impulses(filepath, max_current)
