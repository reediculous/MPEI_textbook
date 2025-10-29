"""
Визуализирует найденные срезанные импульсы с выделением областей среза
и показом максимального значения.
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


def find_clipped_impulses(filepath, global_max):
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

# Загружаем данные
directory = '../../sample_data'
npz_files = [f for f in os.listdir(directory) if f.endswith('.npz')]

# Собираем все срезанные импульсы из всех файлов
all_clipped_impulses = []
all_files_data = []  # (filepath, t, i, max_current)

for npz_file in npz_files:
    filepath = os.path.join(directory, npz_file)
    temp_clipped, temp_t, temp_i, temp_max = find_clipped_impulses(filepath, global_max)

    if temp_clipped:  # Если в этом файле есть срезанные импульсы
        for impulse in temp_clipped:
            all_clipped_impulses.append((npz_file, impulse))
            all_files_data.append((filepath, temp_t, temp_i, temp_max))

if not all_clipped_impulses:
    print("Срезанные импульсы не найдены ни в одном файле")
    exit(0)

print(f"Найдено {len(all_clipped_impulses)} срезанных импульсов в {len(set(item[0] for item in all_clipped_impulses))} файлах")
print(f"Показываем первые 3 импульса:")

# Показываем первые 3 импульса из всех файлов
for impulse_idx in range(min(3, len(all_clipped_impulses))):
    file_with_impulse, (start, end) = all_clipped_impulses[impulse_idx]

    # Находим данные для этого файла
    file_data = None
    for filepath, t, i, max_current in all_files_data:
        if filepath.endswith(file_with_impulse):
            file_data = (t, i, max_current)
            break

    if file_data is None:
        continue

    t, i, max_current = file_data

    print(f"\nПоказываем импульс {impulse_idx+1} из файла: {file_with_impulse}")
    print(f"Позиция: {start} - {end} (длительность: {end-start} точек)")

    # Расширяем область для лучшей видимости
    margin = 100
    start_show = max(0, start - margin)
    end_show = min(len(t), end + margin)

    plt.figure(figsize=(15, 6))
    # Сдвигаем время на ноль и конвертируем в наносекунды
    t_offset = t[start_show]
    t_shifted = t[start_show:end_show] - t_offset
    t_ns = t_shifted * 1e9
    i_show = i[start_show:end_show]

    plt.plot(t_ns, i_show, 'k-', linewidth=3)

    # Выделяем срезанную область
    clipped_start_time = (t[start] - t_offset) * 1e9
    clipped_end_time = (t[end] - t_offset) * 1e9
    plt.axvspan(clipped_start_time, clipped_end_time, color='grey', alpha=0.3)

    # Показываем максимальное значение
    plt.axhline(y=max_current, color='grey', linestyle='--', linewidth=2, alpha=0.8,
                label=f'Уровень среза: {max_current:.4f} А', zorder=5)

    plt.xlabel('Время, нс', fontsize=20)
    plt.ylabel('Ток, А', fontsize=20)
    plt.title(f'Срезанный импульс {impulse_idx+1} (файл: {file_with_impulse})', fontsize=18)
    plt.legend(loc='lower left', fontsize=20)
    plt.grid(True, linestyle='-', alpha=0.7, which="both")
    plt.tick_params(axis='both', labelsize=20)
    plt.subplots_adjust(bottom=0.15, top=0.95)

    print(f"Отображаем график импульса {impulse_idx+1}...")
    plt.show()

    print(f"Импульс {impulse_idx+1}: срезан с {start} по {end} точку")
    print(f"  Длительность среза: {(end-start) * (t[1]-t[0]) * 1e9:.2f} нс")
    print(f"  Значение тока: {max_current:.6f} А")

    if impulse_idx < min(3, len(all_clipped_impulses)) - 1:
        print("Нажмите Enter для продолжения к следующему импульсу...")
        input()
