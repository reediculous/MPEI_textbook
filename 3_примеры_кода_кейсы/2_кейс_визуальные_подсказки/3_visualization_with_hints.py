"""
Визуализирует данные с выделением областей, где обнаружены потенциальные импульсы.
Показывает подсказки для анализа сигналов.
"""

import numpy as np
import matplotlib.pyplot as plt
import os


def split_experimental_data_into_batches(data, batch_size, overlap=0):
    batches = []
    data_length = len(data['t'])

    for i in range(0, data_length, batch_size):
        start = max(i - overlap, 0)
        end = min(i + batch_size + overlap, data_length)

        batch = {
            't': data['t'][start:end],
            'v': data['v'][start:end],
            'i': data['i'][start:end],
            'batch_index': len(batches)
        }
        batches.append(batch)

    return batches


def advanced_filter(batch_data):
    data = np.asarray(batch_data)
    data_shifted = data - np.mean(data)

    # Параметры
    chunk_size = 50
    overlap = 14
    q_threshold = 0.007515
    h_threshold = 0.025

    # Проверяем по амплитуде
    if np.max(data_shifted) > h_threshold or np.min(data_shifted) < -h_threshold:
        return True, []

    # Проверяем по площади в сегментах и собираем потенциальные события
    potential_events = []
    step = chunk_size - overlap
    for start in range(0, len(data_shifted) - chunk_size + 1, step):
        chunk = data_shifted[start:start + chunk_size]
        area = np.trapz(chunk)
        if abs(area) > q_threshold:
            potential_events.append([start, start + chunk_size])
            return True, potential_events

    return False, []


directory = '../../sample_data'

# Загружаем данные
npz_files = [f for f in os.listdir(directory) if f.endswith('.npz')]
filepath = os.path.join(directory, npz_files[0])

try:
    with np.load(filepath) as data:
        raw_data = data['data']
        t = raw_data[0]
        v = raw_data[1]
        i = raw_data[2] / 50

    # Разбиваем на временные промежутки
    batches = split_experimental_data_into_batches({
        't': t, 'v': v, 'i': i
    }, batch_size=1000, overlap=100)

    # Применение фильтрации с визуализацией
    for batch in batches:
        verdict, potential_events = advanced_filter(batch['i'])

        if verdict:
            print(f"Временной промежуток номер {batch['batch_index']}: содержит потенциальные импульсы")

            # Визуализируем временной промежуток с подсказками
            plt.figure(figsize=(15, 6))
            plt.rcParams['figure.dpi'] = 400

            # Сдвигаем время на ноль
            t_batch = batch['t'] - batch['t'][0]

            plt.plot(t_batch * 1e9, batch['i'], 'k-', linewidth=3)

            # Отмечаем потенциальные события
            if potential_events:
                for start_idx, end_idx in potential_events:
                    start_time = t_batch[start_idx] * 1e9
                    end_time = t_batch[end_idx] * 1e9
                    plt.axvspan(start_time, end_time, color='black', alpha=0.3,
                               label='Потенциальные события')

            plt.xlabel('Время, нс', fontsize=20)
            plt.ylabel('Ток, А', fontsize=20)
            plt.ylim(-0.004, 0.009) # Задаем пределы тока
            plt.title(f'Временной промежуток номер {batch["batch_index"]} с подсказками', fontsize=18)
            plt.legend(loc='upper left', fontsize=20)
            plt.tick_params(axis='both', labelsize=20)
            plt.grid(True, linestyle='-', alpha=0.7, which="both")
            plt.subplots_adjust(bottom=0.15, top=0.95)
            plt.show()
        else:
            print(f"Временной промежуток номер {batch['batch_index']}: только шум, пропускаем")
            continue

except Exception as e:
    print(f"Ошибка при загрузке файла {filepath}: {e}")
