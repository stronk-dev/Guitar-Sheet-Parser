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

import lib.config
import os
from PIL import Image, ImageDraw, ImageFont

"""!@brief Calculates the height of rendered text
    This function calculates the dimensions of each line of text
    the section contains and returns the sum
    @param section lib.dataStructures.Section object
    @param fontTablature ImageFont.truetype object of font we are using for tablature lines
    @param fontLyrics ImageFont.truetype object of font we are using for lyric lines
    @return the total height of the section
"""
def calcSectionHeight(section, fontTablature, fontLyrics):
  lineIterator = 0
  amountOfLines = len(section.lyrics)
  heightSum = 0
  # consider section title
  headerWidth, headerHeight = fontTablature.getsize(section.header)
  heightSum += headerHeight
  while lineIterator < amountOfLines:
    # Get chord&lyric line dimensions
    lyricTextWidth, lyricTextHeight = fontLyrics.getsize(section.lyrics[lineIterator])
    tablatureTextWidth, chordTextHeight = fontTablature.getsize(section.tablatures[lineIterator])
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
    @param configObj configparser object
    @return None
"""
def outputToImage(folderLocation, songObj):
  # Create target Directory if doesn't exist
  if not os.path.exists(folderLocation):
    os.mkdir(folderLocation)
    print("Directory " , folderLocation ,  " Created ")
  #else:    
    #print("Directory " , folderLocation ,  " already exists")

  configObj = lib.config.config['output']
  topMargin = int(configObj['topMargin'])
  fontColour = tuple(int(var) for var in configObj['fontColour'].split(','))
  backgroundColour = tuple(int(var) for var in configObj['backgroundColour'].split(','))
  metadataColour = tuple(int(var) for var in configObj['metadataColour'].split(','))
  imageWidth = int(configObj['imageWidth'])
  imageHeight = int(configObj['imageHeight'])
  leftMargin = int(configObj['leftMargin'])
  fontMetadata = ImageFont.truetype(configObj['metafontfamily'], int(configObj['metaFontWeight']))
  fontLyrics = ImageFont.truetype(configObj['lyricfontfamily'], int(configObj['songFontWeight']))
  fontTablature = ImageFont.truetype(configObj['tablaturefontfamliy'], int(configObj['songFontWeight']))
      
  # Init image info
  imageNumber = 1
  currentHeight = topMargin

  # New Image
  a4image = Image.new('RGB',(imageWidth, imageHeight),(backgroundColour))
  draw = ImageDraw.Draw(a4image)
  
  # Write metadata
  for line in songObj.metadata.split('\n'):
    # remove any unwanted characters from metadata
    line = line.rstrip()
    if not line:
      continue
    #print("meta line '{}'".format(line))
    metadataTextWidth, metadataTextHeight = fontMetadata.getsize(line)
    draw.text((leftMargin,currentHeight), line, fill=metadataColour, font=fontMetadata)
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
    if (amountOfLines != len(section.tablatures)):
      print("Cannot write this section to file, since it was not processed correctly. There are {} tablature lines and {} lyric lines. Aborting...".format(len(section.chords), amountOfLines))
      return
    # See if the section would fit on the current page - if it does not, write current buffered image & make the next image ready
    if currentHeight + calcSectionHeight(section, fontTablature, fontLyrics) > imageHeight:
      #print("overflow! starting with a new image")
      outputLocation = folderLocation + "/"  + str(imageNumber) + ".png"
      imageNumber += 1
      a4image.save(outputLocation)
      currentHeight = topMargin
      a4image = Image.new('RGB',(imageWidth, imageHeight),(backgroundColour))
      draw = ImageDraw.Draw(a4image)
    # write section title
    headerWidth, headerHeight = fontTablature.getsize(section.header)
    draw.text((leftMargin,currentHeight), section.header, fill=fontColour, font=fontTablature)
    currentHeight += headerHeight
    # Write each line tablature&lyric data
    while lineIterator < amountOfLines:
      #print("Printing tablatures line {} and lyrics line {}".format(section.tablatures[lineIterator], section.lyrics[lineIterator]))
      # Get tablatures&lyric line
      lyricTextWidth, lyricTextHeight = fontLyrics.getsize(section.lyrics[lineIterator])
      tablatureTextWidth, tablatureTextHeight = fontTablature.getsize(section.tablatures[lineIterator])
      # add to image file
      draw.text((leftMargin,currentHeight), section.tablatures[lineIterator], fill=fontColour, font=fontTablature)
      currentHeight += tablatureTextHeight
      draw.text((leftMargin,currentHeight), section.lyrics[lineIterator], fill=fontColour, font=fontLyrics)
      currentHeight += lyricTextHeight
      lineIterator += 1
      #print("currentheight={}".format(currentHeight))
    # Margin between each section
    currentHeight += topMargin
  # No more sections left, so the current buffered image is ready to be written to file
  outputLocation = folderLocation + "/" + str(imageNumber) + ".png"
  a4image.save(outputLocation)
    
  
  
  
  
  
  
  
  
  
  
  
  
  
