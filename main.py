#!/usr/bin/env python
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time, os
import datetime
path = "/home/pi/Desktop/log.txt"
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

def shutdown(channel):
  os.system("sudo shutdown -h now")

def reboot(channel):
  os.system("sudo reboot")

"""コントロール例"""
if __name__ == '__main__':
    cdsPin = 19
    ledPin = 13 # &motorDriver (0 is On)
    led2Pin = 26
    switchPin = 12 #black
    switch2Pin = 16 # red
    switch3Pin = 25 # red bottom
    #servo pin = 20,21

    bttmInitPos = 90
    bttmPushPos = 69
    phoneInitPos = 120
    phoneGetPos = 90

    #Useing GPIO No.  to idetify channel
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(cdsPin, GPIO.IN) #cdS
    GPIO.setup(ledPin,GPIO.OUT) #led
    GPIO.setup(led2Pin,GPIO.OUT) #led +motor
    GPIO.setup(switchPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(switch2Pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(switch3Pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(switch2Pin, GPIO.RISING, callback = shutdown, bouncetime = 2000)
    GPIO.add_event_detect(switch3Pin, GPIO.RISING, callback = reboot, bouncetime = 2000)

    ServoBttm = SG90_92R_Class(Pin=21,ZeroOffsetDuty=0)
    ServoPhone = SG90_92R_Class(Pin=20,ZeroOffsetDuty=0)

    GPIO.output(ledPin,0) #led ON ,Motor ON
    ServoBttm.SetPos(bttmInitPos) #init pos
    ServoPhone.SetPos(phoneInitPos) #init pos
    GPIO.output(21,0)
    GPIO.output(20,0)
    GPIO.output(ledPin,1) #led OFF ,Motor OFF

    try:
        f = open(path, mode ="a")
        flagSwitch = 0
        blinkTime = 0.5
    except Exception as e:
        print (str(e))
        f.close()
    try:
        while True:
            GPIO.output(led2Pin,1)
            time.sleep(blinkTime)
            GPIO.output(led2Pin,0)

            if GPIO.input(switchPin) == 1: #black switch push
                if flagSwitch == 0:
                    flagSwitch = 1
                    blinkTime = 0.1
					GPIO.output(led2Pin,1)
                    time.sleep(3)
					GPIO.output(led2Pin,0)
                else:
					flagSwitch = 0
					blinkTime = 0.5
					GPIO.output(led2Pin,1)
                    time.sleep(3)
					GPIO.output(led2Pin,0)
            if GPIO.input(cdsPin) == 1: #detect light
                    dt_now = datetime.datetime.now()
                    f.write(str(dt_now) + '\n')
                    f.close()
                    f = open(path, mode ="a")
                    print(dt_now)
                    if flagSwitch == 1 :
                        GPIO.output(ledPin,0) #led ON ,Motor ON
                        time.sleep(1)
                        ServoPhone.SetPos(phoneGetPos) #phone off (get phone)
                        time.sleep(2)
                        ServoBttm.SetPos(bttmPushPos)
                        time.sleep(1)
                        ServoBttm.SetPos(bttmInitPos)
                        time.sleep(1)
                        ServoPhone.SetPos(phoneInitPos)
                        time.sleep(1)
                        GPIO.output(21,0)
                        GPIO.output(20,0)
                        GPIO.output(ledPin,1) #led OFF ,Motor OFF
                    else : 
						#flagSwitch = 0
						#print("sleep 30 \n")
						time.sleep(30)
						time.sleep(1-blinkTime)
    except KeyboardInterrupt  :         #Ctl+Cが押されたらループを終了
        print("\nCtl+C")
    except Exception as e:
        print(str(e))
    finally:
		GPIO.output(ledPin,0) #led ON ,Motor ON
        ServoBttm.Cleanup(pos=bttmInitPos)
        ServoPhone.Cleanup(pos=phoneInitPos)
		GPIO.output(ledPin,1) #led OFF ,Motor OFF
        GPIO.cleanup()
        f.close()
        print("\n exit program")
