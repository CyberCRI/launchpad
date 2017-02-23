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

