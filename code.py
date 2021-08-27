# some of the midi code derived from John Park's macropad tutorial
import time

from adafruit_macropad import MacroPad

macropad = MacroPad(rotation=90)    # orientation horizontal, knob left

# colors
active_color = (255, 0, 0)          # color when key is active step
inactive_color = (0, 0, 0)          # color when note turned off
on_off_color = (0, 0, 32)           # base color for  on/off mode
pitch_color = (0, 32, 0)            # base color for pitch mode
velocity_color = (32, 32, 0)        # base color for velocity mode
legato_color = (32, 0, 32)          # base color for legato mode
selected_color = (255, 255, 255)    # color when key selected
base_color = on_off_color           # init base color to on/off mode

macropad.pixels.brightness = 0.2    # default brightness

# set default colors on keys
for x in range(8):
    macropad.pixels[x] = on_off_color
macropad.pixels[8] = on_off_color
macropad.pixels[9] = pitch_color
macropad.pixels[10] = velocity_color
macropad.pixels[11] = legato_color

# 8-step lists for storing the state of the sequencer
default_pitches = [36, 40, 39, 42, 41, 38, 39, 40]
note_on_map = [True] * 8                        # step on/off state
pitch_map = default_pitches                     # step pitch
velocity_map = [127] * 8                        # step velocity
legato_map = [0.90] * 8                          # step length

sel_key = None                                  # currently selected key

# MIDI variables
mode = 0
mode_text = ["  On/Off", " MIDI Note", " Velocity", "  Length"]
note_names = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
octave = 2

# variables for storing user input info
last_knob_pos = macropad.encoder    # store encoder rotation value
key = None                          # for storing last key pressed

# variables for timing
tempo = 180                         # beats (quarter notes) per minute
min_tempo = 10
max_tempo = 480
current_step = 7                    # number of steps per beat

# display text setup
text_lines = macropad.display_text(" SEQUENCER")
text_lines[0].text = "   Mode:"
text_lines[1].text = "  On/Off"
text_lines[2].text = " "
text_lines[3].text = "BPM: %d" % tempo
text_lines.show()

while True:
    stamp = time.monotonic()  # store current time stamp

    # next beat!
    current_step = (current_step + 1) % 8

    # updateUI
    for step in range(8):
        if note_on_map[step]:
            if (step == sel_key) and (mode != 0):
                macropad.pixels[step] = selected_color
            else:
                macropad.pixels[step] = base_color
        else:
            macropad.pixels[step] = inactive_color
    if note_on_map[current_step]:
        macropad.pixels[current_step] = active_color

    text_lines[3].text = "BPM: %d" % tempo

    if mode == 1:
        note = pitch_map[current_step]
        octave = ((note - 4) // 12) + 1
        note_name = note_names[(note % 12) - 1]
        text_lines[4].text = ("CUR:%d/%s%d" % (note, note_name, octave))
    if mode == 2:
        text_lines[4].text = ("Vel: %d" % velocity_map[current_step])
    if mode == 3:
        text_lines[4].text = ("Length: %f" % legato_map[current_step])

    while time.monotonic() - stamp < 60/tempo: # while elapsed time < 1 beat
        noteDuration = (60/tempo) * legato_map[current_step]
        # if current step on, play MIDI
        if note_on_map[current_step]:
            if time.monotonic() - stamp < noteDuration:
                macropad.midi.send(macropad.NoteOn(pitch_map[current_step], velocity_map[current_step]))
            else:
                macropad.midi.send(macropad.NoteOff(pitch_map[current_step], 0))

        # Check for pressed buttons and store relevent info
        key_events = macropad.keys.events.get()
        if key_events:
            if key_events.pressed:
                key = key_events.key_number
        else:
            key = None
        if key is not None:
            if key < 8:   # if user is trying to do something with a step
                if mode == 0:
                    # if we're in on/off mode, pressing a key
                    # toggles it off or on
                    note_on_map[key] = not note_on_map[key]
                else:
                    # if we're in any other mode, pressing a key
                    # clears previous selection and makes the
                    # pressed key the new selection
                    if note_on_map[key]:
                        if key == sel_key:
                            sel_key = None
                            text_lines[4].text = ""

                        else:
                            sel_key = key
            else:
                # pressing lower row keys changes mode
                # and sets the key color for that mode
                if key == 9:
                    mode = 1
                    base_color = pitch_color
                    text_lines[1].text = "   Pitch"
                elif key == 10:
                    mode = 2
                    base_color = velocity_color
                    text_lines[1].text = "  Velocity"
                elif key == 11:
                    mode = 3
                    base_color = legato_color
                    text_lines[1].text = "   Legato"
                else:
                    mode = 0
                    base_color = on_off_color

        # encoder button press resets everything to default for current mode
        macropad.encoder_switch_debounced.update()
        if macropad.encoder_switch_debounced.pressed:
            # if the button is pressed, we'll clear automation for the mode we're in
            if mode == 0:
                for x in range(8):
                    note_on_map[x] = True
            elif mode == 1:
                pitch_map = [36, 40, 39, 42, 41, 38, 39, 40]
            elif mode == 2:
                for x in range(8):
                    velocity_map[x] = 127
            elif mode == 3:
                for x in range(8):
                    legato_map[x] = 0.5

        # encoder knob turns change bpm in on/off mode
        # and change selected step's value in other modes
        # if nothing is selected it will change bpm no matter the mode
        if last_knob_pos is not macropad.encoder: # the knob has been turned
            knob_pos = macropad.encoder
            knob_delta = knob_pos - last_knob_pos
            last_knob_pos = knob_pos

            text_lines[3].text = ("BPM: %d" % tempo)

            if mode is 0: # ON/OFF
                tempo = tempo + (knob_delta * 5)
                tempo = min(max(tempo, 10), 480)
            if mode is 1: # PITCH
                if sel_key != None:
                    sel_pitch = pitch_map[sel_key]
                    # turn off note we're going to change so we don't
                    # end up with hanging midi-on signals
                    macropad.midi.send(macropad.NoteOff(sel_pitch, 0))
                    sel_pitch = sel_pitch + knob_delta
                    sel_pitch = min(max(sel_pitch, 0), 127)
                    text_lines[5].text = ("SEL: %d" % sel_pitch)
                    pitch_map[sel_key] = sel_pitch
                else:
                    tempo = tempo + (knob_delta * 5)
                    tempo = min(max(tempo, 10), 480)
            if mode is 2: # VELOCITY
                if sel_key != None:
                    sel_vel = velocity_map[sel_key]
                    sel_vel = sel_vel+ knob_delta
                    sel_vel = min(max(sel_vel, 0), 127)
                    text_lines[5].text = ("SET:%d" % sel_vel)
                    velocity_map[sel_key] = sel_vel
                else:
                    tempo = tempo + (knob_delta * 5)
                    tempo = min(max(tempo, 10), 480)
            if mode is 3: # LEGATO
                if sel_key != None:
                    sel_length = legato_map[sel_key]
                    sel_length = sel_length + (knob_delta * 0.05)
                    sel_length = min(max(sel_length, 0), .95) # setting this to 1. bugs out
                    text_lines[5].text = ("SET %d: %f" % (sel_key,sel_length))
                    legato_map[sel_key] = sel_length
                else:
                    tempo = tempo + (knob_delta * 5)
                    tempo = min(max(tempo, 10), 480)

            last_knob_pos = macropad.encoder

        time.sleep(0.01)  # a little delay here helps avoid debounce annoyances