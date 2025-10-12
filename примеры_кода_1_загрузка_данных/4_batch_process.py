"""
Разбивает экспериментальные данные на батчи с возможностью перекрытия.
Полезно для обработки больших массивов данных по частям или для анализа
отдельных участков сигнала.
"""

import numpy as np


def split_experimental_data_into_batches(data, batch_size, overlap=0):
    batches = []
    data_length = len(data['t'])

    for i in range(0, data_length, batch_size):
        start = max(i - overlap, 0)
        end = min(i + batch_size + overlap, data_length)

        batch = {
            't': data['t'][start:end],
            'v': data['v'][start:end],
            'i': data['i'][start:end]
        }
        batches.append(batch)

    return batches

# Пример использования
# Предположим, у нас есть данные из одного файла
data_file = '../sample_data/AlN_ccurrent_50Ohm_2000V_30kHz_000001.npz'

with np.load(data_file) as data:
    raw_data = data['data']
    experimental_data = {
        't': raw_data[0],
        'v': raw_data[1],
        'i': raw_data[2]
    }

# Разбиваем на батчи
batches = split_experimental_data_into_batches(experimental_data, batch_size=1000, overlap=100)

for i, batch in enumerate(batches):
    print(f"Батч {i}: {len(batch['t'])} точек")
    # Обрабатываем каждый батч отдельно
