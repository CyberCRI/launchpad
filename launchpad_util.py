import rtmidi

midiout = None
midiin = None

def connect(port = 0):
    global midiout, midiin
    
    midiout = rtmidi.MidiOut()
    midiin = rtmidi.MidiIn()
    available_ports = midiout.get_ports()

    if available_ports:
        midiout.open_port(port)
        midiin.open_port(port)
    else:
        raise Exception("Cannot connect")

def set_led_color(led, color):
    midiout.send_message([144, led, color])

def clear_led(led):
    set_led_color(led, 0)

def send_sysex(message_body):
    midiout.send_message([240, 0, 32, 41, 2, 24] + message_body + [247])

def set_all_led_color(color):
    send_sysex([14, color])

def clear_all_led():
    set_all_led_color(0)

def scroll_text(text, color, loop = False):
    ascii_array = [ord(c) for c in text]
    send_sysex([20, color, loop and 1 or 0] + ascii_array)

def cancel_scroll_text():
    send_sysex([20])

# cb is a function that takes two parameters ((message, time), data)
def subscribe_touch(cb, data=None):
    midiin.set_callback(cb, data)

