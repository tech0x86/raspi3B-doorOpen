#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import datetime
import wiringpi as w
import sys

def setupMotor(pin):
  w.wiringPiSetupGpio()
  w.pinMode(pin, w.GPIO.PWM_OUTPUT)
  w.pwmSetMode(w.GPIO.PWM_MODE_MS)
  w.pwmSetRange(1920)
  w.pwmSetClock(200)


#SG92Rをコントロールするための
class SG90_92R_Class:
    # mPin : GPIO Number (PWM)
    # mPwm : Pwmコントロール用のインスタンス
    # m_Zero_offset_duty :

    """コンストラクタ"""
    def __init__(self, Pin, ZeroOffsetDuty):
        self.mPin = Pin
        self.m_ZeroOffsetDuty = ZeroOffsetDuty

        #GPIOをPWMモードにする
        GPIO.setup(self.mPin, GPIO.OUT)
        self.mPwm = GPIO.PWM(self.mPin , 50) # set 20ms / 50 Hz

    """位置セット"""
    def SetPos(self,pos):
        #Duty ratio = 2.5%〜12.0% : 0.5ms〜2.4ms : 0 ～ 180deg
        duty = (12-2.5)/180*pos+2.5 + self.m_ZeroOffsetDuty
        self.mPwm.start(duty)


    """終了処理"""
    def Cleanup(self,pos):
        #サーボを10degにセットしてから、インプットモードにしておく
        self.SetPos(pos) #init pos (90)
        time.sleep(1)
        GPIO.setup(self.mPin, GPIO.IN)

"""コントロール例"""
if __name__ == '__main__':
    cdsPin = 19 #wPi24
    ledPin = 26 #wpi25
    ServoBttmPin = 21 #Wpi29
    ServoPhonePin = 20 #Wpi28

    bttmInitPos = 90
    bttmPushPos = 72
    phoneInitPos = 112
    phoneGetPos = 90

    #Useing GPIO No.  to idetify channel

    try:
        print ("input angle")
        angle = int(input())
        setupMotor(ServoPhonePin)
        w.pwmWrite(ServoPhonePin,angle)
        while True:
            print ("input angle")
            w.digitalWrite(ledPin,1)
            angle = int(input())
            w.pwmWrite(ServoPhonePin,angle)
            cdSens = w.digitalRead(cdsPin)

            if cdSens == 1: #detect light
                w.digitalWrite(ledPin,1)
                dt_now = datetime.datetime.now()
                print(dt_now)
                time.sleep(1)
                ServoPhone.SetPos(phoneGetPos) #phone off (get phone)
                time.sleep(3)
                ServoBttm.SetPos(bttmPushPos)
                time.sleep(1)
                ServoBttm.SetPos(bttmInitPos)
                time.sleep(1)
                ServoPhone.SetPos(phoneInitPos)
                time.sleep(1)
                GPIO.output(21,0)
                GPIO.output(20,0)

            w.digitalWrite(ledPin,0)
            time.sleep(0.1)
    except KeyboardInterrupt  :         #Ctl+Cが押されたらループを終了
        print("\nCtl+C")
    except Exception as e:
        print(str(e))
    finally:
        #w.cleanup()
        print("\n exit program")
