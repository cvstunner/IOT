#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "MAX30105.h"
#include "heartRate.h"
#include "spo2_algorithm.h"
#include <NTPClient.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <PicoEspTime.h>

#define SCREEN_WIDTH 128  
#define SCREEN_HEIGHT 64  
#define OLED_RESET -1        
#define SCREEN_ADDRESS 0x3C  

#define GREEN_BTN_PIN 12
#define WHITE_BTN_PIN 13

#define MAX_BRIGHTNESS 255

#define SSID "CVSTUNNER"
#define PSK "12345678912"

const byte RATE_SIZE = 4;  
byte rates[RATE_SIZE];    
byte rateSpot = 0;
long lastBeat = 0; 

float beatsPerMinute;
int beatAvg;

uint32_t irBuffer[500];   
uint32_t redBuffer[500]; 

int32_t bufferLength;  
int32_t spo2;           
int8_t validSPO2;      
int32_t heartRate;      
int8_t validHeartRate;  

byte ledBrightness = 0x1F;  //Options: 0=Off to 255=50mA
byte sampleAverage = 4;     //Options: 1, 2, 4, 8, 16, 32
byte ledMode = 3;           //Options: 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green
int sampleRate = 1000;      //Options: 50, 100, 200, 400, 800, 1000, 1600, 3200
int pulseWidth = 411;       //Options: 69, 118, 215, 411
int adcRange = 16384;        //Options:[0] 2048, 4096, 8192, 16384

int page_flag = 0;
int task_status = 0;
int wifi_status = -1;

unsigned int localPort = 8888;  
char packetBuffer[UDP_TX_PACKET_MAX_SIZE + 1];  
char ReplyBuffer[] = "acknowledged\r\n";    

uint32_t lastTime; 

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
MAX30105 particleSensor;

PicoEspTime rtc;
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP);

void setup() {
  Serial.begin(9600);
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;)
      ;
  }
  if (!particleSensor.begin(Wire1, I2C_SPEED_FAST))  //Use default I2C port, 400kHz speed
  {
    Serial.println("MAX30105 was not found. Please check wiring/power. ");
    while (1)
      ;
  }
  Serial.println("Place your index finger on the sensor with steady pressure.");

  // particleSensor.setup();
  particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange);

  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(2);

  int status = connectWIFI();
  if (status == 0){
    timeClient.begin();
    display.clearDisplay();
    display.setCursor(15, 25);
    timeClient.setTimeOffset(int(3600*5.5));
    timeClient.update();
    display.println(timeClient.getFormattedTime());
    display.display();
  }
  // Buttons Instances
  pinMode(GREEN_BTN_PIN, INPUT_PULLUP);
  pinMode(WHITE_BTN_PIN, INPUT_PULLUP);
}

void loop() {
  // Buttons Listeners
  byte green_btn = digitalRead(GREEN_BTN_PIN);
  byte white_btn = digitalRead(WHITE_BTN_PIN);

  if(page_flag == 0){
    display.clearDisplay();
    display.setCursor(15, 25);
    display.println(timeClient.getFormattedTime());
    display.display();
  }
  
  // if(millis() - lastTime >= 250) {
  //   Serial.println("Ok!");
  //   lastTime = millis();
  // }
  if (green_btn == LOW) {
    Serial.print("Green Btn: ");
    green_btn_clicked();
  } else if (white_btn == LOW) {
    Serial.print("White Btn: ");
    white_btn_clicked();
  }
  Serial.println(millis());
  delay(150);
}

int connectWIFI() {
  int counter = 0;
  WiFi.begin(SSID, PSK);
  Serial.print("Connecting to " + String(SSID));
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    if(counter == 10){
      break;
    }
    counter++;
    Serial.print(counter + "s ");
  }
  Serial.println(WiFi.status());
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Connected! IP address: ");
    Serial.println(WiFi.localIP());
    Serial.printf("UDP server on port %d\n", localPort);
    wifi_status = 0;
    return 0;
  } else {
    Serial.print("Connected Failed!");
    return -1;
    wifi_status = -1;
  }
}

void white_btn_clicked(){
  if (page_flag == 0 && task_status == 0){
    return;
  }
  else if(page_flag == 1 && task_status == 0){
    task_status = 1;
    HRSPO2();
  }
  else if(page_flag == 2 && task_status == 0){
    task_status = 1;
  }
}
  
void green_btn_clicked() {
  if (page_flag == 0) {
    Serial.println("Page 2!");
    display.clearDisplay();
    display.setCursor(15, 25);
    display.println("Oximeter");
    display.display();
    page_flag = 1;
  } else if (page_flag == 1) {
    Serial.println("Page 3!");
    display.clearDisplay();
    display.setCursor(35, 25);
    display.println("ECG");
    display.display();
    page_flag = 2;
  } else if (page_flag == 2) {
    Serial.println("Page 1!");
    display.clearDisplay();
    page_flag = 0;
  }
}

void HRSPO2() {
  String calcTxt;
  int counter = 0;
  bufferLength = 100; 
  int count = 0;
  long irValue;
  double body_temp = 0;

  while (count < 25) {
    for (byte i = 25; i < 100; i++) {
      redBuffer[i - 25] = redBuffer[i];
      irBuffer[i - 25] = irBuffer[i];
    }

    for (byte i = 75; i < 100; i++) {
      while (particleSensor.available() == false)  
        particleSensor.check();                    

      redBuffer[i] = particleSensor.getRed();
      irBuffer[i] = irValue = particleSensor.getIR();
      particleSensor.nextSample();  

      if (checkForBeat(irValue) == true) {
        long delta = millis() - lastBeat;
        lastBeat = millis();

        beatsPerMinute = 60 / (delta / 1000.0);

        if (beatsPerMinute < 255 && beatsPerMinute > 20) {
          rates[rateSpot++] = (byte)beatsPerMinute;  
          rateSpot %= RATE_SIZE;                    

          beatAvg = 0;
          for (byte x = 0; x < RATE_SIZE; x++)
            beatAvg += rates[x];
          beatAvg /= RATE_SIZE;
        }
      }

      if (counter == 1) {
        calcTxt = "Calculating";
      } else if (counter == 16) {
        calcTxt = "Calculating.";
      } else if (counter == 32) {
        calcTxt = "Calculating..";
      } else if (counter == 47) {
        calcTxt = "Calculating...";
      } else if (counter == 61) {
        counter = 0;
      }
      counter++;
      
      display.setTextSize(1);  
      display.clearDisplay();
      display.setCursor(15, 25);
      display.println(calcTxt);
      display.display();  

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

  String bpm = "HR:" + String(heartRate) + "bpm";
  String spo2r = "SPO2:" + String(spo2) + "%";
  String temp = "TEMP:" + String(int(body_temp)) + " C";
  display.clearDisplay();
  display.setTextSize(2);  
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 2);
  display.println(bpm);
  display.setCursor(0, 22);
  display.println(spo2r);
  display.setCursor(0, 44);
  display.println(temp);
  display.drawCircle(88, 44, 2, SSD1306_WHITE);
  display.display();  
  task_status = 0;
}
