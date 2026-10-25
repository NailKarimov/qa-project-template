// Echo device for the bench: the same frame format and rules as python/src/bus_lab/device.py,
// so the Python suite runs unchanged against the board:
//
//   BUS_URL=/dev/ttyUSB0?baud=115200 HIL=1 pytest
//
// Frame: [address][length][payload...][crc low][crc high], CRC-16/MODBUS.
// Rules: answer own address with the same payload; never answer broadcast (0);
// ignore a wrong CRC; flush input after an impossible length byte.
//
// Board: any ESP32 dev board (ESP32-DevKitC, NodeMCU-32S). Arduino IDE → board "ESP32 Dev Module".
// The link is UART0 through the board's USB chip. For the logic analyzer:
//   CH0 → TX0 (GPIO1, "TX"), CH1 → RX0 (GPIO3, "RX"), GND → GND.

#include <Arduino.h>

const uint8_t ADDRESS = 0x11;
const uint8_t BROADCAST = 0x00;
const uint8_t MAX_PAYLOAD = 32;
const uint32_t BAUD = 115200;
const uint32_t BYTE_TIMEOUT_MS = 500;  // same as the simulator
const int LED = 2;                     // on-board LED on most dev boards

uint32_t crcErrors = 0, framingErrors = 0, broadcasts = 0;

uint16_t crc16Modbus(const uint8_t *data, size_t len) {
  uint16_t crc = 0xFFFF;
  for (size_t i = 0; i < len; i++) {
    crc ^= data[i];
    for (int b = 0; b < 8; b++) crc = (crc & 1) ? (crc >> 1) ^ 0xA001 : crc >> 1;
  }
  return crc;
}

// Read exactly n bytes or give up after BYTE_TIMEOUT_MS of silence.
bool readExact(uint8_t *buf, size_t n) {
  size_t got = 0;
  uint32_t last = millis();
  while (got < n) {
    if (Serial.available()) {
      buf[got++] = Serial.read();
      last = millis();
    } else if (millis() - last > BYTE_TIMEOUT_MS) {
      return false;
    }
  }
  return true;
}

void setup() {
  pinMode(LED, OUTPUT);
  Serial.begin(BAUD);
  // Boot messages from the ROM also go out on UART0; the test fixture waits 2 s and flushes them.
}

void loop() {
  if (!Serial.available()) return;

  uint8_t frame[2 + MAX_PAYLOAD + 2];
  if (!readExact(frame, 2)) { framingErrors++; return; }

  uint8_t len = frame[1];
  if (len > MAX_PAYLOAD) {          // rule 4
    framingErrors++;
    delay(5);
    while (Serial.available()) Serial.read();
    return;
  }
  if (!readExact(frame + 2, len + 2)) { framingErrors++; return; }

  uint16_t crc = crc16Modbus(frame, 2 + len);
  if (frame[2 + len] != (crc & 0xFF) || frame[3 + len] != (crc >> 8)) {  // rule 3
    crcErrors++;
    return;
  }
  if (frame[0] == BROADCAST) { broadcasts++; return; }  // rule 2
  if (frame[0] != ADDRESS) return;                      // rule 1

  // Echo: address stays ours, payload unchanged, fresh CRC.
  crc = crc16Modbus(frame, 2 + len);
  frame[2 + len] = crc & 0xFF;
  frame[3 + len] = crc >> 8;
  digitalWrite(LED, HIGH);
  Serial.write(frame, 4 + len);
  Serial.flush();
  digitalWrite(LED, LOW);
}
