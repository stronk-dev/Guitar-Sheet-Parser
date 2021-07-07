#!/usr/bin/env python3
##
# @file transpose.py
#
# @brief This file takes a string corresponding to chord data and transposes it
#
# @section description Description
# -
#
# @section notes Notes
# - 
#
# @section todo TODO
# - take a line of chord data, for each string enclosed in whitespace or tabs:
#     ignore if its in major or minor, just take the ROOT of the chord
#     then get its index in the slider
#     then add/subtract transposition amount and loop around the slider if it goes over
#     make sure to keep line width persistent:
#     if from E to Eb for example, remove a whitespace
#     if from Eb to D for example, add a whitespace
slider = ['E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb']