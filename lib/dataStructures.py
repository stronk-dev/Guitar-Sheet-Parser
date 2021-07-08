#!/usr/bin/env python3
##
# @file dataStructures.py
#
# @brief This file contains the internal data structures required for each tablature file
#
# @section description Description
# -
#
# @section notes Notes
#
# @section todo TODO
# - Move helper functions like stripEmptyLines to a separate file for
# - Move read functions to separate input functions (also to support more types of inputs)

import re
import lib.config
from PIL import ImageFont

"""!@brief Removes empty lines and makes sure every line ends with \r\n
    @param inputString raw txt input
    @return string of parsed input
"""
def stripEmptyLines(inputString):
  nonEmptyLines = ""
  lines = inputString.split("\n")
  for line in lines:
    if line.strip() != "":
      nonEmptyLines += line + "\r\n"
  return nonEmptyLines

"""!@brief Opens a .txt file and loads it's contents into buffer
    @param inputFile path to .txt file
    @return .txt file raw contents
"""
def readSourceFile(inputFile):
  with open(inputFile, 'r') as file:
    return file.read()

"""!@brief Returns whether the string is a line of lyrics or a line of tablature data
    @param inputString single line of text
    @return True if it is tablature data, False if it is lyric data
"""
def isTablatureData(inputString):
  if not inputString:
    return
  #print("Checking '{}' for line type".format(inputString))
  # Assume tablature line if any digit
  if any(char.isdigit() for char in inputString):
    #print("'{}' is a tablature line, since it contains a number".format(inputString))
    return True
  # Assume tablature line if any character {/, #, (, ), }
  tablatureSpecificCharacterString = r"/#"
  if any(elem in inputString for elem in tablatureSpecificCharacterString):
    #print("'{}' is a tablature line, since it contains a tablature specific character".format(inputString))
    return True
  # Assume LYRIC line if any TEXT character OTHER THAN {a, b, c, d, e, f, g, h, b, x, m}
  lyricSpecificCharacterString = r"abcdefghbxm"
  for char in inputString:
    if char.isalpha():
      if not char.lower() in lyricSpecificCharacterString:
        #print("'{}' is a LYRIC line, since it contains lyric specific text characters".format(inputString))
        return False
  # Assume LYRIC line if any character {.}
  lyricSpecialChars = r"."
  if any(elem in inputString for elem in lyricSpecialChars):
    #print("'{}' is a LYRIC line, since it contains lyric specific special characters".format(inputString))
    return False
  # Else warn and assume tablature line
  #print("Unable to identify if '{}' is a lyric or tablature line. Assuming it is a tablature line. Please improve the isTablatureData function".format(inputString))
  return True

"""!@brief Class containing Section specific data
"""
class Section:
  def __init__(self):
    # List of lines of lyrics strings
    self.lyrics = []
    # List of lines of tablature strings
    self.tablatures = []
    # section type string
    self.header = ""
    # string of tablature and lyric data
    self.rawData = ""
    # Flag for succesfully parsed
    self.isParsed = False
    # Expected dimensions of this section
    self.expectedWidth = -1
    self.expectedHeight = -1

  """!@brief Calculates dimensions of rendered text
    @return None
  """
  def calculateSectionDimensions(self, fontTablature, fontLyrics):
    lineIterator = 0
    amountOfLines = len(self.lyrics)
    heightSum = 0
    maxWidth = 0
    # consider section title
    headerWidth, headerHeight = fontTablature.getsize(self.header)
    heightSum += headerHeight
    maxWidth = headerWidth
    while lineIterator < amountOfLines:
      # Get chord&lyric line dimensions
      lyricTextWidth, lyricTextHeight = fontLyrics.getsize(self.lyrics[lineIterator])
      tablatureTextWidth, chordTextHeight = fontTablature.getsize(self.tablatures[lineIterator])
      heightSum += lyricTextHeight + chordTextHeight
      if lyricTextWidth > maxWidth:
        maxWidth = lyricTextWidth
      if tablatureTextWidth > maxWidth:
        maxWidth = tablatureTextWidth
      lineIterator += 1
    self.expectedWidth = maxWidth
    self.expectedHeight = heightSum
    
  """!@brief Converts raw buffered data into separate Lyric and tablature lines
      @return None
  """
  # Parses self.rawData into lyrics and tablature strings
  def initSections(self):
    isFirstLine = True
    # Input sections may have tablature-only or lyric-only sections
    # So we have to insert empty lines if we have subsequent tablature or lyric lines
    lines = self.rawData.split('\r\n')
    for line in lines:
      # Determine lyric or tablature line
      currentIsTablature = isTablatureData(line)
      # Initially just fill in the first line correctly
      if isFirstLine:
        isFirstLine = False
        if currentIsTablature:
          self.tablatures.append(line)
        else:
          self.lyrics.append(line)
      # We want alternating lines, so if the prev is of the same type
      # we need to insert an empty line of the other type
      elif currentIsTablature == prevWasTablature:
        if currentIsTablature:
          #print("Inserting empty Lyric line")
          self.tablatures.append(line)
          self.lyrics.append("")
        else:
          #print("Inserting empty tablature line")
          self.lyrics.append(line)
          self.tablatures.append("")
      # also insert the current line
      elif currentIsTablature:
        #print("Inserting empty Lyric line")
        self.tablatures.append(line)
      else:
        self.lyrics.append(line)
      # move on to next line, save current type
      prevWasTablature = currentIsTablature
    # Simple check to see if it probably exported correctly
    if abs(len(self.lyrics) - len(self.tablatures)) > 1:
      print("Unable to parse section, since there is a mismatch between the amount of tablature and lyric lines.")
      return
    # Add a trailing empty line if necessary
    elif len(self.lyrics) > len(self.tablatures):
      self.tablatures.append("")
    elif len(self.lyrics) < len(self.tablatures):
      self.lyrics.append("")
    self.isParsed = True

"""!@brief Class containing Sections which fit on 1 page
"""
class Page:
  def __init__(self):
    self.sections = []
    self.totalHeight = -1

"""!@brief Class containing Song specific data
""" 
class Song:
  def __init__(self):
    # Src file
    self.inputFile = ""
    # Path to folder
    self.outputLocation = ""
    # Title - based on input file
    self.title = ""
    # List of Section objects
    self.sections = []
    # Meta info: the text before the first section
    self.metadata = ""
    self.metadataWidth = -1
    self.metadataHeight = -1
    # String of entire input
    self.rawData = ""
    # List of pages, which contain sections which fit on a page
    self.pages = []
    # Flag for succesfully parsed
    self.isParsed = False
    configObj = lib.config.config['output']
    self.topMargin = int(configObj['topMargin'])
    self.fontColour = tuple(int(var) for var in configObj['fontColour'].split(','))
    self.backgroundColour = tuple(int(var) for var in configObj['backgroundColour'].split(','))
    self.metadataColour = tuple(int(var) for var in configObj['metadataColour'].split(','))
    self.imageWidth = int(configObj['imageWidth'])
    self.imageHeight = int(configObj['imageHeight'])
    self.leftMargin = int(configObj['leftMargin'])
    self.fontMetadata = ImageFont.truetype(configObj['metafontfamily'], int(configObj['metaFontWeight']))
    self.fontSize = int(configObj['songFontWeight'])
    self.fontLyrics = ImageFont.truetype(configObj['lyricfontfamily'], self.fontSize)
    self.fontTablature = ImageFont.truetype(configObj['tablaturefontfamliy'], self.fontSize)
    self.configObj = configObj


  """!@brief Calculates dimensions of metadata
    @param section lib.dataStructures.Section object
    @return None
  """
  def calculateMetadataDimensions(self):
    # metadata starts topMargin removed from top
    currentHeight = self.topMargin
    maxWidth = 0
    for line in self.metadata.split('\n'):
      line = line.rstrip()
      if not line:
        continue
      metadataTextWidth, metadataTextHeight = self.fontMetadata.getsize(line)
      if metadataTextWidth > maxWidth:
        maxWidth = metadataTextWidth
      currentHeight += metadataTextHeight
    self.metadataWidth = maxWidth
    self.metadataHeight = currentHeight

  """!@brief Resizes all sections by a specified amount
    Also recalculates all section sizes afterwards
    @param mutator amount of fontSize to add/dec from current font size
    @return None
  """
  def resizeAllSections(self, mutator):
    self.fontSize += mutator
    self.fontLyrics = ImageFont.truetype(self.configObj['lyricfontfamily'], self.fontSize)
    self.fontTablature = ImageFont.truetype(self.configObj['tablaturefontfamliy'], self.fontSize)
    self.prerenderSections()

  """!@brief Calculates the expected dimensions of all sections
    @return None
  """
  def prerenderSections(self):
    self.calculateMetadataDimensions()
    for section in self.sections:
      section.calculateSectionDimensions(self.fontTablature, self.fontLyrics)

  """!@brief Calculates the expected dimensions of all sections
    @return None
  """
  def fitSectionsByWidth(self):
    self.prerenderSections()
    while not self.checkOverflowX():
      #print("Overflowing on width of the page. Decreasing font size by 2...")
      self.resizeAllSections(-2)

  """!@brief Checks whether we are overflowing on the width of the page
    @return True if everything OK, False if overflowing
  """
  def checkOverflowX(self):
    for section in self.sections:
      if section.expectedWidth > self.imageWidth:
        return False
    return True

  """!@brief Fits current sections into pages
    @return None
  """
  def sectionsToPages(self):
    self.prerenderSections()
    # First page contains metadata
    currentHeight = self.topMargin
    currentHeight += self.metadataHeight
    currentHeight += self.topMargin
    curPage = Page()
    # Now fit all sections
    for section in self.sections:
      if (section.expectedHeight == -1 or section.expectedWidth == -1):
        print("Warning: this file was not processed correctly. The expected dimensions are not set")
      # See if the section would fit on the current page - if it does not, we have a filled page
      if currentHeight + section.expectedHeight > self.imageHeight:
        curPage.totalHeight = currentHeight
        self.pages.append(curPage)
        currentHeight = self.topMargin
        curPage = Page()
      # Add setion header size and size of lines of data
      headerWidth, headerHeight = self.fontTablature.getsize(section.header)
      currentHeight += headerHeight
      currentHeight += section.expectedHeight
      curPage.sections.append(section)
      # Margin between each section
      currentHeight += self.topMargin
    # No more sections left, so the current buffered image is ready to be written to file
    curPage.totalHeight = currentHeight
    self.pages.append(curPage)
    
  """!@brief Parses self.rawData into Section objects and metadata
      @return None
  """
  def initSections(self):
    # Get raw data
    self.rawData = readSourceFile(self.inputFile)
    # Clean up input
    parseData = stripEmptyLines(self.rawData)
    #print("Clean data='{}'\n".format(parseData))
    # While not EOF: build sections untill new section found.
    delimiterIndex = parseData.find("[")
    if delimiterIndex == -1:
      print("Cannot parse input file, since it is not delimited by '[<sectionName>]' entries")
      return
    # Start with metadata
    self.metadata = parseData[:delimiterIndex]
    #print("Set '{}' as metadata".format(self.metadata))
    parseData = parseData[delimiterIndex:]
    # We are now at the start of the first section, at the '[' character
    while parseData:
      # Init new Section object
      thisSection = Section()
      # Get header on the first line
      delimiterIndex = parseData.find("]\r\n")
      if delimiterIndex == -1:
        print("Cannot parse input file, delimitor did not match '[<sectionName>]'")
        return
      # Skip the ']\r\n' characters
      thisSection.header = parseData[:delimiterIndex+3]
      parseData = parseData[delimiterIndex+3:]
      # Find next section
      delimiterIndex = parseData.find("[")
      # If EOF, current buffer is final section
      if delimiterIndex == -1:
        # Set thisSection's data to remaining buffer
        thisSection.rawData = parseData
        parseData = ""
      else:
        # Set thisSection's data and remove it from the buffer
        thisSection.rawData = parseData[:delimiterIndex]
        #print("set rawData of '{}' to this section".format(thisSection.rawData))
        parseData = parseData[delimiterIndex:]
      # Finally parse section data
      thisSection.initSections()
      if thisSection.isParsed:
        self.sections.append(thisSection)
      else:
        print("Aborting parse due to section not being parseable.")
        return
    self.isParsed = True
  
  
  
  
  
  
  
  
  
  
  
  
