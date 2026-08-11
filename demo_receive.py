import serial
import struct
import time

# --- Настройки ---
COM_PORT = 'COM7'
BAUD_RATE = 115200
START_BYTE = 0xAA  # Произвольный стартовый байт (должен совпадать с Arduino)
DATA_SIZE = 2      # Размер данных (2 байта для int16_t)

# --- Глобальная переменная для хранения позиции руля ---
wheel_position = 0

# --- Подключение к порту ---
try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print(f"Подключено к {COM_PORT} на скорости {BAUD_RATE} бод")
    print("Ожидание данных о позиции...")
except serial.SerialException as e:
    print(f"Ошибка подключения к {COM_PORT}: {e}")
    exit()

buffer = bytearray() # Буфер должен быть глобальным или передаваться в функцию

def read_wheel_position():
    global wheel_position, buffer
    if ser.in_waiting > 0:
        new_bytes = ser.read(ser.in_waiting)
        buffer.extend(new_bytes)

        # Ищем стартовый байт в буфере
        while len(buffer) > 0:
            if buffer[0] == START_BYTE:
                # Найден стартовый байт
                if len(buffer) >= 1 + DATA_SIZE: # Проверяем, достаточно ли байт для данных
                    # Извлекаем 2 байта данных
                    data_bytes = buffer[1 : 1 + DATA_SIZE]
                    buffer = buffer[1 + DATA_SIZE :] # Удаляем обработанное сообщение из буфера

                    # Распаковываем как signed int16 (little-endian)
                    try:
                        position_value = struct.unpack('<h', data_bytes)[0] # '<h' = little-endian signed short (int16_t)
                        wheel_position = position_value
                        # print(f"Принята позиция: {position_value}")  # можно убрать или оставить для дебага
                    except struct.error:
                        print(f"Ошибка при распаковке данных: {data_bytes}")
                    break # Перейти к следующему байту в буфере
                else:
                    # Недостаточно байт для данных, ждём дальше
                    break
            else:
                # Первый байт не стартовый, удаляем его
                buffer.pop(0)

try:
    while True:
        read_wheel_position()
        # Теперь можно использовать глобальную переменную wheel_position где угодно
        # print(f"Текущая позиция руля: {wheel_position}")
        time.sleep(0.0001)
        print(f"Принята позиция: {wheel_position}")  # можно убрать или оставить для дебага


except KeyboardInterrupt:
    print("\nПрервано пользователем")

finally:
    ser.close()
    print(f"Порт {COM_PORT} закрыт.")
