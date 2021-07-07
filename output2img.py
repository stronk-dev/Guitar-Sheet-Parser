# !/usr/bin/python
# This program converts Song objects to imgs printable on A4 paper
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

# return expected height of rendering the complete current section
def calcSectionHeight(section):
  lineIterator = 0
  amountOfLines = len(section.lyrics)
  heightSum = 0
  # add section title
  headerWidth, headerHeight = fontChords.getsize(section.header)
  heightSum += headerHeight
  while lineIterator < amountOfLines:
    # Get chord&lyric line
    lyricTextWidth, lyricTextHeight = fontLyrics.getsize(section.lyrics[lineIterator])
    chordTextWidth, chordTextHeight = fontChords.getsize(section.chords[lineIterator])
    heightSum += lyricTextHeight + chordTextHeight
    lineIterator += 1
    
  return heightSum

def outputToImage(folderLocation, songObj):
  # Create target Directory if don't exist
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
    # remove any unwanted characters from metadat
    line = line.rstrip()
    if not line:
      continue
    #print("meta line '{}'".format(line))
    metadataTextWidth, metadataTextHeight = fontMetadata.getsize(line)
    draw.text((leftMargin,currentHeight), line, fill=(128, 128, 128), font=fontMetadata)
    currentHeight += metadataTextHeight
    
  currentHeight += topMargin
  
  for section in songObj.sections:
    lineIterator = 0
    amountOfLines = len(section.lyrics)
    if (amountOfLines != len(section.chords)):
      print("Cannot write this section to file, since it was not processed correctly. There are {} chord lines and {} lyric lines. Aborting...".format(len(section.chords), amountOfLines))
      return
    # See if it can fit on the current page - if it does not, write & reset
    if currentHeight + calcSectionHeight(section) > imageHeight:
      #print("overflow! starting with a new image")
      outputLocation = folderLocation + "/"  + str(imageNumber) + ".png"
      imageNumber += 1
      a4image.save(outputLocation)
      currentHeight = topMargin
      a4image = Image.new('RGB',(imageWidth, imageHeight),(background))
      draw = ImageDraw.Draw(a4image)
    
    # add section title
    headerWidth, headerHeight = fontChords.getsize(section.header)
    draw.text((leftMargin,currentHeight), section.header, fill=(0, 0, 0), font=fontChords)
    currentHeight += headerHeight
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
    currentHeight += topMargin
      
  # Write remaining image to file as well
  outputLocation = folderLocation + "/" + str(imageNumber) + ".png"
  a4image.save(outputLocation)
    
  
  
  
  
  
  
  
  
  
  
  
  
  
