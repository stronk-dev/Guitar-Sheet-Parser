#!/usr/bin/env python3
##
# @file output2img.py
#
# @brief This program converts the internal data structure to an image file
#
# @section description Description
# Generates PNG images of a specific dimension (currently A4) of tablature data
# Dynamically resizes specific sections to maximize using the entire paper (and avoid awkward page flips)
#
# @section notes Notes
# - 
#
# @section todo TODO
# - Various prints should be printed at specific log levels, to easily switch between debug, info or warnings only

import os

"""!@brief Exports the song object to a txt file
          Perfect to use as source file for any program which requires
          tabs as input, due to the predictable layout of
          metadata
          [section title]
          <non-lyric line>
          <lyric line>
          ...
    @param folderLocation path to where we want the text file
    @param printRaw if set, prints empty lines as well and saves as .raw
            if false, will print in a more readable format
    @param songObj lib.dataStructures.Song object
    @return None
"""
def outputToTxt(folderLocation, printRaw, songObj):
  # Create target Directory if doesn't exist
  if not os.path.exists(folderLocation):
    os.mkdir(folderLocation)
    print("Directory " , folderLocation ,  " Created ")
  #else:    
    #print("Directory " , folderLocation ,  " already exists")
      
  output = ""
  # Write metadata
  for line in songObj.metadata.split('\n'):
    # remove any unwanted characters from metadata
    line = line.rstrip()
    if not line:
      continue
    #print("meta line '{}'".format(line))
    output += line + '\r\n'
  # If exporting raw, do not include the whitespace between metadata and sections
  if not printRaw:
    output += '\r\n'
  # Draw all pages
  for section in songObj.sections:
    lineIterator = 0
    amountOfLines = len(section.lyrics)
    if (amountOfLines != len(section.tablatures)):
      print("Cannot write this section to file, since it was not processed correctly. There are {} tablature lines and {} lyric lines. Aborting...".format(len(section.chords), amountOfLines))
      return
    # write section title
    output += section.header.rstrip() + '\r\n'
    # Write each line tablature&lyric data
    while lineIterator < amountOfLines:
      tabline = section.tablatures[lineIterator].rstrip()
      lyricline = section.lyrics[lineIterator].rstrip()
      if printRaw or len(tabline):
        output += tabline + '\r\n'
      if printRaw or len(lyricline):
        output += lyricline + '\r\n'
      lineIterator += 1
    # If exporting raw, do not include the whitespace between sections
    if not printRaw:
      output += '\r\n'
  # Finished, so print some trailing endlines
  outputLocation = ""
  if not printRaw:
    output += '\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n'
    outputLocation = folderLocation + "/"  + songObj.title + ".txt"
  else:
    outputLocation = folderLocation + "/"  + songObj.title + ".rawtxt"
  with open(outputLocation, "w") as fileOut:
    fileOut.write(output)

  
  
  
  
  
  
  
  
  
  
  
  
