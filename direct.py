import launchpad_util
import random
import time
import sys
import collections
import copy


#### Utility functions ####

Position = collections.namedtuple('Position', ['x', 'y'])

def pos_to_led(pos):
    return 10 * (pos.y + 1) + pos.x + 1 

def led_to_pos(led):
    return Position(led % 10 - 1, led // 10 - 1)

def are_4_adjacent(pos_a, pos_b):
    diff_x = abs(pos_a.x - pos_b.x) 
    diff_y = abs(pos_a.y - pos_b.y)
    return diff_x == 1 and diff_y == 0 or diff_x == 0 and diff_y == 1 


Drop = collections.namedtuple('Drop', ['position', 'color'])

color_name_to_code = { "red": 5, "green": 32, "blue": 48, "white": 3 }

# type is 'solid', 'pulse', or 'blink'
DrawCommand = collections.namedtuple('DrawCommand', ['type', 'color'])

def make_empty_draw_buffer():
    # 8x8 matrix of drawing commands
    return [[None for x in range(8)] for y in range(8)]

def execute_draw_command(pos, command):
    led = pos_to_led(pos)

    launchpad_util.clear_led(led)

    if command == None:
        pass
    elif command.type == 'solid':
        launchpad_util.set_led_color(led, color_name_to_code[command.color])
    elif command.type == 'blink':
        launchpad_util.blink_led(led, color_name_to_code[command.color])
    elif command.type == 'pulse':
        launchpad_util.pulse_led(led, color_name_to_code[command.color])
    else:
        raise ValueError('command has unrecognized type: "%s"' % (command.type))

old_draw_buffer = make_empty_draw_buffer()
def draw(new_draw_buffer):
    global old_draw_buffer

    for y in range(8):
        for x in range(8):
            if new_draw_buffer[y][x] != old_draw_buffer[y][x]:
                execute_draw_command(Position(x, y), new_draw_buffer[y][x])

    old_draw_buffer = copy.deepcopy(new_draw_buffer)


#### Global game data

drops = [Drop(Position(0, 0), 'red')]
next_positions = set()


#### Game Logic ####


def init():
    launchpad_util.connect()
    launchpad_util.clear_all_led()

    # Quick flash on connect
    launchpad_util.set_all_led_color(32)
    time.sleep(1)
    launchpad_util.clear_all_led()

def cleanup():
    # Quick flash on disconnect
    launchpad_util.set_all_led_color(48)
    time.sleep(1)
    launchpad_util.clear_all_led()

def on_touch(message):
    did_touch = (message[0][2] == 127)
    led = message[0][1]    
    touch_pos = led_to_pos(led)
    if did_touch:
        # print "Touched LED %s" % (led)
        if are_4_adjacent(drops[0].position, touch_pos):
            next_positions.add(touch_pos)
    else:
        # print "Released LED %s" % (led)
        if are_4_adjacent(drops[0].position, touch_pos):
            next_positions.remove(touch_pos)
            drops[0] = Drop(touch_pos, drops[0].color)

def make_draw_buffer():
    draw_buffer = make_empty_draw_buffer()

    for drop in drops:
        draw_buffer[drop.position.y][drop.position.x] = DrawCommand('pulse', drop.color)

    for next_pos in next_positions:
        draw_buffer[next_pos.y][next_pos.x] = DrawCommand('solid', 'white')

    return draw_buffer

def main_loop():
    while 1:
        message = launchpad_util.poll_touch()
        if message != None:
            on_touch(message)

        new_draw_buffer = make_draw_buffer()
        draw(new_draw_buffer)

        time.sleep(0.01)


if __name__ == '__main__':
    try:
        init()
        main_loop()
    except KeyboardInterrupt:
        print('\nExiting by user request.\n', file=sys.stderr)
        cleanup()
        sys.exit(0)