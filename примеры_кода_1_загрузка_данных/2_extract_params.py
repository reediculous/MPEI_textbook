"""
Извлекает параметры эксперимента (сопротивление, напряжение, частота) из имени файла
с помощью регулярных выражений. Полезно для автоматической обработки файлов с
параметрами в названии.
"""

import re

def extract_parameters_from_filename(filename):
    # Паттерн для извлечения параметров из имени файла
    match = re.search(r'(\d+)Ohm_(\d+)V_(\d+)kHz', filename)
    if match:
        resistance = int(match.group(1))
        voltage = int(match.group(2))
        frequency = int(match.group(3))
        return resistance, voltage, frequency
    else:
        return None, None, None

# Пример использования
filename = "100Ohm_5V_30kHz.npz"
resistance, voltage, frequency = extract_parameters_from_filename(filename)
print(f"Сопротивление: {resistance} Ом, Напряжение: {voltage} В, Частота: {frequency} кГц")
