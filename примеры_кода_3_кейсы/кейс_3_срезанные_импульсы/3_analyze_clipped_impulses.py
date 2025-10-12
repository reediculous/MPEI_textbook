"""
Проводит детальный анализ срезанных импульсов: длительность среза, время нарастания
и спада, статистику по всем найденным импульсам.
"""

import numpy as np
import matplotlib.pyplot as plt
import json
import os


def analyze_clipped_impulses(filepath, max_current_value):
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
                start_idx = idx
                in_clipped_impulse = True
            elif not is_clipped and in_clipped_impulse:
                if start_idx is not None:
                    clipped_impulses.append((start_idx, idx))
                in_clipped_impulse = False

        # Анализируем каждый срезанный импульс
        analysis_results = []

        for start, end in clipped_impulses:
            # Извлекаем данные импульса
            impulse_t = t[start:end]
            impulse_i = i[start:end]

            # Основные характеристики
            duration = impulse_t[-1] - impulse_t[0]
            clipped_duration = duration
            max_amplitude = np.max(impulse_i)

            # Проверяем, действительно ли импульс срезан
            is_clipped = np.all(impulse_i == max_current_value)

            # Находим точки до и после среза для анализа формы
            pre_clip_start = max(0, start - 50)
            post_clip_end = min(len(i), end + 50)

            pre_clip_i = i[pre_clip_start:start]
            post_clip_i = i[end:post_clip_end]

            # Анализ нарастания и спада
            rise_time = None
            fall_time = None

            if len(pre_clip_i) > 0:
                # Время нарастания до среза
                rise_start = np.where(pre_clip_i < max_current_value * 0.1)[0]
                if len(rise_start) > 0:
                    rise_time = (start - pre_clip_start - rise_start[-1]) * (t[1] - t[0])

            if len(post_clip_i) > 0:
                # Время спада после среза
                fall_end = np.where(post_clip_i < max_current_value * 0.1)[0]
                if len(fall_end) > 0:
                    fall_time = fall_end[0] * (t[1] - t[0])

            result = {
                'start_idx': start,
                'end_idx': end,
                'duration_ns': duration * 1e9,
                'max_amplitude': max_amplitude,
                'is_clipped': is_clipped,
                'rise_time_ns': rise_time * 1e9 if rise_time else None,
                'fall_time_ns': fall_time * 1e9 if fall_time else None,
                'clipped_points_count': end - start
            }

            analysis_results.append(result)

        return analysis_results, clipped_impulses, t, i


# Загружаем максимальное значение тока
with open('../../примеры_кода_2_визуальный_анализ/current_limits.json', 'r') as f:
    limits = json.load(f)
    max_current = limits['max_current']

# Загружаем данные
directory = '../../sample_data'
npz_files = [f for f in os.listdir(directory) if f.endswith('.npz')]
filepath = os.path.join(directory, npz_files[0])

# Анализируем срезанные импульсы
results, clipped_impulses, t, i = analyze_clipped_impulses(filepath, max_current)

if results:
    print(f"Анализ срезанных импульсов:")
    print(f"Найдено {len(results)} срезанных импульсов")
    print()

    for i, result in enumerate(results):
        print(f"Импульс {i+1}:")
        print(f"  Позиция: {result['start_idx']} - {result['end_idx']}")
        print(f"  Длительность: {result['duration_ns']:.2f} нс")
        print(f"  Количество срезанных точек: {result['clipped_points_count']}")
        print(f"  Максимальная амплитуда: {result['max_amplitude']:.6f} А")

        if result['rise_time_ns']:
            print(f"  Время нарастания: {result['rise_time_ns']:.2f} нс")
        if result['fall_time_ns']:
            print(f"  Время спада: {result['fall_time_ns']:.2f} нс")
        print()

    # Статистика
    durations = [r['duration_ns'] for r in results]
    clipped_counts = [r['clipped_points_count'] for r in results]

    print("Статистика:")
    print(f"  Средняя длительность: {np.mean(durations):.2f} нс")
    print(f"  Медианная длительность: {np.median(durations):.2f} нс")
    print(f"  Среднее количество срезанных точек: {np.mean(clipped_counts):.1f}")
    print(f"  Максимальное количество срезанных точек: {np.max(clipped_counts)}")

else:
    print("Срезанные импульсы не найдены")
    print("Это может означать, что:")
    print("1. В данных нет импульсов, превышающих предел измерения")
    print("2. Предел измерения установлен слишком высоко")
    print("3. Импульсы имеют сложную форму без четкого плато")
