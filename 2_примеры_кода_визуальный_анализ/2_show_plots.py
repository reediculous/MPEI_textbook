"""
Создает графики тока и напряжения с едиными осями для всех файлов.
Разбивает данные на временные промежутки и показывает их с правильным масштабированием
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

            # Разбиваем данные на временные промежутки
            batches = split_experimental_data_into_batches({
                't': t, 'v': v, 'i': i
            }, batch_size=10000, overlap=100)

            # Визуализируем каждый временной промежуток
            for batch in batches:
                fig, ax1 = plt.subplots(figsize=(15, 6))
                fig.dpi = 400

                # Сдвигаем время на ноль и конвертируем в наносекунды
                t_batch = batch['t'] - batch['t'][0]
                t_ns = t_batch * 1e9

                # Строим график тока
                ax1.step(t_ns, batch['i'], 'k-', linewidth=3, label='Ток')
                ax1.set_xlabel('Время, нс', fontsize=20)
                ax1.set_ylabel('Ток, А', fontsize=20)
                ax1.tick_params(axis='both', labelsize=20)
                ax1.set_ylim(min_current, max_current)

                # Создаем вторую ось для напряжения
                ax2 = ax1.twinx()
                ax2.step(t_ns, batch['v'], 'k:', linewidth=2, label='Напряжение', alpha=1.0)
                ax2.set_ylabel('Напряжение, В', fontsize=20)
                ax2.tick_params(axis='y', labelsize=20)
                ax2.set_ylim(-3200, 3200)

                # Legend
                lines_1, labels_1 = ax1.get_legend_handles_labels()
                lines_2, labels_2 = ax2.get_legend_handles_labels()
                ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', fontsize=20)

                # Grid
                ax1.grid(True, linestyle='-', alpha=0.7, which="both")

                plt.subplots_adjust(bottom=0.15, top=0.95)
                plt.show()

    except Exception as e:
        print(f"Ошибка при обработке файла {filename}: {e}")
        continue
