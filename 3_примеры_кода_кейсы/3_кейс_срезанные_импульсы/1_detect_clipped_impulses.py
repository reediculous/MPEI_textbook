"""
Находит импульсы, которые достигли максимального значения измерительной системы
(срезаны). Сохраняет такие импульсы в отдельные файлы.
"""

import numpy as np
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


def find_and_save_clipped_impulses(filepath, global_max):
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

        print(f"Найдено {len(clipped_impulses)} срезанных импульсов в файле {os.path.basename(filepath)}")
        return clipped_impulses, t, i, max_current_value

    except Exception as e:
        print(f"Ошибка при загрузке файла {filepath}: {e}")
        return [], [], [], 0


# Загружаем глобальный максимум
global_max = load_global_maximum()
if global_max is None:
    print("Не удалось загрузить глобальный максимум. Завершение работы.")
    exit(1)

print(f"Используем глобальный максимум: {global_max:.6f} А")

# Пример использования
directory = '../../sample_data'
npz_files = [f for f in os.listdir(directory) if f.endswith('.npz')]

# Собираем все срезанные импульсы из всех файлов
all_clipped_impulses = []
all_files_data = []  # (filepath, filename, t, i)

for npz_file in npz_files:
    filepath = os.path.join(directory, npz_file)
    temp_clipped, temp_t, temp_i, temp_max = find_and_save_clipped_impulses(filepath, global_max)

    if temp_clipped:  # Если в этом файле есть срезанные импульсы
        for impulse in temp_clipped:
            all_clipped_impulses.append((npz_file, impulse))
            all_files_data.append((filepath, npz_file, temp_t, temp_i))

if not all_clipped_impulses:
    print("Срезанные импульсы не найдены ни в одном файле")
    exit(0)

print(f"Найдено {len(all_clipped_impulses)} срезанных импульсов в {len(set(item[0] for item in all_clipped_impulses))} файлах")
print(f"Сохраняем первые 3 импульса:")

# Создаем директорию для сохранения, если её нет
os.makedirs('clipped_impulses', exist_ok=True)

# Сохраняем первые 3 импульса из всех файлов
impulse_count = 0
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

    print(f"Сохраняем импульс {impulse_idx+1} из файла: {file_with_impulse}")
    print(f"Позиция: {start} - {end} (длительность: {end-start} точек)")

    impulse_data = {
        't': t[start:end],
        'i': i[start:end],
        'source_file': file_with_impulse,
        'position': (start, end)
    }

    filename = f"clipped_impulses/clipped_impulse_{impulse_count:04d}.npz"
    np.savez(filename, **impulse_data)
    impulse_count += 1

print(f"\nВсего сохранено {impulse_count} срезанных импульсов (первые 3 из всех файлов)")
