#IREC2020 Range Test
#Blake Patterson

import time
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
import adafruit_ssd1306
import adafruit_rfm9x
import subprocess

#Button Configuration
btnA = DigitalInOut(board.D5)
btnA.direction = Direction.INPUT
btnA.pull = Pull.UP
 
btnB = DigitalInOut(board.D6)
btnB.direction = Direction.INPUT
btnB.pull = Pull.UP
 
btnC = DigitalInOut(board.D12)
btnC.direction = Direction.INPUT
btnC.pull = Pull.UP

#I2C Interface
i2c = busio.I2C(board.SCL, board.SDA)

#OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)

#Clear the Display
display.fill(0)
display.show()
width = display.width
height = display.height
 
#Configure RFM9x LoRa Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

rfm9x = adafruit_rfm9x.RFM9x(spi,CS,RESET,915.0)

rfm9x.tx_power = 23 
 
def loRaDetectionTest():

    while True:
        display.fill(0)
 
        try:
            display.text('RFM9x: Detected', 0, 0, 1)
            display.show()
            time.sleep(5)
            return 1

        except RuntimeError as error:
            display.text('RFM9x: ERROR', 0, 0, 1)
            displa.show()
            print('RFM9x Error: ', error)
            return 0
  
        display.show()
        time.sleep(3)



#used if connect command is recieved
def loRaConnectionCommandTest():
    
    display.fill(0)
    display.show()
    display.text('Waiting for\nConnection\nPacket',0,0,1)
    display.show()

    while True:

        packet = None 
        packet = rfm9x.receive()
        i = 0
            
        if packet is not None:
            display.fill(0)
            display.show()
            display.text('Packet Receieved\nConnection Complete',0,0,1)
            display.show()

            while i < 3:
                message = bytes("reply","utf-8")
                rfm9x.send(message)
                time.sleep(1)
                i+=1

            time.sleep(3)

            run()    

#used if connection is intialized from this module master->slave
def loRaConnectionTest():

    display.fill(0)
    display.show()
    display.text('Sending Connection\nPacket',0,0,1)
    display.show()

    timeOut = 0

    while True:

        packet = None
        message = bytes("connect","utf-8")
        rfm9x.send(message)
        packet = rfm9x.receive()
        timeOut+=1
        time.sleep(1)

        if timeOut == 5:
            connectionError()

        if packet is not None:
            display.fill(0)
            display.show()
            display.text('Packet Receieved\nConnection Complete',0,0,1)
            display.show()
            time.sleep(3)
            run()    

def rssiCommandValue():

    display.fill(0)
    display.show()
    display.text('Recieved Command\nTo Send RSSI',0,0,1)
    display.show()

    i = 0

    while i < 3:

        message = bytes("garabage","utf-8")
        rfm9x.send(message)
        i+=1
        time.sleep(2)

    run()
       
def rssiValue():

    display.fill(0)
    display.show()
    display.text('Sending RSSI\nRecieve Packet',0,0,1)
    display.show()

    packet = None

    timeOut = 0

    while True:

        message = bytes("rssi","utf-8")
        rfm9x.send(message)
        time.sleep(1)
        packet = rfm9x.receive()

        timeOut+=1
        
        if timeOut == 5:
            connectionError()

        if packet is not None:
            display.fill(0)
            display.show()
            display.text(str(rfm9x.rssi),0,0,1)
            display.show()
            time.sleep(3)
            run()

def packetCommands(packets):
    
    commandList = ['connect','rssi','other'] #dynamic as needed

    for i in commandList:
        if str(i) == str(packets):
            x = commandList.index(packets)

            if x == 0:
                loRaConnectionCommandTest()

            elif x == 1:
                rssiCommandValue()


def connectionError():

    display.fill(0)
    display.show()
    display.text('Error in Connecting\nTo Module',0,0,1)
    display.show()

    time.sleep(3)

    run()
  
def run():

    display.fill(0)
    display.show()
    display.text('Waiting\nBtA Connect\nBtB RSSI\nBtC Reboot\n',0,0,1)
    display.show()

    prev_packet = None

    while True:

        packet = None;

        packet = rfm9x.receive()

        if packet is None:

#if button A this module will send packets to the slave module

            if not btnA.value: 

                if loRaDetectionTest() == 1:
                    loRaConnectionTest()

                elif loRaDetectionTest != 1:
                    connectionError()

#if button B this module will send packets for rssi to the slave module

            if not btnB.value:

                if loRaDetectionTest() == 1:
                    rssiValue()

                elif loRaDetectionTest() != 1:
                    connectionError()

#if button C this module will reboot

            if not btnC.value:
                display.fill(0)
                display.show()
                display.text('Waiting\nBtA Connect\nBtB RSSI\nBtC Reboot\n',0,0,1)
                subprocess.Popen(['sudo','reboot','-h','now'])


        else :
            prev_packet = packet
            packet_text = str(prev_packet,"utf-8")
            packetCommands(packet_text)
            

run()
