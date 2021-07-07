#!/usr/bin/env python3
##
# @file main.py
#
# @brief This program converts supported tablature source files to a printable format
#
# @section description Description
# Creates Song objects of all tablatures it can find in a given directory or its subdirectories
# Supported inputs currently: Any .txt file, as long as each section has a corresponding [<sectionName>] delimiter
# Supported outputs currently: PNG format
# Song objects are then parsed into separate metadata information and sections
# Sections contain lines of lyric and corresponding tablature data
# The program then tries to fit these sections within the chosen output dimensions (currently A4)
#   as best as it can, shrinking or growing sections to fit the remaining space
#
# @section notes Notes
# - Splitting raw text into lyric and tablature info is very basic at the moment.
#   We need a better way to classify & split the various channels (raw tab, lyrics, chords, more?) that can be expected in tablature
#
# @section todo TODO
# - Various prints should be printed at specific log levels, to easily switch between debug, info or warnings only

import lib.chordFinder
import lib.dataStructures
import lib.initSongs
import lib.transpose
import output2img

def main():
  # Init Song objects for all songs with compatible inputs
  songs = lib.initSongs.getSongObjects()
  # Convert all songs into sections
  for song in songs:
    song.parseMe()
    # Parse as PNG a4
    if song.isParsed:
      # Create subdirectory where we will output our images
      targetDirectory = song.outputLocation + "-a4-png"
      print("Successfully parsed '{}' file. Writing output to '{}'".format(song.inputFile, targetDirectory)) 
      # Write out metadata and sections, as many as can fit on one page
      output2img.outputToImage(targetDirectory, song)

if __name__ == "__main__":
  main()
