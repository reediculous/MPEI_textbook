"""
Загружает один NPZ файл с экспериментальными данными и извлекает массивы времени,
напряжения и тока. Показывает размеры массивов для проверки корректности загрузки.
"""

import numpy as np

data_file = '../sample_data/AlN_ccurrent_50Ohm_2000V_30kHz_000001.npz'

try:
    with np.load(data_file) as data:
        raw_data = data['data']
        t = raw_data[0]
        v = raw_data[1]
        i = raw_data[2]

    print(t.shape)
    print(v.shape)
    print(i.shape)

except Exception as e:
    print(f"Ошибка при загрузке файла {data_file}: {e}")
