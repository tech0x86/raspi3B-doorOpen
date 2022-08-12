#!/usr/bin/python3
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import os
import datetime
import subprocess
import requests

FILE_PATH = "/home/pi3b1/Desktop/log.txt"
PATH_JTALK = "./jtalk.sh"

LINE_NOTIFY_TOKEN = os.environ.get("LINE_TOKEN")
LINE_NOTIFY_API = "https://notify-api.line.me/api/notify"


# pin assigment
PIN_CDS = 19
PIN_MOTOR_POWER = 13  # &motorDriver (0 is On)
PIN_LIFE_LED = 26
PIN_SWITCH_ACT_TRIG = 12  # black switch
PIN_MOTOR_UNLOCK = 20
PIN_MOTOR_TALK = 21

MOT_POS_INIT = 90
MOT_POS_PUSH = 60

FLAG_SWITCH_ACT = 0 # 1 :active unlocker mode
FLAG_LIGHT = 0 # 1 :detect light
LED_BLINK_TIME = 1.0

# サーボSG92Rをコントロールするためのクラス

class SG90_92R_Class:
    # mPin : GPIO Number (PWM)
    # mPwm : Pwmコントロール用のインスタンス
    # m_Zero_offset_duty :

    """コンストラクタ"""
    def __init__(self, Pin, ZeroOffsetDuty):
        self.mPin = Pin
        self.m_ZeroOffsetDuty = ZeroOffsetDuty

        # GPIOをPWMモードにする
        GPIO.setup(self.mPin, GPIO.OUT)
        self.mPwm = GPIO.PWM(self.mPin, 50)  # set 20ms / 50 Hz

    """位置セット"""
    def SetPos(self, pos):
        # Duty ratio = 2.5%〜12.0% : 0.5ms〜2.4ms : 0 ～ 180deg
        duty = (12-2.5)/180*pos+2.5 + self.m_ZeroOffsetDuty
        self.mPwm.start(duty)
    """終了処理"""
    def Cleanup(self, pos):
        # サーボを10degにセットしてから、インプットモードにしておく
        self.SetPos(pos)  # init pos (90)
        time.sleep(1)
        GPIO.setup(self.mPin, GPIO.IN)

# ラズパイでおしゃべりするやつ
# 引数：話す内容
def jtalk_script(message):
    subprocess.run([PATH_JTALK +" "+message],shell=True)

# line　に通知する
def send_line_message(notification_message):
    headers = {"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}
    data = {"message": f" {notification_message}"}
    requests.post(LINE_NOTIFY_API, headers = headers, data = data)

def act_switch_pushed(channel):
    print("act switch pushed")
    GPIO.remove_event_detect(PIN_SWITCH_ACT_TRIG)
    global FLAG_SWITCH_ACT
    global LED_BLINK_TIME

    if FLAG_SWITCH_ACT == 0:
        print("mode activated")
        jtalk_script("置き配受け取りモードオン")
        FLAG_SWITCH_ACT = 1
        LED_BLINK_TIME = 0.1
        GPIO.output(PIN_LIFE_LED, 1)
        time.sleep(3)
        GPIO.output(PIN_LIFE_LED, 0)
    else:
        print("mode deactivated")
        jtalk_script("通常モード")
        FLAG_SWITCH_ACT = 0
        LED_BLINK_TIME = 1.0
        GPIO.output(PIN_LIFE_LED, 1)
        time.sleep(3)
        GPIO.output(PIN_LIFE_LED, 0)
    
    GPIO.add_event_detect(PIN_SWITCH_ACT_TRIG, GPIO.RISING, callback=act_switch_pushed, bouncetime=2000) # 割り込み関数

def light_detected(channel):
    global FLAG_LIGHT
    print("detected light")
    GPIO.remove_event_detect(PIN_CDS)
    dt_now = datetime.datetime.now()
    print(dt_now)

#    f.write(str(dt_now) + '\n')
#    f.close()
#    f = open(FILE_PATH, mode="a")

    if FLAG_SWITCH_ACT == 1 and FLAG_LIGHT == 0: 
        FLAG_LIGHT = 1
        print("start unlock")
        GPIO.output(PIN_MOTOR_POWER, 0)  # Motor power ON
        time.sleep(1)
        motor_talk.SetPos(MOT_POS_PUSH)  # talk on
        jtalk_script("荷物は、玄関前に、置き配してください")
        send_line_message("荷物が届きました")
        time.sleep(4)
        motor_unlock.SetPos(MOT_POS_PUSH) # unlock bttn push
        time.sleep(1)
        motor_unlock.SetPos(MOT_POS_INIT) # unlock bttn unpush
        time.sleep(1)
        motor_talk.SetPos(MOT_POS_INIT) # talk off
        time.sleep(1)
        GPIO.output(PIN_MOTOR_UNLOCK, 0)
        GPIO.output(PIN_MOTOR_TALK, 0)
        GPIO.output(PIN_MOTOR_POWER, 1)  #Motor power OFF
        print("end unlock")
        FLAG_LIGHT = 0

    elif FLAG_SWITCH_ACT == 1 and FLAG_LIGHT == 1:
        print("sleep 10sec act1, light1")
        time.sleep(10.0)
    elif FLAG_SWITCH_ACT == 0 and FLAG_LIGHT == 1:
        print("sleep 10sec act0, light1")
        time.sleep(10.0)
    else:
        FLAG_LIGHT = 1
        print("sleep 30sec")
        jtalk_script("予定のないお客さんが来ましたよ")
        send_line_message("予定のないお客さんが来ました")
        time.sleep(30.0)
        print("sleep 30sec end")
        FLAG_LIGHT = 0
    GPIO.add_event_detect(PIN_CDS, GPIO.RISING, callback=light_detected, bouncetime=5000) # 割り込み関数

GPIO.setmode(GPIO.BCM)
motor_unlock = SG90_92R_Class(Pin=PIN_MOTOR_UNLOCK, ZeroOffsetDuty=0)
motor_talk = SG90_92R_Class(Pin=PIN_MOTOR_TALK, ZeroOffsetDuty=0)

"""コントロール例"""
if __name__ == '__main__':
    # Useing GPIO No.  to idetify channel
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_CDS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(PIN_CDS, GPIO.RISING, callback=light_detected, bouncetime=5000) # 割り込み関数
    GPIO.setup(PIN_MOTOR_POWER, GPIO.OUT) 
    GPIO.setup(PIN_LIFE_LED, GPIO.OUT)
    GPIO.setup(PIN_SWITCH_ACT_TRIG, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(PIN_SWITCH_ACT_TRIG, GPIO.RISING, callback=act_switch_pushed, bouncetime=2000) # 割り込み関数

    GPIO.output(PIN_MOTOR_POWER, 0)  #Motor power ON
    GPIO.output(PIN_MOTOR_UNLOCK, 0) #Motor ON
    GPIO.output(PIN_MOTOR_TALK, 0) #Motor ON
    motor_unlock.SetPos(MOT_POS_INIT)  #set init pos
    motor_talk.SetPos(MOT_POS_INIT)  #set init pos
    time.sleep(1)
    GPIO.output(PIN_MOTOR_POWER, 1)  # Motor power OFF
    
#    try:
#        f = open(FILE_PATH, mode="a")
#    except Exception as e:
#        print(str(e))
#        f.close()
    try:
        while True:
            GPIO.output(PIN_LIFE_LED, 1)
            time.sleep(LED_BLINK_TIME)
            GPIO.output(PIN_LIFE_LED, 0)
            time.sleep(2.0-LED_BLINK_TIME)

    except KeyboardInterrupt:  # Ctl+Cが押されたらループを終了
        print(" Ctl+C")
    except Exception as e:
        print(str(e))
    finally:
        GPIO.output(PIN_MOTOR_POWER, 0)  # Motor ON
        motor_unlock.Cleanup(pos=MOT_POS_INIT)
        motor_talk.Cleanup(pos=MOT_POS_INIT)
        time.sleep(1)
        GPIO.output(PIN_MOTOR_POWER, 1)  # Motor power OFF
        GPIO.cleanup()
        #f.close()
        print("exit program")