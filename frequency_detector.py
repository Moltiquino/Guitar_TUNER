import numpy as np
import pyaudio
import time
import pyfirmata


port = 'COM5'
HIGH = True# Create a high state for turn on led 
LOW = False # Create a low state for turn off led 
board = pyfirmata.Arduino(port) # Initialize the communication with the Arduino card
LED_pin = board.get_pin('d:13:o') # Initialize the pin (d => digital, 13 => Number of the pin, o => output)
buttonpin=2
lpin=13
buttonstate=0
laststate=0



def freq_dect():

    Notemin = 51
    Notemax = 69
    sampfreq = 22050
    framesize = 2048
    frames_per_fft = 16
    netfreq=0
    

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

    window = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, SAMPLES_PER_FFT, False)))
    print ('sampling at', sampfreq, 'Hz with max resolution of', FREQ_STEP, 'Hz')
    print ()

    while stream.is_active():

        
        buf[:-framesize] = buf[framesize:]
        buf[-framesize:] = np.fromstring(stream.read(framesize), np.int16)

        
        fft = np.fft.rfft(buf * window)

        
        freq = (np.abs(fft[imin:imax]).argmax() + imin) * FREQ_STEP

        
        n = freq_to_number(freq)
        n0 = int(round(n))

        
        num_frames += 1

        if num_frames >= frames_per_fft:
            print ('freq: {:7.2f} Hz     note: {:>3s} {:+.2f}'.format(
                freq, note_name(n0), n-n0))





freq_dect()
