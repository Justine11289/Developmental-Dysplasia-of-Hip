#include <MPU9250_WE.h>
#include <Wire.h>

#define MPU9250_ADDR 0x68

MPU9250_WE myMPU9250 = MPU9250_WE(MPU9250_ADDR);

void setup() {
  Serial.begin(115200);
  Wire.begin();

  if (!myMPU9250.init()) {
    Serial.println("MPU9250 does not respond");
  } else {
    Serial.println("MPU9250 is connected");
  }

  Serial.println("Position your MPU9250 flat and don't move it - calibrating...");
  delay(1000);
  myMPU9250.autoOffsets();
  Serial.println("Calibration done!");
}

void loop() {
  // Get raw accelerometer values
  xyzInt rawAccs = myMPU9250.getRawAccs();

  // Print raw accelerometer values
  Serial.print("Raw Acceleration: ");
  Serial.print(rawAccs.x);
  Serial.print(", ");
  Serial.print(rawAccs.y);
  Serial.print(", ");
  Serial.println(rawAccs.z);

  delay(500);
}
