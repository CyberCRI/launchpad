import launchpad_util
import random
import time
import sys

launchpad_util.connect()
launchpad_util.clear_all_led()

text = sys.argv[1]

color = random.randint(1, 127)

launchpad_util.scroll_text(text, color, True)

def main_loop():
    while 1:
        # do your stuff...
        time.sleep(0.1)

if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print >> sys.stderr, '\nExiting by user request.\n'

        launchpad_util.cancel_scroll_text()
        sys.exit(0)