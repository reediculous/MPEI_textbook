"""
Создает графики тока и напряжения с едиными осями для всех файлов.
Разбивает данные на батчи и показывает их с правильным масштабированием
времени и тока.
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt


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


directory = '../sample_data'

# Загружаем заранее определенные пределы тока
with open('current_limits.json', 'r') as f:
    limits = json.load(f)
    min_current = limits['min_current']
    max_current = limits['max_current']

# Получаем список файлов и сортируем их
npz_files = [f for f in os.listdir(directory) if f.endswith('.npz')]
npz_files.sort()

for filename in npz_files:
    filepath = os.path.join(directory, filename)
    try:
        with np.load(filepath) as data:
            raw_data = data['data']
            t = raw_data[0]
            v = raw_data[1]
            i = raw_data[2] / 50  # Конвертируем в амперы

            # Разбиваем данные на батчи
            batches = split_experimental_data_into_batches({
                't': t, 'v': v, 'i': i
            }, batch_size=10000, overlap=100)

            # Визуализируем каждый батч
            for batch in batches:
                fig, ax1 = plt.subplots(figsize=(12, 6))

                # Конвертируем время в наносекунды
                t_ns = batch['t'] * 1e9

                # Строим график тока
                ax1.plot(t_ns, batch['i'], 'b-', linewidth=0.8)
                ax1.set_xlabel('Время (нс)')
                ax1.set_ylabel('Ток (А)', color='b')
                ax1.tick_params(axis='y', labelcolor='b')
                ax1.set_ylim(min_current, max_current)

                # Создаем вторую ось для напряжения
                ax2 = ax1.twinx()
                ax2.step(t_ns, batch['v'], 'r-', linewidth=1, alpha=0.7)
                ax2.set_ylabel('Напряжение (В)', color='r')
                ax2.tick_params(axis='y', labelcolor='r')
                ax2.set_ylim(-2600, 2600)

                plt.title(f'Файл: {filename}')
                plt.tight_layout()
                plt.show()

    except Exception as e:
        print(f"Ошибка при обработке файла {filename}: {e}")
        continue
