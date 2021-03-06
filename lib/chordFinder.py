#!/usr/bin/env python3
##
# @file chordFinder.py
#
# @brief This file returns tablature for chords in different positions and voicings
#
# @section description Description
# -
#
# @section notes Notes
# - File might never be created in the first place, since we might create a lookup table using data from existing available API's
#
# @section todo TODO
# - we need to itemize all chords in the song and major/minor/diminshed/augmented/dom7/maj7/etc (we can support more voicings as we go)
#       then for each chord, get location for each (C A G E D) shape
#       for each shape, generate finger position tab, like so:
#           B       x24442
#           C#m     x46654
#           Amaj7   x02120
#           F#m     244222
#           Am6     x04555
