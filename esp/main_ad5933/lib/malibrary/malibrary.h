/*
 * Header File
 * malibrary.h
*/

#ifndef MALIBRARY_H
#define MALIBRARY_H

#include "Arduino.h"
#include <Wire.h>
#include <AD5933.h>

struct params {
  int frequency;
  float impedance;
  float phase;
};

class Malibrary {
  public:
    Malibrary();

    // void sdInit(const byte chipSelect);
    // void sdWrite(structIna *_structIna, structKuroli *_structKuroli);
    // void serialLog(structIna *_structIna, structKuroli *_structKuroli);
    // void displayInit(const byte kolom, const byte baris);
    // void initIna219();
    // void readIna219(structIna *_structIna219);
    // void initIna226();
    // void readIna226(structIna *_structIna226);
    // void textIna(structIna *_structIna);
  
  private:
    // LiquidCrystal_I2C *_lcd;
    // Adafruit_INA219 *_ina;  //uncomment if using ina219
    // INA226_WE *_ina226; //uncomment if using ina226
    // HCSR04 *_hc;

    // byte TRIG=5, ECHO=6;
    // byte GAS;
};

#endif