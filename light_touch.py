import launchpad_util
import random
import time
import sys

launchpad_util.connect()
launchpad_util.clear_all_led()

def on_touch(message, data):
    did_touch = (message[0][2] == 127)
    led = message[0][1]
    if did_touch:
        # print "Touched LED %s" % (led)
        color = random.randint(1, 127)
        launchpad_util.set_led_color(led, color)
    else:
        # print "Released LED %s" % (led)
        launchpad_util.clear_led(led)

launchpad_util.subscribe_touch(on_touch)


def main_loop():
    while 1:
        # do your stuff...
        time.sleep(0.1)

if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print >> sys.stderr, '\nExiting by user request.\n'
        launchpad_util.clear_all_led()
        sys.exit(0)