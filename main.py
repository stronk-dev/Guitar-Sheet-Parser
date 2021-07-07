# !/usr/bin/python
# This program converts all songs in a given directory to a printable format
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
