#include <TroykaIMU.h>

Compass compass;

const float compassCalibrationBias[3] = { 567.893, -825.35, 1061.436 };
const float compassCalibrationMatrix[3][3] = { { 1.909, 0.082, 0.004 },
                                               { 0.049, 1.942, -0.235 },
                                               { -0.003, 0.008, 1.944 } };

const int ENA_PIN = 4;  // Управление скоростью (ШИМ)
const int A_PIN = 5;    // Направление 1
const int B_PIN = 6;    // Направление 2

// --- Настройки для бинарного обмена ---
const uint8_t START_BYTE = 0xAA;
const size_t FLOAT_SIZE = 4;

// Union для приёма float
union FloatBytesUnion {
  float f_val;
  uint8_t b_val[4];
} float_union;

// Union для отправки int16_t
union Int16BytesUnion {
  int16_t val;
  uint8_t bytes[2];
} azimut_union;

// --- Настройки отправки азимута ---
const unsigned long TARGET_FREQ_HZ = 50;
const unsigned long INTERVAL_MICROS = 1000000UL / TARGET_FREQ_HZ;

unsigned long lastSendTime = 0;
unsigned long currentTime = 0;

// --- Глобальные переменные для приёма ---
uint8_t rx_buffer[4];
uint8_t rx_index = 0;
bool receiving = false;

void setMotorSpeed(int speed) {
  if (speed > 255) speed = 255;
  if (speed < -255) speed = -255;

  if (speed > 0) {
    // Вращение вперёд
    analogWrite(A_PIN, speed);
    digitalWrite(B_PIN, LOW);
    digitalWrite(ENA_PIN, HIGH);
  } else if (speed < 0) {
    // Вращение назад
    analogWrite(B_PIN, -speed);
    digitalWrite(A_PIN, LOW);
    digitalWrite(ENA_PIN, HIGH);
  } else {
    // Остановка
    analogWrite(ENA_PIN, 0);
  }
}

void setup() {
  Serial.begin(115200);  // Инициализация Serial
  // pinMode(3, OUTPUT);
  pinMode(ENA_PIN, OUTPUT);
  pinMode(A_PIN, OUTPUT);
  pinMode(B_PIN, OUTPUT);

  setMotorSpeed(0);  // Начальная остановка

  Serial.println("Compass begin");
  compass.begin();
  compass.setCalibrateMatrix(compassCalibrationMatrix, compassCalibrationBias);
  Serial.println("Initialization completed");
  lastSendTime = micros();
}


void loop() {
  // --- Приём команды на скорость мотора ---
  while (Serial.available()) {
    uint8_t incoming_byte = Serial.read();

    if (!receiving) {
      if (incoming_byte == START_BYTE) {
        receiving = true;
        rx_index = 0;
      }
    } else {
      rx_buffer[rx_index++] = incoming_byte;
      if (rx_index >= FLOAT_SIZE) {
        // Собрали 4 байта
        float_union.b_val[0] = rx_buffer[0];
        float_union.b_val[1] = rx_buffer[1];
        float_union.b_val[2] = rx_buffer[2];
        float_union.b_val[3] = rx_buffer[3];

        float received_speed_f = float_union.f_val;
        int speed = int(received_speed_f * 80);
        setMotorSpeed(speed);
        // analogWrite(3, abs(speed));
        receiving = false;  // Сброс состояния приёма
      }
    }
  }

  // --- Отправка азимута ---
  currentTime = micros();
  if ((currentTime - lastSendTime) >= INTERVAL_MICROS) {
    float azimuth_f = compass.readAzimut() + 180;
    if (azimuth_f > 360) {
      azimuth_f -= 360;
    }
    int16_t azimuth_int = (int16_t)map(azimuth_f, 0, 360, 0, 32768);  // Простое приведение, можно округлить, если нужно

    azimut_union.val = azimuth_int;

    Serial.write(START_BYTE);
    Serial.write(azimut_union.bytes[0]);  // Младший байт
    Serial.write(azimut_union.bytes[1]);  // Старший байт

    lastSendTime = currentTime;
  }

  // delayMicroseconds(10);  // Небольшая задержка, как в отправляющем скетче
}