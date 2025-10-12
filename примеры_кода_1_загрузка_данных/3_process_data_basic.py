"""
Обрабатывает все NPZ файлы в директории, извлекает параметры из имен файлов и
загружает данные. Включает обработку ошибок и базовую информацию о каждом файле.
"""

import os
import numpy as np
import re

def process_experimental_files(directory):
    # Получаем список всех .npz файлов и сортируем их
    npz_files = [f for f in os.listdir(directory) if f.endswith('.npz')]

    for filename in npz_files:
        filepath = os.path.join(directory, filename)
        print(f"Обрабатываем файл: {filename}")

        # Извлекаем параметры из имени файла
        match = re.search(r'(\d+)Ohm_(\d+)V_(\d+)kHz', filename)
        if not match:
            print(f"Пропускаем файл {filename} - неправильное имя")
            continue

        resistance = int(match.group(1))
        voltage = int(match.group(2))
        frequency = int(match.group(3))

        try:
            # Загружаем данные для этого файла
            with np.load(filepath) as data:
                raw_data = data['data']
                t = raw_data[0]  # время
                v = raw_data[1]  # напряжение
                i = raw_data[2]  # ток

                print(f"  Параметры: {resistance}Ом, {voltage}В, {frequency}кГц")
                print(f"  Размер данных: {len(t)} точек")
                # Здесь можно добавить вашу обработку данных

        # Этот блок обработает любые ошибки
        except Exception as e:
            print(f"Ошибка при загрузке файла {filename}: {e}")
            continue

# Использование
process_experimental_files('../sample_data')
