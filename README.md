# wav files

After a long period of wanting to learn more about DSP,
I discovered [Direct to Wav](https://www.instagram.com/direct.to.wav/).
I guess Tyler started this mess.

Most of these scripts can be run on Linux by doing `./main.py && aplay whatever.wav`.

## Resources used so far
* http://blog.acipo.com/wave-generation-in-python/ is how I got my first tones
* http://blog.acipo.com/generating-wave-files-in-c/
* http://blog.acipo.com/handling-endianness-in-c/
* http://blog.bjornroche.com/2011/11/slides-from-fundamentals-of-audio.html helped me with some "big picture" stuff
    * Also has some helpfully suggestive bits on basic linear shift invariant (LSI) FX circuit schematics

## Planned reading
https://ccrma.stanford.edu/~jos/ should take me a while to work through.

## Fun next steps

* [x] Add a delay or reverb channel to the mix
    * [x] Then add feedback to whichever effect was used
* [ ] Add a constraint element to enable looping (start and end should match)
* [ ] DSP challenge: write a script that consumes a wav file and generates a video

## Running this stuff
I can throw together a `setup.py` later if anyone actually wants this to be installable,
but for now you can add scripts under `examples/` like this:

```python
#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wav import Wav, unity,
from wav import tones as tone
# or just
from wav import *
```
