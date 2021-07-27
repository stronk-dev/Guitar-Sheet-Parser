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

import os
from PIL import Image, ImageDraw
import logging

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
    logging.info("Directory {} Created ".format(folderLocation))
  else:    
    logging.debug("Directory {} already exists".format(folderLocation))
      
  # Init image info
  imageNumber = 1
  currentHeight = songObj.verticalMargin

  # New Image
  a4image = Image.new('RGB',(songObj.imageWidth, songObj.imageHeight),(songObj.backgroundColour))
  draw = ImageDraw.Draw(a4image)

  # Add extra whitespace on the left if this is an even page
  # The whitespace on the right for uneven pages is handled elsewhere, by limiting the maximum horizontal size
  horizontalMargin = songObj.horizontalMargin
  if (imageNumber % 2) == 0:
    horizontalMargin += songObj.extraHorizontalMargin
  
  # Write metadata
  for line in songObj.metadata.split('\n'):
    # remove any unwanted characters from metadata
    line = line.rstrip()
    if not line and not songObj.keepEmptyLines:
      continue
    logging.debug("Metadata '{}'".format(line))
    metadataTextWidth, metadataTextHeight = songObj.fontMetadata.getsize(line)
    draw.text((horizontalMargin, currentHeight), line, fill=songObj.metadataColour, font=songObj.fontMetadata)
    currentHeight += metadataTextHeight
  # Draw all pages
  for page in songObj.pages:
    # Margin between metadata and the first section / section and top of page
    currentHeight += songObj.verticalMargin
    for section in page.sections:
      # Reset section specific variables
      lineIterator = 0
      amountOfLines = len(section.lyrics)
      if (amountOfLines != len(section.tablatures)):
        logging.critical("Cannot write this section to file, since it was not processed correctly. There are {} tablature lines and {} lyric lines. Aborting...".format(len(section.chords), amountOfLines))
        return
      if (section.expectedHeight == -1 or section.expectedWidth == -1):
        logging.critical("Cannot write this section to file, since it was not processed correctly. The expected dimensions are not set. Aborting...")
        return
      # write section title
      headerWidth, headerHeight = songObj.fontTablature.getsize(section.header)
      draw.text((horizontalMargin ,currentHeight), section.header, fill=songObj.fontColour, font=songObj.fontTablature)
      currentHeight += headerHeight
      # Write each line tablature&lyric data
      while lineIterator < amountOfLines:
        logging.debug("Printing tablatures line {} and lyrics line {}".format(section.tablatures[lineIterator], section.lyrics[lineIterator]))
        # Get tablatures&lyric line
        lyricTextWidth, lyricTextHeight = songObj.fontLyrics.getsize(section.lyrics[lineIterator])
        tablatureTextWidth, tablatureTextHeight = songObj.fontTablature.getsize(section.tablatures[lineIterator])
        # add to image file
        draw.text((horizontalMargin ,currentHeight), section.tablatures[lineIterator], fill=songObj.fontColour,  font=songObj.fontTablature)
        currentHeight += tablatureTextHeight
        draw.text((horizontalMargin ,currentHeight), section.lyrics[lineIterator], fill=songObj.fontColour, font=songObj.fontLyrics)
        currentHeight += lyricTextHeight
        lineIterator += 1
        logging.debug("currentheight={}".format(currentHeight))
      # If we stripped al whitespace, we need to add whitespace between sections
      if not songObj.keepEmptyLines:
        currentHeight += songObj.verticalMargin
    # Got all sections in the page, so write it
    outputLocation = folderLocation + "/" + songObj.title + '-' + str(imageNumber) + ".png"
    a4image.save(outputLocation)
    a4image = Image.new('RGB',(songObj.imageWidth, songObj.imageHeight),(songObj.backgroundColour))
    draw = ImageDraw.Draw(a4image)
    currentHeight = songObj.verticalMargin
    imageNumber += 1
    # Add extra whitespace on the left if this is an even page
    # The whitespace on the right for uneven pages is handled elsewhere, by limiting the maximum horizontal size
    horizontalMargin = songObj.horizontalMargin
    if (imageNumber % 2) == 0:
      horizontalMargin += songObj.extraHorizontalMargin
    
  
  
  
  
  
  
  
  
  
  
  
  
  
