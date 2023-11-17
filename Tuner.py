import numpy as np
import pyaudio
import time
import pyfirmata
# import board
import digitalio

# from board import SCL,SDA
# import busio
# import adafruit_ssd1306

port = 'COM5'

WIDTH = 128
HEIGHT = 64 
BORDER = 5



# spi = board.SPI()
# oled_reset = digitalio.DigitalInOut(board.D4)
# oled_cs = digitalio.DigitalInOut(board.D5)
# oled_dc = digitalio.DigitalInOut(board.D6)
# oled = adafruit_ssd1306.SSD1306_SPI(WIDTH, HEIGHT, spi, oled_dc, oled_reset, oled_cs)



HIGH = True# Create a high state for turn on led 
LOW = False # Create a low state for turn off led 
board = pyfirmata.Arduino(port) # Initialize the communication with the Arduino card
LED1 = board.get_pin('d:12:o') # Initialize the pin (d => digital, 13 => Number of the pin, o => output)
LED2 = board.get_pin('d:11:o')
LED3 = board.get_pin('d:10:o')
LED4 = board.get_pin('d:9:o')
LED5 = board.get_pin('d:8:o')
LED6 = board.get_pin('d:7:o')
LED7 = board.get_pin('d:3:o')
button = board.digital[2]
in1 = board.get_pin("d:5:o")
in2 = board.get_pin("d:6:o")
LEDs = [LED1,LED2,LED3,LED4,LED5,LED6]
standF = [330.00,242.00,392.00,293.00,220.00,164.00]
LED_index=-1

buttonstate=0
laststate=0
freq=0
press_Time = 0
release_Time = 0
diff=0

it = pyfirmata.util.Iterator(board)
it.start()

def freq_dect(stdfreq):

    Notemin = 51
    Notemax = 69
    sampfreq = 22050
    framesize = 2048
    frames_per_fft = 16
    netfreq=0
    diff=0
    

    SAMPLES_PER_FFT = framesize*frames_per_fft
    FREQ_STEP = float(sampfreq)/SAMPLES_PER_FFT


    NOTE_NAMES = 'C C# D D# E F F# G G# A A# B'.split()

    def freq_to_number(f): return 69 + 12*np.log2(f/440.0)
    def number_to_freq(n): return 440 * 2.0**((n-69)/12.0)
    def note_name(n): return NOTE_NAMES[n % 12] + str(n/12 - 1)

    def note_to_fftbin(n): return number_to_freq(n)/FREQ_STEP
    imin = max(0, int(np.floor(note_to_fftbin(Notemin-1))))
    imax = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(Notemax+1))))


    buf = np.zeros(SAMPLES_PER_FFT, dtype=np.float32)
    num_frames = 0

    stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                    channels=1,
                                    rate=sampfreq,
                                    input=True,
                                    frames_per_buffer=framesize)

    stream.start_stream()
    # start_time = time. time()
    # seconds = 2.0   

    window = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, SAMPLES_PER_FFT, False)))
    print ('sampling at', sampfreq, 'Hz with max resolution of', FREQ_STEP, 'Hz')
    print ()

    while stream.is_active():
        # current_time=time.time()
        # elapsed_time=current_time-start_time
        
        buf[:-framesize] = buf[framesize:]
        buf[-framesize:] = np.fromstring(stream.read(framesize), np.int16)

        
        fft = np.fft.rfft(buf * window)


        freq = round((np.abs(fft[imin:imax]).argmax() + imin) * FREQ_STEP,0)

        
        n = freq_to_number(freq)
        n0 = int(round(n))

        
        num_frames += 1
        netfreq += freq
        if num_frames >= frames_per_fft:
            print ('freq: {:7.2f} Hz     note: {:>3s} {:+.2f}'.format(freq, note_name(n0), n-n0))
            print(freq-stdfreq)
        

        if(freq-stdfreq>2):
            if((stdfreq==standF[0])|(stdfreq==standF[1])|(stdfreq==standF[2])):
                counterclockwise()
            else:
                clockwise()


            time.sleep(0.2)
        elif(freq-stdfreq<-2):
            if((stdfreq==standF[0])|(stdfreq==standF[1])|(stdfreq==standF[2])):
                clockwise()
            else:
                counterclockwise()

            
            time.sleep(0.2)
        elif(freq-stdfreq>=-2 or freq-stdfreq<=2) : 
            stop()
            time.sleep(0.2)
            LED7.write(1)
            time.sleep(2)
            LED7.write(0)
            for LED in LEDs:
                LED.write(0)

            break

 
def counterclockwise():
    in1.write(1)
    in2.write(0)
    for a in reversed(range(-1,5)):
        
        LEDs[a+1].write(0)
        time.sleep(0.039)
        LEDs[a].write(1)
        
        
    
def clockwise():
    in2.write(1)
    in1.write(0)
   
    for a in range(-1,5):
        LEDs[a].write(0)
        time.sleep(0.039)
        LEDs[a+1].write(1)
        

    
def stop():
    in1.write(0)
    in2.write(0)



button.mode = pyfirmata.INPUT
   
for LED in LEDs:
    LED.write(0)

while(True):
    
   
    buttonstate=button.read()
    time.sleep(0.01)
    if(laststate == 0 and buttonstate == 1):
        press_Time=time.time()
    if(laststate == 1 and buttonstate == 0):
        release_Time=time.time()
    
    
    if((buttonstate!=laststate)):
        if((release_Time-press_Time)<1):
            if (buttonstate==0):
                LEDs[LED_index].write(0)
                LED_index+=1
                if LED_index>=len(LEDs):
                    LED_index=0
                LEDs[LED_index].write(1)
       
        if ((release_Time-press_Time)>1):
            
           
            for i in range(6):    
                if(LEDs[i].read()==1):
                    time.sleep(1)
                    LEDs[i].write(0)
                    time.sleep(1)
                    LEDs[i].write(1)
                    time.sleep(1)
                    

                    freq_dect(standF[i])
                    LEDs[i].write(1)
                    time.sleep(1)
                    stop()
                

        else : stop()
                   
    laststate=buttonstate

  #this is a test
    
        
    
    
   
    

   
        
   

    




