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


color_name_to_code = {
    'red': 5, 
    'yellow': 13, 
    'blue': 40,
    'green': 32, 
    'orange': 9, 
    'purple': 48,
    'white': 3,
    'pink': 57,
    'brown': 61
}

# Tuples made in alphabetical order
color_mixing_map = {
    ('red', 'yellow'): 'orange',
    ('blue', 'yellow'): 'green',
    ('blue', 'red'): 'purple'
}

def mix_colors(a, b):
    if a == b: return a

    color_combo = tuple(sorted([a, b]))
    if color_combo in color_mixing_map:
        return color_mixing_map[color_combo]
    else:
        return 'brown'


Drop = collections.namedtuple('Drop', ['position', 'color'])


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

# These have default values in case no map is given
drops = [Drop(Position(0, 0), 'red'), Drop(Position(7, 0), 'blue')]
obstacles = {Position(7, 3), Position(6, 3), Position(5, 3)}

next_positions = set()
pressed_leds_count = 0


#### Game Logic ####

def read_map(map_str):
    global drops, obstacles

    drops = []
    obstacles = set()

    lines = map_str.split('\n')
    y = 0
    for line in lines:
        # If line is empty or starts with '#'' skip it
        if (not line) or line[0] == '#': continue

        for x, c in enumerate(line):
            if c == 'r': 
                drops.append(Drop(Position(x,y), 'red'))
            elif c == 'b': 
                drops.append(Drop(Position(x,y), 'blue'))
            elif c == 'y': 
                drops.append(Drop(Position(x,y), 'yellow'))
            elif c == 'x':
                obstacles.add(Position(x,y))

        y += 1

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

# Returns list of indices of adjacent drop, or empty list
def find_adjacent_drop_indices(pos):
    indices = []
    for i, drop in enumerate(drops):
        if are_4_adjacent(drop.position, pos):
            indices.append(i)
    return indices

def on_touch(message):
    global next_positions, drops, pressed_leds_count

    did_touch = (message[0][2] == 127)
    led = message[0][1]    
    touch_pos = led_to_pos(led)
    if did_touch:
        # print "Touched LED %s" % (led)
        pressed_leds_count += 1

        if (touch_pos not in obstacles) and find_adjacent_drop_indices(touch_pos):
            next_positions.add(touch_pos)
    else:
        # print "Released LED %s" % (led)
        pressed_leds_count -= 1

        # Wait until the player lifts up all touches
        if pressed_leds_count == 0:
            drops = simulate_drops()
            next_positions.clear()

def simulate_drops():
    # First move and split the drops
    split_drops = []
    for drop in drops:
        # if the current position is touched, don't move the drop 
        if drop.position in next_positions:
            split_drops.append(drop)
        else:
            # Duplicate the drop in each of the adjacent positions
            adjacent_positions = [pos for pos in next_positions if are_4_adjacent(pos, drop.position)]
            if adjacent_positions:
               for pos in adjacent_positions:
                split_drops.append(Drop(pos, drop.color))
            else:
                # Keep the drop where it is
                split_drops.append(drop)

    # Next, merge the drops and colors
    merged_drops = []
    for drop in split_drops:
        existing_drop_indexes = [index for index, merged_drop in enumerate(merged_drops) if merged_drop.position == drop.position]
        if not existing_drop_indexes:
            # No drop at that position (yet), add this to the list
            merged_drops.append(drop)
        else:
            existing_drop = merged_drops[existing_drop_indexes[0]]
            merged_drops[existing_drop_indexes[0]] = Drop(drop.position, mix_colors(drop.color, existing_drop.color))

    return merged_drops

def make_draw_buffer():
    draw_buffer = make_empty_draw_buffer()

    for drop in drops:
        draw_buffer[drop.position.y][drop.position.x] = DrawCommand('pulse', drop.color)

    for next_pos in next_positions:
        draw_buffer[next_pos.y][next_pos.x] = DrawCommand('solid', 'white')

    for obstacle in obstacles:
        draw_buffer[obstacle.y][obstacle.x] = DrawCommand('solid', 'pink')

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
        if len(sys.argv) > 1:
            print("Reading map from file '%s'" % (sys.argv[1]))
            map_file = open(sys.argv[1])
            read_map(map_file.read())

        init()
        main_loop()
    except KeyboardInterrupt:
        print('\nExiting by user request.\n', file=sys.stderr)
        cleanup()
        sys.exit(0)