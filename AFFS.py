##########################################################################################
    ## This is a Top-level control module for Automatic Fish Feeder System(AFFS).   ##
    ## AFFS is a ECE senior design-1 project at Mississippi State University,       ##
    ## Starkville, MS. This module controls the overall software flow of the system ##
    ## by empoying parallel programing approach (uses fork and pipe).               ##
    ## In other word, it is a operating system of the AFFS. It has following basic  ##
    ## functionalities:                                                             ##
    ## 1. record video as a raw "h264" video file.                                  ##
    ## 2. read RFID tags continously                                                ##
    ## 3. write information into CSV file                                           ##
    ## 4. trigger motor rotation                                                    ##
    ##--------------------------All right reserved----------------------------------##
    ## Author : Deepak Chapagain, Collin Hoffman, Rose Jensen, Asmita Niroula,      ##
    ##          Luis Jose Domingue                                                  ##
    ## Last Modified  : 11/27/2018                                                  ##
##########################################################################################

from picamera import PiCamera
import RPi.GPIO as GPIO
import os, sys, errno, time, serial, datetime, csv


#--------------------------Child Process---------------------------------------------------
def child(r):
    while True:
        CAMERA_READY = os.read(r,1)
        print("Camera Ready: ",CAMERA_READY)
        
        if(CAMERA_READY=="1"):
            # Fork again to work with motor
            pid2 = os.fork()
            if(pid2 <0):
                print("Could not fork\n")
            else:
                if(pid2>0):
                    get_video()
                    time.sleep(2)
                    os._exit(pid2)
                    
                if(pid2 ==0):
                    # Add motor code here
                    GPIO.setmode(GPIO.BOARD)
                    servoPin=11
                    GPIO.setup(servoPin, GPIO.OUT)
                    pwm=GPIO.PWM(servoPin,50)
                    pwm.start(7)
                    for i in range(0,180):
                            DC=1./18.*(i)+2
                            pwm.ChangeDutyCycle(DC)
                    for i in range(180,0):
                            DC=1./18.*i+2
                            pwm.ChangeDUtyCycle(DC)
                    pwm.stop()
                    GPIO.cleanup()
                    print("Motor")
            
            
    
#---------------------------Parent Process-----------------------------------------------
def parent(w):
    import serial
    port = serial.Serial(
        port='/dev/ttyACM0',
        baudrate = 9600,
        parity = serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout = 1
    )
    
    with open("/home/pi/SD_Project/data/IDs.csv","a+") as myCSV:
        wr = csv.write(myCSV)
        wr.writerow(['Date and Time\n','ID Numbers\n','Video Files\n'])
    
    # Read tags
    while True:
        x = port.readline()
        if x[0:4] == "num:":
            ID = x[4:]
            # Write id and time to CSV file
            wr.writerow([time.ctime(), ID, 'sample.h264'])
            print(ID)
            y = "1"
            # Pipe it to child process
            os.write(w,y)
            
        else:
            print(x)
                    
            
#-----------------------------Camera Method-------------------------------------------------
def get_video():
    #create camera object
    camera = PiCamera()
    #import current time
    x = datetime.datetime.now()
    # import time stamp for file name
    year = x.strftime("%Y")
    month = x.strftime("%m")
    day = x.strftime("%d")
    hour = x.strftime("%H")
    minute = x.strftime("%M")
    second = x.strftime("%S")
    filename = year+month+day+'_'+hour+minute+second+'.h264'
    print("Start recording...")
    camera.start_recording('/home/pi/SD_Project/data/'+filename)
    time.sleep(5)
    camera.stop_recording()
    #time.sleep(1)
    print("Recording saved as "+filename)
    return
    
    
    
#----------------------------- Main---------------------------------------------------
def main():
    # Create pipe
    r,w = os.pipe()
    #Fork to run parallel programming
    pid = os.fork()
    CAMERA_READY = 0
    if(pid <0):
        print("Could not fork\n")
        sys.exit()
    
    if(pid > 0):
        parent(w)
    if(pid==0):
        child(r)
        
main()     
        
    
#-----------------------------End of File------------------------------------------------
            
            
