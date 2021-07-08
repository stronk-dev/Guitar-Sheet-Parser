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
from PIL import Image, ImageDraw

"""!@brief Exports the song object to images
    This function renders the metadata and sections
    of a given Song object, and exports it as PNG to the destination folder.
    It will create the folder if it does not exist yet.
    It will overwrite existing images, but will not clear old images
    @param folderLocation path to where we want the images
    @param songObj lib.dataStructures.Song object
    @return None
"""
def outputToImage(folderLocation, songObj):
  # Create target Directory if doesn't exist
  if not os.path.exists(folderLocation):
    os.mkdir(folderLocation)
    print("Directory " , folderLocation ,  " Created ")
  #else:    
    #print("Directory " , folderLocation ,  " already exists")
      
  # Init image info
  imageNumber = 1
  currentHeight = songObj.topMargin

  # New Image
  a4image = Image.new('RGB',(songObj.imageWidth, songObj.imageHeight),(songObj.backgroundColour))
  draw = ImageDraw.Draw(a4image)
  
  # Write metadata
  for line in songObj.metadata.split('\n'):
    # remove any unwanted characters from metadata
    line = line.rstrip()
    if not line:
      continue
    #print("meta line '{}'".format(line))
    metadataTextWidth, metadataTextHeight = songObj.fontMetadata.getsize(line)
    draw.text((songObj.leftMargin,currentHeight), line, fill=songObj.metadataColour, font=songObj.fontMetadata)
    currentHeight += metadataTextHeight
  # Margin between metadata and the first section
  currentHeight += songObj.topMargin
  # Iterate over each section
  # NOTE: sections might be split into lists of pages containing a list of sections
  #       This change will occur when we add an arranger which resizes sections to fit pages better
  for section in songObj.sections:
    # Reset section specific variables
    lineIterator = 0
    amountOfLines = len(section.lyrics)
    if (amountOfLines != len(section.tablatures)):
      print("Cannot write this section to file, since it was not processed correctly. There are {} tablature lines and {} lyric lines. Aborting...".format(len(section.chords), amountOfLines))
      return
    if (section.expectedHeight == -1 or section.expectedWidth == -1):
      print("Cannot write this section to file, since it was not processed correctly. The expected dimensions are not set. Aborting...")
      return
    # See if the section would fit on the current page - if it does not, write current buffered image & make the next image ready
    if currentHeight + section.expectedHeight > songObj.imageHeight:
      #print("overflow! starting with a new image")
      outputLocation = folderLocation + "/"  + str(imageNumber) + ".png"
      imageNumber += 1
      a4image.save(outputLocation)
      currentHeight = songObj.topMargin
      a4image = Image.new('RGB',(songObj.imageWidth, songObj.imageHeight),(songObj.backgroundColour))
      draw = ImageDraw.Draw(a4image)
    # write section title
    headerWidth, headerHeight = songObj.fontTablature.getsize(section.header)
    draw.text((songObj.leftMargin,currentHeight), section.header, fill=songObj.fontColour, font=songObj.fontTablature)
    currentHeight += headerHeight
    # Write each line tablature&lyric data
    while lineIterator < amountOfLines:
      #print("Printing tablatures line {} and lyrics line {}".format(section.tablatures[lineIterator], section.lyrics[lineIterator]))
      # Get tablatures&lyric line
      lyricTextWidth, lyricTextHeight = songObj.fontLyrics.getsize(section.lyrics[lineIterator])
      tablatureTextWidth, tablatureTextHeight = songObj.fontTablature.getsize(section.tablatures[lineIterator])
      # add to image file
      draw.text((songObj.leftMargin,currentHeight), section.tablatures[lineIterator], fill=songObj.fontColour,  font=songObj.fontTablature)
      currentHeight += tablatureTextHeight
      draw.text((songObj.leftMargin,currentHeight), section.lyrics[lineIterator], fill=songObj.fontColour, font=songObj.fontLyrics)
      currentHeight += lyricTextHeight
      lineIterator += 1
      #print("currentheight={}".format(currentHeight))
    # Margin between each section
    currentHeight += songObj.topMargin
  # No more sections left, so the current buffered image is ready to be written to file
  outputLocation = folderLocation + "/" + str(imageNumber) + ".png"
  a4image.save(outputLocation)
    
  
  
  
  
  
  
  
  
  
  
  
  
  
