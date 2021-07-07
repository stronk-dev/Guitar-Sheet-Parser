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
# - A lot of this stuff is hardcoded. We want to write default fonts, sizes, colours, margins, dimensions, wanted amount of pages
#     to a config file on first boot. Overwrite these if they get passed via CMD arguments (or manually by user)
# - Various prints should be printed at specific log levels, to easily switch between debug, info or warnings only

import os
import lib.dataStructures
from PIL import Image, ImageDraw, ImageFont

# size and font of metadata
metaFontFamily = 'fonts/CourierPrime-Regular.ttf'
metaFontWeight = 8

# size and font of chord and lyric text
lyricFontFamily = 'fonts/CourierPrime-Regular.ttf'
chordFontFamily = 'fonts/CourierPrime-Bold.ttf'
songFontWeight = 14

# image properties
imageWidth, imageHeight = (595, 842) # A4 at 72dpi
background = (255, 255, 255)
fontMetadata = ImageFont.truetype(metaFontFamily, metaFontWeight)
fontLyrics = ImageFont.truetype(lyricFontFamily, songFontWeight)
fontChords = ImageFont.truetype(chordFontFamily, songFontWeight)
fontColour = ()
topMargin = 10
leftMargin = 25

"""!@brief Calculates the height of rendered text
    This function calculates the dimensions of each line of text
    the section contains and returns the sum
    @param section lib.dataStructures.Section object
    @return the total height of the section
"""
def calcSectionHeight(section):
  lineIterator = 0
  amountOfLines = len(section.lyrics)
  heightSum = 0
  # consider section title
  headerWidth, headerHeight = fontChords.getsize(section.header)
  heightSum += headerHeight
  while lineIterator < amountOfLines:
    # Get chord&lyric line dimensions
    lyricTextWidth, lyricTextHeight = fontLyrics.getsize(section.lyrics[lineIterator])
    chordTextWidth, chordTextHeight = fontChords.getsize(section.chords[lineIterator])
    heightSum += lyricTextHeight + chordTextHeight
    lineIterator += 1
  return heightSum

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
  currentHeight = topMargin

  # New Image
  a4image = Image.new('RGB',(imageWidth, imageHeight),(background))
  draw = ImageDraw.Draw(a4image)
  
  # Write metadata
  for line in songObj.metadata.split('\n'):
    # remove any unwanted characters from metadata
    line = line.rstrip()
    if not line:
      continue
    #print("meta line '{}'".format(line))
    metadataTextWidth, metadataTextHeight = fontMetadata.getsize(line)
    draw.text((leftMargin,currentHeight), line, fill=(128, 128, 128), font=fontMetadata)
    currentHeight += metadataTextHeight
  # Margin between metadata and the first section
  currentHeight += topMargin
  # Iterate over each section
  # NOTE: sections might be split into lists of pages containing a list of sections
  #       This change will occur when we add an arranger which resizes sections to fit pages better
  for section in songObj.sections:
    # Reset section specific variables
    lineIterator = 0
    amountOfLines = len(section.lyrics)
    if (amountOfLines != len(section.chords)):
      print("Cannot write this section to file, since it was not processed correctly. There are {} tablature lines and {} lyric lines. Aborting...".format(len(section.chords), amountOfLines))
      return
    # See if the section would fit on the current page - if it does not, write current buffered image & make the next image ready
    if currentHeight + calcSectionHeight(section) > imageHeight:
      #print("overflow! starting with a new image")
      outputLocation = folderLocation + "/"  + str(imageNumber) + ".png"
      imageNumber += 1
      a4image.save(outputLocation)
      currentHeight = topMargin
      a4image = Image.new('RGB',(imageWidth, imageHeight),(background))
      draw = ImageDraw.Draw(a4image)
    # write section title
    headerWidth, headerHeight = fontChords.getsize(section.header)
    draw.text((leftMargin,currentHeight), section.header, fill=(0, 0, 0), font=fontChords)
    currentHeight += headerHeight
    # Write each line tablature&lyric data
    while lineIterator < amountOfLines:
      #print("Printing chord line {} and lyrics line {}".format(section.chords[lineIterator], section.lyrics[lineIterator]))
      # Get chord&lyric line
      lyricTextWidth, lyricTextHeight = fontLyrics.getsize(section.lyrics[lineIterator])
      chordTextWidth, chordTextHeight = fontChords.getsize(section.chords[lineIterator])
      # add to image file
      draw.text((leftMargin,currentHeight), section.chords[lineIterator], fill=(0, 0, 0), font=fontChords)
      currentHeight += chordTextHeight
      draw.text((leftMargin,currentHeight), section.lyrics[lineIterator], fill=(0, 0, 0), font=fontLyrics)
      currentHeight += lyricTextHeight
      lineIterator += 1
      #print("currentheight={}".format(currentHeight))
    # Margin between each section
    currentHeight += topMargin
  # No more sections left, so the current buffered image is ready to be written to file
  outputLocation = folderLocation + "/" + str(imageNumber) + ".png"
  a4image.save(outputLocation)
    
  
  
  
  
  
  
  
  
  
  
  
  
  
