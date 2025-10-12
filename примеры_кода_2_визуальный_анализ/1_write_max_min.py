"""
Находит максимальные и минимальные значения тока по всему датасету и сохраняет их
в JSON файл. Используется для установки единых пределов визуализации.
"""

import numpy as np
import os
import json

directory = '../sample_data'
npz_files = [f for f in os.listdir(directory) if f.endswith('.npz')]

# Определяем максимальные и минимальные значения тока по всему датасету
max_current = -float('inf')
min_current = float('inf')

for filename in npz_files:
    filepath = os.path.join(directory, filename)
    try:
        with np.load(filepath) as data:
            raw_data = data['data']
            i = raw_data[2] / 50  # Конвертируем в амперы

            # Обновляем максимальные и минимальные значения
            current_max = np.max(i)
            current_min = np.min(i)

            if current_max > max_current:
                max_current = current_max
            if current_min < min_current:
                min_current = current_min

    except Exception as e:
        print(f"Ошибка при обработке файла {filename}: {e}")
        continue

# Увеличиваем пределы на 5% для лучшей визуализации
max_current *= 1.05
min_current *= 1.05

# Сохраняем значения в файл для будущего использования
limits = {
    'max_current': max_current,
    'min_current': min_current
}

with open('current_limits.json', 'w') as f:
    json.dump(limits, f)

print(f"Максимальный ток: {max_current:.6f} А")
print(f"Минимальный ток: {min_current:.6f} А")
