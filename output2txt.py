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

import os
import logging

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
    logging.info("Directory {} Created ".format(folderLocation))
  else:    
    logging.debug("Directory {} already exists".format(folderLocation))
      
  output = ""
  emptyLines = []
  lyricLines = []
  nonLyricLines = []
  sectionHeaders = []
  metadataLines = []

  lineCounter = 0
  # Write metadata
  for line in songObj.metadata.splitlines(True):
    # remove any unwanted characters from metadata
    if not songObj.keepEmptyLines and not line:
      continue
    logging.debug("Metadata '{}'".format(line))
    output += line
    metadataLines.append(lineCounter)
    lineCounter += 1
    
  # If exporting raw, do not include the whitespace between metadata and sections
  # also do not add an extra whitespace if we already keep whitespaces from input
  if not printRaw and not songObj.keepEmptyLines:
    output += '\r\n'
    emptyLines.append(lineCounter)
    lineCounter += 1
  # Draw all pages
  for section in songObj.sections:
    lineIterator = 0
    amountOfLines = len(section.lyrics)
    if (amountOfLines != len(section.tablatures)):
      logging.critical("Cannot write this section to file, since it was not processed correctly. There are {} tablature lines and {} lyric lines. Aborting...".format(len(section.chords), amountOfLines))
      return
    # write section title
    output += section.header.rstrip() + '\r\n'
    sectionHeaders.append(lineCounter)
    lineCounter += 1
    # Write each line tablature&lyric data
    while lineIterator < amountOfLines:
      tabline = section.tablatures[lineIterator].rstrip()
      lyricline = section.lyrics[lineIterator].rstrip()
      if printRaw or len(tabline):
        output += tabline + '\r\n'
        nonLyricLines.append(lineCounter)
        lineCounter += 1
      if printRaw or len(lyricline):
        output += lyricline + '\r\n'
        lyricLines.append(lineCounter)
        lineCounter += 1
      #If both lines are empty, it is 1 emptyline
      if not printRaw and not len(tabline) and not len(lyricline):
        output += '\r\n'
        emptyLines.append(lineCounter)
        lineCounter += 1
      lineIterator += 1
    # If exporting raw, do not include the whitespace between sections
    # also do not add an extra whitespace if we already keep whitespaces from input
    if not printRaw and not songObj.keepEmptyLines:
      output += '\r\n'
      emptyLines.append(lineCounter)
      lineCounter += 1
  # Finished
  outputLocation = ""
  if not printRaw:
    outputLocation = folderLocation + "/"  + songObj.title + ".txt"
  else:
    outputLocation = folderLocation + "/"  + songObj.title + ".rawtxt"
  with open(outputLocation, "w") as fileOut:
    fileOut.write(output)
  if songObj.writeMetadata:
    if printRaw:
      outputLocation = folderLocation + "/"  + songObj.title + ".rawtxt.json"
    else:
      outputLocation = folderLocation + "/"  + songObj.title + ".txt.json"

    with open(outputLocation, "w") as fileOut:
      fileOut.write('{\r\n')
      fileOut.write('  "emptyLines": [')
      hasNext = len(emptyLines)
      for entry in emptyLines:
        hasNext -= 1
        fileOut.write(str(entry))
        if hasNext:
          fileOut.write(', ')
      fileOut.write('],\r\n')
      fileOut.write('  "lyricLines": [')
      hasNext = len(lyricLines)
      for entry in lyricLines:
        hasNext -= 1
        fileOut.write(str(entry))
        if hasNext:
          fileOut.write(', ')
      fileOut.write('],\r\n')
      fileOut.write('  "nonLyricLines": [')
      hasNext = len(nonLyricLines)
      for entry in nonLyricLines:
        hasNext -= 1
        fileOut.write(str(entry))
        if hasNext:
          fileOut.write(', ')
      fileOut.write('],\r\n')
      fileOut.write('  "sectionHeaders": [')
      hasNext = len(sectionHeaders)
      for entry in sectionHeaders:
        hasNext -= 1
        fileOut.write(str(entry))
        if hasNext:
          fileOut.write(', ')
      fileOut.write('],\r\n')
      fileOut.write('  "metadataLines": [')
      hasNext = len(metadataLines)
      for entry in metadataLines:
        hasNext -= 1
        fileOut.write(str(entry))
        if hasNext:
          fileOut.write(', ')
      fileOut.write(']\r\n')
      fileOut.write('}\r\n')
  
  
  
  
  
  
  
  
  
  
  
  
