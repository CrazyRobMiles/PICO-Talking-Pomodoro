import board
import busio
import time
import random
import rotaryio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer
from DFPlayer import DFPlayer
from adafruit_ht16k33 import segments

Version = "Version 1.0"

class PomodoroTimer():
    
    TIMER_STARTING = 71
    TIMER_TIME_OVER = 72
    TIMER_HOURS_AND = (60,61,62,63,64,65,66)
    TIMER_HOURS = (73,74,75,76,77,78,79)
    TIMER_GONE = 70
    TIMER_TIME_LEFT = 69
    TIMER_DING = 68
    TIMER_ZERO_MINS = 80
    
    def blocking_sound_play(self,track_no):
        self.dfplayer.play(track=track_no)
        while self.dfplayer.get_status() == 513:
            pass
    
    def __init__(self, i2c_sda,i2c_scl,
                 play_tx,play_rx,vol,
                 encoder_a,encoder_b,encoder_button,
                 time_button
                 ):
        # Make i2c connection
        self.i2c = busio.I2C(i2c_scl, i2c_sda)
        # Make display
        self.display = segments.Seg14x4(self.i2c)
        self.display.fill(0)
        self.display.print('Hi  ')
        # Make mp3 player
        self.uart = busio.UART(tx=play_tx, rx=play_rx)
        self.dfplayer = DFPlayer(uart=self.uart,volume=vol)
        # Make encoder
        self.encoder= rotaryio.IncrementalEncoder(encoder_a, encoder_b)
        # Make encoder button
        tmp_pin = DigitalInOut(encoder_button)
        tmp_pin.pull = Pull.UP
        self.encoder_button = Debouncer(tmp_pin,interval=0.01)
        # Make time button
        tmp_pin = DigitalInOut(time_button)
        tmp_pin.pull = Pull.UP
        self.time_button = Debouncer(tmp_pin,interval=0.01)
    
    def test(self):
        print("Pomodoro Self Test",Version)
        # record the current encoder position
        old_enc_pos=self.encoder.position
        # say hello
        self.display.print("Test")
        # loop forever
        while True:
            # update the button on the encoder
            self.encoder_button.update()
            # has the encoder button been pressed?
            if self.encoder_button.fell:
                # print a message if the button was pressed
                print("Encoder pressed")
            # update the time button
            self.time_button.update()
            # has the time button been pressed
            if self.time_button.fell:
                # print a message
                print("Time pressed")
                # play some messages
                self.blocking_sound_play(67)
                self.blocking_sound_play(61)
                self.blocking_sound_play(25)
            # get the encoder position
            enc_pos=self.encoder.position
            # has the encoder been turned?
            if enc_pos != old_enc_pos:
                # display the encoder position
                self.display.fill(0)
                self.display.print(enc_pos)
                # record the old encoder position
                old_enc_pos = enc_pos
    
    def display_text(self,message):
        self.display.marquee(message,delay=0.2,loop=False)
        
    def pick_option(self,options):
        option=0
        self.display.fill(0)
        self.display.print(options[0])
        old_enc_pos=self.encoder.position
        while True:
            enc_pos=self.encoder.position
            if enc_pos != old_enc_pos:
                diff= enc_pos-old_enc_pos
                option = option + diff
                if option<0:
                    option=len(options)-1
                if option>=len(options):
                    option=0
                self.display.fill(0)
                self.display.print(options[option])
                old_enc_pos = enc_pos
            self.encoder_button.update()
            if self.encoder_button.fell:
                return option
            
    def display_time_mins(self,mins):
        h = mins // 60
        m = mins % 60
        self.display_time(m,h)
        
    def display_time(self,m,h):
        s=f'{h:02d}{m:02d}'
        self.display.fill(0)
        self.display.print(s)

    def read_time(self,max_hours=7):
        mins=0
        hours=0
        old_enc_pos=self.encoder.position
        while True:
            enc_pos=self.encoder.position
            if enc_pos != old_enc_pos:
                diff= enc_pos-old_enc_pos
                mins = mins + diff
                if mins<0:
                    if hours>0:
                        hours = hours-1
                        mins=mins+60
                    else:
                        mins=0
                if mins>59:
                    if hours<max_hours:
                        hours=hours+1
                        mins=mins-60
                    else:
                        mins=59
                old_enc_pos = enc_pos
                self.display_time(mins,hours)
            self.encoder_button.update()
            if self.encoder_button.fell:
                if mins != 0 or  hours != 0:
                    break
        return mins + (hours * 60)
    
    def announce_time(self,mins):
        dh = mins // 60
        dm = mins % 60
        if dh==0:
            if dm==0:
                self.blocking_sound_play(PomodoroTimer.TIMER_ZERO_MINS)
            else:
                self.blocking_sound_play(dm)
        else: 
            if dm == 0:
                # Just announce the hour
                self.blocking_sound_play(PomodoroTimer.TIMER_HOURS[dh-1])
            else:
                # Announce the hour and minute
                self.blocking_sound_play(PomodoroTimer.TIMER_HOURS_AND[dh-1])
                self.blocking_sound_play(dm)
    
    def time_session(self):
        # Display setting prompt
        self.display_text("Set ")
        # Read the duration of the timer
        timer_duration_mins = self.read_time()
        # Are we counting up or down for display and sounds?
        count_up = self.pick_option(("Up  ","Down")) == 0
        # What kind of feedback do we want?
        #  None-0 -> no display, only the end sound
        #  Disp-1 -> just display the count values
        #  Five-2 -> display and announce every five minutes
        #  Ten-3 -> display and announce every ten minutes
        #  Rand-4 -> display and announce at random times
        feedback_type = self.pick_option(("None","Disp","Five","Ten ","Rand"))
        # Select go to start the timer
        self.pick_option(("Go",))
        # Record the start time
        start_time = time.monotonic()
        # Clear the display
        self.display.fill(0)
        # For any of the announcing feedback types - say the timer is starting
        if feedback_type > 1:
            self.blocking_sound_play(PomodoroTimer.TIMER_STARTING)
        # Force an update first time through the loop
        last_min = None
        # Set the time for the first random announcement
        # between 5 and 11 minutes
        random_time = random.randint(5,11)
        # Main timer loop
        while True:
            elapsed_secs = time.monotonic()-start_time
            elapsed_mins = int(elapsed_secs / 60)
            mins_left = timer_duration_mins - elapsed_mins
            # Only want to play one sound per loop
            play_sound = False
            if count_up:
                display_mins = elapsed_mins
                display_sound = PomodoroTimer.TIMER_GONE
            else:
                display_mins = mins_left
                display_sound = PomodoroTimer.TIMER_TIME_LEFT
            if last_min == None or last_min != elapsed_mins:
                last_min = elapsed_mins
                if feedback_type>0:
                    # minute has changed
                    self.display_time_mins(display_mins)
                if feedback_type==2:
                    # feedback every 5 minutes
                    if display_mins > 0 and display_mins % 5 == 0:
                        play_sound=True
                elif feedback_type==3:
                    # feedback every 10 minutes
                    if display_mins > 0 and display_mins % 10 == 0:
                        play_sound=True
                elif feedback_type==4:
                    # feedback at random minutes
                    if elapsed_mins >= random_time:
                        random_time = random_time + random.randint(5,11)
                        play_sound=True
                        
            # Check if an announcement has been requested
            self.time_button.update()
            if self.time_button.fell:
                play_sound=True
            
            # Check if the user wants to abort the time
            self.encoder_button.update()
            if self.encoder_button.fell:
                if self.pick_option(("Stop","Cont")) == 0:
                    break
                else:
                    self.display_time_mins(display_mins)

            # Play a sound if one was requested
            if play_sound:
                self.announce_time(display_mins)
                self.blocking_sound_play(display_sound)
            
            # Check for end of timer
            if elapsed_mins == timer_duration_mins:
                # timer done
                break
            
        # Timer complete
        if feedback_type == 0:
            end_sound = PomodoroTimer.TIMER_DING
        else:
            end_sound = PomodoroTimer.TIMER_TIME_OVER
        
        self.display.fill(0)
        self.display.print("Done")
        self.blocking_sound_play(end_sound)
        
        
    def run(self):
        print("Pomodoro Timer Rob Miles (www.robmiles.com)",Version)
        while True:
            self.time_session()
                
timer = PomodoroTimer(i2c_sda=board.GP0, i2c_scl=board.GP1,
                 play_tx=board.GP4,play_rx=board.GP5,vol=60,
                 encoder_a=board.GP8,encoder_b=board.GP9,encoder_button=board.GP16,
                 time_button=board.GP22
                 )
timer.run()
