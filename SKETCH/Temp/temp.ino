/**************************************************************************
 This is an example for our Monochrome OLEDs based on SSD1306 drivers

 Pick one up today in the adafruit shop!
 ------> http://www.adafruit.com/category/63_98

 This example is for a 128x64 pixel display using I2C to communicate
 3 pins are required to interface (two I2C and one reset).

 Adafruit invests time and resources providing this open
 source code, please support Adafruit and open-source
 hardware by purchasing products from Adafruit!

 Written by Limor Fried/Ladyada for Adafruit Industries,
 with contributions from the open source community.
 BSD license, check license.txt for more information
 All text above, and the splash screen below must be
 included in any redistribution.
 **************************************************************************/

#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "MAX30105.h"
#include "heartRate.h"
#include "spo2_algorithm.h"

#define SCREEN_WIDTH 128  // OLED display width, in pixels
#define SCREEN_HEIGHT 64  // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
// The pins for I2C are defined by the Wire-library.
// On an arduino UNO:       A4(SDA), A5(SCL)
// On an arduino MEGA 2560: 20(SDA), 21(SCL)
// On an arduino LEONARDO:   2(SDA),  3(SCL), ...
#define OLED_RESET -1        // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C  ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32

// TwoWire CustomI2C0(scl, sda);
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
MAX30105 particleSensor;

const byte RATE_SIZE = 4;  //Increase this for more averaging. 4 is good.
byte rates[RATE_SIZE];     //Array of heart rates
byte rateSpot = 0;
long lastBeat = 0;  //Time at which the last beat occurred

float beatsPerMinute;
int beatAvg;

#define MAX_BRIGHTNESS 255

// #if defined(__AVR_ATmega328P__) || defined(__AVR_ATmega168__)
// uint16_t irBuffer[200]; //infrared LED sensor data
// uint16_t redBuffer[200];  //red LED sensor data
// #else
uint32_t irBuffer[500]; //infrared LED sensor data
uint32_t redBuffer[500];  //red LED sensor data
// #endif

int32_t bufferLength; //data length
int32_t spo2; //SPO2 value
int8_t validSPO2; //indicator to show if the SPO2 calculation is valid
int32_t heartRate; //heart rate value
int8_t validHeartRate; //indicator to show if the heart rate calculation is valid

byte ledBrightness = 0x1F; //Options: 0=Off to 255=50mA
byte sampleAverage = 4; //Options: 1, 2, 4, 8, 16, 32
byte ledMode = 3; //Options: 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green
int sampleRate = 1000; //Options: 50, 100, 200, 400, 800, 1000, 1600, 3200
int pulseWidth = 411; //Options: 69, 118, 215, 411
int adcRange = 4096; //Options:[0] 2048, 4096, 8192, 16384

void setup() {\
  Serial.begin(9600);

  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;)
      ;
  }

  if (!particleSensor.begin(Wire, I2C_SPEED_FAST))  //Use default I2C port, 400kHz speed
  {
    Serial.println("MAX30105 was not found. Please check wiring/power. ");
    while (1)
      ;
  }
  Serial.println("Place your index finger on the sensor with steady pressure.");

  // particleSensor.setup();  
  particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange); //Configure sensor with these settings                   
  // particleSensor.setPulseAmplitudeRed(0x0A);  //Turn Red LED to low to indicate sensor is running
  particleSensor.setPulseAmplitudeGreen(0);   //Turn off Green LED


  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(10, 0);
  display.setTextSize(1);  // Draw 2X-scale text
  display.println("Chetan");
  display.display();
  HRSPO2();
  // display.clearDisplay();
  // display.setTextColor(SSD1306_WHITE);
  // display.setCursor(10, 0);
  // // delay(2000);
  // display.setTextSize(2);  // Draw 2X-scale text
  //display.println(name);
  //display.display();  // Show initial text
}

void loop() {
}

void HRSPO2() {
  String calcTxt;
  int counter = 0;
  // for (int i = 0; i <= 500; i++) {
  //   long irValue = particleSensor.getIR();

  //   if (checkForBeat(irValue) == true) {
  //     //We sensed a beat!
  //     long delta = millis() - lastBeat;
  //     lastBeat = millis();

  //     beatsPerMinute = 60 / (delta / 1000.0);

  //     if (beatsPerMinute < 255 && beatsPerMinute > 20) {
  //       rates[rateSpot++] = (byte)beatsPerMinute;  //Store this reading in the array
  //       rateSpot %= RATE_SIZE;                     //Wrap variable

  //       //Take average of readings
  //       beatAvg = 0;
  //       for (byte x = 0; x < RATE_SIZE; x++)
  //         beatAvg += rates[x];
  //       beatAvg /= RATE_SIZE;
  //     }
  //   }

  //   if(counter == 1){
  //     calcTxt = "Calculating";
  //   }
  //   else if(counter == 16){
  //     calcTxt = "Calculating.";
  //   }
  //   else if(counter == 32){
  //     calcTxt = "Calculating..";
  //   }
  //   else if(counter == 47){
  //     calcTxt = "Calculating...";
  //   }
  //   else if(counter == 61){
  //     counter = 0;
  //   }
  //   counter++;
  //   display.clearDisplay();
  //   display.setCursor(10, 0);
  //   display.println(calcTxt);
  //   display.display();  // Show initial text

  //   Serial.print("IR=");
  //   Serial.print(irValue);
  //   Serial.print(", BPM=");
  //   Serial.print(beatsPerMinute);
  //   Serial.print(", Avg BPM=");
  //   Serial.print(beatAvg);

  //   if (irValue < 50000)
  //     Serial.print(" No finger?");

  //   Serial.println();
  // }

  // bufferLength = 100; //buffer length of 100 stores 4 seconds of samples running at 25sps

  // read the first 100 samples, and determine the signal range
  bufferLength = 100; //buffer length of 100 stores 4 seconds of samples running at 25sps

  //read the first 100 samples, and determine the signal range
  // for (byte i = 0 ; i < bufferLength ; i++)
  // {
  //   while (particleSensor.available() == false) //do we have new data?
  //     particleSensor.check(); //Check the sensor for new data

  //   redBuffer[i] = particleSensor.getRed();
  //   irBuffer[i] = particleSensor.getIR();
  //   particleSensor.nextSample(); //We're finished with this sample so move to next sample

  //   Serial.print(F("red="));
  //   Serial.print(redBuffer[i], DEC);
  //   Serial.print(F(", ir="));
  //   Serial.println(irBuffer[i], DEC);
  // }

  //calculate heart rate and SpO2 after first 100 samples (first 4 seconds of samples)
  // maxim_heart_rate_and_oxygen_saturation(irBuffer, bufferLength, redBuffer, &spo2, &validSPO2, &heartRate, &validHeartRate);

  //Continuously taking samples from MAX30102.  Heart rate and SpO2 are calculated every 1 second
  int count = 0;
  long irValue;
  double body_temp = 0;
  while (count < 25)
  {
    // dumping the first 25 sets of samples in the memory and shift the last 75 sets of samples to the top
    for (byte i = 25; i < 100; i++)
    {
      redBuffer[i - 25] = redBuffer[i];
      irBuffer[i - 25] = irBuffer[i];
    }

    //take 25 sets of samples before calculating the heart rate.
    for (byte i = 75; i < 100; i++)
    {
      while (particleSensor.available() == false) //do we have new data?
        particleSensor.check(); //Check the sensor for new data

      redBuffer[i] = particleSensor.getRed();
      irBuffer[i] = irValue = particleSensor.getIR();
      particleSensor.nextSample(); //We're finished with this sample so move to next sample

    if (checkForBeat(irValue) == true) {
      //We sensed a beat!
      long delta = millis() - lastBeat;
      lastBeat = millis();

      beatsPerMinute = 60 / (delta / 1000.0);

      if (beatsPerMinute < 255 && beatsPerMinute > 20) {
        rates[rateSpot++] = (byte)beatsPerMinute;  //Store this reading in the array
        rateSpot %= RATE_SIZE;                     //Wrap variable

        //Take average of readings
        beatAvg = 0;
        for (byte x = 0; x < RATE_SIZE; x++)
          beatAvg += rates[x];
        beatAvg /= RATE_SIZE;
      }
    }

    if(counter == 1){
      calcTxt = "Calculating";
    }
    else if(counter == 16){
      calcTxt = "Calculating.";
    }
    else if(counter == 32){
      calcTxt = "Calculating..";
    }
    else if(counter == 47){
      calcTxt = "Calculating...";
    }
    else if(counter == 61){
      counter = 0;
    }
    counter++;
    display.clearDisplay();
    display.setCursor(10, 0);
    display.println(calcTxt);
    display.display();  // Show initial text

    Serial.print("IR=");
    Serial.print(irValue);
    Serial.print(", BPM=");
    Serial.print(beatsPerMinute);
    Serial.print(", Avg BPM=");
    Serial.print(beatAvg);

    if (irValue < 50000)
      Serial.print(" No finger?");

    Serial.println();

      Serial.print(F("red="));
      Serial.print(redBuffer[i], DEC);
      Serial.print(F(", ir="));
      Serial.print(irBuffer[i], DEC);

      Serial.print(F(", SPO2="));
      Serial.print(spo2, DEC);

      Serial.print(F(", SPO2Valid="));
      Serial.println(validSPO2, DEC);
    }
    maxim_heart_rate_and_oxygen_saturation(irBuffer, bufferLength, redBuffer, &spo2, &validSPO2, &heartRate, &validHeartRate);
    body_temp = particleSensor.readTemperature();
    count++;
  }

  // beatAvg
  String bpm = "HR:" + String(heartRate) + "bpm";
  String spo2r = "SPO2:" + String(spo2) + "%";
  String temp = "TEMP:" + String(int(body_temp)) + " C";
  display.clearDisplay();
  display.setTextSize(2);  // Draw 2X-scale text
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 2);
  display.println(bpm);
  display.setCursor(0, 22);
  display.println(spo2r);
  display.setCursor(0, 44);
  display.println(temp);
  display.drawCircle(88, 44, 2, SSD1306_WHITE);
  display.display();  // Show initial text
  
}
