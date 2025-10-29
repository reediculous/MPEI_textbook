"""
Проводит детальный анализ срезанных импульсов: длительность среза, время нарастания
и спада, статистику по всем найденным импульсам.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import json


def load_global_maximum():
    """Загружает глобальный максимум из файла limits"""
    try:
        with open('../../2_примеры_кода_визуальный_анализ/current_limits.json', 'r') as f:
            limits = json.load(f)
        return limits['max_current_actual']
    except Exception as e:
        print(f"Ошибка при загрузке глобального максимума: {e}")
        return None


def analyze_clipped_impulses(filepath, global_max):
    try:
        with np.load(filepath) as data:
            raw_data = data['data']
            t = raw_data[0]
            i = raw_data[2] / 50  # Конвертируем в амперы

        # Используем глобальный максимум вместо локального
        max_current_value = global_max

        # Ищем последовательные точки с глобальным максимальным значением тока
        clipped_points = np.isclose(i, max_current_value, rtol=1e-10, atol=1e-15)

        # Находим последовательности из 3+ точек, равных глобальному максимуму
        clipped_impulses = []

        # Ищем последовательности из минимум 3 точек подряд
        min_plateau_length = 3
        current_sequence_start = None
        current_sequence_length = 0

        for idx, is_clipped in enumerate(clipped_points):
            if is_clipped:
                if current_sequence_start is None:
                    # Начало новой последовательности
                    current_sequence_start = idx
                    current_sequence_length = 1
                else:
                    # Продолжение текущей последовательности
                    current_sequence_length += 1
            else:
                if current_sequence_start is not None:
                    # Конец последовательности
                    if current_sequence_length >= min_plateau_length:
                        # Это срезанный импульс (плато достаточной длины)
                        clipped_impulses.append((current_sequence_start, idx))
                    current_sequence_start = None
                    current_sequence_length = 0

        # Проверяем, если последовательность продолжается до конца данных
        if current_sequence_start is not None and current_sequence_length >= min_plateau_length:
            clipped_impulses.append((current_sequence_start, len(i)))

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

            # Проверяем, действительно ли импульс срезан (все точки равны глобальному максимуму)
            is_clipped = np.all(np.isclose(impulse_i, max_current_value, rtol=1e-10, atol=1e-15))

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

    except Exception as e:
        print(f"Ошибка при загрузке файла {filepath}: {e}")
        return [], [], [], []


# Загружаем глобальный максимум
global_max = load_global_maximum()
if global_max is None:
    print("Не удалось загрузить глобальный максимум. Завершение работы.")
    exit(1)

print(f"Используем глобальный максимум: {global_max:.6f} А")

# Загружаем данные
directory = '../../sample_data'
npz_files = [f for f in os.listdir(directory) if f.endswith('.npz')]

# Собираем все срезанные импульсы из всех файлов
all_clipped_impulses = []
all_files_data = []  # (filepath, filename, t, i)

for npz_file in npz_files:
    filepath = os.path.join(directory, npz_file)
    temp_results, temp_clipped, temp_t, temp_i = analyze_clipped_impulses(filepath, global_max)

    if temp_clipped:  # Если в этом файле есть срезанные импульсы
        for impulse in temp_clipped:
            all_clipped_impulses.append((npz_file, impulse))
            all_files_data.append((filepath, npz_file, temp_t, temp_i))

if not all_clipped_impulses:
    print("Срезанные импульсы не найдены ни в одном файле")
    print("Это может означать, что:")
    print("1. В данных нет импульсов, превышающих предел измерения")
    print("2. Предел измерения установлен слишком высоко")
    print("3. Импульсы имеют сложную форму без четкого плато")
    exit(0)

print(f"Найдено {len(all_clipped_impulses)} срезанных импульсов в {len(set(item[0] for item in all_clipped_impulses))} файлах")

# Анализируем первые 3 импульса из всех файлов
results = []
for impulse_idx in range(min(3, len(all_clipped_impulses))):
    file_with_impulse, (start, end) = all_clipped_impulses[impulse_idx]

    # Находим данные для этого файла
    file_data = None
    for filepath, filename, t, i in all_files_data:
        if filename == file_with_impulse:
            file_data = (t, i)
            break

    if file_data is None:
        continue

    t, i = file_data

    # Извлекаем данные импульса
    impulse_t = t[start:end]
    impulse_i = i[start:end]

    # Основные характеристики
    duration = impulse_t[-1] - impulse_t[0]
    clipped_duration = duration
    max_amplitude = np.max(impulse_i)

    # Проверяем, действительно ли импульс срезан (все точки равны глобальному максимуму)
    is_clipped = np.all(np.isclose(impulse_i, global_max, rtol=1e-10, atol=1e-15))

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
        rise_start = np.where(pre_clip_i < global_max * 0.1)[0]
        if len(rise_start) > 0:
            rise_time = (start - pre_clip_start - rise_start[-1]) * (t[1] - t[0])

    if len(post_clip_i) > 0:
        # Время спада после среза
        fall_end = np.where(post_clip_i < global_max * 0.1)[0]
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

    results.append(result)

if results:
    print(f"Анализ срезанных импульсов:")
    print(f"Проанализировано {len(results)} срезанных импульсов (первые 3 из всех файлов)")
    print()

    for idx, result in enumerate(results):
        print(f"Импульс {idx+1}:")
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
