# launchpad

Scripts to use the Novation Launchpad from Python.

Requires the [rtmidi library](http://trac.chrisarndt.de/code/wiki/python-rtmidi). To install use:

```
pip install python-rtmidi
```

## Scripts

The file `launchpad_util.py` provides a simple wrapper around the MIDI messages send to and from the Launchpad.

The other scripts are meant to be executed on the command line, and import `launchpad_util` as a library.

* `light_touch.py` - Touches are colored randomly.
* `scroll_text.py` - Scrolls the given text across the screen. Provide the text as a single argument, like `python scroll_text.py "I love popcorn"`.


## Game Prototype 

The game prototype is called `direct.py`. It can load maps and play sounds.

To play sounds, it requires [pyglet](https://bitbucket.org/pyglet/pyglet/wiki/Home). It can be installed with `pip install pyglet`. Pyglet in turn requires [AVbin](http://avbin.github.io/AVbin/Home/Home.html) to be installed in order to read compressed audio files like MP3.

To run the game, call `direct.py` followed by the name of the file that contains the map. The map is a simple text file, containing 8 lines of 8 characters. The characters are "r", "y", "b", "g", "o", "p", "n" to represent drops of red, yellow, blue, green, orange, purple or brown. The same letter in capital form represents a target (or goal) for that color drop. The character "x" is a barrier, and "0" is an empty space.
