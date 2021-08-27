# Macropad-Sequencer
8-step MIDI sequencer to run on an Adafruit Macropad

# Setup
Follow the instructions for assembling your Adafruit Macropad, setting up the bootloader and Circuit Python here: https://learn.adafruit.com/adafruit-macropad-rp2040
Once you have the Macropad booted, drag the following libraries from the Python bundle you downloaded to the Macropad’s lib folder:
adafruit_display_text
adafruit_hid
adafruit_led_animation
adafruit_midi
adafruit_debouncer.mpy
adafruit_macropad.mpy
adafruit_simple_text_display.mpy
neopixel.mpy
Open up the code.py file on the Macropad in your favorite editor and replace the code with the code in this repository. When you save it, the Macropad should reboot and run the program.

# Usage

The sequencer has four modes which can be selected by using the lower row of buttons:
Note On/Off (blue)
Pitch (green)
Velocity (yellow)
Legato/Note Length (pink)

On/Off Mode
 When it starts up it is in On/Off mode. In this mode, pressing any of the keys in the top two rows will toggle that step of the sequence on or off. When a note is off, the light for that step is off and the sequencer will play a rest on that step. In On/Off mode, turning the knob will adjust the tempo and update the BPM on the display. Pressing the knob will turn all notes back on again.

Pitch Mode
Pressing the green key on the lower row will switch the sequencer to Pitch mode where you can adjust the note for each of the 8 steps. To select a step press the key for that step in one of the two top rows. When selected, the step’s color will change to white. While a note is selected, turning the knob will change the selected step’s midi value up or down by a semitone and display the new note name in the display next to the word SET. If no note is selected, turning the knob adjusts the BPM by default. Pressing the knob in Pitch mode, resets all notes to the default pitches.

Velocity Mode
Pressing the yellow key on the lower row will switch the sequencer to Velocity mode where you can adjust the velocity of each step. As with pitch mode, the selected step will be white and the knob will adjust the velocity for that step. Turning a velocity all the way to zero turns the note off. Pressing the knob resets the velocity for all steps to full on (127).
Legato/Note Length Mode
Pressing the pink key on the lower row will switch the sequencer to Legato mode where you can adjust the note length for each step. The length of each step is intentionally limited to 0.4 to 0.9 which seems to keep things in a range that plays well. Pressing the knob resets all steps to a default of 0.9.

# Customizing the Code

There are some things in the code that you may wish to customize to your tastes such as:

colors- The various colors are defined as variables near the beginning of the code and these can be changed to whatever you wish

default_pitches- this list of midi notes is what is used during start up or a knob press as the default sequence it plays. This can be changes to whatever notes you feel are good for a preset. 

tempo variables- the tempo, min_tempo, and max_tempo variables can be modified to what the default BPM is as well as the min/max possible variables.

# Issues

I’ve noticed that when you’re adjusting a selected step in Pitch/Velocity/Legato modes, if you turn the knob too fast while the sequencer plays through that step it can cause a bit of a MIDI glitch. This glitch usually only lasts a step or two, or until the beginning of the sequence at worst. I think that it is because there is a delay in sending the MIDI off message and so a note gets stuck on temporarily. If anyone sees anything in my code that might be contributing to this, feel free to send a pull request.
