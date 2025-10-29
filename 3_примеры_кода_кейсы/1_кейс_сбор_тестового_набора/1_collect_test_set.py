"""
Находит и сохраняет отдельные импульсы из экспериментальных данных.
Использует производную и пороговые значения для точного определения границ импульсов.
"""

import numpy as np
import os


directory = '../../sample_data'
npz_files = [f for f in os.listdir(directory) if f.endswith('.npz')]

# Обработка одного файла для поиска и сохранения импульсов
def find_and_save_impulses(filepath, current_threshold=0.001, derivative_threshold=0.0003, noise_threshold=0.0005, min_duration=10, padding=5):
    try:
        with np.load(filepath) as data:
            raw_data = data['data']
            t = raw_data[0]
            i = raw_data[2] / 50  # Конвертируем в амперы

        # Вычисляем производную тока
        di_dt = np.diff(i)
        # Находим точки, где ток превышает порог (сам импульс)
        above_current_threshold = np.abs(i) > current_threshold
        # Находим точки, где ток возвращается к уровню шума
        at_noise_level = np.abs(i) <= noise_threshold
        # Находим границы импульсов с помощью производной и проверки уровня шума
        impulse_starts = []
        impulse_ends = []
        in_impulse = False
        for idx, (is_above, is_noise) in enumerate(zip(above_current_threshold, at_noise_level)):
            if is_above and not in_impulse:
                # Начало импульса найдено по току, ищем точную границу по производной
                start_idx = idx
                while start_idx > 0 and np.abs(di_dt[start_idx-1]) > derivative_threshold:
                    start_idx -= 1
                impulse_starts.append(start_idx)
                in_impulse = True
            elif (not is_above or is_noise) and in_impulse:
                # Конец импульса найден по току или возврату к уровню шума
                end_idx = idx
                while end_idx < len(di_dt) and np.abs(di_dt[end_idx]) > derivative_threshold:
                    end_idx += 1
                impulse_ends.append(end_idx)
                in_impulse = False

        # Сохраняем найденные импульсы с дополнительными точками
        impulse_count = 0
        for start, end in zip(impulse_starts, impulse_ends):
            if end - start >= min_duration:
                padded_start = max(0, start - padding)
                padded_end = min(len(t), end + padding)

                impulse_data = {
                    't': t[padded_start:padded_end],
                    'i': i[padded_start:padded_end]
                }

                # Сохраняем импульс в отдельный файл
                filename = f"saved_impulses/impulse_{impulse_count:04d}.npz"
                np.savez(filename, **impulse_data)
                impulse_count += 1

        print(f"Найдено и сохранено {impulse_count} импульсов")
        print(f"Параметры: current_threshold={current_threshold}, derivative_threshold={derivative_threshold}, noise_threshold={noise_threshold}, padding={padding}")
        return impulse_count

    except Exception as e:
        print(f"Ошибка при загрузке файла {filepath}: {e}")
        return 0


# Запускаем функцию для первого файла
find_and_save_impulses(f"{directory}/{npz_files[0]}")
