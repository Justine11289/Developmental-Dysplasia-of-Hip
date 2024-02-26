/*
    MPU6050 Triple Axis Gyroscope & Accelerometer. Pitch & Roll & Yaw Gyroscope Example.
    Read more: http://www.jarzebski.pl/arduino/czujniki-i-sensory/3-osiowy-zyroskop-i-akcelerometr-mpu6050.html
    GIT: https://github.com/jarzebski/Arduino-MPU6050
    Web: http://www.jarzebski.pl
    (c) 2014 by Korneliusz Jarzebski
*/

#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu1;//0x68
MPU6050 mpu2;//0x69

// Timers
unsigned long timer = 0;
float timeStep = 0.01;

// Pitch, Roll and Yaw values
float pitch1 = 0,roll1 = 0,yaw1 = 0;
float pitch2 = 0,roll2 = 0,yaw2 = 0;

bool shouldTransmit = false;
void setup() 
{
  delay(500);
  Serial.begin(115200);
  /*while(Serial.available() > 0){
    Serial.read();
  }
  while(Serial.available() == 0 || Serial.read() == 's'){
    
  }*/

  // Initialize MPU6050 1
  while(!mpu1.begin(MPU6050_SCALE_250DPS, MPU6050_RANGE_2G,0x68))
  {
    Serial.println("Could not find a valid MPU6050 sensor 1(0x68), check wiring!");
    delay(500);
  }
  
  // Calibrate gyroscope. The calibration must be at rest.
  // If you don't want calibrate, comment this line.
  mpu1.calibrateGyro();
  
  // Set threshold sensivty. Default 3.
  // If you don't want use threshold, comment this line or set 0.
  mpu1.setThreshold(0);
  
  delay(500);
   // Initialize MPU6050 2
  while(!mpu2.begin(MPU6050_SCALE_250DPS, MPU6050_RANGE_2G,0x69))
  {
    Serial.println("Could not find a valid MPU6050 sensor 2(0x69), check wiring!");
    delay(500);
  }
  
  // Calibrate gyroscope. The calibration must be at rest.
  // If you don't want calibrate, comment this line.
  mpu2.calibrateGyro();
  
  // Set threshold sensivty. Default 3.
  // If you don't want use threshold, comment this line or set 0.
  mpu2.setThreshold(0);
  
  Serial.println("start computing!");
}


void loop(){
  if (Serial.available() > 0) {
    char receivedChar = Serial.read();
    if (receivedChar == 's') {
        shouldTransmit = true;
        //Serial.println("start!");
    } else if (receivedChar == 'e') {
        shouldTransmit = false;
        //Serial.println("END!");
    }
  }
  
  if (shouldTransmit) {
    timer = millis();
  
    // Read normalized values 1
    Vector norm1 = mpu1.readNormalizeGyro();
    Vector norm2 = mpu2.readNormalizeGyro();
  
    // Calculate Pitch, Roll and Yaw 1
  

    pitch1 = norm1.YAxis * timeStep;//degree
    roll1 = norm1.XAxis * timeStep;
    yaw1 = norm1.ZAxis * timeStep;
    
    /*pitch1 = pitch1 + norm1.YAxis * timeStep;//degree
    roll1 = roll1 + norm1.XAxis * timeStep;
    yaw1 = yaw1 + norm1.ZAxis * timeStep;*/
    
    // Read normalized values 2
  
  
    // Calculate Pitch, Roll and Yaw 2
    
    /*pitch2 = pitch2 + norm2.YAxis * timeStep;//degree
    roll2 = roll2 + norm2.XAxis * timeStep;
    yaw2 = yaw2 + norm2.ZAxis * timeStep;*/
    
    
    pitch2 = norm2.YAxis * timeStep;//degree
    roll2 = norm2.XAxis * timeStep;
    yaw2 = norm2.ZAxis * timeStep;
    
    
    // Output raw
    //Serial.print(" Pitch = ");
    //Serial.print("MPU1:");
    Serial.print(pitch1);
    Serial.print(" ");
    //Serial.print(" Roll = ");
    Serial.print(roll1);  
    Serial.print(" ");
    //Serial.print(" Yaw = ");
    Serial.print(yaw1);;
    Serial.print(" ");
    //Serial.print(" Pitch = ");
    //Serial.print("MPU2:");
    Serial.print(pitch2);
    Serial.print(" ");
    //Serial.print(" Roll = ");
    Serial.print(roll2);  
    Serial.print(" ");
    //Serial.print(" Yaw = ");
    Serial.println(yaw2);
  
    
    // Wait to full timeStep period
    //delay((timeStep*1000) - (millis() - timer));
    delay(20);
  }
}
  
