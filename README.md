# PICO Talking Pomodoro

Designs and software for a PICO Talking Pomodoro presented in Hackspace magazine.

![Talking Pomodoro in a box](images/timer.jpg)

## Using the Pomodoro
When you power up the device it says Hi and then displays "Set". Set the time by turning the rotary encoder to select the number of hours and minutes that you want the timer to run for. When you have selected the time, push in the encoder. The screen will now display "Up". 

If you want the timer to count elapsed time press in the encoder. If you want to count down (and tell you how much time is left) turn the encoder until "Down" is displayed. When you have selected the required directin, push in the encoder. 

Now you select the feedback that you want. You can rotate the encoder to select between "None", "Disp", "Five", "Ten" and "Rand":

* None - the time will not be displayed. The timer will play a chime when the time completes
* Disp - the time will be displayed but the timer will be silent.
* Five - the time will be displayed and the timer will announce the time every five minutes. 
* Ten - the time will be displayed and the timer will announce the time every Ten minutes. 
* Rand - - the time will be displayed and the timer will announce the time at random intervals.

To hear the time at any other point, press the button. 

To stop the timer early press in on the rotary control and select "Stop" from the menu that appears. If you select "Cont" the timer will continue.

## Sound files

The Sounds folder contains the MP3 samples used for the announcements. These must be copied onto a MicroSD card which is inserted into the DFPlayer. Note that they must be copied in order as the player ignores filenames and just uses the file position in the folder. If you copy all the files at once they may not be copied in the correct oder. The program FileCopier.py in the sounds folder can be used to copy the files one at a time into a card. 

## Program files

You can find the Circuit Python program in the Code folder. Store this as code.py on your device so that it runs when it is powered up. Make sure you are using Version 7 of Circuit Python. 

## Lib

The timer uses a collection of Circuit Python library files that must be stored in the lib folder on your device. The lib folder contains all the requried files. Copy the contents into the lib folder on your device. 
