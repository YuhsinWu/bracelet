/*
 * 2010712 Monica Lin  Vibration Device
 * mo83117401500094@gmail.com
 * Connet with android device using Bluetooth(BLE)
 * History: v2.0
 */

#include "SoftPWM.h" //https://github.com/bhagman/SoftPWM
#include <stdlib.h>     /* atoi */
#include "pt.h"    /* Protothreads --Adam Dunkels */
#include "neoLibrary.h" /* NeoLibrart impotr Adafruit_NeoPixel*/
/*============================================================================================
 *Setting:  motorPin: which is connects motor pin on arduino
 *          MOTOR_LEN: the number of vibration motor
 *          MAX_PWM: the max power of vibration motor (255 is 5v)
=========================================================================================== */ 
#define MOTOR_LEN 3 //how many vibration motor is going to be used
#define MAX_PWM 153 //0-255 0-5v vibration motor max power is 3v
#define ENABLE_PIN 13
#define CYCLE_BASE 100 //interval change base time (ms)
#define CYCLE_T 6000 //Time Action cycle = CYCLE_T*2 (ms)
#define MAX_F 7
#define MAX_I 5
/* constants won't change. Used here to set a pin number : */
//const int motorPin[] = {2, 3, 1, 4, 5};  //the numer of the MOTOR pin
const int motorPin[] = {3, 4, 5};  //the numer of the MOTOR pin
/* constants won't change. Used here to set interval time 2x milliseconds : */
const int motor_interval[] = {0, 3, 4, 5, 6, 8};   //set the vibration from small to big

typedef struct newMotor
{
  unsigned int intensity;
  unsigned int frequency;
  unsigned int pwm;
}NewMotor;
NewMotor motor[MOTOR_LEN];
//NewMotor *motor = new NewMotor[MOTOR_LEN];

// The value previousMillis and currentMillis will quickly become too large for an int to store
unsigned long previousMillis  = 0;
unsigned long currentMillis;
int previous_cnt = 0;
int cnt_time;

static struct pt pt1, pt2;

void setup()
{
  // Initialize
  neoSetup();
  SoftPWMBegin();
  Serial.begin(115200); // opens  port, sets data rate to 115200 bps
  
  // Enable pin set up
  SoftPWMSet(ENABLE_PIN, 0);
  SoftPWMSetFadeTime(ENABLE_PIN, 100, 500);

  // motor pin set up
  for(int i=0; i<MOTOR_LEN ;i++)
  {
    // Create and set motor pin to 0 (off)
    SoftPWMSet(motorPin[i], 0);
    // Set fade time for motor pin to 100 ms fade-up time, and 500 ms fade-down time
    SoftPWMSetFadeTime(motorPin[i], 100, 500);
  }
  firstStart(); //vibrate all motor for 0.5s
  
  PT_INIT(&pt1);
  PT_INIT(&pt2);
}

void firstStart()
{
  int pwm = MAX_F;
  int delay_t = 500;
  for(int i = 0; i< MOTOR_LEN; i++)
  {
    motor[i].pwm = pwm*21;
    colorSet(i, 2); //green 2
  }
  colorShow();
  outIO();
  delay(delay_t);
  for(int i = 0; i< MOTOR_LEN; i++)
  {
    motor[i].pwm = 0;
    colorSet(i, 0);
  }
  colorShow();
  outIO();
  delay(10);
}

void loop()
{
  protothread1(&pt1);
  protothread2(&pt2);
  /*
  serialRead();
  showdata();
  motorCallback();
  outIO();
  */
}


int serialRead()
{
    int i = 0;
    // 檢查是否有資料可供讀取 
    while (Serial.available() > 0)
    {
      // 讀取進來的 byte
      char r = Serial.read();
      Serial.println(r);
      if(i < MOTOR_LEN)
        motor[i].intensity = (atoi(&r) < MAX_I) ? atoi(&r) : MAX_I;
      else if(i < MOTOR_LEN*2)
        motor[i-MOTOR_LEN].frequency = (atoi(&r) < MAX_F) ? atoi(&r) : MAX_F;
      i=(i+1)%(MOTOR_LEN*2);
    }
}

void showdata()
{
  for(int i=0; i<MOTOR_LEN; i++)
  {
    //Serial.print(motor[i].intensity);
    //Serial.print(motor[i].frequency);
    Serial.print(motor[i].pwm);
    if(i < MOTOR_LEN-1)
      Serial.print(",");
    else
      Serial.println();
  }
}

void setMotorPwm(int motor_number, int frequency, int intensity)
{
    if(cnt_time/intensity%2)
    {
      motor[motor_number].pwm = (frequency)*21;
      colorSet(motor_number, frequency); //green 2
    }
    else
    {
      motor[motor_number].pwm = 0;
      colorSet(motor_number, 0);
    }    
    colorShow();
}

void motorCallback()
{
  //strat a new cycle
  currentMillis = millis();
  cnt_time = (currentMillis - previousMillis)/CYCLE_BASE;

  // current time 
  if((cnt_time) >= CYCLE_T*2)
  {
    previousMillis = currentMillis;
    previous_cnt = cnt_time;
  }
  //set motor output
  if(cnt_time != previous_cnt)
  {
    for(int i =0; i<MOTOR_LEN; i++)
    {
      setMotorPwm(i, motor[i].frequency, motor_interval[motor[i].intensity]);
    }
    // set led
    SoftPWMSet(ENABLE_PIN, motor[0].pwm);
  }
  previous_cnt = cnt_time;
  //end of the a new cycle
}

void outIO()
{
  for(int i =0; i<MOTOR_LEN; i++)
  {
    // Turn on - set to pwm
    SoftPWMSet(motorPin[i], motor[i].pwm);
  }
}

static int protothread1(struct pt *pt) {
  PT_BEGIN(pt);
  serialRead();
  showdata();
  PT_END(pt);
}

static int protothread2(struct pt *pt) {
  PT_BEGIN(pt);
  motorCallback();
  outIO();
  PT_END(pt);
}
