#include "neoLibrary.h"

Adafruit_NeoPixel strip = Adafruit_NeoPixel(5, neo_pin, NEO_GRB + NEO_KHZ800);

void neoSetup()
{
	strip.begin();
	strip.show(); // Initialize all pixels to 'off'
	//Serial.begin(9600);
}

void colorSet(int motor, int color)
{
  if(color == off)
  {
    strip.setPixelColor(motor, strip.Color(0, 0, 0));
  }
	if(color == red)
	{
	strip.setPixelColor(motor, strip.Color(30, 0, 0));
	}
	if(color == green)
	{
	strip.setPixelColor(motor, strip.Color(0, 15, 0));
	}
	if(color == blue)
	{
	strip.setPixelColor(motor, strip.Color(0, 0, 10));
	}
 if(color == yellow)
  {
  strip.setPixelColor(motor, strip.Color(17, 12, 0));
  }
  if(color == no)
  {
    strip.setPixelColor(motor, strip.Color(0, 15, 15));
  }
	if(color == white)
	{
	strip.setPixelColor(motor, strip.Color(10, 10, 10));
	}
	if(color == purple)
	{
	strip.setPixelColor(motor, strip.Color(15, 0, 15));
	}
}

void colorShow()
{
	strip.show();
}
