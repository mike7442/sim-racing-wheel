import serial
import struct
import time
import math

# --- Настройки ---
COM_PORT = 'COM7'
BAUD_RATE = 115200
START_BYTE = 0xAA  # Произвольный стартовый байт
TARGET_FREQ_HZ = 500  # Целевая частота обновления
INTERVAL_SEC = 1.0 / TARGET_FREQ_HZ  # Интервал между отправками (1/500 = 0.002 секунды)

# --- Глобальные переменные ---
last_send_time = 0.0  # Время последней отправки
counter = 0  # Для генерации значения

# --- Подключение к порту ---
try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print(f"Подключено к {COM_PORT} на скорости {BAUD_RATE} бод")
except serial.SerialException as e:
    print(f"Ошибка подключения к {COM_PORT}: {e}")
    exit()

def transmit(value_to_send):
                # Упаковываем float в 4 байта (little-endian)
            packed_data = struct.pack('<f', value_to_send)

            # Формируем сообщение: START_BYTE + 4 байта float
            message = bytearray([START_BYTE]) + packed_data

            # Отправляем байты
            ser.write(message)
            # print(f"Отправлено: [0x{START_BYTE:02X}] + float({value_to_send:.4f})") # Для отладки, можно закомментировать

            # --- Задаём время последнего выполнения ---
##            print(1)

    
try:
    while True:
        current_time = time.time() # Обновляем глобальную переменную времени

        # Проверяем, пора ли отправлять
        if (current_time - last_send_time) >= INTERVAL_SEC:
            # --- Действие: Подготовка и отправка данных ---
            # Пример: отправляем синусоидальное значение
            value_to_send = math.sin(counter * 0.005)  # Меняется от -1 до 1
            print(value_to_send)
            counter = (counter + 1) % (2 * 31415) # Просто счётчик, чтобы не расти бесконечно (опционально)
            last_send_time = current_time
            transmit(value_to_send)

        # --- Задержка для уступки процессора ---
        time.sleep(0.0001) # 100 мкс

except KeyboardInterrupt:
    print("\nПрервано пользователем")

finally:
    ser.close()
    print(f"Порт {COM_PORT} закрыт.")
