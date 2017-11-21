#include <Adafruit_NeoPixel.h>


#define neo_pin 14 //A0

#define red 7
#define purple 6
#define blue 5
#define green 4
#define yellow 3
#define white 2
#define no 1
#define off 0

void neoSetup();
void colorSet(int motor, int color);
void colorShow();
