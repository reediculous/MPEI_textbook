"""
Улучшенная фильтрация, которая не только определяет наличие импульсов,
но и возвращает координаты потенциальных событий для дальнейшего анализа.
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

with np.load(filepath) as data:
    raw_data = data['data']
    t = raw_data[0]
    v = raw_data[1]
    i = raw_data[2] / 50

# Разбиваем на батчи
batches = split_experimental_data_into_batches({
    't': t, 'v': v, 'i': i
}, batch_size=10000, overlap=100)

# Применение продвинутой фильтрации к батчам
for batch in batches:
    verdict, potential_events = advanced_filter(batch['i'])

    if verdict:
        print(f"Батч {batch['batch_index']}: содержит потенциальные импульсы")
        if potential_events:
            print(f"  Найдено {len(potential_events)} потенциальных событий")
    else:
        print(f"Батч {batch['batch_index']}: только шум, пропускаем")
        continue
